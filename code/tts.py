import yaml
import hashlib
import requests
import json
from pathlib import Path
import time
import os
import argparse
import math
from typing import Optional, Dict, Any
import json

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
    parser.add_argument(
        '--max-retries',
        type=int,
        default=5,
        help='Maximum number of retries for failed API calls'
    )
    return parser.parse_args()

# Get API token from environment variable
API_TOKEN = os.getenv('HUGGINGFACE_TOKEN')
if not API_TOKEN:
    raise ValueError("HUGGINGFACE_TOKEN environment variable not set")

API_URL = "https://api-inference.huggingface.co/models/microsoft/speecht5_tts"
headers = {"Authorization": f"Bearer {API_TOKEN}"}

def hash_text(text: str) -> str:
    """Generate a unique hash for the Chinese text."""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]

def parse_error_response(response_text: str) -> Dict[str, Any]:
    """Parse error response and extract relevant information."""
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        return {"error": response_text}

def generate_speech(text: str, max_retries: int = 5) -> Optional[bytes]:
    """Generate speech using Hugging Face's TTS API with retry logic."""
    payload = {
        "inputs": text,
        "parameters": {
            "language": "zh"
        }
    }
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = requests.post(API_URL, headers=headers, json=payload)
            
            if response.status_code == 200:
                return response.content
            
            error_data = parse_error_response(response.text)
            
            # Handle "model loading" case
            if "estimated_time" in error_data:
                wait_time = math.ceil(float(error_data["estimated_time"]))
                print(f"Model is loading. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                retry_count += 1
                continue
                
            # Handle rate limiting
            if response.status_code == 429:
                wait_time = 30  # Default wait time for rate limiting
                print(f"Rate limited. Waiting {wait_time} seconds...")
                time.sleep(wait_time)
                retry_count += 1
                continue
                
            # Handle server errors
            if response.status_code in (500, 503):
                wait_time = 5 * (retry_count + 1)  # Exponential backoff
                print(f"Server error. Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
                retry_count += 1
                continue
                
            # If we get here, it's an unhandled error
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 5 * retry_count  # Exponential backoff
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            continue
    
    print(f"Failed after {max_retries} retries")
    return None

def process_dialogue_file(input_file: str, output_dir: str, max_retries: int) -> None:
    """Process the dialogue YAML file and generate audio files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    with open(input_file, 'r', encoding='utf-8') as f:
        dialogues = yaml.safe_load(f)
    
    for dialogue_key, dialogue_lines in dialogues.items():
        print(f"Processing {dialogue_key}...")
        
        for line in dialogue_lines:
            chinese_text = line['c']
            
            # Generate unique filename based on content
            file_hash = hash_text(chinese_text)
            audio_filename = f"{file_hash}.wav"
            audio_path = output_dir / audio_filename
            
            # Only generate if file doesn't exist
            if not audio_path.exists():
                print(f"Generating audio for: {chinese_text}")
                audio_data = generate_speech(chinese_text, max_retries)
                
                if audio_data:
                    with open(audio_path, 'wb') as f:
                        f.write(audio_data)
                    print(f"Saved: {audio_filename}")
                else:
                    print(f"Failed to generate audio for: {chinese_text}")
                    continue
            
            # Add audio filename to the dialogue data
            line['a'] = audio_filename
    
    # Write updated YAML file
    output_yaml = str(Path(input_file).with_suffix('')) + '_with_audio.yml'
    with open(output_yaml, 'w', encoding='utf-8') as f:
        yaml.dump(dialogues, f, allow_unicode=True, default_flow_style=False)
    
    print(f"\nProcessing complete! Updated YAML saved to: {output_yaml}")

def main():
    args = parse_args()
    process_dialogue_file(args.input, args.output_dir, args.max_retries)

if __name__ == "__main__":
    main()
