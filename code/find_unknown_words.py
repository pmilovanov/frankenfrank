#!/usr/bin/env python3
import argparse
import sys
import os
from typing import Set
import random
from parse import DialogueParseError, parse_dialogues
from text_utils import read_word_list, extract_words_with_trie, extract_dialogue_words_with_trie
from trie import build_trie_from_words

def find_unknown_words(known_words: Set[str], dialogue_words: Set[str]) -> Set[str]:
    """Find all words in dialogue_words that aren't in known_words."""
    return dialogue_words - known_words

def get_default_vocabulary_path() -> str:
    """Get the default path for vocabulary relative to this script."""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "..", "words", "10K.txt")

def main():
    parser = argparse.ArgumentParser(description='Find words in dialogues that aren\'t in the provided word list')
    parser.add_argument('--vocabulary',
                        help='File containing vocabulary for word segmentation (default: ../words/10K.txt)')
    parser.add_argument('--wordlist', required=True,
                        help='File containing known words to check against')
    parser.add_argument('--dialogue', required=True,
                        help='YAML file containing dialogues')
    parser.add_argument('--random-order', action='store_true',
                        help='Output words in random order')
    args = parser.parse_args()

    # Set default vocabulary path if not provided
    if args.vocabulary is None:
        args.vocabulary = get_default_vocabulary_path()

    # Read vocabulary for trie
    try:
        vocabulary = read_word_list(args.vocabulary)
        word_trie = build_trie_from_words(vocabulary)
    except Exception as e:
        print(f"Error processing vocabulary file: {e}", file=sys.stderr)
        sys.exit(1)

    # Read word list to check against
    try:
        known_word_list = read_word_list(args.wordlist)
        known_words = set(known_word_list)
    except Exception as e:
        print(f"Error processing word list: {e}", file=sys.stderr)
        sys.exit(1)

    # Read and parse dialogues
    try:
        with open(args.dialogue, 'r', encoding='utf-8') as f:
            yaml_text = f.read()
        dialogues = parse_dialogues(yaml_text)
    except FileNotFoundError:
        print(f"Dialogue file not found: {args.dialogue}", file=sys.stderr)
        sys.exit(1)
    except DialogueParseError as e:
        print(f"Error parsing dialogues: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading dialogue file: {e}", file=sys.stderr)
        sys.exit(1)

    # Extract words from dialogues using vocabulary trie and find ones not in wordlist
    dialogue_words = extract_dialogue_words_with_trie(dialogues, word_trie)
    unknown_words = find_unknown_words(known_words, dialogue_words)

    # Convert to list for output
    word_list = list(unknown_words)
    if args.random_order:
        random.shuffle(word_list)
    else:
        word_list.sort()

    # Print results
    for word in word_list:
        print(word)

if __name__ == '__main__':
    main()