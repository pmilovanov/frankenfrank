import unittest
from convert_dialogues import convert_dialogue_format

class TestDialogueConversion(unittest.TestCase):
    def test_convert_basic(self):
        """Test basic conversion of a single dialogue"""
        old_format = {
            "1 - Что ты думаешь?": [
                {
                    "s": "A",
                    "c": "你觉得这个怎么样？",
                    "p": "Nǐ juéde zhège zěnmeyàng?",
                    "t": "Что ты об этом думаешь?"
                }
            ]
        }

        expected = [
            {
                "title": "1 - Что ты думаешь?",
                "lines": [
                    {
                        "s": "A",
                        "c": "你觉得这个怎么样？",
                        "p": "Nǐ juéde zhège zěnmeyàng?",
                        "t": "Что ты об этом думаешь?"
                    }
                ]
            }
        ]

        result = convert_dialogue_format(old_format)
        self.assertEqual(result, expected)

    def test_convert_multiple_dialogues(self):
        """Test conversion of multiple dialogues"""
        old_format = {
            "Dialogue 1": [
                {"s": "A", "c": "你好"},
                {"s": "B", "c": "再见"}
            ],
            "Dialogue 2": [
                {"s": "A", "c": "早上好"}
            ]
        }

        expected = [
            {
                "title": "Dialogue 1",
                "lines": [
                    {"s": "A", "c": "你好"},
                    {"s": "B", "c": "再见"}
                ]
            },
            {
                "title": "Dialogue 2",
                "lines": [
                    {"s": "A", "c": "早上好"}
                ]
            }
        ]

        result = convert_dialogue_format(old_format)
        self.assertEqual(result, expected)

    def test_convert_empty(self):
        """Test conversion of empty dictionary"""
        old_format = {}
        expected = []

        result = convert_dialogue_format(old_format)
        self.assertEqual(result, expected)

    def test_convert_complex_dialogue(self):
        """Test conversion with all possible fields"""
        old_format = {
            "Complex dialogue": [
                {
                    "s": "A",
                    "c": "text",
                    "p": "pinyin",
                    "t": "translation",
                    "d": "description",
                    "a": "audio.mp3",
                    "as": "audio_slow.mp3"
                }
            ]
        }

        expected = [
            {
                "title": "Complex dialogue",
                "lines": [
                    {
                        "s": "A",
                        "c": "text",
                        "p": "pinyin",
                        "t": "translation",
                        "d": "description",
                        "a": "audio.mp3",
                        "as": "audio_slow.mp3"
                    }
                ]
            }
        ]

        result = convert_dialogue_format(old_format)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()