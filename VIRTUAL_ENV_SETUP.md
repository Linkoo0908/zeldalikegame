# Virtual Environment Setup Guide

This document explains how to set up and use the Python virtual environment for the Zelda-like 2D Game project.

## Quick Start

### Windows
```bash
# Run the activation script
.\activate_env.bat
```

### Linux/macOS
```bash
# Make the script executable (first time only)
chmod +x activate_env.sh

# Run the activation script
./activate_env.sh
```

## Manual Setup

If you prefer to set up the environment manually:

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Verify Setup
```bash
python verify_env.py
```

## Verification

The `verify_env.py` script checks:
- ✓ Virtual environment is active
- ✓ All dependencies are installed (pygame, pillow)
- ✓ Project structure is correct

## Dependencies

- **pygame >= 2.0.0**: Game development framework
- **pillow >= 8.0.0**: Image processing library

## Troubleshooting

### Virtual Environment Not Found
If you get an error about the virtual environment not being found:
```bash
python -m venv venv
```

### Dependencies Not Installing
Make sure you're in the virtual environment and have internet access:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Permission Issues (Linux/macOS)
Make the activation script executable:
```bash
chmod +x activate_env.sh
```

## Development Workflow

1. Activate the virtual environment using the activation script
2. Verify setup with `python verify_env.py`
3. Run the game with `python main.py`
4. Deactivate when done with `deactivate`

## Files Created

- `venv/` - Virtual environment directory
- `activate_env.bat` - Windows activation script
- `activate_env.sh` - Linux/macOS activation script
- `verify_env.py` - Environment verification script
- `VIRTUAL_ENV_SETUP.md` - This documentation file