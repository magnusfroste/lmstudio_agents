#!/bin/bash

# Interactive installation script for LM Studio project

# Check if running interactively
if [ -t 0 ]; then
    INTERACTIVE=true
else
    INTERACTIVE=false
    echo "Running in non-interactive mode, will default to 'yes' for all prompts."
fi

# Function to prompt user for confirmation - waits for explicit 'y' or 'n'
confirm() {
    if [ "$INTERACTIVE" = true ]; then
        while true; do
            read -p "$1 (y/n): " choice
            case "$choice" in
                y|Y ) return 0;;
                n|N ) return 1;;
                * ) echo "Please answer y or n";;
            esac
        done
    else
        choice="y"
        echo "$1 (y/n): y (auto-selected in non-interactive mode)"
        return 0
    fi
}

# Function to display menu step
show_step() {
    echo "\n=== Step $1: $2 ==="
}

# Check if Python 3.6 or higher is installed
show_step 1 "Checking Python version"
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed. Please install Python 3.6 or higher."
    exit 1
fi

python_version=$(python3 --version | cut -d' ' -f2)
# Extract major and minor version numbers for comparison
IFS='.' read -r major minor patch <<< "$python_version"
if [ "$major" -lt 3 ] || ([ "$major" -eq 3 ] && [ "$minor" -lt 6 ]); then
    echo "Python version $python_version is too old. Please install Python 3.6 or higher."
    exit 1
fi
echo "Python $python_version is installed."

# Check if venv is activated, if not, activate it
show_step 2 "Checking virtual environment"
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Virtual environment is not activated."
    if [ -d "venv" ]; then
        if confirm "Activate existing virtual environment?"; then
            source venv/bin/activate
            echo "Virtual environment activated."
        else
            echo "Please activate the virtual environment manually with 'source venv/bin/activate'."
            exit 1
        fi
    else
        if confirm "Create and activate a new virtual environment?"; then
            python3 -m venv venv
            source venv/bin/activate
            echo "Virtual environment created and activated."
        else
            echo "Virtual environment setup skipped. Please create and activate it manually."
            exit 1
        fi
    fi
else
    echo "Virtual environment is already activated."
fi

# Check if LM Studio server is running on localhost:1234 - Prioritize connectivity check
show_step 3 "Checking LM Studio server status"
echo "Checking if LM Studio server is running on localhost:1234..."
SERVER_RUNNING=false
if command -v curl &> /dev/null; then
    echo "Attempting to connect to LM Studio server on localhost:1234..."
    if curl -s -f http://localhost:1234 > /dev/null; then
        echo "Successfully connected to LM Studio server on localhost:1234."
        SERVER_RUNNING=true
    else
        echo "Could not connect to LM Studio server on localhost:1234."
    fi
else
    echo "curl is not installed, skipping direct connectivity check for LM Studio server."
fi

