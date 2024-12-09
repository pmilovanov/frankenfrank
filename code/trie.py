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
        """Insert a word into the trie."""
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
        """Return True if the word is in the trie."""
        node = self._traverse(word)
        return node is not None and node.is_end

    def starts_with(self, prefix: str) -> bool:
        """Return True if any word starts with the given prefix."""
        return self._traverse(prefix) is not None

    def find_all_with_prefix(self, prefix: str) -> List[str]:
        """Find all words that start with the given prefix."""
        results: List[str] = []
        node = self._traverse(prefix)

        if node is None:
            return results

        def dfs(current_node: TrieNode, current_word: str) -> None:
            if current_node.is_end:
                results.append(current_word)
            for char in sorted(current_node.children.keys()):
                dfs(current_node.children[char], current_word + char)

        dfs(node, prefix)
        return results

    def remove(self, word: str) -> bool:
        """Remove a word from the trie."""
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
            if should_delete_child and not node.children[char].children:
                del node.children[char]
            return not node.is_end and not node.children

        _remove_helper(self.root, word, 0)
        return True

    def _traverse(self, prefix: str) -> Optional[TrieNode]:
        """Traverse to the node representing the prefix."""
        node = self.root
        for char in prefix:
            if char not in node.children:
                return None
            node = node.children[char]
        return node

    def get_all_words(self) -> List[str]:
        """Return all words in sorted order."""
        return self.find_all_with_prefix("")

    def size(self) -> int:
        """Return number of words in the trie."""
        return self._size

    def clear(self) -> None:
        """Remove all words."""
        self.root = TrieNode()
        self._size = 0

    def find_longest_substrings(self, text: str) -> Set[str]:
        """
        Find longest possible substrings that exist in the trie.
        Returns individual characters for parts not found in trie.
        """
        if not text:
            return set()

        results = set()
        pos = 0
        text_len = len(text)

        while pos < text_len:
            current_char = text[pos]

            # If current character isn't in trie, add it and move on
            if current_char not in self.root.children:
                results.add(current_char)
                pos += 1
                continue

            # Try to find longest match starting at current position
            node = self.root
            current_pos = pos
            longest_match = None
            longest_match_pos = pos

            # Look for matches while we have characters and valid trie nodes
            while current_pos < text_len and text[current_pos] in node.children:
                node = node.children[text[current_pos]]
                current_pos += 1
                # If this is a word, update our longest match
                if node.is_end:
                    longest_match = text[pos:current_pos]
                    longest_match_pos = current_pos

            # If we found a match, add it and update position
            if longest_match:
                results.add(longest_match)
                pos = longest_match_pos
            else:
                # No match found, add single character and move on
                results.add(text[pos])
                pos += 1

        return results

def build_trie_from_words(words: List[str]) -> Trie:
    """Build a trie from a list of words."""
    trie = Trie()
    for word in words:
        trie.insert(word)
    return trie