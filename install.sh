#!/bin/bash

# Installation script for LM Studio Function Calling Example

# Exit on any error
set -e

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python3 is not installed. Please install Python3 first."
    echo "You can install it via Homebrew: brew install python3"
    exit 1
fi

# Check if LM Studio server is running on localhost:1234
if ! curl -s http://localhost:1234/v1/models | grep -q "models"; then
    echo "LM Studio server is not running on localhost:1234."
    echo "Please start LM Studio server and load a model like Qwen2.5-7B-Instruct-GGUF."
    echo "You can start the server with: lms server start"
    exit 1
fi

echo "Setting up virtual environment..."
# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "Installing dependencies..."
# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run database seed script to create the sample database
echo "Creating sample sales database..."
python create_sales_database.py

echo "Installation complete! Virtual environment is set up and sample database created."
echo "To activate the virtual environment, run: source venv/bin/activate"
echo "Then, start the application with: python lm_tool_interaction.py"

echo "If you encounter issues, ensure LM Studio is running with the correct model loaded."