# Check for lms CLI tool
if ! command -v lms &> /dev/null; then
    echo "LM Studio CLI tool 'lms' is not installed or not found in PATH."
    echo "Please ensure LM Studio is installed and the 'lms' command is accessible in your terminal."
    echo "You can download LM Studio from its official website and follow installation instructions."
    echo "If 'lms' is installed but not in PATH, you may need to add it manually (e.g., 'export PATH=$PATH:/path/to/lms')."
    if [ "$(uname)" = "Darwin" ]; then
        echo "Since you're on macOS, I can attempt to install LM Studio CLI tools via Homebrew if available."
        if confirm "Would you like me to try installing LM Studio CLI tools via Homebrew?"; then
            if command -v brew &> /dev/null; then
                echo "Installing LM Studio CLI tools via Homebrew..."
                brew install lm-studio
                if command -v lms &> /dev/null; then
                    echo "LM Studio CLI tools installed successfully."
                    if lms status 2>/dev/null | grep -qi "on" || lms status 2>/dev/null | grep -qi "running"; then
                        echo "LM Studio server status confirmed via CLI as running."
                        SERVER_RUNNING=true
                    else
                        if confirm "Would you like to start the LM Studio server now?"; then
                            echo "Starting LM Studio server..."
                            lms server start
                            sleep 5  # Give more time for server to start
                            if lms status 2>/dev/null | grep -qi "on" || lms status 2>/dev/null | grep -qi "running"; then
                                echo "LM Studio server started successfully via CLI."
                                SERVER_RUNNING=true
                            elif command -v curl &> /dev/null && curl -s -f http://localhost:1234 > /dev/null; then
                                echo "CLI status check failed, but direct connection to localhost:1234 succeeded. Assuming server is running."
                                SERVER_RUNNING=true
                            else
                                echo "Failed to start LM Studio server or confirm status. Please start it manually."
                            fi
                        else
                            echo "Please start LM Studio server manually with 'lms server start'."
                        fi
                    fi
                else
                    echo "Installation failed. Please install LM Studio manually."
                fi
            else
                echo "Homebrew is not installed. Please install Homebrew first or install LM Studio manually."
            fi
        fi
    fi
    echo "Alternatively, ensure the server is running manually on localhost:1234 with a model like Qwen2.5-7B-Instruct-GGUF loaded."
    echo "I will not proceed unless you confirm the server is running or you want to continue anyway."
    if [ "$SERVER_RUNNING" = true ]; then
        echo "Server connectivity already confirmed, proceeding."
    elif confirm "Is the LM Studio server running on localhost:1234, or do you want to continue assuming it is?"; then
        echo "Continuing installation assuming server is running. If it's not, the application may fail to start."
        SERVER_RUNNING=true
    else
        echo "Please install LM Studio or start the server manually before proceeding."
        exit 1
    fi
else
    echo "LM Studio CLI tool 'lms' found in PATH."
    LMS_STATUS_OUTPUT=$(lms status 2>/dev/null)
    if echo "$LMS_STATUS_OUTPUT" | grep -qi "on" || echo "$LMS_STATUS_OUTPUT" | grep -qi "running"; then
        echo "LM Studio server is running according to CLI."
        SERVER_RUNNING=true
    else
        echo "LM Studio server is not running according to CLI check on localhost:1234."
        if [ "$SERVER_RUNNING" = true ]; then
            echo "However, direct connectivity check succeeded, so assuming server is running."
        elif confirm "Would you like to start the LM Studio server now?"; then
            echo "Starting LM Studio server..."
            lms server start
            sleep 5  # Give more time for server to start
            LMS_STATUS_OUTPUT=$(lms status 2>/dev/null)
            if echo "$LMS_STATUS_OUTPUT" | grep -qi "on" || echo "$LMS_STATUS_OUTPUT" | grep -qi "running"; then
                echo "LM Studio server started successfully via CLI."
                SERVER_RUNNING=true
            elif command -v curl &> /dev/null && curl -s -f http://localhost:1234 > /dev/null; then
                echo "CLI status check failed, but direct connection to localhost:1234 succeeded. Assuming server is running."
                SERVER_RUNNING=true
            else
                echo "Failed to start LM Studio server. Please start it manually and load a model like Qwen2.5-7B-Instruct-GGUF."
                echo "Alternatively, ensure the server is running on localhost:1234."
                if confirm "Is the LM Studio server running on localhost:1234, or do you want to continue assuming it is?"; then
                    echo "Continuing installation assuming server is running. If it's not, the application may fail to start."
                    SERVER_RUNNING=true
                else
                    echo "Please start LM Studio server manually before proceeding."
                    exit 1
                fi
            fi
        else
            echo "Please start LM Studio server manually with 'lms server start' and load a model like Qwen2.5-7B-Instruct-GGUF."
            echo "Alternatively, ensure the server is running on localhost:1234."
            if confirm "Is the LM Studio server running on localhost:1234, or do you want to continue assuming it is?"; then
                echo "Continuing installation assuming server is running. If it's not, the application may fail to start."
                SERVER_RUNNING=true
            else
                echo "Please start LM Studio server manually before proceeding."
                exit 1
            fi
        fi
    fi
fi

# Final verification of server status
show_step 3.1 "Final verification of LM Studio server"
if [ "$SERVER_RUNNING" = true ]; then
    echo "LM Studio server is confirmed or assumed to be running on localhost:1234. Proceeding with installation."
