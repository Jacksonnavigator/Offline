#!/usr/bin/env python
"""
Build script for creating application executable
Usage: python build.py [--onefile|--onedir] [--windows|--linux|--pi]
"""

import subprocess
import sys
import argparse
from pathlib import Path


def build_executable(args):
    """Build executable using PyInstaller"""
    
    project_root = Path(__file__).parent
    spec_file = project_root / "build.spec"
    
    # Build command
    cmd = [
        "pyinstaller",
        str(spec_file),
        "--distpath", str(project_root / "dist"),
        "--buildpath", str(project_root / "build"),
        "--specpath", str(project_root),
    ]
    
    # Add options
    if args.onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    if args.windowed:
        cmd.append("--windowed")
    else:
        cmd.append("--console")
    
    # Add icon if exists
    icon_path = project_root / "assets" / "icon.ico"
    if icon_path.exists():
        cmd.extend(["--icon", str(icon_path)])
    
    print("Building executable...")
    print(" ".join(cmd))
    
    try:
        result = subprocess.run(cmd, cwd=str(project_root))
        if result.returncode == 0:
            print("✓ Build successful!")
            dist_dir = project_root / "dist" / "DocumentReader"
            if args.onefile:
                dist_dir = project_root / "dist" / "DocumentReader.exe"
            print(f"Executable created at: {dist_dir}")
            return True
        else:
            print("✗ Build failed!")
            return False
    except Exception as e:
        print(f"Error during build: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Build Portable Offline AI Document Reader"
    )
    parser.add_argument(
        "--onefile",
        action="store_true",
        help="Create single executable file"
    )
    parser.add_argument(
        "--onedir",
        action="store_true",
        help="Create directory with dependencies"
    )
    parser.add_argument(
        "--windowed",
        action="store_true",
        default=True,
        help="Build as windowed application (no console)"
    )
    parser.add_argument(
        "--console",
        action="store_true",
        help="Build with console window visible"
    )
    
    args = parser.parse_args()
    
    # Set defaults
    if not args.onefile and not args.onedir:
        args.onedir = True
    
    if args.console:
        args.windowed = False
    
    # Build
    success = build_executable(args)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
