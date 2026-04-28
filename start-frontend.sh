#!/bin/bash
# Start the Vue.js frontend dev server
# Run from project root: bash start-frontend.sh

cd "$(dirname "$0")/src/web"

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

echo "Starting frontend on http://localhost:5173"
npm run dev
