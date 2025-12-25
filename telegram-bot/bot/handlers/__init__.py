"""
dLNk Telegram Bot - Handlers Package

This package contains all message and callback handlers for the bot.
Handlers process incoming messages and user interactions.

Modules:
    commands: Command handlers (/start, /help, /status, etc.)
    callbacks: Inline keyboard callback handlers
    inline: Inline query handlers
    integration_commands: Integration-specific commands

Command Categories:
    Status & Info:
        - /start: Initialize bot
        - /help: Show help
        - /status: System status
        - /users: User statistics
        - /licenses: License statistics
        - /logs: Recent logs
    
    Management:
        - /ban: Ban user
        - /unban: Unban user
        - /revoke: Revoke license
        - /extend: Extend license
        - /create: Create license
    
    Registration Management:
        - /pending: View pending registrations
        - /approve: Approve registration
        - /reject: Reject registration
    
    Admin:
        - /addadmin: Add admin
        - /removeadmin: Remove admin
        - /broadcast: Send to all admins

Example:
    >>> from bot.handlers import commands, callbacks
    >>> 
    >>> # Register handlers with router
    >>> commands.register_handlers(router, bot)
    >>> callbacks.register_handlers(router, bot)
"""

from . import commands
from . import callbacks
from . import inline
from . import integration_commands

__all__ = ['commands', 'callbacks', 'inline', 'integration_commands']
__version__ = '1.0.0'
