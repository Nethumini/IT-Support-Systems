#!/usr/bin/env bash
# IT Support Systems Run Script (macOS/Linux equivalent of run.ps1)
set -e

cd "$(dirname "$0")"

if [ ! -d "venv" ]; then
    echo "ERROR: Virtual environment not found!"
    echo "Create it first:  uv venv venv --python 3.12 && uv pip install --python venv/bin/python -r requirements.txt"
    exit 1
fi

if [ ! -f "backend/.env" ]; then
    echo "WARNING: backend/.env not found!"
    echo "Copy backend/.env.example and add your API keys"
fi

echo "Starting server..."
echo "API:  http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "Press CTRL+C to stop"
echo

cd backend
exec ../venv/bin/python -m uvicorn app.main:app --reload
