#!/usr/bin/env python3
import sys
import unicodedata
from typing import Set, List
from parse import Dialogue
from trie import Trie, build_trie_from_words

def read_word_list(filename: str) -> List[str]:
    """
    Read words from a file, one per line, skipping empty lines and removing punctuation/whitespace.
    Returns a list to maintain original order (useful for some applications).
    For set operations, callers can convert to set as needed.
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            # Read lines and filter out empty ones after stripping
            lines = [line.strip() for line in f]
            # Remove all whitespace and punctuation from each non-empty line
            words = []
            for line in lines:
                # Skip completely empty lines
                if not line:
                    continue
                # Remove all whitespace within the line
                word = clean_text(line)
                # Only add non-empty results
                if word:
                    words.append(word)
            return words
    except FileNotFoundError:
        print(f"Word list file not found: {filename}", file=sys.stderr)
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"Error reading file {filename}: invalid UTF-8 encoding", file=sys.stderr)
        sys.exit(1)

def clean_text(text: str) -> str:
    """Remove all whitespace and punctuation from text."""
    # Remove all whitespace
    text = ''.join(text.split())
    # Remove all punctuation
    return ''.join(char for char in text
                   if not char.isspace() and not unicodedata.category(char).startswith('P'))

def is_only_punctuation_or_whitespace(text: str) -> bool:
    """Return True if string consists entirely of punctuation and/or whitespace."""
    return all(char.isspace() or unicodedata.category(char).startswith('P')
               for char in text)

def extract_words_with_trie(text: str, word_trie: Trie) -> Set[str]:
    """Extract words from text using the trie to find longest matches."""
    return word_trie.find_longest_substrings(clean_text(text))

def extract_dialogue_words_with_trie(dialogues: List[Dialogue], word_trie: Trie) -> Set[str]:
    """Extract all words from dialogues using trie-based segmentation."""
    words = set()
    for dialogue in dialogues:
        for line in dialogue.lines:
            words.update(extract_words_with_trie(line.chinese, word_trie))
    return words