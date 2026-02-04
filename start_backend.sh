#!/bin/bash

# Start the backend server
cd backend

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
if [ ! -f "venv/.installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
    touch venv/.installed
fi

# Initialize database if it doesn't exist
if [ ! -f "podcast_task_manager.db" ]; then
    echo "Initializing database..."
    python init_db.py
fi

# Start the server
echo "Starting backend server on http://localhost:8000"
python main.py
