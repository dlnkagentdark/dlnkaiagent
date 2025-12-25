#!/usr/bin/env python3
"""
dLNk IDE - Login Window
AI-04 UI/UX Designer
Version: 1.0.0

Modern Dark Theme Login Window using CustomTkinter
Color Palette: dLNk Official Colors
"""

import customtkinter as ctk
from PIL import Image
import os
import sys
import hashlib
import platform
import uuid

# Set appearance mode and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# dLNk Official Color Palette
COLORS = {
    # Primary Colors
    'bg_primary': '#1a1a2e',      # พื้นหลังหลัก - Dark Blue-Black
    'bg_secondary': '#16213e',    # พื้นหลังรอง - Darker Blue
    'bg_tertiary': '#0f3460',     # พื้นหลังที่สาม - Deep Blue
    
    # Accent Colors
    'accent_primary': '#e94560',   # สีเน้นหลัก - Red-Pink
    'accent_secondary': '#533483', # สีเน้นรอง - Purple
    'accent_success': '#00d9ff',   # สำเร็จ - Cyan
    'accent_warning': '#ffc107',   # เตือน - Yellow
    'accent_error': '#ff4757',     # ผิดพลาด - Red
    
    # Text Colors
    'text_primary': '#ffffff',     # ข้อความหลัก - White
    'text_secondary': '#a0a0a0',   # ข้อความรอง - Gray
    'text_muted': '#6c757d',       # ข้อความจาง - Dark Gray
    'text_link': '#00d9ff',        # ลิงก์ - Cyan
    
    # Border & Shadow
    'border_color': '#2d2d44',     # ขอบ
}

# App Configuration
APP_NAME = "dLNk IDE"
APP_VERSION = "1.0.0"
APP_TAGLINE = "AI-Powered Development"


def get_hardware_id() -> str:
    """Generate unique hardware ID for license validation"""
    info = f"{platform.node()}-{platform.machine()}-{platform.processor()}"
    mac = uuid.getnode()
    combined = f"{info}-{mac}"
    return hashlib.sha256(combined.encode()).hexdigest()[:32]


