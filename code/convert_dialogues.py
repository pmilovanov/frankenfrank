#!/usr/bin/env python3
import argparse
import json
import sys
import yaml
from typing import List, Dict

def convert_dialogue_format(old_format: Dict) -> List[Dict]:
    """
    Convert dialogues from old dictionary format to new list format.

    Old format:
    {
        "dialogue title": [
            {"s": "A", "c": "text", ...},
            ...
        ],
        ...
    }

    New format:
    [
        {
            "title": "dialogue title",
            "lines": [
                {"s": "A", "c": "text", ...},
                ...
            ]
        },
        ...
    ]
    """
    new_format = []

    for title, lines in old_format.items():
        new_dialogue = {
            "title": title,
            "lines": lines
        }
        new_format.append(new_dialogue)

    return new_format

def main():
    parser = argparse.ArgumentParser(description='Convert dialogue files from old YAML to new JSON format')
    parser.add_argument('input', type=str, help='Input YAML file in old format')
    parser.add_argument('-o', '--output', type=str, help='Output JSON file (default: stdout)')
    parser.add_argument('--indent', type=int, default=2, help='JSON indentation (default: 2)')
    parser.add_argument('--ensure-ascii', action='store_true',
                        help='Ensure ASCII output in JSON (default: False, allowing Unicode)')
    args = parser.parse_args()

    # Read input file
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            input_text = f.read()
    except FileNotFoundError:
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading input file: {e}", file=sys.stderr)
        sys.exit(1)

    # Parse YAML and convert format
    try:
        old_format = yaml.safe_load(input_text)
        if old_format is None:  # Empty file case
            new_format = []
        elif not isinstance(old_format, dict):
            print("Error: Input file must contain a YAML dictionary/object", file=sys.stderr)
            sys.exit(1)
        else:
            new_format = convert_dialogue_format(old_format)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error converting format: {e}", file=sys.stderr)
        sys.exit(1)

    # Generate JSON output
    try:
        output_json = json.dumps(
            new_format,
            ensure_ascii=args.ensure_ascii,
            indent=args.indent,
            allow_nan=False  # Ensure valid JSON output
        )

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(output_json)
                f.write('\n')  # Add trailing newline
        else:
            print(output_json)

    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()