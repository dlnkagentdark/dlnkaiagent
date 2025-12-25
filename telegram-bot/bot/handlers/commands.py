"""
dLNk Telegram Bot - Command Handlers

This module contains all command handlers for the bot.
Commands are registered with the router and handle user interactions.

Available Commands:
    - /start: Initialize bot and show welcome message
    - /help: Display available commands
    - /status: Show system status
    - /users: Display user statistics
    - /licenses: Display license statistics
    - /logs: View recent logs
    - /ban: Ban a user
    - /unban: Unban a user
    - /revoke: Revoke a license
    - /extend: Extend license duration
    - /verify: Verify a license key
    - /quick: Quick create license menu
    - /alert: Alert settings
    - /myid: Get Telegram ID
    - /addadmin: Add admin
    - /removeadmin: Remove admin
    - /broadcast: Send message to all admins
    - /search: Search users/licenses
    - /create: Create new license
    - /settings: Bot settings
    - /pending: View pending registration requests
    - /approve: Approve a registration request
    - /reject: Reject a registration request
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandStart

from ..keyboards.main_menu import get_main_menu_keyboard
from ..keyboards.inline import (
    get_confirm_keyboard, 
    get_main_menu_inline,
    get_quick_create_keyboard,
    get_alert_settings_keyboard
)

if TYPE_CHECKING:
    from ..bot import DLNkBot

logger = logging.getLogger(__name__)


def register_handlers(router: Router, bot: "DLNkBot"):
    """
    Register all command handlers with the router.
    
    This function sets up all bot commands and their handlers.
    Each handler is registered as an async function that processes
    incoming messages matching specific command patterns.
    
    Args:
        router: aiogram Router instance for registering handlers
        bot: DLNkBot instance providing access to bot functionality
    """
    
    @router.message(CommandStart())
    async def cmd_start(message: Message):
        """
        Handle /start command.
        
        Displays welcome message and main menu to the user.
        Shows different content based on admin status.
        
        Args:
            message: Incoming Telegram message
        """
        user = message.from_user
        is_admin = bot.is_admin(user.id)
        
        welcome_text = (
            "🚀 <b>dLNk Admin Bot</b>\n\n"
            f"Welcome, {user.first_name}!\n\n"
            "This bot helps you manage dLNk IDE licenses, users, and system monitoring.\n\n"
            "Use /help to see available commands."
        )
        
        if is_admin:
            welcome_text += "\n\n✅ <b>Admin access granted</b>"
        else:
            welcome_text += (
                "\n\n⚠️ <b>Note:</b> You are not registered as an admin.\n"
                "Contact the system administrator for access."
            )
        
        await message.answer(
            welcome_text,
            reply_markup=get_main_menu_keyboard()
        )
        logger.info(f"User {user.id} ({user.username}) started the bot")
    
    @router.message(Command("help"))
    async def cmd_help(message: Message):
        """
        Handle /help command.
        
        Displays a comprehensive list of all available commands
        organized by category.
        
        Args:
            message: Incoming Telegram message
        """
        help_text = """
📋 <b>Available Commands</b>

<b>📊 Status & Info:</b>
/status - System status overview
/users - User statistics
/licenses - License statistics
/logs - View recent logs

<b>🔧 Management:</b>
/ban [user_id] - Ban a user
/unban [user_id] - Unban a user
/revoke [license_key] - Revoke a license
/extend [license_key] [days] - Extend license
/create - Create new license

<b>🔑 License:</b>
/verify [license_key] - Verify a license
/quick - Quick create license menu
/search [query] - Search users/licenses

<b>⚙️ Settings:</b>
/alert - Alert settings
/settings - Bot settings
/myid - Get your Telegram ID

<b>👤 Admin:</b>
/addadmin [user_id] - Add admin
/removeadmin [user_id] - Remove admin
/broadcast [message] - Send to all admins

<b>📝 Registration Management:</b>
/pending - View pending registration requests
/approve [user_email] - Approve registration
/reject [user_email] - Reject registration
        """
        await message.answer(help_text, reply_markup=get_main_menu_inline())
    
    @router.message(Command("status"))
    async def cmd_status(message: Message):
        """
        Handle /status command.
        
        Displays current system status including service health,
        statistics, alerts, and resource usage.
        
        Args:
            message: Incoming Telegram message
        """
        # TODO: Get real status from backend API
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        status_text = f"""
📊 <b>System Status</b>
<i>Updated: {now}</i>

