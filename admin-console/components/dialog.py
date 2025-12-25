#!/usr/bin/env python3
"""
dLNk Admin Console - Dialog Components
"""

import customtkinter as ctk
from typing import Callable, Optional
from utils.theme import COLORS


class Dialog(ctk.CTkToplevel):
    """Base Dialog Component"""
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Center on parent
        self.transient(parent)
        self.grab_set()
        
        # Configure appearance
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Position window
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
        
        self.result = None
    
    def close(self, result=None):
        """Close the dialog"""
        self.result = result
        self.grab_release()
        self.destroy()


class ConfirmDialog(Dialog):
    """Confirmation Dialog"""
    
    def __init__(self, parent, title: str, message: str, 
                 confirm_text: str = "Confirm", cancel_text: str = "Cancel",
                 confirm_color: str = None, on_confirm: Callable = None):
        super().__init__(parent, title, width=400, height=200)
        
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.confirm_color = confirm_color or COLORS['accent']
        self.on_confirm = on_confirm
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Message
        message_label = ctk.CTkLabel(
            self,
            text=self.message,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_primary'],
            wraplength=350
        )
        message_label.pack(expand=True, padx=30, pady=30)
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text=self.cancel_text,
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_primary'],
            width=120,
            height=38,
            command=lambda: self.close(False)
        )
        cancel_btn.pack(side="left", expand=True, padx=5)
        
        # Confirm button
        confirm_btn = ctk.CTkButton(
            btn_frame,
            text=self.confirm_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.confirm_color,
            hover_color=COLORS['hover'],
            text_color=COLORS['text_primary'],
            width=120,
            height=38,
            command=self._confirm
        )
        confirm_btn.pack(side="right", expand=True, padx=5)
    
    def _confirm(self):
        """Handle confirm action"""
        if self.on_confirm:
            self.on_confirm()
        self.close(True)


class InputDialog(Dialog):
    """Input Dialog for getting user input"""
    
    def __init__(self, parent, title: str, fields: list, 
                 submit_text: str = "Submit", on_submit: Callable = None):
        # Calculate height based on number of fields
        height = 150 + (len(fields) * 70)
        super().__init__(parent, title, width=450, height=min(height, 500))
        
        self.fields = fields  # [{'key': 'name', 'label': 'Name', 'type': 'text', 'required': True}, ...]
        self.submit_text = submit_text
        self.on_submit = on_submit
        self.entries = {}
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Scrollable frame for fields
        scroll_frame = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color=COLORS['border']
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create input fields
        for field in self.fields:
            self._create_field(scroll_frame, field)
        
        # Error label
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['error']
        )
        self.error_label.pack(pady=(0, 10))
        
        # Buttons frame
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Cancel button
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Cancel",
            font=ctk.CTkFont(size=14),
            fg_color=COLORS['bg_tertiary'],
            hover_color=COLORS['bg_secondary'],
            text_color=COLORS['text_primary'],
            width=120,
            height=38,
            command=lambda: self.close(None)
        )
        cancel_btn.pack(side="left", expand=True, padx=5)
        
        # Submit button
        submit_btn = ctk.CTkButton(
            btn_frame,
            text=self.submit_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=COLORS['accent'],
            hover_color=COLORS['hover'],
            text_color=COLORS['text_primary'],
            width=120,
            height=38,
            command=self._submit
        )
        submit_btn.pack(side="right", expand=True, padx=5)
    
    def _create_field(self, parent, field: dict):
        """Create an input field"""
        key = field.get('key', '')
        label = field.get('label', key)
        field_type = field.get('type', 'text')
        required = field.get('required', False)
        options = field.get('options', [])
        default = field.get('default', '')
        
        # Label
        label_text = f"{label} {'*' if required else ''}"
        label_widget = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        label_widget.pack(anchor="w", pady=(10, 5))
        
        # Input widget
        if field_type == 'select':
            entry = ctk.CTkOptionMenu(
                parent,
                values=options,
                fg_color=COLORS['input_bg'],
                button_color=COLORS['accent'],
                button_hover_color=COLORS['hover'],
                dropdown_fg_color=COLORS['bg_secondary'],
                dropdown_hover_color=COLORS['accent'],
                width=400,
                height=40
            )
            if default:
                entry.set(default)
        elif field_type == 'number':
            entry = ctk.CTkEntry(
                parent,
                placeholder_text=field.get('placeholder', ''),
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=400,
                height=40
            )
            if default:
                entry.insert(0, str(default))
        elif field_type == 'password':
            entry = ctk.CTkEntry(
                parent,
                placeholder_text=field.get('placeholder', ''),
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=400,
                height=40,
                show="•"
            )
        elif field_type == 'textarea':
            entry = ctk.CTkTextbox(
                parent,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=400,
                height=100
            )
            if default:
                entry.insert("1.0", default)
        else:  # text
            entry = ctk.CTkEntry(
                parent,
                placeholder_text=field.get('placeholder', ''),
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=400,
                height=40
            )
            if default:
                entry.insert(0, default)
        
        entry.pack(anchor="w")
        self.entries[key] = {'widget': entry, 'type': field_type, 'required': required}
    
    def _get_values(self) -> dict:
        """Get all field values"""
        values = {}
        for key, entry_info in self.entries.items():
            widget = entry_info['widget']
            field_type = entry_info['type']
            
            if field_type == 'textarea':
                values[key] = widget.get("1.0", "end-1c")
            elif field_type == 'select':
                values[key] = widget.get()
            else:
                values[key] = widget.get()
        
        return values
    
    def _validate(self) -> tuple:
        """Validate all required fields"""
        values = self._get_values()
        
        for key, entry_info in self.entries.items():
            if entry_info['required'] and not values.get(key, '').strip():
                return False, f"Field '{key}' is required"
        
        return True, values
    
    def _submit(self):
        """Handle submit action"""
        valid, result = self._validate()
        
        if not valid:
            self.error_label.configure(text=result)
            return
        
        if self.on_submit:
            self.on_submit(result)
        
        self.close(result)


class MessageDialog(Dialog):
    """Simple message dialog"""
    
    def __init__(self, parent, title: str, message: str, 
                 message_type: str = "info", button_text: str = "OK"):
        super().__init__(parent, title, width=400, height=200)
        
        self.message = message
        self.message_type = message_type
        self.button_text = button_text
        
        self.create_widgets()
    
    def create_widgets(self):
        """Create dialog widgets"""
        # Icon based on type
        icons = {
            'info': ('ℹ️', COLORS['success']),
            'success': ('✅', COLORS['success']),
            'warning': ('⚠️', COLORS['warning']),
            'error': ('❌', COLORS['error']),
        }
        icon, color = icons.get(self.message_type, ('ℹ️', COLORS['text_primary']))
        
        # Icon
        icon_label = ctk.CTkLabel(
            self,
            text=icon,
            font=ctk.CTkFont(size=36)
        )
        icon_label.pack(pady=(30, 10))
        
        # Message
        message_label = ctk.CTkLabel(
            self,
            text=self.message,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_primary'],
            wraplength=350
        )
        message_label.pack(expand=True, padx=30)
        
        # OK button
        ok_btn = ctk.CTkButton(
            self,
            text=self.button_text,
            font=ctk.CTkFont(size=14),
            fg_color=color,
            hover_color=COLORS['hover'],
            text_color=COLORS['text_primary'],
            width=120,
            height=38,
            command=lambda: self.close(True)
        )
        ok_btn.pack(pady=(10, 30))
