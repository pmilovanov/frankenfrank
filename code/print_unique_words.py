#!/usr/bin/env python3

import argparse
import sys
from typing import Set, List
from parse import Dialogue, DialogueParseError, parse_dialogues
from trie import Trie, build_trie_from_words

def read_word_list(filename: str) -> List[str]:
    """Read words from a file, one per line, skipping empty lines."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Word list file not found: {filename}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error reading file {filename}: invalid UTF-8 encoding", file=sys.stderr)
        sys.exit(1)

def extract_words(dialogues: List[Dialogue], word_trie: Trie) -> Set[str]:
    """Extract all words from dialogues using the word trie."""
    words = set()
    for dialogue in dialogues:
        for line in dialogue.lines:
            words.update(word_trie.find_longest_substrings(line.chinese))
    return words

def main():
    parser = argparse.ArgumentParser(description='Extract words from dialogues using a word list')
    parser.add_argument('-d', '--dialogues', required=True,
                        help='YAML file containing dialogues')
    parser.add_argument('-w', '--words', required=True,
                        help='File containing words, one per line')
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

    # Read and parse word list
    try:
        words = read_word_list(args.words)
        word_trie = build_trie_from_words(words)
    except Exception as e:
        print(f"Error processing word list: {e}", file=sys.stderr)
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

    # Extract and print words
    found_words = extract_words(selected_dialogues, word_trie)
    for word in sorted(found_words):
        print(word)

if __name__ == '__main__':
    main()