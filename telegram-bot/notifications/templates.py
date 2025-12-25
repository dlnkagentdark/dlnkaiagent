"""
dLNk Telegram Bot - Message Templates

This module contains message templates for various notifications.
"""

from typing import Optional, List, Dict


class MessageTemplates:
    """
    Message templates for Telegram notifications.
    
    All templates use HTML formatting for Telegram.
    """
    
    # Severity icons
    SEVERITY_ICONS = {
        1: "ℹ️",   # Low
        2: "⚠️",   # Medium
        3: "🚨",   # High
        4: "🔴"    # Critical
    }
    
    @staticmethod
    def security_alert(
        title: str,
        message: str,
        severity: int,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        timestamp: str = ""
    ) -> str:
        """
        Generate security alert message.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Severity level (1-4)
            user_id: Related user ID
            ip_address: Related IP address
            timestamp: Alert timestamp
            
        Returns:
            Formatted HTML message
        """
        icon = MessageTemplates.SEVERITY_ICONS.get(severity, "ℹ️")
        severity_text = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}.get(severity, "Unknown")
        
        msg = f"""
🛡️ <b>Security Alert</b>

{icon} <b>{title}</b>

{message}

<b>Severity:</b> {severity_text}"""
        
        if user_id:
            msg += f"\n<b>User:</b> <code>{user_id}</code>"
        
        if ip_address:
            msg += f"\n<b>IP:</b> <code>{ip_address}</code>"
        
        msg += f"\n<b>Time:</b> {timestamp}"
        
        return msg.strip()
    
    @staticmethod
    def license_alert(
        event: str,
        license_key: str,
        user_id: str,
        license_type: Optional[str] = None,
        expires_at: Optional[str] = None,
        timestamp: str = ""
    ) -> str:
        """
        Generate license alert message.
        
        Args:
            event: Event type
            license_key: License key
            user_id: User ID
            license_type: License type
            expires_at: Expiration date
            timestamp: Alert timestamp
            
        Returns:
            Formatted HTML message
        """
        event_icons = {
            "created": "🆕",
            "activated": "✅",
            "expired": "⏰",
            "revoked": "🚫",
            "extended": "⏳",
            "transferred": "🔄"
        }
        icon = event_icons.get(event.lower(), "🔑")
        
        msg = f"""
🔑 <b>License Event</b>

{icon} <b>{event.title()}</b>

<b>License:</b> <code>{license_key}</code>
<b>User:</b> {user_id}"""
        
        if license_type:
            msg += f"\n<b>Type:</b> {license_type}"
        
        if expires_at:
            msg += f"\n<b>Expires:</b> {expires_at}"
        
        msg += f"\n<b>Time:</b> {timestamp}"
        
        return msg.strip()
    
    @staticmethod
    def system_alert(
        title: str,
        message: str,
        severity: int,
        component: Optional[str] = None,
        metrics: Optional[Dict] = None,
        timestamp: str = ""
    ) -> str:
        """
        Generate system alert message.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Severity level
            component: System component
            metrics: System metrics
            timestamp: Alert timestamp
            
        Returns:
            Formatted HTML message
        """
        icon = MessageTemplates.SEVERITY_ICONS.get(severity, "ℹ️")
        
        msg = f"""
⚙️ <b>System Alert</b>

{icon} <b>{title}</b>

{message}"""
        
        if component:
            msg += f"\n\n<b>Component:</b> {component}"
        
        if metrics:
            msg += "\n\n<b>Metrics:</b>"
            for key, value in metrics.items():
                msg += f"\n├ {key}: <code>{value}</code>"
        
        msg += f"\n\n<b>Time:</b> {timestamp}"
        
        return msg.strip()
    
    @staticmethod
    def user_alert(
        event: str,
        user_id: str,
        username: Optional[str] = None,
        details: Optional[str] = None,
        timestamp: str = ""
    ) -> str:
        """
        Generate user alert message.
        
        Args:
            event: Event type
            user_id: User ID
            username: Username
            details: Additional details
            timestamp: Alert timestamp
            
        Returns:
            Formatted HTML message
        """
        event_icons = {
            "registered": "👤",
            "banned": "🚫",
            "unbanned": "✅",
            "login": "🔐",
            "logout": "🚪",
            "updated": "✏️"
        }
        icon = event_icons.get(event.lower(), "👤")
        
        msg = f"""
👥 <b>User Event</b>

{icon} <b>{event.title()}</b>

<b>User ID:</b> <code>{user_id}</code>"""
        
        if username:
            msg += f"\n<b>Username:</b> {username}"
        
        if details:
            msg += f"\n<b>Details:</b> {details}"
        
        msg += f"\n<b>Time:</b> {timestamp}"
        
        return msg.strip()
    
    @staticmethod
    def custom_alert(
        title: str,
        message: str,
        icon: str = "📢",
        timestamp: str = ""
    ) -> str:
        """
        Generate custom alert message.
        
        Args:
            title: Alert title
            message: Alert message
            icon: Custom icon
            timestamp: Alert timestamp
            
        Returns:
            Formatted HTML message
        """
        return f"""
{icon} <b>{title}</b>

{message}

<b>Time:</b> {timestamp}
        """.strip()
    
    @staticmethod
    def daily_summary(date: str, stats: Dict) -> str:
        """
        Generate daily summary message.
        
        Args:
            date: Summary date
            stats: Statistics dict
            
        Returns:
            Formatted HTML message
        """
        return f"""
📊 <b>Daily Summary - {date}</b>

<b>👥 Users:</b>
├ Total: <code>{stats.get('total_users', 0):,}</code>
├ New: <code>{stats.get('new_users', 0):,}</code>
└ Active: <code>{stats.get('active_users', 0):,}</code>

<b>🔑 Licenses:</b>
├ Total: <code>{stats.get('total_licenses', 0):,}</code>
├ New: <code>{stats.get('new_licenses', 0):,}</code>
└ Expired: <code>{stats.get('expired_licenses', 0):,}</code>

<b>🤖 AI Requests:</b> <code>{stats.get('ai_requests', 0):,}</code>

<b>⚠️ Alerts:</b> <code>{stats.get('security_alerts', 0)}</code>

<b>⏱️ Uptime:</b> <code>{stats.get('system_uptime', 'N/A')}</code>

<i>Generated automatically by dLNk Bot</i>
        """.strip()
    
    @staticmethod
    def expiring_licenses_alert(
        licenses: List[Dict],
        timestamp: str = ""
    ) -> str:
        """
        Generate expiring licenses alert.
        
        Args:
            licenses: List of expiring licenses
            timestamp: Alert timestamp
            
        Returns:
            Formatted HTML message
        """
        msg = f"""
⏰ <b>Expiring Licenses Alert</b>

The following licenses are expiring soon:

"""
        for i, lic in enumerate(licenses[:10], 1):
            msg += f"{i}. <code>{lic.get('key', 'N/A')}</code>\n"
            msg += f"   Owner: {lic.get('owner', 'N/A')} | Expires: {lic.get('expires_at', 'N/A')}\n\n"
        
        if len(licenses) > 10:
            msg += f"<i>...and {len(licenses) - 10} more</i>\n\n"
        
        msg += f"<b>Time:</b> {timestamp}"
        
        return msg.strip()
    
    @staticmethod
    def welcome_message(username: str, is_admin: bool = False) -> str:
        """
        Generate welcome message.
        
        Args:
            username: User's name
            is_admin: Whether user is admin
            
        Returns:
            Formatted HTML message
        """
        msg = f"""
🚀 <b>Welcome to dLNk Admin Bot</b>

Hello, {username}!

This bot helps you manage dLNk IDE licenses, users, and system monitoring.

Use /help to see available commands.
        """
        
        if is_admin:
            msg += "\n\n✅ <b>Admin access granted</b>"
        else:
            msg += "\n\n⚠️ <b>Note:</b> You are not registered as an admin."
        
        return msg.strip()
    
    @staticmethod
    def error_message(error: str, details: Optional[str] = None) -> str:
        """
        Generate error message.
        
        Args:
            error: Error description
            details: Additional details
            
        Returns:
            Formatted HTML message
        """
        msg = f"""
❌ <b>Error</b>

{error}
        """
        
        if details:
            msg += f"\n\n<b>Details:</b>\n<code>{details}</code>"
        
        return msg.strip()
    
    @staticmethod
    def success_message(action: str, details: Optional[str] = None) -> str:
        """
        Generate success message.
        
        Args:
            action: Completed action
            details: Additional details
            
        Returns:
            Formatted HTML message
        """
        msg = f"""
✅ <b>Success</b>

{action}
        """
        
        if details:
            msg += f"\n\n{details}"
        
        return msg.strip()
