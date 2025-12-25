#!/usr/bin/env python3
"""
dLNk Admin Console - Login View
"""

import customtkinter as ctk
from utils.theme import COLORS


class LoginView(ctk.CTkFrame):
    """Admin Login View"""
    
    def __init__(self, parent, on_success):
        super().__init__(parent, fg_color="transparent")
        
        self.on_success = on_success
        self.create_widgets()
    
    def create_widgets(self):
        """Create login form widgets"""
        # Center container
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")
        
        # Logo
        logo_frame = ctk.CTkFrame(center, fg_color="transparent")
        logo_frame.pack(pady=(0, 10))
        
        logo = ctk.CTkLabel(
            logo_frame,
            text="dLNk",
            font=ctk.CTkFont(size=56, weight="bold"),
            text_color=COLORS['accent']
        )
        logo.pack()
        
        subtitle = ctk.CTkLabel(
            logo_frame,
            text="Admin Console",
            font=ctk.CTkFont(size=20),
            text_color=COLORS['text_secondary']
        )
        subtitle.pack()
        
        # Divider
        ctk.CTkFrame(center, height=1, width=350, fg_color=COLORS['border']).pack(pady=30)
        
        # Login Form
        form_frame = ctk.CTkFrame(center, fg_color="transparent")
        form_frame.pack()
        
        # Admin Key Label
        key_label = ctk.CTkLabel(
            form_frame,
            text="Admin Key",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        key_label.pack(anchor="w", pady=(0, 5))
        
        # Admin Key Entry
        self.admin_key_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="DLNK-ADMIN-XXXX-XXXX-XXXX",
            width=350,
            height=48,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border'],
            show="•"
        )
        self.admin_key_entry.pack(pady=(0, 15))
        self.admin_key_entry.bind("<Return>", lambda e: self.login())
        self.admin_key_entry.bind("<FocusIn>", lambda e: self._on_entry_focus(self.admin_key_entry))
        
        # 2FA Code Label
        totp_label = ctk.CTkLabel(
            form_frame,
            text="2FA Code (optional)",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        totp_label.pack(anchor="w", pady=(0, 5))
        
        # 2FA Code Entry
        self.totp_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="000000",
            width=350,
            height=48,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border']
        )
        self.totp_entry.pack(pady=(0, 25))
        self.totp_entry.bind("<Return>", lambda e: self.login())
        self.totp_entry.bind("<FocusIn>", lambda e: self._on_entry_focus(self.totp_entry))
        
        # Login Button
        self.login_btn = ctk.CTkButton(
            form_frame,
            text="LOGIN",
            width=350,
            height=48,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['accent'],
            hover_color=COLORS['hover'],
            command=self.login
        )
        self.login_btn.pack(pady=(0, 15))
        
        # Error Label
        self.error_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['error']
        )
        self.error_label.pack()
        
        # Version info
        version_label = ctk.CTkLabel(
            center,
            text="v1.0.0",
            font=ctk.CTkFont(size=10),
            text_color=COLORS['text_secondary']
        )
        version_label.pack(pady=(30, 0))
        
        # Focus on admin key entry
        self.admin_key_entry.focus_set()
    
    def _on_entry_focus(self, entry):
        """Handle entry focus - highlight border"""
        entry.configure(border_color=COLORS['accent'])
        
        # Reset other entries
        for e in [self.admin_key_entry, self.totp_entry]:
            if e != entry:
                e.configure(border_color=COLORS['border'])
    
    def login(self):
        """Handle login attempt"""
        admin_key = self.admin_key_entry.get().strip()
        totp_code = self.totp_entry.get().strip()
        
        # Clear previous error
        self.error_label.configure(text="")
        
        # Validate input
        if not admin_key:
            self.error_label.configure(text="Please enter Admin Key")
            self.admin_key_entry.configure(border_color=COLORS['error'])
            return
        
        # Disable button during login
        self.login_btn.configure(state="disabled", text="Logging in...")
        self.update()
        
        # Import auth module
        import sys
        import os
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        from app.auth import AdminAuth
        
        # Attempt login
        auth = AdminAuth()
        success, message, admin_data = auth.login(admin_key, totp_code)
        
        # Re-enable button
        self.login_btn.configure(state="normal", text="LOGIN")
        
        if success:
            self.on_success(admin_data)
        else:
            self.error_label.configure(text=message)
            self.admin_key_entry.configure(border_color=COLORS['error'])
    
    def show_error(self, message: str):
        """Display error message"""
        self.error_label.configure(text=message)
    
    def clear_form(self):
        """Clear the login form"""
        self.admin_key_entry.delete(0, "end")
        self.totp_entry.delete(0, "end")
        self.error_label.configure(text="")
        self.admin_key_entry.configure(border_color=COLORS['border'])
