#!/bin/bash

# Golf Ball Tracker Launcher for macOS/Linux
# ------------------------------------------

# Set colors for terminal output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏌️  Starting Golf Ball Tracker...${NC}"
echo "----------------------------------"

# Check for virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️ Virtual environment not found. Running setup...${NC}"
    python3 setup.py || { echo -e "${YELLOW}❌ Setup failed${NC}"; exit 1; }
fi

# Activate virtual environment
source venv/bin/activate || { echo -e "${YELLOW}❌ Virtual environment activation failed${NC}"; exit 1; }

# Check for required packages
pip show opencv-python > /dev/null || {
    echo -e "${YELLOW}⚠️ Missing dependencies. Installing...${NC}"
    pip install -r requirements.txt
}

# Check FFmpeg (critical for video processing)
if ! command -v ffmpeg &> /dev/null; then
    echo -e "${YELLOW}⚠️ FFmpeg not found. Attempting to install via Homebrew...${NC}"
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo -e "${YELLOW}❌ Homebrew not available. Please install FFmpeg manually:"
        echo -e "https://ffmpeg.org/download.html${NC}"
        exit 1
    fi
fi

# Run the application
echo -e "${GREEN}🚀 Launching application...${NC}"
python3 golf_tracker.py

# Deactivate virtual environment on exit
deactivate
echo -e "${GREEN}✅ Session ended${NC}"
