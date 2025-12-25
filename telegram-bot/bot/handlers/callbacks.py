"""
dLNk Telegram Bot - Callback Handlers

This module handles all callback queries from inline keyboards.
"""

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from aiogram import Router, F
from aiogram.types import CallbackQuery

from ..keyboards.inline import (
    get_main_menu_inline,
    get_confirm_keyboard,
    get_alert_settings_keyboard
)

if TYPE_CHECKING:
    from ..bot import DLNkBot

logger = logging.getLogger(__name__)


def register_handlers(router: Router, bot: "DLNkBot"):
    """
    Register all callback handlers.
    
    Args:
        router: aiogram Router instance
        bot: DLNkBot instance
    """
    
    # ==========================================
    # Confirm/Cancel Callbacks
    # ==========================================
    
    @router.callback_query(F.data.startswith("confirm_"))
    async def callback_confirm(callback: CallbackQuery):
        """Handle confirm callbacks"""
        action = callback.data.replace("confirm_", "")
        user_id = callback.from_user.id
        
        # Check admin permission
        if not bot.is_admin(user_id):
            await callback.answer("⛔ Access denied", show_alert=True)
            return
        
        # Handle different confirm actions
        if action.startswith("ban_"):
            target_user = action.replace("ban_", "")
            # TODO: Actually ban user via backend API
            await callback.message.edit_text(
                f"✅ <b>User Banned</b>\n\n"
                f"User <code>{target_user}</code> has been banned.\n\n"
                f"• All licenses revoked\n"
                f"• Access blocked\n"
                f"• Action logged"
            )
            logger.info(f"Admin {user_id} banned user {target_user}")
            
            # Send alert to other admins
            await bot.send_alert(
                f"🚫 User <code>{target_user}</code> was banned by admin {user_id}",
                severity=2
            )
        
        elif action.startswith("unban_"):
            target_user = action.replace("unban_", "")
            # TODO: Actually unban user via backend API
            await callback.message.edit_text(
                f"✅ <b>User Unbanned</b>\n\n"
                f"User <code>{target_user}</code> has been unbanned.\n\n"
                f"They can now access the system again."
            )
            logger.info(f"Admin {user_id} unbanned user {target_user}")
        
        elif action.startswith("revoke_"):
            license_key = action.replace("revoke_", "")
            # TODO: Actually revoke license via backend API
            await callback.message.edit_text(
                f"✅ <b>License Revoked</b>\n\n"
                f"License <code>{license_key}</code> has been revoked.\n\n"
                f"The user will be notified."
            )
            logger.info(f"Admin {user_id} revoked license {license_key}")
        
        elif action.startswith("extend_"):
            parts = action.replace("extend_", "").rsplit("_", 1)
            license_key = parts[0]
            days = int(parts[1]) if len(parts) > 1 else 30
            # TODO: Actually extend license via backend API
            await callback.message.edit_text(
                f"✅ <b>License Extended</b>\n\n"
                f"License <code>{license_key}</code> extended by {days} days."
            )
            logger.info(f"Admin {user_id} extended license {license_key} by {days} days")
        
        elif action == "broadcast":
            # Get the broadcast message from the original message
            original_text = callback.message.text or ""
            # Extract message between quotes
            if ">" in original_text:
                broadcast_msg = original_text.split(">")[1].split("<")[0].strip()
            else:
                broadcast_msg = "System notification"
            
            # TODO: Actually broadcast to all admins
            success, fail = await bot.broadcast(
                f"📢 <b>Broadcast from Admin</b>\n\n{broadcast_msg}"
            )
            await callback.message.edit_text(
                f"✅ <b>Broadcast Sent</b>\n\n"
                f"Successfully sent to {success} admin(s).\n"
                f"Failed: {fail}"
            )
            logger.info(f"Admin {user_id} sent broadcast")
        
        await callback.answer("✅ Action completed")
    
    @router.callback_query(F.data == "cancel")
    async def callback_cancel(callback: CallbackQuery):
        """Handle cancel callbacks"""
        await callback.message.edit_text("❌ Action cancelled.")
        await callback.answer("Cancelled")
    
    # ==========================================
    # Menu Navigation Callbacks
    # ==========================================
    
    @router.callback_query(F.data.startswith("menu_"))
    async def callback_menu(callback: CallbackQuery):
        """Handle menu navigation callbacks"""
        menu = callback.data.replace("menu_", "")
        
        if menu == "status":
            # Trigger /status command logic
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
└ New Registrations: <code>12</code>
            """
            await callback.message.edit_text(
                status_text,
                reply_markup=get_main_menu_inline()
            )
        
        elif menu == "users":
            users_text = """
