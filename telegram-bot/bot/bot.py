"""
dLNk Telegram Bot - Main Bot Class

This module contains the main DLNkBot class that handles
bot initialization, handler registration, and lifecycle management.
"""

import logging
from typing import List, Optional
from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from .handlers import commands, callbacks, inline, integration_commands
from .middleware.auth import AdminAuthMiddleware
from .middleware.rate_limit import RateLimitMiddleware

logger = logging.getLogger(__name__)


class DLNkBot:
    """
    dLNk Telegram Admin Bot
    
    Main bot class that orchestrates all bot functionality including:
    - Command handling
    - Callback query handling
    - Inline query handling
    - Admin authentication
    - Rate limiting
    - Alert sending
    
    Attributes:
        token: Telegram bot token
        admin_chat_ids: List of admin Telegram user IDs
        bot: aiogram Bot instance
        dp: aiogram Dispatcher instance
    """
    
    def __init__(self, token: str, admin_chat_ids: List[int]):
        """
        Initialize the bot.
        
        Args:
            token: Telegram bot token from BotFather
            admin_chat_ids: List of Telegram user IDs that have admin access
        """
        self.token = token
        self.admin_chat_ids = admin_chat_ids
        
        # Create bot instance with HTML parse mode
        self.bot = Bot(
            token=token,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Create dispatcher with memory storage for FSM
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Store reference to bot in dispatcher for handlers
        self.dp["bot_instance"] = self
        self.dp["admin_chat_ids"] = admin_chat_ids
        
        # Setup handlers
        self._setup_handlers()
        
        logger.info(f"Bot initialized with {len(admin_chat_ids)} admin(s)")
    
    def _setup_handlers(self):
        """Setup all message and callback handlers"""
        
        # Create main router
        router = Router(name="main")
        
        # Add middleware
        router.message.middleware(
            AdminAuthMiddleware(self.admin_chat_ids)
        )
        router.message.middleware(
            RateLimitMiddleware()
        )
        
        # Register command handlers
        commands.register_handlers(router, self)
        
        # Register callback handlers
        callbacks.register_handlers(router, self)
        
        # Register inline handlers
        inline.register_handlers(router, self)
        
        # Register integration handlers
        integration_commands.register_integration_handlers(router, self)
        
        # Include router in dispatcher
        self.dp.include_router(router)
        
        logger.info("All handlers registered successfully")
    
    async def start(self):
        """Start the bot and begin polling for updates"""
        logger.info("Bot starting...")
        
        # Get bot info
        bot_info = await self.bot.get_me()
        logger.info(f"Bot: @{bot_info.username} (ID: {bot_info.id})")
        
        # Delete webhook and drop pending updates
        await self.bot.delete_webhook(drop_pending_updates=True)
        
        # Start polling
        logger.info("Starting polling...")
        await self.dp.start_polling(self.bot)
    
    async def stop(self):
        """Stop the bot gracefully"""
        logger.info("Stopping bot...")
        await self.dp.stop_polling()
        await self.bot.session.close()
        logger.info("Bot stopped")
    
    async def send_alert(
        self,
        message: str,
        severity: int = 1,
        chat_id: Optional[int] = None,
        parse_mode: str = "HTML"
    ):
        """
        Send alert to admin(s).
        
        Args:
            message: Alert message content
            severity: Alert severity level (1=low, 2=medium, 3=high, 4=critical)
            chat_id: Specific chat ID to send to (or all admins if None)
            parse_mode: Message parse mode (HTML or Markdown)
        """
        # Severity icons
        icons = {
            1: "ℹ️",   # Info/Low
            2: "⚠️",   # Warning/Medium
            3: "🚨",   # Alert/High
            4: "🔴"    # Critical
        }
        icon = icons.get(severity, "ℹ️")
        
        # Format message
        full_message = f"{icon} <b>Alert</b>\n\n{message}"
        
        # Send to specific chat or all admins
        if chat_id:
            try:
                await self.bot.send_message(
                    chat_id, 
                    full_message, 
                    parse_mode=parse_mode
                )
                logger.info(f"Alert sent to {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send alert to {chat_id}: {e}")
        else:
            for admin_id in self.admin_chat_ids:
                try:
                    await self.bot.send_message(
                        admin_id, 
                        full_message, 
                        parse_mode=parse_mode
                    )
                    logger.info(f"Alert sent to admin {admin_id}")
                except Exception as e:
                    logger.error(f"Failed to send alert to {admin_id}: {e}")
    
    async def broadcast(
        self,
        message: str,
        chat_ids: Optional[List[int]] = None,
        parse_mode: str = "HTML"
    ):
        """
        Broadcast message to multiple users.
        
        Args:
            message: Message content
            chat_ids: List of chat IDs (or all admins if None)
            parse_mode: Message parse mode
        """
        targets = chat_ids or self.admin_chat_ids
        success_count = 0
        fail_count = 0
        
        for chat_id in targets:
            try:
                await self.bot.send_message(
                    chat_id, 
                    message, 
                    parse_mode=parse_mode
                )
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to broadcast to {chat_id}: {e}")
                fail_count += 1
        
        logger.info(f"Broadcast complete: {success_count} success, {fail_count} failed")
        return success_count, fail_count
    
    def is_admin(self, user_id: int) -> bool:
        """
        Check if a user is an admin.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            True if user is admin, False otherwise
        """
        # If no admins configured, allow all (for initial setup)
        if not self.admin_chat_ids:
            return True
        return user_id in self.admin_chat_ids
