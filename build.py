#!/usr/bin/env python3
"""
Local build script for Komorebi Floating Workspace Indicator

This script builds the Windows executable locally for testing purposes.
Note: This utility is Windows-only as Komorebi window manager is only available for Windows.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import shutil
import time

def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"   Command: {cmd}")
        print(f"   Error: {e.stderr}")
        return False

def safe_remove_directory(path):
    """Safely remove a directory with retry logic for Windows."""
    if not Path(path).exists():
        return True
    
    print(f"🧹 Removing previous {path} directory...")
    max_retries = 3
    for attempt in range(max_retries):
        try:
            shutil.rmtree(path)
            print(f"✅ Successfully removed {path}")
            return True
        except PermissionError as e:
            if attempt < max_retries - 1:
                print(f"⚠️  Permission error removing {path}, retrying in 2 seconds... (attempt {attempt + 1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"❌ Failed to remove {path} after {max_retries} attempts: {e}")
                print(f"   Please close any applications that might be using files in {path}")
                return False
        except Exception as e:
            print(f"❌ Error removing {path}: {e}")
            return False

def main():
    """Main build function."""
    print("🚀 Starting local build for Komorebi Floating Workspace Indicator")
    print(f"📋 Platform: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    
    # Check if we're on Windows
    if platform.system() != "Windows":
        print("❌ Error: This utility is Windows-only as Komorebi window manager is only available for Windows.")
        return 1
    
    # Check if we're in the right directory
    if not Path("run.py").exists():
        print("❌ Error: run.py not found. Please run this script from the project root.")
        return 1
    
    # Use Python 3's pip explicitly to avoid Python 2.7 conflicts
    pip_cmd = f"{sys.executable} -m pip"
    
    # Install PyInstaller if not already installed
    if not run_command(f"{pip_cmd} install pyinstaller", "Installing PyInstaller"):
        return 1
    
    # Clean previous build and dist directories with retry logic
    for folder in ["build", "dist"]:
        if not safe_remove_directory(folder):
            print(f"⚠️  Continuing build despite failure to remove {folder}...")
    
    # Build the executable using spec file or default command with hidden imports
    pyinstaller_cmd = (
        f"{sys.executable} -m PyInstaller --windowed run.py --name komorebi-indicator "
        "--hidden-import=PyQt6 --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtCore"
    )
    if Path("komorebi-indicator.spec").exists():
        if not run_command(f"{sys.executable} -m PyInstaller komorebi-indicator.spec", "Building executable"):
            return 1
    else:
        if not run_command(pyinstaller_cmd, "Building executable"):
            return 1
    
    # Check if build was successful
    exe_path = Path("dist/komorebi-indicator.exe")
    
    if exe_path.exists():
        size_mb = exe_path.stat().st_size / (1024 * 1024)
        print(f"✅ Build successful!")
        print(f"📁 Executable location: {exe_path.absolute()}")
        print(f"📏 File size: {size_mb:.1f} MB")
        print("\n🎉 You can now test the executable!")
    else:
        print("❌ Build failed: Executable not found")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 