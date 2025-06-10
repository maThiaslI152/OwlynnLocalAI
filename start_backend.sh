#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Change to backend directory
cd Backend

# Install requirements if needed
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "Installing backend requirements..."
    pip install -r ../requirements.txt
fi

# Start the backend server
echo "Starting backend server..."
uvicorn main:app --reload --host 0.0.0.0 --port 8001 