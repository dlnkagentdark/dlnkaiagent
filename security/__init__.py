#!/usr/bin/env python3
"""
dLNk Security Module v1.0
ระบบ Security & Protection สำหรับ dLNk IDE

Usage:
    from security import SecuritySystem, get_security_system
    
    # Initialize
    security = get_security_system(
        telegram_bot_token='your_token',
        telegram_chat_id='your_chat_id'
    )
    
    # Filter prompt
    result = security.filter_prompt("user prompt here", user_id="user123")
    if result['allowed']:
        # Process prompt
        pass
    else:
        # Handle blocked prompt
        print(result['response'])
    
    # Check rate limit
    rate_status = security.check_rate_limit("user123")
    
    # Log activity
    security.log_activity("user123", "code_generation", {"model": "gpt-4"})

Modules:
    - prompt_filter: บล็อก Prompt อันตราย
    - activity: บันทึกกิจกรรมผู้ใช้
    - anomaly: ตรวจจับพฤติกรรมผิดปกติ
    - alerts: แจ้งเตือนผ่าน Telegram
    - encryption: เข้ารหัสข้อมูล
    - utils: ฟังก์ชันช่วยเหลือ
"""

__version__ = '1.0.0'
__author__ = 'dLNk Team'

# Main classes
from .main import (
    SecuritySystem,
    get_security_system,
    init_security
)

# Prompt Filter
from .prompt_filter import (
    PromptFilter,
    PromptFilterMiddleware,
    FilterResult,
    create_filter,
    integrate_with_ai_bridge
)

# Activity
from .activity import (
    ActivityLogger,
    ActivityTracker,
    ActivityStorage,
    ActivityLog,
    ActivityType
)

# Anomaly Detection
from .anomaly import (
    AnomalyDetector,
    AnomalyResult,
    RateLimiter,
    RateLimitStatus,
    BruteForceDetector,
    BruteForceStatus
)

# Alerts
from .alerts import (
    AlertManager,
    Alert,
    TelegramAlert,
    EmergencyShutdown,
    EmergencyLevel,
    create_telegram_alert
)

# Encryption
from .encryption import (
    TokenEncryption,
    ConfigEncryption,
    LogEncryption,
    SecureTokenStorage,
    SecureConfigManager
)

# Utils
from .utils import (
    hash_string,
    hash_file,
    generate_token,
    get_hwid,
    sanitize_input,
    mask_sensitive_data
)

# Configuration
from .config import (
    security_config,
    prompt_filter_config,
    anomaly_config,
    alert_config
)

__all__ = [
    # Version
    '__version__',
    
    # Main
    'SecuritySystem',
    'get_security_system',
    'init_security',
    
    # Prompt Filter
    'PromptFilter',
    'PromptFilterMiddleware',
    'FilterResult',
    'create_filter',
    'integrate_with_ai_bridge',
    
    # Activity
    'ActivityLogger',
    'ActivityTracker',
    'ActivityStorage',
    'ActivityLog',
    'ActivityType',
    
    # Anomaly
    'AnomalyDetector',
    'AnomalyResult',
    'RateLimiter',
    'RateLimitStatus',
    'BruteForceDetector',
    'BruteForceStatus',
    
    # Alerts
    'AlertManager',
    'Alert',
    'TelegramAlert',
    'EmergencyShutdown',
    'EmergencyLevel',
    'create_telegram_alert',
    
    # Encryption
    'TokenEncryption',
    'ConfigEncryption',
    'LogEncryption',
    'SecureTokenStorage',
    'SecureConfigManager',
    
    # Utils
    'hash_string',
    'hash_file',
    'generate_token',
    'get_hwid',
    'sanitize_input',
    'mask_sensitive_data',
    
    # Config
    'security_config',
    'prompt_filter_config',
    'anomaly_config',
    'alert_config',
]
