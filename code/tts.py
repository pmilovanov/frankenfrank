import yaml
import json
import hashlib
import asyncio
from google.cloud import texttospeech_v1beta1
from google.auth.exceptions import DefaultCredentialsError
from pathlib import Path
import os
from typing import List, Dict, Any, Optional, Tuple, NamedTuple, Union
import logging
import argparse
import shutil
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenerationConfig(NamedTuple):
    """Configuration for audio generation behavior"""
    force_normal: bool
    force_slow: bool
    max_rps: int

class RPSLimiter:
    """Rate limiter for API calls"""
    def __init__(self, max_rps: int):
        self.max_rps = max_rps
        self.semaphore = asyncio.Semaphore(max_rps)
        self.last_release_time = {}  # Track last release time for each slot

    async def acquire(self):
        """Acquire a slot while maintaining the RPS limit"""
        await self.semaphore.acquire()
        current_time = time.monotonic()

        # Find the oldest slot
        slot = None
        oldest_time = float('inf')
        for i in range(self.max_rps):
            last_time = self.last_release_time.get(i, 0)
            if last_time < oldest_time:
                oldest_time = last_time
                slot = i

        # If we need to wait to maintain RPS, do so
        time_since_last = current_time - oldest_time
        if time_since_last < 1.0:  # Less than a second has passed
            await asyncio.sleep(1.0 - time_since_last)

        self.last_release_time[slot] = time.monotonic()
        return slot

    def release(self):
        """Release a slot"""
        self.semaphore.release()

class AsyncRateLimiter:
    """Context manager for rate limiting"""
    def __init__(self, limiter: RPSLimiter):
        self.limiter = limiter
        self.slot = None

    async def __aenter__(self):
        self.slot = await self.limiter.acquire()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        self.limiter.release()

class DialogueTTSGenerator:
    def __init__(self, output_dir: Path, batch_size: int = 10, config: GenerationConfig = None):
        self.config = config or GenerationConfig(
            force_normal=False,
            force_slow=False,
            max_rps=15
        )

        try:
            self.client = texttospeech_v1beta1.TextToSpeechAsyncClient()
            logger.info("Using application default credentials")
        except DefaultCredentialsError as e:
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
        self.rate_limiter = RPSLimiter(self.config.max_rps)

        logger.info(f"Rate limiting enabled: maximum {self.config.max_rps} requests per second")

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

        self.audio_configs = {
            'normal': texttospeech_v1beta1.AudioConfig(
                audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3,
                speaking_rate=0.87,
                pitch=0.0
            ),
            'slow': texttospeech_v1beta1.AudioConfig(
                audio_encoding=texttospeech_v1beta1.AudioEncoding.MP3,
                speaking_rate=0.75,
                pitch=0.0
            )
        }

    def get_file_hash(self, text: str) -> str:
        """Generate a hash for the Chinese text to use as filename"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()

    def get_audio_paths(self, text: str) -> Tuple[Path, Path]:
        """Get the expected audio file paths for normal and slow versions"""
        file_hash = self.get_file_hash(text)
        normal_path = self.output_dir / f"{file_hash}.mp3"
        slow_path = self.output_dir / f"{file_hash}_slow.mp3"
        return normal_path, slow_path

    async def generate_audio_for_line(self, text: str, speaker: str, speed: str = 'normal') -> Tuple[str, bytes]:
        """Generate audio for a single line of dialogue with rate limiting"""
        synthesis_input = texttospeech_v1beta1.SynthesisInput(text=text)
        voice = self.speaker_voices.get(speaker)
        if not voice:
            raise ValueError(f"No voice defined for speaker {speaker}")

        async with AsyncRateLimiter(self.rate_limiter):
            response = await self.client.synthesize_speech(
                input=synthesis_input,
                voice=voice,
                audio_config=self.audio_configs[speed]
            )

        file_hash = self.get_file_hash(text)
        filename = f"{file_hash}_slow.mp3" if speed == 'slow' else f"{file_hash}.mp3"
        return filename, response.audio_content

    async def process_line(self, line: Dict[str, Any]) -> Dict[str, Any]:
        """Process a single dialogue line, generating both normal and slow versions"""
        if 'c' not in line:
            return line

        normal_path, slow_path = self.get_audio_paths(line['c'])

        # Handle normal speed version
        should_generate_normal = (
                self.config.force_normal or
                not normal_path.exists() or
                'a' not in line
        )

        if should_generate_normal:
            action = "Regenerating" if normal_path.exists() else "Generating"
            logger.info(f"{action} normal speed audio for: {line['c'][:20]}...")
            filename, audio_content = await self.generate_audio_for_line(line['c'], line['s'], 'normal')
            with open(normal_path, "wb") as out:
                out.write(audio_content)
            line['a'] = filename
        else:
            logger.debug(f"Skipping normal speed audio for: {line['c'][:20]}...")
            if 'a' not in line:
                line['a'] = normal_path.name

        # Handle slow speed version
        should_generate_slow = (
                self.config.force_slow or
                not slow_path.exists() or
                'as' not in line
        )

        if should_generate_slow:
            action = "Regenerating" if slow_path.exists() else "Generating"
            logger.info(f"{action} slow speed audio for: {line['c'][:20]}...")
            filename, audio_content = await self.generate_audio_for_line(line['c'], line['s'], 'slow')
            with open(slow_path, "wb") as out:
                out.write(audio_content)
            line['as'] = filename
        else:
            logger.debug(f"Skipping slow speed audio for: {line['c'][:20]}...")
            if 'as' not in line:
                line['as'] = slow_path.name

        return line

    async def process_batch(self, batch: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of dialogue lines concurrently"""
        return await asyncio.gather(*[self.process_line(line) for line in batch])

    async def process_dialogues(self, content: str, file_format: str) -> Dict:
        """Process all dialogues in the content with batching"""
        if file_format == 'json':
            data = json.loads(content)
        else:  # yaml
            data = yaml.safe_load(content)

        # Collect all dialogue lines that need processing
        all_lines = []
        line_locations = []

        for dialogue_key, dialogue in data.items():
            for i, line in enumerate(dialogue):
                if 'c' in line:
                    all_lines.append(line)
                    line_locations.append((dialogue_key, i))

        total_lines = len(all_lines)
        logger.info(f"Processing {total_lines} lines in batches of {self.batch_size}")

        if self.config.force_normal:
            logger.info("Force regeneration enabled for normal speed audio")
        if self.config.force_slow:
            logger.info("Force regeneration enabled for slow speed audio")

        for i in range(0, total_lines, self.batch_size):
            batch = all_lines[i:i + self.batch_size]
            logger.info(f"Processing batch {i//self.batch_size + 1}")
            processed_batch = await self.process_batch(batch)

            # Update the original data structure
            for j, line in enumerate(processed_batch):
                dialogue_key, line_index = line_locations[i + j]
                data[dialogue_key][line_index] = line

        return data

