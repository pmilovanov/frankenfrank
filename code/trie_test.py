import unittest
from trie import Trie, build_trie_from_words

class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()

    def test_basic_operations(self):
        words = ["hello", "help", "world"]
        for word in words:
            self.trie.insert(word)

        self.assertTrue(self.trie.search("hello"))
        self.assertTrue(self.trie.search("help"))
        self.assertTrue(self.trie.search("world"))
        self.assertFalse(self.trie.search("hell"))
        self.assertFalse(self.trie.search("helping"))

        self.assertTrue(self.trie.starts_with("hel"))
        self.assertTrue(self.trie.starts_with("wor"))
        self.assertFalse(self.trie.starts_with("abc"))

    def test_cjk_characters(self):
        # Test Chinese characters
        chinese_words = ["你好", "你好世界", "世界"]
        for word in chinese_words:
            self.trie.insert(word)

        self.assertTrue(self.trie.search("你好"))
        self.assertTrue(self.trie.search("你好世界"))
        self.assertTrue(self.trie.starts_with("你"))
        self.assertTrue(self.trie.starts_with("世"))

        # Test Japanese characters (mixture of kanji, hiragana, katakana)
        japanese_words = ["こんにちは", "世界", "コンピュータ"]
        for word in japanese_words:
            self.trie.insert(word)

        self.assertTrue(self.trie.search("こんにちは"))
        self.assertTrue(self.trie.search("コンピュータ"))
        self.assertTrue(self.trie.starts_with("こん"))

        # Test Korean characters
        korean_words = ["안녕하세요", "세계", "컴퓨터"]
        for word in korean_words:
            self.trie.insert(word)

        self.assertTrue(self.trie.search("안녕하세요"))
        self.assertTrue(self.trie.search("세계"))
        self.assertTrue(self.trie.starts_with("안녕"))

    def test_mixed_scripts(self):
        # Test mixing different scripts
        mixed_words = ["hello你好", "world世界", "computer컴퓨터"]
        for word in mixed_words:
            self.trie.insert(word)

        self.assertTrue(self.trie.search("hello你好"))
        self.assertTrue(self.trie.search("world世界"))
        self.assertTrue(self.trie.starts_with("hello"))
        self.assertTrue(self.trie.starts_with("world世"))

    def test_prefix_search(self):
        words = ["你好", "你好世界", "你们", "世界"]
        for word in words:
            self.trie.insert(word)

        with_prefix = self.trie.find_all_with_prefix("你")
        self.assertEqual(set(with_prefix), {"你好", "你好世界", "你们"})

        with_prefix = self.trie.find_all_with_prefix("你好")
        self.assertEqual(set(with_prefix), {"你好", "你好世界"})

    def test_remove(self):
        words = ["你好", "你好世界", "世界"]
        for word in words:
            self.trie.insert(word)

        self.assertTrue(self.trie.remove("你好"))
        self.assertFalse(self.trie.search("你好"))
        self.assertTrue(self.trie.search("你好世界"))
        self.assertTrue(self.trie.search("世界"))

    def test_size_and_clear(self):
        words = ["你好", "你好世界", "世界", "hello", "world"]
        for word in words:
            self.trie.insert(word)

        self.assertEqual(self.trie.size(), 5)

        self.trie.clear()
        self.assertEqual(self.trie.size(), 0)
        self.assertFalse(self.trie.search("你好"))
        self.assertFalse(self.trie.search("hello"))

    def test_build_from_words(self):
        words = ["你好", "你好世界", "世界", "hello", "world"]
        trie = build_trie_from_words(words)

        self.assertEqual(trie.size(), 5)
        for word in words:
            self.assertTrue(trie.search(word))

    def test_find_longest_substrings_basic(self):
        words = ["cat", "cats", "dog", "doggy"]
        trie = build_trie_from_words(words)

        # Should find "cats" as longest match starting with 'c'
        result = trie.find_longest_substrings("cats")
        self.assertEqual(result, {"cats"})

        # Should find "dog" as longest match starting with 'd'
        result = trie.find_longest_substrings("dog")
        self.assertEqual(result, {"dog"})

        # Should find both "cat" and "dog"
        result = trie.find_longest_substrings("catdog")
        self.assertEqual(result, {"cat", "dog"})

    def test_find_longest_substrings_cjk(self):
        words = ["你好", "你好世界", "世界"]
        trie = build_trie_from_words(words)

        # Should find "你好世界" as longest match
        result = trie.find_longest_substrings("你好世界")
        self.assertEqual(result, {"你好世界"})

        # Should find "你好" and "世界"
        result = trie.find_longest_substrings("你好和世界")
        self.assertEqual(result, {"你好", "和", "世界"})

        # Should find individual characters for non-matching text
        result = trie.find_longest_substrings("我是")
        self.assertEqual(result, {"我", "是"})

    def test_find_longest_substrings_mixed(self):
        words = ["hello", "你好", "world", "世界"]
        trie = build_trie_from_words(words)

        # Should handle mixed script text
        result = trie.find_longest_substrings("hello你好world世界")
        self.assertEqual(result, {"hello", "你好", "world", "世界"})

        # Should handle text with non-matching characters
        result = trie.find_longest_substrings("hello和world")
        self.assertEqual(result, {"hello", "和", "world"})

    def test_find_longest_substrings_edge_cases(self):
        words = ["a", "ab", "abc", "b", "bc"]
        trie = build_trie_from_words(words)

        # Empty string
        result = trie.find_longest_substrings("")
        self.assertEqual(result, set())

        # Single character not in trie
        result = trie.find_longest_substrings("x")
        self.assertEqual(result, {"x"})

        # Should find longest match "abc" rather than "ab"
        result = trie.find_longest_substrings("abc")
        self.assertEqual(result, {"abc"})

        # Multiple overlapping possibilities
        result = trie.find_longest_substrings("abbc")
        self.assertEqual(result, {"ab", "bc"})

    def test_find_longest_substrings_special_chars(self):
        words = ["hello", "world", "你", "好"]
        trie = build_trie_from_words(words)

        # Test with spaces and punctuation
        result = trie.find_longest_substrings("hello world!")
        self.assertEqual(result, {"hello", " ", "world", "!"})

        # Test with emojis and special characters
        result = trie.find_longest_substrings("hello🌍world")
        self.assertEqual(result, {"hello", "🌍", "world"})

if __name__ == '__main__':
    unittest.main()