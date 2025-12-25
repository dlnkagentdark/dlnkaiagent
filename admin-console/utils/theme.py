#!/usr/bin/env python3
"""
dLNk Admin Console - Theme Configuration

This module defines the visual theme for the dLNk Admin Console,
including colors, fonts, and status indicators. All values are
aligned with the dLNk IDE Style Guide (ui-design/STYLE_GUIDE.md).

Usage:
    from utils.theme import COLORS, FONTS, STATUS_COLORS
    
    # Apply background color
    widget.configure(fg_color=COLORS['bg_primary'])
    
    # Apply font
    label.configure(font=FONTS['heading'])

Author: AI-04 UI/UX Designer
Version: 1.1.0
Last Updated: December 2025
"""

# =============================================================================
# COLOR PALETTE
# =============================================================================
# All colors are derived from the dLNk IDE Style Guide
# Reference: ui-design/STYLE_GUIDE.md

COLORS = {
    # Primary Background Colors
    'bg_primary': '#1a1a2e',      # Main background - Dark Blue-Black
    'bg_secondary': '#16213e',    # Panels, sidebars - Darker Blue
    'bg_tertiary': '#0f3460',     # Highlights, selections - Deep Blue
    
    # Accent Colors
    'accent': '#e94560',          # Primary accent - Red-Pink
    'accent_secondary': '#533483', # Secondary accent - Purple
    
    # Semantic Colors
    'success': '#00d9ff',         # Success states - Cyan
    'warning': '#ffc107',         # Warning states - Yellow
    'error': '#ff4757',           # Error states - Red
    
    # Text Colors
    'text_primary': '#ffffff',    # Primary text - White
    'text_secondary': '#a0a0a0',  # Secondary text - Gray
    'text_muted': '#6c757d',      # Muted/disabled text - Dark Gray
    'text_link': '#00d9ff',       # Links - Cyan
    
    # Border & UI Elements
    'border': '#2d2d44',          # Borders, dividers
    'hover': '#c73e54',           # Hover state for accent
    'card_bg': '#242444',         # Card backgrounds
    'sidebar_bg': '#0f0f1a',      # Sidebar background
    'input_bg': '#1a1a3e',        # Input field background
    
    # Additional UI Colors
    'scrollbar': '#3d3d5c',       # Scrollbar track
    'scrollbar_thumb': '#5d5d7c', # Scrollbar thumb
    'tooltip_bg': '#0f3460',      # Tooltip background
    'overlay': 'rgba(0, 0, 0, 0.5)', # Modal overlay
}

# =============================================================================
# FONT CONFIGURATION
# =============================================================================
# Font tuples for CustomTkinter: (family, size, weight)

FONTS = {
    # Display Fonts
    'display': ('Segoe UI', 48, 'bold'),   # Logo, hero text
    'title': ('Segoe UI', 24, 'bold'),     # Page titles
    'subtitle': ('Segoe UI', 18, 'normal'), # Section subtitles
    
    # Heading Fonts
    'heading': ('Segoe UI', 16, 'bold'),   # Section headers
    'subheading': ('Segoe UI', 14, 'bold'), # Card headers
    
    # Body Fonts
    'body': ('Segoe UI', 14, 'normal'),    # Regular text
    'body_small': ('Segoe UI', 13, 'normal'), # Smaller body text
    'small': ('Segoe UI', 12, 'normal'),   # Labels, captions
    'tiny': ('Segoe UI', 11, 'normal'),    # Badges, metadata
    
    # Special Fonts
    'code': ('Consolas', 12, 'normal'),    # Code, monospace
    'code_large': ('Consolas', 14, 'normal'), # Larger code
    'button': ('Segoe UI', 14, 'bold'),    # Button text
    'button_small': ('Segoe UI', 12, 'bold'), # Small button text
}

# =============================================================================
# STATUS COLORS
# =============================================================================
# Colors for various status indicators