class LoginWindow(ctk.CTk):
    """
    dLNk IDE Login Window
    Modern Dark Theme with Official Color Palette
    """
    
    def __init__(self):
        super().__init__()
        
        # Window Configuration
        self.title(f"{APP_NAME} - Login")
        self.geometry("450x650")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Center window on screen
        self.center_window()
        
        # Hardware ID
        self.hwid = get_hardware_id()
        
        # Create UI
        self.create_widgets()
        
        # Bind events
        self.bind_events()
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 450
        height = 650
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create all UI widgets"""
        
        # ===== LOGO SECTION =====
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(pady=(40, 20))
        
        # Logo Text with Gradient Effect (simulated)
        logo_label = ctk.CTkLabel(
            logo_frame,
            text="dLNk",
            font=ctk.CTkFont(family="Segoe UI", size=56, weight="bold"),
            text_color=COLORS['accent_primary']
        )
        logo_label.pack()
        
        # Version Label
        version_label = ctk.CTkLabel(
            logo_frame,
            text=f"IDE v{APP_VERSION}",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="normal"),
            text_color=COLORS['text_secondary']
        )
        version_label.pack(pady=(5, 0))
        
        # Tagline
        tagline_label = ctk.CTkLabel(
            logo_frame,
            text=APP_TAGLINE,
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=COLORS['text_muted']
        )
        tagline_label.pack(pady=(5, 0))
        
        # ===== INPUT SECTION =====
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(pady=25, padx=45, fill="x")
        
        # Username/Email Label
        username_label = ctk.CTkLabel(
            input_frame,
            text="Username / Email",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        )
        username_label.pack(anchor="w", pady=(0, 5))
        
        # Username Entry
        self.username_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Enter your username or email",
            height=48,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_color'],
            border_width=2,
            corner_radius=10,
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_muted']
        )
        self.username_entry.pack(fill="x", pady=(0, 18))
        
        # License Key Label
        license_label = ctk.CTkLabel(
            input_frame,
            text="License Key",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        )
        license_label.pack(anchor="w", pady=(0, 5))
        
        # License Key Entry
        self.license_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="XXXX-XXXX-XXXX-XXXX",
            height=48,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_color'],
            border_width=2,
            corner_radius=10,
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_muted'],
            show="•"
        )
        self.license_entry.pack(fill="x", pady=(0, 18))
        
        # Show/Hide License Key Button
        self.show_license = False
        self.toggle_btn = ctk.CTkButton(
            input_frame,
            text="👁 Show",
            width=70,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            corner_radius=6,
            command=self.toggle_license_visibility
        )
        self.toggle_btn.place(relx=1.0, rely=0.52, anchor="e", x=-5)
        
        # Remember Me Checkbox
        self.remember_var = ctk.BooleanVar(value=False)
        remember_cb = ctk.CTkCheckBox(
            input_frame,
            text="Remember me",
            variable=self.remember_var,
            font=ctk.CTkFont(size=13),
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_secondary'],
            border_color=COLORS['border_color'],
            checkmark_color=COLORS['text_primary'],
            text_color=COLORS['text_secondary']
        )
        remember_cb.pack(anchor="w", pady=(0, 25))
        
        # Login Button
        self.login_btn = ctk.CTkButton(
            input_frame,
            text="LOGIN",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['accent_primary'],
            hover_color="#c73e54",
            text_color=COLORS['text_primary'],
            corner_radius=10,
            command=self.login
        )
        self.login_btn.pack(fill="x", pady=(0, 15))
        
        # Register Link Frame
        register_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        register_frame.pack()
        
        ctk.CTkLabel(
            register_frame,
            text="Don't have a license?",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted']
        ).pack(side="left")
        
        register_btn = ctk.CTkButton(
            register_frame,
            text="Register",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['accent_success'],
            width=70,
            height=28,
            command=self.show_register
        )
        register_btn.pack(side="left", padx=(5, 0))
        
        # ===== DIVIDER =====
        divider_frame = ctk.CTkFrame(self, fg_color="transparent")
        divider_frame.pack(fill="x", padx=45, pady=15)
        
        ctk.CTkFrame(
            divider_frame,
            height=1,
            fg_color=COLORS['border_color']
        ).pack(fill="x")
        
        # ===== STATUS SECTION =====
        status_frame = ctk.CTkFrame(
            self,
            fg_color=COLORS['bg_secondary'],
            corner_radius=10
        )
        status_frame.pack(fill="x", padx=45, pady=10)
        
        # Status Indicator
        status_inner = ctk.CTkFrame(status_frame, fg_color="transparent")
        status_inner.pack(pady=12, padx=15)
        
        # Status dot
        self.status_dot = ctk.CTkLabel(
            status_inner,
            text="●",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['accent_success']
        )
        self.status_dot.pack(side="left", padx=(0, 8))
        
        self.status_label = ctk.CTkLabel(
            status_inner,
            text="Offline Mode Available",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.status_label.pack(side="left")
        
        # ===== FOOTER =====
        footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        footer_frame.pack(side="bottom", pady=20)
        
        # Hardware ID (truncated)
        hwid_label = ctk.CTkLabel(
            footer_frame,
            text=f"HWID: {self.hwid[:16]}...",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted']
        )
        hwid_label.pack()
        
        # Copyright
        copyright_label = ctk.CTkLabel(
            footer_frame,
            text="© 2024 dLNk Team. All rights reserved.",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_muted']
        )
        copyright_label.pack(pady=(5, 0))
    
    def bind_events(self):
        """Bind keyboard and mouse events"""
        self.username_entry.bind("<Return>", lambda e: self.license_entry.focus())
        self.license_entry.bind("<Return>", lambda e: self.login())
        
        # Focus effects
        self.username_entry.bind("<FocusIn>", lambda e: self.on_entry_focus(self.username_entry, True))
        self.username_entry.bind("<FocusOut>", lambda e: self.on_entry_focus(self.username_entry, False))
        self.license_entry.bind("<FocusIn>", lambda e: self.on_entry_focus(self.license_entry, True))
        self.license_entry.bind("<FocusOut>", lambda e: self.on_entry_focus(self.license_entry, False))
    
    def on_entry_focus(self, entry, focused):
        """Handle entry focus visual feedback"""
        if focused:
            entry.configure(border_color=COLORS['accent_primary'])
        else:
            entry.configure(border_color=COLORS['border_color'])
    
    def toggle_license_visibility(self):
        """Toggle license key visibility"""
        self.show_license = not self.show_license
        if self.show_license:
            self.license_entry.configure(show="")
            self.toggle_btn.configure(text="🔒 Hide")
        else:
            self.license_entry.configure(show="•")
            self.toggle_btn.configure(text="👁 Show")
    
    def update_status(self, message: str, status_type: str = "info"):
        """Update status message with appropriate color"""
        colors = {
            "info": COLORS['text_secondary'],
            "success": COLORS['accent_success'],
            "warning": COLORS['accent_warning'],
            "error": COLORS['accent_error']
        }
        dot_colors = {
            "info": COLORS['text_muted'],
            "success": COLORS['accent_success'],
            "warning": COLORS['accent_warning'],
            "error": COLORS['accent_error']
        }
        self.status_label.configure(text=message, text_color=colors.get(status_type, colors["info"]))
        self.status_dot.configure(text_color=dot_colors.get(status_type, dot_colors["info"]))
    
    def login(self):
        """Handle login button click"""
        username = self.username_entry.get().strip()
        license_key = self.license_entry.get().strip()
        
        # Validation
        if not username:
            self.update_status("Please enter username or email", "error")
            self.username_entry.focus()
            return
        
        if not license_key:
            self.update_status("Please enter license key", "error")
            self.license_entry.focus()
            return
        
        # Disable button during login
        self.login_btn.configure(state="disabled", text="Logging in...")
        self.update_status("Validating license...", "info")
        
        # Simulate login process (replace with actual implementation)
        self.after(1500, lambda: self.login_complete(True))
    
    def login_complete(self, success: bool):
        """Handle login completion"""
        self.login_btn.configure(state="normal", text="LOGIN")
        
        if success:
            self.update_status("Login successful! Launching IDE...", "success")
            # Save credentials if remember me is checked
            if self.remember_var.get():
                # Implement save logic
                pass
            # Launch main application
            self.after(1000, self.launch_ide)
        else:
            self.update_status("Invalid license key", "error")
    
    def launch_ide(self):
        """Launch the main IDE application"""
        print("Launching dLNk IDE...")
        # Implement IDE launch logic
        self.destroy()
    
    def show_register(self):
        """Open registration window"""
        print("Opening registration window...")
        # Import and open RegisterWindow
        try:
            from register_window import RegisterWindow
            self.withdraw()
            register = RegisterWindow(self)
            register.mainloop()
        except ImportError:
            self.update_status("Registration module not found", "error")


class RegisterWindow(ctk.CTkToplevel):
    """Registration Window for new users"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        
        # Window Configuration
        self.title(f"{APP_NAME} - Register")
        self.geometry("450x550")
        self.resizable(False, False)
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Center window
        self.center_window()
        
        # Create UI
        self.create_widgets()
        
        # Handle close
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def center_window(self):
        """Center the window on screen"""
        self.update_idletasks()
        width = 450
        height = 550
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create registration form widgets"""
        
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(30, 20))
        
        ctk.CTkLabel(
            header_frame,
            text="Create Account",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['accent_primary']
        ).pack()
        
        ctk.CTkLabel(
            header_frame,
            text="Register for a new dLNk IDE license",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary']
        ).pack(pady=(5, 0))
        
        # Form Frame
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=20, padx=45, fill="x")
        
        # Email
        ctk.CTkLabel(
            form_frame,
            text="Email Address",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, 5))
        
        self.email_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="your@email.com",
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_color'],
            border_width=2,
            corner_radius=10
        )
        self.email_entry.pack(fill="x", pady=(0, 15))
        
        # Username
        ctk.CTkLabel(
            form_frame,
            text="Username",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, 5))
        
        self.reg_username_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Choose a username",
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_color'],
            border_width=2,
            corner_radius=10
        )
        self.reg_username_entry.pack(fill="x", pady=(0, 15))
        
        # Telegram Username
        ctk.CTkLabel(
            form_frame,
            text="Telegram Username (Optional)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        ).pack(anchor="w", pady=(0, 5))
        
        self.telegram_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="@username",
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_color'],
            border_width=2,
            corner_radius=10
        )
        self.telegram_entry.pack(fill="x", pady=(0, 20))
        
        # Terms Checkbox
        self.terms_var = ctk.BooleanVar(value=False)
        terms_cb = ctk.CTkCheckBox(
            form_frame,
            text="I agree to the Terms of Service",
            variable=self.terms_var,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_secondary'],
            text_color=COLORS['text_secondary']
        )
        terms_cb.pack(anchor="w", pady=(0, 20))
        
        # Register Button
        self.register_btn = ctk.CTkButton(
            form_frame,
            text="REGISTER",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['accent_primary'],
            hover_color="#c73e54",
            corner_radius=10,
            command=self.register
        )
        self.register_btn.pack(fill="x", pady=(0, 15))
        
        # Back to Login
        back_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        back_frame.pack()
        
        ctk.CTkLabel(
            back_frame,
            text="Already have a license?",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_muted']
        ).pack(side="left")
        
        back_btn = ctk.CTkButton(
            back_frame,
            text="Login",
            font=ctk.CTkFont(size=12, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['accent_success'],
            width=50,
            height=28,
            command=self.on_close
        )
        back_btn.pack(side="left", padx=(5, 0))
    
    def register(self):
        """Handle registration"""
        email = self.email_entry.get().strip()
        username = self.reg_username_entry.get().strip()
        
        if not email or not username:
            return
        
        if not self.terms_var.get():
            return
        
        # Implement registration logic
        print(f"Registering: {email}, {username}")
        self.on_close()
    
    def on_close(self):
        """Handle window close"""
        self.parent.deiconify()
        self.destroy()


if __name__ == "__main__":
    app = LoginWindow()
    app.mainloop()
