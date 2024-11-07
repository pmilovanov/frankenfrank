#!/usr/bin/env python3
import yaml
import argparse
from typing import Dict, List, Union

def format_dialogue(yaml_text: str) -> str:
    """
    Formats YAML dialogue data to show just the dialogue name, speakers, and Chinese text.
    
    Args:
        yaml_text: String containing YAML formatted dialogue data
    
    Returns:
        Formatted string with dialogue name and speaker lines
    """
    # Parse YAML string
    try:
        dialogues = yaml.safe_load(yaml_text)
    except yaml.YAMLError as e:
        return f"Error parsing YAML: {str(e)}"
    
    # Handle single dialogue case
    if isinstance(dialogues, Dict):
        dialogues = [dialogues]
    
    formatted_output = []
    
    for dialogue in dialogues:
        for key, value in dialogue.items():
            formatted_output.append("")
            # Add dialogue name
            formatted_output.append(f"{key}:")
            
            # Add each line of dialogue
            for line in value:
                speaker = line['s']
                chinese = line['c']
                formatted_output.append(f"{speaker}: {chinese}")
    
    return "\n".join(formatted_output)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Format YAML dialogue files to show speakers and Chinese text.')
    parser.add_argument('-f', '--file', required=True, help='Input YAML file path')
    parser.add_argument('-o', '--output', help='Output file path (optional, defaults to stdout)')
    args = parser.parse_args()

    try:
        # Read input file
        with open(args.file, 'r', encoding='utf-8') as f:
            yaml_text = f.read()
        
        # Format the dialogue
        formatted_text = format_dialogue(yaml_text)
        
        # Handle output
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(formatted_text)
            print(f"Output written to {args.output}")
        else:
            print(formatted_text)
            
    except FileNotFoundError:
        print(f"Error: Could not find file '{args.file}'")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
