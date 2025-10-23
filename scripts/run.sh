#!/bin/bash
# Quick run helper for Talent Trawler (Linux/Mac)

# Check if folder argument provided
if [ -z "$1" ]; then
    echo "Usage: ./scripts/run.sh <folder_name>"
    echo "Example: ./scripts/run.sh pm_candidates"
    exit 1
fi

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run ./scripts/setup.sh first."
    exit 1
fi

source venv/bin/activate

# Run the application
python3 talent_trawler.py "$1"
