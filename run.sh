#!/bin/bash

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run setup.sh first"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Configuration file (.env) not found. Please run setup.sh first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Run the system
echo "Starting Agent Swarm System..."
python3 src/main.py

# Deactivate virtual environment on exit
deactivate
