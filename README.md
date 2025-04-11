# code2xml

`code2xml` is a utility designed to facilitate the generation of code context for Large Language Models (LLMs). It converts source code files into an XML representation, making it easier to select and format project files as XML prompts for LLMs. This tool preserves the directory structure and content of your code files within an XML format, which is particularly useful for:

- Providing code context to LLMs
- Structuring code for analysis by LLMs
- Generating XML prompts from code

The tool scans your codebase based on provided glob patterns and creates an XML tree that represents both the directory structure and the content of each file, optimized for LLM consumption.

## TO-DO

- [] Add support for multiple `--include` or `-i` calls

## Installation

### Prerequisites

- Python 3.9 or higher

### Installation Steps

1. Clone this repository:

```
git clone https://github.com/yourusername/code2xml.git
cd code2xml
```

2. Install locally using `pip`:
   ```
   pip install .
   ```

3. Optional: Install locally using `pip` developer mode:

  If you’re actively editing the script and don’t want to re-install on every change, use the editable install flag.
  
  ```
  pip install -e .
  ```

#### Alternative

1. Make the script executable:
   ```
   chmod +x code2xml.py
   ```

2. Optional: Create a symlink to use it globally:
   ```
   sudo ln -s $(pwd)/code2xml.py /usr/local/bin/code2xml
   ```

## Usage

### Basic Usage

Run the script with the `--include` parameter followed by a glob pattern to match the files you want to convert:

```
code2xml --include "src/**/*.py"
```

This will output the XML representation of all Python files in the `src` directory and its subdirectories to standard output.

### Save Output to File

To save the output to a file:

```
code2xml --include "src/**/*.py" > output.txt
```

### Examples

Convert all Python files in the current directory:
```
code2xml --include "*.py"
```

Convert all JavaScript and TypeScript files in a project:
```
code2xml --include "project/**/*.{js,ts}"
```

Convert all source files except node_modules directory:
```
code2xml --include "!(node_modules)/**/*.*"
```

## XML Output Structure

The generated XML has the following structure:

```xml
<project>
  <directory_structure>
    <directory name="dir1">
      <directory name="dir2">
        <file name="file1.py" />
      </directory>
      <file name="file2.py" />
    </directory>
  </directory_structure>

  <file name="file1.py">
    # file content goes here
  </file>
  <file name="file2.py">
    # file content goes here
  </file>
</project>
```

## License

[MIT License](LICENSE)