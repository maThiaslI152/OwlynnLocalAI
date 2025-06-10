#!/bin/bash

echo "Building frontend for production..."

# Change to the frontend directory
cd Frontend

# Ensure node_modules/.bin is in the PATH
export PATH="$(pwd)/node_modules/.bin:$PATH"

# Install dependencies if node_modules does not exist
if [ ! -d "node_modules" ]; then
  echo "Installing dependencies..."
  npm install --legacy-peer-deps
fi

# Build the frontend for production
npm run build

# Serve the production build
echo "Starting production server..."
npx serve -s build 