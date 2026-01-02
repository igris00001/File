<p align="center">
  <img src="YOUR_PNG_URL" width="160" />
</p>


# Telegram File Sharing Bot

A powerful **Telegram file-sharing bot** with **private channel storage**, **force-join rules**, **admin-only link creation**, and **broadcast messaging** — all running **without a VPS** (hosted on Render).

---

## 🚀 Features

- 📦 Private channel file storage
- 🔗 Old-style download links (`/start <message_id>`)
- 🔒 Force users to join channels before download
- 👑 Admin-only link generation
- 📢 Broadcast messages to all users
- ☁️ No VPS required (Render hosting)
- ♾️ Unlimited files (Telegram hosted)
- ⚡ Fast & lightweight

---

## 🧠 How It Works

1. Admin uploads files to a **private Telegram channel**
2. Admin sends the file’s **Telegram message link** to the bot
3. Bot generates a **download link**
4. Users must **join required channels**
5. Bot sends the file after verification

---

## 📁 Project Structure
telegram-file-bot/ ├── bot.py ├── requirements.txt └── README.md

---

## ⚙️ Requirements

- Python 3.9+
- Telegram Bot Token
- Render account
- GitHub account

---

## 🛠 Setup Guide

### 1️⃣ Create Telegram Bot
- Open **@BotFather**
- Create a new bot
- Copy the **BOT TOKEN**

---

### 2️⃣ Create Channels

#### 🔒 Private Channel (Storage)
- Create a **private channel**
- Upload files here
- Add bot as **Admin**
- Get channel ID using **@userinfobot**
Example: -1000000000000

#### 🌐 Public Channels (Force Join)
- Create public channels (example):
@Letsucks @USRxMEE

- Add bot as **Admin** in each

---

### 3️⃣ GitHub Setup

1. Create a new repository
2. Upload:
 - `bot.py`
 - `requirements.txt`
3. Commit changes

---

### 4️⃣ Deploy on Render

1. Go to **Render → New → Web Service**
2. Connect GitHub repository
3. Set:
 - **Build Command**
   ```
   pip install -r requirements.txt
   ```
 - **Start Command**
   ```
   python bot.py
   ```

---

### 5️⃣ Environment Variables (IMPORTANT)

Add these in **Render → Environment**:
BOT_TOKEN   = your_bot_token_here CHANNEL_ID = -1000000000000 ADMIN_ID   = 1234567890


⚠️ Do NOT hardcode tokens in `bot.py`.

---

## 👑 Admin Usage

### Create download link
Send a **private channel file link** to the bot:
https://t.me/c/0000000000/17

Bot replies:
https://t.me/YourBotUsername?start=17

---

### Broadcast message
/broadcast Hello everyone 👋 New files uploaded!


---

## 👥 User Flow

1. User opens download link
2. Bot checks channel membership
3. If not joined → shows join buttons
4. After joining → file is sent

---

## ❗ Notes

- Only users who clicked `/start` receive broadcasts
- Bot must be admin in all channels
- Public channels are required for force-join
- Private channels cannot be force-joined

---

## 🧑‍💻 Author

**Made by @xchup**

---

## 📜 License

This project is for educational and personal use.
