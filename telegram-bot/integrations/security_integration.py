#!/usr/bin/env python3
"""
Security Integration for Telegram Bot
======================================
Connects Telegram Bot with Security Module for real-time alerts.

This module provides:
- Security alert receiver from Security Module
- Alert formatting and forwarding to admins
- Alert acknowledgment handling
- Security statistics reporting

Author: dLNk Team (AI-10 Integration)
Version: 1.0.0
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Add security module to path
security_path = Path(__file__).parent.parent.parent / "security"
if security_path.exists():
    sys.path.insert(0, str(security_path.parent))

logger = logging.getLogger('SecurityIntegration')


class SecurityEventType(Enum):
    """Types of security events"""
    PROMPT_BLOCKED = "prompt_blocked"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    ANOMALY_DETECTED = "anomaly_detected"
    BRUTE_FORCE_ATTEMPT = "brute_force_attempt"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    EMERGENCY = "emergency"


@dataclass
class SecurityEvent:
    """Security event data structure"""
    event_id: str
    event_type: SecurityEventType
    timestamp: str
    severity: int  # 1-4
    title: str
    message: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class SecurityIntegration:
    """
    Integration layer between Telegram Bot and Security Module.
    
    Receives security events from the Security Module and forwards
    them to admins via Telegram Bot.
    """
    
    def __init__(self, bot_instance=None):
        """
        Initialize Security Integration.
        
        Args:
            bot_instance: DLNkBot instance for sending messages
        """
        self.bot = bot_instance
        self.security_module = None
        self.alert_manager = None
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._running = False
        self._task: Optional[asyncio.Task] = None
        
        # Event handlers
        self._event_handlers: Dict[SecurityEventType, List[Callable]] = {
            event_type: [] for event_type in SecurityEventType
        }
        
        # Statistics
        self.stats = {
            "events_received": 0,
            "events_forwarded": 0,
            "events_failed": 0,
            "by_type": {},
            "by_severity": {}
        }
        
        # Severity icons
        self.severity_icons = {
            1: "ℹ️",   # Low
            2: "⚠️",   # Medium
            3: "🚨",   # High
            4: "🔴"    # Critical
        }
        
        # Initialize connection to security module
        self._initialize_security_module()
    
    def _initialize_security_module(self):
        """Initialize connection to security module"""
        try:
            from security.alerts import AlertManager, create_telegram_alert
            from security import SecurityManager
            
            # Get security manager instance
            self.security_module = SecurityManager()
            
            # Register callback for security events
            if hasattr(self.security_module, 'alert_manager'):
                self.alert_manager = self.security_module.alert_manager
                self.alert_manager.add_callback(self._on_security_alert)
                logger.info("Connected to Security Module AlertManager")
            
            logger.info("Security Integration initialized successfully")
            
        except ImportError as e:
            logger.warning(f"Security module not available: {e}")
            logger.info("Running in standalone mode - will receive events via API")
        except Exception as e:
            logger.error(f"Failed to initialize security module: {e}")
    
    def set_bot(self, bot_instance):
        """Set bot instance for sending messages"""
        self.bot = bot_instance
        logger.info("Bot instance set for Security Integration")
    
    async def start(self):
        """Start the event processing loop"""
        if self._running:
            return
        
        self._running = True
        self._task = asyncio.create_task(self._process_events())
        logger.info("Security Integration started")
    
    async def stop(self):
        """Stop the event processing loop"""
        self._running = False
        
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        
        logger.info("Security Integration stopped")
    
    async def _process_events(self):
        """Process events from the queue"""
        while self._running:
            try:
                event = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=1.0
                )
                await self._handle_event(event)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def _handle_event(self, event: SecurityEvent):
        """Handle a security event"""
        self.stats["events_received"] += 1
        
        # Update type stats
        event_type = event.event_type.value
        self.stats["by_type"][event_type] = self.stats["by_type"].get(event_type, 0) + 1
        
        # Update severity stats
        self.stats["by_severity"][event.severity] = \
            self.stats["by_severity"].get(event.severity, 0) + 1
        
        # Call registered handlers
        for handler in self._event_handlers.get(event.event_type, []):
            try:
                await handler(event)
            except Exception as e:
                logger.error(f"Event handler error: {e}")
        
        # Forward to Telegram
        if self.bot:
            try:
                await self._forward_to_telegram(event)
                self.stats["events_forwarded"] += 1
            except Exception as e:
                logger.error(f"Failed to forward event to Telegram: {e}")
                self.stats["events_failed"] += 1
    
    async def _forward_to_telegram(self, event: SecurityEvent):
        """Forward security event to Telegram admins"""
        if not self.bot:
            return
        
        # Format message
        icon = self.severity_icons.get(event.severity, "ℹ️")
        severity_name = ["", "Low", "Medium", "High", "Critical"][event.severity]
        
        message = f"""
{icon} <b>Security Alert</b>

