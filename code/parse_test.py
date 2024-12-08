import unittest
import yaml
from typing import List
from dataclasses import dataclass

# Import the code under test (assuming it's in dialogue.py)
from parse import Dialogue, parse_dialogue_from_dict, parse_dialogues

class TestDialogueParsing(unittest.TestCase):
    def setUp(self):
        # Sample valid dialogue data
        self.valid_dialogue = {
            "s": "A",
            "c": "你好！",
            "p": "Nǐ hǎo!",
            "t": "Здравствуй!",
            "d": "Буквально означает «ты хороший». Произносится как nǐ háo, когда следуют подряд два слова третьим тоном",
            "a": "ecde115cdca96a1a181db6b9e88c1e1f6e208ca77916627cc8a9fa02b39d0692.mp3",
            "as": "ecde115cdca96a1a181db6b9e88c1e1f6e208ca77916627cc8a9fa02b39d0692_slow.mp3"
        }

        # Sample YAML with multiple dialogues
        self.valid_yaml_multiple = """
- s: "A"
  c: "你好！"
  p: "Nǐ hǎo!"
  t: "Здравствуй!"
  d: "Description 1"
  a: "audio1.mp3"
  as: "audio1_slow.mp3"
- s: "B"
  c: "再见"
  p: "Zàijiàn"
  t: "До свидания!"
  d: "Description 2"
  a: "audio2.mp3"
  as: "audio2_slow.mp3"
"""

    def test_dialogue_dataclass_creation(self):
        """Test creating a Dialogue instance directly"""
        dialogue = Dialogue(
            speaker="A",
            chinese="你好！",
            pronunciation="Nǐ hǎo!",
            translation="Здравствуй!",
            description="Test description",
            audio="test.mp3",
            audio_slow="test_slow.mp3"
        )
        self.assertEqual(dialogue.speaker, "A")
        self.assertEqual(dialogue.chinese, "你好！")
        self.assertEqual(dialogue.pronunciation, "Nǐ hǎo!")
        self.assertEqual(dialogue.translation, "Здравствуй!")
        self.assertEqual(dialogue.description, "Test description")
        self.assertEqual(dialogue.audio, "test.mp3")
        self.assertEqual(dialogue.audio_slow, "test_slow.mp3")

    def test_parse_dialogue_from_dict(self):
        """Test parsing a single dialogue from a dictionary"""
        dialogue = parse_dialogue_from_dict(self.valid_dialogue)
        self.assertIsInstance(dialogue, Dialogue)
        self.assertEqual(dialogue.speaker, "A")
        self.assertEqual(dialogue.chinese, "你好！")
        self.assertEqual(dialogue.pronunciation, "Nǐ hǎo!")
        self.assertEqual(dialogue.translation, "Здравствуй!")
        self.assertTrue(dialogue.description.startswith("Буквально"))
        self.assertTrue(dialogue.audio.endswith(".mp3"))
        self.assertTrue(dialogue.audio_slow.endswith("_slow.mp3"))

    def test_parse_dialogues_single(self):
        """Test parsing YAML with a single dialogue"""
        yaml_single = yaml.dump(self.valid_dialogue)
        dialogues = parse_dialogues(yaml_single)
        self.assertEqual(len(dialogues), 1)
        self.assertIsInstance(dialogues[0], Dialogue)
        self.assertEqual(dialogues[0].speaker, "A")

    def test_parse_dialogues_multiple(self):
        """Test parsing YAML with multiple dialogues"""
        dialogues = parse_dialogues(self.valid_yaml_multiple)
        self.assertEqual(len(dialogues), 2)
        self.assertEqual(dialogues[0].speaker, "A")
        self.assertEqual(dialogues[1].speaker, "B")
        self.assertEqual(dialogues[0].chinese, "你好！")
        self.assertEqual(dialogues[1].chinese, "再见")

    def test_parse_dialogues_invalid_yaml(self):
        """Test handling invalid YAML"""
        invalid_yaml = "{ invalid: yaml: content:"
        result = parse_dialogues(invalid_yaml)
        self.assertEqual(len(result), 1)
        self.assertTrue(isinstance(result[0], str))
        self.assertTrue(result[0].startswith("Error parsing YAML"))

    def test_parse_dialogue_missing_fields(self):
        """Test handling dictionary with missing required fields"""
        invalid_dialogue = {
            "s": "A",
            "c": "你好！"
            # missing other required fields
        }
        with self.assertRaises(KeyError):
            parse_dialogue_from_dict(invalid_dialogue)

    def test_parse_dialogues_empty_yaml(self):
        """Test handling empty YAML"""
        empty_yaml = ""
        dialogues = parse_dialogues(empty_yaml)
        self.assertEqual(len(dialogues), 0)

    def test_unicode_handling(self):
        """Test handling of Unicode characters in all relevant fields"""
        unicode_dialogue = {
            "s": "话",  # Chinese character as speaker
            "c": "你好！世界",
            "p": "Nǐ hǎo! Shìjiè",
            "t": "Здравствуй, мир!",
            "d": "描述 - Description - Описание",
            "a": "audio.mp3",
            "as": "audio_slow.mp3"
        }
        dialogue = parse_dialogue_from_dict(unicode_dialogue)
        self.assertEqual(dialogue.speaker, "话")
        self.assertEqual(dialogue.chinese, "你好！世界")
        self.assertEqual(dialogue.pronunciation, "Nǐ hǎo! Shìjiè")
        self.assertEqual(dialogue.translation, "Здравствуй, мир!")
        self.assertEqual(dialogue.description, "描述 - Description - Описание")

if __name__ == '__main__':
    unittest.main()