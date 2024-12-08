from typing import Dict, List, Optional, Set

class TrieNode:
    def __init__(self):
        self.children: Dict[str, TrieNode] = {}
        self.is_end: bool = False
        self.value: Optional[str] = None

    def __repr__(self) -> str:
        return f"TrieNode(value={self.value}, is_end={self.is_end}, children={len(self.children)})"

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self._size = 0

    def insert(self, word: str) -> None:
        """
        Insert a word into the trie.
        Each character, including CJK characters, is treated as a single node.
        """
        if not word:
            return

        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.value = char

        # Only increment size if this is a new word
        if not node.is_end:
            self._size += 1
        node.is_end = True

    def search(self, word: str) -> bool:
        """
        Return True if the word is in the trie, False otherwise.
        """
        node = self._traverse(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """
        Return True if there is any word in the trie that starts with the given prefix.
        """
        return self._traverse(prefix) is not None

    def find_all_with_prefix(self, prefix: str) -> List[str]:
        """
        Find all words that start with the given prefix.
        Returns them in sorted order.
        """
        results: List[str] = []
        node = self._traverse(prefix)

        if node is None:
            return results

        # Use DFS to find all words with the prefix
        def dfs(current_node: TrieNode, current_word: str) -> None:
            if current_node.is_end:
                results.append(current_word)

            # Sort children keys to ensure consistent ordering
            for char in sorted(current_node.children.keys()):
                dfs(current_node.children[char], current_word + char)

        dfs(node, prefix)
        return results

    def remove(self, word: str) -> bool:
        """
        Remove a word from the trie.
        Returns True if the word was found and removed, False otherwise.
        """
        def _remove_helper(node: TrieNode, word: str, depth: int) -> bool:
            if depth == len(word):
                if not node.is_end:
                    return False
                node.is_end = False
                self._size -= 1
                return True

            char = word[depth]
            if char not in node.children:
                return False

            should_delete_child = _remove_helper(node.children[char], word, depth + 1)

            # If child should be deleted and it has no other children
            if should_delete_child and not node.children[char].children:
                del node.children[char]

            # Current node should be deleted if it's not end of another word and has no children
            return not node.is_end and not node.children

        _remove_helper(self.root, word, 0)
        return True

    def _traverse(self, prefix: str) -> Optional[TrieNode]:
        """
        Traverse the trie following the prefix.
        Returns the last node if prefix exists, None otherwise.
        """
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def get_all_words(self) -> List[str]:
        """
        Return all words in the trie in sorted order.
        """
        return self.find_all_with_prefix("")

    def size(self) -> int:
        """
        Return the number of words in the trie.
        """
        return self._size

    def clear(self) -> None:
        """
        Remove all words from the trie.
        """
        self.root = TrieNode()
        self._size = 0

    def find_longest_substrings(self, text: str) -> Set[str]:
        """
        Greedily extract longest possible substrings from text that exist in the trie.

        For each position in text, finds the longest substring starting at that position
        that exists in the trie. If no substring is found starting with that character,
        the single character is added to the result set.

        Args:
            text: The input text to search for substrings

        Returns:
            A set of strings, where each string is either:
            - The longest substring from some position that exists in the trie
            - A single character from the input that wasn't present in the trie
        """
        results = set()
        pos = 0

        while pos < len(text):
            # Start with the current character
            current_char = text[pos]

            # If current character isn't in trie, add it and move on
            if current_char not in self.root.children:
                results.add(current_char)
                pos += 1
                continue

            # Find longest possible match starting at current position
            node = self.root.children[current_char]
            last_found_pos = pos
            current_pos = pos + 1
            longest_match = current_char

            # If single character is a word, track it
            if node.is_end:
                last_found_pos = current_pos
                longest_match = text[pos:current_pos]

            # Try to match longer substrings
            while current_pos < len(text):
                char = text[current_pos]
                if char not in node.children:
                    break

                node = node.children[char]
                current_pos += 1

                if node.is_end:
                    last_found_pos = current_pos
                    longest_match = text[pos:current_pos]

            # Add the longest match found
            results.add(longest_match)

            # Move position to after the last found match
            pos = last_found_pos

        return results

def build_trie_from_words(words: List[str]) -> Trie:
    """
    Build a trie from a list of words.
    """
    trie = Trie()
    for word in words:
        trie.insert(word)
    return trie