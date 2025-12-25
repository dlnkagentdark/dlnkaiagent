#!/usr/bin/env python3
"""
dLNk Admin Console - Components Package

This package provides reusable UI components for the admin console.
All components follow the dLNk Style Guide for consistent appearance.

Components:
    Navigation:
        - Sidebar: Navigation sidebar with menu items
        - Header: Page header with title and actions
    
    Data Display:
        - DataTable: Sortable, paginated data table
        - StatCard: Statistics card with icon and value
        - ChartPlaceholder: Placeholder for chart components
    
    Dialogs:
        - Dialog: Base dialog class
        - ConfirmDialog: Yes/No confirmation dialogs
        - InputDialog: Form input dialogs
        - MessageDialog: Simple message/alert dialogs
        - LoadingDialog: Loading indicator dialogs
        - ProgressDialog: Progress bar dialogs

Usage:
    from components import Sidebar, DataTable, ConfirmDialog
    
    # Create sidebar
    sidebar = Sidebar(parent, on_navigate=handle_nav)
    
    # Create data table
    table = DataTable(parent, columns=['Name', 'Email', 'Status'])
    table.set_data(users)
    
    # Show confirmation
    dialog = ConfirmDialog(parent, "Confirm", "Are you sure?")
    if dialog.result:
        # User confirmed
        pass

Author: AI-04 UI/UX Designer
Version: 1.1.0
Last Updated: December 2025
"""

# Navigation Components
from .sidebar import Sidebar
from .header import Header

# Data Display Components
from .table import DataTable
from .chart import StatCard, ChartPlaceholder

# Dialog Components
from .dialog import (
    Dialog,
    ConfirmDialog,
    InputDialog,
    MessageDialog,
    LoadingDialog,
    ProgressDialog
)

__all__ = [
    # Navigation
    'Sidebar',
    'Header',
    
    # Data Display
    'DataTable',
    'StatCard',
    'ChartPlaceholder',
    
    # Dialogs
    'Dialog',
    'ConfirmDialog',
    'InputDialog',
    'MessageDialog',
    'LoadingDialog',
    'ProgressDialog',
]

__version__ = '1.1.0'
