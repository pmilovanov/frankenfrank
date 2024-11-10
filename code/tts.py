import yaml
import hashlib
import asyncio
from google.cloud import texttospeech_v1beta1
from google.auth.exceptions import DefaultCredentialsError
from pathlib import Path
import os
from typing import List, Dict, Any, Optional, Tuple
import logging
import argparse
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DialogueTTSGenerator:
    def __init__(self, output_dir: Path, batch_size: int = 10):
        # Try to initialize client with application default credentials first
        try:
            self.client = texttospeech_v1beta1.TextToSpeechAsyncClient()
            logger.info("Using application default credentials")
        except DefaultCredentialsError as e:
            # If explicit credentials path is set, use that
            creds_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            if creds_path and os.path.exists(creds_path):
                self.client = texttospeech_v1beta1.TextToSpeechAsyncClient()
                logger.info(f"Using credentials from: {creds_path}")
            else:
                raise DefaultCredentialsError(
                    "No credentials found. Either set up application default credentials "
                    "or set GOOGLE_APPLICATION_CREDENTIALS environment variable"
                ) from e

        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        self.batch_size = batch_size
        
        self.speaker_voices = {
            'A': texttospeech_v1beta1.VoiceSelectionParams(
                language_code='cmn-CN',
                name='cmn-CN-Wavenet-A',
            ),
            'B': texttospeech_v1beta1.VoiceSelectionParams(
                language_code='cmn-CN',
                name='cmn-CN-Wavenet-B',
            ),
            'C': texttospeech_v1beta1.VoiceSelectionParams(
                language_code='cmn-CN',
                name='cmn-CN-Wavenet-C',
            ),
            'D': texttospeech_v1beta1.VoiceSelectionParams(
                language_code='cmn-CN',
                name='cmn-CN-Wavenet-D',
            ),
        }
        
        self.audio_config = texttospeech_v1beta1.AudioConfig(
            audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3,
            speaking_rate=0.9,
            pitch=0.0
        )

    def get_file_hash(self, text: str) -> str:
        """Generate a hash for the Chinese text to use as filename"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def get_audio_path(self, text: str) -> Path:
        """Get the expected audio file path for a given text"""
        filename = f"{self.get_file_hash(text)}.mp3"
        return self.output_dir / filename

    async def generate_audio_for_line(self, text: str, speaker: str) -> Tuple[str, bytes]:
        """Generate audio for a single line of dialogue"""
        synthesis_input = texttospeech_v1beta1.SynthesisInput(text=text)
        voice = self.speaker_voices.get(speaker)
        if not voice:
            raise ValueError(f"No voice defined for speaker {speaker}")

        response = await self.client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=self.audio_config
        )

        filename = f"{self.get_file_hash(text)}.mp3"
        return filename, response.audio_content

    async def process_line(self, line: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single dialogue line, checking for existing audio"""
        if 'c' not in line:
            return line
        
        # Calculate expected audio path
        audio_path = self.get_audio_path(line['c'])
        expected_filename = audio_path.name
        
        # If audio attribute exists and file exists, skip
        if 'a' in line and audio_path.exists():
            logger.debug(f"Skipping line with existing audio: {line['c'][:20]}...")
            return line
            
        # If file exists but attribute is missing, add attribute
        if audio_path.exists():
            logger.info(f"Found existing audio file for: {line['c'][:20]}...")
            line['a'] = expected_filename
            return line
            
        # If neither exists, generate new audio
        logger.info(f"Generating new audio for: {line['c'][:20]}...")
        filename, audio_content = await self.generate_audio_for_line(line['c'], line['s'])
        with open(audio_path, "wb") as out:
            out.write(audio_content)
        line['a'] = filename
        return line

    async def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of dialogue lines concurrently"""
        return await asyncio.gather(*[self.process_line(line) for line in batch])

    async def process_dialogues(self, yaml_content: str) -> Dict:
        """Process all dialogues in the YAML content with batching"""
        data = yaml.safe_load(yaml_content)
        
        # Collect all dialogue lines that need processing
        all_lines = []
        line_locations = []  # Keep track of where each line belongs
        
        for dialogue_key, dialogue in data.items():
            for i, line in enumerate(dialogue):
                if 'c' in line:
                    all_lines.append(line)
                    line_locations.append((dialogue_key, i))

        # Process in batches
        total_lines = len(all_lines)
        logger.info(f"Processing {total_lines} lines in batches of {self.batch_size}")

        for i in range(0, total_lines, self.batch_size):
            batch = all_lines[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}")
            processed_batch = await self.process_batch(batch)
            
            # Update the original data structure
            for j, line in enumerate(processed_batch):
                dialogue_key, line_index = line_locations[i + j]
                data[dialogue_key][line_index] = line

        return data

async def main(args: argparse.Namespace):
    try:
        # Convert paths to Path objects
        input_path = Path(args.input_yaml)
        output_dir = Path(args.audio_output_dir)
        backup_path = input_path.with_suffix('.bak.yaml')
        
        # Create backup of original file
        logger.info(f"Creating backup of original YAML at {backup_path}")
        shutil.copy2(input_path, backup_path)
        
        # Initialize the generator
        generator = DialogueTTSGenerator(
            output_dir=output_dir,
            batch_size=args.batch_size
        )
        
        # Read input YAML
        with open(input_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        
        logger.info(f"Starting audio generation from {input_path}")
        logger.info(f"Audio files will be saved to {output_dir}")
        
        # Process dialogues
        updated_data = await generator.process_dialogues(yaml_content)
        
        # Update the original YAML file in-place
        with open(input_path, 'w', encoding='utf-8') as f:
            yaml.dump(updated_data, f, allow_unicode=True, sort_keys=False)
        
        logger.info(f"Successfully processed all dialogue lines")
        logger.info(f"Original YAML backed up to: {backup_path}")
        logger.info(f"Updated YAML saved in-place at: {input_path}")
        
    except DefaultCredentialsError as e:
        logger.error(f"Authentication error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing dialogues: {e}")
        raise

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Generate TTS audio for dialogue YAML files')
    
    parser.add_argument(
        '-i', '--input-yaml',
        required=True,
        help='Input YAML file containing dialogues (will be updated in-place)'
    )
    
    parser.add_argument(
        '-d', '--audio-output-dir',
        default='generated_audio',
        help='Directory to output audio files (default: generated_audio)'
    )
    
    parser.add_argument(
        '-b', '--batch-size',
        type=int,
        default=10,
        help='Number of audio files to generate concurrently (default: 10)'
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