else
    echo "Could not confirm LM Studio server on localhost:1234."
    echo "Please ensure the server is running and accessible."
    if ! confirm "Is the LM Studio server definitely running on localhost:1234, or do you want to proceed anyway?"; then
        echo "Please start the server manually or troubleshoot the connection issue before continuing."
        exit 1
    else
        echo "Proceeding with installation despite connectivity check failure. The application may not work if the server is not running."
    fi
fi

# Check read access to necessary files
echo "Checking read access to necessary files..."
if [ -r "examples/sample_text.txt" ] && [ -r "examples/sample.json" ]; then
    echo "Read access to examples folder files: OK"
else
    echo "WARNING: No read access to one or more files in examples folder. The application may fail to read these files."
    echo "Please ensure the files exist and you have permission to read them."
    echo "On macOS, you may need to grant Terminal access to files in System Preferences > Security & Privacy > Privacy > Files and Folders."
fi

if [ -f "product_sales.db" ]; then
    if [ -r "product_sales.db" ]; then
        echo "Read access to database file: OK"
    else
        echo "WARNING: No read access to product_sales.db. The application may fail to access the database."
        echo "Please ensure you have permission to read the file."
        echo "On macOS, you may need to grant Terminal access to files in System Preferences > Security & Privacy > Privacy > Files and Folders."
    fi
else
    echo "Database file product_sales.db does not exist. Attempting to create it..."
    if [ -f "create_sales_database.py" ]; then
        echo "Running create_sales_database.py to initialize the database..."
        if command -v python3 &> /dev/null; then
            python3 create_sales_database.py
            if [ $? -eq 0 ]; then
                echo "Database created successfully."
            else
                echo "ERROR: Failed to create database with python3. Please check create_sales_database.py or run it manually."
            fi
        elif command -v python &> /dev/null; then
            python create_sales_database.py
            if [ $? -eq 0 ]; then
                echo "Database created successfully."
            else
                echo "ERROR: Failed to create database with python. Please check create_sales_database.py or run it manually."
            fi
        else
            echo "ERROR: Python not found. Please install Python and ensure 'python3' or 'python' is in your PATH."
        fi
    else
        echo "ERROR: create_sales_database.py not found. Cannot initialize database."
        echo "Please ensure the file exists in the project directory."
    fi
fi

# Check for critical project directories
echo "Checking project structure..."
for dir in "examples" "tools" "templates"; do
    if [ -d "$dir" ]; then
        echo "Directory $dir: OK"
    else
        echo "WARNING: Directory $dir is missing. The application may not function correctly."
        echo "Please ensure the project structure is intact. You may need to re-clone or re-download the project."
    fi
done

# Check for LMStudio server availability (simple port check)
echo "Checking if LMStudio server is running on localhost:1234..."
if command -v nc &> /dev/null; then
    if nc -z localhost 1234 2>/dev/null; then
        echo "LMStudio server appears to be running on localhost:1234: OK"
    else
        echo "WARNING: LMStudio server is not running on localhost:1234. The application will fail to connect."
        echo "Please ensure LMStudio is installed and running. Refer to the project documentation for setup instructions."
    fi
else
    echo "Note: 'nc' (netcat) not found. Skipping LMStudio server check."
    echo "Please ensure LMStudio is running on localhost:1234 before using the application."
fi

# Install dependencies
show_step 4 "Installing dependencies"
if confirm "Install required dependencies now?"; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    echo "Dependencies installed."
else
    echo "Dependency installation skipped. Please install them manually with 'pip install -r requirements.txt'."
fi

# Create sample sales database
show_step 5 "Creating sample sales database"
if [ -f "product_sales.db" ]; then
    echo "Sample sales database already exists."
    if confirm "Would you like to recreate the sample sales database?"; then
        echo "Creating sample sales database..."
        python create_sales_database.py
        echo "Sample sales database created."
    else
        echo "Keeping existing database."
    fi
else
    if confirm "Create sample sales database now?"; then
        echo "Creating sample sales database..."
        python create_sales_database.py
        echo "Sample sales database created."
    else
        echo "Database creation skipped. You can create it later with 'python create_sales_database.py'."
    fi
fi

echo "\n=== Installation Complete ==="
echo "Setup is complete. You can now run the project with 'venv/bin/python3 llmchat.py'."
echo "Type 'exit' to close the interactive chat when you're done."
