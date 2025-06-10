#!/bin/bash

# Start Docker services
cd "$(dirname "$0")"
docker-compose up -d

# Start backend (in background)
echo "Starting backend server..."
cd Backend
source ../venv/bin/activate
nohup python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload > ../backend.log 2>&1 &
cd ..

# Start frontend (in foreground)
echo "Starting frontend server..."
cd Frontend
npm start 