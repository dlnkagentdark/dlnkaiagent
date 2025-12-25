#!/usr/bin/env python3
"""
dLNk Security Module Configuration
การตั้งค่าระบบ Security & Protection
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class SecurityConfig:
    """การตั้งค่าหลักของระบบ Security"""
    
    # Base paths
    BASE_DIR: Path = field(default_factory=lambda: Path.home() / ".dlnk-ide")
    LOG_DIR: Path = field(default_factory=lambda: Path.home() / ".dlnk-ide" / "logs")
    DB_DIR: Path = field(default_factory=lambda: Path.home() / ".dlnk-ide" / "db")
    
    # Database
    SECURITY_DB: str = "security.db"
    
    # Encryption
    ENCRYPTION_KEY_FILE: str = ".security_key"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_RETENTION_DAYS: int = 90
    ENCRYPT_LOGS: bool = True
    
    def __post_init__(self):
        # Ensure directories exist
        self.BASE_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.DB_DIR.mkdir(parents=True, exist_ok=True)


@dataclass
class PromptFilterConfig:
    """การตั้งค่า Prompt Filter"""
    
    # Blocked response message
    BLOCKED_RESPONSE: str = """⚠️ **คำถามนี้ถูกบล็อก**

คำถามของคุณเกี่ยวข้องกับการโจมตีระบบ dLNk ซึ่งไม่ได้รับอนุญาต

**สิ่งที่คุณสามารถถามได้:**
- คำถามเกี่ยวกับการเขียนโค้ด
- คำถามเกี่ยวกับ hacking/security (เป้าหมายอื่น)
- คำถามทั่วไปทุกประเภท

**สิ่งที่ไม่อนุญาต:**
- โจมตี dLNk, dLNk AI, หรือ Jetski
- ขโมย API Keys/Tokens ของระบบ
- Bypass License System

หากคุณคิดว่านี่เป็นข้อผิดพลาด กรุณาติดต่อ Admin"""
    
    # Enable/disable features
    ENABLE_PATTERN_MATCHING: bool = True
    ENABLE_KEYWORD_MATCHING: bool = True
    ENABLE_LEETSPEAK_DETECTION: bool = True
    
    # Alert settings
    ALERT_ON_BLOCK: bool = True
    ALERT_MIN_SEVERITY: int = 3  # Alert only on high/critical


@dataclass
class AnomalyConfig:
    """การตั้งค่า Anomaly Detection"""
    
    # Rate limiting
    MAX_REQUESTS_PER_MINUTE: int = 60
    MAX_REQUESTS_PER_HOUR: int = 500
    
    # Brute force detection
    MAX_FAILED_LOGINS: int = 5
    FAILED_LOGIN_WINDOW_MINUTES: int = 5
    
    # Blocked prompt threshold
    MAX_BLOCKED_PROMPTS: int = 3
    BLOCKED_PROMPT_WINDOW_MINUTES: int = 5
    
    # Anomaly score thresholds
    SCORE_THRESHOLD_WARNING: float = 1.5
    SCORE_THRESHOLD_CRITICAL: float = 2.0


@dataclass
class AlertConfig:
    """การตั้งค่า Alert System"""
    
    # Telegram settings
    TELEGRAM_BOT_TOKEN: str = field(
        default_factory=lambda: os.environ.get('DLNK_TELEGRAM_BOT_TOKEN', '')
    )
    TELEGRAM_ADMIN_CHAT_ID: str = field(
        default_factory=lambda: os.environ.get('DLNK_TELEGRAM_ADMIN_ID', '')
    )
    TELEGRAM_ENABLED: bool = True
    
    # Alert settings
    ALERT_COOLDOWN_SECONDS: int = 60  # Prevent spam
    MAX_ALERTS_PER_HOUR: int = 50
    
    # Severity levels
    SEVERITY_LOW: int = 1
    SEVERITY_MEDIUM: int = 2
    SEVERITY_HIGH: int = 3
    SEVERITY_CRITICAL: int = 4
    
    # Severity icons
    SEVERITY_ICONS: Dict[int, str] = field(default_factory=lambda: {
        1: "ℹ️",   # Low
        2: "⚠️",   # Medium
        3: "🚨",   # High
        4: "🔴"    # Critical
    })


@dataclass
class EncryptionConfig:
    """การตั้งค่า Encryption"""
    
    # Algorithm settings
    KEY_LENGTH: int = 32  # 256 bits
    SALT_LENGTH: int = 16
    ITERATIONS: int = 100000
    
    # File encryption
    CHUNK_SIZE: int = 64 * 1024  # 64KB
    
    # Token encryption
    TOKEN_EXPIRY_HOURS: int = 24


# Global configuration instances
security_config = SecurityConfig()
prompt_filter_config = PromptFilterConfig()
anomaly_config = AnomalyConfig()
alert_config = AlertConfig()
encryption_config = EncryptionConfig()
