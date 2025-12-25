#!/usr/bin/env python3
"""
Telegram Alert System
Send security alerts to admin via Telegram
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger('TelegramAlert')


@dataclass
class TelegramConfig:
    """การตั้งค่า Telegram"""
    bot_token: str
    chat_id: str
    enabled: bool = True
    parse_mode: str = "Markdown"
    disable_notification: bool = False


class TelegramAlert:
    """
    Send alerts via Telegram
    """
    
    def __init__(self, config: TelegramConfig = None):
        if config:
            self.config = config
        else:
            # Load from environment
            self.config = TelegramConfig(
                bot_token=os.environ.get('DLNK_TELEGRAM_BOT_TOKEN', ''),
                chat_id=os.environ.get('DLNK_TELEGRAM_ADMIN_ID', ''),
                enabled=bool(os.environ.get('DLNK_TELEGRAM_BOT_TOKEN'))
            )
        
        self.api_url = f"https://api.telegram.org/bot{self.config.bot_token}"
        
        # Severity icons
        self.severity_icons = {
            1: "ℹ️",   # Low
            2: "⚠️",   # Medium
            3: "🚨",   # High
            4: "🔴"    # Critical
        }
        
        # Statistics
        self.stats = {
            "total_sent": 0,
            "successful": 0,
            "failed": 0,
        }
    
    async def send_alert(
        self,
        title: str,
        message: str,
        severity: int = 1,
        parse_mode: str = None
    ) -> bool:
        """
        Send alert to Telegram
        
        Args:
            title: Alert title
            message: Alert message
            severity: 1-4 (low to critical)
            parse_mode: Markdown or HTML
        
        Returns:
            True if sent successfully
        """
        if not self.config.enabled:
            logger.debug("Telegram alerts disabled")
            return False
        
        if not self.config.bot_token or not self.config.chat_id:
            logger.warning("Telegram not configured")
            return False
        
        self.stats["total_sent"] += 1
        
        # Format message with severity indicator
        icon = self.severity_icons.get(severity, "ℹ️")
        full_message = f"{icon} *{title}*\n\n{message}"
        
        # Add timestamp
        full_message += f"\n\n_Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}_"
        
        try:
            import aiohttp
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/sendMessage",
                    json={
                        'chat_id': self.config.chat_id,
                        'text': full_message,
                        'parse_mode': parse_mode or self.config.parse_mode,
                        'disable_notification': self.config.disable_notification and severity < 3
                    }
                ) as response:
                    if response.status == 200:
                        self.stats["successful"] += 1
                        logger.info(f"Telegram alert sent: {title}")
                        return True
                    else:
                        self.stats["failed"] += 1
                        error_text = await response.text()
                        logger.error(f"Failed to send Telegram alert: {error_text}")
                        return False
                        
        except ImportError:
            # Fallback to requests if aiohttp not available
            return self._send_sync(full_message, parse_mode)
        except Exception as e:
            self.stats["failed"] += 1
            logger.error(f"Error sending Telegram alert: {e}")
            return False
    
    def _send_sync(self, message: str, parse_mode: str = None) -> bool:
        """Synchronous send using requests"""
        try:
            import requests
            
            response = requests.post(
                f"{self.api_url}/sendMessage",
                json={
                    'chat_id': self.config.chat_id,
                    'text': message,
                    'parse_mode': parse_mode or self.config.parse_mode,
                    'disable_notification': self.config.disable_notification
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.stats["successful"] += 1
                return True
            else:
                self.stats["failed"] += 1
                logger.error(f"Telegram API error: {response.text}")
                return False
                
        except Exception as e:
            self.stats["failed"] += 1
            logger.error(f"Error sending Telegram alert: {e}")
            return False
    
    def send_alert_sync(
        self,
        title: str,
        message: str,
        severity: int = 1
    ) -> bool:
        """Synchronous wrapper for send_alert"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If already in async context, use thread
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.send_alert(title, message, severity)
                    )
                    return future.result(timeout=10)
            else:
                return asyncio.run(self.send_alert(title, message, severity))
        except Exception as e:
            logger.error(f"Error in sync send: {e}")
            # Fallback to direct sync
            icon = self.severity_icons.get(severity, "ℹ️")
            full_message = f"{icon} *{title}*\n\n{message}"
            return self._send_sync(full_message)
    
    async def send_document(
        self,
        document_path: str,
        caption: str = None
    ) -> bool:
        """Send document to Telegram"""
        if not self.config.enabled:
            return False
        
        try:
            import aiohttp
            
            with open(document_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('chat_id', self.config.chat_id)
                data.add_field('document', f)
                if caption:
                    data.add_field('caption', caption)
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_url}/sendDocument",
                        data=data
                    ) as response:
                        return response.status == 200
                        
        except Exception as e:
            logger.error(f"Error sending document: {e}")
            return False
    
    async def send_photo(
        self,
        photo_path: str,
        caption: str = None
    ) -> bool:
        """Send photo to Telegram"""
        if not self.config.enabled:
            return False
        
        try:
            import aiohttp
            
            with open(photo_path, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('chat_id', self.config.chat_id)
                data.add_field('photo', f)
                if caption:
                    data.add_field('caption', caption)
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.api_url}/sendPhoto",
                        data=data
                    ) as response:
                        return response.status == 200
                        
        except Exception as e:
            logger.error(f"Error sending photo: {e}")
            return False
    
    def test_connection(self) -> bool:
        """Test Telegram connection"""
        try:
            import requests
            
            response = requests.get(
                f"{self.api_url}/getMe",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    bot_info = data.get('result', {})
                    logger.info(f"Telegram connected: @{bot_info.get('username')}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics"""
        return self.stats.copy()


def create_telegram_alert(
    bot_token: str = None,
    chat_id: str = None
) -> TelegramAlert:
    """
    Create TelegramAlert instance
    
    Usage:
        from security.alerts import create_telegram_alert
        alert = create_telegram_alert()
        alert.send_alert_sync("Test", "Hello!")
    """
    config = TelegramConfig(
        bot_token=bot_token or os.environ.get('DLNK_TELEGRAM_BOT_TOKEN', ''),
        chat_id=chat_id or os.environ.get('DLNK_TELEGRAM_ADMIN_ID', ''),
        enabled=True
    )
    return TelegramAlert(config)
