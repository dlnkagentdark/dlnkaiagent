"""
dLNk Telegram Bot - Inline Query Handlers

This module handles inline queries for searching users, licenses, and logs.
"""

import logging
import hashlib
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent
)

if TYPE_CHECKING:
    from ..bot import DLNkBot

logger = logging.getLogger(__name__)


def register_handlers(router: Router, bot: "DLNkBot"):
    """
    Register all inline query handlers.
    
    Args:
        router: aiogram Router instance
        bot: DLNkBot instance
    """
    
    @router.inline_query()
    async def inline_search(inline_query: InlineQuery):
        """
        Handle inline queries for searching.
        
        Usage:
            @bot_username user john
            @bot_username license DLNK-
            @bot_username log error
        """
        query = inline_query.query.strip()
        user_id = inline_query.from_user.id
        
        # Check if user is admin
        if not bot.is_admin(user_id):
            results = [
                InlineQueryResultArticle(
                    id="no_access",
                    title="⛔ Access Denied",
                    description="You don't have permission to use inline search",
                    input_message_content=InputTextMessageContent(
                        message_text="⛔ Access denied. Admin privileges required."
                    )
                )
            ]
            await inline_query.answer(results, cache_time=60)
            return
        
        # Parse query
        parts = query.split(maxsplit=1)
        search_type = parts[0].lower() if parts else ""
        search_term = parts[1] if len(parts) > 1 else ""
        
        results = []
        
        if search_type == "user" or search_type == "u":
            results = await _search_users(search_term)
        elif search_type == "license" or search_type == "l":
            results = await _search_licenses(search_term)
        elif search_type == "log":
            results = await _search_logs(search_term)
        else:
            # Show help
            results = _get_search_help()
        
        await inline_query.answer(results, cache_time=10)
    
    logger.info("Inline handlers registered")


async def _search_users(query: str) -> list:
    """
    Search for users.
    
    Args:
        query: Search query
        
    Returns:
        List of InlineQueryResultArticle
    """
    # TODO: Actually search via backend API
    # For now, return mock results
    
    if not query:
        return [
            InlineQueryResultArticle(
                id="user_help",
                title="🔍 Search Users",
                description="Type a username or user ID to search",
                input_message_content=InputTextMessageContent(
                    message_text="Usage: @bot user [query]\nExample: @bot user john"
                )
            )
        ]
    
    # Mock results
    mock_users = [
        {"id": "12345", "username": "john_doe", "license": "Pro", "status": "Active"},
        {"id": "67890", "username": "john_smith", "license": "Basic", "status": "Active"},
        {"id": "11111", "username": "johnny", "license": "Trial", "status": "Expired"},
    ]
    
    # Filter by query
    filtered = [u for u in mock_users if query.lower() in u["username"].lower() or query in u["id"]]
    
    if not filtered:
        return [
            InlineQueryResultArticle(
                id="no_users",
                title="❌ No Users Found",
                description=f"No users matching '{query}'",
                input_message_content=InputTextMessageContent(
                    message_text=f"No users found matching: {query}"
                )
            )
        ]
    
    results = []
    for user in filtered[:10]:  # Limit to 10 results
        status_emoji = "✅" if user["status"] == "Active" else "⚠️"
        result_id = hashlib.md5(f"user_{user['id']}".encode()).hexdigest()
        
        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title=f"👤 {user['username']}",
                description=f"ID: {user['id']} | {user['license']} | {status_emoji} {user['status']}",
                input_message_content=InputTextMessageContent(
                    message_text=(
                        f"👤 <b>User Details</b>\n\n"
                        f"<b>Username:</b> {user['username']}\n"
                        f"<b>ID:</b> <code>{user['id']}</code>\n"
                        f"<b>License:</b> {user['license']}\n"
                        f"<b>Status:</b> {status_emoji} {user['status']}"
                    ),
                    parse_mode="HTML"
                )
            )
        )
    
    return results


