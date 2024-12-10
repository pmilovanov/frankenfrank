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
    title: str = None  # New field for the dialogue title

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

def parse_dialogue_from_dict(dialogue_dict: dict) -> Dialogue:
    """
    Parse a dialogue from a dictionary containing title and lines.

    Args:
        dialogue_dict: Dictionary with 'lines' (required) and 'title' (optional) fields

    Returns:
        Dialogue object with parsed lines and title

    Raises:
        DialogueParseError: If dialogue structure or content is invalid
    """
    if not isinstance(dialogue_dict, dict):
        raise DialogueParseError(f"Expected dict, got {type(dialogue_dict)}")

    if 'lines' not in dialogue_dict:
        raise DialogueParseError("Missing required field: 'lines'")

    if not isinstance(dialogue_dict['lines'], list):
        raise DialogueParseError(f"Expected list of dialogue lines, got {type(dialogue_dict['lines'])}")

    dialogue_lines = []
    for i, line in enumerate(dialogue_dict['lines']):
        try:
            dialogue_lines.append(parse_dialogue_line_from_dict(line))
        except DialogueParseError as e:
            raise DialogueParseError(f"Error in line {i}: {str(e)}")

    return Dialogue(
        lines=dialogue_lines,
        title=dialogue_dict.get('title')  # Optional title field
    )

def parse_dialogues(yaml_text: str) -> List[Dialogue]:
    """
    Parse dialogues from YAML text. Expects a list of dialogue objects,
    each containing a 'lines' list and optional 'title' field.

    Args:
        yaml_text: YAML formatted string containing dialogues

    Returns:
        List of Dialogue objects

    Raises:
        yaml.YAMLError: If YAML parsing fails
        DialogueParseError: If dialogue structure or content is invalid
    """
    content = yaml.safe_load(yaml_text)

    # Handle empty YAML case
    if content is None:
        return []

    # Validate top-level structure is a list
    if not isinstance(content, list):
        raise DialogueParseError(f"Invalid YAML structure. Expected list of dialogues, got {type(content)}")

    # Parse all dialogues
    results = []
    for i, dialogue_dict in enumerate(content):
        try:
            results.append(parse_dialogue_from_dict(dialogue_dict))
        except DialogueParseError as e:
            raise DialogueParseError(f"Error in dialogue {i}: {str(e)}")

    return results