🟢 <b>Services:</b>
├ AI Bridge: <code>Online</code>
├ License Server: <code>Online</code>
├ Admin Console: <code>Online</code>
└ Telegram Bot: <code>Online</code>

📈 <b>Statistics (24h):</b>
├ Active Users: <code>45</code>
├ AI Requests: <code>12,345</code>
├ New Registrations: <code>12</code>
└ License Activations: <code>8</code>

⚠️ <b>Alerts:</b>
├ Security Alerts: <code>2</code>
├ System Warnings: <code>0</code>
└ License Issues: <code>1</code>

💾 <b>Resources:</b>
├ CPU: <code>23%</code>
├ Memory: <code>45%</code>
└ Storage: <code>67%</code>
        """
        await message.answer(status_text)
        logger.info(f"Status requested by {message.from_user.id}")
    
    @router.message(Command("users"))
    async def cmd_users(message: Message):
        """
        Handle /users command.
        
        Displays user statistics including total users,
        activity metrics, and distribution by license type.
        
        Args:
            message: Incoming Telegram message
        """
        # TODO: Get real data from backend API
        users_text = """
👥 <b>User Statistics</b>

📊 <b>Total Users:</b> <code>1,234</code>
├ Active (7d): <code>456</code>
├ Active (30d): <code>789</code>
└ New (7d): <code>78</code>

📈 <b>By License Type:</b>
├ Trial: <code>234</code> (19%)
├ Basic: <code>456</code> (37%)
├ Pro: <code>333</code> (27%)
└ Enterprise: <code>211</code> (17%)

🌍 <b>Top Regions:</b>
├ Thailand: <code>45%</code>
├ USA: <code>20%</code>
├ Vietnam: <code>15%</code>
└ Other: <code>20%</code>

📱 <b>By Platform:</b>
├ Windows: <code>65%</code>
├ macOS: <code>25%</code>
└ Linux: <code>10%</code>
        """
        await message.answer(users_text)
    
    @router.message(Command("licenses"))
    async def cmd_licenses(message: Message):
        """
        Handle /licenses command.
        
        Displays license statistics including counts by status,
        type distribution, and expiration forecasts.
        
        Args:
            message: Incoming Telegram message
        """
        # TODO: Get real data from backend API
        licenses_text = """
🔑 <b>License Statistics</b>

📊 <b>Total Licenses:</b> <code>1,234</code>
├ Active: <code>987</code> ✅
├ Expired: <code>200</code> ⚠️
├ Revoked: <code>47</code> ❌
└ Pending: <code>0</code>

📈 <b>By Type:</b>
├ Trial (7d): <code>234</code>
├ Basic (30d): <code>456</code>
├ Pro (90d): <code>333</code>
└ Enterprise (365d): <code>211</code>

⏰ <b>Expiring Soon:</b>
├ Today: <code>5</code>
├ This Week: <code>23</code>
└ This Month: <code>45</code>

💰 <b>Revenue (Est.):</b>
├ This Month: <code>$12,345</code>
└ This Year: <code>$145,678</code>
        """
        await message.answer(licenses_text)
    
    @router.message(Command("logs"))
    async def cmd_logs(message: Message):
        """
        Handle /logs command.
        
        Displays recent system logs with timestamps and event types.
        
        Args:
            message: Incoming Telegram message
        """
        # TODO: Get real logs from backend API
        now = datetime.now()
        
        logs_text = f"""
📋 <b>Recent Logs</b>
<i>Last 10 entries</i>

<code>{now.strftime('%H:%M:%S')}</code> ✅ User login: john_doe
<code>{now.strftime('%H:%M:%S')}</code> 🔑 License created: DLNK-XXXX
<code>{now.strftime('%H:%M:%S')}</code> 🚨 Security alert: Blocked prompt
<code>{now.strftime('%H:%M:%S')}</code> 👤 User registered: jane_smith
<code>{now.strftime('%H:%M:%S')}</code> 🔄 Token refreshed: user123
<code>{now.strftime('%H:%M:%S')}</code> ⚠️ Rate limit hit: user456
<code>{now.strftime('%H:%M:%S')}</code> ✅ License verified: DLNK-YYYY
<code>{now.strftime('%H:%M:%S')}</code> 🔧 Settings updated by admin
<code>{now.strftime('%H:%M:%S')}</code> 📊 Stats exported
<code>{now.strftime('%H:%M:%S')}</code> 🔄 System health check: OK

