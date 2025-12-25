#!/usr/bin/env python3
"""
dLNk Admin Console - Data Table Component
"""

import customtkinter as ctk
from typing import List, Dict, Callable, Optional
from utils.theme import COLORS, STATUS_COLORS


class DataTable(ctk.CTkScrollableFrame):
    """Scrollable Data Table Component"""
    
    def __init__(self, parent, columns: List[Dict], data: List[Dict] = None, 
                 on_row_click: Callable = None, row_height: int = 45):
        super().__init__(parent, fg_color=COLORS['bg_tertiary'], corner_radius=10)
        
        self.columns = columns  # [{'key': 'name', 'title': 'Name', 'width': 150}, ...]
        self.data = data or []
        self.on_row_click = on_row_click
        self.row_height = row_height
        self.rows = []
        
        self.create_header()
        self.populate_data()
    
    def create_header(self):
        """Create table header"""
        header_frame = ctk.CTkFrame(self, fg_color=COLORS['bg_secondary'], height=40)
        header_frame.pack(fill="x", padx=5, pady=(5, 0))
        header_frame.pack_propagate(False)
        
        for col in self.columns:
            label = ctk.CTkLabel(
                header_frame,
                text=col.get('title', col.get('key', '')),
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=COLORS['text_secondary'],
                width=col.get('width', 100),
                anchor="w"
            )
            label.pack(side="left", padx=10)
    
    def populate_data(self):
        """Populate table with data"""
        # Clear existing rows
        for row in self.rows:
            row.destroy()
        self.rows = []
        
        # Create rows
        for i, item in enumerate(self.data):
            row = self._create_row(item, i)
            self.rows.append(row)
    
    def _create_row(self, item: Dict, index: int) -> ctk.CTkFrame:
        """Create a data row"""
        bg_color = COLORS['bg_tertiary'] if index % 2 == 0 else COLORS['bg_secondary']
        
        row_frame = ctk.CTkFrame(
            self, 
            fg_color=bg_color, 
            height=self.row_height,
            corner_radius=0
        )
        row_frame.pack(fill="x", padx=5, pady=1)
        row_frame.pack_propagate(False)
        
        # Make row clickable
        if self.on_row_click:
            row_frame.bind("<Button-1>", lambda e, data=item: self.on_row_click(data))
            row_frame.configure(cursor="hand2")
        
        for col in self.columns:
            key = col.get('key', '')
            value = item.get(key, '')
            
            # Handle special column types
            col_type = col.get('type', 'text')
            
            if col_type == 'status':
                self._create_status_cell(row_frame, value, col.get('width', 100))
            elif col_type == 'actions':
                self._create_actions_cell(row_frame, item, col.get('actions', []), col.get('width', 150))
            elif col_type == 'code':
                self._create_code_cell(row_frame, value, col.get('width', 150))
            else:
                self._create_text_cell(row_frame, str(value), col.get('width', 100))
        
        return row_frame
    
    def _create_text_cell(self, parent, text: str, width: int):
        """Create a text cell"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_primary'],
            width=width,
            anchor="w"
        )
        label.pack(side="left", padx=10)
    
    def _create_code_cell(self, parent, text: str, width: int):
        """Create a code/monospace cell"""
        label = ctk.CTkLabel(
            parent,
            text=text,
            font=ctk.CTkFont(size=11, family="Consolas"),
            text_color=COLORS['success'],
            width=width,
            anchor="w"
        )
        label.pack(side="left", padx=10)
    
    def _create_status_cell(self, parent, status: str, width: int):
        """Create a status cell with color"""
        status_lower = status.lower() if status else ''
        color = STATUS_COLORS.get(status_lower, COLORS['text_secondary'])
        
        # Status indicator
        frame = ctk.CTkFrame(parent, fg_color="transparent", width=width)
        frame.pack(side="left", padx=10)
        frame.pack_propagate(False)
        
        # Dot indicator
        dot = ctk.CTkLabel(
            frame,
            text="●",
            font=ctk.CTkFont(size=10),
            text_color=color
        )
        dot.pack(side="left")
        
        # Status text
        label = ctk.CTkLabel(
            frame,
            text=status.title() if status else 'N/A',
            font=ctk.CTkFont(size=12),
            text_color=color
        )
        label.pack(side="left", padx=5)
    
    def _create_actions_cell(self, parent, item: Dict, actions: List[Dict], width: int):
        """Create an actions cell with buttons"""
        frame = ctk.CTkFrame(parent, fg_color="transparent", width=width)
        frame.pack(side="left", padx=5)
        
        for action in actions:
            btn = ctk.CTkButton(
                frame,
                text=action.get('text', 'Action'),
                font=ctk.CTkFont(size=11),
                fg_color=action.get('color', COLORS['bg_secondary']),
                hover_color=action.get('hover_color', COLORS['accent']),
                text_color=COLORS['text_primary'],
                width=action.get('width', 60),
                height=28,
                command=lambda a=action, d=item: a.get('callback', lambda x: None)(d)
            )
            btn.pack(side="left", padx=2)
    
    def update_data(self, data: List[Dict]):
        """Update table data"""
        self.data = data
        self.populate_data()
    
    def add_row(self, item: Dict):
        """Add a single row"""
        self.data.append(item)
        row = self._create_row(item, len(self.data) - 1)
        self.rows.append(row)
    
    def remove_row(self, index: int):
        """Remove a row by index"""
        if 0 <= index < len(self.rows):
            self.rows[index].destroy()
            self.rows.pop(index)
            self.data.pop(index)
    
    def clear(self):
        """Clear all data"""
        for row in self.rows:
            row.destroy()
        self.rows = []
        self.data = []
