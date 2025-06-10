#!/bin/bash

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Update pip to the latest version
python -m pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Install spaCy language model
python -m spacy download en_core_web_sm

# Create necessary directories
mkdir -p uploads cache

# Start Docker services
docker-compose up -d

# Install frontend dependencies
cd frontend
npm install

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "DEBUG=false
LLM_BASE_URL=http://localhost:1234/v1
LLM_MODEL=Qwen3-14B
POSTGRES_USER=owlynn
POSTGRES_PASSWORD=owlynn_password
POSTGRES_DB=owlynn_db" > .env
fi

# Install Tesseract and Tesseract language data
brew install tesseract tesseract-lang

echo "Setup completed! You can now:"
echo "1. Start the backend server: python -m Backend.main"
echo "2. Start the frontend development server: cd frontend && npm start"
echo "3. Access the application at http://localhost:3000" 