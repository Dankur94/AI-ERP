#!/bin/bash
# Start the FastAPI backend server
# Run from project root: bash start-backend.sh

cd "$(dirname "$0")"

# Install dependencies if needed
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python -m venv .venv
fi

source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate

pip install -q -r src/api/requirements.txt

echo "Starting backend on http://localhost:8000"
python -m uvicorn src.api.main:app --reload --port 8000
