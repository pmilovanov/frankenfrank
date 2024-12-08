
# A dataclass to store the parsed data from a json like this
#
#     {
#       "s": "A",
#       "c": "你好！",
#       "p": "Nǐ hǎo!",
#       "t": "Здравствуй!",
#       "d": "Буквально означает «ты хороший». Произносится как nǐ háo, когда следуют подряд два слова третьим тоном",
#       "a": "ecde115cdca96a1a181db6b9e88c1e1f6e208ca77916627cc8a9fa02b39d0692.mp3",
#       "as": "ecde115cdca96a1a181db6b9e88c1e1f6e208ca77916627cc8a9fa02b39d0692_slow.mp3"
#     }
#
#  s: speaker
#  c: text in chinese
#  p: pronunciation (pinyin)
#  t: translation
#  d: description
#  a: audio file
#  as: audio file slow

from dataclasses import dataclass

@dataclass
class Dialogue:
    speaker: str
    chinese: str
    pronunciation: str
    translation: str
    description: str
    audio: str
    audio_slow: str

def parse_dialogue_from_dict(dialogue_dict: dict) -> Dialogue:
    return Dialogue(
        speaker=dialogue_dict['s'],
        chinese=dialogue_dict['c'],
        pronunciation=dialogue_dict['p'],
        translation=dialogue_dict['t'],
        description=dialogue_dict['d'],
        audio=dialogue_dict['a'],
        audio_slow=dialogue_dict['as']
    )

# parse a list of dialogues from yaml
def parse_dialogues(yaml_text: str) -> list[Dialogue]:
    try:
        dialogues = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        return [f"Error parsing YAML: {str(e)}"]

    # Handle single dialogue case
    if isinstance(dialogues, dict):
        dialogues = [dialogues]

    return [parse_dialogue_from_dict(dialogue) for dialogue in dialogues]