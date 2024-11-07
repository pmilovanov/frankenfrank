import yaml
import hashlib
import requests
import json
from pathlib import Path
import time
import os
import argparse
from typing import Optional

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate TTS audio for Chinese dialogue YAML files'
    )
    parser.add_argument(
        '-i', '--input',
        required=True,
        help='Input YAML file containing dialogues'
    )
    parser.add_argument(
        '-o', '--output-dir',
        required=True,
        help='Output directory for generated audio files'
    )
    return parser.parse_args()

# Get API token from environment variable
API_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
if not API_TOKEN:
    raise ValueError("HUGGINGFACE_TOKEN environment variable not set")

API_URL = "https://api-inference.huggingface.co/models/coqui/XTTS-v2"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

# Speaker voice mappings - using different speakers for A and B
SPEAKER_VOICES = {
    'A': "female",  # These are example voice options, check XTTS documentation
    'B': "male"     # for actual available voice options
}

def hash_text(text: str) -> str:
    """Generate a unique hash for the Chinese text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]

def generate_speech(text: str, speaker: str = "female") -> Optional[bytes]:
    """Generate speech using Hugging Face's TTS API."""
    payload = {
        "inputs": text,
        "parameters": {
            "speaker": speaker,
            "language": "zh"
        }
    }
    
    response = requests.post(API_URL, headers=headers, json=payload)
    
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

def process_dialogue_file(input_file: str, output_dir: str) -> None:
    """Process the dialogue YAML file and generate audio files."""
    # Create output directory if it doesn't exist
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read YAML file
    with open(input_file, 'r', encoding='utf-8') as f:
        dialogues = yaml.safe_load(f)
    
    # Process each dialogue
    for dialogue_key, dialogue_lines in dialogues.items():
        print(f"Processing {dialogue_key}...")
        
        for line in dialogue_lines:
            chinese_text = line['c']
            speaker = line['s']
            
            # Generate unique filename based on content
            file_hash = hash_text(chinese_text)
            audio_filename = f"{file_hash}.wav"
            audio_path = output_dir / audio_filename
            
            # Only generate if file doesn't already exist
            if not audio_path.exists():
                print(f"Generating audio for: {chinese_text}")
                audio_data = generate_speech(
                    chinese_text,
                    SPEAKER_VOICES.get(speaker, "female")
                )
                
                if audio_data:
                    with open(audio_path, 'wb') as f:
                        f.write(audio_data)
                    print(f"Saved: {audio_filename}")
                    # Add small delay to avoid API rate limits
                    time.sleep(1)
            
            # Add audio filename to the dialogue data
            line['a'] = audio_filename
    
    # Write updated YAML file
    output_yaml = str(Path(input_file).with_suffix('')) + '_with_audio.yml'
    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(dialogues, f, allow_unicode=True, default_flow_style=False)
    
    print(f"\nProcessing complete! Updated YAML saved to: {output_yaml}")

def main():
    args = parse_args()
    process_dialogue_file(args.input, args.output_dir)

if __name__ == "__main__":
    main()
