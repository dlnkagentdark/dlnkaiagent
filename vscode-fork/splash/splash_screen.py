#!/usr/bin/env python3
"""
dLNk IDE - Splash Screen
AI-04 UI/UX Designer
Version: 1.0.0

Animated splash screen displayed during application startup
"""

import customtkinter as ctk
import threading
import time
from typing import Callable, Optional

# Set appearance mode
ctk.set_appearance_mode("dark")

# dLNk Official Color Palette
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_tertiary': '#0f3460',
    'accent_primary': '#e94560',
    'accent_secondary': '#533483',
    'accent_success': '#00d9ff',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'text_muted': '#6c757d',
}

APP_NAME = "dLNk IDE"
APP_VERSION = "1.0.0"
APP_TAGLINE = "AI-Powered Development"


class SplashScreen(ctk.CTkToplevel):
    """
    Animated Splash Screen for dLNk IDE
    Shows logo, loading animation, and status messages
    """
    
    def __init__(self, parent=None, on_complete: Optional[Callable] = None):
        super().__init__(parent)
        
        self.on_complete = on_complete
        self.loading_progress = 0
        self.is_loading = True
        
        # Window Configuration
        self.title("")
        self.geometry("500x350")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Remove window decorations
        self.overrideredirect(True)
        
        # Center window
        self.center_window()
        
        # Make window stay on top
        self.attributes('-topmost', True)
        
        # Create UI
        self.create_widgets()
        
        # Start loading animation
        self.start_loading()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 500
        height = 350
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create splash screen widgets"""
        
        # Main Container with border effect
        self.main_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_primary'],
            border_color=COLORS['accent_primary'],
            border_width=2,
            corner_radius=15
        )
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # ===== LOGO SECTION =====
        logo_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        logo_frame.pack(pady=(50, 20))
        
        # Logo Text
        self.logo_label = ctk.CTkLabel(
            logo_frame,
            text="dLNk",
            font=ctk.CTkFont(family="Segoe UI", size=64, weight="bold"),
            text_color=COLORS['accent_primary']
        )
        self.logo_label.pack()
        
        # Version
        version_label = ctk.CTkLabel(
            logo_frame,
            text=f"IDE v{APP_VERSION}",
            font=ctk.CTkFont(size=18),
            text_color=COLORS['text_secondary']
        )
        version_label.pack(pady=(5, 0))
        
        # Tagline
        tagline_label = ctk.CTkLabel(
            logo_frame,
            text=APP_TAGLINE,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_muted']
        )
        tagline_label.pack(pady=(5, 0))
        
        # ===== LOADING SECTION =====
        loading_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        loading_frame.pack(fill="x", padx=60, pady=30)
        
        # Progress Bar
        self.progress_bar = ctk.CTkProgressBar(
            loading_frame,
            height=6,
            fg_color=COLORS['bg_secondary'],
            progress_color=COLORS['accent_primary'],
            corner_radius=3
        )
        self.progress_bar.pack(fill="x")
        self.progress_bar.set(0)
        
        # Status Label
        self.status_label = ctk.CTkLabel(
            loading_frame,
            text="Initializing...",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(pady=(15, 0))
        
        # ===== FOOTER =====
        footer_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=20)
        
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© 2024 dLNk Team",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted']
        )
        copyright_label.pack()
    
    def start_loading(self):
        """Start the loading animation"""
        loading_thread = threading.Thread(target=self.loading_sequence, daemon=True)
        loading_thread.start()
    
    def loading_sequence(self):
        """Simulate loading sequence with status updates"""
        
        loading_steps = [
            ("Initializing core components...", 0.15),
            ("Loading configuration...", 0.25),
            ("Connecting to AI services...", 0.40),
            ("Validating license...", 0.55),
            ("Loading extensions...", 0.70),
            ("Preparing workspace...", 0.85),
            ("Almost ready...", 0.95),
            ("Welcome to dLNk IDE!", 1.0),
        ]
        
        for status, progress in loading_steps:
            if not self.is_loading:
                break
            
            # Update UI in main thread
            self.after(0, lambda s=status, p=progress: self.update_progress(s, p))
            
            # Simulate loading time
            time.sleep(0.4 + (progress * 0.3))
        
        # Complete loading
        self.after(500, self.complete_loading)
    
    def update_progress(self, status: str, progress: float):
        """Update progress bar and status label"""
        self.progress_bar.set(progress)
        self.status_label.configure(text=status)
        
        # Change color when complete
        if progress >= 1.0:
            self.progress_bar.configure(progress_color=COLORS['accent_success'])
    
    def complete_loading(self):
        """Handle loading completion"""
        self.is_loading = False
        
        # Fade out effect (simplified)
        self.after(300, self.close_splash)
    
    def close_splash(self):
        """Close splash screen and trigger callback"""
        if self.on_complete:
            self.on_complete()
        self.destroy()


class SplashScreenStandalone(ctk.CTk):
    """
    Standalone splash screen for testing
    """
    
    def __init__(self):
        super().__init__()
        
        # Hide main window
        self.withdraw()
        
        # Show splash
        self.splash = SplashScreen(self, on_complete=self.on_splash_complete)
    
    def on_splash_complete(self):
        """Called when splash screen completes"""
        print("Splash complete! Launching main application...")
        self.deiconify()
        
        # Show main window
        self.title(f"{APP_NAME}")
        self.geometry("800x600")
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Add placeholder content
        label = ctk.CTkLabel(
            self,
            text="Main Application Window",
            font=ctk.CTkFont(size=24),
            text_color=COLORS['text_primary']
        )
        label.place(relx=0.5, rely=0.5, anchor="center")


def show_splash(on_complete: Optional[Callable] = None) -> SplashScreen:
    """
    Utility function to show splash screen
    
    Args:
        on_complete: Callback function when loading completes
        
    Returns:
        SplashScreen instance
    """
    root = ctk.CTk()
    root.withdraw()
    splash = SplashScreen(root, on_complete=on_complete)
    return splash


if __name__ == "__main__":
    # Test splash screen standalone
    app = SplashScreenStandalone()
    app.mainloop()
