"""
dLNk License System Configuration
การตั้งค่าระบบ License และ Authentication
"""

import os
import secrets
from pathlib import Path

class Config:
    """การตั้งค่าหลัก"""
    
    # Base Directory
    BASE_DIR = Path(__file__).parent
    DATA_DIR = Path.home() / ".dlnk-ide"
    
    # Database
    DATABASE_PATH = str(DATA_DIR / "dlnk_license.db")
    
    # Encryption
    MASTER_SECRET = os.environ.get('DLNK_MASTER_SECRET', b"dLNk-AI-TOP-SECRET-MASTER-KEY-2025")
    if isinstance(MASTER_SECRET, str):
        MASTER_SECRET = MASTER_SECRET.encode()
    SALT = b"dlnk-static-salt-v2"
    
    # License Settings
    LICENSE_PREFIX = "DLNK"
    DEFAULT_TRIAL_DAYS = 14
    DEFAULT_PRO_DAYS = 365
    DEFAULT_ENTERPRISE_DAYS = 365
    
    # Session Settings
    SESSION_SECRET_KEY = os.environ.get('DLNK_SESSION_SECRET', secrets.token_hex(32))
    SESSION_LIFETIME_HOURS = 24
    OFFLINE_GRACE_DAYS = 7
    
    # Security Settings
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    MIN_PASSWORD_LENGTH = 8
    REQUIRE_SPECIAL_CHAR = True
    
    # 2FA Settings
    ENABLE_2FA = True
    TOTP_ISSUER = "dLNk IDE"
    
    # API Settings
    API_HOST = os.environ.get('DLNK_API_HOST', '0.0.0.0')
    API_PORT = int(os.environ.get('DLNK_API_PORT', 8088))
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS = 100
    RATE_LIMIT_WINDOW = 60  # seconds
    
    # Feature Definitions
    FEATURES = {
        'trial': ['ai_chat', 'basic_code_assist'],
        'pro': ['ai_chat', 'code_complete', 'history', 'dark_mode', 'priority_support'],
        'enterprise': ['ai_chat', 'code_complete', 'history', 'dark_mode', 'priority_support', 
                       'unlimited', 'api_access', 'custom_branding', 'admin_panel']
    }
    
    # Admin API URL (for registration)
    ADMIN_API_URL = os.environ.get('DLNK_ADMIN_API', 'http://localhost:8089')
    
    @classmethod
    def init_directories(cls):
        """สร้างโฟลเดอร์ที่จำเป็น"""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        return cls.DATA_DIR


class DevelopmentConfig(Config):
    """การตั้งค่าสำหรับ Development"""
    DEBUG = True
    LOG_LEVEL = "DEBUG"


class ProductionConfig(Config):
    """การตั้งค่าสำหรับ Production"""
    DEBUG = False
    LOG_LEVEL = "INFO"
    
    # Override with environment variables
    MASTER_SECRET = os.environ.get('DLNK_MASTER_SECRET', Config.MASTER_SECRET)
    if isinstance(MASTER_SECRET, str):
        MASTER_SECRET = MASTER_SECRET.encode()


def get_config():
    """Get configuration based on environment"""
    env = os.environ.get('DLNK_ENV', 'development')
    if env == 'production':
        return ProductionConfig
    return DevelopmentConfig
