"""
dLNk Telegram Bot - Rate Limiting Middleware

This middleware implements rate limiting to prevent abuse
and ensure fair usage of the bot.
"""

import logging
import time
from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from config import RateLimitConfig

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseMiddleware):
    """
    Middleware for rate limiting.
    
    Tracks message counts per user and blocks users who exceed
    the configured rate limit.
    """
    
    def __init__(
        self,
        rate_limit: int = None,
        time_window: int = None,
        cooldown: int = None
    ):
        """
        Initialize the middleware.
        
        Args:
            rate_limit: Max messages per time window
            time_window: Time window in seconds
            cooldown: Cooldown period after rate limit hit
        """
        self.rate_limit = rate_limit or RateLimitConfig.MESSAGES_PER_MINUTE
        self.time_window = time_window or RateLimitConfig.TIME_WINDOW
        self.cooldown = cooldown or RateLimitConfig.COOLDOWN
        
        # Track user message timestamps
        # {user_id: [timestamp1, timestamp2, ...]}
        self.user_messages: Dict[int, list] = defaultdict(list)
        
        # Track users in cooldown
        # {user_id: cooldown_end_timestamp}
        self.cooldowns: Dict[int, float] = {}
        
        super().__init__()
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process incoming message and apply rate limiting.
        
        Args:
            handler: Next handler in chain
            event: Incoming message
            data: Handler data
            
        Returns:
            Handler result or None if rate limited
        """
        # Skip non-message events
        if not isinstance(event, Message):
            return await handler(event, data)
        
        user_id = event.from_user.id
        current_time = time.time()
        
        # Check if user is in cooldown
        if user_id in self.cooldowns:
            if current_time < self.cooldowns[user_id]:
                remaining = int(self.cooldowns[user_id] - current_time)
                logger.warning(f"User {user_id} is in cooldown for {remaining}s")
                await event.answer(
                    f"⏳ <b>Rate Limited</b>\n\n"
                    f"Please wait {remaining} seconds before sending more messages."
                )
                return None
            else:
                # Cooldown expired
                del self.cooldowns[user_id]
        
        # Clean old timestamps
        self._clean_old_timestamps(user_id, current_time)
        
        # Check rate limit
        message_count = len(self.user_messages[user_id])
        
        if message_count >= self.rate_limit:
            # Apply cooldown
            self.cooldowns[user_id] = current_time + self.cooldown
            logger.warning(
                f"Rate limit exceeded for user {user_id}: "
                f"{message_count}/{self.rate_limit} in {self.time_window}s"
            )
            await event.answer(
                f"⚠️ <b>Rate Limit Exceeded</b>\n\n"
                f"You've sent too many messages.\n"
                f"Please wait {self.cooldown} seconds."
            )
            return None
        
        # Record this message
        self.user_messages[user_id].append(current_time)
        
        # Store rate limit info in data
        data['rate_limit_remaining'] = self.rate_limit - message_count - 1
        
        return await handler(event, data)
    
    def _clean_old_timestamps(self, user_id: int, current_time: float):
        """
        Remove timestamps older than the time window.
        
        Args:
            user_id: User ID to clean
            current_time: Current timestamp
        """
        cutoff = current_time - self.time_window
        self.user_messages[user_id] = [
            ts for ts in self.user_messages[user_id]
            if ts > cutoff
        ]
    
    def reset_user(self, user_id: int):
        """
        Reset rate limit for a specific user.
        
        Args:
            user_id: User ID to reset
        """
        if user_id in self.user_messages:
            del self.user_messages[user_id]
        if user_id in self.cooldowns:
            del self.cooldowns[user_id]
        logger.info(f"Rate limit reset for user {user_id}")
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get rate limit stats for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with rate limit statistics
        """
        current_time = time.time()
        self._clean_old_timestamps(user_id, current_time)
        
        message_count = len(self.user_messages[user_id])
        in_cooldown = user_id in self.cooldowns
        cooldown_remaining = 0
        
        if in_cooldown:
            cooldown_remaining = max(0, int(self.cooldowns[user_id] - current_time))
        
        return {
            'user_id': user_id,
            'message_count': message_count,
            'rate_limit': self.rate_limit,
            'remaining': self.rate_limit - message_count,
            'in_cooldown': in_cooldown,
            'cooldown_remaining': cooldown_remaining,
            'time_window': self.time_window
        }
