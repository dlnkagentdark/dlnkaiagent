#!/usr/bin/env python3
"""
dLNk Admin Console - Dialog Components

This module provides reusable dialog components for the admin console.
All dialogs follow the dLNk Style Guide for consistent appearance.

Available Dialogs:
    - Dialog: Base dialog class
    - ConfirmDialog: Yes/No confirmation dialogs
    - InputDialog: Form input dialogs with multiple fields
    - MessageDialog: Simple message/alert dialogs
    - LoadingDialog: Loading indicator dialogs
    - ProgressDialog: Progress bar dialogs

Usage:
    from components.dialog import ConfirmDialog, MessageDialog
    
    # Show confirmation
    dialog = ConfirmDialog(
        parent=self,
        title="Confirm Action",
        message="Are you sure you want to delete this item?",
        confirm_color=COLORS['error']
    )
    if dialog.result:
        # User confirmed
        pass
    
    # Show message
    MessageDialog(parent=self, title="Success", message="Operation completed!", message_type="success")

Author: AI-04 UI/UX Designer
Version: 1.1.0
Last Updated: December 2025
"""

import customtkinter as ctk
from typing import Callable, Optional, List, Dict, Any
from utils.theme import COLORS, FONTS, RADIUS


class Dialog(ctk.CTkToplevel):
    """
    Base Dialog Component.
    
    Provides common functionality for all dialog types including
    window positioning, modal behavior, and theming.
    
    Attributes:
        result: The dialog result (set when closed)
        
    Args:
        parent: Parent window
        title: Dialog window title
        width: Dialog width in pixels
        height: Dialog height in pixels
    """
    
    def __init__(self, parent, title: str, width: int = 400, height: int = 300):
        """Initialize the base dialog."""
        super().__init__(parent)
        
        self.title(title)
        self.geometry(f"{width}x{height}")
        self.resizable(False, False)
        
        # Make modal
        self.transient(parent)
        self.grab_set()
        
        # Configure appearance
        self.configure(fg_color=COLORS['bg_primary'])
        
        # Center on parent window
        self._center_on_parent(parent, width, height)
        
        self.result = None
    
    def _center_on_parent(self, parent, width: int, height: int):
        """
        Center the dialog on the parent window.
        
        Args:
            parent: Parent window
            width: Dialog width
            height: Dialog height
        """
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - width) // 2
        y = parent.winfo_y() + (parent.winfo_height() - height) // 2
        self.geometry(f"+{x}+{y}")
    
    def close(self, result: Any = None):
        """
        Close the dialog with an optional result.
        
        Args:
            result: Value to return as the dialog result
        """
        self.result = result
        self.grab_release()
        self.destroy()


class ConfirmDialog(Dialog):
    """
    Confirmation Dialog for yes/no decisions.
    
    Displays a message with confirm and cancel buttons.
    
    Attributes:
        result: True if confirmed, False if cancelled
        
    Args:
        parent: Parent window
        title: Dialog title
        message: Confirmation message to display
        confirm_text: Text for confirm button (default: "Confirm")
        cancel_text: Text for cancel button (default: "Cancel")
        confirm_color: Color for confirm button (default: accent color)
        on_confirm: Callback function when confirmed
        
    Example:
        dialog = ConfirmDialog(
            parent=self,
            title="Delete User",
            message="Are you sure you want to delete this user?",
            confirm_text="Delete",
            confirm_color=COLORS['error']
        )
        if dialog.result:
            delete_user()
    """
    
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        confirm_text: str = "Confirm",
        cancel_text: str = "Cancel",
        confirm_color: str = None,
        on_confirm: Callable = None
    ):
        """Initialize the confirmation dialog."""
        super().__init__(parent, title, width=400, height=200)
        
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text
        self.confirm_color = confirm_color or COLORS['accent']
        self.on_confirm = on_confirm
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Message label
        message_label = ctk.CTkLabel(
            self,
            text=self.message,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_primary'],
            wraplength=350
        )
        message_label.pack(expand=True, padx=30, pady=30)
        
        # Button container
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
            corner_radius=RADIUS['md'],
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
            corner_radius=RADIUS['md'],
            command=self._on_confirm
        )
        confirm_btn.pack(side="right", expand=True, padx=5)
    
    def _on_confirm(self):
        """Handle confirm button click."""
        if self.on_confirm:
            self.on_confirm()
        self.close(True)


