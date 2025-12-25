#!/usr/bin/env python3
"""
dLNk Admin Console - Configuration
"""

import os
from pathlib import Path

# Application Info
APP_NAME = "dLNk Admin Console"
APP_VERSION = "1.0.0"

# Paths
CONFIG_DIR = Path.home() / ".dlnk-ide"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# API Endpoints
API_BASE_URL = os.environ.get('DLNK_API_URL', 'http://localhost:5001')
API_ENDPOINTS = {
    'auth': f'{API_BASE_URL}/auth',
    'licenses': f'{API_BASE_URL}/api/licenses',
    'users': f'{API_BASE_URL}/api/users',
    'logs': f'{API_BASE_URL}/api/logs',
    'stats': f'{API_BASE_URL}/api/stats',
    'tokens': f'{API_BASE_URL}/api/tokens',
    'alerts': f'{API_BASE_URL}/api/alerts',
}

# Window Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 600

# Telegram Settings
TELEGRAM_BOT_TOKEN = os.environ.get('DLNK_TELEGRAM_BOT_TOKEN', '')
TELEGRAM_ADMIN_CHAT_ID = os.environ.get('DLNK_TELEGRAM_ADMIN_ID', '')

# Alert Thresholds
ALERT_THRESHOLDS = {
    'max_requests_per_minute': 30,
    'max_requests_per_hour': 500,
    'suspicious_activity_score': 0.7,
}
