#!/usr/bin/env python
"""
Setup and installation script
Handles first-time setup and dependency management
"""

import subprocess
import sys
import platform
from pathlib import Path


def run_command(cmd, description=None):
    """Run shell command"""
    if description:
        print(f"\n{'='*60}")
        print(f"► {description}")
        print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False


def setup_windows():
    """Setup for Windows"""
    print("\n🖥️  Setting up for Windows...")
    
    # Create virtual environment
    if not Path("venv").exists():
        run_command("python -m venv venv", "Creating virtual environment")
    
    # Activate and install
    activate_cmd = "venv\\Scripts\\activate &&"
    
    run_command(f"{activate_cmd} pip install --upgrade pip", "Upgrading pip")
    run_command(f"{activate_cmd} pip install -r requirements.txt", "Installing dependencies")
    
    print("\n✓ Windows setup complete!")
    print("\nTo activate virtual environment:")
    print("  venv\\Scripts\\activate")
    print("\nTo run application:")
    print("  python app.py")


def setup_linux():
    """Setup for Linux/Raspberry Pi"""
    print("\n🐧 Setting up for Linux/Raspberry Pi...")
    
    # Install system packages
    if platform.system() == "Linux":
        run_command("sudo apt-get update", "Updating system packages")
        run_command(
            "sudo apt-get install -y python3.12 python3.12-venv python3-pip tesseract-ocr",
            "Installing system dependencies"
        )
    
    # Create virtual environment
    if not Path("venv").exists():
        run_command("python3 -m venv venv", "Creating virtual environment")
    
    # Activate and install
    activate_cmd = "source venv/bin/activate &&"
    
    run_command(f"{activate_cmd} pip install --upgrade pip", "Upgrading pip")
    run_command(f"{activate_cmd} pip install -r requirements.txt", "Installing dependencies")
    
    print("\n✓ Linux setup complete!")
    print("\nTo activate virtual environment:")
    print("  source venv/bin/activate")
    print("\nTo run application:")
    print("  python3 app.py")


def setup_macos():
    """Setup for macOS"""
    print("\n🍎 Setting up for macOS...")
    
    # Install system packages using Homebrew
    run_command("brew install python3 tesseract", "Installing system dependencies")
    
    # Create virtual environment
    if not Path("venv").exists():
        run_command("python3 -m venv venv", "Creating virtual environment")
    
    # Activate and install
    activate_cmd = "source venv/bin/activate &&"
    
    run_command(f"{activate_cmd} pip install --upgrade pip", "Upgrading pip")
    run_command(f"{activate_cmd} pip install -r requirements.txt", "Installing dependencies")
    
    print("\n✓ macOS setup complete!")
    print("\nTo activate virtual environment:")
    print("  source venv/bin/activate")
    print("\nTo run application:")
    print("  python3 app.py")


def main():
    """Main setup function"""
    print("\n" + "="*60)
    print("  Portable Offline AI Document Reader - Setup")
    print("="*60)
    
    system = platform.system()
    
    if system == "Windows":
        setup_windows()
    elif system == "Darwin":
        setup_macos()
    elif system == "Linux":
        setup_linux()
    else:
        print(f"Unknown system: {system}")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("Setup complete! You can now run the application.")
    print("="*60)


if __name__ == "__main__":
    main()
