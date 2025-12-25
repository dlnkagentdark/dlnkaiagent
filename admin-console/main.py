#!/usr/bin/env python3
"""
dLNk Admin Console - Main Entry Point
Desktop Application for managing dLNk IDE

Usage:
    python main.py

Requirements:
    pip install customtkinter pillow requests matplotlib cryptography pyotp
"""

import sys
import os

# Ensure the app directory is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from app.app import AdminApp


def main():
    """Main entry point for dLNk Admin Console"""
    # Set appearance mode
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    # Print startup banner
    print("""
╔══════════════════════════════════════════════════════════╗
║              dLNk Admin Console v1.0.0                   ║
║                                                          ║
║  Desktop Application for dLNk IDE Management             ║
║                                                          ║
║  Features:                                               ║
║    • Dashboard with real-time statistics                 ║
║    • License management (create, revoke, extend)         ║
║    • User management (view, ban, unban)                  ║
║    • C2 Logs and Alert monitoring                        ║
║    • Antigravity Token management                        ║
║    • System settings configuration                       ║
║                                                          ║
║  Login with your Admin Key to get started.               ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    # Create and run app
    try:
        app = AdminApp()
        app.protocol("WM_DELETE_WINDOW", app.on_closing)
        app.mainloop()
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
