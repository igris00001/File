# Made by @xchup

import os
import time
import re
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ========= CONFIG =========
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # private storage channel

FORCE_CHANNELS = [
    ("Channel 1️⃣", "https://t.me/Letsucks"),
    ("Channel 2️⃣", "https://t.me/USRxMEE")
]

LINK_EXPIRY = 600  # 10 minutes

# ==========================
bot = telebot.TeleBot(BOT_TOKEN, threaded=False)
app = Flask(__name__)

LINK_RE = re.compile(r"t.me/c/\d+/(\d+)")

# store expiry
links = {}

# ========= FORCE JOIN =========
def joined(user_id):
    for _, url in FORCE_CHANNELS:
        try:
            chat = url.split("/")[-1]
            status = bot.get_chat_member(f"@{chat}", user_id).status
            if status not in ["member", "administrator", "creator"]:
                return False
        except:
            return False
    return True

def join_buttons():
    kb = InlineKeyboardMarkup()
    for name, url in FORCE_CHANNELS:
        kb.add(InlineKeyboardButton(name, url=url))
    kb.add(InlineKeyboardButton("✅ Joined", callback_data="check"))
    return kb

@bot.callback_query_handler(func=lambda c: c.data == "check")
def recheck(c):
    if joined(c.from_user.id):
        bot.answer_callback_query(c.id, "Verified ✅")
        bot.delete_message(c.message.chat.id, c.message.message_id)
    else:
        bot.answer_callback_query(c.id, "Join all channels ❌", show_alert=True)

# ========= START =========
@bot.message_handler(commands=["start"])
def start(m):
    args = m.text.split()

    if len(args) == 2:
        key = args[1]

        if key not in links:
            bot.send_message(m.chat.id, "❌ Link expired or invalid")
            return

        msg_id, expiry = links[key]
        if time.time() > expiry:
            del links[key]
            bot.send_message(m.chat.id, "⏰ Link expired")
            return

        if not joined(m.from_user.id):
            bot.send_message(
                m.chat.id,
                "🔒 Join required:",
                reply_markup=join_buttons()
            )
            return

        bot.copy_message(m.chat.id, CHANNEL_ID, msg_id)
        return

    bot.send_message(m.chat.id, "👋 Welcome!")

# ========= ADMIN LINK =========
@bot.message_handler(func=lambda m: m.from_user.id == ADMIN_ID)
def admin(m):
    match = LINK_RE.search(m.text or "")
    if not match:
        return

    msg_id = int(match.group(1))
    key = str(int(time.time()))
    links[key] = (msg_id, time.time() + LINK_EXPIRY)

    bot.reply_to(
        m,
        f"✅ Download link (10 min):\n"
        f"https://t.me/{bot.get_me().username}?start={key}"
    )

# ========= WEBHOOK =========
@app.route("/", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def home():
    return "Bot running"

# ========= START =========
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=os.getenv("WEBHOOK_URL"))
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 10000)))
