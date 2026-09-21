#!/usr/bin/env bash
# IT Support Systems Frontend Run Script (macOS/Linux equivalent of run-frontend.ps1)
set -e

cd "$(dirname "$0")"

if [ ! -d "frontend/node_modules" ]; then
    echo "Installing frontend dependencies..."
    (cd frontend && npm install)
fi

echo "Starting frontend dev server..."
echo "Frontend: http://localhost:5173  (from other machines: http://192.168.1.48:5173)"
echo "Press CTRL+C to stop"
echo

cd frontend
# --host serves the page to other machines on the network, so the Windows
# test machine can open it.
exec npm run dev -- --host