def get_file_format(file_path: str) -> str:
    """Determine the file format based on the file extension"""
    ext = Path(file_path).suffix.lower()
    if ext == '.json':
        return 'json'
    elif ext in ('.yaml', '.yml'):
        return 'yaml'
    else:
        raise ValueError(f"Unsupported file format: {ext}. Must be .json, .yaml, or .yml")

async def main(args: argparse.Namespace):
    try:
        input_path = Path(args.input_file)
        output_dir = Path(args.audio_output_dir)
        file_format = get_file_format(args.input_file)
        backup_path = input_path.with_suffix(f'.bak{input_path.suffix}')

        # Create backup of original file
        logger.info(f"Creating backup of original {file_format.upper()} file at {backup_path}")
        shutil.copy2(input_path, backup_path)

        config = GenerationConfig(
            force_normal=args.force_normal,
            force_slow=args.force_slow,
            max_rps=args.max_rps
        )

        generator = DialogueTTSGenerator(
            output_dir=output_dir,
            batch_size=args.batch_size,
            config=config
        )

        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.info(f"Starting audio generation from {input_path}")
        logger.info(f"Audio files will be saved to {output_dir}")

        updated_data = await generator.process_dialogues(content, file_format)

        with open(input_path, 'w', encoding='utf-8') as f:
            if file_format == 'json':
                json.dump(updated_data, f, ensure_ascii=False, indent=2)
            else:  # yaml
                yaml.dump(updated_data, f, allow_unicode=True, sort_keys=False)

        logger.info(f"Successfully processed all dialogue lines")
        logger.info(f"Original {file_format.upper()} backed up to: {backup_path}")
        logger.info(f"Updated {file_format.upper()} saved in-place at: {input_path}")

    except DefaultCredentialsError as e:
        logger.error(f"Authentication error: {e}")
        raise
    except Exception as e:
        logger.error(f"Error processing dialogues: {e}")
        raise

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Generate normal and slow TTS audio for dialogue files (YAML or JSON)'
    )

    parser.add_argument(
        '-i', '--input-file',
        required=True,
        help='Input file containing dialogues (YAML or JSON, will be updated in-place)'
    )

    parser.add_argument(
        '-d', '--audio-output-dir',
        default='generated_audio',
        help='Directory to output audio files (default: generated_audio)'
    )

    parser.add_argument(
        '-b', '--batch-size',
        type=int,
        default=30,
        help='Number of audio files to generate concurrently (default: 30)'
    )

    parser.add_argument(
        '--force-normal',
        action='store_true',
        help='Force regeneration of normal speed audio even if files exist'
    )

    parser.add_argument(
        '--force-slow',
        action='store_true',
        help='Force regeneration of slow speed audio even if files exist'
    )

    parser.add_argument(
        '--max-rps',
        type=int,
        default=18,
        help='Maximum requests per second to the API (default: 18)'
    )

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))