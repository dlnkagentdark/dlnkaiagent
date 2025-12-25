#!/usr/bin/env python3
"""
dLNk Admin Console
ระบบจัดการ Admin สำหรับ dLNk IDE
รองรับทั้ง GUI และ Web Interface
"""

import os
import sys
import json
import threading
import datetime
from pathlib import Path

# Check if running in headless mode
HEADLESS = '--web' in sys.argv or os.environ.get('DISPLAY') is None

# GUI imports (only if not headless)
ctk = None
Image = None

if not HEADLESS:
    try:
        import customtkinter as ctk
        from PIL import Image
    except ImportError:
        print("[!] GUI not available. Use --web for web interface.")
        HEADLESS = True

# Web imports
try:
    from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
    from flask_cors import CORS
except ImportError:
    os.system("pip3 install flask flask-cors -q")
    from flask import Flask, render_template_string, request, jsonify, redirect, url_for, session
    from flask_cors import CORS

# Import license system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dlnk_license_system import DLNKLicenseSystem, LicenseType, LicenseStatus

# Configuration
CONFIG_DIR = Path.home() / ".dlnk-ide"
LICENSE_DB = CONFIG_DIR / "licenses.db"

# Colors
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


# ==================== GUI ADMIN CONSOLE ====================

# Only define GUI class if not headless
AdminConsoleGUI = None

