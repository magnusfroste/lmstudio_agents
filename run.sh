#!/bin/bash

# run.sh - A script to automate setup and launch of the LMStudio Chat project

# Exit on any error
set -e

# Define colors for output
echo_green() {
    echo "\033[32m$1\033[0m"
}
echo_yellow() {
    echo "\033[33m$1\033[0m"
}
echo_red() {
    echo "\033[31m$1\033[0m"
}

# Welcome message
echo_green "Welcome to the LMStudio Chat Setup and Run Script"
echo "This script will set up the environment and start the chat application."

# Determine project directory
PROJECT_DIR="$(dirname "$(realpath "$0")")"
echo "Project directory: $PROJECT_DIR"

# Step 1: Check for Python
echo "Checking for Python..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
    PIP_CMD="pip3"
    echo_green "Python3 found!"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
    PIP_CMD="pip"
    echo_green "Python found!"
else
    echo_red "ERROR: Python not found. Please install Python and ensure 'python3' or 'python' is in your PATH."
    exit 1
fi

# Step 2: Create or activate virtual environment
echo "Setting up virtual environment..."
VENV_DIR="$PROJECT_DIR/venv"
if [ -d "$VENV_DIR" ]; then
    echo "Virtual environment already exists at $VENV_DIR"
else
    echo "Creating virtual environment at $VENV_DIR..."
    $PYTHON_CMD -m venv "$VENV_DIR"
    echo_green "Virtual environment created!"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"
echo_green "Virtual environment activated!"

# Step 3: Install dependencies
echo "Installing dependencies from requirements.txt..."
$PIP_CMD install -r "$PROJECT_DIR/requirements.txt"
echo_green "Dependencies installed!"

# Step 4: Check for database file
echo "Checking for database file..."
DB_FILE="$PROJECT_DIR/product_sales.db"
if [ -f "$DB_FILE" ]; then
    echo "Database file found at $DB_FILE"
else
    echo_yellow "Database file not found. Creating database..."
    if [ -f "$PROJECT_DIR/create_sales_database.py" ]; then
        $PYTHON_CMD "$PROJECT_DIR/create_sales_database.py"
        if [ $? -eq 0 ]; then
            echo_green "Database created successfully at $DB_FILE"
        else
            echo_red "ERROR: Failed to create database. Please run create_sales_database.py manually."
            exit 1
        fi
    else
        echo_red "ERROR: create_sales_database.py not found. Cannot create database."
        exit 1
    fi
fi

# Step 5: Check if LMStudio server is running
echo "Checking if LMStudio server is running on localhost:1234..."
if command -v nc &> /dev/null; then
    if nc -z localhost 1234 2>/dev/null; then
        echo_green "LMStudio server is running on localhost:1234!"
    else
        echo_red "WARNING: LMStudio server is not running on localhost:1234. The chat will fail to connect."
        echo "Please ensure LMStudio is installed and running before continuing."
        read -p "Continue anyway? (y/n): " continue_choice
        if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
            echo "Exiting. Please start LMStudio and run this script again."
            exit 1
        fi
    fi
else
    echo_yellow "Note: 'nc' (netcat) not found. Skipping LMStudio server check."
    echo "Please ensure LMStudio is running on localhost:1234 before continuing."
    read -p "Continue anyway? (y/n): " continue_choice
    if [[ ! "$continue_choice" =~ ^[Yy]$ ]]; then
        echo "Exiting. Please start LMStudio and run this script again."
        exit 1
    fi
fi

# Step 6: Launch the chat application
echo_green "Starting LMStudio Chat application..."
echo "Type 'exit' to stop the chat."
$PYTHON_CMD "$PROJECT_DIR/llmchat.py"

echo_green "Chat application terminated."
echo "To run the chat again, use: source venv/bin/activate && python llmchat.py"
