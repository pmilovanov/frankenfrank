import yaml
from dataclasses import dataclass
from typing import Optional, Union, List

@dataclass
class Dialogue:
    chinese: str  # only required field
    speaker: Optional[str] = None
    pronunciation: Optional[str] = None
    translation: Optional[str] = None
    description: Optional[str] = None
    audio: Optional[str] = None
    audio_slow: Optional[str] = None

def parse_dialogue_from_dict(dialogue_dict: dict) -> Union[Dialogue, str]:
    """
    Parse a single dialogue from a dictionary.
    Only 'chinese' field is required, all others are optional.
    Returns either a Dialogue object or an error message string.
    """
    # Check for required 'chinese' field
    if 'c' not in dialogue_dict:
        return "Missing required field: chinese text"

    try:
        return Dialogue(
            chinese=dialogue_dict['c'],
            speaker=dialogue_dict.get('s'),
            pronunciation=dialogue_dict.get('p'),
            translation=dialogue_dict.get('t'),
            description=dialogue_dict.get('d'),
            audio=dialogue_dict.get('a'),
            audio_slow=dialogue_dict.get('as')
        )
    except Exception as e:
        return f"Error creating Dialogue object: {str(e)}"

def parse_dialogues(yaml_text: str) -> List[Union[Dialogue, str]]:
    """
    Parse dialogues from YAML text. Returns a list of either Dialogue objects
    or error message strings for failed parses.
    """
    try:
        dialogues = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        return [f"Error parsing YAML: {str(e)}"]

    # Handle empty YAML case
    if dialogues is None:
        return []

    # Handle single dialogue case
    if isinstance(dialogues, dict):
        dialogues = [dialogues]

    # Handle non-list/non-dict case
    if not isinstance(dialogues, list):
        return [f"Invalid YAML structure. Expected list or dict, got {type(dialogues)}"]

    # Parse each dialogue, collecting both successes and errors
    results = []
    for dialogue in dialogues:
        if not isinstance(dialogue, dict):
            results.append(f"Invalid dialogue format: expected dict, got {type(dialogue)}")
            continue
        results.append(parse_dialogue_from_dict(dialogue))

    return results