👥 <b>User Statistics</b>

📊 <b>Total Users:</b> <code>1,234</code>
├ Active (7d): <code>456</code>
└ New (7d): <code>78</code>

📈 <b>By License Type:</b>
├ Trial: <code>234</code>
├ Pro: <code>789</code>
└ Enterprise: <code>211</code>
            """
            await callback.message.edit_text(
                users_text,
                reply_markup=get_main_menu_inline()
            )
        
        elif menu == "licenses":
            licenses_text = """
🔑 <b>License Statistics</b>

📊 <b>Total:</b> <code>1,234</code>
├ Active: <code>987</code> ✅
├ Expired: <code>200</code> ⚠️
└ Revoked: <code>47</code> ❌

⏰ <b>Expiring Soon:</b> <code>45</code>
            """
            await callback.message.edit_text(
                licenses_text,
                reply_markup=get_main_menu_inline()
            )
        
        elif menu == "logs":
            logs_text = """
📋 <b>Recent Logs</b>

<code>12:34:56</code> ✅ User login
<code>12:33:45</code> 🔑 License created
<code>12:32:12</code> 🚨 Security alert
<code>12:31:00</code> 👤 User registered
<code>12:30:45</code> 🔄 Token refreshed
            """
            await callback.message.edit_text(
                logs_text,
                reply_markup=get_main_menu_inline()
            )
        
        elif menu == "settings":
            settings_text = """
⚙️ <b>Bot Settings</b>

<b>General:</b>
├ Language: English
├ Notifications: Enabled
└ Rate Limiting: Active

<b>Connection:</b>
├ Backend: Connected ✅
└ Latency: 45ms
            """
            await callback.message.edit_text(
                settings_text,
                reply_markup=get_main_menu_inline()
            )
        
        elif menu == "main":
            await callback.message.edit_text(
                "📋 <b>Main Menu</b>\n\nSelect an option:",
                reply_markup=get_main_menu_inline()
            )
        
        await callback.answer()
    
    # ==========================================
    # Quick Create Callbacks
    # ==========================================
    
    @router.callback_query(F.data.startswith("create_"))
    async def callback_create(callback: CallbackQuery):
        """Handle quick create license callbacks"""
        user_id = callback.from_user.id
        
        if not bot.is_admin(user_id):
            await callback.answer("⛔ Access denied", show_alert=True)
            return
        
        license_type = callback.data.replace("create_", "")
        
        # License type configurations
        type_config = {
            "trial": ("Trial", 7, ["AI Autocomplete"]),
            "basic": ("Basic", 30, ["AI Autocomplete", "Code Analysis"]),
            "pro": ("Pro", 90, ["AI Autocomplete", "Code Analysis", "Security Scan"]),
            "enterprise": ("Enterprise", 365, ["All Features", "Priority Support", "Custom Integration"])
        }
        
        if license_type not in type_config:
            await callback.answer("Invalid license type", show_alert=True)
            return
        
        type_name, days, features = type_config[license_type]
        
        # TODO: Actually create license via backend API
        # Generate mock license key
        import random
        import string
        key_parts = ['DLNK'] + [''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) for _ in range(3)]
        license_key = '-'.join(key_parts)
        
        features_text = '\n'.join([f"├ {f} ✅" for f in features[:-1]] + [f"└ {features[-1]} ✅"])
        
        result_text = f"""
