"""
File Operations Tool

This module provides functions for interacting with the local file system,
allowing the LLM to read content from files.
"""

import os

def read_file_content(path: str) -> str:
    """
    Reads the content of a specified file and returns it as a string.
    
    Args:
        path (str): The path to the file to be read.
    
    Returns:
        str: The content of the file if successful, or an error message if the file cannot be read.
    """
    try:
        # Ensure the path is relative to the current working directory
        if not os.path.isabs(path):
            path = os.path.join(os.getcwd(), path)
        if not os.path.exists(path):
            return f"Error: File '{path}' does not exist."
        if not os.path.isfile(path):
            return f"Error: '{path}' is not a file."
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Limit the response size to avoid overwhelming the model
            if len(content) > 10000:
                return content[:10000] + "\n... (content truncated due to length)"
            return content
    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"
