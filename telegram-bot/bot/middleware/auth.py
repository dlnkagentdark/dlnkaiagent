"""
dLNk Telegram Bot - Admin Authentication Middleware

This middleware checks if the user is an admin before processing
certain commands that require elevated privileges.
"""

import logging
from typing import Any, Awaitable, Callable, Dict, List

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

logger = logging.getLogger(__name__)


# Commands that require admin access
ADMIN_COMMANDS = {
    '/status', '/users', '/licenses', '/logs',
    '/ban', '/unban', '/revoke', '/extend',
    '/alert', '/settings', '/stats', '/create',
    '/addadmin', '/removeadmin', '/broadcast',
    '/quick', '/search'
}

# Commands that are public (no admin required)
PUBLIC_COMMANDS = {
    '/start', '/help', '/myid', '/verify'
}


class AdminAuthMiddleware(BaseMiddleware):
    """
    Middleware for admin authentication.
    
    Checks if the user sending a command is in the admin list.
    Non-admin users are blocked from using admin commands.
    """
    
    def __init__(self, admin_chat_ids: List[int]):
        """
        Initialize the middleware.
        
        Args:
            admin_chat_ids: List of Telegram user IDs that have admin access
        """
        self.admin_chat_ids = set(admin_chat_ids)
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process incoming message and check admin status.
        
        Args:
            handler: Next handler in chain
            event: Incoming message
            data: Handler data
            
        Returns:
            Handler result or None if blocked
        """
        # Skip non-message events
        if not isinstance(event, Message):
            return await handler(event, data)
        
        # Skip non-command messages
        if not event.text or not event.text.startswith('/'):
            return await handler(event, data)
        
        # Extract command
        command = event.text.split()[0].lower()
        if '@' in command:
            command = command.split('@')[0]
        
        # Check if command requires admin
        user_id = event.from_user.id
        is_admin = self._is_admin(user_id)
        
        # Store admin status in data for handlers
        data['is_admin'] = is_admin
        data['admin_chat_ids'] = self.admin_chat_ids
        
        # Public commands - allow all
        if command in PUBLIC_COMMANDS:
            return await handler(event, data)
        
        # Admin commands - check permission
        if command in ADMIN_COMMANDS:
            if not is_admin:
                logger.warning(
                    f"Unauthorized access attempt: User {user_id} tried {command}"
                )
                await event.answer(
                    "⛔ <b>Access Denied</b>\n\n"
                    "This command requires admin privileges.\n"
                    "Contact the system administrator for access."
                )
                return None
        
        # Unknown commands or allowed - proceed
        return await handler(event, data)
    
    def _is_admin(self, user_id: int) -> bool:
        """
        Check if user is an admin.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if admin, False otherwise
        """
        # If no admins configured, allow all (for initial setup)
        if not self.admin_chat_ids:
            return True
        return user_id in self.admin_chat_ids
    
    def add_admin(self, user_id: int):
        """Add a user to admin list"""
        self.admin_chat_ids.add(user_id)
        logger.info(f"Added admin: {user_id}")
    
    def remove_admin(self, user_id: int):
        """Remove a user from admin list"""
        self.admin_chat_ids.discard(user_id)
        logger.info(f"Removed admin: {user_id}")
