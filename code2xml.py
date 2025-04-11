#!/usr/bin/env python3

import os
import sys
import glob
import argparse
from pathlib import Path

from xml.etree import ElementTree as ET

def escape_for_xml(text: str) -> str:
    """
    Escapes special characters to ensure the text is XML-safe.
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def count_tokens(text: str) -> int:
    """
    Estimates the number of tokens in the text using a simple approximation.
    This is a rough estimate - actual token count may vary by model.
    """
    return len(text) // 4

def collect_files_from_input(input_path: str) -> list:
    """
    Collect files based on user's input type:
    - Glob pattern (e.g., **/*.py)
    - Directory path (e.g., /src/utils/)
    - Individual file path (e.g., /src/main.py)
    """
    path = Path(input_path)
    
    if path.is_file():
        return [str(path)]
    
    elif path.is_dir():
        # collect all files recursively from directory
        return [str(p) for p in path.rglob('*') if p.is_file()]
    
    else:
        return glob.glob(input_path, recursive=True)

def convert_files_to_xml(file_paths):
    """
    Creates an XML structure:
    <context>
        <file name="filename1">...</file>
        <file name="filename2">...</file>
        ...
    </context>
    """
    # create the root <context> element
    context_element = ET.Element("context")

    # append each matching file as <file>
    for fpath in file_paths:
        try:
            with open(fpath, 'r', encoding='utf-8') as infile:
                file_content = infile.read()
        except Exception as e:
            print(f"Warning: Could not read file {fpath}. Skipping. Error: {e}", file=sys.stderr)
            continue

        file_element = ET.SubElement(context_element, "file")
        file_element.set("name", os.path.basename(fpath))
        
        escaped_content = escape_for_xml(file_content)
        file_element.text = "\n" + escaped_content

    return context_element

def main():
    parser = argparse.ArgumentParser(description="Convert code files to an XML structure.")
    parser.add_argument(
        "-i", "--include",
        nargs='+',
        required=True,
        help="""
            Glob patterns, directories, or file paths to include. 
            Multiple inputs can be space-separated. 
            Examples: '-i **/*.py /src/utils/ main.py'
            Note: Use quotes around the pattern to prevent shell expansion.
            """
    )

    args = parser.parse_args()
    
    # collect all file paths from all inputs
    all_files = set()  # Using set to avoid duplicates
    for input_path in args.include:
        files = collect_files_from_input(input_path)
        all_files.update(files)

    # build the XML structure
    root_element = convert_files_to_xml(sorted(all_files))  # Sort for consistent output

    # convert the ElementTree to a pretty-printed XML string
    tree = ET.ElementTree(root_element)
    
    ET.indent(tree, space="  ", level=0)

    xml_string = ET.tostring(tree.getroot(), encoding='utf-8').decode('utf-8')
    
    #### PRINTING XML ####
    print(xml_string)
    
    # Print token count estimate
    token_count = count_tokens(xml_string)
    print(f"\nEstimated token count: {token_count}", file=sys.stderr)

if __name__ == "__main__":
    main()
