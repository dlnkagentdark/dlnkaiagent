"""
dLNk Telegram Bot - Configuration
"""

import os
from typing import List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BotConfig:
    """Bot Configuration"""
    
    # Bot Token (from BotFather)
    BOT_TOKEN: str = os.getenv('DLNK_TELEGRAM_BOT_TOKEN', '')
    
    # Admin Chat IDs (who can use admin commands)
    @staticmethod
    def get_admin_chat_ids() -> List[int]:
        ids_str = os.getenv('DLNK_ADMIN_CHAT_IDS', '')
        return [int(id.strip()) for id in ids_str.split(',') if id.strip().isdigit()]
    
    ADMIN_CHAT_IDS: List[int] = property(lambda self: BotConfig.get_admin_chat_ids())


class APIConfig:
    """Backend API Configuration"""
    
    # Backend API URL
    BACKEND_URL: str = os.getenv('DLNK_BACKEND_URL', 'http://localhost:8000')
    
    # API Timeout (seconds)
    API_TIMEOUT: int = int(os.getenv('DLNK_API_TIMEOUT', '30'))
    
    # API Key for authentication
    API_KEY: str = os.getenv('DLNK_API_KEY', '')


class AlertConfig:
    """Alert Configuration"""
    
    # Enable/Disable alerts
    ENABLED: bool = os.getenv('DLNK_ALERT_ENABLED', 'true').lower() == 'true'
    
    # Severity threshold (1=low, 2=medium, 3=high, 4=critical)
    SEVERITY_THRESHOLD: int = int(os.getenv('DLNK_ALERT_THRESHOLD', '2'))
    
    # Alert types
    SECURITY_ALERTS: bool = os.getenv('DLNK_SECURITY_ALERTS', 'true').lower() == 'true'
    LICENSE_ALERTS: bool = os.getenv('DLNK_LICENSE_ALERTS', 'true').lower() == 'true'
    SYSTEM_ALERTS: bool = os.getenv('DLNK_SYSTEM_ALERTS', 'true').lower() == 'true'


class RateLimitConfig:
    """Rate Limiting Configuration"""
    
    # Messages per minute per user
    MESSAGES_PER_MINUTE: int = int(os.getenv('DLNK_RATE_LIMIT', '30'))
    
    # Time window in seconds
    TIME_WINDOW: int = int(os.getenv('DLNK_RATE_WINDOW', '60'))
    
    # Cooldown after rate limit hit (seconds)
    COOLDOWN: int = int(os.getenv('DLNK_RATE_COOLDOWN', '60'))


class DatabaseConfig:
    """Local Database Configuration"""
    
    # Database path
    DB_PATH: Path = Path(os.getenv('DLNK_BOT_DB_PATH', str(Path.home() / '.dlnk-ide' / 'telegram_bot.db')))
    
    # Ensure directory exists
    @classmethod
    def ensure_db_dir(cls):
        cls.DB_PATH.parent.mkdir(parents=True, exist_ok=True)


class LogConfig:
    """Logging Configuration"""
    
    # Log level
    LEVEL: str = os.getenv('DLNK_LOG_LEVEL', 'INFO')
    
    # Log format
    FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Log file (optional)
    LOG_FILE: Optional[str] = os.getenv('DLNK_LOG_FILE')


# Convenience access
BOT_TOKEN = BotConfig.BOT_TOKEN
ADMIN_CHAT_IDS = BotConfig.get_admin_chat_ids()
BACKEND_API_URL = APIConfig.BACKEND_URL
ALERT_ENABLED = AlertConfig.ENABLED
ALERT_SEVERITY_THRESHOLD = AlertConfig.SEVERITY_THRESHOLD
RATE_LIMIT_MESSAGES = RateLimitConfig.MESSAGES_PER_MINUTE
RATE_LIMIT_WINDOW = RateLimitConfig.TIME_WINDOW
