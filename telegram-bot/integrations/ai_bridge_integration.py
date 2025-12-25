#!/usr/bin/env python3
"""
AI Bridge Integration for Telegram Bot
=======================================
Connects Telegram Bot with AI Bridge for status monitoring and management.

This module provides:
- AI Bridge status monitoring
- Provider status checking
- Token status monitoring
- System health alerts

Author: dLNk Team (AI-10 Integration)
Version: 1.0.0
"""

import asyncio
import logging
import aiohttp
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger('AIBridgeIntegration')


@dataclass
class AIBridgeConfig:
    """Configuration for AI Bridge connection"""
    rest_url: str = "http://localhost:8766"
    ws_url: str = "ws://localhost:8765"
    timeout: int = 10
    retry_attempts: int = 3


@dataclass
class BridgeStatus:
    """AI Bridge status data"""
    running: bool
    token_valid: bool
    providers: Dict[str, Any]
    ws_stats: Dict[str, Any]
    rest_stats: Dict[str, Any]
    timestamp: str


class AIBridgeIntegration:
    """
    Integration layer between Telegram Bot and AI Bridge.
    
    Provides monitoring and management capabilities for AI Bridge
    through the Telegram Bot interface.
    """
    
    def __init__(self, config: AIBridgeConfig = None, bot_instance=None):
        """
        Initialize AI Bridge Integration.
        
        Args:
            config: AI Bridge connection configuration
            bot_instance: DLNkBot instance for sending messages
        """
        self.config = config or AIBridgeConfig()
        self.bot = bot_instance
        self._session: Optional[aiohttp.ClientSession] = None
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        
        # Status cache
        self._last_status: Optional[BridgeStatus] = None
        self._last_check: Optional[datetime] = None
        
        # Alert thresholds
        self.alert_thresholds = {
            "token_expiry_minutes": 30,  # Alert when token expires in 30 min
            "error_rate_percent": 10,    # Alert when error rate > 10%
            "response_time_ms": 5000,    # Alert when response time > 5s
        }
        
        # Statistics
        self.stats = {
            "checks_performed": 0,
            "alerts_sent": 0,
            "errors": 0
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
    
    def set_bot(self, bot_instance):
        """Set bot instance for sending alerts"""
        self.bot = bot_instance
        logger.info("Bot instance set for AI Bridge Integration")
    
    async def get_status(self) -> Optional[BridgeStatus]:
        """
        Get current AI Bridge status.
        
        Returns:
            BridgeStatus object or None if unavailable
        """
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.config.rest_url}/status") as response:
                if response.status == 200:
                    data = await response.json()
                    
                    status = BridgeStatus(
                        running=data.get('running', False),
                        token_valid=data.get('token_valid', False),
                        providers=data.get('providers', {}),
                        ws_stats=data.get('ws_server', {}),
                        rest_stats=data.get('rest_server', {}),
                        timestamp=datetime.now().isoformat()
                    )
                    
                    self._last_status = status
                    self._last_check = datetime.now()
                    self.stats["checks_performed"] += 1
                    
                    return status
                else:
                    logger.warning(f"AI Bridge returned status {response.status}")
                    return None
                    
        except aiohttp.ClientError as e:
            logger.error(f"Failed to connect to AI Bridge: {e}")
            self.stats["errors"] += 1
            return None
        except Exception as e:
            logger.error(f"Error getting AI Bridge status: {e}")
            self.stats["errors"] += 1
            return None
    
    async def get_providers(self) -> List[Dict[str, Any]]:
        """Get available AI providers"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.config.rest_url}/providers") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('providers', [])
                return []
                
        except Exception as e:
            logger.error(f"Error getting providers: {e}")
            return []
    
    async def get_token_status(self) -> Dict[str, Any]:
        """Get token manager status"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.config.rest_url}/token/status") as response:
                if response.status == 200:
                    return await response.json()
                return {"valid": False, "error": f"HTTP {response.status}"}
                
        except Exception as e:
            logger.error(f"Error getting token status: {e}")
            return {"valid": False, "error": str(e)}
    
    async def refresh_token(self) -> bool:
        """Request token refresh"""
        try:
            session = await self._get_session()
            
            async with session.post(f"{self.config.rest_url}/token/refresh") as response:
                if response.status == 200:
                    logger.info("Token refresh requested successfully")
                    return True
                else:
                    logger.warning(f"Token refresh failed: HTTP {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error refreshing token: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get AI Bridge statistics"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.config.rest_url}/stats") as response:
                if response.status == 200:
                    return await response.json()
                return {}
                
        except Exception as e:
            logger.error(f"Error getting stats: {e}")
            return {}
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on AI Bridge"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "bridge_online": False,
            "token_valid": False,
            "providers_available": 0,
            "issues": []
        }
        
        # Check bridge status
        status = await self.get_status()
        if status:
            result["bridge_online"] = status.running
            result["token_valid"] = status.token_valid
            result["providers_available"] = len([
                p for p in status.providers.values() 
                if p.get('available', False)
            ])
            
            # Check for issues
            if not status.running:
                result["issues"].append("AI Bridge is not running")
            
            if not status.token_valid:
                result["issues"].append("Token is invalid or expired")
            
            if result["providers_available"] == 0:
                result["issues"].append("No AI providers available")
            
            # Check error rates
            rest_stats = status.rest_stats
            if rest_stats:
                total = rest_stats.get('total_requests', 0)
                errors = rest_stats.get('errors', 0)
                if total > 0:
                    error_rate = (errors / total) * 100
                    if error_rate > self.alert_thresholds["error_rate_percent"]:
                        result["issues"].append(f"High error rate: {error_rate:.1f}%")
        else:
            result["issues"].append("Cannot connect to AI Bridge")
        
        return result
    
    # Monitoring
    
    async def start_monitoring(self, interval_seconds: int = 60):
        """Start background monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(
            self._monitor_loop(interval_seconds)
        )
        logger.info(f"AI Bridge monitoring started (interval: {interval_seconds}s)")
    
    async def stop_monitoring(self):
        """Stop background monitoring"""
        self._monitoring = False
        
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        
        logger.info("AI Bridge monitoring stopped")
    
    async def _monitor_loop(self, interval: int):
        """Background monitoring loop"""
        while self._monitoring:
            try:
                await self._check_and_alert()
                await asyncio.sleep(interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(interval)
    
    async def _check_and_alert(self):
        """Check status and send alerts if needed"""
        health = await self.health_check()
        
        if health["issues"] and self.bot:
            # Send alert for each issue
            for issue in health["issues"]:
                severity = 3 if "not running" in issue or "No AI providers" in issue else 2
                
                await self.bot.send_alert(
                    message=f"<b>AI Bridge Issue</b>\n\n{issue}",
                    severity=severity
                )
                self.stats["alerts_sent"] += 1
    
    # Telegram command helpers
    
    def format_status_message(self, status: BridgeStatus) -> str:
        """Format status for Telegram message"""
        if not status:
            return "❌ <b>AI Bridge Status</b>\n\nCannot connect to AI Bridge"
        
        # Status icon
        icon = "✅" if status.running else "❌"
        
        # Provider list
        providers_list = []
        for name, info in status.providers.items():
            p_icon = "🟢" if info.get('available', False) else "🔴"
            providers_list.append(f"  {p_icon} {name}")
        providers_str = "\n".join(providers_list) if providers_list else "  None"
        
        # Token status
        token_icon = "🔑" if status.token_valid else "🔒"
        token_status = "Valid" if status.token_valid else "Invalid/Expired"
        
        # Stats
        ws_stats = status.ws_stats
        rest_stats = status.rest_stats
        
        message = f"""
{icon} <b>AI Bridge Status</b>