async def _search_licenses(query: str) -> list:
    """
    Search for licenses.
    
    Args:
        query: Search query
        
    Returns:
        List of InlineQueryResultArticle
    """
    # TODO: Actually search via backend API
    
    if not query:
        return [
            InlineQueryResultArticle(
                id="license_help",
                title="🔍 Search Licenses",
                description="Type a license key or owner name to search",
                input_message_content=InputTextMessageContent(
                    message_text="Usage: @bot license [query]\nExample: @bot license DLNK-"
                )
            )
        ]
    
    # Mock results
    mock_licenses = [
        {"key": "DLNK-ABCD-1234-WXYZ", "owner": "john_doe", "type": "Pro", "status": "Active", "expires": "2025-12-31"},
        {"key": "DLNK-EFGH-5678-UVWX", "owner": "jane_smith", "type": "Enterprise", "status": "Active", "expires": "2026-06-30"},
        {"key": "DLNK-IJKL-9012-RSTU", "owner": "bob_wilson", "type": "Basic", "status": "Expired", "expires": "2024-12-31"},
    ]
    
    # Filter by query
    filtered = [
        l for l in mock_licenses 
        if query.upper() in l["key"] or query.lower() in l["owner"].lower()
    ]
    
    if not filtered:
        return [
            InlineQueryResultArticle(
                id="no_licenses",
                title="❌ No Licenses Found",
                description=f"No licenses matching '{query}'",
                input_message_content=InputTextMessageContent(
                    message_text=f"No licenses found matching: {query}"
                )
            )
        ]
    
    results = []
    for lic in filtered[:10]:
        status_emoji = "✅" if lic["status"] == "Active" else "⚠️"
        result_id = hashlib.md5(f"license_{lic['key']}".encode()).hexdigest()
        
        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title=f"🔑 {lic['key'][:15]}...",
                description=f"{lic['owner']} | {lic['type']} | {status_emoji} {lic['status']}",
                input_message_content=InputTextMessageContent(
                    message_text=(
                        f"🔑 <b>License Details</b>\n\n"
                        f"<b>Key:</b> <code>{lic['key']}</code>\n"
                        f"<b>Owner:</b> {lic['owner']}\n"
                        f"<b>Type:</b> {lic['type']}\n"
                        f"<b>Status:</b> {status_emoji} {lic['status']}\n"
                        f"<b>Expires:</b> {lic['expires']}"
                    ),
                    parse_mode="HTML"
                )
            )
        )
    
    return results


async def _search_logs(query: str) -> list:
    """
    Search logs.
    
    Args:
        query: Search query
        
    Returns:
        List of InlineQueryResultArticle
    """
    # TODO: Actually search via backend API
    
    if not query:
        return [
            InlineQueryResultArticle(
                id="log_help",
                title="🔍 Search Logs",
                description="Type a keyword to search logs (error, warning, etc.)",
                input_message_content=InputTextMessageContent(
                    message_text="Usage: @bot log [query]\nExample: @bot log error"
                )
            )
        ]
    
    # Mock results
    mock_logs = [
        {"time": "12:34:56", "level": "ERROR", "message": "Connection timeout to AI service"},
        {"time": "12:33:45", "level": "WARNING", "message": "Rate limit approaching for user123"},
        {"time": "12:32:12", "level": "ERROR", "message": "Invalid license key attempted"},
        {"time": "12:31:00", "level": "INFO", "message": "User login successful"},
        {"time": "12:30:45", "level": "WARNING", "message": "High memory usage detected"},
    ]
    
    # Filter by query
    filtered = [
        l for l in mock_logs 
        if query.lower() in l["level"].lower() or query.lower() in l["message"].lower()
    ]
    
    if not filtered:
        return [
            InlineQueryResultArticle(
                id="no_logs",
                title="❌ No Logs Found",
                description=f"No logs matching '{query}'",
                input_message_content=InputTextMessageContent(
                    message_text=f"No logs found matching: {query}"
                )
            )
        ]
    
    results = []
    for i, log in enumerate(filtered[:10]):
        level_emoji = {"ERROR": "🔴", "WARNING": "⚠️", "INFO": "ℹ️"}.get(log["level"], "📋")
        result_id = hashlib.md5(f"log_{i}_{log['time']}".encode()).hexdigest()
        
        results.append(
            InlineQueryResultArticle(
                id=result_id,
                title=f"{level_emoji} [{log['level']}] {log['time']}",
                description=log["message"][:50],
                input_message_content=InputTextMessageContent(
                    message_text=(
                        f"📋 <b>Log Entry</b>\n\n"
                        f"<b>Time:</b> {log['time']}\n"
                        f"<b>Level:</b> {level_emoji} {log['level']}\n"
                        f"<b>Message:</b> {log['message']}"
                    ),
                    parse_mode="HTML"
                )
            )
        )
    
    return results


def _get_search_help() -> list:
    """
    Get search help results.
    
    Returns:
        List of InlineQueryResultArticle with help info
    """
    return [
        InlineQueryResultArticle(
            id="help_user",
            title="👤 Search Users",
            description="Type: user [query]",
            input_message_content=InputTextMessageContent(
                message_text=(
                    "🔍 <b>Inline Search Help</b>\n\n"
                    "<b>Search Users:</b>\n"
                    "<code>@bot user john</code>\n\n"
                    "<b>Search Licenses:</b>\n"
                    "<code>@bot license DLNK-</code>\n\n"
                    "<b>Search Logs:</b>\n"
                    "<code>@bot log error</code>"
                ),
                parse_mode="HTML"
            )
        ),
        InlineQueryResultArticle(
            id="help_license",
            title="🔑 Search Licenses",
            description="Type: license [query]",
            input_message_content=InputTextMessageContent(
                message_text="Usage: @bot license [key or owner]"
            )
        ),
        InlineQueryResultArticle(
            id="help_log",
            title="📋 Search Logs",
            description="Type: log [query]",
            input_message_content=InputTextMessageContent(
                message_text="Usage: @bot log [keyword]"
            )
        )
    ]
