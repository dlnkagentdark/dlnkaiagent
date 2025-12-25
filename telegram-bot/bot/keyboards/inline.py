"""
dLNk Telegram Bot - Inline Keyboards

This module contains all inline keyboard builders for the bot.
"""

from typing import Optional
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    """
    Get a confirm/cancel inline keyboard.
    
    Args:
        action: Action identifier to include in callback data
        
    Returns:
        InlineKeyboardMarkup with confirm and cancel buttons
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Confirm",
                callback_data=f"confirm_{action}"
            ),
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel"
            )
        ]
    ])


def get_main_menu_inline() -> InlineKeyboardMarkup:
    """
    Get the main menu inline keyboard.
    
    Returns:
        InlineKeyboardMarkup with main menu options
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 Status", callback_data="menu_status"),
            InlineKeyboardButton(text="👥 Users", callback_data="menu_users")
        ],
        [
            InlineKeyboardButton(text="🔑 Licenses", callback_data="menu_licenses"),
            InlineKeyboardButton(text="📋 Logs", callback_data="menu_logs")
        ],
        [
            InlineKeyboardButton(text="⚙️ Settings", callback_data="menu_settings")
        ],
        [
            InlineKeyboardButton(text="🔄 Refresh", callback_data="refresh"),
            InlineKeyboardButton(text="❌ Close", callback_data="close")
        ]
    ])


def get_quick_create_keyboard() -> InlineKeyboardMarkup:
    """
    Get the quick create license keyboard.
    
    Returns:
        InlineKeyboardMarkup with license type options
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🆓 Trial (7 days)",
                callback_data="create_trial"
            ),
            InlineKeyboardButton(
                text="📦 Basic (30 days)",
                callback_data="create_basic"
            )
        ],
        [
            InlineKeyboardButton(
                text="⭐ Pro (90 days)",
                callback_data="create_pro"
            ),
            InlineKeyboardButton(
                text="🏢 Enterprise (365 days)",
                callback_data="create_enterprise"
            )
        ],
        [
            InlineKeyboardButton(
                text="❌ Cancel",
                callback_data="cancel"
            )
        ]
    ])


def get_alert_settings_keyboard() -> InlineKeyboardMarkup:
    """
    Get the alert settings keyboard.
    
    Returns:
        InlineKeyboardMarkup with alert setting options
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔔 Toggle Alerts",
                callback_data="alert_toggle"
            )
        ],
        [
            InlineKeyboardButton(
                text="🛡️ Security",
                callback_data="alert_security"
            ),
            InlineKeyboardButton(
                text="🔑 License",
                callback_data="alert_license"
            ),
            InlineKeyboardButton(
                text="⚙️ System",
                callback_data="alert_system"
            )
        ],
        [
            InlineKeyboardButton(
                text="1️⃣ Low",
                callback_data="alert_severity_1"
            ),
            InlineKeyboardButton(
                text="2️⃣ Medium",
                callback_data="alert_severity_2"
            ),
            InlineKeyboardButton(
                text="3️⃣ High",
                callback_data="alert_severity_3"
            ),
            InlineKeyboardButton(
                text="4️⃣ Critical",
                callback_data="alert_severity_4"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 Back to Menu",
                callback_data="menu_main"
            )
        ]
    ])


def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    data_type: str
) -> InlineKeyboardMarkup:
    """
    Get a pagination keyboard.
    
    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        data_type: Type of data being paginated (users, licenses, logs)
        
    Returns:
        InlineKeyboardMarkup with pagination buttons
    """
    buttons = []
    
    # Previous button
    if current_page > 1:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️ Previous",
                callback_data=f"page_{data_type}_{current_page - 1}"
            )
        )
    
    # Page indicator
    buttons.append(
        InlineKeyboardButton(
            text=f"📄 {current_page}/{total_pages}",
            callback_data="noop"
        )
    )
    
    # Next button
    if current_page < total_pages:
        buttons.append(
            InlineKeyboardButton(
                text="Next ➡️",
                callback_data=f"page_{data_type}_{current_page + 1}"
            )
        )
    
    return InlineKeyboardMarkup(inline_keyboard=[
        buttons,
        [
            InlineKeyboardButton(
                text="🏠 Back to Menu",
                callback_data="menu_main"
            )
        ]
    ])


def get_user_actions_keyboard(user_id: str) -> InlineKeyboardMarkup:
    """
    Get user action buttons.
    
    Args:
        user_id: User ID for actions
        
    Returns:
        InlineKeyboardMarkup with user action buttons
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 View Details",
                callback_data=f"user_details_{user_id}"
            ),
            InlineKeyboardButton(
                text="🔑 View Licenses",
                callback_data=f"user_licenses_{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🚫 Ban User",
                callback_data=f"ban_{user_id}"
            ),
            InlineKeyboardButton(
                text="📧 Send Message",
                callback_data=f"message_{user_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 Back",
                callback_data="menu_users"
            )
        ]
    ])


def get_license_actions_keyboard(license_key: str) -> InlineKeyboardMarkup:
    """
    Get license action buttons.
    
    Args:
        license_key: License key for actions
        
    Returns:
        InlineKeyboardMarkup with license action buttons
    """
    # Truncate key for callback data (max 64 bytes)
    short_key = license_key[:30] if len(license_key) > 30 else license_key
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📋 View Details",
                callback_data=f"lic_details_{short_key}"
            ),
            InlineKeyboardButton(
                text="👤 View Owner",
                callback_data=f"lic_owner_{short_key}"
            )
        ],
        [
            InlineKeyboardButton(
                text="⏰ Extend",
                callback_data=f"extend_{short_key}_30"
            ),
            InlineKeyboardButton(
                text="🚫 Revoke",
                callback_data=f"revoke_{short_key}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏠 Back",
                callback_data="menu_licenses"
            )
        ]
    ])


def get_yes_no_keyboard(action: str) -> InlineKeyboardMarkup:
    """
    Get a simple yes/no keyboard.
    
    Args:
        action: Action identifier
        
    Returns:
        InlineKeyboardMarkup with yes and no buttons
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="✅ Yes",
                callback_data=f"yes_{action}"
            ),
            InlineKeyboardButton(
                text="❌ No",
                callback_data=f"no_{action}"
            )
        ]
    ])


def get_back_button(callback_data: str = "menu_main") -> InlineKeyboardMarkup:
    """
    Get a simple back button.
    
    Args:
        callback_data: Callback data for the back button
        
    Returns:
        InlineKeyboardMarkup with back button
    """
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🏠 Back to Menu",
                callback_data=callback_data
            )
        ]
    ])
