# Made by @xchup

import time
import asyncio
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

LINKS = {}
USERS = set()

MEDIA_LIFETIME = 15 * 60  # 15 minutes

FORCE_CHANNELS = [
    -1003638744016,  # Channel 1
    -1003594086276   # Channel 2
]

DB_CHANNEL_ID = int(__import__("os").getenv("CHANNEL_ID"))
ADMIN_ID = int(__import__("os").getenv("ADMIN_ID"))

async def is_joined(app, user_id):
    for ch in FORCE_CHANNELS:
        try:
            m = await app.get_chat_member(ch, user_id)
            if m.status not in ("member", "administrator", "owner"):
                return False
        except:
            return False
    return True


def join_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("𝐂𝐡𝐚𝐧𝐧𝐞𝐥 1️⃣", url="https://t.me/+If39xLm7SeQwZTM1")],
        [InlineKeyboardButton("𝐂𝐡𝐚𝐧𝐧𝐞𝐥 2️⃣", url="https://t.me/+bdtAg0G5dLc2ODg1")],
        [InlineKeyboardButton("📥 Get File", callback_data="get_file")]
    ])


def expired_text(msg):
    if msg.video:
        return "📹 Video expired"
    if msg.document:
        return "📄 Document expired"
    if msg.photo:
        return "🖼 Image expired"
    return "❌ Media expired"


async def auto_delete(app, chat_id, msg):
    await asyncio.sleep(MEDIA_LIFETIME)
    try:
        await msg.delete()
        await app.send_message(chat_id, expired_text(msg))
    except:
        pass


def register(app):

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
                    "🔒 Join channels first:",
                    reply_markup=join_buttons()
                )

            sent = await app.copy_message(
                message.chat.id,
                DB_CHANNEL_ID,
                LINKS[token]
            )
            asyncio.create_task(auto_delete(app, message.chat.id, sent))
            return

        await message.reply("👋 Welcome!")


    @app.on_callback_query(filters.regex("get_file"))
    async def get_file(_, q):
        USERS.add(q.from_user.id)

        if not await is_joined(app, q.from_user.id):
            return await q.answer("Join all channels!", show_alert=True)

        token = q.message.text.split("start=")[-1]
        if token not in LINKS:
            return await q.answer("Invalid link", show_alert=True)

        sent = await app.copy_message(
            q.message.chat.id,
            DB_CHANNEL_ID,
            LINKS[token]
        )
        await q.message.delete()
        asyncio.create_task(auto_delete(app, q.message.chat.id, sent))
        await q.answer("File sent!")


    @app.on_message(filters.private & filters.text & filters.user(ADMIN_ID))
    async def admin(_, message):
        if "t.me/c/" not in message.text:
            return

        msg_id = int(message.text.split("/")[-1])
        token = str(int(time.time() * 1000))
        LINKS[token] = msg_id

        me = await app.get_me()
        await message.reply(
            f"✅ Permanent link:\nhttps://t.me/{me.username}?start={token}"
        )


    @app.on_message(filters.command("broadcast") & filters.user(ADMIN_ID))
    async def broadcast(_, message):
        if not message.reply_to_message:
            return await message.reply("Reply to a message")

        ok = 0
        for uid in USERS:
            try:
                await message.reply_to_message.copy(uid)
                ok += 1
                await asyncio.sleep(0.05)
            except:
                pass

        await message.reply(f"✅ Sent to {ok} users")
