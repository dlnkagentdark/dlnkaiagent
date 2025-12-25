#!/usr/bin/env python3
"""
dLNk AI Installer - Fresh Machine Setup
============================================
ติดตั้งและตั้งค่า dLNk AI บนเครื่องใหม่

Features:
- ดาวน์โหลด dLNk AI extension
- ตั้งค่า VS Code
- Import token อัตโนมัติ
- สร้าง profile แยก

Author: dLNk Team
Version: 1.0.0
"""

import os
import sys
import json
import shutil
import zipfile
import subprocess
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    print("Installing requests...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests


class dLNk AIInstaller:
    """
    dLNk AI Installer for Fresh Machines
    
    Usage:
        installer = dLNk AIInstaller()
        installer.install()
    """
    
    # VS Code paths for different OS
    VSCODE_PATHS = {
        'win32': [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\dLNk IDE\Code.exe"),
            r"C:\Program Files\dLNk IDE\Code.exe",
            r"C:\Program Files (x86)\dLNk IDE\Code.exe"
        ],
        'darwin': [
            "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
            os.path.expanduser("~/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code")
        ],
        'linux': [
            "/usr/bin/code",
            "/usr/local/bin/code",
            os.path.expanduser("~/.local/bin/code")
        ]
    }
    
    # Extension marketplace
    DLNK_AI_EXTENSION_ID = "Google.dlnk_ai"
    
    def __init__(self):
        self.platform = sys.platform
        self.home = Path.home()
        self.dlnk_dir = self.home / ".dlnk"
        self.profile_dir = self.dlnk_dir / "vscode_profile"
        
        # Ensure directories exist
        self.dlnk_dir.mkdir(parents=True, exist_ok=True)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
    
    def find_vscode(self) -> Optional[str]:
        """Find VS Code executable"""
        paths = self.VSCODE_PATHS.get(self.platform, self.VSCODE_PATHS['linux'])
        
        for path in paths:
            if os.path.exists(path):
                return path
        
        # Try 'code' command
        try:
            result = subprocess.run(['which', 'code'], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        
        return None
    
    def install_vscode(self) -> bool:
        """Install VS Code if not found"""
        print("📥 VS Code not found. Installing...")
        
        if self.platform == 'win32':
            # Windows: Download and run installer
            url = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
            installer_path = self.dlnk_dir / "vscode_installer.exe"
            
            print("   Downloading VS Code installer...")
            response = requests.get(url, stream=True)
            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            print("   Running installer (silent mode)...")
            subprocess.run([str(installer_path), '/VERYSILENT', '/MERGETASKS=!runcode'])
            return True
            
        elif self.platform == 'darwin':
            # macOS: Use Homebrew
            print("   Installing via Homebrew...")
            subprocess.run(['brew', 'install', '--cask', 'visual-studio-code'])
            return True
            
        else:
            # Linux: Use snap or apt
            print("   Installing via snap...")
            try:
                subprocess.run(['sudo', 'snap', 'install', 'code', '--classic'])
                return True
            except:
                print("   Trying apt...")
                subprocess.run(['sudo', 'apt', 'install', '-y', 'code'])
                return True
        
        return False
    
    def install_extension(self, vscode_path: str) -> bool:
        """Install dLNk AI extension"""
        print(f"📦 Installing dLNk AI extension...")
        
        try:
            # Use VS Code CLI to install extension
            result = subprocess.run([
                vscode_path,
                '--install-extension', self.DLNK_AI_EXTENSION_ID,
                '--user-data-dir', str(self.profile_dir)
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("   ✅ Extension installed successfully")
                return True
            else:
                print(f"   ⚠️ Extension install output: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"   ❌ Failed to install extension: {e}")
            return False
    
    def configure_vscode(self) -> bool:
        """Configure VS Code settings for dLNk AI"""
        print("⚙️ Configuring VS Code...")
        
        settings_dir = self.profile_dir / "User"
        settings_dir.mkdir(parents=True, exist_ok=True)
        
        settings = {
            # dLNk AI settings
            "dlnk_ai.enableAutoComplete": True,
            "dlnk_ai.enableChat": True,
            "dlnk_ai.model": "gemini-2.0-flash",
            
            # Proxy settings (for token harvesting)
            "http.proxy": "http://localhost:8081",
            "http.proxyStrictSSL": False,
            
            # Editor settings
            "editor.fontSize": 14,
            "editor.fontFamily": "'Fira Code', Consolas, 'Courier New', monospace",
            "editor.fontLigatures": True,
            
            # Theme
            "workbench.colorTheme": "One Dark Pro",
            
            # Terminal
            "terminal.integrated.fontSize": 13,
            
            # Auto-save
            "files.autoSave": "afterDelay",
            "files.autoSaveDelay": 1000,
            
            # dLNk branding
            "window.title": "dLNk AI IDE - ${activeEditorShort}${separator}${rootName}"
        }
        
        settings_file = settings_dir / "settings.json"
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        
        print(f"   ✅ Settings saved to {settings_file}")
        return True
    
    def import_token(self, token_file: str) -> bool:
        """Import token from file"""
        print(f"🔑 Importing token from {token_file}...")
        
        try:
            with open(token_file, 'r') as f:
                data = json.load(f)
            
            # Extract tokens
            access_token = None
            refresh_token = None
            
            if 'tokens' in data:
                access_token = data['tokens'].get('access_token')
                refresh_token = data['tokens'].get('refresh_token')
            else:
                access_token = data.get('access_token')
                refresh_token = data.get('refresh_token')
            
            if not access_token:
                print("   ❌ No access_token found in file")
                return False
            
            # Save to dLNk token storage
            token_storage = self.dlnk_dir / "tokens" / "unified_tokens.json"
            token_storage.parent.mkdir(parents=True, exist_ok=True)
            
            import time
            from datetime import datetime
            
            tokens = {}
            if token_storage.exists():
                with open(token_storage, 'r') as f:
                    tokens = json.load(f)
            
            tokens['dlnk_ai'] = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expiry': time.time() + 3600,
                'updated_at': datetime.now().isoformat()
            }
            
            with open(token_storage, 'w') as f:
                json.dump(tokens, f, indent=2)
            
            print(f"   ✅ Token imported successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Failed to import token: {e}")
            return False
    
    def create_launcher_script(self, vscode_path: str) -> str:
        """Create launcher script"""
        print("📝 Creating launcher script...")
        
        if self.platform == 'win32':
            script_path = self.dlnk_dir / "launch_dlnk.bat"
            script_content = f'''@echo off
echo Starting dLNk AI IDE...
start "" "{vscode_path}" --user-data-dir="{self.profile_dir}" --proxy-server=http://localhost:8081 --ignore-certificate-errors
'''
        else:
            script_path = self.dlnk_dir / "launch_dlnk.sh"
            script_content = f'''#!/bin/bash
echo "Starting dLNk AI IDE..."
"{vscode_path}" --user-data-dir="{self.profile_dir}" --proxy-server=http://localhost:8081 --ignore-certificate-errors &
'''
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        if self.platform != 'win32':
            os.chmod(script_path, 0o755)
        
        print(f"   ✅ Launcher created: {script_path}")
        return str(script_path)
    
    def install(self, token_file: str = None) -> bool:
        """
        Full installation process
        
        Args:
            token_file: Path to stolen_data.json (optional)
        
        Returns:
            True if successful
        """
        print("=" * 60)
        print("🚀 dLNk dLNk AI Installer")
        print("=" * 60)
        
        # 1. Find or install VS Code
        vscode_path = self.find_vscode()
        if not vscode_path:
            if not self.install_vscode():
                print("❌ Failed to install VS Code")
                return False
            vscode_path = self.find_vscode()
        
        if not vscode_path:
            print("❌ VS Code not found after installation")
            return False
        
        print(f"✅ VS Code found: {vscode_path}")
        
        # 2. Install dLNk AI extension
        self.install_extension(vscode_path)
        
        # 3. Configure VS Code
        self.configure_vscode()
        
        # 4. Import token if provided
        if token_file:
            self.import_token(token_file)
        
        # 5. Create launcher script
        launcher = self.create_launcher_script(vscode_path)
        
        print("\n" + "=" * 60)
        print("✅ Installation Complete!")
        print("=" * 60)
        print(f"\n📂 Profile directory: {self.profile_dir}")
        print(f"🚀 Launcher script: {launcher}")
        print(f"\nTo start dLNk AI IDE, run:")
        print(f"   {launcher}")
        
        return True
    
    def launch(self) -> bool:
        """Launch VS Code with dLNk profile"""
        vscode_path = self.find_vscode()
        if not vscode_path:
            print("❌ VS Code not found")
            return False
        
        print("🚀 Launching dLNk AI IDE...")
        
        subprocess.Popen([
            vscode_path,
            f'--user-data-dir={self.profile_dir}',
            '--proxy-server=http://localhost:8081',
            '--ignore-certificate-errors'
        ])
        
        return True


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="dLNk AI Installer")
    parser.add_argument('--token', type=str, help='Path to token file')
    parser.add_argument('--launch', action='store_true', help='Launch after install')
    
    args = parser.parse_args()
    
    installer = dLNk AIInstaller()
    
    if installer.install(args.token):
        if args.launch:
            installer.launch()


if __name__ == "__main__":
    main()
