#!/usr/bin/env python3
import argparse
import asyncio
import hashlib
import logging
import os
import shutil
import time
from pathlib import Path
from typing import List, Optional, Tuple, NamedTuple
from google.cloud import texttospeech_v1beta1
from google.auth.exceptions import DefaultCredentialsError

from parse import Dialogue, DialogueLine, parse_dialogues, save_dialogues, DialogueParseError

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
    def __init__(self, output_dir: Path, batch_size: int = 10, config: Optional[GenerationConfig] = None):
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

    def get_file_hash(self, text: str, speaker: str) -> str:
        """
        Generate a hash for the text and speaker combination.
        Different speakers will generate different hashes even for the same text.
        """
        # Combine speaker and text with a delimiter that can't appear in either
        content = f"{speaker}\x00{text}"  # Using null byte as delimiter
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def get_audio_paths(self, text: str, speaker: str) -> Tuple[Path, Path]:
        """Get the expected audio file paths for normal and slow versions"""
        file_hash = self.get_file_hash(text, speaker)
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

        file_hash = self.get_file_hash(text, speaker)
        filename = f"{file_hash}_slow.mp3" if speed == 'slow' else f"{file_hash}.mp3"
        return filename, response.audio_content

    async def process_line(self, line: DialogueLine) -> DialogueLine:
        """Process a single dialogue line, generating both normal and slow versions"""
        if not line.chinese or not line.speaker:
            return line

        normal_path, slow_path = self.get_audio_paths(line.chinese, line.speaker)

        # Handle normal speed version
        should_generate_normal = (
                self.config.force_normal or
                not normal_path.exists() or
                not line.audio
        )

        if should_generate_normal:
            action = "Regenerating" if normal_path.exists() else "Generating"
            logger.info(f"{action} normal speed audio for speaker {line.speaker}: {line.chinese[:20]}...")
            filename, audio_content = await self.generate_audio_for_line(line.chinese, line.speaker, 'normal')
            with open(normal_path, "wb") as out:
                out.write(audio_content)
            line.audio = filename
        else:
            logger.debug(f"Skipping normal speed audio for speaker {line.speaker}: {line.chinese[:20]}...")
            if not line.audio:
                line.audio = normal_path.name

        # Handle slow speed version
        should_generate_slow = (
                self.config.force_slow or
                not slow_path.exists() or
                not line.audio_slow
        )

        if should_generate_slow:
            action = "Regenerating" if slow_path.exists() else "Generating"
            logger.info(f"{action} slow speed audio for speaker {line.speaker}: {line.chinese[:20]}...")
            filename, audio_content = await self.generate_audio_for_line(line.chinese, line.speaker, 'slow')
            with open(slow_path, "wb") as out:
                out.write(audio_content)
            line.audio_slow = filename
        else:
            logger.debug(f"Skipping slow speed audio for speaker {line.speaker}: {line.chinese[:20]}...")
            if not line.audio_slow:
                line.audio_slow = slow_path.name

        return line

    async def process_batch(self, dialogues: List[Dialogue]) -> List[Dialogue]:
        """Process a batch of dialogues concurrently"""
        tasks = []
        for dialogue in dialogues:
            for line in dialogue.lines:
                tasks.append(self.process_line(line))

        processed_lines = await asyncio.gather(*tasks)

        # Reconstruct dialogues with processed lines
        line_index = 0
        result_dialogues = []
        for dialogue in dialogues:
            processed_dialogue = Dialogue(
                title=dialogue.title,
                lines=processed_lines[line_index:line_index + len(dialogue.lines)]
            )
            result_dialogues.append(processed_dialogue)
            line_index += len(dialogue.lines)

        return result_dialogues

    async def process_dialogues(self, dialogues: List[Dialogue]) -> List[Dialogue]:
        """Process all dialogues in batches"""
        total_lines = sum(len(dialogue.lines) for dialogue in dialogues)
        logger.info(f"Processing {total_lines} lines from {len(dialogues)} dialogues")

        if self.config.force_normal:
            logger.info("Force regeneration enabled for normal speed audio")
        if self.config.force_slow:
            logger.info("Force regeneration enabled for slow speed audio")

        # Process dialogues in batches based on total line count
        result_dialogues = []
        current_batch = []
        current_line_count = 0

        for dialogue in dialogues:
            dialogue_line_count = len(dialogue.lines)

            if current_line_count + dialogue_line_count > self.batch_size:
                # Process current batch
                if current_batch:
                    result_dialogues.extend(await self.process_batch(current_batch))
                # Start new batch with current dialogue
                current_batch = [dialogue]
                current_line_count = dialogue_line_count
            else:
                # Add to current batch
                current_batch.append(dialogue)
                current_line_count += dialogue_line_count

        # Process final batch
        if current_batch:
            result_dialogues.extend(await self.process_batch(current_batch))

        return result_dialogues

async def main(args: argparse.Namespace):
    try:
        input_path = Path(args.input_file)
        output_dir = Path(args.audio_output_dir)
        backup_path = input_path.with_suffix(f'.bak{input_path.suffix}')

        # Create backup of original file
        logger.info(f"Creating backup of original file at {backup_path}")
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

        # Read and parse dialogues using the shared parsing code
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                content = f.read()
            dialogues = parse_dialogues(content)
            if not dialogues:
                logger.error("No dialogues found in file")
                return
        except (FileNotFoundError, DialogueParseError) as e:
            logger.error(f"Error reading dialogues: {e}")
            return

        logger.info(f"Starting audio generation from {input_path}")
        logger.info(f"Audio files will be saved to {output_dir}")

        # Process dialogues and generate audio
        updated_dialogues = await generator.process_dialogues(dialogues)

        # Save updated dialogues using shared saving code
        logger.info("Saving updated dialogues...")
        save_dialogues(updated_dialogues, input_path, format='json')

        logger.info(f"Successfully processed all dialogue lines")
        logger.info(f"Original file backed up to: {backup_path}")
        logger.info(f"Updated file saved in-place at: {input_path}")

    except Exception as e:
        logger.error(f"Error processing dialogues: {e}")
        raise

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Generate normal and slow TTS audio for dialogue files'
    )

    parser.add_argument(
        '-i', '--input-file',
        required=True,
        help='Input file containing dialogues'
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
        help='Number of lines to process concurrently (default: 30)'
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