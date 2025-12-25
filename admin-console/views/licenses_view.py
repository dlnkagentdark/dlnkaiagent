#!/usr/bin/env python3
"""
dLNk Admin Console - License Management View
"""

import customtkinter as ctk
from utils.theme import COLORS, STATUS_COLORS
from components.header import Header
from components.dialog import InputDialog, ConfirmDialog, MessageDialog


class LicensesView(ctk.CTkFrame):
    """License Management View"""
    
    def __init__(self, parent, api_client=None):
        super().__init__(parent, fg_color="transparent")
        
        self.api_client = api_client
        self.licenses = []
        self.filtered_licenses = []
        
        self.create_widgets()
        self.load_data()
    
    def create_widgets(self):
        """Create license management widgets"""
        # Header with Create button
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        
        self.header = Header(header_frame, "License Management", on_refresh=self.load_data)
        self.header.pack(side="left", fill="x", expand=True)
        
        # Create License Button
        create_btn = ctk.CTkButton(
            header_frame,
            text="+ Create License",
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['accent'],
            hover_color=COLORS['hover'],
            width=150,
            height=38,
            command=self.show_create_dialog
        )
        create_btn.pack(side="right", padx=(20, 0))
        
        # Search and Filter Bar
        filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        filter_frame.pack(fill="x", pady=(0, 15))
        
        # Search Entry
        self.search_entry = ctk.CTkEntry(
            filter_frame,
            placeholder_text="🔍 Search licenses...",
            width=300,
            height=40,
            fg_color=COLORS['bg_tertiary'],
            border_color=COLORS['border']
        )
        self.search_entry.pack(side="left")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_licenses())
        
        # Status Filter
        self.status_var = ctk.StringVar(value="All")
        status_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All", "Active", "Expired", "Revoked"],
            variable=self.status_var,
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['bg_secondary'],
            dropdown_hover_color=COLORS['accent'],
            width=120,
            height=40,
            command=lambda x: self.filter_licenses()
        )
        status_filter.pack(side="left", padx=10)
        
        # Type Filter
        self.type_var = ctk.StringVar(value="All Types")
        type_filter = ctk.CTkOptionMenu(
            filter_frame,
            values=["All Types", "Trial", "Basic", "Pro", "Enterprise", "Admin"],
            variable=self.type_var,
            fg_color=COLORS['bg_tertiary'],
            button_color=COLORS['accent'],
            button_hover_color=COLORS['hover'],
            dropdown_fg_color=COLORS['bg_secondary'],
            dropdown_hover_color=COLORS['accent'],
            width=130,
            height=40,
            command=lambda x: self.filter_licenses()
        )
        type_filter.pack(side="left")
        
        # License count
        self.count_label = ctk.CTkLabel(
            filter_frame,
            text="0 licenses",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        self.count_label.pack(side="right")
        
        # Licenses Table
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
            ("License Key", 200),
            ("User", 120),
            ("Type", 100),
            ("Status", 100),
            ("Expires", 100),
            ("Actions", 180),
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
        """Load licenses from API"""
        if self.api_client:
            self.licenses = self.api_client.get_licenses()
        else:
            self.licenses = self._get_mock_licenses()
        
        self.filter_licenses()
    
    def _get_mock_licenses(self):
        """Get mock license data"""
        return [
            {'key': 'DLNK-PRO-A1B2-C3D4-E5F6', 'user': 'john_doe', 'type': 'Pro', 'status': 'active', 'expires': '2025-12-31'},
            {'key': 'DLNK-ENT-G7H8-I9J0-K1L2', 'user': 'jane_smith', 'type': 'Enterprise', 'status': 'active', 'expires': '2026-06-30'},
            {'key': 'DLNK-TRI-M3N4-O5P6-Q7R8', 'user': 'bob_wilson', 'type': 'Trial', 'status': 'expired', 'expires': '2024-01-15'},
            {'key': 'DLNK-BAS-S9T0-U1V2-W3X4', 'user': 'alice_jones', 'type': 'Basic', 'status': 'active', 'expires': '2025-09-20'},
            {'key': 'DLNK-PRO-Y5Z6-A7B8-C9D0', 'user': 'charlie_brown', 'type': 'Pro', 'status': 'revoked', 'expires': '2025-03-15'},
            {'key': 'DLNK-ADM-E1F2-G3H4-I5J6', 'user': 'admin_user', 'type': 'Admin', 'status': 'active', 'expires': '2027-01-01'},
        ]
    
    def filter_licenses(self):
        """Filter licenses based on search and filters"""
        search_text = self.search_entry.get().lower()
        status_filter = self.status_var.get().lower()
        type_filter = self.type_var.get().lower()
        
        self.filtered_licenses = []
        
        for lic in self.licenses:
            # Search filter
            if search_text:
                searchable = f"{lic.get('key', '')} {lic.get('user', '')}".lower()
                if search_text not in searchable:
                    continue
            
            # Status filter
            if status_filter != "all":
                if lic.get('status', '').lower() != status_filter:
                    continue
            
            # Type filter
            if type_filter != "all types":
                if lic.get('type', '').lower() != type_filter:
                    continue
            
            self.filtered_licenses.append(lic)
        
        self._render_licenses()
        self.count_label.configure(text=f"{len(self.filtered_licenses)} licenses")
    
    def _render_licenses(self):
        """Render license rows"""
        # Clear existing rows (except header)
        for widget in self.table_frame.winfo_children()[1:]:
            widget.destroy()
        
        if not self.filtered_licenses:
            no_data = ctk.CTkLabel(
                self.table_frame,
                text="No licenses found",
                font=ctk.CTkFont(size=14),
                text_color=COLORS['text_secondary']
            )
            no_data.pack(pady=50)
            return
        
        for i, lic in enumerate(self.filtered_licenses):
            self._create_license_row(lic, i)
    
    def _create_license_row(self, lic: dict, index: int):
        """Create a license row"""
        bg_color = COLORS['bg_tertiary'] if index % 2 == 0 else COLORS['bg_secondary']
        
        row = ctk.CTkFrame(self.table_frame, fg_color=bg_color, height=50)
        row.pack(fill="x", padx=5, pady=1)
        row.pack_propagate(False)
        
        # License Key
        ctk.CTkLabel(
            row,
            text=lic.get('key', 'N/A'),
            font=ctk.CTkFont(size=11, family="Consolas"),
            text_color=COLORS['success'],
            width=200,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # User
        ctk.CTkLabel(
            row,
            text=lic.get('user', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
            width=120,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Type
        ctk.CTkLabel(
            row,
            text=lic.get('type', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['accent'],
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Status
        status = lic.get('status', 'unknown').lower()
        status_color = STATUS_COLORS.get(status, COLORS['text_secondary'])
        
        status_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
        status_frame.pack(side="left", padx=10)
        status_frame.pack_propagate(False)
        
        ctk.CTkLabel(
            status_frame,
            text=f"● {status.title()}",
            font=ctk.CTkFont(size=12),
            text_color=status_color,
            anchor="w"
        ).pack(side="left")
        
        # Expires
        ctk.CTkLabel(
            row,
            text=lic.get('expires', 'N/A'),
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary'],
            width=100,
            anchor="w"
        ).pack(side="left", padx=10)
        
        # Actions
        actions_frame = ctk.CTkFrame(row, fg_color="transparent", width=180)
        actions_frame.pack(side="left", padx=5)
        
        # View button
        ctk.CTkButton(
            actions_frame,
            text="View",
            font=ctk.CTkFont(size=11),
            fg_color=COLORS['bg_secondary'],
            hover_color=COLORS['accent'],
            width=50,
            height=28,
            command=lambda l=lic: self.view_license(l)
        ).pack(side="left", padx=2)
        
        # Extend button
        if status == 'active':
            ctk.CTkButton(
                actions_frame,
                text="+30d",
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['success'],
                hover_color="#00b3cc",
                width=50,
                height=28,
                command=lambda l=lic: self.extend_license(l)
            ).pack(side="left", padx=2)
            
            # Revoke button
            ctk.CTkButton(
                actions_frame,
                text="Revoke",
                font=ctk.CTkFont(size=11),
                fg_color=COLORS['error'],
                hover_color="#cc3a47",
                width=55,
                height=28,
                command=lambda l=lic: self.revoke_license(l)
            ).pack(side="left", padx=2)
    
    def show_create_dialog(self):
        """Show create license dialog"""
        fields = [
            {'key': 'owner', 'label': 'Owner Name', 'type': 'text', 'required': True, 'placeholder': 'Enter owner name'},
            {'key': 'type', 'label': 'License Type', 'type': 'select', 'required': True, 
             'options': ['Trial', 'Basic', 'Pro', 'Enterprise', 'Admin'], 'default': 'Basic'},
            {'key': 'duration', 'label': 'Duration (days)', 'type': 'number', 'required': True, 'default': '30'},
        ]
        
        dialog = InputDialog(
            self.winfo_toplevel(),
            "Create New License",
            fields,
            submit_text="Create",
            on_submit=self._create_license
        )
        dialog.wait_window()
    
    def _create_license(self, data: dict):
        """Create a new license"""
        owner = data.get('owner', '')
        license_type = data.get('type', 'Basic')
        duration = int(data.get('duration', 30))
        
        if self.api_client:
            result = self.api_client.create_license(owner, license_type, duration)
        else:
            # Mock creation
            import secrets
            result = {
                'key': f"DLNK-{license_type[:3].upper()}-{secrets.token_hex(4).upper()}-{secrets.token_hex(4).upper()}",
                'owner': owner,
                'type': license_type,
                'expires': '2026-01-10',
                'encrypted': f"gAAAAAB{secrets.token_urlsafe(64)}"
            }
        
        # Show success dialog with license key
        MessageDialog(
            self.winfo_toplevel(),
            "License Created",
            f"License created successfully!\n\nKey: {result.get('key', 'N/A')}\nExpires: {result.get('expires', 'N/A')}",
            message_type="success"
        )
        
        self.load_data()
    
    def view_license(self, lic: dict):
        """View license details"""
        details = f"""
License Key: {lic.get('key', 'N/A')}
User: {lic.get('user', 'N/A')}
Type: {lic.get('type', 'N/A')}
Status: {lic.get('status', 'N/A').title()}
Expires: {lic.get('expires', 'N/A')}
        """.strip()
        
        MessageDialog(
            self.winfo_toplevel(),
            "License Details",
            details,
            message_type="info"
        )
    
    def extend_license(self, lic: dict):
        """Extend license by 30 days"""
        dialog = ConfirmDialog(
            self.winfo_toplevel(),
            "Extend License",
            f"Extend license {lic.get('key', '')} by 30 days?",
            confirm_text="Extend",
            confirm_color=COLORS['success'],
            on_confirm=lambda: self._do_extend(lic)
        )
        dialog.wait_window()
    
    def _do_extend(self, lic: dict):
        """Perform license extension"""
        if self.api_client:
            self.api_client.extend_license(lic.get('key', ''), 30)
        
        MessageDialog(
            self.winfo_toplevel(),
            "License Extended",
            f"License extended by 30 days.",
            message_type="success"
        )
        self.load_data()
    
    def revoke_license(self, lic: dict):
        """Revoke a license"""
        dialog = ConfirmDialog(
            self.winfo_toplevel(),
            "Revoke License",
            f"Are you sure you want to revoke license {lic.get('key', '')}?\n\nThis action cannot be undone.",
            confirm_text="Revoke",
            confirm_color=COLORS['error'],
            on_confirm=lambda: self._do_revoke(lic)
        )
        dialog.wait_window()
    
    def _do_revoke(self, lic: dict):
        """Perform license revocation"""
        if self.api_client:
            self.api_client.revoke_license(lic.get('key', ''))
        
        MessageDialog(
            self.winfo_toplevel(),
            "License Revoked",
            f"License has been revoked.",
            message_type="warning"
        )
        self.load_data()
