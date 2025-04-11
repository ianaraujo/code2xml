#!/usr/bin/env python3
import argparse
import glob
import os
import sys

from xml.etree import ElementTree as ET

def escape_for_xml(text: str) -> str:
    """
    Escapes special characters to ensure the text is XML-safe.
    """
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def collect_files(pattern: str):
    """
    Uses the glob library to collect all files matching the given pattern.
    """
    return glob.glob(pattern, recursive=True)

def build_directory_tree(file_paths):
    """
    Given a list of file paths, builds a nested dictionary structure
    representing the directory tree.
    """
    tree = {}
    cwd = os.getcwd()  # current working directory for relative paths

    for fpath in file_paths:
        relative_path = os.path.relpath(fpath, start=cwd)
        parts = relative_path.split(os.sep)

        current_level = tree

        for part in parts[:-1]:
            if part not in current_level:
                current_level[part] = {}
            
            current_level = current_level[part]

        filename = parts[-1]
        if filename not in current_level:
            # use None to signify “this key is a file, not a directory”
            current_level[filename] = None

    return tree

def add_directory_structure_xml(root_element, directory_tree):
    """
    Adds a <directory_structure> element to the root_element (<project>)
    that reflects the nested directory tree.
    """
    dir_struct_elem = ET.SubElement(root_element, "directory_structure")

    def dict_to_xml(d, parent_xml):
        for name, contents in d.items():
            if contents is None:
                # file
                file_elem = ET.SubElement(parent_xml, "file")
                file_elem.set("name", name)
            else:
                # directory
                dir_elem = ET.SubElement(parent_xml, "directory")
                dir_elem.set("name", name)
                
                dict_to_xml(contents, dir_elem)

    dict_to_xml(directory_tree, dir_struct_elem)

def convert_files_to_xml(file_paths):
    """
    Creates an XML structure:

    <project>
      <directory_structure>
        <directory name="...">
          <file name="..." />
          ...
        </directory>
      </directory_structure>

      <file name="filename1">...</file>
      <file name="filename2">...</file>
      ...
    </project>
    """
    # create the root <project> element
    project_element = ET.Element("project")

    # build and append the <directory_structure>
    directory_tree = build_directory_tree(file_paths)
    add_directory_structure_xml(project_element, directory_tree)

    # append each matching file as <file>
    for fpath in file_paths:
        try:
            with open(fpath, 'r', encoding='utf-8') as infile:
                file_content = infile.read()
        except Exception as e:
            print(f"Warning: Could not read file {fpath}. Skipping. Error: {e}", file=sys.stderr)
            continue

        file_element = ET.SubElement(project_element, "file")
        file_element.set("name", os.path.basename(fpath))

        escaped_content = escape_for_xml(file_content)
        file_element.text = "\n" + escaped_content

    return project_element

def main():
    parser = argparse.ArgumentParser(description="Convert code files to an XML structure (with directory tree).")
    parser.add_argument(
        "--include",
        required=True,
        help="Glob pattern to match the code files (e.g., 'src/**/*.py')."
    )

    args = parser.parse_args()

    # collect file paths matching the user-supplied glob pattern
    file_paths = collect_files(args.include)

    # build the full XML structure
    root_element = convert_files_to_xml(file_paths)

    # convert the ElementTree to a pretty-printed XML string (basic indentation only)
    tree = ET.ElementTree(root_element)

    ET.indent(tree, space="  ", level=0)

    xml_bytes = ET.tostring(tree.getroot(), encoding='utf-8')
    print(xml_bytes.decode('utf-8'))


if __name__ == "__main__":
    main()
