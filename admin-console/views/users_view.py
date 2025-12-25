#!/usr/bin/env python3
"""
dLNk Admin Console - User Management View
"""

import customtkinter as ctk
from utils.theme import COLORS, STATUS_COLORS
from components.header import Header
from components.dialog import ConfirmDialog, MessageDialog


class UsersView(ctk.CTkFrame):
    """User Management View"""
    
    def __init__(self, parent, api_client=None):
        super().__init__(parent, fg_color="transparent")
        
        self.api_client = api_client
        self.users = []
        self.filtered_users = []
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create user management widgets"""
        # Header
        self.header = Header(self, "User Management", on_refresh=self.load_data)
        self.header.pack(fill="x", pady=(0, 20))
        
        # Search and Filter Bar
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 15))
        
        # Search Entry
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="🔍 Search users...",
            width=300,
            height=40,
            fg_color=COLORS['bg_tertiary'],
            border_color=COLORS['border']
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_users())
        
        # Status Filter
        self.status_var = ctk.StringVar(value="All")
        status_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Active", "Banned"],
            variable=self.status_var,
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['bg_secondary'],
            dropdown_hover_color=COLORS['accent'],
            width=120,
            height=40,
            command=lambda x: self.filter_users()
        )
        status_filter.pack(side="left", padx=10)
        
        # Role Filter
        self.role_var = ctk.StringVar(value="All Roles")
        role_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Roles", "User", "Premium", "Admin"],
            variable=self.role_var,
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['bg_secondary'],
            dropdown_hover_color=COLORS['accent'],
            width=130,
            height=40,
            command=lambda x: self.filter_users()
        )
        role_filter.pack(side="left")
        
        # User count
        self.count_label = ctk.CTkLabel(
            filter_frame,
            text="0 users",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.count_label.pack(side="right")
        
        # Users Table
        self.table_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=COLORS['bg_tertiary'],
            corner_radius=10,
            scrollbar_button_color=COLORS['border'],
            scrollbar_button_hover_color=COLORS['accent']
        )
        self.table_frame.pack(fill="both", expand=True)
        
        # Table Header
        self._create_table_header()
    
    def _create_table_header(self):
        """Create table header row"""
        header_row = ctk.CTkFrame(self.table_frame, fg_color=COLORS['bg_secondary'], height=45)
        header_row.pack(fill="x", padx=5, pady=5)
        header_row.pack_propagate(False)
        
        headers = [
            ("Username", 150),
            ("Email", 200),
            ("Role", 100),
            ("Status", 100),
            ("Created", 100),
            ("Last Login", 100),
            ("Actions", 150),
        ]
        
        for title, width in headers:
            ctk.CTkLabel(
                header_row,
                text=title,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_secondary'],
                width=width,
                anchor="w"
            ).pack(side="left", padx=10)
    
    def load_data(self):
        """Load users from API"""
        if self.api_client:
            self.users = self.api_client.get_users()
        else:
            self.users = self._get_mock_users()
        
        self.filter_users()
    
    def _get_mock_users(self):
        """Get mock user data"""
        return [
            {'username': 'john_doe', 'email': 'john@example.com', 'role': 'user', 'status': 'active', 'created': '2024-01-15', 'last_login': '2025-01-10'},
            {'username': 'jane_smith', 'email': 'jane@example.com', 'role': 'premium', 'status': 'active', 'created': '2024-02-20', 'last_login': '2025-01-09'},
            {'username': 'bob_wilson', 'email': 'bob@example.com', 'role': 'user', 'status': 'banned', 'created': '2024-03-10', 'last_login': '2024-12-01'},
            {'username': 'alice_jones', 'email': 'alice@example.com', 'role': 'premium', 'status': 'active', 'created': '2024-04-05', 'last_login': '2025-01-10'},
            {'username': 'charlie_brown', 'email': 'charlie@example.com', 'role': 'user', 'status': 'active', 'created': '2024-05-12', 'last_login': '2025-01-08'},
            {'username': 'admin_user', 'email': 'admin@dlnk.io', 'role': 'admin', 'status': 'active', 'created': '2024-01-01', 'last_login': '2025-01-10'},
        ]
    
    def filter_users(self):
        """Filter users based on search and filters"""
        search_text = self.search_entry.get().lower()
        status_filter = self.status_var.get().lower()
        role_filter = self.role_var.get().lower()
        
        self.filtered_users = []
        
        for user in self.users:
            # Search filter
            if search_text:
                searchable = f"{user.get('username', '')} {user.get('email', '')}".lower()
                if search_text not in searchable:
                    continue
            
            # Status filter
            if status_filter != "all":
                if user.get('status', '').lower() != status_filter:
                    continue
            
            # Role filter
            if role_filter != "all roles":
                if user.get('role', '').lower() != role_filter:
                    continue
            
            self.filtered_users.append(user)
        
        self._render_users()
        self.count_label.configure(text=f"{len(self.filtered_users)} users")
    
    def _render_users(self):
        """Render user rows"""
        # Clear existing rows (except header)
        for widget in self.table_frame.winfo_children()[1:]:
            widget.destroy()
        
        if not self.filtered_users:
            no_data = ctk.CTkLabel(
                self.table_frame,
                text="No users found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS['text_secondary']
            )
            no_data.pack(pady=50)
            return
        
        for i, user in enumerate(self.filtered_users):
            self._create_user_row(user, i)
    
    def _create_user_row(self, user: dict, index: int):
        """Create a user row"""
        bg_color = COLORS['bg_tertiary'] if index % 2 == 0 else COLORS['bg_secondary']
        
        row = ctk.CTkFrame(self.table_frame, fg_color=bg_color, height=50)
        row.pack(fill="x", padx=5, pady=1)
        row.pack_propagate(False)
        
        # Username
        ctk.CTkLabel(
            row,
            text=user.get('username', 'N/A'),
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=COLORS['text_primary'],
            width=150,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Email
        ctk.CTkLabel(
            row,
            text=user.get('email', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            width=200,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Role
        role = user.get('role', 'user')
        role_colors = {
            'admin': COLORS['accent'],
            'premium': COLORS['success'],
            'user': COLORS['text_secondary']
        }
        ctk.CTkLabel(
            row,
            text=role.title(),
            font=ctk.CTkFont(size=12),
            text_color=role_colors.get(role.lower(), COLORS['text_secondary']),
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Status
        status = user.get('status', 'unknown').lower()
        status_color = COLORS['success'] if status == 'active' else COLORS['error']
        
        ctk.CTkLabel(
            row,
            text=f"● {status.title()}",
            font=ctk.CTkFont(size=12),
            text_color=status_color,
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Created
        ctk.CTkLabel(
            row,
            text=user.get('created', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Last Login
        ctk.CTkLabel(
            row,
            text=user.get('last_login', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Actions
        actions_frame = ctk.CTkFrame(row, fg_color="transparent", width=150)
        actions_frame.pack(side="left", padx=5)
        
        # View Activity button
        ctk.CTkButton(
            actions_frame,
            text="Activity",
            font=ctk.CTkFont(size=11),
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['accent'],
            width=60,
            height=28,
            command=lambda u=user: self.view_activity(u)
        ).pack(side="left", padx=2)
        
        # Ban/Unban button
        if status == 'active':
            ctk.CTkButton(
                actions_frame,
                text="Ban",
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['error'],
                hover_color="#cc3a47",
                width=50,
                height=28,
                command=lambda u=user: self.ban_user(u)
            ).pack(side="left", padx=2)
        else:
            ctk.CTkButton(
                actions_frame,
                text="Unban",
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['success'],
                hover_color="#00b3cc",
                width=55,
                height=28,
                command=lambda u=user: self.unban_user(u)
            ).pack(side="left", padx=2)
    
    def view_activity(self, user: dict):
        """View user activity log"""
        # Mock activity data
        activities = [
            f"• 2025-01-10 14:30 - AI Request (success)",
            f"• 2025-01-10 14:25 - AI Request (success)",
            f"• 2025-01-10 14:20 - Login from 192.168.1.100",
            f"• 2025-01-09 18:45 - AI Request (success)",
            f"• 2025-01-09 18:30 - Login from 192.168.1.100",
        ]
        
        activity_text = f"Activity Log for {user.get('username', 'N/A')}\n\n" + "\n".join(activities)
        
        MessageDialog(
            self.winfo_toplevel(),
            "User Activity",
            activity_text,
            message_type="info"
        )
    
    def ban_user(self, user: dict):
        """Ban a user"""
        dialog = ConfirmDialog(
            self.winfo_toplevel(),
            "Ban User",
            f"Are you sure you want to ban user '{user.get('username', '')}'?\n\nThey will no longer be able to use the service.",
            confirm_text="Ban",
            confirm_color=COLORS['error'],
            on_confirm=lambda: self._do_ban(user)
        )
        dialog.wait_window()
    
    def _do_ban(self, user: dict):
        """Perform user ban"""
        if self.api_client:
            self.api_client.ban_user(user.get('username', ''))
        
        MessageDialog(
            self.winfo_toplevel(),
            "User Banned",
            f"User '{user.get('username', '')}' has been banned.",
            message_type="warning"
        )
        self.load_data()
    
    def unban_user(self, user: dict):
        """Unban a user"""
        dialog = ConfirmDialog(
            self.winfo_toplevel(),
            "Unban User",
            f"Are you sure you want to unban user '{user.get('username', '')}'?",
            confirm_text="Unban",
            confirm_color=COLORS['success'],
            on_confirm=lambda: self._do_unban(user)
        )
        dialog.wait_window()
    
    def _do_unban(self, user: dict):
        """Perform user unban"""
        if self.api_client:
            self.api_client.unban_user(user.get('username', ''))
        
        MessageDialog(
            self.winfo_toplevel(),
            "User Unbanned",
            f"User '{user.get('username', '')}' has been unbanned.",
            message_type="success"
        )
        self.load_data()
