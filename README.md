# 🎬 Telegram Anime Provider Bot Factory

Production-ready, asynchronous, scalable **Telegram Anime Provider Bot Factory** built with **Python 3.11+**, **Pyrogram**, **TgCrypto**, and an ultra-fast **JSON Database Engine**.

---

## ✨ Features

- 🏭 **Bot Cloning Engine (`/clone`)**: Users can clone their own isolated Anime Provider Bot in seconds via `@BotFather` token.
- 🔐 **Encrypted Token Storage**: Bot tokens are encrypted using **Fernet** cryptography before being saved to database. No plaintext tokens!
- 🔍 **Flexible Filter & Episode Search**: Supports exact `S1 E4` / `Season 1 Episode 4` / `1x4` queries, single season/episode numbers, and flexible keyword search across captions.
- 🎨 **Small Caps & Colorful UI**: Visually polished inline keyboards and messages formatted with small caps typography (`ᴀʙᴄᴅᴇ...`) and bright emojis.
- 🤖 **Auto Bot Commands**: Automatically sets Telegram bot commands (`SetBotCommands`) for user and admin scopes on Factory and Cloned bots.
- 🔐 **Force Subscribe (`/setfs`)**: Supports **Public Channels** (membership check) and **Private Channels** (auto-approving join requests).
- 🏷️ **Upload System (`/upload`)**: Single episode upload or batch season upload (`/done`, `/cancel`).
- ✏️ **Edit & Delete System (`/edit`, `/delete`)**: Instantly update video files, captions, thumbnails, or remove episodes without bot restarts.
- 📣 **Broadcast System (`/broadcast`)**: Progress tracking, FloodWait retry, and global broadcast capabilities for Supreme Developers (`/broadcast all`).
- 📊 **Statistics & Admin Panel (`/stats`, `/admin`)**: Detailed analytics, database sizes, uptime, and interactive permission selector (`/giveadmin`, `/editadmin`, `/remadmin`).
- 🎁 **Referral System (`/refer`)**: Unique referral links, conversion tracking, rankings, and referral statistics.
- 👑 **Supreme Developer Tools (`/supreme`, `/botlist`, `/db`, `/restart`)**: Global access across all cloned instances.
- 🧹 **Automatic Background Cleanup**: Auto-deletes inactive clones with zero uploaded episodes and <100 users after 3 days.

---

## 🛠️ Configuration & Installation

Credentials can be set **directly inside `app.py`** (header constants) or passed via environment variables / `.env` file.

### Environment Variables / `app.py` Constants

| Variable | Description |
| :--- | :--- |
| `API_ID` | Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | Telegram API Hash from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | Factory Bot Token from [@BotFather](https://t.me/BotFather) |
| `SUPREME_IDS` | Comma-separated Telegram User IDs for Supreme Developers |
| `LOG_CHANNEL_ID` | Global developer log channel ID (e.g. `-1001234567890`, optional) |
| `FACTORY_NAME` | Custom name for your Factory Bot |

---

## 🤖 BotFather Setup

1. Open [@BotFather](https://t.me/BotFather) on Telegram.
2. Send `/newbot` to create your Main Factory Bot.
3. Copy the Bot Token provided by BotFather.
4. Paste the token into `BOT_TOKEN` inside `app.py` or `.env`.

---

## 📢 Channel Permissions Setup (For Force Subscribe)

When configuring Force Subscribe (`/setfs`):
- Add your bot as an **Administrator** in your target channel.
- Grant permissions: **Invite Users via Link** and **Manage Join Requests** (for private request channels).

---

## 💻 Local Testing

1. **Clone & Navigate:**
   ```bash
   git clone <repo_url>
   cd anime-bot-factory
   ```

2. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Credentials:**
   Edit constants in `app.py` or create `.env`:
   ```bash
   cp .env.example .env
   ```

4. **Run Bot:**
   ```bash
   python app.py
   # or
   python main.py
   ```

---

## 🚀 Deployment Guides

### 1. Render Deployment

1. Create a new **Background Worker** on [Render.com](https://render.com).
2. Connect your GitHub repository.
3. Set **Runtime** to `Python 3`.
4. Set **Build Command**: `pip install -r requirements.txt`
5. Set **Start Command**: `python app.py`
6. Add Environment Variables in Render dashboard (`API_ID`, `API_HASH`, `BOT_TOKEN`, `SUPREME_IDS`).
7. Click **Deploy**.

---

### 2. Railway Deployment

1. Create a new project on [Railway.app](https://railway.app).
2. Deploy from GitHub Repo.
3. Add environment variables in Railway settings tab.
4. Railway will automatically detect `Procfile` and deploy `python app.py`.

---

### 3. Koyeb Deployment

1. Create a new app on [Koyeb.com](https://koyeb.com).
2. Select GitHub as source.
3. Set **Build command**: `pip install -r requirements.txt`
4. Set **Run command**: `python app.py`
5. Set Environment Variables (`API_ID`, `API_HASH`, `BOT_TOKEN`, `SUPREME_IDS`).
6. Deploy service.

---

### 4. VPS Deployment (Ubuntu/Debian)

```bash
# Update system & install python
sudo apt update && sudo apt install -y python3 python3-pip git screen

# Clone repository
git clone <repo_url>
cd anime-bot-factory

# Install requirements
pip3 install -r requirements.txt

# Run inside screen session
screen -S animebot
python3 app.py
```

---

### 5. Termux Deployment (Android)

```bash
# Update packages
pkg update && pkg upgrade -y
pkg install python git -y

# Clone repo & install dependencies
git clone <repo_url>
cd anime-bot-factory
pip install -r requirements.txt

# Start Bot
python app.py
```

---

## 📜 License

Distributed under the MIT License.
