#!/usr/bin/env python3
"""
dLNk Admin Console - Header Component
"""

import customtkinter as ctk
from datetime import datetime
from utils.theme import COLORS


class Header(ctk.CTkFrame):
    """Page Header Component"""
    
    def __init__(self, parent, title: str, show_refresh: bool = True, on_refresh=None):
        super().__init__(parent, fg_color="transparent")
        
        self.title = title
        self.on_refresh = on_refresh
        
        self.create_widgets(show_refresh)
    
    def create_widgets(self, show_refresh: bool):
        """Create header widgets"""
        # Title
        title_label = ctk.CTkLabel(
            self,
            text=self.title,
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(side="left")
        
        # Right side container
        right_frame = ctk.CTkFrame(self, fg_color="transparent")
        right_frame.pack(side="right")
        
        # Last updated time
        self.time_label = ctk.CTkLabel(
            right_frame,
            text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.time_label.pack(side="left", padx=(0, 15))
        
        # Refresh button
        if show_refresh:
            refresh_btn = ctk.CTkButton(
                right_frame,
                text="🔄 Refresh",
                font=ctk.CTkFont(size=13),
                fg_color=COLORS['bg_tertiary'],
                hover_color=COLORS['accent'],
                text_color=COLORS['text_primary'],
                width=100,
                height=32,
                command=self._handle_refresh
            )
            refresh_btn.pack(side="left")
    
    def _handle_refresh(self):
        """Handle refresh button click"""
        self.update_time()
        if self.on_refresh:
            self.on_refresh()
    
    def update_time(self):
        """Update the last updated time"""
        self.time_label.configure(
            text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def set_title(self, title: str):
        """Update the title"""
        self.title = title
        # Find and update title label
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkLabel):
                widget.configure(text=title)
                break
