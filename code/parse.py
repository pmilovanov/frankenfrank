import yaml
import json
from dataclasses import dataclass
from typing import Dict, List, Union, TextIO, Any

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

    # Map between internal attribute names and external field names
    _field_map = {
        'chinese': 'c',
        'speaker': 's',
        'pronunciation': 'p',
        'translation': 't',
        'description': 'd',
        'audio': 'a',
        'audio_slow': 'as'
    }
    _reverse_field_map = {v: k for k, v in _field_map.items()}

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with short field names, excluding None values"""
        result = {}
        for internal_name, value in vars(self).items():
            if value is not None and internal_name in self._field_map:
                result[self._field_map[internal_name]] = value
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DialogueLine':
        """Create instance from dictionary with short field names"""
        kwargs = {}
        for short_name, value in data.items():
            if short_name in cls._reverse_field_map:
                kwargs[cls._reverse_field_map[short_name]] = value
        return cls(**kwargs)

@dataclass
class Dialogue:
    lines: List[DialogueLine]
    title: str = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values"""
        result = {
            "lines": [line.to_dict() for line in self.lines]
        }
        if self.title is not None:
            result["title"] = self.title
        return result

def parse_dialogue_line_from_dict(line_dict: dict) -> DialogueLine:
    """
    Parse a single dialogue line from a dictionary.
    Raises DialogueParseError if the line is invalid.
    """
    if not isinstance(line_dict, dict):
        raise DialogueParseError(f"Expected dict, got {type(line_dict)}")

    if 'c' not in line_dict:
        raise DialogueParseError("Missing required field: chinese text ('c')")

    return DialogueLine.from_dict(line_dict)

def parse_dialogue_from_dict(dialogue_dict: dict) -> Dialogue:
    """
    Parse a dialogue from a dictionary containing title and lines.
    Raises DialogueParseError if any line is invalid.
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
        title=dialogue_dict.get('title')
    )

def parse_dialogues(yaml_text: str) -> List[Dialogue]:
    """
    Parse dialogues from YAML/JSON text. Expects a list of dialogue objects,
    each containing a 'lines' list and optional 'title' field.

    Args:
        yaml_text: YAML/JSON formatted string containing dialogues

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

def save_dialogues(dialogues: List[Dialogue], output: Union[str, TextIO], format: str = 'json', **kwargs) -> None:
    """
    Save dialogues to a file or file-like object in the specified format.

    Args:
        dialogues: List of Dialogue objects to save
        output: Filename (str) or file-like object to write to
        format: Output format ('json' or 'yaml')
        **kwargs: Additional arguments passed to json.dumps or yaml.dump

    Raises:
        ValueError: If format is not 'json' or 'yaml'
        IOError: If there's an error writing to the file
    """
    if format not in ('json', 'yaml'):
        raise ValueError("Format must be 'json' or 'yaml'")

    # Convert dialogues to list of dicts
    data = [dialogue.to_dict() for dialogue in dialogues]

    # Set default arguments for each format
    if format == 'json':
        kwargs.setdefault('ensure_ascii', False)
        kwargs.setdefault('indent', 2)
        kwargs.setdefault('allow_nan', False)
        output_text = json.dumps(data, **kwargs)
    else:  # yaml
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('sort_keys', False)
        output_text = yaml.dump(data, **kwargs)

    # Handle string filename or file-like object
    if isinstance(output, str):
        with open(output, 'w', encoding='utf-8') as f:
            f.write(output_text)
            if not output_text.endswith('\n'):
                f.write('\n')
    else:
        output.write(output_text)
        if not output_text.endswith('\n'):
            output.write('\n')