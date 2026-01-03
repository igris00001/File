# Made by @xchup

import os
import time
import re
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# =====================================================
# DUMMY HTTP SERVER (Render Free Web Service)
# =====================================================

class DummyHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_dummy_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), DummyHandler)
    server.serve_forever()

threading.Thread(target=run_dummy_server, daemon=True).start()

# =====================================================
# CONFIG
# =====================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # private storage channel

FORCE_CHANNELS = [
    ("Channel 1️⃣", "https://t.me/Letsucks"),
    ("Channel 2️⃣", "https://t.me/USRxMEE")
]

LINK_EXPIRY_SECONDS = 10 * 60  # 10 minutes

bot = telebot.TeleBot(BOT_TOKEN, threaded=False)

LINK_RE = re.compile(r"t\.me/c/\d+/(\d+)")

# key -> (message_id, expiry_time)
links = {}

# =====================================================
# FORCE JOIN CHECK
# =====================================================

def is_joined(user_id):
    for _, url in FORCE_CHANNELS:
        try:
            username = url.split("/")[-1]
            status = bot.get_chat_member(f"@{username}", user_id).status
            if status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

def join_buttons(key):
    kb = InlineKeyboardMarkup(row_width=1)
    for name, url in FORCE_CHANNELS:
        kb.add(InlineKeyboardButton(name, url=url))
    kb.add(
        InlineKeyboardButton(
            "📂 Get File",
            callback_data=f"get_{key}"
        )
    )
    return kb

# =====================================================
# CALLBACK: GET FILE
# =====================================================

@bot.callback_query_handler(func=lambda c: c.data.startswith("get_"))
def get_file(c):
    key = c.data.split("_", 1)[1]

    if key not in links:
        bot.answer_callback_query(c.id, "❌ Link expired", show_alert=True)
        return

    msg_id, expiry = links[key]
    if time.time() > expiry:
        del links[key]
        bot.answer_callback_query(c.id, "⏰ Link expired", show_alert=True)
        return

    if not is_joined(c.from_user.id):
        bot.answer_callback_query(
            c.id,
            "❌ Join all channels first!",
            show_alert=True
        )
        return

    # Clean UI (Option A)
    bot.delete_message(c.message.chat.id, c.message.message_id)

    bot.copy_message(
        c.message.chat.id,
        CHANNEL_ID,
        msg_id
    )

    bot.answer_callback_query(c.id, "📦 File sent!")

# =====================================================
# START COMMAND
# =====================================================

@bot.message_handler(commands=["start"])
def start(msg):
    args = msg.text.split()

    if len(args) == 2:
        key = args[1]

        if key not in links:
            bot.send_message(msg.chat.id, "❌ Link expired or invalid.")
            return

        msg_id, expiry = links[key]
        if time.time() > expiry:
            del links[key]
            bot.send_message(msg.chat.id, "⏰ Link expired.")
            return

        if not is_joined(msg.from_user.id):
            bot.send_message(
                msg.chat.id,
                "🔒 Join all channels to get the file:",
                reply_markup=join_buttons(key)
            )
            return

        bot.copy_message(msg.chat.id, CHANNEL_ID, msg_id)
        return

    bot.send_message(msg.chat.id, "👋 Welcome!")

# =====================================================
# ADMIN: CREATE LINK
# =====================================================

@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin_handler(m):
    match = LINK_RE.search(m.text or "")
    if not match:
        return

    message_id = int(match.group(1))
    key = str(int(time.time() * 1000))

    links[key] = (
        message_id,
        time.time() + LINK_EXPIRY_SECONDS
    )

    bot.reply_to(
        m,
        "✅ Download link (expires in 10 minutes):\n\n"
        f"https://t.me/{bot.get_me().username}?start={key}"
    )

# =====================================================
# RUN BOT
# =====================================================

bot.infinity_polling()