class InputDialog(Dialog):
    """
    Input Dialog for collecting user input.
    
    Supports multiple field types: text, password, number, select, textarea.
    
    Attributes:
        result: Dictionary of field values if submitted, None if cancelled
        
    Args:
        parent: Parent window
        title: Dialog title
        fields: List of field definitions
        submit_text: Text for submit button (default: "Submit")
        on_submit: Callback function with values dict when submitted
        
    Field Definition Format:
        {
            'key': 'field_name',      # Required: unique identifier
            'label': 'Field Label',   # Display label
            'type': 'text',           # text, password, number, select, textarea
            'required': True,         # Whether field is required
            'placeholder': 'Hint',    # Placeholder text
            'default': 'value',       # Default value
            'options': ['a', 'b']     # Options for select type
        }
        
    Example:
        fields = [
            {'key': 'email', 'label': 'Email', 'type': 'text', 'required': True},
            {'key': 'role', 'label': 'Role', 'type': 'select', 'options': ['admin', 'user']}
        ]
        dialog = InputDialog(parent=self, title="Add User", fields=fields)
        if dialog.result:
            create_user(dialog.result['email'], dialog.result['role'])
    """
    
    def __init__(
        self,
        parent,
        title: str,
        fields: List[Dict],
        submit_text: str = "Submit",
        on_submit: Callable = None
    ):
        """Initialize the input dialog."""
        # Calculate height based on number of fields
        height = 150 + (len(fields) * 70)
        super().__init__(parent, title, width=450, height=min(height, 500))
        
        self.fields = fields
        self.submit_text = submit_text
        self.on_submit = on_submit
        self.entries: Dict[str, Dict] = {}
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Scrollable container for fields
        scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=COLORS['border']
        )
        scroll_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create each field
        for field in self.fields:
            self._create_field(scroll_frame, field)
        
        # Error message label
        self.error_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['error']
        )
        self.error_label.pack(pady=(0, 10))
        
        # Button container
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
            corner_radius=RADIUS['md'],
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
            corner_radius=RADIUS['md'],
            command=self._on_submit
        )
        submit_btn.pack(side="right", expand=True, padx=5)
    
    def _create_field(self, parent, field: Dict):
        """
        Create a single input field.
        
        Args:
            parent: Parent container
            field: Field definition dictionary
        """
        key = field.get('key', '')
        label = field.get('label', key)
        field_type = field.get('type', 'text')
        required = field.get('required', False)
        options = field.get('options', [])
        default = field.get('default', '')
        placeholder = field.get('placeholder', '')
        
        # Label with required indicator
        label_text = f"{label} {'*' if required else ''}"
        label_widget = ctk.CTkLabel(
            parent,
            text=label_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        label_widget.pack(anchor="w", pady=(10, 5))
        
        # Create appropriate widget based on type
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
                height=40,
                corner_radius=RADIUS['md']
            )
            if default:
                entry.set(default)
                
        elif field_type == 'number':
            entry = ctk.CTkEntry(
                parent,
                placeholder_text=placeholder,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=400,
                height=40,
                corner_radius=RADIUS['md']
            )
            if default:
                entry.insert(0, str(default))
                
        elif field_type == 'password':
            entry = ctk.CTkEntry(
                parent,
                placeholder_text=placeholder,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=400,
                height=40,
                corner_radius=RADIUS['md'],
                show="•"
            )
            
        elif field_type == 'textarea':
            entry = ctk.CTkTextbox(
                parent,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=400,
                height=100,
                corner_radius=RADIUS['md']
            )
            if default:
                entry.insert("1.0", default)
                
        else:  # text (default)
            entry = ctk.CTkEntry(
                parent,
                placeholder_text=placeholder,
                fg_color=COLORS['input_bg'],
                border_color=COLORS['border'],
                width=400,
                height=40,
                corner_radius=RADIUS['md']
            )
            if default:
                entry.insert(0, default)
        
        entry.pack(anchor="w")
        self.entries[key] = {
            'widget': entry,
            'type': field_type,
            'required': required
        }
    
    def _get_values(self) -> Dict[str, str]:
        """
        Get all field values.
        
        Returns:
            Dictionary mapping field keys to their values
        """
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
        """
        Validate all required fields.
        
        Returns:
            Tuple of (is_valid, result_or_error_message)
        """
        values = self._get_values()
        
        for key, entry_info in self.entries.items():
            if entry_info['required'] and not values.get(key, '').strip():
                return False, f"Field '{key}' is required"
        
        return True, values
    
    def _on_submit(self):
        """Handle submit button click."""
        valid, result = self._validate()
        
        if not valid:
            self.error_label.configure(text=result)
            return
        
        if self.on_submit:
            self.on_submit(result)
        
        self.close(result)


