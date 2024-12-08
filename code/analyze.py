

from typing import List



def parse_trie(strings: List[str]) -> Trie:
    trie = Trie()
    for string in strings:
        trie.insert(string)
    return trie
