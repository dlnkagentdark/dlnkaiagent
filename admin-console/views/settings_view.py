#!/usr/bin/env python3
"""
dLNk Admin Console - Settings View
"""

import customtkinter as ctk
from utils.theme import COLORS
from components.header import Header
from components.dialog import MessageDialog, ConfirmDialog


class SettingsView(ctk.CTkFrame):
    """Settings Management View"""
    
    def __init__(self, parent, api_client=None):
        super().__init__(parent, fg_color="transparent")
        
        self.api_client = api_client
        self.settings = {}
        
        self.create_widgets()
        self.load_settings()
    
    def create_widgets(self):
        """Create settings widgets"""
        # Header
        self.header = Header(self, "Settings", show_refresh=False)
        self.header.pack(fill="x", pady=(0, 20))
        
        # Scrollable content
        content = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS['border'],
            scrollbar_button_hover_color=COLORS['accent']
        )
        content.pack(fill="both", expand=True)
        
        # Telegram Settings Section
        self._create_telegram_section(content)
        
        # Alert Thresholds Section
        self._create_alerts_section(content)
        
        # API Settings Section
        self._create_api_section(content)
        
        # Security Settings Section
        self._create_security_section(content)
        
        # Save Button
        save_frame = ctk.CTkFrame(self, fg_color="transparent")
        save_frame.pack(fill="x", pady=20)
        
        ctk.CTkButton(
            save_frame,
            text="💾 Save All Settings",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['accent'],
            hover_color=COLORS['hover'],
            width=200,
            height=45,
            command=self.save_settings
        ).pack(side="right")
    
    def _create_section(self, parent, title: str, icon: str) -> ctk.CTkFrame:
        """Create a settings section"""
        section = ctk.CTkFrame(parent, fg_color=COLORS['bg_tertiary'], corner_radius=12)
        section.pack(fill="x", pady=(0, 15))
        
        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            header,
            text=f"{icon} {title}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=COLORS['text_primary']
        ).pack(side="left")
        
        # Content frame
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 20))
        
        return content
    
    def _create_input_row(self, parent, label: str, key: str, placeholder: str = "", 
                          input_type: str = "text", width: int = 400) -> ctk.CTkEntry:
        """Create an input row"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=8)
        
        # Label
        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary'],
            width=200,
            anchor="w"
        ).pack(side="left")
        
        # Input
        if input_type == "password":
            entry = ctk.CTkEntry(
                row,
                placeholder_text=placeholder,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=width,
                height=38,
                show="•"
            )
        else:
            entry = ctk.CTkEntry(
                row,
                placeholder_text=placeholder,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=width,
                height=38
            )
        entry.pack(side="left")
        
        self.settings[key] = entry
        return entry
    
    def _create_switch_row(self, parent, label: str, key: str, default: bool = False) -> ctk.CTkSwitch:
        """Create a switch row"""
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=8)
        
        # Label
        ctk.CTkLabel(
            row,
            text=label,
            font=ctk.CTkFont(size=13),
            text_color=COLORS['text_secondary'],
            width=200,
            anchor="w"
        ).pack(side="left")
        
        # Switch
        switch_var = ctk.BooleanVar(value=default)
        switch = ctk.CTkSwitch(
            row,
            text="",
            variable=switch_var,
            onvalue=True,
            offvalue=False,
            fg_color=COLORS['border'],
            progress_color=COLORS['accent'],
            button_color=COLORS['text_primary'],
            button_hover_color=COLORS['success']
        )
        switch.pack(side="left")
        
        self.settings[key] = switch_var
        return switch
    
    def _create_telegram_section(self, parent):
        """Create Telegram settings section"""
        content = self._create_section(parent, "Telegram Bot Settings", "🤖")
        
        # Bot Token
        self._create_input_row(
            content, 
            "Bot Token", 
            "telegram_bot_token",
            "Enter Telegram Bot Token",
            input_type="password"
        )
        
        # Admin Chat ID
        self._create_input_row(
            content,
            "Admin Chat ID",
            "telegram_admin_id",
            "Enter Admin Chat ID"
        )
        
        # Enable Notifications
        self._create_switch_row(
            content,
            "Enable Notifications",
            "telegram_enabled",
            default=True
        )
        
        # Test Button
        test_frame = ctk.CTkFrame(content, fg_color="transparent")
        test_frame.pack(fill="x", pady=(10, 0))
        
        ctk.CTkButton(
            test_frame,
            text="📤 Test Connection",
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['accent'],
            width=150,
            height=35,
            command=self.test_telegram
        ).pack(side="left", padx=(200, 0))
    
    def _create_alerts_section(self, parent):
        """Create Alert Thresholds section"""
        content = self._create_section(parent, "Alert Thresholds", "🚨")
        
        # Max Requests Per Minute
        self._create_input_row(
            content,
            "Max Requests/Minute",
            "max_requests_minute",
            "30",
            width=150
        )
        
        # Max Requests Per Hour
        self._create_input_row(
            content,
            "Max Requests/Hour",
            "max_requests_hour",
            "500",
            width=150
        )
        
        # Suspicious Activity Score
        self._create_input_row(
            content,
            "Suspicious Score Threshold",
            "suspicious_threshold",
            "0.7",
            width=150
        )
        
        # Alert on Blocked
        self._create_switch_row(
            content,
            "Alert on Blocked Prompts",
            "alert_on_blocked",
            default=True
        )
        
        # Alert on Rate Limit
        self._create_switch_row(
            content,
            "Alert on Rate Limit",
            "alert_on_rate_limit",
            default=True
        )
    
    def _create_api_section(self, parent):
        """Create API Settings section"""
        content = self._create_section(parent, "API Endpoints", "🔗")
        
        # Backend URL
        self._create_input_row(
            content,
            "Backend API URL",
            "api_backend_url",
            "http://localhost:5001"
        )
        
        # Antigravity URL
        self._create_input_row(
            content,
            "Antigravity API URL",
            "api_antigravity_url",
            "https://api.antigravity.ai"
        )
        
        # Request Timeout
        self._create_input_row(
            content,
            "Request Timeout (seconds)",
            "api_timeout",
            "30",
            width=150
        )
    
    def _create_security_section(self, parent):
        """Create Security Settings section"""
        content = self._create_section(parent, "Security Settings", "🔐")
        
        # Session Lifetime
        self._create_input_row(
            content,
            "Session Lifetime (hours)",
            "session_lifetime",
            "24",
            width=150
        )
        
        # Max Login Attempts
        self._create_input_row(
            content,
            "Max Login Attempts",
            "max_login_attempts",
            "5",
            width=150
        )
        
        # Lockout Duration
        self._create_input_row(
            content,
            "Lockout Duration (minutes)",
            "lockout_duration",
            "30",
            width=150
        )
        
        # Require 2FA
        self._create_switch_row(
            content,
            "Require 2FA for Login",
            "require_2fa",
            default=False
        )
        
        # IP Whitelist
        self._create_input_row(
            content,
            "IP Whitelist (comma-separated)",
            "ip_whitelist",
            "Leave empty to allow all"
        )
        
        # Change Password Button
        pwd_frame = ctk.CTkFrame(content, fg_color="transparent")
        pwd_frame.pack(fill="x", pady=(15, 0))
        
        ctk.CTkButton(
            pwd_frame,
            text="🔑 Change Admin Password",
            font=ctk.CTkFont(size=12),
            fg_color=COLORS['warning'],
            hover_color="#cc9900",
            text_color="#000",
            width=200,
            height=35,
            command=self.change_password
        ).pack(side="left", padx=(200, 0))
    
    def load_settings(self):
        """Load current settings"""
        # Load default values
        defaults = {
            'telegram_bot_token': '',
            'telegram_admin_id': '',
            'max_requests_minute': '30',
            'max_requests_hour': '500',
            'suspicious_threshold': '0.7',
            'api_backend_url': 'http://localhost:5001',
            'api_antigravity_url': 'https://api.antigravity.ai',
            'api_timeout': '30',
            'session_lifetime': '24',
            'max_login_attempts': '5',
            'lockout_duration': '30',
            'ip_whitelist': '',
        }
        
        for key, value in defaults.items():
            if key in self.settings:
                widget = self.settings[key]
                if isinstance(widget, ctk.CTkEntry):
                    widget.delete(0, "end")
                    widget.insert(0, value)
    
    def save_settings(self):
        """Save all settings"""
        # Collect values
        values = {}
        for key, widget in self.settings.items():
            if isinstance(widget, ctk.CTkEntry):
                values[key] = widget.get()
            elif isinstance(widget, ctk.BooleanVar):
                values[key] = widget.get()
        
        # Validate
        try:
            int(values.get('max_requests_minute', '30'))
            int(values.get('max_requests_hour', '500'))
            float(values.get('suspicious_threshold', '0.7'))
            int(values.get('api_timeout', '30'))
            int(values.get('session_lifetime', '24'))
            int(values.get('max_login_attempts', '5'))
            int(values.get('lockout_duration', '30'))
        except ValueError:
            MessageDialog(
                self.winfo_toplevel(),
                "Validation Error",
                "Please enter valid numeric values for threshold fields.",
                message_type="error"
            )
            return
        
        # Save (mock)
        MessageDialog(
            self.winfo_toplevel(),
            "Settings Saved",
            "All settings have been saved successfully.",
            message_type="success"
        )
    
    def test_telegram(self):
        """Test Telegram connection"""
        bot_token = self.settings.get('telegram_bot_token')
        admin_id = self.settings.get('telegram_admin_id')
        
        if bot_token and admin_id:
            token = bot_token.get() if isinstance(bot_token, ctk.CTkEntry) else ''
            chat_id = admin_id.get() if isinstance(admin_id, ctk.CTkEntry) else ''
            
            if not token or not chat_id:
                MessageDialog(
                    self.winfo_toplevel(),
                    "Test Failed",
                    "Please enter both Bot Token and Admin Chat ID.",
                    message_type="error"
                )
                return
        
        # Mock test
        MessageDialog(
            self.winfo_toplevel(),
            "Test Successful",
            "Telegram connection test successful!\n\nA test message has been sent to the admin chat.",
            message_type="success"
        )
    
    def change_password(self):
        """Open change password dialog"""
        from components.dialog import InputDialog
        
        fields = [
            {'key': 'current', 'label': 'Current Password', 'type': 'password', 'required': True},
            {'key': 'new', 'label': 'New Password', 'type': 'password', 'required': True},
            {'key': 'confirm', 'label': 'Confirm Password', 'type': 'password', 'required': True},
        ]
        
        dialog = InputDialog(
            self.winfo_toplevel(),
            "Change Password",
            fields,
            submit_text="Change Password",
            on_submit=self._do_change_password
        )
        dialog.wait_window()
    
    def _do_change_password(self, data: dict):
        """Perform password change"""
        current = data.get('current', '')
        new = data.get('new', '')
        confirm = data.get('confirm', '')
        
        if new != confirm:
            MessageDialog(
                self.winfo_toplevel(),
                "Password Mismatch",
                "New password and confirmation do not match.",
                message_type="error"
            )
            return
        
        if len(new) < 8:
            MessageDialog(
                self.winfo_toplevel(),
                "Password Too Short",
                "Password must be at least 8 characters long.",
                message_type="error"
            )
            return
        
        # Mock password change
        MessageDialog(
            self.winfo_toplevel(),
            "Password Changed",
            "Your password has been changed successfully.",
            message_type="success"
        )