STATUS_COLORS = {
    # License Status
    'active': COLORS['success'],      # Active/valid
    'expired': COLORS['warning'],     # Expired
    'revoked': COLORS['error'],       # Revoked
    'trial': '#9b59b6',               # Trial period
    
    # User Status
    'online': COLORS['success'],      # Online
    'offline': COLORS['text_muted'],  # Offline
    'blocked': COLORS['error'],       # Blocked
    'pending': COLORS['warning'],     # Pending approval
    
    # Action Status
    'success': COLORS['success'],     # Success
    'error': COLORS['error'],         # Error
    'warning': COLORS['warning'],     # Warning
    'info': COLORS['success'],        # Info
}

# =============================================================================
# SEVERITY COLORS
# =============================================================================
# Colors for log severity and alert levels

SEVERITY_COLORS = {
    'critical': COLORS['error'],       # Critical - Red
    'high': '#ff6b6b',                 # High - Light Red
    'warning': COLORS['warning'],      # Warning - Yellow
    'medium': '#ffa502',               # Medium - Orange
    'info': COLORS['success'],         # Info - Cyan
    'low': COLORS['text_secondary'],   # Low - Gray
    'debug': '#6c757d',                # Debug - Dark Gray
}

# =============================================================================
# SPACING CONSTANTS
# =============================================================================
# Consistent spacing values

SPACING = {
    'xs': 4,    # Extra small
    'sm': 8,    # Small
    'md': 16,   # Medium
    'lg': 24,   # Large
    'xl': 32,   # Extra large
    '2xl': 48,  # 2x Extra large
    '3xl': 64,  # 3x Extra large
}

# =============================================================================
# BORDER RADIUS
# =============================================================================
# Consistent border radius values

RADIUS = {
    'sm': 4,    # Small elements
    'md': 8,    # Buttons, inputs
    'lg': 12,   # Cards
    'xl': 16,   # Modals
    '2xl': 24,  # Large containers
    'full': 9999, # Pills, circles
}

# =============================================================================
# ANIMATION DURATIONS
# =============================================================================
# Transition timing values (in milliseconds)

ANIMATION = {
    'fast': 150,    # Hover states
    'normal': 250,  # Panel transitions
    'slow': 400,    # Page transitions
}

# =============================================================================
# ICON SIZES
# =============================================================================
# Standard icon sizes

ICON_SIZES = {
    'xs': 12,   # Tiny icons
    'sm': 16,   # Small icons
    'md': 20,   # Medium icons
    'lg': 24,   # Large icons
    'xl': 32,   # Extra large icons
    '2xl': 48,  # Display icons
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_status_color(status: str) -> str:
    """
    Get the color for a given status.
    
    Args:
        status: Status string (e.g., 'active', 'expired', 'blocked')
        
    Returns:
        Hex color string
        
    Example:
        >>> color = get_status_color('active')
        >>> print(color)  # '#00d9ff'
    """
    return STATUS_COLORS.get(status.lower(), COLORS['text_secondary'])


def get_severity_color(severity: str) -> str:
    """
    Get the color for a given severity level.
    
    Args:
        severity: Severity string (e.g., 'critical', 'warning', 'info')
        
    Returns:
        Hex color string
        
    Example:
        >>> color = get_severity_color('critical')
        >>> print(color)  # '#ff4757'
    """
    return SEVERITY_COLORS.get(severity.lower(), COLORS['text_secondary'])


def apply_theme(widget, style: str = 'default'):
    """
    Apply theme styling to a widget.
    
    Args:
        widget: CustomTkinter widget to style
        style: Style preset ('default', 'card', 'sidebar', 'input')
        
    Example:
        >>> apply_theme(my_frame, 'card')
    """
    styles = {
        'default': {
            'fg_color': COLORS['bg_primary'],
        },
        'card': {
            'fg_color': COLORS['card_bg'],
            'corner_radius': RADIUS['lg'],
        },
        'sidebar': {
            'fg_color': COLORS['sidebar_bg'],
        },
        'input': {
            'fg_color': COLORS['input_bg'],
            'border_color': COLORS['border'],
            'corner_radius': RADIUS['md'],
        },
    }
    
    if style in styles:
        for key, value in styles[style].items():
            try:
                widget.configure(**{key: value})
            except Exception:
                pass