<b>Running:</b> {"Yes" if status.running else "No"}
<b>Token:</b> {token_icon} {token_status}

<b>Providers:</b>
{providers_str}

<b>WebSocket Server:</b>
  • Connections: {ws_stats.get('active_connections', 0)}
  • Messages: {ws_stats.get('total_messages', 0)}

<b>REST API Server:</b>
  • Requests: {rest_stats.get('total_requests', 0)}
  • Errors: {rest_stats.get('errors', 0)}

<i>Last updated: {status.timestamp}</i>
"""
        return message
    
    def format_health_message(self, health: Dict[str, Any]) -> str:
        """Format health check for Telegram message"""
        # Overall status
        if not health["issues"]:
            icon = "✅"
            status = "Healthy"
        elif len(health["issues"]) <= 1:
            icon = "⚠️"
            status = "Warning"
        else:
            icon = "❌"
            status = "Critical"
        
        message = f"""
{icon} <b>AI Bridge Health Check</b>

<b>Status:</b> {status}
<b>Bridge Online:</b> {"Yes" if health["bridge_online"] else "No"}
<b>Token Valid:</b> {"Yes" if health["token_valid"] else "No"}
<b>Providers Available:</b> {health["providers_available"]}
"""
        
        if health["issues"]:
            issues_str = "\n".join(f"  • {issue}" for issue in health["issues"])
            message += f"\n<b>Issues:</b>\n{issues_str}"
        
        message += f"\n\n<i>Checked: {health['timestamp']}</i>"
        
        return message
    
    def get_integration_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return {
            **self.stats,
            "last_check": self._last_check.isoformat() if self._last_check else None,
            "monitoring_active": self._monitoring
        }


# Singleton instance
_integration_instance: Optional[AIBridgeIntegration] = None


def get_ai_bridge_integration(
    config: AIBridgeConfig = None,
    bot_instance=None
) -> AIBridgeIntegration:
    """Get or create AI Bridge integration instance"""
    global _integration_instance
    
    if _integration_instance is None:
        _integration_instance = AIBridgeIntegration(config, bot_instance)
    elif bot_instance:
        _integration_instance.set_bot(bot_instance)
    
    return _integration_instance
