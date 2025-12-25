#!/usr/bin/env python3
"""
dLNk Production Configuration v2.0
===================================
ไฟล์กำหนดค่าสำหรับ Production Environment

คุณสมบัติ:
- Environment-based configuration
- Secure secrets management
- Multi-tier AI fallback
- Anonymization settings
- Cloud deployment ready
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from cryptography.fernet import Fernet

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('dLNk-Config')


@dataclass
class AIConfig:
    """การตั้งค่า AI Backend"""
    # Primary: Jetski (ฝังใน Antigravity)
    jetski_enabled: bool = True
    jetski_endpoint: str = "internal://antigravity/jetski"
    
    # Secondary: OpenAI-compatible (Fallback)
    openai_enabled: bool = True
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-4.1-mini"
    
    # Tertiary: Local LLM (Offline fallback)
    local_llm_enabled: bool = False
    local_llm_endpoint: str = "http://localhost:11434/api/generate"
    local_llm_model: str = "llama2"
    
    # Conversation Memory
    memory_enabled: bool = True
    max_context_tokens: int = 8192
    session_timeout_hours: int = 24


@dataclass
class SecurityConfig:
    """การตั้งค่าความปลอดภัย"""
    # Encryption
    secret_key: str = ""
    encryption_algorithm: str = "Fernet"
    
    # Authentication
    admin_password_hash: str = ""
    session_lifetime_hours: int = 8
    max_login_attempts: int = 5
    lockout_duration_minutes: int = 30
    require_2fa: bool = False
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window_seconds: int = 60
    
    # Self-Protection
    prompt_filter_enabled: bool = True
    block_self_attack: bool = True
    log_blocked_prompts: bool = True
    
    # Input Validation
    max_prompt_length: int = 32000
    sanitize_html: bool = True
    prevent_sql_injection: bool = True
    prevent_xss: bool = True


@dataclass
class AnonymizationConfig:
    """การตั้งค่าการปกปิดตัวตน"""
    enabled: bool = True
    
    # Tor Configuration
    use_tor: bool = True
    tor_control_port: int = 9051
    tor_socks_port: int = 9050
    rotate_ip_interval_minutes: int = 10
    
    # HWID Obfuscation
    obfuscate_hwid: bool = True
    hwid_rotation_enabled: bool = True
    
    # Traffic Encryption
    encrypt_all_traffic: bool = True
    use_ssl_pinning: bool = True
    
    # No Logging Policy
    log_real_ip: bool = False
    log_hwid: bool = False
    log_user_agent: bool = False


@dataclass
class CloudConfig:
    """การตั้งค่า Cloud Deployment"""
    # Serverless
    serverless_enabled: bool = False
    serverless_provider: str = "cloudflare"  # cloudflare, vercel, aws_lambda
    
    # Database
    database_type: str = "sqlite"  # sqlite, mysql, postgresql
    database_url: str = "sqlite:///dlnk.db"
    
    # CDN
    cdn_enabled: bool = False
    cdn_url: str = ""
    
    # Auto-scaling
    auto_scale_enabled: bool = False
    min_instances: int = 1
    max_instances: int = 10


@dataclass
class TelegramConfig:
    """การตั้งค่า Telegram Bot"""
    enabled: bool = True
    bot_token: str = ""
    admin_chat_ids: list = field(default_factory=list)
    webhook_enabled: bool = False
    webhook_url: str = ""
    
    # Commands
    allow_license_generation: bool = True
    allow_broadcast: bool = True
    allow_user_management: bool = True


@dataclass
class UIConfig:
    """การตั้งค่า UI/Branding"""
    app_name: str = "dLNk"
    app_version: str = "2.0.0"
    theme: str = "dark"  # dark, light, custom
    
    # Branding
    logo_path: str = "assets/dlnk_logo.png"
    icon_path: str = "assets/dlnk_icon.ico"
    primary_color: str = "#1a1a2e"
    accent_color: str = "#e94560"
    
    # Language
    default_language: str = "th"
    supported_languages: list = field(default_factory=lambda: ["th", "en"])


class DLNKProductionConfig:
    """
    dLNk Production Configuration Manager
    
    จัดการการตั้งค่าทั้งหมดสำหรับ Production Environment
    """
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path.home() / ".dlnk" / "config.json"
        
        # Initialize configs
        self.ai = AIConfig()
        self.security = SecurityConfig()
        self.anonymization = AnonymizationConfig()
        self.cloud = CloudConfig()
        self.telegram = TelegramConfig()
        self.ui = UIConfig()
        
        # Load from environment first
        self._load_from_environment()
        
        # Then load from file (overrides env)
        if self.config_path.exists():
            self._load_from_file()
        
        # Generate secret key if not set
        if not self.security.secret_key:
            self.security.secret_key = Fernet.generate_key().decode()
            logger.warning("Generated new secret key. Save this for production!")
    
    def _load_from_environment(self):
        """โหลดการตั้งค่าจาก Environment Variables"""
        # AI Config
        self.ai.openai_api_key = os.environ.get("OPENAI_API_KEY", "")
        self.ai.openai_base_url = os.environ.get("OPENAI_BASE_URL", self.ai.openai_base_url)
        
        # Security Config
        self.security.secret_key = os.environ.get("DLNK_SECRET_KEY", "")
        
        # Telegram Config
        self.telegram.bot_token = os.environ.get("DLNK_TELEGRAM_BOT_TOKEN", "")
        admin_ids = os.environ.get("DLNK_TELEGRAM_ADMIN_IDS", "")
        if admin_ids:
            self.telegram.admin_chat_ids = [int(x.strip()) for x in admin_ids.split(",")]
        
        # Cloud Config
        self.cloud.database_url = os.environ.get("DATABASE_URL", self.cloud.database_url)
        
        logger.info("Loaded configuration from environment variables")
    
    def _load_from_file(self):
        """โหลดการตั้งค่าจากไฟล์ JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Update each config section
            for key, value in data.get('ai', {}).items():
                if hasattr(self.ai, key):
                    setattr(self.ai, key, value)
            
            for key, value in data.get('security', {}).items():
                if hasattr(self.security, key):
                    setattr(self.security, key, value)
            
            for key, value in data.get('anonymization', {}).items():
                if hasattr(self.anonymization, key):
                    setattr(self.anonymization, key, value)
            
            for key, value in data.get('cloud', {}).items():
                if hasattr(self.cloud, key):
                    setattr(self.cloud, key, value)
            
            for key, value in data.get('telegram', {}).items():
                if hasattr(self.telegram, key):
                    setattr(self.telegram, key, value)
            
            for key, value in data.get('ui', {}).items():
                if hasattr(self.ui, key):
                    setattr(self.ui, key, value)
            
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    def save(self):
        """บันทึกการตั้งค่าลงไฟล์"""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'ai': self.ai.__dict__,
            'security': {k: v for k, v in self.security.__dict__.items() 
                        if k not in ['secret_key', 'admin_password_hash']},  # Don't save secrets
            'anonymization': self.anonymization.__dict__,
            'cloud': self.cloud.__dict__,
            'telegram': {k: v for k, v in self.telegram.__dict__.items() 
                        if k != 'bot_token'},  # Don't save token
            'ui': self.ui.__dict__,
        }
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved configuration to {self.config_path}")
    
    def validate(self) -> Dict[str, Any]:
        """ตรวจสอบความถูกต้องของการตั้งค่า"""
        issues = []
        warnings = []
        
        # Check AI config
        if not self.ai.jetski_enabled and not self.ai.openai_enabled and not self.ai.local_llm_enabled:
            issues.append("No AI backend enabled! At least one must be enabled.")
        
        if self.ai.openai_enabled and not self.ai.openai_api_key:
            warnings.append("OpenAI API key not set. OpenAI fallback will not work.")
        
        # Check Security config
        if not self.security.secret_key:
            issues.append("Secret key not set!")
        
        if self.security.secret_key == "changeme" or len(self.security.secret_key) < 32:
            warnings.append("Secret key is weak. Use a strong random key for production.")
        
        # Check Telegram config
        if self.telegram.enabled and not self.telegram.bot_token:
            warnings.append("Telegram bot token not set. Bot will not work.")
        
        if self.telegram.enabled and not self.telegram.admin_chat_ids:
            warnings.append("No admin chat IDs configured for Telegram bot.")
        
        # Check Anonymization config
        if self.anonymization.enabled and self.anonymization.use_tor:
            warnings.append("Tor must be installed and running for anonymization to work.")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
    
    def get_ai_providers(self) -> list:
        """รับรายการ AI providers ที่เปิดใช้งาน"""
        providers = []
        
        if self.ai.jetski_enabled:
            providers.append({
                'name': 'Jetski',
                'type': 'primary',
                'endpoint': self.ai.jetski_endpoint
            })
        
        if self.ai.openai_enabled:
            providers.append({
                'name': 'OpenAI',
                'type': 'secondary',
                'endpoint': self.ai.openai_base_url,
                'model': self.ai.openai_model
            })
        
        if self.ai.local_llm_enabled:
            providers.append({
                'name': 'Local LLM',
                'type': 'tertiary',
                'endpoint': self.ai.local_llm_endpoint,
                'model': self.ai.local_llm_model
            })
        
        return providers
    
    def print_summary(self):
        """แสดงสรุปการตั้งค่า"""
        print("=" * 60)
        print("dLNk Production Configuration Summary")
        print("=" * 60)
        
        print(f"\n📱 App: {self.ui.app_name} v{self.ui.app_version}")
        print(f"🎨 Theme: {self.ui.theme}")
        print(f"🌐 Language: {self.ui.default_language}")
        
        print(f"\n🤖 AI Providers:")
        for provider in self.get_ai_providers():
            print(f"   - {provider['name']} ({provider['type']})")
        
        print(f"\n🔒 Security:")
        print(f"   - Prompt Filter: {'✅' if self.security.prompt_filter_enabled else '❌'}")
        print(f"   - Rate Limiting: {self.security.rate_limit_requests}/min")
        print(f"   - 2FA Required: {'✅' if self.security.require_2fa else '❌'}")
        
        print(f"\n🕵️ Anonymization:")
        print(f"   - Enabled: {'✅' if self.anonymization.enabled else '❌'}")
        print(f"   - Tor: {'✅' if self.anonymization.use_tor else '❌'}")
        print(f"   - HWID Obfuscation: {'✅' if self.anonymization.obfuscate_hwid else '❌'}")
        
        print(f"\n☁️ Cloud:")
        print(f"   - Database: {self.cloud.database_type}")
        print(f"   - Serverless: {'✅' if self.cloud.serverless_enabled else '❌'}")
        
        print(f"\n📱 Telegram Bot:")
        print(f"   - Enabled: {'✅' if self.telegram.enabled else '❌'}")
        print(f"   - Admins: {len(self.telegram.admin_chat_ids)}")
        
        # Validation
        validation = self.validate()
        print(f"\n{'✅' if validation['valid'] else '❌'} Configuration Valid: {validation['valid']}")
        
        if validation['issues']:
            print("\n⛔ Issues:")
            for issue in validation['issues']:
                print(f"   - {issue}")
        
        if validation['warnings']:
            print("\n⚠️ Warnings:")
            for warning in validation['warnings']:
                print(f"   - {warning}")
        
        print("\n" + "=" * 60)


# ===== Production Ready Config Template =====

PRODUCTION_CONFIG_TEMPLATE = """
# dLNk Production Environment Variables
# =====================================
# Copy this to your .env file or set in your system

# === REQUIRED ===
DLNK_SECRET_KEY=your-32-char-secret-key-here-min
DLNK_TELEGRAM_BOT_TOKEN=your-telegram-bot-token
DLNK_TELEGRAM_ADMIN_IDS=123456789,987654321

# === OPTIONAL ===
# OpenAI Fallback (if Jetski unavailable)
OPENAI_API_KEY=your-openai-key-if-needed
OPENAI_BASE_URL=https://api.openai.com/v1

# Database (for cloud deployment)
DATABASE_URL=sqlite:///dlnk.db

# Tor (for anonymization)
TOR_CONTROL_PORT=9051
TOR_SOCKS_PORT=9050
"""


if __name__ == "__main__":
    # Demo
    config = DLNKProductionConfig()
    config.print_summary()
    
    print("\n📋 Production Environment Template:")
    print(PRODUCTION_CONFIG_TEMPLATE)
