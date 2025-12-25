"""
dLNk Telegram Bot - Notification Scheduler

This module handles scheduled notifications and periodic tasks.
"""

import logging
import asyncio
from datetime import datetime, time
from typing import TYPE_CHECKING, Optional, Callable, List

if TYPE_CHECKING:
    from .alert_sender import AlertSender

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """
    Schedule and manage periodic notifications.
    
    This class handles:
    - Daily summary reports
    - Expiring license alerts
    - System health checks
    - Custom scheduled notifications
    """
    
    def __init__(self, alert_sender: "AlertSender"):
        """
        Initialize the scheduler.
        
        Args:
            alert_sender: AlertSender instance for sending notifications
        """
        self.alert_sender = alert_sender
        self._tasks: List[asyncio.Task] = []
        self._running = False
        
        # Schedule configuration
        self.daily_summary_time = time(hour=9, minute=0)  # 9:00 AM
        self.expiring_check_interval = 3600 * 6  # Every 6 hours
        self.health_check_interval = 300  # Every 5 minutes
    
    async def start(self):
        """Start all scheduled tasks."""
        if self._running:
            logger.warning("Scheduler already running")
            return
        
        self._running = True
        logger.info("Starting notification scheduler...")
        
        # Start scheduled tasks
        self._tasks = [
            asyncio.create_task(self._daily_summary_loop()),
            asyncio.create_task(self._expiring_licenses_loop()),
            asyncio.create_task(self._health_check_loop())
        ]
        
        logger.info(f"Started {len(self._tasks)} scheduled tasks")
    
    async def stop(self):
        """Stop all scheduled tasks."""
        if not self._running:
            return
        
        self._running = False
        logger.info("Stopping notification scheduler...")
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self._tasks, return_exceptions=True)
        self._tasks = []
        
        logger.info("Notification scheduler stopped")
    
    async def _daily_summary_loop(self):
        """Loop for sending daily summaries."""
        while self._running:
            try:
                # Calculate time until next summary
                now = datetime.now()
                target = datetime.combine(now.date(), self.daily_summary_time)
                
                if now.time() >= self.daily_summary_time:
                    # Already past today's time, schedule for tomorrow
                    target = datetime.combine(
                        now.date().replace(day=now.day + 1),
                        self.daily_summary_time
                    )
                
                wait_seconds = (target - now).total_seconds()
                logger.info(f"Next daily summary in {wait_seconds / 3600:.1f} hours")
                
                await asyncio.sleep(wait_seconds)
                
                if self._running:
                    await self.alert_sender.send_daily_summary()
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in daily summary loop: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _expiring_licenses_loop(self):
        """Loop for checking expiring licenses."""
        while self._running:
            try:
                await asyncio.sleep(self.expiring_check_interval)
                
                if self._running:
                    # TODO: Fetch actual expiring licenses from backend
                    # For now, use mock data
                    expiring = await self._get_expiring_licenses()
                    
                    if expiring:
                        await self.alert_sender.send_expiring_licenses_alert(expiring)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in expiring licenses loop: {e}")
                await asyncio.sleep(60)
    
    async def _health_check_loop(self):
        """Loop for system health checks."""
        while self._running:
            try:
                await asyncio.sleep(self.health_check_interval)
                
                if self._running:
                    # TODO: Perform actual health checks
                    health = await self._check_system_health()
                    
                    if not health["healthy"]:
                        await self.alert_sender.send_system_alert(
                            title="System Health Warning",
                            message=health["message"],
                            severity=health["severity"],
                            metrics=health.get("metrics")
                        )
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in health check loop: {e}")
                await asyncio.sleep(60)
    
    async def _get_expiring_licenses(self) -> List[dict]:
        """
        Get licenses expiring soon.
        
        Returns:
            List of expiring license dicts
        """
        # TODO: Implement actual API call
        # This is mock data for demonstration
        return []
    
    async def _check_system_health(self) -> dict:
        """
        Check system health.
        
        Returns:
            Health status dict
        """
        # TODO: Implement actual health checks
        # This is mock data for demonstration
        return {
            "healthy": True,
            "message": "All systems operational",
            "severity": 1,
            "metrics": {
                "cpu": "23%",
                "memory": "45%",
                "disk": "67%"
            }
        }
    
    def schedule_one_time(
        self,
        delay_seconds: int,
        callback: Callable,
        *args,
        **kwargs
    ) -> asyncio.Task:
        """
        Schedule a one-time notification.
        
        Args:
            delay_seconds: Delay before execution
            callback: Async function to call
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback
            
        Returns:
            asyncio.Task for the scheduled notification
        """
        async def delayed_call():
            await asyncio.sleep(delay_seconds)
            await callback(*args, **kwargs)
        
        task = asyncio.create_task(delayed_call())
        self._tasks.append(task)
        return task
    
    def schedule_recurring(
        self,
        interval_seconds: int,
        callback: Callable,
        *args,
        **kwargs
    ) -> asyncio.Task:
        """
        Schedule a recurring notification.
        
        Args:
            interval_seconds: Interval between executions
            callback: Async function to call
            *args: Positional arguments for callback
            **kwargs: Keyword arguments for callback
            
        Returns:
            asyncio.Task for the scheduled notification
        """
        async def recurring_call():
            while self._running:
                try:
                    await asyncio.sleep(interval_seconds)
                    if self._running:
                        await callback(*args, **kwargs)
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    logger.error(f"Error in recurring task: {e}")
        
        task = asyncio.create_task(recurring_call())
        self._tasks.append(task)
        return task
    
    def set_daily_summary_time(self, hour: int, minute: int = 0):
        """
        Set the time for daily summary.
        
        Args:
            hour: Hour (0-23)
            minute: Minute (0-59)
        """
        self.daily_summary_time = time(hour=hour, minute=minute)
        logger.info(f"Daily summary time set to {hour:02d}:{minute:02d}")
    
    def set_expiring_check_interval(self, hours: int):
        """
        Set the interval for expiring license checks.
        
        Args:
            hours: Interval in hours
        """
        self.expiring_check_interval = hours * 3600
        logger.info(f"Expiring check interval set to {hours} hours")
    
    def set_health_check_interval(self, minutes: int):
        """
        Set the interval for health checks.
        
        Args:
            minutes: Interval in minutes
        """
        self.health_check_interval = minutes * 60
        logger.info(f"Health check interval set to {minutes} minutes")
