import yaml
from dataclasses import dataclass
from typing import Dict, List

class DialogueParseError(Exception):
    """Raised when there's an error parsing dialogues"""
    pass

@dataclass
class DialogueLine:
    chinese: str
    speaker: str = None
    pronunciation: str = None
    translation: str = None
    description: str = None
    audio: str = None
    audio_slow: str = None

@dataclass
class Dialogue:
    lines: List[DialogueLine]

def parse_dialogue_line_from_dict(line_dict: dict) -> DialogueLine:
    """
    Parse a single dialogue line from a dictionary.
    Raises DialogueParseError if the line is invalid.
    """
    if not isinstance(line_dict, dict):
        raise DialogueParseError(f"Expected dict, got {type(line_dict)}")

    if 'c' not in line_dict:
        raise DialogueParseError("Missing required field: chinese text ('c')")

    return DialogueLine(
        chinese=line_dict['c'],
        speaker=line_dict.get('s'),
        pronunciation=line_dict.get('p'),
        translation=line_dict.get('t'),
        description=line_dict.get('d'),
        audio=line_dict.get('a'),
        audio_slow=line_dict.get('as')
    )

def parse_dialogue_from_dict(lines: List[dict]) -> Dialogue:
    """
    Parse a list of dialogue lines into a Dialogue object.
    Raises DialogueParseError if any line is invalid.
    """
    if not isinstance(lines, list):
        raise DialogueParseError(f"Expected list of dialogue lines, got {type(lines)}")

    dialogue_lines = []
    for i, line in enumerate(lines):
        try:
            dialogue_lines.append(parse_dialogue_line_from_dict(line))
        except DialogueParseError as e:
            raise DialogueParseError(f"Error in line {i}: {str(e)}")

    return Dialogue(lines=dialogue_lines)

def parse_dialogues(yaml_text: str) -> List[Dialogue]:
    """
    Parse dialogues from YAML text. Expects a dictionary where keys are dialogue titles
    and values are lists of dialogue lines.

    Raises:
        yaml.YAMLError: If YAML parsing fails
        DialogueParseError: If dialogue structure or content is invalid
    """
    content = yaml.safe_load(yaml_text)

    # Handle empty YAML case
    if content is None:
        return []

    # Validate top-level structure is a dictionary
    if not isinstance(content, dict):
        raise DialogueParseError(f"Invalid YAML structure. Expected dict of dialogues, got {type(content)}")

    # Parse all dialogues
    results = []
    for title, dialogue_lines in content.items():
        try:
            results.append(parse_dialogue_from_dict(dialogue_lines))
        except DialogueParseError as e:
            raise DialogueParseError(f"Error in dialogue '{title}': {str(e)}")

    return results