#!/usr/bin/env python3
"""
dLNk Telegram Bot - Main Entry Point

This is the main entry point for the dLNk Admin Telegram Bot.
It initializes the bot and starts polling for updates.

Usage:
    python main.py
    
Environment Variables:
    DLNK_TELEGRAM_BOT_TOKEN: Bot token from BotFather
    DLNK_ADMIN_CHAT_IDS: Comma-separated admin user IDs
"""

import asyncio
import logging
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config import (
    BOT_TOKEN, 
    ADMIN_CHAT_IDS, 
    LogConfig,
    DatabaseConfig
)
from bot.bot import DLNkBot

# Setup logging
logging.basicConfig(
    level=getattr(logging, LogConfig.LEVEL),
    format=LogConfig.FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout),
        *([logging.FileHandler(LogConfig.LOG_FILE)] if LogConfig.LOG_FILE else [])
    ]
)
logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    
    # Validate configuration
    if not BOT_TOKEN:
        logger.error("❌ DLNK_TELEGRAM_BOT_TOKEN is not set!")
        logger.error("Please set the environment variable or create a .env file")
        sys.exit(1)
    
    if not ADMIN_CHAT_IDS:
        logger.warning("⚠️ No admin chat IDs configured. Bot will be open to all users.")
    else:
        logger.info(f"✅ Configured {len(ADMIN_CHAT_IDS)} admin(s)")
    
    # Ensure database directory exists
    DatabaseConfig.ensure_db_dir()
    
    # Create and start bot
    bot = DLNkBot(
        token=BOT_TOKEN,
        admin_chat_ids=ADMIN_CHAT_IDS
    )
    
    logger.info("🚀 Starting dLNk Telegram Bot...")
    logger.info(f"📡 Bot configured with {len(ADMIN_CHAT_IDS)} admin(s)")
    
    try:
        await bot.start()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Bot crashed: {e}")
        raise


def run():
    """Synchronous entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