class MessageDialog(Dialog):
    """
    Simple Message Dialog for alerts and notifications.
    
    Displays a message with an icon and OK button.
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Message to display
        message_type: Type of message ('info', 'success', 'warning', 'error')
        button_text: Text for OK button (default: "OK")
        
    Example:
        MessageDialog(
            parent=self,
            title="Success",
            message="User created successfully!",
            message_type="success"
        )
    """
    
    # Icon and color mapping for message types
    MESSAGE_ICONS = {
        'info': ('ℹ️', COLORS['success']),
        'success': ('✅', COLORS['success']),
        'warning': ('⚠️', COLORS['warning']),
        'error': ('❌', COLORS['error']),
    }
    
    def __init__(
        self,
        parent,
        title: str,
        message: str,
        message_type: str = "info",
        button_text: str = "OK"
    ):
        """Initialize the message dialog."""
        super().__init__(parent, title, width=400, height=200)
        
        self.message = message
        self.message_type = message_type
        self.button_text = button_text
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Get icon and color for message type
        icon, color = self.MESSAGE_ICONS.get(
            self.message_type,
            ('ℹ️', COLORS['text_primary'])
        )
        
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
            corner_radius=RADIUS['md'],
            command=lambda: self.close(True)
        )
        ok_btn.pack(pady=(10, 30))


class LoadingDialog(Dialog):
    """
    Loading Dialog with spinner animation.
    
    Displays a loading indicator while an operation is in progress.
    Cannot be closed by the user - must be closed programmatically.
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Loading message to display
        
    Example:
        # Show loading
        loading = LoadingDialog(parent=self, message="Processing...")
        
        # Do work...
        
        # Close loading
        loading.close()
    """
    
    def __init__(
        self,
        parent,
        title: str = "Loading",
        message: str = "Please wait..."
    ):
        """Initialize the loading dialog."""
        super().__init__(parent, title, width=300, height=150)
        
        self.message = message
        self._animation_running = True
        self._dot_count = 0
        
        # Prevent closing by user
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self._create_widgets()
        self._animate()
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Loading spinner (animated dots)
        self.spinner_label = ctk.CTkLabel(
            self,
            text="⏳",
            font=ctk.CTkFont(size=36)
        )
        self.spinner_label.pack(pady=(30, 10))
        
        # Message
        self.message_label = ctk.CTkLabel(
            self,
            text=self.message,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_secondary']
        )
        self.message_label.pack(pady=10)
    
    def _animate(self):
        """Animate the loading indicator."""
        if not self._animation_running:
            return
        
        # Cycle through loading dots
        dots = "." * (self._dot_count % 4)
        self.message_label.configure(text=f"{self.message}{dots}")
        self._dot_count += 1
        
        # Schedule next animation frame
        self.after(500, self._animate)
    
    def update_message(self, message: str):
        """
        Update the loading message.
        
        Args:
            message: New message to display
        """
        self.message = message
        self.message_label.configure(text=message)
    
    def close(self, result: Any = None):
        """Close the loading dialog."""
        self._animation_running = False
        super().close(result)


class ProgressDialog(Dialog):
    """
    Progress Dialog with progress bar.
    
    Displays a progress bar for long-running operations.
    
    Args:
        parent: Parent window
        title: Dialog title
        message: Progress message to display
        determinate: Whether progress is determinate (default: True)
        
    Example:
        # Show progress
        progress = ProgressDialog(parent=self, message="Uploading files...")
        
        # Update progress
        for i in range(100):
            progress.set_progress(i / 100)
            progress.update_message(f"Uploading file {i+1}/100")
        
        # Close
        progress.close()
    """
    
    def __init__(
        self,
        parent,
        title: str = "Progress",
        message: str = "Processing...",
        determinate: bool = True
    ):
        """Initialize the progress dialog."""
        super().__init__(parent, title, width=400, height=180)
        
        self.message = message
        self.determinate = determinate
        
        # Prevent closing by user
        self.protocol("WM_DELETE_WINDOW", lambda: None)
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create the dialog widgets."""
        # Message
        self.message_label = ctk.CTkLabel(
            self,
            text=self.message,
            font=ctk.CTkFont(size=14),
            text_color=COLORS['text_primary']
        )
        self.message_label.pack(pady=(30, 15))
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            self,
            width=350,
            height=12,
            fg_color=COLORS['bg_tertiary'],
            progress_color=COLORS['accent'],
            corner_radius=RADIUS['sm']
        )
        self.progress_bar.pack(pady=10)
        
        if self.determinate:
            self.progress_bar.set(0)
        else:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start()
        
        # Percentage label
        self.percent_label = ctk.CTkLabel(
            self,
            text="0%",
            font=ctk.CTkFont(size=12),
            text_color=COLORS['text_secondary']
        )
        if self.determinate:
            self.percent_label.pack(pady=(5, 20))
    
    def set_progress(self, value: float):
        """
        Set the progress value.
        
        Args:
            value: Progress value between 0 and 1
        """
        if self.determinate:
            self.progress_bar.set(value)
            self.percent_label.configure(text=f"{int(value * 100)}%")
    
    def update_message(self, message: str):
        """
        Update the progress message.
        
        Args:
            message: New message to display
        """
        self.message = message
        self.message_label.configure(text=message)
    
    def close(self, result: Any = None):
        """Close the progress dialog."""
        if not self.determinate:
            self.progress_bar.stop()
        super().close(result)
