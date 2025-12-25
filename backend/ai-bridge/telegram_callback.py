#!/usr/bin/env python3
"""
Telegram Callback for AI Bridge
================================
Sends events to Telegram Bot via webhook.

This module provides:
- Security event forwarding
- Status change notifications
- Error notifications

Author: dLNk Team (AI-10 Integration)
Version: 1.0.0
"""

import logging
import asyncio
import aiohttp
from typing import Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger('TelegramCallback')


@dataclass
class TelegramWebhookConfig:
    """Configuration for Telegram webhook"""
    webhook_url: str = "http://localhost:8089"
    timeout: int = 10
    enabled: bool = True


class TelegramCallback:
    """
    Send events to Telegram Bot via webhook.
    
    This class is used by AI Bridge to forward events
    to the Telegram Bot for admin notifications.
    """
    
    def __init__(self, config: TelegramWebhookConfig = None):
        """
        Initialize Telegram Callback.
        
        Args:
            config: Webhook configuration
        """
        self.config = config or TelegramWebhookConfig()
        self._session: Optional[aiohttp.ClientSession] = None
        
        # Statistics
        self.stats = {
            "events_sent": 0,
            "events_failed": 0
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout)
            )
        return self._session
    
    async def close(self):
        """Close HTTP session"""
        if self._session and not self._session.closed:
            await self._session.close()
    
    async def send_security_event(
        self,
        event_type: str,
        title: str,
        message: str,
        severity: int = 2,
        user_id: str = None,
        ip_address: str = None,
        details: Dict[str, Any] = None
    ) -> bool:
        """
        Send security event to Telegram Bot.
        
        Args:
            event_type: Type of security event
            title: Event title
            message: Event message
            severity: Severity level (1-4)
            user_id: Related user ID
            ip_address: Related IP address
            details: Additional details
        
        Returns:
            True if sent successfully
        """
        if not self.config.enabled:
            return False
        
        try:
            session = await self._get_session()
            
            payload = {
                "event_type": event_type,
                "title": title,
                "message": message,
                "severity": severity,
                "user_id": user_id,
                "ip_address": ip_address,
                "details": details
            }
            
            async with session.post(
                f"{self.config.webhook_url}/webhook/security",
                json=payload
            ) as response:
                if response.status == 200:
                    self.stats["events_sent"] += 1
                    logger.info(f"Security event sent: {event_type}")
                    return True
                else:
                    self.stats["events_failed"] += 1
                    logger.warning(f"Failed to send security event: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.stats["events_failed"] += 1
            logger.error(f"Error sending security event: {e}")
            return False
    
    async def send_bridge_event(
        self,
        event_type: str,
        title: str,
        message: str,
        severity: int = 1,
        provider: str = None,
        details: Dict[str, Any] = None
    ) -> bool:
        """
        Send AI Bridge event to Telegram Bot.
        
        Args:
            event_type: Type of event (status_change, error, etc.)
            title: Event title
            message: Event message
            severity: Severity level (1-4)
            provider: Related provider name
            details: Additional details
        
        Returns:
            True if sent successfully
        """
        if not self.config.enabled:
            return False
        
        try:
            session = await self._get_session()
            
            payload = {
                "event_type": event_type,
                "title": title,
                "message": message,
                "severity": severity,
                "provider": provider,
                "details": details
            }
            
            async with session.post(
                f"{self.config.webhook_url}/webhook/ai-bridge",
                json=payload
            ) as response:
                if response.status == 200:
                    self.stats["events_sent"] += 1
                    logger.info(f"Bridge event sent: {event_type}")
                    return True
                else:
                    self.stats["events_failed"] += 1
                    logger.warning(f"Failed to send bridge event: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            self.stats["events_failed"] += 1
            logger.error(f"Error sending bridge event: {e}")
            return False
    
    async def send_alert(
        self,
        title: str,
        message: str,
        severity: int = 2
    ) -> bool:
        """
        Send generic alert to Telegram Bot.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Severity level (1-4)
        
        Returns:
            True if sent successfully
        """
        if not self.config.enabled:
            return False
        
        try:
            session = await self._get_session()
            
            payload = {
                "title": title,
                "message": message,
                "severity": severity
            }
            
            async with session.post(
                f"{self.config.webhook_url}/webhook/alert",
                json=payload
            ) as response:
                if response.status == 200:
                    self.stats["events_sent"] += 1
                    return True
                else:
                    self.stats["events_failed"] += 1
                    return False
                    
        except Exception as e:
            self.stats["events_failed"] += 1
            logger.error(f"Error sending alert: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics"""
        return self.stats.copy()


# Singleton instance
_callback_instance: Optional[TelegramCallback] = None


def get_telegram_callback(config: TelegramWebhookConfig = None) -> TelegramCallback:
    """Get or create Telegram callback instance"""
    global _callback_instance
    
    if _callback_instance is None:
        _callback_instance = TelegramCallback(config)
    
    return _callback_instance


# Convenience functions

async def notify_security_event(
    event_type: str,
    title: str,
    message: str,
    **kwargs
) -> bool:
    """Send security event notification"""
    callback = get_telegram_callback()
    return await callback.send_security_event(
        event_type=event_type,
        title=title,
        message=message,
        **kwargs
    )


async def notify_bridge_event(
    event_type: str,
    title: str,
    message: str,
    **kwargs
) -> bool:
    """Send bridge event notification"""
    callback = get_telegram_callback()
    return await callback.send_bridge_event(
        event_type=event_type,
        title=title,
        message=message,
        **kwargs
    )


async def notify_alert(title: str, message: str, severity: int = 2) -> bool:
    """Send alert notification"""
    callback = get_telegram_callback()
    return await callback.send_alert(title, message, severity)
