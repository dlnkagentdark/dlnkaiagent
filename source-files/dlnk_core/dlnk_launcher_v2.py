#!/usr/bin/env python3
"""
dLNk IDE Launcher v2.0
หน้าต่าง Login และ Launcher สำหรับ dLNk IDE
UI โทนดาร์กพร้อมระบบ License Key
รองรับทั้งการเชื่อมต่อ Server และ Offline Mode
"""

import customtkinter as ctk
import subprocess
import threading
import time
import os
import sys
import webbrowser
import hashlib
import platform
import uuid
import json
from pathlib import Path
from PIL import Image

# Import license system
try:
    from dlnk_license_system import DLNKLicenseSystem, LicenseType, validate_encrypted_license
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from dlnk_license_system import DLNKLicenseSystem, LicenseType, validate_encrypted_license

# --- CONFIGURATION ---
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

APP_NAME = "dLNk IDE"
APP_VERSION = "2.0.0"
TELEGRAM_LINK = "https://t.me/dlnkai"
CONFIG_DIR = Path.home() / ".dlnk-ide"
CONFIG_FILE = CONFIG_DIR / "config.json"
LICENSE_DB = CONFIG_DIR / "licenses.db"

# Dark theme colors
COLORS = {
    "bg_dark": "#0d0d0d",
    "bg_secondary": "#1a1a1a",
    "bg_card": "#242424",
    "accent": "#00ff88",
    "accent_hover": "#00cc6a",
    "text_primary": "#ffffff",
    "text_secondary": "#888888",
    "error": "#ff4444",
    "success": "#00ff88",
    "warning": "#ffcc00",
    "border": "#333333"
}


def get_hardware_id() -> str:
    """Generate unique hardware ID"""
    info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
    mac = uuid.getnode()
    combined = f"{info}-{mac}"
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


