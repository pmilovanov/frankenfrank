#!/usr/bin/env python3

import argparse
import sys
from typing import List
from parse import Dialogue, DialogueParseError, parse_dialogues

def print_dialogue(dialogue: Dialogue, dialogue_num: int):
    """Print a single dialogue's lines in 'speaker: chinese' format."""
    print(f"# Dialogue {dialogue_num}")
    for line in dialogue.lines:
        speaker = line.speaker if line.speaker else "?"
        print(f"{speaker}: {line.chinese}")
    print()  # Empty line between dialogues

def main():
    parser = argparse.ArgumentParser(description='Print Chinese lines from dialogues')
    parser.add_argument('-d', '--dialogues', required=True,
                        help='YAML file containing dialogues')
    parser.add_argument('-s', '--first-dialogue', type=int, default=0,
                        help='Index of first dialogue to process (0-based, default: 0)')
    parser.add_argument('-c', '--dialogue-count', type=int,
                        help='Number of dialogues to process (default: process all remaining)')

    args = parser.parse_args()

    # Validate dialogue range arguments
    if args.first_dialogue < 0:
        print("Error: --first-dialogue must be non-negative", file=sys.stderr)
        sys.exit(1)
    if args.dialogue_count is not None and args.dialogue_count <= 0:
        print("Error: --dialogue-count must be positive", file=sys.stderr)
        sys.exit(1)

    # Read and parse dialogues
    try:
        with open(args.dialogues, 'r', encoding='utf-8') as f:
            yaml_text = f.read()
        all_dialogues = parse_dialogues(yaml_text)
    except FileNotFoundError:
        print(f"Dialogue file not found: {args.dialogues}", file=sys.stderr)
        sys.exit(1)
    except DialogueParseError as e:
        print(f"Error parsing dialogues: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading dialogue file: {e}", file=sys.stderr)
        sys.exit(1)

    # Handle out of range start index
    if not all_dialogues:
        print("No dialogues found in file", file=sys.stderr)
        sys.exit(1)

    if args.first_dialogue >= len(all_dialogues):
        print(f"Error: --first-dialogue ({args.first_dialogue}) exceeds number of dialogues ({len(all_dialogues)})",
              file=sys.stderr)
        sys.exit(1)

    # Select dialogue range
    end_index = None
    if args.dialogue_count is not None:
        end_index = args.first_dialogue + args.dialogue_count
        if end_index > len(all_dialogues):
            print(f"Warning: requested {args.dialogue_count} dialogues but only "
                  f"{len(all_dialogues) - args.first_dialogue} remain after index {args.first_dialogue}",
                  file=sys.stderr)

    selected_dialogues = all_dialogues[args.first_dialogue:end_index]

    # Print dialogues
    for i, dialogue in enumerate(selected_dialogues, start=args.first_dialogue + 1):
        print_dialogue(dialogue, i)

if __name__ == '__main__':
    main()