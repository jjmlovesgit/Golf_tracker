@echo off
title Golf Ball Tracker
color 0A

echo Starting Golf Ball Tracker...
echo ----------------------------

:: Activate virtual environment
if exist "venv\Scripts\activate" (
    call venv\Scripts\activate
) else (
    echo Virtual environment not found. Please run setup.py first.
    pause
    exit /b 1
)

:: Check if main file exists
if not exist "golf_tracker.py" (
    echo Error: golftracker.py not found in current directory
    pause
    exit /b 1
)

:: Run the application
python golftracker.py

:: Keep window open after completion
echo ----------------------------
echo Application terminated
pause