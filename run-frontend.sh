#!/usr/bin/env bash
# IT Support Systems Frontend Run Script (macOS/Linux equivalent of run-frontend.ps1)
set -e

cd "$(dirname "$0")"

if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    (cd frontend && npm install)
fi

echo "Starting frontend dev server..."
echo "Frontend will be available at: http://localhost:5173"
echo "Press CTRL+C to stop"
echo

cd frontend
exec npm run dev
