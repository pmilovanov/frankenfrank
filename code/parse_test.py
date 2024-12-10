import unittest
import yaml
import json
from io import StringIO
from parse import (
    DialogueLine,
    Dialogue,
    parse_dialogues,
    parse_dialogue_from_dict,
    parse_dialogue_line_from_dict,
    save_dialogues,
    DialogueParseError
)

class TestDialogueParsing(unittest.TestCase):
    def setUp(self):
        # Sample valid dialogue in JSON format
        self.valid_yaml = """[
  {
    "title": "Что ты думаешь?",
    "lines": [
      {
        "s": "A",
        "c": "你觉得这个怎么样？",
        "p": "Nǐ juéde zhège zěnmeyàng?",
        "t": "Что ты об этом думаешь?",
        "d": "觉得 (juéde) \\"думать/чувствовать\\", часто используется, чтобы обозначить мнение"
      },
      {
        "s": "B",
        "c": "我觉得很好。",
        "p": "Wǒ juéde hěn hǎo.",
        "t": "Я думаю, что это хорошо."
      }
    ]
  },
  {
    "title": "You look very happy!",
    "lines": [
      {
        "s": "A",
        "c": "你今天看起来很高兴。",
        "p": "Nǐ jīntiān kàn qǐlái hěn gāoxìng.",
        "t": "Сегодня ты выглядишь очень счастливым.",
        "d": "看起来 (kàn qǐlái) значит \\"выглядеть\\", часто используется для описания внешнего вида"
      }
    ]
  }
]"""
        # Sample minimal dialogue in JSON format
        self.minimal_yaml = """[
  {
    "lines": [
      {
        "c": "你好！"
      },
      {
        "c": "再见"
      }
    ]
  }
]"""

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
        """Test parsing a single dialogue with title and lines"""
        dialogue_dict = {
            "title": "Test Dialogue",
            "lines": [
                {"c": "你好！", "s": "A"},
                {"c": "再见", "s": "B"}
            ]
        }
        dialogue = parse_dialogue_from_dict(dialogue_dict)
        self.assertEqual(dialogue.title, "Test Dialogue")
        self.assertEqual(len(dialogue.lines), 2)
        self.assertEqual(dialogue.lines[0].chinese, "你好！")
        self.assertEqual(dialogue.lines[1].chinese, "再见")

    def test_parse_dialogues_valid(self):
        """Test parsing valid dialogues in new format"""
        dialogues = parse_dialogues(self.valid_yaml)
        self.assertEqual(len(dialogues), 2)
        self.assertEqual(dialogues[0].title, "Что ты думаешь?")
        self.assertEqual(len(dialogues[0].lines), 2)
        self.assertEqual(dialogues[1].title, "You look very happy!")
        self.assertEqual(len(dialogues[1].lines), 1)
        self.assertEqual(dialogues[0].lines[0].chinese, "你觉得这个怎么样？")
        self.assertEqual(dialogues[1].lines[0].chinese, "你今天看起来很高兴。")

    def test_parse_dialogues_minimal(self):
        """Test parsing minimal dialogues"""
        dialogues = parse_dialogues(self.minimal_yaml)
        self.assertEqual(len(dialogues), 1)
        self.assertIsNone(dialogues[0].title)
        self.assertEqual(len(dialogues[0].lines), 2)
        self.assertEqual(dialogues[0].lines[0].chinese, "你好！")
        self.assertEqual(dialogues[0].lines[1].chinese, "再见")

    def test_parse_dialogues_empty(self):
        """Test parsing empty YAML"""
        dialogues = parse_dialogues("")
        self.assertEqual(dialogues, [])

    def test_parse_dialogues_invalid_structure(self):
        """Test parsing invalid JSON structure"""
        invalid_yaml = "[\"not an object\"]"
        with self.assertRaises(DialogueParseError) as context:
            parse_dialogues(invalid_yaml)
        self.assertTrue("Error in dialogue" in str(context.exception))

    def test_parse_dialogues_missing_lines(self):
        """Test parsing dialogue with missing lines field"""
        invalid_yaml = """[
  {
    "title": "Test Dialogue",
    "no_lines_field": []
  }
]"""
        with self.assertRaises(DialogueParseError) as context:
            parse_dialogues(invalid_yaml)
        self.assertTrue("Missing required field: 'lines'" in str(context.exception))

    def test_parse_dialogues_invalid_lines(self):
        """Test parsing dialogue with invalid lines structure"""
        invalid_yaml = """[
  {
    "title": "Test Dialogue",
    "lines": "not a list"
  }
]"""
        with self.assertRaises(DialogueParseError) as context:
            parse_dialogues(invalid_yaml)
        self.assertTrue("Expected list" in str(context.exception))

    def test_parse_dialogues_invalid_line(self):
        """Test parsing dialogue with invalid line"""
        invalid_yaml = """[
  {
    "title": "Test Dialogue",
    "lines": [
      {
        "s": "A",
        "p": "test"
      }
    ]
  }
]"""
        with self.assertRaises(DialogueParseError) as context:
            parse_dialogues(invalid_yaml)
        self.assertTrue("Missing required field" in str(context.exception))

    # New tests for serialization functionality
    def test_save_dialogues_json(self):
        """Test saving dialogues to JSON"""
        dialogues = parse_dialogues(self.valid_yaml)
        output = StringIO()
        save_dialogues(dialogues, output, format='json')
        output.seek(0)

        # Parse the output and verify
        saved_content = json.loads(output.getvalue())
        self.assertEqual(len(saved_content), 2)
        self.assertEqual(saved_content[0]["title"], "Что ты думаешь?")
        self.assertEqual(saved_content[0]["lines"][0]["c"], "你觉得这个怎么样？")

    def test_save_dialogues_yaml(self):
        """Test saving dialogues to YAML"""
        dialogues = parse_dialogues(self.valid_yaml)
        output = StringIO()
        save_dialogues(dialogues, output, format='yaml')
        output.seek(0)

        # Parse the output and verify
        saved_content = yaml.safe_load(output.getvalue())
        self.assertEqual(len(saved_content), 2)
        self.assertEqual(saved_content[0]["title"], "Что ты думаешь?")
        self.assertEqual(saved_content[0]["lines"][0]["c"], "你觉得这个怎么样？")

    def test_save_dialogues_roundtrip(self):
        """Test that saving and then loading dialogues preserves all information"""
        original_dialogues = parse_dialogues(self.valid_yaml)

        # Save to JSON and reload
        output = StringIO()
        save_dialogues(original_dialogues, output, format='json')
        output.seek(0)
        reloaded_dialogues = parse_dialogues(output.getvalue())

        # Compare each dialogue
        self.assertEqual(len(original_dialogues), len(reloaded_dialogues))
        for orig, reloaded in zip(original_dialogues, reloaded_dialogues):
            self.assertEqual(orig.title, reloaded.title)
            self.assertEqual(len(orig.lines), len(reloaded.lines))
            for orig_line, reloaded_line in zip(orig.lines, reloaded.lines):
                self.assertEqual(orig_line.chinese, reloaded_line.chinese)
                self.assertEqual(orig_line.speaker, reloaded_line.speaker)
                self.assertEqual(orig_line.pronunciation, reloaded_line.pronunciation)
                self.assertEqual(orig_line.translation, reloaded_line.translation)
                self.assertEqual(orig_line.description, reloaded_line.description)
                self.assertEqual(orig_line.audio, reloaded_line.audio)
                self.assertEqual(orig_line.audio_slow, reloaded_line.audio_slow)

    def test_save_dialogues_invalid_format(self):
        """Test that saving with invalid format raises ValueError"""
        dialogues = parse_dialogues(self.minimal_yaml)
        with self.assertRaises(ValueError):
            save_dialogues(dialogues, StringIO(), format='invalid')

if __name__ == '__main__':
    unittest.main()