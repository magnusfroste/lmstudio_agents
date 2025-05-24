"""
Test script for File Operations Tool

This script tests the read_file_content function from the file_operations module.
"""

from tools.file_operations import read_file_content

def main():
    test_file_path = "examples/sample_text.txt"
    print(f"Testing reading content from {test_file_path}")
    content = read_file_content(test_file_path)
    print("Result:")
    print(content)

if __name__ == "__main__":
    main()
