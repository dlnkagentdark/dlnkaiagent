"""
dLNk Telegram Bot - Main Menu Keyboard

This module contains the reply keyboard for the main menu.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get the main menu reply keyboard.
    
    Returns:
        ReplyKeyboardMarkup with main menu buttons
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 Status"),
                KeyboardButton(text="👥 Users"),
                KeyboardButton(text="🔑 Licenses")
            ],
            [
                KeyboardButton(text="📋 Logs"),
                KeyboardButton(text="🔔 Alerts"),
                KeyboardButton(text="⚙️ Settings")
            ],
            [
                KeyboardButton(text="🆕 Quick Create"),
                KeyboardButton(text="🔍 Search")
            ],
            [
                KeyboardButton(text="❓ Help")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
        input_field_placeholder="Select an option or type a command..."
    )
    return keyboard


def get_admin_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get the admin-specific menu keyboard.
    
    Returns:
        ReplyKeyboardMarkup with admin menu buttons
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="📊 System Status"),
                KeyboardButton(text="👥 User Management")
            ],
            [
                KeyboardButton(text="🔑 License Management"),
                KeyboardButton(text="📋 View Logs")
            ],
            [
                KeyboardButton(text="🔔 Alert Settings"),
                KeyboardButton(text="⚙️ Bot Settings")
            ],
            [
                KeyboardButton(text="📢 Broadcast"),
                KeyboardButton(text="👤 Admin List")
            ],
            [
                KeyboardButton(text="🏠 Main Menu")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """
    Get a simple cancel keyboard.
    
    Returns:
        ReplyKeyboardMarkup with cancel button
    """
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="❌ Cancel")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def remove_keyboard():
    """
    Remove the reply keyboard.
    
    Returns:
        ReplyKeyboardRemove instance
    """
    from aiogram.types import ReplyKeyboardRemove
    return ReplyKeyboardRemove()
