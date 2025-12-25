"""
dLNk Telegram Bot - Alert Sender

This module handles sending alerts and notifications to admins.
"""

import logging
from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

from .templates import MessageTemplates

if TYPE_CHECKING:
    from bot.bot import DLNkBot

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class AlertType(Enum):
    """Alert types"""
    SECURITY = "security"
    LICENSE = "license"
    SYSTEM = "system"
    USER = "user"
    CUSTOM = "custom"


class AlertSender:
    """
    Send alerts and notifications to admin via Telegram.
    
    This class provides methods for sending various types of alerts
    including security alerts, license notifications, and system alerts.
    """
    
    def __init__(self, bot: "DLNkBot"):
        """
        Initialize the alert sender.
        
        Args:
            bot: DLNkBot instance for sending messages
        """
        self.bot = bot
        self.templates = MessageTemplates()
        self._alert_history: List[dict] = []
    
    async def send_security_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[dict] = None
    ):
        """
        Send a security alert to admins.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity level
            user_id: Related user ID (optional)
            ip_address: Related IP address (optional)
            details: Additional details (optional)
        """
        alert_message = self.templates.security_alert(
            title=title,
            message=message,
            severity=severity.value,
            user_id=user_id,
            ip_address=ip_address,
            timestamp=self._get_timestamp()
        )
        
        await self.bot.send_alert(alert_message, severity=severity.value)
        
        self._log_alert(
            alert_type=AlertType.SECURITY,
            title=title,
            severity=severity,
            user_id=user_id
        )
        
        logger.info(f"Security alert sent: {title} (severity: {severity.name})")
    
    async def send_license_alert(
        self,
        event: str,
        license_key: str,
        user_id: str,
        license_type: Optional[str] = None,
        expires_at: Optional[str] = None
    ):
        """
        Send a license-related alert.
        
        Args:
            event: Event type (created, activated, expired, revoked, etc.)
            license_key: License key
            user_id: User ID
            license_type: License type (optional)
            expires_at: Expiration date (optional)
        """
        alert_message = self.templates.license_alert(
            event=event,
            license_key=license_key,
            user_id=user_id,
            license_type=license_type,
            expires_at=expires_at,
            timestamp=self._get_timestamp()
        )
        
        await self.bot.send_alert(alert_message, severity=AlertSeverity.LOW.value)
        
        self._log_alert(
            alert_type=AlertType.LICENSE,
            title=f"License {event}",
            severity=AlertSeverity.LOW,
            user_id=user_id
        )
        
        logger.info(f"License alert sent: {event} for {license_key}")
    
    async def send_system_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        component: Optional[str] = None,
        metrics: Optional[dict] = None
    ):
        """
        Send a system alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity level
            component: System component name (optional)
            metrics: System metrics (optional)
        """
        alert_message = self.templates.system_alert(
            title=title,
            message=message,
            severity=severity.value,
            component=component,
            metrics=metrics,
            timestamp=self._get_timestamp()
        )
        
        await self.bot.send_alert(alert_message, severity=severity.value)
        
        self._log_alert(
            alert_type=AlertType.SYSTEM,
            title=title,
            severity=severity
        )
        
        logger.info(f"System alert sent: {title} (severity: {severity.name})")
    
    async def send_user_alert(
        self,
        event: str,
        user_id: str,
        username: Optional[str] = None,
        details: Optional[str] = None
    ):
        """
        Send a user-related alert.
        
        Args:
            event: Event type (registered, banned, unbanned, etc.)
            user_id: User ID
            username: Username (optional)
            details: Additional details (optional)
        """
        alert_message = self.templates.user_alert(
            event=event,
            user_id=user_id,
            username=username,
            details=details,
            timestamp=self._get_timestamp()
        )
        
        await self.bot.send_alert(alert_message, severity=AlertSeverity.LOW.value)
        
        self._log_alert(
            alert_type=AlertType.USER,
            title=f"User {event}",
            severity=AlertSeverity.LOW,
            user_id=user_id
        )
        
        logger.info(f"User alert sent: {event} for user {user_id}")
    
    async def send_custom_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity = AlertSeverity.MEDIUM,
        icon: str = "📢"
    ):
        """
        Send a custom alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity level
            icon: Custom icon emoji
        """
        alert_message = self.templates.custom_alert(
            title=title,
            message=message,
            icon=icon,
            timestamp=self._get_timestamp()
        )
        
        await self.bot.send_alert(alert_message, severity=severity.value)
        
        self._log_alert(
            alert_type=AlertType.CUSTOM,
            title=title,
            severity=severity
        )
        
        logger.info(f"Custom alert sent: {title}")
    
    async def send_daily_summary(self):
        """Send daily summary to admins."""
        # TODO: Fetch actual stats from backend
        summary = self.templates.daily_summary(
            date=datetime.now().strftime("%Y-%m-%d"),
            stats={
                "total_users": 1234,
                "new_users": 45,
                "active_users": 456,
                "total_licenses": 987,
                "new_licenses": 23,
                "expired_licenses": 12,
                "ai_requests": 12345,
                "security_alerts": 2,
                "system_uptime": "99.9%"
            }
        )
        
        await self.bot.broadcast(summary)
        logger.info("Daily summary sent")
    
    async def send_expiring_licenses_alert(self, licenses: List[dict]):
        """
        Send alert about expiring licenses.
        
        Args:
            licenses: List of license dicts with key, owner, expires_at
        """
        if not licenses:
            return
        
        alert_message = self.templates.expiring_licenses_alert(
            licenses=licenses,
            timestamp=self._get_timestamp()
        )
        
        await self.bot.send_alert(alert_message, severity=AlertSeverity.MEDIUM.value)
        logger.info(f"Expiring licenses alert sent: {len(licenses)} licenses")
    
    def _get_timestamp(self) -> str:
        """Get current timestamp string."""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _log_alert(
        self,
        alert_type: AlertType,
        title: str,
        severity: AlertSeverity,
        user_id: Optional[str] = None
    ):
        """Log alert to history."""
        self._alert_history.append({
            "timestamp": self._get_timestamp(),
            "type": alert_type.value,
            "title": title,
            "severity": severity.value,
            "user_id": user_id
        })
        
        # Keep only last 100 alerts in memory
        if len(self._alert_history) > 100:
            self._alert_history = self._alert_history[-100:]
    
    def get_alert_history(self, limit: int = 10) -> List[dict]:
        """
        Get recent alert history.
        
        Args:
            limit: Maximum number of alerts to return
            
        Returns:
            List of alert dicts
        """
        return self._alert_history[-limit:]
    
    def get_alert_stats(self) -> dict:
        """
        Get alert statistics.
        
        Returns:
            Dict with alert counts by type and severity
        """
        stats = {
            "total": len(self._alert_history),
            "by_type": {},
            "by_severity": {}
        }
        
        for alert in self._alert_history:
            # Count by type
            alert_type = alert["type"]
            stats["by_type"][alert_type] = stats["by_type"].get(alert_type, 0) + 1
            
            # Count by severity
            severity = alert["severity"]
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
        
        return stats
