"""
JSON Operations Tool

This module provides functions for interacting with JSON files,
allowing the LLM to read and process structured data, such as accounting data.
"""

import os
import json

def read_json_file(path: str) -> str:
    """
    Reads the content of a specified JSON file and returns it as a formatted string.
    
    Args:
        path (str): The path to the JSON file to be read.
    
    Returns:
        str: The content of the JSON file as a formatted string if successful, 
             or an error message if the file cannot be read or is not valid JSON.
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
            data = json.load(file)
            # Convert JSON data to a formatted string for readability
            formatted_data = json.dumps(data, indent=2)
            # Limit the response size to avoid overwhelming the model
            if len(formatted_data) > 10000:
                return formatted_data[:10000] + "\n... (content truncated due to length)"
            return formatted_data
    except json.JSONDecodeError as e:
        return f"Error: File '{path}' contains invalid JSON. Details: {str(e)}"
    except Exception as e:
        return f"Error reading JSON file '{path}': {str(e)}"
