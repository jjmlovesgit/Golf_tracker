#!/usr/bin/env python
import os
import subprocess
import sys
from pathlib import Path

def create_venv():
    """Create Python virtual environment"""
    print("🛠 Creating virtual environment...")
    venv_path = "venv"
    if not os.path.exists(venv_path):
        os.system(f"{sys.executable} -m venv {venv_path}")
    else:
        print("✅ Virtual environment already exists")

def install_dependencies():
    """Install required packages"""
    print("📦 Installing dependencies...")
    requirements = [
        "gradio>=4.0.0",
        "opencv-python",
        "numpy",
        "python-dotenv",
        "vision-agent"
    ]
    
    pip_cmd = [
        os.path.join("venv", "Scripts", "pip") if os.name == "nt" 
        else os.path.join("venv", "bin", "pip"),
        "install"
    ] + requirements
    
    subprocess.check_call(pip_cmd)
    print("✅ Dependencies installed")

def configure_api():
    """Configure VisionAgent API key"""
    print("\n🔑 VisionAgent API Configuration")
    print("Get your key at: https://va.landing.ai/settings/api-key")
    
    api_key = input("Enter your VisionAgent API key: ").strip()
    
    with open(".env", "w") as f:
        f.write(f"VISION_AGENT_API_KEY={api_key}\n")
    
    print("✅ API key saved to .env file")

def create_launchers():
    """Create platform-specific launcher scripts"""
    # Windows launcher
    with open("launch_app.bat", "w") as f:
        f.write("""@echo off
call venv\\Scripts\\activate
python golf_tracker.py
pause
""")
    
    # Unix launcher
    with open("launch_app.sh", "w") as f:
        f.write("""#!/bin/bash
source venv/bin/activate
python golf_tracker.pyp.py
""")
    
    os.chmod("launch_app.sh", 0o755)  # Make executable
    print("✅ Created launcher scripts")

def main():
    print("\n🏌️ Golf Ball Tracker Setup\n")
    
    create_venv()
    install_dependencies()
    configure_api()
    create_launchers()
    
    # Ask to run immediately
    run_now = input("\n🚀 Setup complete! Run the app now? [Y/n]: ").strip().lower()
    if not run_now or run_now == "y":
        print("\nStarting Golf Ball Tracker...")
        if os.name == "nt":
            os.system("launch_app.bat")
        else:
            os.system("./launch_app.sh")

if __name__ == "__main__":
    main()
