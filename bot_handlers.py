# Made by @xchup
# Pyrogram File Sharing Bot Handlers
# Anyone-can-generate links + Media auto-expire + Broadcast

import time
import asyncio
import os
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait

# ================= CONFIG =================

ADMIN_ID = int(os.getenv("ADMIN_ID"))
DB_CHANNEL_ID = int(os.getenv("CHANNEL_ID"))

# Force-join channel IDs
FORCE_CHANNELS = [
    -1003638744016,  # Channel 1
    -1003594086276   # Channel 2
]

# Invite links (shown to users)
INVITE_LINKS = [
    "https://t.me/+If39xLm7SeQwZTM1",
    "https://t.me/+bdtAg0G5dLc2ODg1"
]

MEDIA_LIFETIME = 15 * 60  # 15 minutes

# ================= MEMORY STORAGE =================

LINKS = {}   # token -> message_id (PERMANENT)
USERS = set()

# ================= HELPERS =================

async def is_joined(app, user_id: int) -> bool:
    for ch in FORCE_CHANNELS:
        try:
            member = await app.get_chat_member(ch, user_id)
            if member.status not in ("member", "administrator", "owner"):
                return False
        except:
            return False
    return True


def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("𝐂𝐡𝐚𝐧𝐧𝐞𝐥 1️⃣", url=INVITE_LINKS[0])],
        [InlineKeyboardButton("𝐂𝐡𝐚𝐧𝐧𝐞𝐥 2️⃣", url=INVITE_LINKS[1])],
        [InlineKeyboardButton("📥 Get File", callback_data="get_file")]
    ])


async def auto_delete(app, chat_id, msg):
    await asyncio.sleep(MEDIA_LIFETIME)
    try:
        await msg.delete()
        await app.send_message(chat_id, "ᴍᴇᴅɪᴀ ᴇxᴩɪʀᴇᴅ")
    except:
        pass

# ================= REGISTER HANDLERS =================

def register(app):

    # ---------- /start ----------
    @app.on_message(filters.command("start"))
    async def start(_, message):
        USERS.add(message.from_user.id)
        args = message.command

        if len(args) == 2:
            token = args[1]

            if token not in LINKS:
                return await message.reply("❌ Invalid link.")

            if not await is_joined(app, message.from_user.id):
                return await message.reply(
                    "🔒 Join all channels to continue:",
                    reply_markup=join_buttons()
                )

            sent = await app.copy_message(
                chat_id=message.chat.id,
                from_chat_id=DB_CHANNEL_ID,
                message_id=LINKS[token]
            )

            asyncio.create_task(auto_delete(app, message.chat.id, sent))
            return

        await message.reply(
            "👋 Welcome!\n\n"
            "Send a Telegram file link (t.me/c/...) to generate a share link."
        )


    # ---------- Get File Button ----------
    @app.on_callback_query(filters.regex("get_file"))
    async def get_file(_, query):
        USERS.add(query.from_user.id)

        if not await is_joined(app, query.from_user.id):
            return await query.answer(
                "❌ Join all channels first!",
                show_alert=True
            )

        if "start=" not in (query.message.text or ""):
            return await query.answer("❌ Invalid session", show_alert=True)

        token = query.message.text.split("start=")[-1].strip()

        if token not in LINKS:
            return await query.answer("❌ Invalid link", show_alert=True)

        sent = await app.copy_message(
            chat_id=query.message.chat.id,
            from_chat_id=DB_CHANNEL_ID,
            message_id=LINKS[token]
        )

        await query.message.delete()
        asyncio.create_task(auto_delete(app, query.message.chat.id, sent))
        await query.answer("📦 File sent!")


    # ---------- ANY USER: GENERATE LINK ----------
    @app.on_message(filters.private & filters.text)
    async def generate_link(_, message):
        USERS.add(message.from_user.id)

        if "t.me/c/" not in message.text:
            return

        try:
            msg_id = int(message.text.split("/")[-1])
        except:
            return await message.reply("❌ Invalid Telegram file link.")

        token = str(int(time.time() * 1000))
        LINKS[token] = msg_id

        me = await app.get_me()
        await message.reply(
            "✅ Share link generated:\n\n"
            f"https://t.me/{me.username}?start={token}\n\n"
            "⏱ Media auto-expires after 15 minutes"
        )


    # ---------- BROADCAST (ADMIN ONLY) ----------
    @app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
    async def broadcast(_, message):
        if not message.reply_to_message:
            return await message.reply(
                "❌ Reply to a message with /broadcast"
            )

        sent = 0
        failed = 0

        status = await message.reply("📢 Broadcast started...")

        for user_id in list(USERS):
            try:
                await message.reply_to_message.copy(user_id)
                sent += 1
                await asyncio.sleep(0.05)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except:
                failed += 1

        await status.edit(
            f"✅ Broadcast completed\n\n"
            f"📤 Sent: {sent}\n"
            f"❌ Failed: {failed}"
        )
