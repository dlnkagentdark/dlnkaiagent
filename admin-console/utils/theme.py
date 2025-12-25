#!/usr/bin/env python3
"""
dLNk Admin Console - Theme Colors
"""

# Color Theme (matching dLNk IDE)
COLORS = {
    'bg_primary': '#1a1a2e',
    'bg_secondary': '#16213e',
    'bg_tertiary': '#0f3460',
    'accent': '#e94560',
    'accent_secondary': '#533483',
    'success': '#00d9ff',
    'warning': '#ffc107',
    'error': '#ff4757',
    'text_primary': '#ffffff',
    'text_secondary': '#a0a0a0',
    'border': '#2d2d44',
    'hover': '#c73e54',
    'card_bg': '#242444',
    'sidebar_bg': '#0f0f1a',
    'input_bg': '#1a1a3e',
}

# Font Settings
FONTS = {
    'title': ('Segoe UI', 24, 'bold'),
    'subtitle': ('Segoe UI', 18, 'normal'),
    'heading': ('Segoe UI', 16, 'bold'),
    'body': ('Segoe UI', 14, 'normal'),
    'small': ('Segoe UI', 12, 'normal'),
    'code': ('Consolas', 12, 'normal'),
}

# Status Colors
STATUS_COLORS = {
    'active': COLORS['success'],
    'expired': COLORS['warning'],
    'revoked': COLORS['error'],
    'blocked': COLORS['error'],
    'pending': COLORS['warning'],
    'success': COLORS['success'],
    'error': COLORS['error'],
}

# Severity Colors
SEVERITY_COLORS = {
    'critical': COLORS['error'],
    'warning': COLORS['warning'],
    'info': COLORS['success'],
    'low': COLORS['text_secondary'],
}
