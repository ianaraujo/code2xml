#!/usr/bin/env python3

import os
import sys
import glob
import argparse
import subprocess
import shutil

from pathlib import Path
from xml.etree import ElementTree as ET

def escape_for_xml(text: str) -> str:
    """
    Escapes special characters to ensure the text is XML-safe.
    """
    return (text.replace("&amp;amp;", "&amp;amp;amp;")
                .replace("&amp;lt;", "&amp;amp;lt;")
                .replace("&amp;gt;", "&amp;amp;gt;"))

def count_tokens(text: str) -> int:
    """
    Estimates the number of tokens in the text using a simple approximation.
    This is a rough estimate - actual token count may vary by model.
    """
    return len(text) // 4

def copy(text: str) -> None:
    try:
        if shutil.which("clip.exe"):
            subprocess.run("clip.exe", input=text.encode('utf-8'), check=True)
            print("\nXML output copied to clipboard.")
    except Exception as e:
        print(f"\nWarning: Could not copy to clipboard. Error: {e}", file=sys.stderr)
        print("\nYou can manually copy the XML output from the console.")
        return

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
        <file name="filename1">
          ... file content with a newline at the start and end ...
        </file>
        <file name="filename2">
          ... file content ...
        </file>
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
        
        # Add newlines before and after the file content.
        escaped_content = escape_for_xml(file_content)
        file_element.text = "\n" + escaped_content + "\n"

    return context_element

def format_xml(elem: ET.Element) -> str:
    """
    Custom formatter that converts an ElementTree Element into a string according to:
    
    - Each opening and closing tag appears on its own line.
    - No extra indentation is added to XML tags.
    - If the element is a <file>, its text content is indented (here with two spaces per line)
      and ensured to begin and end with a blank line.
    """
    # Build the opening tag with attributes (if any)
    attr_text = " ".join(f'{key}="{value}"' for key, value in elem.attrib.items())
    if attr_text:
        open_tag = f"<{elem.tag} {attr_text}>"
    else:
        open_tag = f"<{elem.tag}>"
        
    lines = [open_tag]

    # Process element text.
    if elem.text and elem.text.strip():
        # For file tags, indent each nonempty line by two spaces.
        if elem.tag == "file":
            # We assume elem.text already has newlines at the start and end.
            text_lines = elem.text.splitlines()
            for line in text_lines:
                if line.strip():
                    lines.append("  " + line)
                else:
                    # preserve blank lines
                    lines.append("")
        else:
            lines.extend(elem.text.splitlines())
    
    # Process all child elements recursively.
    for child in elem:
        child_formatted = format_xml(child)
        # Add each line of the child formatting.
        lines.extend(child_formatted.splitlines())
    
    # Add closing tag on its own line.
    closing_tag = f"</{elem.tag}>"
    lines.append(closing_tag)
    
    return "\n".join(lines)

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
    
    # Collect all file paths from all inputs (avoid duplicates)
    all_files = set()
    for input_path in args.include:
        files = collect_files_from_input(input_path)
        all_files.update(files)

    # Build the XML structure
    root_element = convert_files_to_xml(sorted(all_files))  # sort for consistent output

    # Use our custom formatter instead of ET.tostring
    xml_string = format_xml(root_element)

    print(xml_string)  # print to console
    copy(xml_string)   # try copying to clipboard
    
    # Print token count estimate (sent to stderr)
    token_count = count_tokens(xml_string)
    print(f"\nEstimated token count: {token_count}", file=sys.stderr)

if __name__ == "__main__":
    main()
