@echo off
echo Activating Python virtual environment...

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Error: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
echo Virtual environment activated!
echo.

REM Check if dependencies are installed
python -c "import pygame, PIL" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

echo.
echo === Zelda-like 2D Game Development Environment ===
echo To verify setup: python verify_env.py
echo To run the game: python main.py
echo To deactivate: deactivate
echo.