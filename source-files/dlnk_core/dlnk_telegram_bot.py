#!/usr/bin/env python3
"""
dLNk Telegram Admin Bot
บอทเทเลแกรมสำหรับจัดการ License และ Admin Console
"""

import os
import sys
import asyncio
import logging
from pathlib import Path
from datetime import datetime

# Telegram imports
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
except ImportError:
    print("[!] Installing python-telegram-bot...")
    os.system("pip3 install python-telegram-bot -q")
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Import license system
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from dlnk_license_system import DLNKLicenseSystem, LicenseType, LicenseStatus

# Configuration
CONFIG_DIR = Path.home() / ".dlnk-ide"
LICENSE_DB = CONFIG_DIR / "licenses.db"
BOT_TOKEN_FILE = CONFIG_DIR / "telegram_bot_token.txt"

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('dLNk-TelegramBot')

# Admin user IDs (Telegram user IDs that can use admin commands)
ADMIN_IDS = set()
ADMIN_IDS_FILE = CONFIG_DIR / "admin_telegram_ids.txt"


def load_admin_ids():
    """Load admin Telegram IDs from file"""
    global ADMIN_IDS
    if ADMIN_IDS_FILE.exists():
        with open(ADMIN_IDS_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if line and line.isdigit():
                    ADMIN_IDS.add(int(line))
    logger.info(f"Loaded {len(ADMIN_IDS)} admin IDs")


def save_admin_ids():
    """Save admin Telegram IDs to file"""
    with open(ADMIN_IDS_FILE, 'w') as f:
        for admin_id in ADMIN_IDS:
            f.write(f"{admin_id}\n")


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    return user_id in ADMIN_IDS or len(ADMIN_IDS) == 0  # Allow all if no admins set


class DLNKTelegramBot:
    """
    dLNk Telegram Admin Bot
    """
    
    def __init__(self, token: str):
        self.token = token
        self.license_system = DLNKLicenseSystem(str(LICENSE_DB))
        self.application = None
        
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        
        welcome_text = f"""
🤖 *Welcome to dLNk Admin Bot*

Hello {user.first_name}!

This bot helps you manage dLNk licenses and users.

*Available Commands:*
/stats - View license statistics
/licenses - List all licenses
/create - Create new license
/verify <key> - Verify a license key
/revoke <key> - Revoke a license
/extend <key> <days> - Extend license
/users - List all users
/help - Show this help

Your Telegram ID: `{user.id}`
        """
        
        if not is_admin(user.id):
            welcome_text += "\n\n⚠️ *Note:* You are not registered as an admin. Contact the system administrator to get access."
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')
        
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        await self.start(update, context)
        
    async def stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
            
        stats = self.license_system.get_license_stats()
        
        stats_text = f"""
📊 *dLNk License Statistics*

*Licenses:*
├ Total: {stats['total_licenses']}
├ Active: {stats['active_licenses']} ✅
├ Expired: {stats['expired_licenses']} ⚠️
└ Revoked: {stats['revoked_licenses']} ❌

*Users:* {stats['total_users']}
*Activations:* {stats['total_activations']}

*By Type:*
"""
        for type_name, count in stats.get('by_type', {}).items():
            stats_text += f"├ {type_name}: {count}\n"
            
        await update.message.reply_text(stats_text, parse_mode='Markdown')
        
    async def licenses(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /licenses command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
            
        all_licenses = self.license_system.get_all_licenses()
        
        if not all_licenses:
            await update.message.reply_text("No licenses found.")
            return
            
        licenses_text = "🔑 *License List*\n\n"
        
        for i, lic in enumerate(all_licenses[:20], 1):  # Limit to 20
            status_emoji = "✅" if lic.status == LicenseStatus.ACTIVE else "❌"
            licenses_text += f"{i}. `{lic.key}`\n"
            licenses_text += f"   {status_emoji} {lic.license_type.value} | Expires: {lic.expires_at[:10]}\n\n"
            
        if len(all_licenses) > 20:
            licenses_text += f"\n_...and {len(all_licenses) - 20} more_"
            
        await update.message.reply_text(licenses_text, parse_mode='Markdown')
        
    async def create(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /create command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
            
        # Parse arguments
        args = context.args
        
        # Default values
        owner = "Telegram User"
        license_type = LicenseType.BASIC
        duration = 30
        
        if args:
            if len(args) >= 1:
                owner = args[0]
            if len(args) >= 2 and args[1] in ['trial', 'basic', 'pro', 'enterprise', 'admin']:
                license_type = LicenseType(args[1])
            if len(args) >= 3:
                try:
                    duration = int(args[2])
                except:
                    pass
        
        # Create license
        try:
            license_obj = self.license_system.create_license(
                user_id=str(update.effective_user.id),
                license_type=license_type,
                duration_days=duration,
                owner_name=owner
            )
            
            result_text = f"""
✅ *License Created Successfully!*

*Key:* `{license_obj.key}`
*Type:* {license_obj.license_type.value}
*Owner:* {owner}
*Expires:* {license_obj.expires_at[:10]}
*Features:* {', '.join(license_obj.features)}

*Encrypted Key (for distribution):*
```
{license_obj.encrypted_key}
```
            """
            
            await update.message.reply_text(result_text, parse_mode='Markdown')
            
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {str(e)}")
            
    async def verify(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /verify command"""
        if not context.args:
            await update.message.reply_text("Usage: /verify <license_key>")
            return
            
        key = context.args[0]
        
        valid, message, license_obj = self.license_system.verify_license(key)
        
        if valid:
            result_text = f"""
✅ *License Valid*

*Key:* `{key[:20]}...`
*Type:* {license_obj.license_type.value}
*Status:* {license_obj.status.value}
*Expires:* {license_obj.expires_at[:10]}
*Features:* {', '.join(license_obj.features)}
            """
        else:
            result_text = f"""
❌ *License Invalid*

*Key:* `{key[:20]}...`
*Reason:* {message}
            """
            
        await update.message.reply_text(result_text, parse_mode='Markdown')
        
    async def revoke(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /revoke command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
            
        if not context.args:
            await update.message.reply_text("Usage: /revoke <license_key>")
            return
            
        key = context.args[0]
        
        if self.license_system.revoke_license(key):
            await update.message.reply_text(f"✅ License `{key}` has been revoked.", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ License `{key}` not found.", parse_mode='Markdown')
            
    async def extend(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /extend command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
            
        if len(context.args) < 1:
            await update.message.reply_text("Usage: /extend <license_key> [days]")
            return
            
        key = context.args[0]
        days = 30
        
        if len(context.args) >= 2:
            try:
                days = int(context.args[1])
            except:
                pass
                
        if self.license_system.extend_license(key, days):
            await update.message.reply_text(f"✅ License `{key}` extended by {days} days.", parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ License `{key}` not found.", parse_mode='Markdown')
            
    async def users(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
            
        all_users = self.license_system.get_all_users()
        
        if not all_users:
            await update.message.reply_text("No users found.")
            return
            
        users_text = "👥 *User List*\n\n"
        
        for i, user in enumerate(all_users[:20], 1):
            users_text += f"{i}. *{user.username}*\n"
            users_text += f"   Role: {user.role} | Email: {user.email or 'N/A'}\n\n"
            
        await update.message.reply_text(users_text, parse_mode='Markdown')
        
    async def add_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addadmin command"""
        # Only existing admins can add new admins
        if ADMIN_IDS and not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
            
        if not context.args:
            await update.message.reply_text("Usage: /addadmin <telegram_user_id>")
            return
            
        try:
            new_admin_id = int(context.args[0])
            ADMIN_IDS.add(new_admin_id)
            save_admin_ids()
            await update.message.reply_text(f"✅ User ID `{new_admin_id}` added as admin.", parse_mode='Markdown')
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Must be a number.")
            
    async def remove_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removeadmin command"""
        if not is_admin(update.effective_user.id):
            await update.message.reply_text("⛔ Access denied. Admin only.")
            return
            
        if not context.args:
            await update.message.reply_text("Usage: /removeadmin <telegram_user_id>")
            return
            
        try:
            admin_id = int(context.args[0])
            if admin_id in ADMIN_IDS:
                ADMIN_IDS.remove(admin_id)
                save_admin_ids()
                await update.message.reply_text(f"✅ User ID `{admin_id}` removed from admins.", parse_mode='Markdown')
            else:
                await update.message.reply_text(f"❌ User ID `{admin_id}` is not an admin.", parse_mode='Markdown')
        except ValueError:
            await update.message.reply_text("❌ Invalid user ID. Must be a number.")
            
    async def myid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /myid command"""
        user = update.effective_user
        await update.message.reply_text(
            f"Your Telegram ID: `{user.id}`\nUsername: @{user.username or 'N/A'}",
            parse_mode='Markdown'
        )
        
    async def quick_create(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard for quick license creation"""
        keyboard = [
            [
                InlineKeyboardButton("Trial (7 days)", callback_data="create_trial"),
                InlineKeyboardButton("Basic (30 days)", callback_data="create_basic"),
            ],
            [
                InlineKeyboardButton("Pro (90 days)", callback_data="create_pro"),
                InlineKeyboardButton("Enterprise (365 days)", callback_data="create_enterprise"),
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("🔑 Quick Create License:", reply_markup=reply_markup)
        
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if not is_admin(query.from_user.id):
            await query.edit_message_text("⛔ Access denied. Admin only.")
            return
            
        data = query.data
        
        if data.startswith("create_"):
            type_map = {
                "create_trial": (LicenseType.TRIAL, 7),
                "create_basic": (LicenseType.BASIC, 30),
                "create_pro": (LicenseType.PRO, 90),
                "create_enterprise": (LicenseType.ENTERPRISE, 365),
            }
            
            if data in type_map:
                license_type, duration = type_map[data]
                
                license_obj = self.license_system.create_license(
                    user_id=str(query.from_user.id),
                    license_type=license_type,
                    duration_days=duration,
                    owner_name=f"TG_{query.from_user.id}"
                )
                
                result_text = f"""
✅ *{license_type.value.upper()} License Created!*

*Key:* `{license_obj.key}`
*Expires:* {license_obj.expires_at[:10]}

*Encrypted Key:*
```
{license_obj.encrypted_key}
```
                """
                
                await query.edit_message_text(result_text, parse_mode='Markdown')
                
    def run(self):
        """Run the bot"""
        load_admin_ids()
        
        self.application = Application.builder().token(self.token).build()
        
        # Add handlers
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("stats", self.stats))
        self.application.add_handler(CommandHandler("licenses", self.licenses))
        self.application.add_handler(CommandHandler("create", self.create))
        self.application.add_handler(CommandHandler("quick", self.quick_create))
        self.application.add_handler(CommandHandler("verify", self.verify))
        self.application.add_handler(CommandHandler("revoke", self.revoke))
        self.application.add_handler(CommandHandler("extend", self.extend))
        self.application.add_handler(CommandHandler("users", self.users))
        self.application.add_handler(CommandHandler("addadmin", self.add_admin))
        self.application.add_handler(CommandHandler("removeadmin", self.remove_admin))
        self.application.add_handler(CommandHandler("myid", self.myid))
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        logger.info("Starting dLNk Telegram Bot...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='dLNk Telegram Admin Bot')
    parser.add_argument('--token', help='Telegram Bot Token')
    parser.add_argument('--add-admin', type=int, help='Add admin by Telegram user ID')
    
    args = parser.parse_args()
    
    # Get token
    token = args.token
    
    if not token:
        if BOT_TOKEN_FILE.exists():
            with open(BOT_TOKEN_FILE, 'r') as f:
                token = f.read().strip()
        else:
            token = os.environ.get('DLNK_TELEGRAM_BOT_TOKEN')
            
    if args.add_admin:
        load_admin_ids()
        ADMIN_IDS.add(args.add_admin)
        save_admin_ids()
        print(f"Added admin ID: {args.add_admin}")
        return
            
    if not token:
        print("Error: No bot token provided.")
        print("Usage: python dlnk_telegram_bot.py --token YOUR_BOT_TOKEN")
        print("Or set DLNK_TELEGRAM_BOT_TOKEN environment variable")
        print(f"Or create token file at: {BOT_TOKEN_FILE}")
        return
        
    # Save token for future use
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(BOT_TOKEN_FILE, 'w') as f:
        f.write(token)
        
    bot = DLNKTelegramBot(token)
    bot.run()


if __name__ == "__main__":
    main()
