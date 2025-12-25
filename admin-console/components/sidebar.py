#!/usr/bin/env python3
"""
dLNk Admin Console - Navigation Sidebar Component
"""

import customtkinter as ctk
from utils.theme import COLORS


class Sidebar(ctk.CTkFrame):
    """Navigation Sidebar Component"""
    
    def __init__(self, parent, on_navigate, on_logout=None):
        super().__init__(parent, fg_color=COLORS['sidebar_bg'], width=220)
        self.pack_propagate(False)
        
        self.on_navigate = on_navigate
        self.on_logout = on_logout
        self.buttons = {}
        self.active_button = None
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create sidebar widgets"""
        # Logo Section
        logo_frame = ctk.CTkFrame(self, fg_color="transparent")
        logo_frame.pack(fill="x", pady=20)
        
        # Logo Text
        ctk.CTkLabel(
            logo_frame,
            text="dLNk",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=COLORS['accent']
        ).pack()
        
        ctk.CTkLabel(
            logo_frame,
            text="Admin Console",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        ).pack()
        
        # Divider
        ctk.CTkFrame(
            self, 
            height=1, 
            fg_color=COLORS['border']
        ).pack(fill="x", padx=20, pady=10)
        
        # Navigation Items
        nav_items = [
            ("dashboard", "📊", "Dashboard"),
            ("licenses", "🔑", "Licenses"),
            ("users", "👥", "Users"),
            ("logs", "📋", "Logs"),
            ("tokens", "🎫", "Tokens"),
            ("settings", "⚙️", "Settings"),
        ]
        
        nav_frame = ctk.CTkFrame(self, fg_color="transparent")
        nav_frame.pack(fill="x", pady=10)
        
        for view_id, icon, label in nav_items:
            btn = self._create_nav_button(nav_frame, view_id, icon, label)
            self.buttons[view_id] = btn
        
        # Set dashboard as active by default
        self.set_active("dashboard")
        
        # Spacer
        ctk.CTkFrame(self, fg_color="transparent").pack(fill="both", expand=True)
        
        # User Info Section (at bottom)
        user_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_tertiary'], corner_radius=10)
        user_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.user_label = ctk.CTkLabel(
            user_frame,
            text="Admin",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLORS['accent']
        )
        self.user_label.pack(anchor="w", padx=15, pady=(10, 2))
        
        self.role_label = ctk.CTkLabel(
            user_frame,
            text="Administrator",
            font=ctk.CTkFont(size=11),
            text_color=COLORS['text_secondary']
        )
        self.role_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Logout Button
        logout_btn = ctk.CTkButton(
            self,
            text="🚪 Logout",
            font=ctk.CTkFont(size=13),
            fg_color="transparent",
            hover_color=COLORS['error'],
            text_color=COLORS['text_secondary'],
            anchor="w",
            height=40,
            command=self._handle_logout
        )
        logout_btn.pack(fill="x", padx=15, pady=(0, 20))
    
    def _create_nav_button(self, parent, view_id: str, icon: str, label: str) -> ctk.CTkButton:
        """Create a navigation button"""
        btn = ctk.CTkButton(
            parent,
            text=f"{icon}  {label}",
            font=ctk.CTkFont(size=14),
            fg_color="transparent",
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_secondary'],
            anchor="w",
            height=42,
            corner_radius=8,
            command=lambda v=view_id: self._navigate(v)
        )
        btn.pack(fill="x", padx=10, pady=2)
        return btn
    
    def _navigate(self, view_id: str):
        """Handle navigation"""
        self.set_active(view_id)
        if self.on_navigate:
            self.on_navigate(view_id)
    
    def set_active(self, view_id: str):
        """Set active navigation button"""
        # Reset all buttons
        for btn in self.buttons.values():
            btn.configure(
                fg_color="transparent",
                text_color=COLORS['text_secondary']
            )
        
        # Set active button
        if view_id in self.buttons:
            self.buttons[view_id].configure(
                fg_color=COLORS['accent'],
                text_color=COLORS['text_primary']
            )
            self.active_button = view_id
    
    def update_user_info(self, username: str, role: str):
        """Update user info display"""
        self.user_label.configure(text=username)
        self.role_label.configure(text=role.title())
    
    def _handle_logout(self):
        """Handle logout button click"""
        if self.on_logout:
            self.on_logout()
        else:
            # Try to get root window and call logout
            try:
                self.winfo_toplevel().logout()
            except Exception:
                pass