if not HEADLESS and ctk is not None:
    class AdminConsoleGUI(ctk.CTk):
        """
        Admin Console GUI
        หน้าต่างจัดการ Admin แบบ Desktop
        """
        
        def __init__(self):
        super().__init__()
        
        # Initialize
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self.license_system = DLNKLicenseSystem(str(LICENSE_DB))
        self.current_user = None
        
        # Window setup
        self.title("dLNk Admin Console")
        self.geometry("1000x700")
        self.configure(fg_color=COLORS["bg_dark"])
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Show login first
        self.show_login()
        
    def show_login(self):
        """Show login screen"""
        self.login_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        self.login_frame.pack(fill="both", expand=True)
        
        # Center container
        center_frame = ctk.CTkFrame(self.login_frame, fg_color=COLORS["bg_card"], corner_radius=15)
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title
        title = ctk.CTkLabel(
            center_frame,
            text="🔐 Admin Login",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["accent"]
        )
        title.pack(pady=(30, 20))
        
        # Username
        self.username_entry = ctk.CTkEntry(
            center_frame,
            placeholder_text="Username",
            width=250,
            height=40,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"]
        )
        self.username_entry.pack(pady=10, padx=30)
        
        # Password
        self.password_entry = ctk.CTkEntry(
            center_frame,
            placeholder_text="Password",
            show="•",
            width=250,
            height=40,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"]
        )
        self.password_entry.pack(pady=10, padx=30)
        
        # Status
        self.login_status = ctk.CTkLabel(
            center_frame,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["error"]
        )
        self.login_status.pack(pady=5)
        
        # Login button
        login_btn = ctk.CTkButton(
            center_frame,
            text="Login",
            width=250,
            height=40,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_dark"],
            command=self.do_login
        )
        login_btn.pack(pady=(10, 30))
        
        # Default credentials hint
        hint = ctk.CTkLabel(
            center_frame,
            text="Default: admin / admin123",
            font=ctk.CTkFont(size=10),
            text_color=COLORS["text_secondary"]
        )
        hint.pack(pady=(0, 20))
        
    def do_login(self):
        """Perform login"""
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        success, user = self.license_system.authenticate_user(username, password)
        
        if success and user.role in ["admin", "superadmin"]:
            self.current_user = user
            self.login_frame.destroy()
            self.show_dashboard()
        else:
            self.login_status.configure(text="Invalid credentials or insufficient permissions")
            
    def show_dashboard(self):
        """Show main dashboard"""
        # Main container
        self.main_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        self.main_frame.pack(fill="both", expand=True)
        
        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self.main_frame,
            width=200,
            fg_color=COLORS["bg_secondary"],
            corner_radius=0
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        # Sidebar title
        sidebar_title = ctk.CTkLabel(
            self.sidebar,
            text="dLNk Admin",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=COLORS["accent"]
        )
        sidebar_title.pack(pady=20)
        
        # Sidebar buttons
        self.sidebar_buttons = {}
        menu_items = [
            ("📊 Dashboard", self.show_stats_panel),
            ("🔑 Licenses", self.show_licenses_panel),
            ("👥 Users", self.show_users_panel),
            ("➕ Create License", self.show_create_license_panel),
            ("📝 Activity Log", self.show_activity_panel),
            ("⚙️ Settings", self.show_settings_panel),
        ]
        
        for text, command in menu_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                font=ctk.CTkFont(size=13),
                fg_color="transparent",
                hover_color=COLORS["bg_card"],
                text_color=COLORS["text_primary"],
                anchor="w",
                height=40,
                command=command
            )
            btn.pack(fill="x", padx=10, pady=2)
            self.sidebar_buttons[text] = btn
            
        # Logout button at bottom
        logout_btn = ctk.CTkButton(
            self.sidebar,
            text="🚪 Logout",
            font=ctk.CTkFont(size=12),
            fg_color="transparent",
            hover_color=COLORS["error"],
            text_color=COLORS["text_secondary"],
            height=35,
            command=self.logout
        )
        logout_btn.pack(side="bottom", fill="x", padx=10, pady=20)
        
        # Content area
        self.content_frame = ctk.CTkFrame(
            self.main_frame,
            fg_color=COLORS["bg_dark"]
        )
        self.content_frame.pack(side="right", fill="both", expand=True, padx=20, pady=20)
        
        # Show dashboard by default
        self.show_stats_panel()
        
    def clear_content(self):
        """Clear content area"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
            
    def show_stats_panel(self):
        """Show statistics panel"""
        self.clear_content()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Get stats
        stats = self.license_system.get_license_stats()
        
        # Stats cards
        cards_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)
        
        stat_items = [
            ("Total Licenses", stats["total_licenses"], COLORS["accent"]),
            ("Active", stats["active_licenses"], COLORS["success"]),
            ("Expired", stats["expired_licenses"], COLORS["warning"]),
            ("Revoked", stats["revoked_licenses"], COLORS["error"]),
            ("Total Users", stats["total_users"], COLORS["accent"]),
            ("Activations", stats["total_activations"], COLORS["accent"]),
        ]
        
        for i, (label, value, color) in enumerate(stat_items):
            card = ctk.CTkFrame(cards_frame, fg_color=COLORS["bg_card"], corner_radius=10)
            card.grid(row=i//3, column=i%3, padx=10, pady=10, sticky="nsew")
            
            value_label = ctk.CTkLabel(
                card,
                text=str(value),
                font=ctk.CTkFont(size=32, weight="bold"),
                text_color=color
            )
            value_label.pack(pady=(15, 5))
            
            name_label = ctk.CTkLabel(
                card,
                text=label,
                font=ctk.CTkFont(size=12),
                text_color=COLORS["text_secondary"]
            )
            name_label.pack(pady=(0, 15))
            
        for i in range(3):
            cards_frame.columnconfigure(i, weight=1)
            
        # Recent activity
        activity_title = ctk.CTkLabel(
            self.content_frame,
            text="Recent Activity",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        activity_title.pack(anchor="w", pady=(20, 10))
        
        activity_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["bg_card"],
            height=200
        )
        activity_frame.pack(fill="x")
        
        for activity in stats.get("recent_activity", []):
            row = ctk.CTkFrame(activity_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            action_label = ctk.CTkLabel(
                row,
                text=f"• {activity['action']}: {activity['details']}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_primary"],
                anchor="w"
            )
            action_label.pack(side="left", padx=10)
            
            time_label = ctk.CTkLabel(
                row,
                text=activity['timestamp'][:19],
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"]
            )
            time_label.pack(side="right", padx=10)
            
    def show_licenses_panel(self):
        """Show licenses panel"""
        self.clear_content()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="🔑 License Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Licenses list
        licenses_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["bg_card"]
        )
        licenses_frame.pack(fill="both", expand=True)
        
        # Header
        header = ctk.CTkFrame(licenses_frame, fg_color=COLORS["bg_secondary"])
        header.pack(fill="x", pady=(0, 5))
        
        headers = ["Key", "Type", "Status", "Expires", "Actions"]
        widths = [200, 80, 80, 150, 150]
        
        for h, w in zip(headers, widths):
            lbl = ctk.CTkLabel(
                header,
                text=h,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["text_secondary"],
                width=w
            )
            lbl.pack(side="left", padx=5, pady=5)
            
        # License rows
        licenses = self.license_system.get_all_licenses()
        
        for lic in licenses:
            row = ctk.CTkFrame(licenses_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            
            # Key
            key_label = ctk.CTkLabel(
                row,
                text=lic.key,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_primary"],
                width=200
            )
            key_label.pack(side="left", padx=5)
            
            # Type
            type_label = ctk.CTkLabel(
                row,
                text=lic.license_type.value,
                font=ctk.CTkFont(size=11),
                text_color=COLORS["accent"],
                width=80
            )
            type_label.pack(side="left", padx=5)
            
            # Status
            status_color = COLORS["success"] if lic.status == LicenseStatus.ACTIVE else COLORS["error"]
            status_label = ctk.CTkLabel(
                row,
                text=lic.status.value,
                font=ctk.CTkFont(size=11),
                text_color=status_color,
                width=80
            )
            status_label.pack(side="left", padx=5)
            
            # Expires
            expires_label = ctk.CTkLabel(
                row,
                text=lic.expires_at[:10],
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"],
                width=150
            )
            expires_label.pack(side="left", padx=5)
            
            # Actions
            actions_frame = ctk.CTkFrame(row, fg_color="transparent", width=150)
            actions_frame.pack(side="left", padx=5)
            
            extend_btn = ctk.CTkButton(
                actions_frame,
                text="+30d",
                width=50,
                height=25,
                font=ctk.CTkFont(size=10),
                fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"],
                text_color=COLORS["bg_dark"],
                command=lambda k=lic.key: self.extend_license(k)
            )
            extend_btn.pack(side="left", padx=2)
            
            if lic.status == LicenseStatus.ACTIVE:
                revoke_btn = ctk.CTkButton(
                    actions_frame,
                    text="Revoke",
                    width=60,
                    height=25,
                    font=ctk.CTkFont(size=10),
                    fg_color=COLORS["error"],
                    hover_color="#cc3333",
                    command=lambda k=lic.key: self.revoke_license(k)
                )
                revoke_btn.pack(side="left", padx=2)
                
    def show_users_panel(self):
        """Show users panel"""
        self.clear_content()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="👥 User Management",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Create user button
        create_btn = ctk.CTkButton(
            self.content_frame,
            text="+ Create User",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_dark"],
            command=self.show_create_user_dialog
        )
        create_btn.pack(anchor="w", pady=(0, 10))
        
        # Users list
        users_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["bg_card"]
        )
        users_frame.pack(fill="both", expand=True)
        
        users = self.license_system.get_all_users()
        
        for user in users:
            row = ctk.CTkFrame(users_frame, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=10)
            
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(side="left")
            
            name_label = ctk.CTkLabel(
                info_frame,
                text=user.username,
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=COLORS["text_primary"]
            )
            name_label.pack(anchor="w")
            
            details_label = ctk.CTkLabel(
                info_frame,
                text=f"{user.email or 'No email'} | Role: {user.role}",
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_secondary"]
            )
            details_label.pack(anchor="w")
            
    def show_create_license_panel(self):
        """Show create license panel"""
        self.clear_content()
        
        # Title
        title = ctk.CTkLabel(
            self.content_frame,
            text="➕ Create New License",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Form
        form_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        form_frame.pack(fill="x", pady=10)
        
        # Owner name
        owner_label = ctk.CTkLabel(form_frame, text="Owner Name:", text_color=COLORS["text_primary"])
        owner_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.owner_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="Enter owner name",
            width=300,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"]
        )
        self.owner_entry.pack(anchor="w", padx=20)
        
        # License type
        type_label = ctk.CTkLabel(form_frame, text="License Type:", text_color=COLORS["text_primary"])
        type_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.type_var = ctk.StringVar(value="basic")
        type_menu = ctk.CTkOptionMenu(
            form_frame,
            values=["trial", "basic", "pro", "enterprise", "admin"],
            variable=self.type_var,
            fg_color=COLORS["bg_secondary"],
            button_color=COLORS["accent"],
            button_hover_color=COLORS["accent_hover"]
        )
        type_menu.pack(anchor="w", padx=20)
        
        # Duration
        duration_label = ctk.CTkLabel(form_frame, text="Duration (days):", text_color=COLORS["text_primary"])
        duration_label.pack(anchor="w", padx=20, pady=(15, 5))
        
        self.duration_entry = ctk.CTkEntry(
            form_frame,
            placeholder_text="30",
            width=100,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"]
        )
        self.duration_entry.insert(0, "30")
        self.duration_entry.pack(anchor="w", padx=20)
        
        # Create button
        create_btn = ctk.CTkButton(
            form_frame,
            text="Create License",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_dark"],
            command=self.create_license
        )
        create_btn.pack(anchor="w", padx=20, pady=20)
        
        # Result area
        self.result_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        self.result_frame.pack(fill="x", pady=10)
        
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_primary"],
            wraplength=500
        )
        self.result_label.pack(pady=20, padx=20)
        
    def create_license(self):
        """Create new license"""
        owner = self.owner_entry.get() or "User"
        license_type = LicenseType(self.type_var.get())
        duration = int(self.duration_entry.get() or 30)
        
        try:
            license_obj = self.license_system.create_license(
                user_id=self.current_user.user_id,
                license_type=license_type,
                duration_days=duration,
                owner_name=owner
            )
            
            result_text = f"""
