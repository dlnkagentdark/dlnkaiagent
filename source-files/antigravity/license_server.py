import logging
import sqlite3
import datetime
import uuid
import threading
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# --- CONFIGURATION ---
BOT_TOKEN = "8209736694:AAGdDD_ko9zq27C-gvCIDqCHAH3UnYY9RJc"
ADMIN_USER_ID = 123456789 # Placeholder: Update with actual Admin ID or use username check
ADMIN_USERNAME = "dlnkai"
SERVER_PORT = 5000
DB_FILE = "dlnk_commercial.db"

# --- FLASK APP ---
app = Flask(__name__)

# --- DATABASE ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS licenses
                 (key TEXT PRIMARY KEY, days INTEGER, status TEXT, 
                  created_at TEXT, activated_at TEXT, hwid TEXT)''')
    conn.commit()
    conn.close()

def generate_key_db(days):
    new_key = "dLNk-" + str(uuid.uuid4())[:8].upper()
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    c.execute("INSERT INTO licenses (key, days, status, created_at) VALUES (?, ?, 'READY', ?)", 
              (new_key, days, now))
    conn.commit()
    conn.close()
    return new_key

def validate_key_db(key, hwid):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    row = c.execute("SELECT days, status, hwid, activated_at FROM licenses WHERE key=?", (key,)).fetchone()
    
    if not row:
        conn.close()
        return False, "ไม่พบรหัสลิขสิทธิ์นี้"
    
    days, status, db_hwid, activated_at = row
    
    if status == 'READY':
        now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
        c.execute("UPDATE licenses SET status='ACTIVE', activated_at=?, hwid=? WHERE key=?", (now, hwid, key))
        conn.commit()
        conn.close()
        return True, "ยืนยันรหัสลิขสิทธิ์สำเร็จ"
        
    if status == 'ACTIVE':
        if db_hwid != hwid:
            conn.close()
            return False, "รหัสนี้ถูกใช้งานกับเครื่องอื่นแล้ว"
        return True, "เข้าสู่ระบบสำเร็จ"
        
    conn.close()
    return False, "รหัสหมดอายุหรือถูกระงับ"

# --- TELEGRAM BOT LOGIC ---
# --- TELEGRAM BOT (INTERACTIVE & AI) ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    if user.username == ADMIN_USERNAME:
        # ADMIN MENU
        keyboard = [
            [InlineKeyboardButton("💎 สร้างรหัส 30 วัน", callback_data='gen_30'),
             InlineKeyboardButton("👑 สร้างรหัส 1 ปี", callback_data='gen_365')],
            [InlineKeyboardButton("📊 เช็คยอดผู้ใช้", callback_data='status')],
            [InlineKeyboardButton("🤖 ปิด/เปิด AI Mode", callback_data='toggle_ai')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"👑 **สวัสดีครับ แอดมิน {user.first_name}**\nเลือกจัดการระบบได้จากปุ่มด้านล่าง หรือพิมพ์สั่งงาน AI ได้เลยครับ",
            reply_markup=reply_markup, parse_mode='Markdown'
        )
    else:
        # USER MENU
        keyboard = [
            [InlineKeyboardButton("🛒 ซื้อรหัสลิขสิทธิ์", url=f'https://t.me/{ADMIN_USERNAME}')],
            [InlineKeyboardButton("🛠️ วิธีใช้งาน IDE", callback_data='help')],
            [InlineKeyboardButton("💬 คุยกับ AI (เขียนโค้ด)", callback_data='ai_help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"👋 **ยินดีต้อนรับสู่ dLNk AI**\nกรุณาใช้คีย์เพื่อเข้าสู่ระบบ IDE หากยังไม่มีรหัส โปรดติดต่อแอดมิน",
            reply_markup=reply_markup, parse_mode='Markdown'
        )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith('gen_'):
        days = int(data.split('_')[1])
        key = generate_key_db(days)
        await query.edit_message_text(f"✅ **สร้างรหัสสำเร็จ**\nKey: `{key}`\nอายุ: {days} วัน", parse_mode='Markdown')
        
    elif data == 'status':
        conn = sqlite3.connect(DB_FILE)
        active = conn.cursor().execute("SELECT count(*) FROM licenses WHERE status='ACTIVE'").fetchone()[0]
        conn.close()
        await query.edit_message_text(f"📊 **สถิติปัจจุบัน**\nสมาชิกที่เปิดใช้งาน: `{active}` คน", parse_mode='Markdown')
        
    elif data == 'help':
        await query.edit_message_text("ℹ️ **วิธีใช้งาน:**\n1. นำรหัสที่ซื้อไปกรอกใน dLNk Launcher\n2. กดเข้าสู่ระบบ\n3. เริ่มเขียนมัลแวร์บน IDE ได้ทันที", parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # (Existing AI Chat Logic for natural language)
    text = update.message.text.lower()
    
    if "สร้าง" in text or "key" in text:
        key = generate_key_db(30)
        await update.message.reply_text(f"✅ จัดให้ครับบอส: `{key}` (30 วัน)", parse_mode='Markdown')
    elif "เขียน" in text or "code" in text or "มัลแวร์" in text:
        await update.message.reply_text("🤖 **dLNk AI Generating Code...**")
        # (Snippet logic here...)
        code = "print('dLNk AI Ready')"
        await update.message.reply_text(f"```python\n{code}\n```", parse_mode='Markdown')
    else:
        await update.message.reply_text("ผมรับคำสั่งภาษาไทยได้ครับ เช่น 'สร้างคีย์' หรือ 'เขียนโค้ด'")

# --- FLASK API ---
@app.route('/verify', methods=['POST'])
def verify():
    data = request.get_json()
    key = data.get('key')
    hwid = data.get("hwid")
    success, msg = validate_key_db(key, hwid)
    if success:
        return jsonify({"status": "success", "message": msg}), 200
    return jsonify({"status": "fail", "message": msg}), 403

def run_flask():
    app.run(host='0.0.0.0', port=SERVER_PORT)

if __name__ == "__main__":
    init_db()
    
    # Start API in thread
    api_thread = threading.Thread(target=run_flask)
    api_thread.daemon = True
    api_thread.start()
    
    # Start Bot
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("[*] dLNk Commercial Server Active.")
    application.run_polling()
