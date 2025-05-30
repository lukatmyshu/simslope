"""
Setup script for the Golf Slope Detection System.
Handles environment setup, dependency installation, and system checks.
"""

import os
import sys
import subprocess
import platform
import venv
from pathlib import Path

def check_python_version():
    """Check if Python version meets requirements."""
    required_version = (3, 7)
    current_version = sys.version_info[:2]
    
    if current_version < required_version:
        print(f"Error: Python {required_version[0]}.{required_version[1]} or higher is required.")
        print(f"Current version: {current_version[0]}.{current_version[1]}")
        sys.exit(1)
    
    print(f"✓ Python version {current_version[0]}.{current_version[1]} detected")

def create_virtual_environment():
    """Create a virtual environment if it doesn't exist."""
    venv_path = Path("venv")
    
    if not venv_path.exists():
        print("Creating virtual environment...")
        venv.create(venv_path, with_pip=True)
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment already exists")

def get_python_executable():
    """Get the path to the Python executable in the virtual environment."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/python.exe")
    return Path("venv/bin/python")

def get_pip_executable():
    """Get the path to pip in the virtual environment."""
    if platform.system() == "Windows":
        return Path("venv/Scripts/pip.exe")
    return Path("venv/bin/pip")

def install_dependencies():
    """Install required packages using pip."""
    pip_path = get_pip_executable()
    
    print("Installing dependencies...")
    try:
        subprocess.run([
            str(pip_path),
            "install",
            "--upgrade",
            "pip"
        ], check=True)
        
        subprocess.run([
            str(pip_path),
            "install",
            "-r",
            "requirements.txt"
        ], check=True)
        print("✓ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)

def check_opencv():
    """Verify OpenCV installation and functionality."""
    python_path = get_python_executable()
    
    print("Verifying OpenCV installation...")
    try:
        result = subprocess.run([
            str(python_path),
            "-c",
            "import cv2; print(f'OpenCV version: {cv2.__version__}')"
        ], capture_output=True, text=True, check=True)
        print(f"✓ {result.stdout.strip()}")
    except subprocess.CalledProcessError:
        print("Error: OpenCV verification failed")
        sys.exit(1)

def create_run_script():
    """Create a run script for easy execution."""
    if platform.system() == "Windows":
        script_content = """@echo off
call venv\\Scripts\\activate
python main.py
pause
"""
        script_path = "run.bat"
    else:
        script_content = """#!/bin/bash
source venv/bin/activate
python main.py
"""
        script_path = "run.sh"
        # Make the script executable
        os.chmod(script_path, 0o755)
    
    with open(script_path, "w") as f:
        f.write(script_content)
    print(f"✓ Created {script_path} for easy execution")

def main():
    """Main setup function."""
    print("Setting up Golf Slope Detection System...")
    print("----------------------------------------")
    
    # Check Python version
    check_python_version()
    
    # Create virtual environment
    create_virtual_environment()
    
    # Install dependencies
    install_dependencies()
    
    # Verify OpenCV
    check_opencv()
    
    # Create run script
    create_run_script()
    
    print("\nSetup completed successfully!")
    print("\nTo run the application:")
    if platform.system() == "Windows":
        print("1. Double-click run.bat")
        print("   OR")
        print("2. Open a command prompt and run:")
        print("   run.bat")
    else:
        print("1. Open a terminal and run:")
        print("   ./run.sh")
    
    print("\nMake sure to start your golf simulator (E6 TruGolf or GSPro) in windowed mode before running the application.")

if __name__ == "__main__":
    main() 