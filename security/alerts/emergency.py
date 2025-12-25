#!/usr/bin/env python3
"""
Emergency Shutdown System
ระบบปิดฉุกเฉินเมื่อพบภัยคุกคามร้ายแรง
"""

import os
import sys
import logging
import signal
import threading
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger('EmergencyShutdown')


class EmergencyLevel(Enum):
    """ระดับฉุกเฉิน"""
    WARNING = 1      # Log and alert only
    RESTRICT = 2     # Restrict new connections
    LOCKDOWN = 3     # Block all non-admin access
    SHUTDOWN = 4     # Full system shutdown


@dataclass
class EmergencyEvent:
    """ข้อมูล Emergency Event"""
    timestamp: str
    level: EmergencyLevel
    reason: str
    triggered_by: str
    details: Optional[Dict[str, Any]] = None
    resolved: bool = False
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None


class EmergencyShutdown:
    """
    Emergency Shutdown System
    """
    
    def __init__(
        self,
        alert_manager=None,
        auto_shutdown_on_critical: bool = False
    ):
        self.alert_manager = alert_manager
        self.auto_shutdown_on_critical = auto_shutdown_on_critical
        
        # Current state
        self.current_level = EmergencyLevel.WARNING
        self.is_active = False
        
        # Event history
        self.events: List[EmergencyEvent] = []
        
        # Shutdown handlers
        self.shutdown_handlers: List[Callable[[], None]] = []
        
        # Lock
        self._lock = threading.Lock()
        
        # Statistics
        self.stats = {
            "total_events": 0,
            "warnings": 0,
            "restrictions": 0,
            "lockdowns": 0,
            "shutdowns": 0,
        }
    
    def trigger(
        self,
        level: EmergencyLevel,
        reason: str,
        triggered_by: str = "system",
        details: Dict[str, Any] = None
    ) -> EmergencyEvent:
        """
        Trigger emergency action
        
        Args:
            level: Emergency level
            reason: Reason for emergency
            triggered_by: Who/what triggered it
            details: Additional details
        
        Returns:
            EmergencyEvent
        """
        with self._lock:
            self.stats["total_events"] += 1
            
            event = EmergencyEvent(
                timestamp=datetime.now().isoformat(),
                level=level,
                reason=reason,
                triggered_by=triggered_by,
                details=details
            )
            
            self.events.append(event)
            
            # Update current level if higher
            if level.value > self.current_level.value:
                self.current_level = level
                self.is_active = True
            
            # Update stats
            if level == EmergencyLevel.WARNING:
                self.stats["warnings"] += 1
            elif level == EmergencyLevel.RESTRICT:
                self.stats["restrictions"] += 1
            elif level == EmergencyLevel.LOCKDOWN:
                self.stats["lockdowns"] += 1
            elif level == EmergencyLevel.SHUTDOWN:
                self.stats["shutdowns"] += 1
            
            # Log
            logger.critical(
                f"EMERGENCY [{level.name}]: {reason} "
                f"(triggered by: {triggered_by})"
            )
            
            # Alert
            self._send_alert(event)
            
            # Execute level-specific actions
            self._execute_actions(level, event)
            
            return event
    
    def _send_alert(self, event: EmergencyEvent):
        """Send emergency alert"""
        if not self.alert_manager:
            return
        
        level_icons = {
            EmergencyLevel.WARNING: "⚠️",
            EmergencyLevel.RESTRICT: "🔒",
            EmergencyLevel.LOCKDOWN: "🚫",
            EmergencyLevel.SHUTDOWN: "🔴"
        }
        
        icon = level_icons.get(event.level, "⚠️")
        
        self.alert_manager.critical(
            title=f"{icon} EMERGENCY: {event.level.name}",
            message=(
                f"Reason: {event.reason}\n"
                f"Triggered by: {event.triggered_by}\n"
                f"Time: {event.timestamp}"
            ),
            details=event.details
        )
    
    def _execute_actions(self, level: EmergencyLevel, event: EmergencyEvent):
        """Execute level-specific actions"""
        if level == EmergencyLevel.WARNING:
            # Just log and alert (already done)
            pass
        
        elif level == EmergencyLevel.RESTRICT:
            # Restrict new connections
            self._restrict_mode()
        
        elif level == EmergencyLevel.LOCKDOWN:
            # Block all non-admin access
            self._lockdown_mode()
        
        elif level == EmergencyLevel.SHUTDOWN:
            # Full system shutdown
            if self.auto_shutdown_on_critical:
                self._shutdown()
            else:
                logger.critical("SHUTDOWN triggered but auto_shutdown disabled")
    
    def _restrict_mode(self):
        """Enter restrict mode"""
        logger.warning("Entering RESTRICT mode - new connections limited")
        # Implementation depends on the system
        # Could set a flag that the main app checks
    
    def _lockdown_mode(self):
        """Enter lockdown mode"""
        logger.warning("Entering LOCKDOWN mode - all access blocked")
        # Implementation depends on the system
    
    def _shutdown(self):
        """Execute shutdown"""
        logger.critical("Executing EMERGENCY SHUTDOWN")
        
        # Run shutdown handlers
        for handler in self.shutdown_handlers:
            try:
                handler()
            except Exception as e:
                logger.error(f"Shutdown handler error: {e}")
        
        # Log final message
        logger.critical("System shutdown complete")
        
        # Exit
        os._exit(1)
    
    def add_shutdown_handler(self, handler: Callable[[], None]):
        """Add shutdown handler"""
        self.shutdown_handlers.append(handler)
    
    def resolve(
        self,
        resolved_by: str = "admin",
        reset_level: bool = True
    ):
        """Resolve current emergency"""
        with self._lock:
            now = datetime.now().isoformat()
            
            # Mark recent events as resolved
            for event in reversed(self.events):
                if not event.resolved:
                    event.resolved = True
                    event.resolved_at = now
                    event.resolved_by = resolved_by
            
            if reset_level:
                self.current_level = EmergencyLevel.WARNING
                self.is_active = False
            
            logger.info(f"Emergency resolved by {resolved_by}")
            
            if self.alert_manager:
                self.alert_manager.info(
                    title="✅ Emergency Resolved",
                    message=f"Resolved by: {resolved_by}\nTime: {now}"
                )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        return {
            "is_active": self.is_active,
            "current_level": self.current_level.name,
            "current_level_value": self.current_level.value,
            "total_events": len(self.events),
            "unresolved_events": sum(1 for e in self.events if not e.resolved)
        }
    
    def get_events(
        self,
        resolved: bool = None,
        level: EmergencyLevel = None,
        limit: int = 100
    ) -> List[EmergencyEvent]:
        """Get events"""
        events = self.events.copy()
        
        if resolved is not None:
            events = [e for e in events if e.resolved == resolved]
        
        if level is not None:
            events = [e for e in events if e.level == level]
        
        return events[-limit:]
    
    def get_stats(self) -> Dict[str, int]:
        """Get statistics"""
        return self.stats.copy()
    
    # Convenience methods
    
    def warn(self, reason: str, **kwargs):
        """Trigger warning"""
        return self.trigger(EmergencyLevel.WARNING, reason, **kwargs)
    
    def restrict(self, reason: str, **kwargs):
        """Trigger restriction"""
        return self.trigger(EmergencyLevel.RESTRICT, reason, **kwargs)
    
    def lockdown(self, reason: str, **kwargs):
        """Trigger lockdown"""
        return self.trigger(EmergencyLevel.LOCKDOWN, reason, **kwargs)
    
    def shutdown(self, reason: str, **kwargs):
        """Trigger shutdown"""
        return self.trigger(EmergencyLevel.SHUTDOWN, reason, **kwargs)
    
    def is_restricted(self) -> bool:
        """Check if in restricted mode"""
        return self.current_level.value >= EmergencyLevel.RESTRICT.value
    
    def is_locked_down(self) -> bool:
        """Check if in lockdown mode"""
        return self.current_level.value >= EmergencyLevel.LOCKDOWN.value


# Global instance
_emergency_system: Optional[EmergencyShutdown] = None


def get_emergency_system(alert_manager=None) -> EmergencyShutdown:
    """Get or create emergency system"""
    global _emergency_system
    if _emergency_system is None:
        _emergency_system = EmergencyShutdown(alert_manager=alert_manager)
    return _emergency_system


def trigger_emergency(
    level: EmergencyLevel,
    reason: str,
    **kwargs
) -> EmergencyEvent:
    """Trigger emergency on global system"""
    return get_emergency_system().trigger(level, reason, **kwargs)
