#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Activate virtual environment if it exists
if [ -d "$SCRIPT_DIR/venv" ]; then
    source "$SCRIPT_DIR/venv/bin/activate"
elif [ -d "$SCRIPT_DIR/.venv" ]; then
    source "$SCRIPT_DIR/.venv/bin/activate"
fi

# Change to backend directory
cd "$SCRIPT_DIR/Backend"

# Install requirements if needed
if [ ! -d "$SCRIPT_DIR/venv" ] && [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Installing backend requirements..."
    pip install -r "$SCRIPT_DIR/requirements.txt"
fi

# Start the backend server
echo "Starting backend server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8001 