#!/usr/bin/env python3
"""
Security Middleware for AI Bridge
=================================
Integrates Security Module with AI Bridge for prompt filtering and protection.

Author: dLNk Team (AI-08 Security)
Version: 1.0.0
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional, Tuple

# Add security module to path
security_path = Path(__file__).parent.parent.parent / "security"
if security_path.exists():
    sys.path.insert(0, str(security_path.parent))

logger = logging.getLogger('SecurityMiddleware')


class SecurityMiddleware:
    """
    Security Middleware for AI Bridge
    
    Provides:
    - Prompt filtering
    - Rate limiting
    - Activity logging
    - Anomaly detection
    """
    
    def __init__(self, enable_alerts: bool = True, telegram_config: Dict = None):
        """
        Initialize Security Middleware
        
        Args:
            enable_alerts: Enable Telegram alerts
            telegram_config: Telegram bot configuration
        """
        self.enabled = True
        self.prompt_filter = None
        self.rate_limiter = None
        self.activity_logger = None
        self.alert_manager = None
        
        self._initialize_components(enable_alerts, telegram_config)
    
    def _initialize_components(self, enable_alerts: bool, telegram_config: Dict):
        """Initialize security components"""
        try:
            # Try to import security module
            from security.prompt_filter import create_filter
            from security.anomaly import RateLimiter, RateLimitConfig
            from security.activity import ActivityLogger
            
            # Initialize prompt filter
            self.prompt_filter = create_filter()
            logger.info("Prompt filter initialized")
            
            # Initialize rate limiter
            config = RateLimitConfig(
                requests_per_minute=60,
                requests_per_hour=500,
                requests_per_day=5000
            )
            self.rate_limiter = RateLimiter(config)
            logger.info("Rate limiter initialized")
            
            # Initialize activity logger
            self.activity_logger = ActivityLogger(
                log_dir=str(Path.home() / ".dlnk-ide" / "logs")
            )
            logger.info("Activity logger initialized")
            
            # Initialize alert manager if enabled
            if enable_alerts and telegram_config:
                from security.alerts import AlertManager
                self.alert_manager = AlertManager(
                    telegram_bot_token=telegram_config.get('bot_token'),
                    telegram_chat_id=telegram_config.get('chat_id')
                )
                logger.info("Alert manager initialized")
            
            logger.info("Security middleware fully initialized")
            
        except ImportError as e:
            logger.warning(f"Security module not available: {e}")
            logger.warning("Running without security features")
            self.enabled = False
        except Exception as e:
            logger.error(f"Failed to initialize security: {e}")
            self.enabled = False
    
    def filter_prompt(
        self,
        prompt: str,
        user_id: str = "anonymous",
        ip_address: str = None,
        session_id: str = None
    ) -> Tuple[bool, Optional[str], Dict[str, Any]]:
        """
        Filter a prompt for security threats
        
        Args:
            prompt: The prompt to filter
            user_id: User identifier
            ip_address: Client IP address
            session_id: Session identifier
        
        Returns:
            Tuple of (allowed, blocked_response, metadata)
        """
        if not self.enabled or not self.prompt_filter:
            return True, None, {"security_enabled": False}
        
        try:
            result = self.prompt_filter.filter(
                prompt=prompt,
                user_id=user_id,
                ip_address=ip_address,
                session_id=session_id
            )
            
            metadata = {
                "security_enabled": True,
                "severity": result.severity,
                "allowed": result.allowed
            }
            
            if not result.allowed:
                metadata["reason"] = result.reason
                metadata["matched_pattern"] = result.matched_pattern
                
                # Log security event
                if self.activity_logger:
                    self.activity_logger.log_security_event(
                        user_id=user_id,
                        event="prompt_blocked",
                        severity=result.severity,
                        details={
                            "pattern": result.matched_pattern,
                            "reason": result.reason
                        },
                        ip_address=ip_address
                    )
                
                return False, result.response, metadata
            
            return True, None, metadata
            
        except Exception as e:
            logger.error(f"Error filtering prompt: {e}")
            return True, None, {"security_enabled": True, "error": str(e)}
    
    def check_rate_limit(
        self,
        user_id: str,
        ip_address: str = None
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check rate limit for a user
        
        Args:
            user_id: User identifier
            ip_address: Client IP address
        
        Returns:
            Tuple of (allowed, status_info)
        """
        if not self.enabled or not self.rate_limiter:
            return True, {"rate_limit_enabled": False}
        
        try:
            status = self.rate_limiter.check(user_id)
            
            info = {
                "rate_limit_enabled": True,
                "allowed": status.allowed,
                "remaining_minute": status.remaining_minute,
                "remaining_hour": status.remaining_hour,
                "remaining_day": status.remaining_day
            }
            
            if not status.allowed:
                info["message"] = status.message
                info["reset_time"] = status.reset_time
                
                # Log rate limit event
                if self.activity_logger:
                    self.activity_logger.log_security_event(
                        user_id=user_id,
                        event="rate_limit_exceeded",
                        severity=2,
                        details=info,
                        ip_address=ip_address
                    )
            
            return status.allowed, info
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            return True, {"rate_limit_enabled": True, "error": str(e)}
    
    def log_activity(
        self,
        user_id: str,
        action: str,
        details: Dict[str, Any] = None,
        ip_address: str = None,
        session_id: str = None
    ):
        """Log user activity"""
        if not self.enabled or not self.activity_logger:
            return
        
        try:
            self.activity_logger.log(
                user_id=user_id,
                action=action,
                details=details or {},
                ip_address=ip_address,
                session_id=session_id
            )
        except Exception as e:
            logger.error(f"Error logging activity: {e}")
    
    def send_alert(
        self,
        title: str,
        message: str,
        severity: int = 1
    ):
        """Send security alert"""
        if not self.enabled or not self.alert_manager:
            return
        
        try:
            self.alert_manager.send_alert(title, message, severity)
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get security statistics"""
        stats = {
            "enabled": self.enabled,
            "prompt_filter": {},
            "rate_limiter": {},
            "activity_logger": {}
        }
        
        if self.prompt_filter:
            stats["prompt_filter"] = self.prompt_filter.get_stats()
        
        if self.rate_limiter:
            stats["rate_limiter"] = self.rate_limiter.get_stats()
        
        if self.activity_logger:
            stats["activity_logger"] = self.activity_logger.get_stats()
        
        return stats


# Singleton instance
_middleware_instance: Optional[SecurityMiddleware] = None


def get_security_middleware(
    enable_alerts: bool = True,
    telegram_config: Dict = None
) -> SecurityMiddleware:
    """Get or create security middleware instance"""
    global _middleware_instance
    
    if _middleware_instance is None:
        _middleware_instance = SecurityMiddleware(
            enable_alerts=enable_alerts,
            telegram_config=telegram_config
        )
    
    return _middleware_instance


def filter_prompt(
    prompt: str,
    user_id: str = "anonymous",
    **kwargs
) -> Tuple[bool, Optional[str], Dict[str, Any]]:
    """Convenience function to filter prompt"""
    middleware = get_security_middleware()
    return middleware.filter_prompt(prompt, user_id, **kwargs)


def check_rate_limit(user_id: str, **kwargs) -> Tuple[bool, Dict[str, Any]]:
    """Convenience function to check rate limit"""
    middleware = get_security_middleware()
    return middleware.check_rate_limit(user_id, **kwargs)
