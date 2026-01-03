# Made by @xchup
# Pyrogram File Sharing Bot with Expiring Links

import os
import time
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_ID = int(os.getenv("ADMIN_ID"))          # single admin
DB_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))   # private storage channel

FORCE_CHANNELS = [
    -1003599850450,   # channel 1 ID
    -1001234567890    # channel 2 ID (add more if needed)
]

LINK_EXPIRY = 600  # 10 minutes (seconds)

# ================= BOT =================

app = Client(
    "filesharebot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN
)

# In-memory link store
LINKS = {}  # token: (message_id, expire_time)

# ================= HELPERS =================

async def is_joined(user_id):
    for ch in FORCE_CHANNELS:
        try:
            member = await app.get_chat_member(ch, user_id)
            if member.status not in ("member", "administrator", "owner"):
                return False
        except:
            return False
    return True


def join_buttons():
    buttons = []
    for i, ch in enumerate(FORCE_CHANNELS, start=1):
        buttons.append([
            InlineKeyboardButton(
                f"Channel {i}",
                url=f"https://t.me/c/{str(ch)[4:]}"
            )
        ])
    buttons.append([InlineKeyboardButton("📥 Get File", callback_data="recheck")])
    return InlineKeyboardMarkup(buttons)


# ================= START =================

@app.on_message(filters.command("start"))
async def start(client, message):
    args = message.command

    if len(args) == 2:
        token = args[1]

        if token not in LINKS:
            return await message.reply("❌ Link expired or invalid.")

        msg_id, exp = LINKS[token]
        if time.time() > exp:
            LINKS.pop(token, None)
            return await message.reply("⌛ This link has expired.")

        if not await is_joined(message.from_user.id):
            return await message.reply(
                "🔒 Join all channels to get the file:",
                reply_markup=join_buttons()
            )

        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=DB_CHANNEL_ID,
            message_id=msg_id
        )
        return

    await message.reply("👋 Welcome!\nSend me a Telegram file link (admin only).")


# ================= RECHECK =================

@app.on_callback_query(filters.regex("recheck"))
async def recheck(client, query):
    if await is_joined(query.from_user.id):
        await query.message.edit_text(
            "✅ Verified!\nNow open the download link again."
        )
    else:
        await query.answer("❌ Join all channels first!", show_alert=True)


# ================= ADMIN LINK CREATION =================

@app.on_message(filters.private & filters.text)
async def admin_handler(client, message):
    if message.from_user.id != ADMIN_ID:
        return

    if "t.me/c/" not in message.text:
        return await message.reply("❌ Send a Telegram private file link.")

    try:
        msg_id = int(message.text.split("/")[-1])
    except:
        return await message.reply("❌ Invalid link.")

    token = str(int(time.time() * 1000))
    LINKS[token] = (msg_id, time.time() + LINK_EXPIRY)

    await message.reply(
        f"✅ Download link (expires in 10 minutes):\n\n"
        f"https://t.me/{(await client.get_me()).username}?start={token}"
    )


# ================= DUMMY SERVER (RENDER FREE) =================

from flask import Flask
from threading import Thread

web = Flask(__name__)

@web.route("/")
def home():
    return "Bot is alive"

def run_web():
    web.run(host="0.0.0.0", port=10000)

Thread(target=run_web).start()

# ================= RUN =================

app.run()

