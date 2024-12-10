#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

def remove_audio_attributes(input_path: Path, output_path: Path | None = None):
    """Remove 'a' and 'as' attributes from each line in the dialogues"""

    # Read input file
    with open(input_path, 'r', encoding='utf-8') as f:
        dialogues = json.load(f)

    # Process each dialogue
    for dialogue in dialogues:
        for line in dialogue['lines']:
            line.pop('a', None)  # Remove 'a' if it exists
            line.pop('as', None)  # Remove 'as' if it exists

    # Determine output path
    output_path = output_path or input_path

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dialogues, f, ensure_ascii=False, indent=2)
        f.write('\n')

def main():
    parser = argparse.ArgumentParser(description='Remove audio attributes from dialogue JSON')
    parser.add_argument('input', type=str, help='Input JSON file')
    parser.add_argument('-o', '--output', type=str, help='Output JSON file (default: overwrite input)')

    args = parser.parse_args()
    remove_audio_attributes(Path(args.input), Path(args.output) if args.output else None)

if __name__ == '__main__':
    main()