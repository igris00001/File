# Made by @xchup
import telebot
import os
import re
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= DUMMY HTTP SERVER (RENDER FREE) =================

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

# ================= BOT CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
ADMIN_ID = int(os.getenv("ADMIN_ID"))

FORCE_CHANNELS = [
    "@Letsucks",
    "@USRxMEE"
]

LINK_EXPIRY_SECONDS = 10 * 60  # 10 minutes

bot = telebot.TeleBot(BOT_TOKEN)
LINK_RE = re.compile(r"t\.me/c/\d+/(\d+)")

USERS_FILE = "users.json"
LINKS_FILE = "links.json"

# ================= INIT FILES =================

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w") as f:
        json.dump([], f)

if not os.path.exists(LINKS_FILE):
    with open(LINKS_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USERS_FILE) as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, "w") as f:
        json.dump(data, f, indent=2)

def add_user(uid):
    users = load_users()
    if uid not in users:
        users.append(uid)
        save_users(users)

def load_links():
    with open(LINKS_FILE) as f:
        return json.load(f)

def save_links(data):
    with open(LINKS_FILE, "w") as f:
        json.dump(data, f, indent=2)

# ================= FORCE JOIN =================

def is_joined(user_id):
    for ch in FORCE_CHANNELS:
        try:
            status = bot.get_chat_member(ch, user_id).status
            if status not in ("member", "administrator", "creator"):
                return False
        except:
            return False
    return True

def join_buttons(code):
    kb = InlineKeyboardMarkup(row_width=1)
    for i, ch in enumerate(FORCE_CHANNELS, start=1):
        kb.add(
            InlineKeyboardButton(
                f"𝐂𝐡𝐚𝐧𝐧𝐞𝐥 {i}️⃣",
                url=f"https://t.me/{ch[1:]}"
            )
        )
    kb.add(
        InlineKeyboardButton(
            "📥 Get File",
            callback_data=f"get_{code}"
        )
    )
    return kb

# ================= CALLBACK =================

@bot.callback_query_handler(func=lambda c: c.data.startswith("get_"))
def get_file(call):
    code = call.data.split("_", 1)[1]
    links = load_links()

    if code not in links:
        bot.answer_callback_query(call.id, "❌ Link expired", show_alert=True)
        return

    data = links[code]
    if time.time() > data["expires"]:
        del links[code]
        save_links(links)
        bot.answer_callback_query(call.id, "❌ Link expired", show_alert=True)
        return

    if not is_joined(call.from_user.id):
        bot.answer_callback_query(call.id, "❌ Join all channels first!", show_alert=True)
        return

    bot.copy_message(
        call.message.chat.id,
        CHANNEL_ID,
        data["message_id"]
    )

# ================= START =================

@bot.message_handler(commands=["start"])
def start(msg):
    add_user(msg.from_user.id)
    args = msg.text.split()

    if len(args) == 2:
        code = args[1]
        links = load_links()

        if code not in links:
            bot.reply_to(msg, "❌ Link expired.")
            return

        data = links[code]
        if time.time() > data["expires"]:
            del links[code]
            save_links(links)
            bot.reply_to(msg, "❌ Link expired.")
            return

        if not is_joined(msg.from_user.id):
            bot.send_message(
                msg.chat.id,
                "🔒 Join all channels to get the file:",
                reply_markup=join_buttons(code)
            )
            return

        bot.copy_message(msg.chat.id, CHANNEL_ID, data["message_id"])
    else:
        bot.reply_to(msg, "👋 Welcome!")

# ================= ADMIN =================

@bot.message_handler(func=lambda m: True)
def admin_handler(msg):
    add_user(msg.from_user.id)

    if msg.from_user.id != ADMIN_ID:
        return

    # Broadcast
    if msg.text and msg.text.startswith("/broadcast"):
        users = load_users()
        sent = 0
        for uid in users:
            try:
                if msg.reply_to_message:
                    bot.copy_message(uid, msg.chat.id, msg.reply_to_message.message_id)
                else:
                    text = msg.text.replace("/broadcast", "").strip()
                    if text:
                        bot.send_message(uid, text)
                sent += 1
            except:
                pass
        bot.reply_to(msg, f"✅ Broadcast sent to {sent} users.")
        return

    # Create link
    match = LINK_RE.search(msg.text or "")
    if not match:
        return

    message_id = int(match.group(1))
    links = load_links()

    code = str(int(time.time() * 1000))
    links[code] = {
        "message_id": message_id,
        "expires": time.time() + LINK_EXPIRY_SECONDS
    }
    save_links(links)

    bot.reply_to(
        msg,
        f"✅ Download link (expires in 10 minutes):\n\n"
        f"https://t.me/{bot.get_me().username}?start={code}"
    )

# ================= RUN =================

bot.infinity_polling()
