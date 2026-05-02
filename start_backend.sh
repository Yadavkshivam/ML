#!/bin/bash
cd "$(dirname "$0")"
source venv/bin/activate
echo "Starting Flask Backend Server..."
echo "API will be available at http://localhost:8000"
python app.py