<b>Type:</b> {event.event_type.value.replace('_', ' ').title()}
<b>Severity:</b> {severity_name}
<b>Time:</b> {event.timestamp}

<b>{event.title}</b>
{event.message}
"""
        
        if event.user_id:
            message += f"\n<b>User:</b> <code>{event.user_id}</code>"
        
        if event.ip_address:
            message += f"\n<b>IP:</b> <code>{event.ip_address}</code>"
        
        if event.details:
            details_str = "\n".join(f"  • {k}: {v}" for k, v in event.details.items())
            message += f"\n\n<b>Details:</b>\n{details_str}"
        
        message += f"\n\n<i>Event ID: {event.event_id}</i>"
        
        # Send alert
        await self.bot.send_alert(
            message=message,
            severity=event.severity,
            parse_mode="HTML"
        )
    
    def _on_security_alert(self, alert):
        """Callback for security module alerts"""
        try:
            # Convert alert to SecurityEvent
            event = SecurityEvent(
                event_id=alert.id if hasattr(alert, 'id') else f"SEC-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                event_type=self._map_alert_type(alert),
                timestamp=alert.timestamp if hasattr(alert, 'timestamp') else datetime.now().isoformat(),
                severity=alert.severity if hasattr(alert, 'severity') else 2,
                title=alert.title if hasattr(alert, 'title') else "Security Alert",
                message=alert.message if hasattr(alert, 'message') else str(alert),
                user_id=alert.user_id if hasattr(alert, 'user_id') else None,
                details=alert.details if hasattr(alert, 'details') else None
            )
            
            # Add to queue
            asyncio.create_task(self._event_queue.put(event))
            
        except Exception as e:
            logger.error(f"Error processing security alert: {e}")
    
    def _map_alert_type(self, alert) -> SecurityEventType:
        """Map alert source to event type"""
        source = getattr(alert, 'source', 'security')
        
        if 'prompt' in source.lower():
            return SecurityEventType.PROMPT_BLOCKED
        elif 'rate' in source.lower():
            return SecurityEventType.RATE_LIMIT_EXCEEDED
        elif 'anomaly' in source.lower():
            return SecurityEventType.ANOMALY_DETECTED
        elif 'brute' in source.lower():
            return SecurityEventType.BRUTE_FORCE_ATTEMPT
        elif 'emergency' in source.lower():
            return SecurityEventType.EMERGENCY
        else:
            return SecurityEventType.SUSPICIOUS_ACTIVITY
    
    # Public API for receiving events
    
    async def receive_event(
        self,
        event_type: str,
        title: str,
        message: str,
        severity: int = 2,
        user_id: str = None,
        ip_address: str = None,
        details: Dict[str, Any] = None
    ):
        """
        Receive a security event from external source.
        
        This method can be called by other components to send
        security events to the Telegram Bot.
        
        Args:
            event_type: Type of event (e.g., 'prompt_blocked')
            title: Event title
            message: Event message
            severity: Severity level (1-4)
            user_id: Related user ID
            ip_address: Related IP address
            details: Additional details
        """
        try:
            event_type_enum = SecurityEventType(event_type)
        except ValueError:
            event_type_enum = SecurityEventType.SUSPICIOUS_ACTIVITY
        
        event = SecurityEvent(
            event_id=f"EXT-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            event_type=event_type_enum,
            timestamp=datetime.now().isoformat(),
            severity=severity,
            title=title,
            message=message,
            user_id=user_id,
            ip_address=ip_address,
            details=details
        )
        
        await self._event_queue.put(event)
    
    def register_handler(
        self,
        event_type: SecurityEventType,
        handler: Callable
    ):
        """Register a handler for specific event type"""
        self._event_handlers[event_type].append(handler)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get integration statistics"""
        return self.stats.copy()
    
    def get_recent_events(self, limit: int = 10) -> List[Dict]:
        """Get recent events (from security module if available)"""
        if self.alert_manager:
            return self.alert_manager.get_alerts(limit=limit)
        return []


# Singleton instance
_integration_instance: Optional[SecurityIntegration] = None


def get_security_integration(bot_instance=None) -> SecurityIntegration:
    """Get or create security integration instance"""
    global _integration_instance
    
    if _integration_instance is None:
        _integration_instance = SecurityIntegration(bot_instance)
    elif bot_instance:
        _integration_instance.set_bot(bot_instance)
    
    return _integration_instance


async def forward_security_event(
    event_type: str,
    title: str,
    message: str,
    severity: int = 2,
    **kwargs
):
    """Convenience function to forward security event"""
    integration = get_security_integration()
    await integration.receive_event(
        event_type=event_type,
        title=title,
        message=message,
        severity=severity,
        **kwargs
    )
