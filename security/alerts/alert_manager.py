#!/usr/bin/env python3
"""
Alert Manager
จัดการการแจ้งเตือน Security
"""

import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import threading
import queue

logger = logging.getLogger('AlertManager')


class AlertSeverity(Enum):
    """ระดับความรุนแรง"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Alert:
    """โครงสร้างข้อมูล Alert"""
    id: str
    timestamp: str
    title: str
    message: str
    severity: int
    source: str = "security"
    user_id: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[str] = None


@dataclass
class AlertConfig:
    """การตั้งค่า Alert"""
    enabled: bool = True
    min_severity: int = 1  # Minimum severity to send
    cooldown_seconds: int = 60  # Prevent spam
    max_alerts_per_hour: int = 50
    store_alerts: bool = True
    max_stored_alerts: int = 1000


class AlertManager:
    """
    Manage security alerts
    """
    
    def __init__(
        self,
        config: AlertConfig = None,
        telegram_alert=None,
        email_alert=None
    ):
        self.config = config or AlertConfig()
        self.telegram_alert = telegram_alert
        self.email_alert = email_alert
        
        # Alert storage
        self.alerts: List[Alert] = []
        
        # Rate limiting
        self.alert_times: List[datetime] = []
        self.last_alert_by_type: Dict[str, datetime] = {}
        
        # Alert queue for async processing
        self.alert_queue: queue.Queue = queue.Queue()
        
        # Callbacks
        self.callbacks: List[Callable[[Alert], None]] = []
        
        # Lock
        self._lock = threading.Lock()
        
        # Alert counter
        self._alert_counter = 0
        
        # Statistics
        self.stats = {
            "total_alerts": 0,
            "sent_alerts": 0,
            "suppressed_alerts": 0,
            "acknowledged_alerts": 0,
        }
        
        # Severity icons
        self.severity_icons = {
            1: "ℹ️",   # Low
            2: "⚠️",   # Medium
            3: "🚨",   # High
            4: "🔴"    # Critical
        }
    
    def _generate_id(self) -> str:
        """Generate unique alert ID"""
        self._alert_counter += 1
        return f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self._alert_counter:04d}"
    
    def _check_rate_limit(self) -> bool:
        """Check if we can send more alerts"""
        now = datetime.now()
        hour_ago = now - timedelta(hours=1)
        
        # Clean old entries
        self.alert_times = [t for t in self.alert_times if t > hour_ago]
        
        return len(self.alert_times) < self.config.max_alerts_per_hour
    
    def _check_cooldown(self, alert_type: str) -> bool:
        """Check cooldown for alert type"""
        if alert_type not in self.last_alert_by_type:
            return True
        
        last_time = self.last_alert_by_type[alert_type]
        cooldown = timedelta(seconds=self.config.cooldown_seconds)
        
        return datetime.now() - last_time > cooldown
    
    def send_alert(
        self,
        title: str,
        message: str,
        severity: int = 1,
        source: str = "security",
        user_id: str = None,
        details: Dict[str, Any] = None,
        force: bool = False
    ) -> Optional[Alert]:
        """
        Send a security alert
        
        Args:
            title: Alert title
            message: Alert message
            severity: 1-4 (low to critical)
            source: Source of alert
            user_id: Related user ID
            details: Additional details
            force: Force send even if rate limited
        
        Returns:
            Alert object if sent
        """
        with self._lock:
            self.stats["total_alerts"] += 1
            
            # Check if enabled
            if not self.config.enabled:
                return None
            
            # Check minimum severity
            if severity < self.config.min_severity:
                self.stats["suppressed_alerts"] += 1
                return None
            
            # Check rate limit (unless forced or critical)
            if not force and severity < 4:
                if not self._check_rate_limit():
                    logger.warning("Alert rate limit exceeded")
                    self.stats["suppressed_alerts"] += 1
                    return None
                
                alert_type = f"{source}:{title}"
                if not self._check_cooldown(alert_type):
                    logger.debug(f"Alert cooldown active for: {alert_type}")
                    self.stats["suppressed_alerts"] += 1
                    return None
                
                self.last_alert_by_type[alert_type] = datetime.now()
            
            # Create alert
            alert = Alert(
                id=self._generate_id(),
                timestamp=datetime.now().isoformat(),
                title=title,
                message=message,
                severity=severity,
                source=source,
                user_id=user_id,
                details=details
            )
            
            # Store alert
            if self.config.store_alerts:
                self.alerts.append(alert)
                if len(self.alerts) > self.config.max_stored_alerts:
                    self.alerts = self.alerts[-self.config.max_stored_alerts:]
            
            # Track for rate limiting
            self.alert_times.append(datetime.now())
            
            # Send via channels
            self._dispatch_alert(alert)
            
            self.stats["sent_alerts"] += 1
            
            logger.info(f"Alert sent: [{severity}] {title}")
            
            return alert
    
    def _dispatch_alert(self, alert: Alert):
        """Dispatch alert to all channels"""
        icon = self.severity_icons.get(alert.severity, "ℹ️")
        formatted_message = f"{icon} *{alert.title}*\n\n{alert.message}"
        
        if alert.user_id:
            formatted_message += f"\n\nUser: {alert.user_id}"
        
        # Send via Telegram
        if self.telegram_alert:
            try:
                self.telegram_alert.send_alert_sync(
                    title=alert.title,
                    message=alert.message,
                    severity=alert.severity
                )
            except Exception as e:
                logger.error(f"Failed to send Telegram alert: {e}")
        
        # Send via Email (if configured)
        if self.email_alert and alert.severity >= 3:
            try:
                self.email_alert.send(
                    subject=f"[Security Alert] {alert.title}",
                    body=formatted_message
                )
            except Exception as e:
                logger.error(f"Failed to send email alert: {e}")
        
        # Call callbacks
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Alert callback error: {e}")
    
    def add_callback(self, callback: Callable[[Alert], None]):
        """Add alert callback"""
        self.callbacks.append(callback)
    
    def acknowledge(self, alert_id: str, acknowledged_by: str = "admin") -> bool:
        """Acknowledge an alert"""
        with self._lock:
            for alert in self.alerts:
                if alert.id == alert_id:
                    alert.acknowledged = True
                    alert.acknowledged_by = acknowledged_by
                    alert.acknowledged_at = datetime.now().isoformat()
                    self.stats["acknowledged_alerts"] += 1
                    logger.info(f"Alert acknowledged: {alert_id}")
                    return True
            return False
    
    def get_alerts(
        self,
        severity: int = None,
        acknowledged: bool = None,
        limit: int = 100
    ) -> List[Alert]:
        """Get alerts"""
        with self._lock:
            alerts = self.alerts.copy()
            
            if severity is not None:
                alerts = [a for a in alerts if a.severity >= severity]
            
            if acknowledged is not None:
                alerts = [a for a in alerts if a.acknowledged == acknowledged]
            
            return alerts[-limit:]
    
    def get_unacknowledged(self) -> List[Alert]:
        """Get unacknowledged alerts"""
        return self.get_alerts(acknowledged=False)
    
    def get_critical_alerts(self) -> List[Alert]:
        """Get critical alerts"""
        return self.get_alerts(severity=4)
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics"""
        stats = self.stats.copy()
        stats["pending_alerts"] = len(self.get_unacknowledged())
        stats["critical_alerts"] = len(self.get_critical_alerts())
        return stats
    
    def clear_old_alerts(self, days: int = 7):
        """Clear old alerts"""
        with self._lock:
            cutoff = (datetime.now() - timedelta(days=days)).isoformat()
            self.alerts = [a for a in self.alerts if a.timestamp > cutoff]
    
    # Convenience methods for different severity levels
    
    def info(self, title: str, message: str, **kwargs):
        """Send info alert"""
        return self.send_alert(title, message, severity=1, **kwargs)
    
    def warning(self, title: str, message: str, **kwargs):
        """Send warning alert"""
        return self.send_alert(title, message, severity=2, **kwargs)
    
    def high(self, title: str, message: str, **kwargs):
        """Send high severity alert"""
        return self.send_alert(title, message, severity=3, **kwargs)
    
    def critical(self, title: str, message: str, **kwargs):
        """Send critical alert"""
        return self.send_alert(title, message, severity=4, force=True, **kwargs)