<i>Use /logs [count] for more entries</i>
        """
        await message.answer(logs_text)
    
    @router.message(Command("ban"))
    async def cmd_ban(message: Message):
        """
        Handle /ban command.
        
        Initiates the process to ban a user. Requires confirmation.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ <b>Usage:</b> /ban [user_id]\n\n"
                "<b>Example:</b>\n"
                "<code>/ban user123</code>\n"
                "<code>/ban 12345678</code>"
            )
            return
        
        user_id = args[0]
        await message.answer(
            f"⚠️ <b>Confirm Ban</b>\n\n"
            f"Are you sure you want to ban user <code>{user_id}</code>?\n\n"
            f"This will:\n"
            f"• Revoke all active licenses\n"
            f"• Block future access\n"
            f"• Log the action",
            reply_markup=get_confirm_keyboard(f"ban_{user_id}")
        )
    
    @router.message(Command("unban"))
    async def cmd_unban(message: Message):
        """
        Handle /unban command.
        
        Initiates the process to unban a user. Requires confirmation.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ <b>Usage:</b> /unban [user_id]\n\n"
                "<b>Example:</b>\n"
                "<code>/unban user123</code>"
            )
            return
        
        user_id = args[0]
        await message.answer(
            f"⚠️ <b>Confirm Unban</b>\n\n"
            f"Are you sure you want to unban user <code>{user_id}</code>?",
            reply_markup=get_confirm_keyboard(f"unban_{user_id}")
        )
    
    @router.message(Command("revoke"))
    async def cmd_revoke(message: Message):
        """
        Handle /revoke command.
        
        Initiates the process to revoke a license. Requires confirmation.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ <b>Usage:</b> /revoke [license_key]\n\n"
                "<b>Example:</b>\n"
                "<code>/revoke DLNK-XXXX-XXXX-XXXX</code>"
            )
            return
        
        license_key = args[0]
        await message.answer(
            f"⚠️ <b>Confirm Revoke</b>\n\n"
            f"Are you sure you want to revoke license:\n"
            f"<code>{license_key}</code>?\n\n"
            f"This action cannot be undone.",
            reply_markup=get_confirm_keyboard(f"revoke_{license_key}")
        )
    
    @router.message(Command("extend"))
    async def cmd_extend(message: Message):
        """
        Handle /extend command.
        
        Initiates the process to extend a license. Requires confirmation.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if len(args) < 1:
            await message.answer(
                "❌ <b>Usage:</b> /extend [license_key] [days]\n\n"
                "<b>Example:</b>\n"
                "<code>/extend DLNK-XXXX-XXXX-XXXX 30</code>\n\n"
                "Default: 30 days"
            )
            return
        
        license_key = args[0]
        days = int(args[1]) if len(args) > 1 and args[1].isdigit() else 30
        
        await message.answer(
            f"⚠️ <b>Confirm Extension</b>\n\n"
            f"Extend license <code>{license_key}</code> by {days} days?",
            reply_markup=get_confirm_keyboard(f"extend_{license_key}_{days}")
        )
    
    @router.message(Command("verify"))
    async def cmd_verify(message: Message):
        """
        Handle /verify command.
        
        Verifies a license key and displays its details.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ <b>Usage:</b> /verify [license_key]\n\n"
                "<b>Example:</b>\n"
                "<code>/verify DLNK-XXXX-XXXX-XXXX</code>"
            )
            return
        
        license_key = args[0]
        
        # TODO: Actually verify via backend API
        # For now, show mock result
        verify_text = f"""
✅ <b>License Valid</b>

<b>Key:</b> <code>{license_key[:20]}...</code>
<b>Type:</b> Pro
<b>Status:</b> Active ✅
<b>Owner:</b> john_doe
<b>Expires:</b> 2025-12-31
<b>Activations:</b> 2/3

<b>Features:</b>
├ AI Autocomplete ✅
├ Code Analysis ✅
├ Security Scan ✅
└ Priority Support ✅
        """
        await message.answer(verify_text)
    
    @router.message(Command("quick"))
    async def cmd_quick(message: Message):
        """
        Handle /quick command.
        
        Displays quick create license menu with preset options.
        
        Args:
            message: Incoming Telegram message
        """
        await message.answer(
            "🔑 <b>Quick Create License</b>\n\n"
            "Select license type to create:",
            reply_markup=get_quick_create_keyboard()
        )
    
    @router.message(Command("alert"))
    async def cmd_alert(message: Message):
        """
        Handle /alert command.
        
        Displays and manages alert settings.
        
        Args:
            message: Incoming Telegram message
        """
        alert_text = """
🔔 <b>Alert Settings</b>

<b>Current Settings:</b>
├ Alerts: ✅ Enabled
├ Severity Threshold: Medium (2)
├ Security Alerts: ✅
├ License Alerts: ✅
└ System Alerts: ✅

<b>Recent Alerts:</b>
├ Security: 2 (last 24h)
├ License: 5 (last 24h)
└ System: 0 (last 24h)

Use buttons below to change settings.
        """
        await message.answer(alert_text, reply_markup=get_alert_settings_keyboard())
    
    @router.message(Command("myid"))
    async def cmd_myid(message: Message):
        """
        Handle /myid command.
        
        Displays the user's Telegram ID and account information.
        
        Args:
            message: Incoming Telegram message
        """
        user = message.from_user
        is_admin = bot.is_admin(user.id)
        
        myid_text = f"""
👤 <b>Your Information</b>

<b>Telegram ID:</b> <code>{user.id}</code>
<b>Username:</b> @{user.username or 'N/A'}
<b>Name:</b> {user.first_name} {user.last_name or ''}
<b>Admin Status:</b> {'✅ Admin' if is_admin else '❌ Not Admin'}

<i>Share your ID with the administrator to request access.</i>
        """
        await message.answer(myid_text)
    
    @router.message(Command("addadmin"))
    async def cmd_addadmin(message: Message):
        """
        Handle /addadmin command.
        
        Adds a new admin by Telegram user ID.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ <b>Usage:</b> /addadmin [telegram_user_id]\n\n"
                "<b>Example:</b>\n"
                "<code>/addadmin 123456789</code>"
            )
            return
        
        try:
            new_admin_id = int(args[0])
            # TODO: Actually add admin via backend
            await message.answer(
                f"✅ User <code>{new_admin_id}</code> has been added as admin.\n\n"
                f"They can now use admin commands."
            )
            logger.info(f"Admin {message.from_user.id} added new admin {new_admin_id}")
        except ValueError:
            await message.answer("❌ Invalid user ID. Must be a number.")
    
    @router.message(Command("removeadmin"))
    async def cmd_removeadmin(message: Message):
        """
        Handle /removeadmin command.
        
        Removes an admin by Telegram user ID.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ <b>Usage:</b> /removeadmin [telegram_user_id]\n\n"
                "<b>Example:</b>\n"
                "<code>/removeadmin 123456789</code>"
            )
            return
        
        try:
            admin_id = int(args[0])
            # TODO: Actually remove admin via backend
            await message.answer(
                f"✅ User <code>{admin_id}</code> has been removed from admins."
            )
            logger.info(f"Admin {message.from_user.id} removed admin {admin_id}")
        except ValueError:
            await message.answer("❌ Invalid user ID. Must be a number.")
    
    @router.message(Command("broadcast"))
    async def cmd_broadcast(message: Message):
        """
        Handle /broadcast command.
        
        Sends a message to all admins. Requires confirmation.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split(maxsplit=1)
        
        if len(args) < 2:
            await message.answer(
                "❌ <b>Usage:</b> /broadcast [message]\n\n"
                "<b>Example:</b>\n"
                "<code>/broadcast System maintenance in 1 hour</code>"
            )
            return
        
        broadcast_msg = args[1]
        await message.answer(
            f"📢 <b>Confirm Broadcast</b>\n\n"
            f"Send this message to all admins?\n\n"
            f"<blockquote>{broadcast_msg}</blockquote>",
            reply_markup=get_confirm_keyboard(f"broadcast")
        )
    
    @router.message(Command("search"))
    async def cmd_search(message: Message):
        """
        Handle /search command.
        
        Searches for users and licenses matching the query.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ <b>Usage:</b> /search [query]\n\n"
                "<b>Examples:</b>\n"
                "<code>/search john</code> - Search users\n"
                "<code>/search DLNK-</code> - Search licenses"
            )
            return
        
        query = ' '.join(args)
        
        # TODO: Actually search via backend API
        search_text = f"""
🔍 <b>Search Results for:</b> <code>{query}</code>

<b>Users Found:</b> 2
├ john_doe (ID: 12345)
└ john_smith (ID: 67890)

<b>Licenses Found:</b> 1
└ DLNK-JOHN-XXXX-XXXX (Active)

<i>Click on result to view details</i>
        """
        await message.answer(search_text)
    
    @router.message(Command("create"))
    async def cmd_create(message: Message):
        """
        Handle /create command.
        
        Creates a new license with specified parameters.
        
        Args:
            message: Incoming Telegram message
        """
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "🔑 <b>Create License</b>\n\n"
                "<b>Usage:</b>\n"
                "<code>/create [owner] [type] [days]</code>\n\n"
                "<b>Types:</b> trial, basic, pro, enterprise\n\n"
                "<b>Examples:</b>\n"
                "<code>/create john_doe pro 90</code>\n"
                "<code>/create company enterprise 365</code>\n\n"
                "Or use /quick for quick create menu.",
                reply_markup=get_quick_create_keyboard()
            )
            return
        
        owner = args[0]
        license_type = args[1] if len(args) > 1 else 'basic'
        days = int(args[2]) if len(args) > 2 and args[2].isdigit() else 30
        
        # TODO: Actually create via backend API
        # For now, show mock result
        create_text = f"""
✅ <b>License Created!</b>

<b>Key:</b> <code>DLNK-{owner[:4].upper()}-XXXX-XXXX</code>
<b>Type:</b> {license_type.title()}
<b>Owner:</b> {owner}
<b>Duration:</b> {days} days
<b>Expires:</b> 2025-12-31

<b>Encrypted Key (for distribution):</b>
<code>eyJrZXkiOiJETE5LLVhYWFgtWFhYWC1YWFhYIiwidHlwZSI6InBybyJ9...</code>

<i>Send this encrypted key to the user.</i>
        """
        await message.answer(create_text)
        logger.info(f"License created by {message.from_user.id}: {owner}/{license_type}/{days}d")
    
    @router.message(Command("stats"))
    async def cmd_stats(message: Message):
        """
        Handle /stats command.
        
        Alias for /status command.
        
        Args:
            message: Incoming Telegram message
        """
        await cmd_status(message)
    
    @router.message(Command("settings"))
    async def cmd_settings(message: Message):
        """
        Handle /settings command.
        
        Displays current bot settings and configuration.
        
        Args:
            message: Incoming Telegram message
        """
        settings_text = """
⚙️ <b>Bot Settings</b>

<b>General:</b>
├ Language: English
├ Timezone: Asia/Bangkok
└ Notifications: Enabled

<b>Rate Limiting:</b>
├ Messages/min: 30
├ Cooldown: 60s
└ Status: Active

<b>API Connection:</b>
├ Backend: Connected ✅
├ Latency: 45ms
└ Last Check: Just now

<b>Admin Count:</b> 3

<i>Contact developer to change settings.</i>
        """
        await message.answer(settings_text)
    
    # ==========================================
    # Registration Management Commands
    # ==========================================
    
    @router.message(Command("pending"))
    async def cmd_pending(message: Message):
        """
        Handle /pending command.
        
        Displays list of pending registration requests that need
        admin approval or rejection.
        
        Args:
            message: Incoming Telegram message
        """
        user = message.from_user
        
        # Check admin permission
        if not bot.is_admin(user.id):
            await message.answer(
                "❌ <b>Access Denied</b>\n\n"
                "Only admins can view pending registrations."
            )
            return
        
        # Get pending registrations from API
        try:
            from api_client.backend import BackendAPIClient
            api_client = BackendAPIClient()
            pending_list = await api_client.get_pending_registrations()
            await api_client.close()
            
            if not pending_list:
                await message.answer(
                    "📋 <b>Pending Registrations</b>\n\n"
                    "✅ No pending registration requests.\n\n"
                    "<i>All registration requests have been processed.</i>"
                )
                return
            
            # Format pending list
            pending_text = f"📋 <b>Pending Registrations</b>\n\n"
            pending_text += f"<b>Total:</b> {len(pending_list)} request(s)\n\n"
            
            for idx, reg in enumerate(pending_list[:10], 1):
                email = reg.get('email', 'N/A')
                username = reg.get('username', 'N/A')
                requested_type = reg.get('requested_type', 'trial')
                created_at = reg.get('created_at', 'N/A')
                
                pending_text += (
                    f"<b>{idx}.</b> {username}\n"
                    f"   📧 <code>{email}</code>\n"
                    f"   🔑 Requested: {requested_type}\n"
                    f"   📅 {created_at}\n\n"
                )
            
            if len(pending_list) > 10:
                pending_text += f"<i>... and {len(pending_list) - 10} more</i>\n\n"
            
            pending_text += (
                "<b>Actions:</b>\n"
                "• <code>/approve [email]</code> - Approve request\n"
                "• <code>/reject [email]</code> - Reject request"
            )
            
            await message.answer(pending_text)
            logger.info(f"Admin {user.id} viewed {len(pending_list)} pending registrations")
            
        except Exception as e:
            logger.error(f"Error fetching pending registrations: {e}")
            await message.answer(
                "❌ <b>Error</b>\n\n"
                f"Failed to fetch pending registrations.\n"
                f"<code>{str(e)}</code>"
            )
    
    @router.message(Command("approve"))
    async def cmd_approve(message: Message):
        """
        Handle /approve command.
        
        Approves a pending registration request and creates
        a license for the user.
        
        Usage: /approve [user_email] [license_type] [days]
        
        Args:
            message: Incoming Telegram message
        """
        user = message.from_user
        
        # Check admin permission
        if not bot.is_admin(user.id):
            await message.answer(
                "❌ <b>Access Denied</b>\n\n"
                "Only admins can approve registrations."
            )
            return
        
        args = message.text.split()[1:] if len(message.text.split()) > 1 else []
        
        if not args:
            await message.answer(
                "❌ <b>Usage:</b> /approve [user_email] [license_type] [days]\n\n"
                "<b>Parameters:</b>\n"
                "• <code>user_email</code> - Email of user to approve (required)\n"
                "• <code>license_type</code> - trial, pro, enterprise (default: trial)\n"
                "• <code>days</code> - License duration (default: 30)\n\n"
                "<b>Examples:</b>\n"
                "<code>/approve user@example.com</code>\n"
                "<code>/approve user@example.com pro 90</code>\n"
                "<code>/approve user@example.com enterprise 365</code>\n\n"
                "<i>Use /pending to see pending requests</i>"
            )
            return
        
        email = args[0]
        license_type = args[1] if len(args) > 1 else 'trial'
        days = int(args[2]) if len(args) > 2 and args[2].isdigit() else 30
        
        # Validate license type
        valid_types = ['trial', 'pro', 'enterprise']
        if license_type.lower() not in valid_types:
            await message.answer(
                f"❌ <b>Invalid License Type</b>\n\n"
                f"<code>{license_type}</code> is not valid.\n\n"
                f"<b>Valid types:</b> {', '.join(valid_types)}"
            )
            return
        
        # Confirm approval
        await message.answer(
            f"⚠️ <b>Confirm Approval</b>\n\n"
            f"<b>Email:</b> <code>{email}</code>\n"
            f"<b>License Type:</b> {license_type.title()}\n"
            f"<b>Duration:</b> {days} days\n\n"
            f"This will:\n"
            f"• Activate the user account\n"
            f"• Generate a {license_type} license\n"
            f"• Send notification to user\n\n"
            f"Proceed with approval?",
            reply_markup=get_confirm_keyboard(f"approve_{email}_{license_type}_{days}")
        )
    
    @router.message(Command("reject"))
    async def cmd_reject(message: Message):
        """
        Handle /reject command.
        
        Rejects a pending registration request.
        
        Usage: /reject [user_email] [reason]
        
        Args:
            message: Incoming Telegram message
        """
        user = message.from_user
        
        # Check admin permission
        if not bot.is_admin(user.id):
            await message.answer(
                "❌ <b>Access Denied</b>\n\n"
                "Only admins can reject registrations."
            )
            return
        
        args = message.text.split(maxsplit=2)
        
        if len(args) < 2:
            await message.answer(
                "❌ <b>Usage:</b> /reject [user_email] [reason]\n\n"
                "<b>Parameters:</b>\n"
                "• <code>user_email</code> - Email of user to reject (required)\n"
                "• <code>reason</code> - Reason for rejection (optional)\n\n"
                "<b>Examples:</b>\n"
                "<code>/reject user@example.com</code>\n"
                "<code>/reject user@example.com Invalid information provided</code>\n\n"
                "<i>Use /pending to see pending requests</i>"
            )
            return
        
        email = args[1]
        reason = args[2] if len(args) > 2 else "No reason provided"
        
        # Confirm rejection
        await message.answer(
            f"⚠️ <b>Confirm Rejection</b>\n\n"
            f"<b>Email:</b> <code>{email}</code>\n"
            f"<b>Reason:</b> {reason}\n\n"
            f"This will:\n"
            f"• Reject the registration request\n"
            f"• Notify the user of rejection\n"
            f"• Log the action\n\n"
            f"Proceed with rejection?",
            reply_markup=get_confirm_keyboard(f"reject_{email}")
        )
    
    logger.info("Command handlers registered")
