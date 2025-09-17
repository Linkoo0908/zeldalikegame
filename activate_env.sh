#!/bin/bash
echo "Activating Python virtual environment..."

# Check if virtual environment exists
if [ ! -f "venv/bin/activate" ]; then
    echo "Error: Virtual environment not found!"
    echo "Please run: python -m venv venv"
    exit 1
fi

source venv/bin/activate
echo "Virtual environment activated!"
echo ""

# Check if dependencies are installed
python -c "import pygame, PIL" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "=== Zelda-like 2D Game Development Environment ==="
echo "To verify setup: python verify_env.py"
echo "To run the game: python main.py"
echo "To deactivate: deactivate"
echo ""