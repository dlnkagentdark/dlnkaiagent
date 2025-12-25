#!/usr/bin/env python3
"""
dLNk IDE - Build Script
สคริปต์สำหรับ build ไฟล์ .exe ด้วย PyInstaller

การใช้งาน:
    python build_exe.py [--onefile] [--console]

Options:
    --onefile   : รวมทุกอย่างเป็นไฟล์เดียว (default)
    --onedir    : แยกเป็นโฟลเดอร์
    --console   : แสดง console window (สำหรับ debug)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Configuration
APP_NAME = "dLNk_Launcher"
MAIN_SCRIPT = "dlnk_launcher_v2.py"
ICON_FILE = "dlnk_icon_256.png"

# Files to include
DATA_FILES = [
    "dlnk_logo.png",
    "dlnk_icon_64.png",
    "dlnk_icon_128.png",
    "dlnk_icon_256.png",
    "dlnk_license_system.py",
    "dlnk_ai_bridge_v2.py",
]

# Hidden imports
HIDDEN_IMPORTS = [
    "customtkinter",
    "PIL",
    "PIL.Image",
    "PIL.ImageTk",
    "cryptography",
    "cryptography.fernet",
    "sqlite3",
    "hashlib",
    "hmac",
    "secrets",
    "json",
    "threading",
    "subprocess",
    "platform",
    "uuid",
    "datetime",
    "pathlib",
    "logging",
]


def build_exe(onefile=True, console=False):
    """Build executable with PyInstaller"""
    
    print("=" * 60)
    print(f"Building {APP_NAME}")
    print("=" * 60)
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"[OK] PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("[ERROR] PyInstaller not installed. Run: pip install pyinstaller")
        return False
    
    # Check main script exists
    if not os.path.exists(MAIN_SCRIPT):
        print(f"[ERROR] Main script not found: {MAIN_SCRIPT}")
        return False
    
    # Build command
    cmd = ["pyinstaller"]
    
    # One file or one directory
    if onefile:
        cmd.append("--onefile")
    else:
        cmd.append("--onedir")
    
    # Console or windowed
    if console:
        cmd.append("--console")
    else:
        cmd.append("--windowed")
    
    # App name
    cmd.extend(["--name", APP_NAME])
    
    # Icon
    if os.path.exists(ICON_FILE):
        cmd.extend(["--icon", ICON_FILE])
    
    # Add data files
    for data_file in DATA_FILES:
        if os.path.exists(data_file):
            cmd.extend(["--add-data", f"{data_file}{os.pathsep}."])
    
    # Hidden imports
    for hidden in HIDDEN_IMPORTS:
        cmd.extend(["--hidden-import", hidden])
    
    # Clean build
    cmd.append("--clean")
    
    # Main script
    cmd.append(MAIN_SCRIPT)
    
    print(f"\n[*] Running: {' '.join(cmd)}\n")
    
    # Run PyInstaller
    result = subprocess.run(cmd, capture_output=False)
    
    if result.returncode == 0:
        print("\n" + "=" * 60)
        print("[SUCCESS] Build completed!")
        print("=" * 60)
        
        # Show output location
        if onefile:
            exe_path = Path("dist") / f"{APP_NAME}.exe"
            if sys.platform != "win32":
                exe_path = Path("dist") / APP_NAME
        else:
            exe_path = Path("dist") / APP_NAME
        
        print(f"\nOutput: {exe_path}")
        
        if exe_path.exists():
            size = exe_path.stat().st_size / (1024 * 1024)
            print(f"Size: {size:.2f} MB")
        
        return True
    else:
        print("\n[ERROR] Build failed!")
        return False


def clean():
    """Clean build artifacts"""
    dirs_to_remove = ["build", "dist", "__pycache__"]
    files_to_remove = [f"{APP_NAME}.spec"]
    
    for d in dirs_to_remove:
        if os.path.exists(d):
            shutil.rmtree(d)
            print(f"[*] Removed: {d}/")
    
    for f in files_to_remove:
        if os.path.exists(f):
            os.remove(f)
            print(f"[*] Removed: {f}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Build dLNk IDE Launcher")
    parser.add_argument("--onedir", action="store_true", help="Build as directory instead of single file")
    parser.add_argument("--console", action="store_true", help="Show console window")
    parser.add_argument("--clean", action="store_true", help="Clean build artifacts")
    
    args = parser.parse_args()
    
    if args.clean:
        clean()
    else:
        build_exe(onefile=not args.onedir, console=args.console)
