#!/usr/bin/env python3
"""
dLNk IDE - Register Window
AI-04 UI/UX Designer
Version: 1.0.0

Registration Window for new dLNk IDE users
"""

import customtkinter as ctk
import re

# Set appearance mode and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# dLNk Official Color Palette
COLORS = {
    # Primary Colors
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_tertiary': '#0f3460',
    
    # Accent Colors
    'accent_primary': '#e94560',
    'accent_secondary': '#533483',
    'accent_success': '#00d9ff',
    'accent_warning': '#ffc107',
    'accent_error': '#ff4757',
    
    # Text Colors
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'text_muted': '#6c757d',
    'text_link': '#00d9ff',
    
    # Border
    'border_color': '#2d2d44',
}

APP_NAME = "dLNk IDE"


class RegisterWindow(ctk.CTk):
    """
    dLNk IDE Registration Window
    Standalone registration form
    """
    
    def __init__(self, parent=None):
        super().__init__()
        
        self.parent = parent
        
        # Window Configuration
        self.title(f"{APP_NAME} - Register")
        self.geometry("480x700")
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
        width = 480
        height = 700
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self):
        """Create registration form widgets"""
        
        # ===== HEADER =====
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(35, 15))
        
        # Logo
        logo_label = ctk.CTkLabel(
            header_frame,
            text="dLNk",
            font=ctk.CTkFont(family="Segoe UI", size=42, weight="bold"),
            text_color=COLORS['accent_primary']
        )
        logo_label.pack()
        
        # Title
        title_label = ctk.CTkLabel(
            header_frame,
            text="Create Your Account",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(15, 5))
        
        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Join the AI-Powered Development Revolution",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.pack()
        
        # ===== FORM =====
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.pack(pady=20, padx=50, fill="x")
        
        # Email Field
        self.create_form_field(
            form_frame,
            "Email Address",
            "email",
            "your@email.com",
            "📧"
        )
        
        # Username Field
        self.create_form_field(
            form_frame,
            "Username",
            "username",
            "Choose a unique username",
            "👤"
        )
        
        # Password Field
        self.create_form_field(
            form_frame,
            "Password",
            "password",
            "Create a strong password",
            "🔒",
            show="•"
        )
        
        # Confirm Password Field
        self.create_form_field(
            form_frame,
            "Confirm Password",
            "confirm_password",
            "Confirm your password",
            "🔒",
            show="•"
        )
        
        # Telegram Username (Optional)
        self.create_form_field(
            form_frame,
            "Telegram Username (Optional)",
            "telegram",
            "@username",
            "📱"
        )
        
        # ===== TERMS =====
        terms_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        terms_frame.pack(fill="x", pady=(10, 20))
        
        self.terms_var = ctk.BooleanVar(value=False)
        terms_cb = ctk.CTkCheckBox(
            terms_frame,
            text="",
            variable=self.terms_var,
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['accent_primary'],
            hover_color=COLORS['accent_secondary'],
            border_color=COLORS['border_color'],
            width=24,
            height=24
        )
        terms_cb.pack(side="left")
        
        terms_text = ctk.CTkLabel(
            terms_frame,
            text="I agree to the ",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        terms_text.pack(side="left")
        
        terms_link = ctk.CTkButton(
            terms_frame,
            text="Terms of Service",
            font=ctk.CTkFont(size=12, underline=True),
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_link'],
            width=100,
            height=24,
            command=self.show_terms
        )
        terms_link.pack(side="left")
        
        # ===== STATUS MESSAGE =====
        self.status_label = ctk.CTkLabel(
            form_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['accent_error']
        )
        self.status_label.pack(pady=(0, 10))
        
        # ===== REGISTER BUTTON =====
        self.register_btn = ctk.CTkButton(
            form_frame,
            text="CREATE ACCOUNT",
            height=50,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=COLORS['accent_primary'],
            hover_color="#c73e54",
            text_color=COLORS['text_primary'],
            corner_radius=10,
            command=self.register
        )
        self.register_btn.pack(fill="x", pady=(0, 15))
        
        # ===== BACK TO LOGIN =====
        back_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        back_frame.pack()
        
        ctk.CTkLabel(
            back_frame,
            text="Already have an account?",
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_muted']
        ).pack(side="left")
        
        back_btn = ctk.CTkButton(
            back_frame,
            text="Login",
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['accent_success'],
            width=60,
            height=28,
            command=self.go_to_login
        )
        back_btn.pack(side="left", padx=(5, 0))
    
    def create_form_field(self, parent, label_text, field_name, placeholder, icon="", show=""):
        """Create a form field with label and entry"""
        
        # Label
        label = ctk.CTkLabel(
            parent,
            text=f"{icon} {label_text}" if icon else label_text,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_secondary']
        )
        label.pack(anchor="w", pady=(0, 5))
        
        # Entry
        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=45,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_secondary'],
            border_color=COLORS['border_color'],
            border_width=2,
            corner_radius=10,
            text_color=COLORS['text_primary'],
            placeholder_text_color=COLORS['text_muted']
        )
        
        if show:
            entry.configure(show=show)
        
        entry.pack(fill="x", pady=(0, 12))
        
        # Store reference
        setattr(self, f"{field_name}_entry", entry)
        
        # Focus effects
        entry.bind("<FocusIn>", lambda e, ent=entry: ent.configure(border_color=COLORS['accent_primary']))
        entry.bind("<FocusOut>", lambda e, ent=entry: ent.configure(border_color=COLORS['border_color']))
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_password(self, password: str) -> tuple:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain uppercase letter"
        if not re.search(r'[a-z]', password):
            return False, "Password must contain lowercase letter"
        if not re.search(r'[0-9]', password):
            return False, "Password must contain a number"
        return True, "Password is strong"
    
    def show_status(self, message: str, is_error: bool = True):
        """Show status message"""
        color = COLORS['accent_error'] if is_error else COLORS['accent_success']
        self.status_label.configure(text=message, text_color=color)
    
    def register(self):
        """Handle registration"""
        # Get values
        email = self.email_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        telegram = self.telegram_entry.get().strip()
        
        # Validate email
        if not email:
            self.show_status("Email is required")
            self.email_entry.focus()
            return
        
        if not self.validate_email(email):
            self.show_status("Invalid email format")
            self.email_entry.focus()
            return
        
        # Validate username
        if not username:
            self.show_status("Username is required")
            self.username_entry.focus()
            return
        
        if len(username) < 3:
            self.show_status("Username must be at least 3 characters")
            self.username_entry.focus()
            return
        
        # Validate password
        if not password:
            self.show_status("Password is required")
            self.password_entry.focus()
            return
        
        valid, msg = self.validate_password(password)
        if not valid:
            self.show_status(msg)
            self.password_entry.focus()
            return
        
        # Confirm password
        if password != confirm_password:
            self.show_status("Passwords do not match")
            self.confirm_password_entry.focus()
            return
        
        # Terms
        if not self.terms_var.get():
            self.show_status("Please accept the Terms of Service")
            return
        
        # All validations passed
        self.register_btn.configure(state="disabled", text="Creating account...")
        self.show_status("Creating your account...", is_error=False)
        
        # Simulate registration (replace with actual API call)
        self.after(2000, self.registration_complete)
    
    def registration_complete(self):
        """Handle registration completion"""
        self.register_btn.configure(state="normal", text="CREATE ACCOUNT")
        self.show_status("Account created successfully! Check your email.", is_error=False)
        
        # Go back to login after delay
        self.after(2000, self.go_to_login)
    
    def show_terms(self):
        """Show terms of service"""
        # Implement terms dialog
        print("Showing Terms of Service...")
    
    def go_to_login(self):
        """Go back to login window"""
        if self.parent:
            self.parent.deiconify()
        self.destroy()
    
    def on_close(self):
        """Handle window close"""
        self.go_to_login()


if __name__ == "__main__":
    app = RegisterWindow()
    app.mainloop()
