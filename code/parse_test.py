import unittest
import yaml
from typing import List
from dataclasses import dataclass

# Import the code under test
from parse import Dialogue, parse_dialogue_from_dict, parse_dialogues

class TestDialogueParsing(unittest.TestCase):
    def setUp(self):
        # Sample valid dialogue data with all fields
        self.valid_dialogue_full = {
            "s": "A",
            "c": "你好！",
            "p": "Nǐ hǎo!",
            "t": "Здравствуй!",
            "d": "Буквально означает «ты хороший»",
            "a": "audio.mp3",
            "as": "audio_slow.mp3"
        }

        # Sample valid dialogue with only required field
        self.valid_dialogue_minimal = {
            "c": "你好！"
        }

        # Sample YAML with multiple dialogues
        self.valid_yaml_multiple = """
- c: "你好！"
  s: "A"
  p: "Nǐ hǎo!"
- c: "再见"
  t: "До свидания!"
  d: "Description"
"""

    def test_dialogue_dataclass_creation(self):
        """Test creating Dialogue instances with different field combinations"""
        # Test with only required field
        dialogue_min = Dialogue(chinese="你好！")
        self.assertEqual(dialogue_min.chinese, "你好！")
        self.assertIsNone(dialogue_min.speaker)
        self.assertIsNone(dialogue_min.pronunciation)

        # Test with all fields
        dialogue_full = Dialogue(
            chinese="你好！",
            speaker="A",
            pronunciation="Nǐ hǎo!",
            translation="Hello!",
            description="Test",
            audio="test.mp3",
            audio_slow="test_slow.mp3"
        )
        self.assertEqual(dialogue_full.chinese, "你好！")
        self.assertEqual(dialogue_full.speaker, "A")

    def test_parse_dialogue_minimal(self):
        """Test parsing dialogue with only the required chinese field"""
        result = parse_dialogue_from_dict(self.valid_dialogue_minimal)
        self.assertIsInstance(result, Dialogue)
        self.assertEqual(result.chinese, "你好！")
        self.assertIsNone(result.speaker)
        self.assertIsNone(result.pronunciation)
        self.assertIsNone(result.translation)
        self.assertIsNone(result.description)
        self.assertIsNone(result.audio)
        self.assertIsNone(result.audio_slow)

    def test_parse_dialogue_full(self):
        """Test parsing dialogue with all fields"""
        result = parse_dialogue_from_dict(self.valid_dialogue_full)
        self.assertIsInstance(result, Dialogue)
        self.assertEqual(result.chinese, "你好！")
        self.assertEqual(result.speaker, "A")
        self.assertEqual(result.pronunciation, "Nǐ hǎo!")

    def test_parse_dialogue_missing_required(self):
        """Test handling dictionary without required chinese field"""
        invalid_dialogue = {
            "s": "A",
            "p": "Nǐ hǎo!"
        }
        result = parse_dialogue_from_dict(invalid_dialogue)
        self.assertIsInstance(result, str)
        self.assertTrue("Missing required field: chinese" in result)

    def test_parse_dialogues_empty_yaml(self):
        """Test handling empty YAML"""
        empty_yaml = ""
        dialogues = parse_dialogues(empty_yaml)
        self.assertEqual(len(dialogues), 0)

    def test_parse_dialogues_mixed_content(self):
        """Test handling mix of full and minimal dialogues"""
        results = parse_dialogues(self.valid_yaml_multiple)
        self.assertEqual(len(results), 2)
        self.assertIsInstance(results[0], Dialogue)
        self.assertIsInstance(results[1], Dialogue)
        self.assertEqual(results[0].chinese, "你好！")
        self.assertEqual(results[0].speaker, "A")
        self.assertEqual(results[1].chinese, "再见")
        self.assertIsNone(results[1].speaker)

    def test_unicode_handling(self):
        """Test handling of Unicode characters"""
        unicode_dialogue = {
            "c": "你好！世界",
            "p": "Nǐ hǎo! Shìjiè",
            "t": "Здравствуй, мир!"
        }
        result = parse_dialogue_from_dict(unicode_dialogue)
        self.assertIsInstance(result, Dialogue)
        self.assertEqual(result.chinese, "你好！世界")
        self.assertEqual(result.pronunciation, "Nǐ hǎo! Shìjiè")
        self.assertEqual(result.translation, "Здравствуй, мир!")

if __name__ == '__main__':
    unittest.main()