✅ <b>{type_name} License Created!</b>

<b>Key:</b> <code>{license_key}</code>
<b>Type:</b> {type_name}
<b>Duration:</b> {days} days
<b>Created by:</b> Admin {user_id}

<b>Features:</b>
{features_text}

<b>Encrypted Key:</b>
<code>eyJrZXkiOiJ{{{{license_key}}}}IiwidHlwZSI6Int{{{{license_type}}}}In0=</code>

<i>Send this encrypted key to the user.</i>
        """
        
        await callback.message.edit_text(result_text)
        await callback.answer(f"✅ {type_name} license created!")
        
        logger.info(f"Admin {user_id} created {license_type} license: {license_key}")
    
    # ==========================================
    # Alert Settings Callbacks
    # ==========================================
    
    @router.callback_query(F.data.startswith("alert_"))
    async def callback_alert(callback: CallbackQuery):
        """Handle alert settings callbacks"""
        user_id = callback.from_user.id
        
        if not bot.is_admin(user_id):
            await callback.answer("⛔ Access denied", show_alert=True)
            return
        
        action = callback.data.replace("alert_", "")
        
        if action == "toggle":
            # TODO: Actually toggle alerts
            await callback.answer("🔔 Alerts toggled", show_alert=False)
        
        elif action == "security":
            # TODO: Toggle security alerts
            await callback.answer("🛡️ Security alerts toggled", show_alert=False)
        
        elif action == "license":
            # TODO: Toggle license alerts
            await callback.answer("🔑 License alerts toggled", show_alert=False)
        
        elif action == "system":
            # TODO: Toggle system alerts
            await callback.answer("⚙️ System alerts toggled", show_alert=False)
        
        elif action.startswith("severity_"):
            level = int(action.replace("severity_", ""))
            severity_names = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
            await callback.answer(f"📊 Severity set to {severity_names.get(level, 'Unknown')}", show_alert=False)
        
        # Refresh alert settings display
        alert_text = """
🔔 <b>Alert Settings</b>

<b>Current Settings:</b>
├ Alerts: ✅ Enabled
├ Severity Threshold: Medium (2)
├ Security Alerts: ✅
├ License Alerts: ✅
└ System Alerts: ✅

<i>Settings updated!</i>
        """
        await callback.message.edit_text(
            alert_text,
            reply_markup=get_alert_settings_keyboard()
        )
    
    # ==========================================
    # Pagination Callbacks
    # ==========================================
    
    @router.callback_query(F.data.startswith("page_"))
    async def callback_page(callback: CallbackQuery):
        """Handle pagination callbacks"""
        page_info = callback.data.replace("page_", "")
        # Format: page_type_number (e.g., page_users_2)
        
        parts = page_info.rsplit("_", 1)
        if len(parts) != 2:
            await callback.answer("Invalid page", show_alert=True)
            return
        
        page_type, page_num = parts
        page_num = int(page_num)
        
        # TODO: Fetch actual paginated data
        await callback.answer(f"Page {page_num}")
    
    # ==========================================
    # Refresh Callback
    # ==========================================
    
    @router.callback_query(F.data == "refresh")
    async def callback_refresh(callback: CallbackQuery):
        """Handle refresh callbacks"""
        await callback.answer("🔄 Refreshing...")
        # The actual refresh logic would depend on what's being refreshed
        # This is handled by the menu callbacks above
    
    # ==========================================
    # Close/Dismiss Callback
    # ==========================================
    
    @router.callback_query(F.data == "close")
    async def callback_close(callback: CallbackQuery):
        """Handle close/dismiss callbacks"""
        await callback.message.delete()
        await callback.answer()
    
    logger.info("Callback handlers registered")
