import unittest
import yaml
from parse import (
    DialogueLine,
    Dialogue,
    parse_dialogues,
    parse_dialogue_from_dict,
    parse_dialogue_line_from_dict,
    DialogueParseError
)

class TestDialogueParsing(unittest.TestCase):
    def setUp(self):
        # Sample valid dialogue dictionary
        self.valid_yaml = """
dialogue1:
    - s: "A"
      c: "你好！"
      p: "Nǐ hǎo!"
      t: "Здравствуй!"
      d: "Description 1"
      a: "audio1.mp3"
      as: "audio1_slow.mp3"
    - s: "B"
      c: "你好！"
      p: "Nǐ hǎo!"
      t: "Здравствуй!"
dialogue2:
    - s: "A"
      c: "再见"
      p: "Zàijiàn"
      t: "До свидания!"
"""
        # Sample minimal dialogue
        self.minimal_yaml = """
minimal:
    - c: "你好！"
    - c: "再见"
"""

    def test_parse_dialogue_line(self):
        """Test parsing a single dialogue line"""
        line_dict = {
            "c": "你好！",
            "s": "A",
            "p": "Nǐ hǎo!",
            "t": "Hello!",
            "d": "Test description",
            "a": "test.mp3",
            "as": "test_slow.mp3"
        }
        line = parse_dialogue_line_from_dict(line_dict)
        self.assertEqual(line.chinese, "你好！")
        self.assertEqual(line.speaker, "A")

    def test_parse_dialogue_line_minimal(self):
        """Test parsing dialogue line with only required field"""
        line_dict = {"c": "你好！"}
        line = parse_dialogue_line_from_dict(line_dict)
        self.assertEqual(line.chinese, "你好！")
        self.assertIsNone(line.speaker)
        self.assertIsNone(line.pronunciation)

    def test_parse_dialogue(self):
        """Test parsing a single dialogue with multiple lines"""
        lines = [
            {"c": "你好！", "s": "A"},
            {"c": "再见", "s": "B"}
        ]
        dialogue = parse_dialogue_from_dict(lines)
        self.assertEqual(len(dialogue.lines), 2)
        self.assertEqual(dialogue.lines[0].chinese, "你好！")
        self.assertEqual(dialogue.lines[1].chinese, "再见")

    def test_parse_dialogues_valid(self):
        """Test parsing valid dialogues"""
        dialogues = parse_dialogues(self.valid_yaml)
        self.assertEqual(len(dialogues), 2)
        self.assertEqual(len(dialogues[0].lines), 2)
        self.assertEqual(len(dialogues[1].lines), 1)
        self.assertEqual(dialogues[0].lines[0].chinese, "你好！")
        self.assertEqual(dialogues[1].lines[0].chinese, "再见")

    def test_parse_dialogues_minimal(self):
        """Test parsing minimal dialogues"""
        dialogues = parse_dialogues(self.minimal_yaml)
        self.assertEqual(len(dialogues), 1)
        self.assertEqual(len(dialogues[0].lines), 2)
        self.assertEqual(dialogues[0].lines[0].chinese, "你好！")
        self.assertEqual(dialogues[0].lines[1].chinese, "再见")

    def test_parse_dialogues_empty(self):
        """Test parsing empty YAML"""
        dialogues = parse_dialogues("")
        self.assertEqual(dialogues, [])

    def test_parse_dialogues_invalid_structure(self):
        """Test parsing YAML with invalid structure"""
        invalid_yaml = "- not a dictionary"
        with self.assertRaises(DialogueParseError) as context:
            parse_dialogues(invalid_yaml)
        self.assertTrue("Invalid YAML structure" in str(context.exception))

    def test_parse_dialogues_invalid_lines(self):
        """Test parsing dialogue with invalid lines structure"""
        invalid_yaml = """
dialogue1:
    not_a_list: true
"""
        with self.assertRaises(DialogueParseError) as context:
            parse_dialogues(invalid_yaml)
        self.assertTrue("Expected list" in str(context.exception))

    def test_parse_dialogues_invalid_line(self):
        """Test parsing dialogue with invalid line"""
        invalid_yaml = """
dialogue1:
    - s: "A"
      p: "test"
"""
        with self.assertRaises(DialogueParseError) as context:
            parse_dialogues(invalid_yaml)
        self.assertTrue("Missing required field" in str(context.exception))

if __name__ == '__main__':
    unittest.main()