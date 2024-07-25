#SECTION: Imports
import os
import argparse
import fnmatch
import logging
from datetime import datetime

#SECTION: Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class FileProcessingError(Exception):
    """Custom exception class for file processing errors."""
    pass

#SECTION: File Reading Function
def read_file_content(file_path):
    """Read and return the content of a file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        logging.error(f"Error reading file {file_path}: {e}")
        raise FileProcessingError(f"Unable to read file: {file_path}")

#SECTION: Gitignore Handling
def parse_gitignore(directory):
    """
    Parse .gitignore file and return a list of patterns.
    
    Args:
    directory (str): The directory containing the .gitignore file.
    
    Returns:
    list: A list of patterns from the .gitignore file.
    """
    gitignore_path = os.path.join(directory, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r') as gitignore_file:
            for line in gitignore_file:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

#SECTION: File Collection Function
def collect_files(directory, recursive=False, ignore_patterns=None):
    """
    Collect files from the given directory, respecting .gitignore if provided.
    
    Args:
    directory (str): The directory to collect files from.
    recursive (bool): Whether to recursively collect files from subdirectories.
    ignore_patterns (list): List of patterns to ignore, typically from .gitignore.
    
    Returns:
    generator: A generator yielding file paths that are not ignored.
    """
    def is_ignored(file_path):
        """
        Check if a file should be ignored based on .gitignore patterns.
        
        Args:
        file_path (str): The path of the file to check.
        
        Returns:
        bool: True if the file should be ignored, False otherwise.
        """
        if not ignore_patterns:
            return False
        
        rel_path = os.path.relpath(file_path, directory)
        return any(fnmatch.fnmatch(rel_path, pattern) or 
                   fnmatch.fnmatch(os.path.basename(rel_path), pattern) 
                   for pattern in ignore_patterns)

    if recursive:
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if not is_ignored(file_path):
                    yield file_path
    else:
        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            if os.path.isfile(file_path) and not is_ignored(file_path):
                yield file_path

#SECTION: Argument Parsing Function
def parse_arguments():
    """
    Parse command-line arguments.
    
    Returns:
    argparse.Namespace: An object containing the parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Combine files into a single Markdown document.")
    parser.add_argument("-o", "--output", default="combined_files.md", help="Output file name")
    parser.add_argument("-a", "--all", action="store_true", help="Include all files without confirmation")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively process subdirectories")
    parser.add_argument("-d", "--directory", default=".", help="Source directory to process")
    parser.add_argument("--ignore-gitignore", action="store_true", help="Ignore .gitignore file")
    return parser.parse_args()

#SECTION: User Interaction Functions
def get_user_confirmation(filename):
    """
    Ask the user if they want to include a file in the output.
    
    Args:
    filename (str): The name of the file to confirm.
    
    Returns:
    bool: True if the user wants to include the file, False otherwise.
    """
    while True:
        response = input(f"Include '{filename}' in the output? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Invalid input. Please enter 'y' for yes or 'n' for no.")

#SECTION: Table of Contents Generation
def generate_toc(files):
    """
    Generate a table of contents in Markdown format.
    
    Args:
    files (list): A list of filenames to include in the TOC.
    
    Returns:
    str: A Markdown-formatted table of contents.
    """
    toc = "# Table of Contents\n\n"
    for file in files:
        # Create a link-friendly version of the filename
        link = file.replace(' ', '-').replace('.', '')
        toc += f"- [{file}](#{link})\n"
    toc += "\n"  # Add an extra newline for separation
    return toc

#SECTION: Language Identification
def get_language_identifier(filename):
    """
    Determine the programming language based on the file extension.
    
    Args:
    filename (str): The name of the file.
    
    Returns:
    str: A language identifier for Markdown code blocks.
    """
    extension = filename.split('.')[-1].lower()
    language_map = {
        'py': 'python',
        'js': 'javascript',
        'html': 'html',
        'css': 'css',
        'java': 'java',
        'c': 'c',
        'cpp': 'cpp',
        'md': 'markdown',
        'txt': 'text',
        'json': 'json',
        'xml': 'xml',
        'sql': 'sql',
        'sh': 'bash',
        'yaml': 'yaml',
        'yml': 'yaml',
        # Add more mappings as needed
    }
    return language_map.get(extension, '')  # Return empty string if extension not found

#SECTION: Metadata
def generate_metadata():
    """Generate metadata including timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return f"Generated on: {timestamp}\n"

#SECTION: Main Function
def combine_files_to_markdown(output_file='combined_files.md', include_all=False, directory='.', recursive=False, ignore_gitignore=False):
    """
    Combine user-selected files into a single Markdown file.
    
    Args:
    output_file (str): Name of the output Markdown file.
    include_all (bool): If True, include all files without user confirmation.
    directory (str): Source directory to process.
    recursive (bool): If True, recursively process subdirectories.
    ignore_gitignore (bool): If True, ignore .gitignore file.
    
    Raises:
    Exception: If an error occurs during file combination.
    """
    try:
        ignore_patterns = None if ignore_gitignore else parse_gitignore(directory)
        files = collect_files(directory, recursive, ignore_patterns)
        script_name = os.path.basename(__file__)
        files = [f for f in files if os.path.basename(f) != script_name and os.path.abspath(f) != os.path.abspath(output_file)]
        
        files_to_include = []
        for filename in files:
            if include_all or get_user_confirmation(filename):
                files_to_include.append(filename)
        
        with open(output_file, 'w') as outfile:
            # Write metadata
            outfile.write("# File Combination Metadata\n")
            outfile.write("```\n")
            outfile.write(generate_metadata())
            outfile.write("```\n\n")
            
            # Write table of contents
            outfile.write(generate_toc(files_to_include))
            
            # Write file contents
            for filename in files_to_include:
                try:
                    content = read_file_content(filename)
                    lang_identifier = get_language_identifier(filename)
                    outfile.write(f"### {filename}\n")
                    outfile.write(f"```{lang_identifier}\n")
                    outfile.write(content)
                    outfile.write("\n```\n\n")
                except FileProcessingError as e:
                    logging.error(f"Skipping file {filename}: {str(e)}")
        
        logging.info(f"Successfully combined {len(files_to_include)} out of {len(files)} files into {output_file}")
    except Exception as e:
        logging.error(f"An error occurred while combining files: {str(e)}")
        raise

#SECTION: Script Entry Point
if __name__ == "__main__":
    try:
        args = parse_arguments()
        combine_files_to_markdown(args.output, args.all, args.directory, args.recursive, args.ignore_gitignore)
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        exit(1)