class DLNKLauncher(ctk.CTk):
    """
    dLNk IDE Launcher v2.0
    หน้าต่าง Login และ Launcher หลัก
    """
    
    def __init__(self):
        super().__init__()
        
        # Initialize config directory
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize license system
        self.license_system = DLNKLicenseSystem(str(LICENSE_DB))
        
        # Load saved config
        self.config = self.load_config()
        
        # Hardware ID
        self.hwid = get_hardware_id()
        
        # Process handles
        self.proxy_process = None
        self.ai_bridge_process = None
        
        # Window setup
        self.title(f"{APP_NAME} - Launcher")
        self.geometry("520x680")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        
        # Create UI
        self.create_ui()
        
        # Check for saved key
        if self.config.get("license_key"):
            self.entry_key.insert(0, self.config["license_key"])
            self.remember_var.set(True)
            
        # Server URL
        self.server_url = "http://127.0.0.1:5000"
        if os.path.exists("server_ip.txt"):
            with open("server_ip.txt", "r") as f:
                self.server_url = f.read().strip()
                
    def load_config(self) -> dict:
        """Load configuration from file"""
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
        
    def save_config(self):
        """Save configuration to file"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
            
    def create_ui(self):
        """Create main UI"""
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        self.main_frame.pack(fill="both", expand=True, padx=30, pady=20)
        
        # Logo
        try:
            image_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dlnk_logo.png")
            if os.path.exists(image_path):
                self.logo_image = ctk.CTkImage(Image.open(image_path), size=(180, 180))
                self.label_logo = ctk.CTkLabel(self.main_frame, text="", image=self.logo_image)
                self.label_logo.pack(pady=(10, 5))
            else:
                raise FileNotFoundError()
        except Exception as e:
            self.label_title = ctk.CTkLabel(
                self.main_frame, 
                text="dLNk", 
                font=ctk.CTkFont(size=64, weight="bold"),
                text_color=COLORS["accent"]
            )
            self.label_title.pack(pady=(20, 5))
            
        # Subtitle
        self.label_subtitle = ctk.CTkLabel(
            self.main_frame, 
            text="Intelligent Development Environment", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS["text_secondary"]
        )
        self.label_subtitle.pack(pady=(0, 20))
        
        # License Frame
        self.license_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["bg_card"],
            corner_radius=15
        )
        self.license_frame.pack(fill="x", pady=10)
        
        # License Label
        self.license_label = ctk.CTkLabel(
            self.license_frame,
            text="🔑 License Key",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        self.license_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        # License Entry
        self.entry_key = ctk.CTkEntry(
            self.license_frame, 
            placeholder_text="Enter your license key...",
            font=ctk.CTkFont(size=13),
            height=45,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"],
            text_color=COLORS["text_primary"]
        )
        self.entry_key.pack(fill="x", padx=20, pady=(0, 10))
        
        # Remember checkbox
        self.remember_var = ctk.BooleanVar(value=False)
        self.remember_check = ctk.CTkCheckBox(
            self.license_frame,
            text="Remember my license key",
            variable=self.remember_var,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"]
        )
        self.remember_check.pack(anchor="w", padx=20, pady=(0, 15))
        
        # Status Label
        self.label_status = ctk.CTkLabel(
            self.main_frame, 
            text="Ready to connect...",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"]
        )
        self.label_status.pack(pady=10)
        
        # Progress bar (hidden by default)
        self.progress_bar = ctk.CTkProgressBar(
            self.main_frame,
            fg_color=COLORS["bg_secondary"],
            progress_color=COLORS["accent"],
            height=4
        )
        self.progress_bar.set(0)
        
        # Launch Button
        self.button_login = ctk.CTkButton(
            self.main_frame, 
            text="🚀 Launch dLNk IDE",
            command=self.login_event,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=50,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_dark"],
            corner_radius=10
        )
        self.button_login.pack(fill="x", pady=15)
        
        # Mode selection
        self.mode_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.mode_frame.pack(fill="x", pady=5)
        
        self.mode_var = ctk.StringVar(value="auto")
        
        self.mode_auto = ctk.CTkRadioButton(
            self.mode_frame,
            text="Auto",
            variable=self.mode_var,
            value="auto",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"]
        )
        self.mode_auto.pack(side="left", padx=10)
        
        self.mode_online = ctk.CTkRadioButton(
            self.mode_frame,
            text="Online",
            variable=self.mode_var,
            value="online",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"]
        )
        self.mode_online.pack(side="left", padx=10)
        
        self.mode_offline = ctk.CTkRadioButton(
            self.mode_frame,
            text="Offline",
            variable=self.mode_var,
            value="offline",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"],
            fg_color=COLORS["accent"]
        )
        self.mode_offline.pack(side="left", padx=10)
        
        # Info Frame
        self.info_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["bg_secondary"],
            corner_radius=10
        )
        self.info_frame.pack(fill="x", pady=15)
        
        # Hardware ID
        self.hwid_label = ctk.CTkLabel(
            self.info_frame,
            text=f"Hardware ID: {self.hwid[:16]}...",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        self.hwid_label.pack(pady=(8, 2))
        
        # Version
        self.version_label = ctk.CTkLabel(
            self.info_frame,
            text=f"Version {APP_VERSION}",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        self.version_label.pack(pady=(2, 8))
        
        # Footer buttons
        self.footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.footer_frame.pack(fill="x", pady=5)
        
        self.button_admin = ctk.CTkButton(
            self.footer_frame,
            text="Admin Console",
            command=self.open_admin_console,
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"],
            width=100,
            height=30
        )
        self.button_admin.pack(side="left")
        
        self.button_contact = ctk.CTkButton(
            self.footer_frame,
            text="Contact Support",
            command=lambda: webbrowser.open(TELEGRAM_LINK),
            font=ctk.CTkFont(size=11),
            fg_color="transparent",
            hover_color=COLORS["bg_card"],
            text_color=COLORS["text_secondary"],
            width=100,
            height=30
        )
        self.button_contact.pack(side="right")
        
    def set_status(self, message: str, color: str = None):
        """Set status message"""
        if color is None:
            color = COLORS["text_secondary"]
        self.label_status.configure(text=message, text_color=color)
        
    def login_event(self):
        """Handle login button click"""
        key = self.entry_key.get().strip()
        
        if not key:
            self.set_status("⚠️ Please enter a license key", COLORS["error"])
            return
            
        self.button_login.configure(state="disabled", text="Verifying...")
        self.progress_bar.pack(fill="x", pady=5)
        self.progress_bar.set(0.2)
        self.set_status("Validating license...", COLORS["warning"])
        
        # Run validation in separate thread
        threading.Thread(target=self.validate_and_launch, args=(key,), daemon=True).start()
        
    def validate_and_launch(self, key: str):
        """Validate license and launch IDE"""
        mode = self.mode_var.get()
        
        try:
            self.after(0, lambda: self.progress_bar.set(0.4))
            
            # Try online verification first (if not offline mode)
            if mode != "offline":
                online_valid = self.try_online_verification(key)
                if online_valid:
                    self.after(0, lambda: self.progress_bar.set(0.6))
                    self.save_license_key(key)
                    self.after(0, self.perform_launch_sequence)
                    return
                elif mode == "online":
                    # Online mode required but failed
                    self.after(0, lambda: self.set_status("❌ Server verification failed", COLORS["error"]))
                    self.after(0, lambda: self.button_login.configure(state="normal", text="🚀 Launch dLNk IDE"))
                    self.after(0, lambda: self.progress_bar.pack_forget())
                    return
                    
            # Try offline verification
            self.after(0, lambda: self.set_status("Trying offline verification...", COLORS["warning"]))
            
            # First try encrypted key format
            is_valid, message, data = validate_encrypted_license(key)
            if is_valid:
                self.after(0, lambda: self.progress_bar.set(0.6))
                self.save_license_key(key)
                self.after(0, self.perform_launch_sequence)
                return
                
            # Then try database key format
            valid, msg, license_obj = self.license_system.verify_license(key, self.hwid)
            if valid:
                self.after(0, lambda: self.progress_bar.set(0.6))
                self.save_license_key(key)
                self.after(0, self.perform_launch_sequence)
                return
                
            # All verification failed
            self.after(0, lambda: self.set_status(f"❌ {msg}", COLORS["error"]))
            self.after(0, lambda: self.button_login.configure(state="normal", text="🚀 Launch dLNk IDE"))
            self.after(0, lambda: self.progress_bar.pack_forget())
            
        except Exception as e:
            self.after(0, lambda: self.set_status(f"❌ Error: {str(e)}", COLORS["error"]))
            self.after(0, lambda: self.button_login.configure(state="normal", text="🚀 Launch dLNk IDE"))
            self.after(0, lambda: self.progress_bar.pack_forget())
            
    def try_online_verification(self, key: str) -> bool:
        """Try online license verification"""
        try:
            import requests
            r = requests.post(
                f"{self.server_url}/verify",
                json={"key": key, "hwid": self.hwid},
                timeout=5
            )
            return r.status_code == 200
        except:
            return False
            
    def save_license_key(self, key: str):
        """Save license key if remember is checked"""
        if self.remember_var.get():
            self.config["license_key"] = key
            self.save_config()
            
            # Also save to legacy file
            with open("dlnk_key.txt", "w") as f:
                f.write(key)
        else:
            self.config.pop("license_key", None)
            self.save_config()
            
    def perform_launch_sequence(self):
        """Perform the launch sequence"""
        self.progress_bar.set(0.7)
        self.set_status("Starting AI Bridge...", COLORS["accent"])
        
        # 1. Start AI Bridge
        try:
            ai_bridge_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dlnk_ai_bridge.py")
            if os.path.exists(ai_bridge_path):
                self.ai_bridge_process = subprocess.Popen(
                    [sys.executable, ai_bridge_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                time.sleep(1)
        except Exception as e:
            print(f"AI Bridge start failed: {e}")
            
        self.progress_bar.set(0.8)
        self.set_status("Starting MITM Engine...", COLORS["accent"])
        
        # 2. Start MITM Proxy (optional)
        try:
            proxy_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "mitm_https_proxy.py")
            if os.path.exists(proxy_path):
                self.proxy_process = subprocess.Popen(
                    [sys.executable, proxy_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                )
                time.sleep(2)
        except Exception as e:
            print(f"Proxy start failed: {e}")
            
        self.progress_bar.set(0.9)
        self.set_status("Launching IDE...", COLORS["accent"])
        
        # 3. Launch IDE
        ide_launched = self.launch_ide()
        
        if ide_launched:
            self.progress_bar.set(1.0)
            self.set_status("✓ dLNk IDE is running", COLORS["success"])
            self.button_login.configure(text="Running...", state="disabled")
            
            # Close launcher after delay
            self.after(3000, self.destroy)
        else:
            self.set_status("❌ Failed to launch IDE", COLORS["error"])
            self.button_login.configure(state="normal", text="🚀 Launch dLNk IDE")
            self.progress_bar.pack_forget()
            
    def launch_ide(self) -> bool:
        """Launch the IDE"""
        # Try dLNk IDE first
        dlnk_paths = [
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "dlnk-ide.exe"),
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "dLNk AI.exe"),
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "bin", "dlnk-ide"),
        ]
        
        for path in dlnk_paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen([path])
                    return True
                except:
                    continue
                    
        # Fallback to VS Code with proxy
        vscode_paths = [
            os.path.expandvars(r"%LOCALAPPDATA%\Programs\dLNk IDE\Code.exe"),
            r"C:\Program Files\dLNk IDE\Code.exe",
            r"C:\Program Files (x86)\dLNk IDE\Code.exe",
            "/usr/bin/code",
            "/usr/local/bin/code"
        ]
        
        for path in vscode_paths:
            if os.path.exists(path):
                try:
                    subprocess.Popen([
                        path,
                        "--proxy-server=http://localhost:8081",
                        "--ignore-certificate-errors",
                        "--user-data-dir=dlnk_vscode_profile"
                    ])
                    return True
                except:
                    continue
                    
        return False
        
    def open_admin_console(self):
        """Open Admin Console"""
        admin_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "dlnk_admin_console.py")
        
        if os.path.exists(admin_path):
            subprocess.Popen([sys.executable, admin_path])
        else:
            self.set_status("Admin Console not found", COLORS["error"])


def main():
    """Main entry point"""
    app = DLNKLauncher()
    app.mainloop()


if __name__ == "__main__":
    main()