✅ License Created Successfully!

Key: {license_obj.key}
Type: {license_obj.license_type.value}
Expires: {license_obj.expires_at[:10]}
Features: {', '.join(license_obj.features)}

Encrypted Key (for distribution):
{license_obj.encrypted_key[:50]}...
            """
            
            self.result_label.configure(text=result_text, text_color=COLORS["success"])
            
        except Exception as e:
            self.result_label.configure(text=f"Error: {str(e)}", text_color=COLORS["error"])
            
    def show_activity_panel(self):
        """Show activity log panel"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="📝 Activity Log",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Activity list
        stats = self.license_system.get_license_stats()
        
        activity_frame = ctk.CTkScrollableFrame(
            self.content_frame,
            fg_color=COLORS["bg_card"]
        )
        activity_frame.pack(fill="both", expand=True)
        
        for activity in stats.get("recent_activity", []):
            row = ctk.CTkFrame(activity_frame, fg_color="transparent")
            row.pack(fill="x", pady=5, padx=10)
            
            time_label = ctk.CTkLabel(
                row,
                text=activity['timestamp'][:19],
                font=ctk.CTkFont(size=10),
                text_color=COLORS["text_secondary"],
                width=150
            )
            time_label.pack(side="left")
            
            action_label = ctk.CTkLabel(
                row,
                text=activity['action'],
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color=COLORS["accent"],
                width=150
            )
            action_label.pack(side="left")
            
            details_label = ctk.CTkLabel(
                row,
                text=activity['details'],
                font=ctk.CTkFont(size=11),
                text_color=COLORS["text_primary"]
            )
            details_label.pack(side="left", padx=10)
            
    def show_settings_panel(self):
        """Show settings panel"""
        self.clear_content()
        
        title = ctk.CTkLabel(
            self.content_frame,
            text="⚙️ Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS["text_primary"]
        )
        title.pack(anchor="w", pady=(0, 20))
        
        # Settings options
        settings_frame = ctk.CTkFrame(self.content_frame, fg_color=COLORS["bg_card"], corner_radius=10)
        settings_frame.pack(fill="x", pady=10)
        
        # Web server toggle
        self.web_server_var = ctk.BooleanVar(value=False)
        web_check = ctk.CTkCheckBox(
            settings_frame,
            text="Enable Web Admin Interface (Port 5001)",
            variable=self.web_server_var,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            command=self.toggle_web_server
        )
        web_check.pack(anchor="w", padx=20, pady=15)
        
        # Telegram bot toggle
        self.telegram_var = ctk.BooleanVar(value=False)
        telegram_check = ctk.CTkCheckBox(
            settings_frame,
            text="Enable Telegram Bot",
            variable=self.telegram_var,
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"]
        )
        telegram_check.pack(anchor="w", padx=20, pady=15)
        
        # Database info
        db_label = ctk.CTkLabel(
            settings_frame,
            text=f"Database: {LICENSE_DB}",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_secondary"]
        )
        db_label.pack(anchor="w", padx=20, pady=(15, 20))
        
    def show_create_user_dialog(self):
        """Show create user dialog"""
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create User")
        dialog.geometry("350x300")
        dialog.configure(fg_color=COLORS["bg_dark"])
        
        # Username
        username_label = ctk.CTkLabel(dialog, text="Username:", text_color=COLORS["text_primary"])
        username_label.pack(pady=(20, 5))
        
        username_entry = ctk.CTkEntry(
            dialog,
            width=250,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"]
        )
        username_entry.pack()
        
        # Email
        email_label = ctk.CTkLabel(dialog, text="Email:", text_color=COLORS["text_primary"])
        email_label.pack(pady=(10, 5))
        
        email_entry = ctk.CTkEntry(
            dialog,
            width=250,
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"]
        )
        email_entry.pack()
        
        # Password
        password_label = ctk.CTkLabel(dialog, text="Password:", text_color=COLORS["text_primary"])
        password_label.pack(pady=(10, 5))
        
        password_entry = ctk.CTkEntry(
            dialog,
            width=250,
            show="•",
            fg_color=COLORS["bg_secondary"],
            border_color=COLORS["border"]
        )
        password_entry.pack()
        
        # Role
        role_label = ctk.CTkLabel(dialog, text="Role:", text_color=COLORS["text_primary"])
        role_label.pack(pady=(10, 5))
        
        role_var = ctk.StringVar(value="user")
        role_menu = ctk.CTkOptionMenu(
            dialog,
            values=["user", "admin"],
            variable=role_var,
            fg_color=COLORS["bg_secondary"]
        )
        role_menu.pack()
        
        def create():
            try:
                self.license_system.create_user(
                    username=username_entry.get(),
                    email=email_entry.get(),
                    password=password_entry.get(),
                    role=role_var.get()
                )
                dialog.destroy()
                self.show_users_panel()
            except Exception as e:
                error_label = ctk.CTkLabel(dialog, text=str(e), text_color=COLORS["error"])
                error_label.pack()
                
        create_btn = ctk.CTkButton(
            dialog,
            text="Create",
            fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"],
            text_color=COLORS["bg_dark"],
            command=create
        )
        create_btn.pack(pady=20)
        
    def extend_license(self, key: str):
        """Extend license by 30 days"""
        self.license_system.extend_license(key, 30)
        self.show_licenses_panel()
        
    def revoke_license(self, key: str):
        """Revoke license"""
        self.license_system.revoke_license(key)
        self.show_licenses_panel()
        
    def toggle_web_server(self):
        """Toggle web server"""
        if self.web_server_var.get():
            threading.Thread(target=start_web_server, daemon=True).start()
            
    def logout(self):
        """Logout and show login screen"""
        self.current_user = None
        self.main_frame.destroy()
        self.show_login()


