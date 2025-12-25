#!/usr/bin/env python3
"""
dLNk Unified System - Setup Script
===================================
ติดตั้ง dependencies และตั้งค่าระบบ

Usage:
    python setup.py install     # ติดตั้ง dependencies
    python setup.py configure   # ตั้งค่าระบบ
    python setup.py all         # ทำทั้งหมด
"""

import os
import sys
import subprocess
from pathlib import Path


def install_dependencies():
    """Install required Python packages"""
    print("=" * 60)
    print("Installing Dependencies...")
    print("=" * 60)
    
    packages = [
        "httpx[http2]",      # For gRPC calls
        "requests",          # For REST API calls
        "customtkinter",     # For GUI
        "pillow",            # For images
        "cryptography",      # For certificates
        "fastapi",           # For API server
        "uvicorn",           # For API server
        "python-telegram-bot",  # For Telegram bot
        "flask",             # For license server
    ]
    
    for package in packages:
        print(f"\n📦 Installing {package}...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                package, "-q", "--upgrade"
            ])
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ⚠️ Failed to install {package}")
    
    print("\n✅ Dependencies installation complete!")


def configure_system():
    """Configure the system"""
    print("=" * 60)
    print("Configuring System...")
    print("=" * 60)
    
    # Create directories
    home = Path.home()
    dlnk_dir = home / ".dlnk"
    
    dirs = [
        dlnk_dir,
        dlnk_dir / "tokens",
        dlnk_dir / "sessions",
        dlnk_dir / "logs",
        dlnk_dir / "certs"
    ]
    
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"   📁 Created: {d}")
    
    # Create default config
    config_file = dlnk_dir / "config.json"
    if not config_file.exists():
        import json
        config = {
            "proxy_port": 8081,
            "license_server": "http://127.0.0.1:5000",
            "telegram_link": "https://t.me/dlnkai",
            "auto_refresh": True,
            "default_provider": "dlnk_ai"
        }
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"   📝 Created config: {config_file}")
    
    print("\n✅ System configuration complete!")
    print(f"\n📂 dLNk directory: {dlnk_dir}")


def create_shortcuts():
    """Create desktop shortcuts (Windows)"""
    if sys.platform != 'win32':
        print("⚠️ Shortcuts only supported on Windows")
        return
    
    print("=" * 60)
    print("Creating Shortcuts...")
    print("=" * 60)
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        path = os.path.join(desktop, "dLNk AI.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(path)
        shortcut.Targetpath = sys.executable
        shortcut.Arguments = f'"{os.path.join(os.path.dirname(__file__), "dlnk_unified_launcher.py")}"'
        shortcut.WorkingDirectory = os.path.dirname(__file__)
        shortcut.Description = "dLNk AI - Unified System"
        shortcut.save()
        
        print(f"   ✅ Created shortcut: {path}")
    except ImportError:
        print("   ⚠️ Install pywin32 and winshell for shortcuts")
    except Exception as e:
        print(f"   ⚠️ Failed to create shortcut: {e}")


def print_usage():
    """Print usage instructions"""
    print("""
╔════════════════════════════════════════════════════════════╗
║           dLNk Unified System - Quick Start                ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  1. Import Token:                                          ║
║     - Run the launcher                                     ║
║     - Go to "Tokens" tab                                   ║
║     - Click "Import Token from File"                       ║
║     - Select your stolen_data.json file                    ║
║                                                            ║
║  2. Start Chatting:                                        ║
║     - Go to "AI Chat" tab                                  ║
║     - Type your message and press Enter                    ║
║                                                            ║
║  3. Launch VS Code:                                        ║
║     - Go to "Settings" tab                                 ║
║     - Click "Launch VS Code with Proxy"                    ║
║                                                            ║
║  CLI Mode:                                                 ║
║     python dlnk_unified_launcher.py --cli                  ║
║                                                            ║
║  API Server:                                               ║
║     python -m uvicorn ai_gateway_server:app --port 8000    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
""")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    command = sys.argv[1].lower()
    
    if command == "install":
        install_dependencies()
    elif command == "configure":
        configure_system()
    elif command == "shortcuts":
        create_shortcuts()
    elif command == "all":
        install_dependencies()
        configure_system()
        create_shortcuts()
        print_usage()
    elif command == "help":
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print(__doc__)


if __name__ == "__main__":
    main()