# ==================== WEB ADMIN INTERFACE ====================

app = Flask(__name__)
app.secret_key = "dlnk-admin-secret-key-2025"
CORS(app)

license_system = None

WEB_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>dLNk Admin Console</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', sans-serif; 
            background: #0d0d0d; 
            color: #fff; 
            min-height: 100vh;
        }
        .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
        .header { 
            background: #1a1a1a; 
            padding: 20px; 
            margin-bottom: 20px;
            border-radius: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { color: #00ff88; }
        .card { 
            background: #242424; 
            border-radius: 10px; 
            padding: 20px; 
            margin-bottom: 20px;
        }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 15px; 
        }
        .stat-card { 
            background: #1a1a1a; 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
        }
        .stat-value { font-size: 2em; color: #00ff88; font-weight: bold; }
        .stat-label { color: #888; font-size: 0.9em; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #333; }
        th { color: #888; font-weight: normal; }
        .btn { 
            background: #00ff88; 
            color: #000; 
            border: none; 
            padding: 8px 16px; 
            border-radius: 5px; 
            cursor: pointer;
            font-weight: bold;
        }
        .btn:hover { background: #00cc6a; }
        .btn-danger { background: #ff4444; color: #fff; }
        .btn-danger:hover { background: #cc3333; }
        .status-active { color: #00ff88; }
        .status-expired { color: #ffcc00; }
        .status-revoked { color: #ff4444; }
        input, select { 
            background: #1a1a1a; 
            border: 1px solid #333; 
            color: #fff; 
            padding: 10px; 
            border-radius: 5px;
            width: 100%;
            margin-bottom: 10px;
        }
        .form-group { margin-bottom: 15px; }
        label { display: block; margin-bottom: 5px; color: #888; }
        .nav { display: flex; gap: 10px; margin-bottom: 20px; }
        .nav a { 
            color: #888; 
            text-decoration: none; 
            padding: 10px 20px;
            border-radius: 5px;
        }
        .nav a:hover, .nav a.active { background: #242424; color: #00ff88; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 dLNk Admin Console</h1>
            <span>{{ user }}</span>
        </div>
        
        <div class="nav">
            <a href="/" class="{{ 'active' if page == 'dashboard' else '' }}">Dashboard</a>
            <a href="/licenses" class="{{ 'active' if page == 'licenses' else '' }}">Licenses</a>
            <a href="/create" class="{{ 'active' if page == 'create' else '' }}">Create License</a>
        </div>
        
        {% block content %}{% endblock %}
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
{% extends "base" %}
{% block content %}
<div class="stats-grid">
    <div class="stat-card">
        <div class="stat-value">{{ stats.total_licenses }}</div>
        <div class="stat-label">Total Licenses</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{{ stats.active_licenses }}</div>
        <div class="stat-label">Active</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{{ stats.expired_licenses }}</div>
        <div class="stat-label">Expired</div>
    </div>
    <div class="stat-card">
        <div class="stat-value">{{ stats.total_users }}</div>
        <div class="stat-label">Users</div>
    </div>
</div>

<div class="card">
    <h3>Recent Activity</h3>
    <table>
        <tr><th>Time</th><th>Action</th><th>Details</th></tr>
        {% for activity in stats.recent_activity %}
        <tr>
            <td>{{ activity.timestamp[:19] }}</td>
            <td>{{ activity.action }}</td>
            <td>{{ activity.details }}</td>
        </tr>
        {% endfor %}
    </table>
</div>
{% endblock %}
"""


@app.route('/')
def dashboard():
    global license_system
    if license_system is None:
        license_system = DLNKLicenseSystem(str(LICENSE_DB))
    
    stats = license_system.get_license_stats()
    
    html = WEB_TEMPLATE.replace("{% block content %}{% endblock %}", DASHBOARD_TEMPLATE)
    return render_template_string(html, stats=stats, page="dashboard", user="Admin")


@app.route('/licenses')
def licenses():
    global license_system
    if license_system is None:
        license_system = DLNKLicenseSystem(str(LICENSE_DB))
        
    all_licenses = license_system.get_all_licenses()
    
    licenses_html = """
    <div class="card">
        <h3>All Licenses</h3>
        <table>
            <tr><th>Key</th><th>Type</th><th>Status</th><th>Expires</th><th>Actions</th></tr>
            {% for lic in licenses %}
            <tr>
                <td>{{ lic.key }}</td>
                <td>{{ lic.license_type.value }}</td>
                <td class="status-{{ lic.status.value }}">{{ lic.status.value }}</td>
                <td>{{ lic.expires_at[:10] }}</td>
                <td>
                    <a href="/extend/{{ lic.key }}" class="btn">+30d</a>
                    {% if lic.status.value == 'active' %}
                    <a href="/revoke/{{ lic.key }}" class="btn btn-danger">Revoke</a>
                    {% endif %}
                </td>
            </tr>
            {% endfor %}
        </table>
    </div>
    """
    
    html = WEB_TEMPLATE.replace("{% block content %}{% endblock %}", licenses_html)
    return render_template_string(html, licenses=all_licenses, page="licenses", user="Admin")


@app.route('/create', methods=['GET', 'POST'])
def create():
    global license_system
    if license_system is None:
        license_system = DLNKLicenseSystem(str(LICENSE_DB))
        
    result = None
    
    if request.method == 'POST':
        owner = request.form.get('owner', 'User')
        license_type = LicenseType(request.form.get('type', 'basic'))
        duration = int(request.form.get('duration', 30))
        
        license_obj = license_system.create_license(
            user_id="admin",
            license_type=license_type,
            duration_days=duration,
            owner_name=owner
        )
        
        result = {
            "key": license_obj.key,
            "type": license_obj.license_type.value,
            "expires": license_obj.expires_at[:10],
            "encrypted": license_obj.encrypted_key
        }
    
    create_html = """
    <div class="card">
        <h3>Create New License</h3>
        <form method="POST">
            <div class="form-group">
                <label>Owner Name</label>
                <input type="text" name="owner" placeholder="Enter owner name">
            </div>
            <div class="form-group">
                <label>License Type</label>
                <select name="type">
                    <option value="trial">Trial</option>
                    <option value="basic" selected>Basic</option>
                    <option value="pro">Pro</option>
                    <option value="enterprise">Enterprise</option>
                    <option value="admin">Admin</option>
                </select>
            </div>
            <div class="form-group">
                <label>Duration (days)</label>
                <input type="number" name="duration" value="30">
            </div>
            <button type="submit" class="btn">Create License</button>
        </form>
        
        {% if result %}
        <div style="margin-top: 20px; padding: 15px; background: #1a1a1a; border-radius: 5px;">
            <h4 style="color: #00ff88;">✅ License Created!</h4>
            <p><strong>Key:</strong> {{ result.key }}</p>
            <p><strong>Type:</strong> {{ result.type }}</p>
            <p><strong>Expires:</strong> {{ result.expires }}</p>
            <p><strong>Encrypted Key:</strong></p>
            <textarea style="width: 100%; height: 100px; background: #0d0d0d; border: 1px solid #333; color: #fff; padding: 10px;">{{ result.encrypted }}</textarea>
        </div>
        {% endif %}
    </div>
    """
    
    html = WEB_TEMPLATE.replace("{% block content %}{% endblock %}", create_html)
    return render_template_string(html, result=result, page="create", user="Admin")


@app.route('/extend/<key>')
def extend(key):
    global license_system
    if license_system is None:
        license_system = DLNKLicenseSystem(str(LICENSE_DB))
    license_system.extend_license(key, 30)
    return redirect('/licenses')


@app.route('/revoke/<key>')
def revoke(key):
    global license_system
    if license_system is None:
        license_system = DLNKLicenseSystem(str(LICENSE_DB))
    license_system.revoke_license(key)
    return redirect('/licenses')


@app.route('/api/verify', methods=['POST'])
def api_verify():
    global license_system
    if license_system is None:
        license_system = DLNKLicenseSystem(str(LICENSE_DB))
        
    data = request.json
    key = data.get('key', '')
    hwid = data.get('hwid', '')
    
    valid, message, license_obj = license_system.verify_license(key, hwid)
    
    if valid:
        return jsonify({
            "valid": True,
            "message": message,
            "features": license_obj.features if license_obj else []
        })
    else:
        return jsonify({
            "valid": False,
            "message": message
        }), 401


def start_web_server(port=5001):
    """Start web server"""
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk Admin Console')
    parser.add_argument('--web', action='store_true', help='Start web server only')
    parser.add_argument('--port', type=int, default=5001, help='Web server port')
    
    args = parser.parse_args()
    
    if args.web or HEADLESS:
        print(f"Starting web admin console on http://0.0.0.0:{args.port}")
        start_web_server(args.port)
    else:
        if ctk is not None:
            gui_app = AdminConsoleGUI()
            gui_app.mainloop()
        else:
            print("GUI not available. Starting web server instead...")
            start_web_server(args.port)


if __name__ == "__main__":
    main()
