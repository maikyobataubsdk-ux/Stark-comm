"""
╔══════════════════════════════════════════════════════════════════╗
║           ᴀɴɪᴍᴇ ʙᴏᴛ ꜰᴀᴄᴛᴏʀʏ — ᴘʀᴏᴅᴜᴄᴛɪᴏɴ ʀᴇᴀᴅʏ               ║
║   ᴊꜱᴏɴ ᴅᴀᴛᴀʙᴀꜱᴇ • ᴇɴᴄʀʏᴘᴛᴇᴅ ᴛᴏᴋᴇɴꜱ • ᴀᴜᴛᴏ ᴄᴏᴍᴍᴀɴᴅꜱ           ║
╚══════════════════════════════════════════════════════════════════╝
"""
import asyncio, base64, hashlib, html, json, logging, os, re, secrets, signal, time
from urllib.parse import quote

from pyrogram import Client, filters, enums
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, RawUpdateHandler
from pyrogram.errors import (FloodWait, RPCError, UserNotParticipant, AccessTokenInvalid,
                             AccessTokenExpired, UserIsBlocked, InputUserDeactivated,
                             PeerIdInvalid, ChatAdminRequired)
from pyrogram.raw.functions.bots import SetBotCommands
from pyrogram.raw.types import BotCommand, BotCommandScopeDefault, BotCommandScopeChat

try:
    from dotenv import load_dotenv; load_dotenv()
except Exception:
    pass

# ══════════════════════════════════════════════════════════════════
#  ⚙️ ᴄᴏɴꜰɪɢ — ʏʜᴀᴀɴ ᴠᴀʟᴜᴇꜱ ᴅɪʀᴇᴄᴛ ᴘᴀꜱᴛᴇ ᴋᴀʀᴏ (ᴇɴᴠ ɪɴ ᴄᴏᴅᴇ)
# ══════════════════════════════════════════════════════════════════
API_ID: int = 0                      # <-- my.telegram.org ꜱᴇ ᴀᴘɪ ɪᴅ
API_HASH: str = ""                   # <-- my.telegram.org ꜱᴇ ᴀᴘɪ ʜᴀꜱʜ
BOT_TOKEN: str = ""                  # <-- ꜰᴀᴄᴛᴏʀʏ ʙᴏᴛ ᴛᴏᴋᴇɴ (@ʙᴏᴛꜰᴀᴛʜᴇʀ)
SUPREME_IDS: str = ""                # <-- ᴄᴏᴍᴍᴀ ꜱᴇᴘᴀʀᴀᴛᴇᴅ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴜꜱᴇʀ ɪᴅꜱ (ᴇx: "12345,67890")
LOG_CHANNEL_ID: int = 0              # <-- ɢʟᴏʙᴀʟ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪᴅ (0 = ᴏꜰꜰ)
FACTORY_NAME: str = "Anime Bot Factory"
CLONE_BOT_ID_TOKEN: str = ""         # <-- ᴏᴘᴛɪᴏɴᴀʟ ᴇxᴛʀᴀ ꜱᴇᴄʀᴇᴛ ꜰᴏʀ ᴛᴏᴋᴇɴ ᴇɴᴄʀʏᴘᴛɪᴏɴ
DB_DIR: str = "data"                 # ᴊꜱᴏɴ ᴅᴀᴛᴀʙᴀꜱᴇ ꜰᴏʟᴅᴇʀ
THUMB_DIR: str = "thumbs"            # ᴛʜᴜᴍʙɴᴀɪʟ ᴄᴀᴄʜᴇ ꜰᴏʟᴅᴇʀ
CLEANUP_INTERVAL: int = 3600         # ꜱᴇᴄᴏɴᴅꜱ — ᴀᴜᴛᴏ-ᴄʟᴇᴀɴᴜᴘ ᴄʜᴇᴄᴋ
CLONE_INACTIVE_DAYS: int = 3         # ɪɴᴀᴄᴛɪᴠᴇ ᴅᴀʏꜱ ʙᴇꜰᴏʀᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ
CLONE_MIN_USERS: int = 100           # ᴜꜱᴇʀꜱ >= ᴛʜɪꜱ = ɴᴇᴠᴇʀ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ

# (ᴏᴘᴛɪᴏɴᴀʟ) ᴇɴᴠᴵᴀʀꜱ ᴏᴠᴇʀʀɪᴅᴇ — ᴄᴏᴅᴇ ᴠᴀʟᴜᴇꜱ ᴘʀɪᴏʀɪᴛʏ ᴡʜᴇɴ ꜱᴇᴛ
API_ID = int(os.getenv("API_ID") or API_ID or 0)
API_HASH = os.getenv("API_HASH") or API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN") or BOT_TOKEN
SUPREME_IDS = os.getenv("SUPREME_IDS") or SUPREME_IDS
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID") or LOG_CHANNEL_ID or 0)
FACTORY_NAME = os.getenv("FACTORY_NAME") or FACTORY_NAME
CLONE_BOT_ID_TOKEN = os.getenv("CLONE_BOT_ID_TOKEN") or CLONE_BOT_ID_TOKEN

SUPREMES = {int(x) for x in SUPREME_IDS.replace(" ", "").split(",") if x.strip().isdigit()}

# ═════════════════════════ ʟᴏɢɢɪɴɢ ═════════════════════════
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
    handlers=[logging.StreamHandler(), logging.FileHandler("factory.log", encoding="utf-8")],
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
LOG = logging.getLogger("ꜰᴀᴄᴛᴏʀʏ")

PM_HTML = enums.ParseMode.HTML
PM_OFF = enums.ParseMode.DISABLED
CMS = enums.ChatMemberStatus

START_TS = now = None
def now(): return int(time.time())
START_TS = now()
DAY_START = lambda: (now() // 86400) * 86400

def dt(ts): return time.strftime("%d %b %Y, %H:%M UTC", time.gmtime(ts))

def hms(sec):
    sec = int(sec); d = sec // 86400; h = (sec % 86400) // 3600; m = (sec % 3600) // 60
    return (f"{d}ᴅ " if d else "") + f"{h}ʜ {m}ᴍ"

def human_size(n):
    n = float(n)
    for u in ("B", "KB", "MB", "GB"):
        if n < 1024 or u == "GB":
            return f"{int(n)} B" if u == "B" else f"{n:.1f} {u}"
        n /= 1024

def hesc(s): return html.escape(str(s) if s else "")

# ═════════════════════ ᴛᴇxᴛ ꜱᴛʏʟᴇ — ꜱᴍᴀʟʟ ᴄᴀᴘꜱ ═════════════════════
_SMALL_MAP = str.maketrans(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ",
    "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘqʀꜱᴛᴜᴠᴡxʏᴢ" "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘqʀꜱᴛᴜᴠᴡxʏᴢ")
def sc(t): return str(t).translate(_SMALL_MAP)

def btn(text, cb): return InlineKeyboardButton(text, callback_data=cb)
def ubtn(text, url): return InlineKeyboardButton(text, url=url)

def chunk(text, limit=3800):
    out, cur = [], ""
    for line in text.split("\n"):
        if len(cur) + len(line) + 1 > limit:
            out.append(cur); cur = line
        else:
            cur = (cur + "\n" + line) if cur else line
    if cur: out.append(cur)
    return out or [""]

# ═════════════════════ ᴄᴏɴꜱᴛᴀɴᴛ ᴛᴇxᴛꜱ ═════════════════════
DEFAULT_START = (
    "👋 ʜᴇʟʟᴏ {name}!\n\n"
    f"🎯 ɪ'ᴍ <b>{{botname}}</b> — ʏᴏᴜʀ ᴀɴɪᴍᴇ ᴘʀᴏᴠɪᴅᴇʀ ʙᴏᴛ.\n\n"
    "🔍 ꜱᴇᴀʀᴄʜ ᴇᴘɪꜱᴏᴅᴇ ᴊᴜꜱᴛ ʙʏ ꜱᴇɴᴅɪɴɢ:\n"
    "▸ S1 E1\n▸ Season 1 Episode 1\n▸ 1x1\n\n"
    "▶️ ꜱᴇɴᴅ ɴᴏᴡ ᴀɴᴅ ᴇɴᴊᴏʏ! ✨")

DEFAULT_CAPTION = "🎬 ꜱᴇᴀꜱᴏɴ {season} • ᴇᴘɪꜱᴏᴅᴇ {episode}\n\n🤖 @{botname}"

COMING_SOON = ("🔔 <b>ᴄᴏᴍɪɴɢ ꜱᴏᴏɴ</b>\n\n"
               "New episodes are not uploaded yet.\nPlease check again later.")

INVALID_FMT = (
    "❌ <b>ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!</b>\n\n"
    "✅ <b>ᴛʀʏ ʟɪᴋᴇ ᴛʜɪꜱ:</b>\n"
    "━━━━━━━━━━━━━━\n"
    "▸ Season 1 Episode 4\n▸ S1 E4\n▸ s1e4\n▸ 1x4")

CLONE_PROMPT = (
    "🤖 <b>ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴀɴɪᴍᴇ ʙᴏᴛ</b>\n━━━━━━━━━━━━━━\n\n"
    "1️⃣ @BotFather ᴏᴘᴇɴ ᴋᴀʀᴏ\n"
    "2️⃣ /newbot → ɴᴀᴍᴇ & ᴜꜱᴇʀɴᴀᴍᴇ ꜱᴇᴛ ᴋᴀʀᴏ\n"
    f"3️⃣ ᴛᴏᴋᴇɴ ᴄᴏᴘʏ ᴋᴀʀᴋᴇ ʏᴀʜᴀᴀɴ ꜱᴇɴᴅ ᴋᴀʀᴏ\n\n"
    "🔐 <b>ꜱᴇᴄᴜʀɪᴛʏ:</b> ᴛᴏᴋᴇɴ <u>ᴇɴᴄʀʏᴘᴛᴇᴅ</u> ꜱᴛᴏʀᴇ ʜᴏᴛᴀ ʜᴀɪ — ᴘʟᴀɪɴᴛᴇxᴛ ᴋᴀʜɪ ɴᴀʜɪ ʀʜᴇᴛᴀ.\n\n"
    "⏳ ɴᴏᴡ ꜱᴇɴᴅ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ:")

CLONE_SUCCESS = (
    "🎉 <b>ᴄʟᴏɴᴇ ᴄʀᴇᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n━━━━━━━━━━━━━━\n\n"
    "🤖 ʙᴏᴛ: <b>@{uname}</b>\n"
    "🆔: <code>{bid}</code>\n"
    "👤 ᴏᴡɴᴇʀ: <b>{name}</b>\n\n"
    "✅ ʙᴏᴛ ꜱᴛᴀʀᴛᴇᴅ + ᴄᴏᴍᴍᴀɴᴅꜱ ᴀᴜᴛᴏ-ꜱᴇᴛ\n\n"
    "📌 <b>ɴᴇxᴛ ꜱᴛᴇᴘꜱ:</b>\n"
    "▸ /setfs — ꜰᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ\n"
    "▸ /editstart — ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ\n"
    "▸ /upload — ᴇᴘɪꜱᴏᴅᴇꜱ ᴀᴅᴅ ᴋᴀʀᴏ\n\n"
    "🚀 ʏᴏᴜʀ ʙᴏᴛ ɪꜱ ʟɪᴠᴇ ɴᴏᴡ!")

ADMIN_PANEL_TXT = (
    "🛠 <b>ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</b>\n━━━━━━━━━━━━━━\n"
    "🤖 ʙᴏᴛ: @{uname}\n"
    "👤 ʏᴏᴜ: <b>{role}</b>\n\n"
    "⬇️ ꜱᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ:")

# ═════════════════════ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ & ʀᴏʟᴇꜱ ═════════════════════
PERMS = ["upload", "edit", "delete", "broadcast", "forcesub", "editstart", "stats",
         "manage_admins", "thumb", "captions", "seasons", "list", "restart_upload"]

PERM_LABELS = {
    "upload": "ᴜᴘʟᴏᴀᴅ ᴇᴘɪꜱᴏᴅᴇꜱ", "edit": "ᴇᴅɪᴛ ᴇᴘɪꜱᴏᴅᴇꜱ", "delete": "ᴅᴇʟᴇᴛᴇ ᴇᴘɪꜱᴏᴅᴇꜱ",
    "broadcast": "ʙʀᴏᴀᴅᴄᴀꜱᴛ", "forcesub": "ꜰᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ", "editstart": "ᴇᴅɪᴛ ꜱᴛᴀʀᴛ",
    "stats": "ᴠɪᴇᴡ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ", "manage_admins": "ᴍᴀɴᴀɢᴇ ᴀᴅᴍɪɴꜱ", "thumb": "ᴜᴘʟᴏᴀᴅ ᴛʜᴜᴍʙɴᴀɪʟ",
    "captions": "ᴍᴀɴᴀɢᴇ ᴄᴀᴘᴛɪᴏɴꜱ", "seasons": "ᴍᴀɴᴀɢᴇ ꜱᴇᴀꜱᴏɴꜱ", "list": "ᴜꜱᴇ ʟɪꜱᴛ",
    "restart_upload": "ʀᴇꜱᴛᴀʀᴛ ᴜᴘʟᴏᴀᴅ",
}

ROLE_PRESETS = {
    "owner": list(PERMS),
    "manager": ["manage_admins", "broadcast", "upload", "edit", "delete", "stats",
                "forcesub", "editstart", "captions", "thumb", "seasons", "list", "restart_upload"],
    "uploader": ["upload", "edit", "seasons", "captions", "thumb", "list"],
    "broadcaster": ["broadcast"],
    "analyst": ["stats", "list"],
    "custom": [],
}
ROLE_NAME = {"owner": "👑 ᴏᴡɴᴇʀ", "manager": "🛠 ᴍᴀɴᴀɢᴇʀ", "uploader": "⬆️ ᴜᴘʟᴏᴀᴅᴇʀ",
             "broadcaster": "📣 ʙʀᴏᴀᴅᴄᴀꜱᴛᴇʀ", "analyst": "📊 ᴀɴᴀʟʏꜱᴛ", "custom": "⚙️ ᴄᴜꜱᴛᴏᴍ"}

# ═════════════════════ ᴄᴏᴍᴍᴀɴᴅ ꜱᴇᴛꜱ (ᴀᴜᴛᴏ-ꜱᴇᴛ ɪɴ ᴛᴇʟᴇɢʀᴀᴍ) ═════════════════════
USER_CMD_RAW = [("start", "ꜱᴛᴀʀᴛ ʙᴏᴛ"), ("refer", "ʀᴇꜰᴇʀ & ᴇᴀʀɴ")]
ADMIN_CMD_RAW = [("upload", "ᴀᴅᴅ ᴇᴘɪꜱᴏᴅᴇꜱ"), ("edit", "ᴇᴅɪᴛ ᴇᴘɪꜱᴏᴅᴇ"), ("delete", "ᴅᴇʟᴇᴛᴇ ᴇᴘɪꜱᴏᴅᴇ"),
                 ("broadcast", "ꜱᴇɴᴅ ᴜᴘᴅᴀᴛᴇꜱ"), ("stats", "ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ"), ("list", "ᴇᴘɪꜱᴏᴅᴇ ʟɪꜱᴛ"),
                 ("admin", "ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ"), ("setfs", "ꜰᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ"), ("editstart", "ꜱᴇᴛ ꜱᴛᴀʀᴛ ᴍꜱɢ"),
                 ("giveadmin", "ᴀᴅᴅ ᴀᴅᴍɪɴ"), ("editadmin", "ᴇᴅɪᴛ ᴀᴅᴍɪɴ"), ("remadmin", "ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ"),
                 ("done", "ꜰɪɴɪꜱʜ ᴜᴘʟᴏᴀᴅ"), ("cancel", "ᴄᴀɴᴄᴇʟ ꜱᴇꜱꜱɪᴏɴ")]
FACTORY_CMD_RAW = [("clone", "ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ʙᴏᴛ")]
SUPREME_CMD_RAW = [("supreme", "ꜱᴜᴘʀᴇᴍᴇ ᴘᴀɴᴇʟ"), ("botlist", "ᴀʟʟ ʙᴏᴛꜱ"), ("db", "ᴅᴀᴛᴀʙᴀꜱᴇ"), ("restart", "ʀᴇꜱᴛᴀʀᴛ ᴄʟᴏɴᴇꜱ")]

ALL_CMDS = ["start", "refer"] + [x[0] for x in ADMIN_CMD_RAW + FACTORY_CMD_RAW + SUPREME_CMD_RAW]
FACTORY_ONLY = {"clone", "supreme", "botlist", "db", "restart"}

# ═════════════════════ ɢʟᴏʙᴀʟ ꜱᴛᴀᴛᴇ ═════════════════════
RUNNING = {}        # bot_id -> Client
STORES = {}         # bot_id -> Store
SESSIONS = {}       # (bot_id, uid) -> {"step":..., "data":{...}}
RATE = {}
LAST_UNAUTH = {}
ACTIVE_THRO = {}
FACTORY = None      # factory Store
FACTORY_CLIENT = None

_COLLECTIONS = ["users", "episodes", "admins", "settings", "referrals", "broadcast_logs", "activity"]

# ══════════════════════════════════════════════════════════════════
#  🗄️ ᴊꜱᴏɴ ᴅᴀᴛᴀʙᴀꜱᴇ — ᴀꜱʏɴᴄ, ᴀᴛᴏᴍɪᴄ, ᴋᴇʏᴇᴅ (ɪɴᴅᴇxᴇᴅ) ᴄᴏʟʟᴇᴄᴛɪᴏɴꜱ
# ══════════════════════════════════════════════════════════════════
class Store:
    """JSON-backed document store. Docs keyed by _id = O(1) index lookups.
       Writes are debounced + flushed atomically (tmp file + os.replace)."""

    def __init__(self, path):
        self.path = path
        self.data = {}
        self._dirty = False
        self._task = None
        self._load()

    def _load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
                if not isinstance(self.data, dict):
                    raise ValueError("root not dict")
            except Exception as e:
                LOG.error("ᴅʙ ʟᴏᴀᴅ ꜰᴀɪʟᴇᴅ %s: %s", self.path, e)
                try: os.replace(self.path, self.path + ".corrupt")
                except OSError: pass
                self.data = {}

    def c(self, name):
        return self.data.setdefault(name, {})

    def get_sync(self, col, _id):
        return self.c(col).get(str(_id))

    async def get(self, col, _id):
        return self.c(col).get(str(_id))

    async def put(self, col, _id, doc):
        self.c(col)[str(_id)] = doc
        self.flush_soon()
        return doc

    async def update(self, col, _id, **fields):
        d = self.c(col).get(str(_id))
        if d is None:
            return None
        d.update(fields)
        self.flush_soon()
        return d

    async def delete(self, col, _id):
        self.c(col).pop(str(_id), None)
        self.flush_soon()

    def count(self, col):
        return len(self.c(col))

    def find(self, col, pred=None):
        return [v for v in self.c(col).values() if pred is None or pred(v)]

    def flush_soon(self):
        self._dirty = True
        if self._task is None or self._task.done():
            try:
                self._task = asyncio.get_running_loop().create_task(self._flush_later())
            except RuntimeError:
                pass

    async def _flush_later(self):
        await asyncio.sleep(0.4)
        if self._dirty:
            await self.flush()

    async def flush(self):
        self._dirty = False
        payload = json.dumps(self.data, ensure_ascii=False, separators=(",", ":"))
        await asyncio.to_thread(self._write, payload)

    def _write(self, payload):
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(payload)
        os.replace(tmp, self.path)

    def size(self):
        try: return os.path.getsize(self.path)
        except OSError: return 0


def clone_path(bid): return os.path.join(DB_DIR, f"clone_{bid}.json")

def get_store(bid):
    s = STORES.get(bid)
    if not s:
        s = Store(clone_path(bid))
        STORES[bid] = s
    return s

def cfg(store):
    return store.c("settings").get("cfg") or {}

async def set_cfg(store, **kw):
    d = dict(cfg(store)); d.update(kw)
    await store.put("settings", "cfg", d)

async def ensure_defaults(store):
    st = store.c("settings")
    if "cfg" not in st:
        st["cfg"] = {"fs_mode": "off", "fs_channel": 0, "fs_username": "", "fs_link": "",
                     "log_channel": 0, "caption": "", "owner_id": None, "created_at": now()}
        store.flush_soon()
    if "start" not in st:
        st["start"] = {"type": "text", "text": DEFAULT_START}
        store.flush_soon()

# ═════════════════════ ᴛᴏᴋᴇɴ ᴇɴᴄʀʏᴘᴛɪᴏɴ (ɴᴏ ᴘʟᴀɪɴᴛᴇxᴛ!) ═════════════════════
_FER = None
def _fernet():
    from cryptography.fernet import Fernet
    secret = (str(API_HASH) + ":" + str(CLONE_BOT_ID_TOKEN or "ᴀɴɪᴍᴇ-ꜰᴀᴄᴛᴏʀʏ-ᴠ1")).encode()
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret).digest()))

def enc_token(t):
    global _FER
    _FER = _FER or _fernet()
    return _FER.encrypt(t.encode()).decode()

def dec_token(e):
    global _FER
    _FER = _FER or _fernet()
    return _FER.decrypt(e.encode()).decode()

# ═════════════════════ ᴇᴘɪꜱᴏᴅᴇ ᴘᴀʀꜱᴇʀ ═════════════════════
_EP_RX = [
    re.compile(r"season\s*(\d{1,3})\s*(?:ep(?:isode)?)\s*(\d{1,3})", re.I),
    re.compile(r"\bs\s*(\d{1,3})\s*e\s*(\d{1,3})\b", re.I),
    re.compile(r"\b(\d{1,3})\s*[x×]\s*(\d{1,3})\b", re.I),
]

def parse_episode(text):
    if not text: return None
    t = re.sub(r"[._]", " ", text.strip())
    for rx in _EP_RX:
        m = rx.search(t)
        if m:
            s, e = int(m.group(1)), int(m.group(2))
            if 1 <= s <= 999 and 1 <= e <= 999:
                return s, e
    return None

def ep_id(s, e): return f"{s}:{e}"

def get_media(m):
    if m.video:
        return "video", m.video.file_id, (m.video.thumbs[0].file_id if m.video.thumbs else None)
    if m.animation:
        return "animation", m.animation.file_id, (m.animation.thumbs[0].file_id if m.animation.thumbs else None)
    if m.document:
        return "document", m.document.file_id, (m.document.thumbs[0].file_id if m.document.thumbs else None)
    return None, None, None

# ═════════════════════ ꜱᴇꜱꜱɪᴏɴ / ʀᴀᴛᴇ / ᴘᴇʀᴍꜱ ═════════════════════
def get_sess(c, uid): return SESSIONS.get((c.bot_id, uid))
def set_sess(c, uid, step, **data): SESSIONS[(c.bot_id, uid)] = {"step": step, "data": data}
def clear_sess(c, uid): SESSIONS.pop((c.bot_id, uid), None)

def rate_ok(c, uid):
    k = (c.bot_id, uid); t = now()
    if t - RATE.get(k, 0) < 2.5: return False
    RATE[k] = t; return True

def is_supreme(uid): return uid in SUPREMES

async def perm_ok(c, uid, perm):
    if is_supreme(uid): return True
    a = await c.store.get("admins", uid)
    if not a: return False
    if a.get("role") == "owner": return True
    return perm in a.get("permissions", [])

# ═════════════════════ ʟᴏɢɢɪɴɢ / ɴᴏᴛɪꜰʏ ═════════════════════
async def dev_log(text):
    if FACTORY is not None:
        await FACTORY.put("developer_logs", secrets.token_hex(6), {"text": text, "at": now()})
    if LOG_CHANNEL_ID and FACTORY_CLIENT is not None:
        try:
            await FACTORY_CLIENT.send_message(LOG_CHANNEL_ID, text, parse_mode=PM_OFF,
                                              disable_web_page_preview=True)
        except RPCError:
            pass

async def log_event(c, event, detail="", important=False, uid=None):
    await c.store.put("activity", secrets.token_hex(5),
                      {"event": event, "detail": detail, "uid": uid, "at": now()})
    text = f"{event}\n{detail}\n🤖 @{c.username} | {dt(now())}"
    lc = cfg(c.store).get("log_channel", 0)
    if lc:
        try: await c.send_message(lc, text, parse_mode=PM_OFF, disable_web_page_preview=True)
        except RPCError: pass
    if important:
        await dev_log(text)

async def touch_active(c):
    if c.is_factory or FACTORY is None: return
    t = now()
    if t - ACTIVE_THRO.get(c.bot_id, 0) < 300: return
    ACTIVE_THRO[c.bot_id] = t
    await FACTORY.update("bots", c.bot_id, last_active=t)

async def unauthorized(c, uid):
    k = (c.bot_id, uid)
    if now() - LAST_UNAUTH.get(k, 0) < 600: return
    LAST_UNAUTH[k] = now()
    await log_event(c, "🚫 ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴀᴛᴛᴇᴍᴘᴛ", f"ᴜꜱᴇʀ: {uid}", important=True, uid=uid)

async def q_safe(q, text, alert=False):
    try: await q.answer(text, show_alert=alert)
    except RPCError: pass

# ═════════════════════ ᴀᴜᴛᴏ ᴄᴏᴍᴍᴀɴᴅꜱ (ꜱᴇᴛᴍʏᴄᴏᴍᴍᴀɴᴅꜱ) ═════════════════════
def _raw(lst): return [BotCommand(command=a, description=b) for a, b in lst]

async def _set_scope(c, peer, lst):
    try:
        scope = BotCommandScopeDefault() if peer is None else BotCommandScopeChat(peer=peer)
        await c.invoke(SetBotCommands(scope=scope, lang_code="", commands=_raw(lst)))
        return True
    except Exception as e:
        LOG.debug("ꜱᴇᴛᴄᴏᴍᴍᴀɴᴅꜱ ꜰᴀɪʟᴇᴅ: %s", e)
        return False

async def apply_admin_commands(c, uid):
    lst = ADMIN_CMD_RAW + (FACTORY_CMD_RAW + SUPREME_CMD_RAW if c.is_factory and is_supreme(uid) else [])
    try: peer = await c.resolve_peer(int(uid))
    except Exception: return
    await _set_scope(c, peer, lst)

async def apply_commands(c):
    base = USER_CMD_RAW + (FACTORY_CMD_RAW if c.is_factory else [])
    await _set_scope(c, None, base)
    for uid in list(c.store.c("admins").keys()):
        await apply_admin_commands(c, int(uid))
    if c.is_factory:
        for uid in SUPREMES:
            await apply_admin_commands(c, uid)

# ═════════════════════ ᴜꜱᴇʀꜱ / ꜰᴏʀᴄᴇ-ꜱᴜʙ / ꜱᴛᴀʀᴛ ═════════════════════
async def ensure_user(c, tu):
    uid = str(tu.id)
    u = await c.store.get("users", uid)
    if u:
        if u.get("last_seen", 0) < now() - 3600:
            await c.store.update("users", uid, last_seen=now())
        return u
    u = {"_id": uid, "first_name": (tu.first_name or "")[:64], "username": (tu.username or ""),
         "started_at": now(), "last_seen": now(), "fs_verified": False}
    await c.store.put("users", uid, u)
    await log_event(c, "🆕 ɴᴇᴡ ᴜꜱᴇʀ", f"ᴄʜᴀᴛ: {uid} (@{u['username']})", important=True, uid=tu.id)
    await touch_active(c)
    return u

async def fs_state(c, uid):
    """Returns (ok, keyboard|None)."""
    st = cfg(c.store)
    mode = st.get("fs_mode", "off")
    if mode == "off": return True, None
    if is_supreme(uid): return True, None
    a = await c.store.get("admins", uid)
    if a or st.get("owner_id") == uid: return True, None
    u = await c.store.get("users", uid)
    if mode == "public":
        ok = False
        try:
            mem = await c.get_chat_member(st.get("fs_channel"), uid)
            ok = mem.status in (CMS.MEMBER, CMS.ADMINISTRATOR, CMS.OWNER)
        except UserNotParticipant:
            ok = False
        except RPCError:
            ok = False
        if ok:
            if u: await c.store.update("users", uid, fs_verified=True)
            return True, None
        if not st.get("fs_username"): return True, None
        kb = InlineKeyboardMarkup([[ubtn("🔗 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ", f"https://t.me/{st['fs_username']}")],
                                   [btn("✅ ᴠᴇʀɪꜰʏ ɴᴏᴡ", "ckfs")]])
        return False, kb
    # private request mode
    if u and u.get("fs_verified"): return True, None
    if not st.get("fs_link"): return True, None
    kb = InlineKeyboardMarkup([[ubtn("🔗 ʀᴇQᴜᴇꜱᴛ ᴛᴏ ᴊᴏɪɴ", st["fs_link"])],
                               [btn("✅ ᴠᴇʀɪꜰʏ ɴᴏᴡ", "ckfs")]])
    return False, kb

async def convert_referral(c, uid):
    pend = [r for r in c.store.find("referrals")
            if r.get("user") == str(uid) and r.get("status") == "pending"]
    for r in pend:
        await c.store.update("referrals", r["_id"], status="converted", converted_at=now())
        await log_event(c, "🤝 ʀᴇꜰᴇʀʀᴀʟ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ", f"ʀᴇꜰ: {r['referrer']} → {uid}", uid=uid)
        try:
            await c.send_message(int(r["referrer"]), "🎉 <b>ɴᴇᴡ ʀᴇꜰᴇʀʀᴀʟ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n\n🎁 ᴋᴇᴇᴘ ꜱʜᴀʀɪɴɢ!", parse_mode=PM_HTML)
        except RPCError:
            pass

def render_text(template, user, c):
    name = hesc(user.get("first_name") or "ᴜꜱᴇʀ")
    uname = hesc(user.get("username") or user.get("_id", ""))
    return (template.replace("{name}", name).replace("{username}", uname)
            .replace("{botname}", hesc(c.username)))

async def send_start_content(c, chat_id, user):
    s = c.store.c("settings").get("start") or {"type": "text", "text": DEFAULT_START}
    text = render_text(s.get("text") or DEFAULT_START, user or {}, c)
    if c.is_factory:
        rows = [[btn("🤖 ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ʙᴏᴛ", "cloneme")], [btn("🎁 ʀᴇꜰᴇʀ & ᴇᴀʀɴ", "rf|menu")]]
    else:
        rows = [[btn("🔍 ʜᴏᴡ ᴛᴏ ꜱᴇᴀʀᴄʜ", "fmt"), btn("🎁 ʀᴇꜰᴇʀ & ᴇᴀʀɴ", "rf|menu")]]
    kb = InlineKeyboardMarkup(rows)
    t = s.get("type", "text")
    try:
        if t == "photo" and s.get("file_id"):
            await c.send_photo(chat_id, s["file_id"], caption=text, parse_mode=PM_HTML, reply_markup=kb)
        elif t == "video" and s.get("file_id"):
            await c.send_video(chat_id, s["file_id"], caption=text, parse_mode=PM_HTML, reply_markup=kb)
        elif t == "animation" and s.get("file_id"):
            await c.send_animation(chat_id, s["file_id"], caption=text, parse_mode=PM_HTML, reply_markup=kb)
        elif t == "document" and s.get("file_id"):
            await c.send_document(chat_id, s["file_id"], caption=text, parse_mode=PM_HTML, reply_markup=kb)
        else:
            await c.send_message(chat_id, text, parse_mode=PM_HTML, reply_markup=kb,
                                 disable_web_page_preview=True)
    except RPCError as e:
        LOG.warning("ꜱᴛᴀʀᴛ ᴄᴏɴᴛᴇɴᴛ ꜰᴀʟʟʙᴀᴄᴋ: %s", e)
        try:
            await c.send_message(chat_id, text, parse_mode=PM_HTML, reply_markup=kb,
                                 disable_web_page_preview=True)
        except RPCError:
            pass

# ═════════════════════ ᴇᴘɪꜱᴏᴅᴇ ᴅᴇʟɪᴠᴇʀʏ ═════════════════════
def build_caption(c, ep, user):
    st = cfg(c.store)
    base = ep.get("caption") or st.get("caption") or DEFAULT_CAPTION
    name = hesc(user.get("first_name") or "ᴀɴɪᴍᴇ ꜰᴀɴ") if user else "ᴀɴɪᴍᴇ ꜰᴀɴ"
    uname = hesc(user.get("username") or "—") if user else "—"
    return (base.replace("{season}", str(ep["season"])).replace("{episode}", str(ep["episode"]))
                .replace("{name}", name).replace("{username}", uname)
                .replace("{botname}", c.username or "ʙᴏᴛ"))

async def resolve_thumb(c, ep):
    p = ep.get("thumb_path")
    if p and os.path.exists(p): return p
    tid = ep.get("thumb_id")
    if not tid: return None
    path = os.path.join(THUMB_DIR, f"{c.bot_id}_{ep['season']}_{ep['episode']}.jpg")
    try:
        out = await c.download_media(tid, file_name=path)
        ep["thumb_path"] = out or path
        c.store.flush_soon()
        return ep["thumb_path"]
    except RPCError:
        return None

async def save_episode(c, uid, s, e, file_id, mtype, caption, thumb_id):
    doc = {"_id": ep_id(s, e), "season": s, "episode": e, "file_id": file_id, "type": mtype,
           "caption": caption or "", "thumb_id": thumb_id, "thumb_path": None,
           "uploaded_by": uid, "created_at": now(), "updated_at": now()}
    await c.store.put("episodes", doc["_id"], doc)
    await touch_active(c)
    await log_event(c, "🎬 ᴇᴘɪꜱᴏᴅᴇ ᴜᴘʟᴏᴀᴅᴇᴅ", f"ꜱ{ꜱ}" if False else f"ꜱ{s} ᴇ{e}", important=True, uid=uid)
    return doc

async def send_episode(c, chat_id, s, e, user=None):
    ep = await c.store.get("episodes", ep_id(s, e))
    if not ep:
        return False
    if user is None:
        user = await c.store.get("users", str(chat_id))
    caption = build_caption(c, ep, user)
    kb = InlineKeyboardMarkup([[btn("▶️ ɴᴇxᴛ ᴇᴘɪꜱᴏᴅᴇ ▶️", f"next|{s}:{e}")]])
    thumb = await resolve_thumb(c, ep)
    t = ep.get("type", "video")
    sent = False
    for attempt in range(2):
        try:
            if t == "animation":
                await c.send_animation(chat_id, ep["file_id"], caption=caption, parse_mode=PM_HTML, reply_markup=kb)
            elif t == "document":
                await c.send_document(chat_id, ep["file_id"], caption=caption, parse_mode=PM_HTML,
                                      reply_markup=kb, thumb=thumb)
            else:
                await c.send_video(chat_id, ep["file_id"], caption=caption, parse_mode=PM_HTML,
                                   reply_markup=kb, thumb=thumb)
            sent = True
            break
        except FloodWait as f:
            if attempt == 0:
                await asyncio.sleep(min(f.value, 60))
        except RPCError as ex:
            LOG.error("ꜱᴇɴᴅ_ᴇᴘɪꜱᴏᴅᴇ: %s", ex)
            break
    if not sent:
        try:
            await c.send_message(chat_id, "⚠️ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇɴᴅ ꜰɪʟᴇ.</b> ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ.", parse_mode=PM_HTML)
        except RPCError:
            pass
        return True
    await touch_active(c)
    await c.store.put("activity", secrets.token_hex(5),
                      {"event": "📤 ᴇᴘɪꜱᴏᴅᴇ ꜱᴇɴᴛ", "detail": f"ꜱ{s} ᴇ{e} → {chat_id}", "uid": chat_id, "at": now()})
    return True

# ═════════════════════ ᴄᴏᴍᴍᴀɴᴅ ʜᴀɴᴅʟᴇʀꜱ ═════════════════════
async def cmd_start(c, m):
    uid = m.from_user.id
    user = await ensure_user(c, m.from_user)
    payload = m.command[1] if len(m.command) > 1 else ""
    if payload.startswith("ref_"):
        ref = payload[4:]
        if ref.isdigit() and int(ref) != uid:
            rid = f"{int(ref)}_{uid}"
            if not await c.store.get("referrals", rid) and await c.store.get("users", int(ref)):
                await c.store.put("referrals", rid, {"_id": rid, "referrer": str(int(ref)),
                                                     "user": str(uid), "status": "pending", "at": now()})
                await log_event(c, "🤝 ɴᴇᴡ ʀᴇꜰᴇʀʀᴀʟ", f"{ref} → {uid}", uid=uid)
    ok, kb = await fs_state(c, uid)
    if not ok:
        await unauthorized(c, uid)
        try:
            await m.reply("🔐 <b>ᴀᴄᴄᴇꜱꜱ ʟᴏᴄᴋᴇᴅ!</b>\n\nᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ᴛʜᴇɴ ᴘʀᴇꜱꜱ ✅ ᴠᴇʀɪꜰʏ.",
                          reply_markup=kb, parse_mode=PM_HTML, disable_web_page_preview=True)
        except RPCError:
            pass
        return
    await convert_referral(c, uid)
    await send_start_content(c, m.chat.id, user)

async def episode_request(c, m):
    uid = m.from_user.id
    if not rate_ok(c, uid): return
    ok, kb = await fs_state(c, uid)
    if not ok:
        await unauthorized(c, uid)
        try:
            await m.reply("🔐 <b>ᴀᴄᴄᴇꜱꜱ ʟᴏᴄᴋᴇᴅ!</b> ᴊᴏɪɴ ᴛʜᴇ ᴄʜᴀɴɴᴇʟ ꜰɪʀꜱᴛ.",
                          reply_markup=kb, parse_mode=PM_HTML, disable_web_page_preview=True)
        except RPCError:
            pass
        return
    pe = parse_episode(m.text)
    if not pe:
        await m.reply(INVALID_FMT, parse_mode=PM_HTML, disable_web_page_preview=True)
        return
    s, e = pe
    found = await send_episode(c, uid, s, e)
    if not found:
        seasons = sorted({int(k.split(":")[0]) for k in c.store.c("episodes")})
        if seasons:
            kb2 = InlineKeyboardMarkup([[btn(f"📚 ꜱᴇᴀꜱᴏɴ {x}", f"sea|{x}") for x in seasons[:5]]])
            await m.reply(f"❌ <b>ꜱᴇᴀꜱᴏɴ {s} ᴇᴘɪꜱᴏᴅᴇ {e} ɴᴏᴛ ꜰᴏᴜɴᴅ!</b>\n\nᴀᴠᴀɪʟᴀʙʟᴇ ꜱᴇᴀꜱᴏɴꜱ 👇",
                          reply_markup=kb2, parse_mode=PM_HTML)
        else:
            await m.reply("❌ <b>ɴᴏ ᴇᴘɪꜱᴏᴅᴇꜱ ᴜᴘʟᴏᴀᴅᴇᴅ ʏᴇᴛ!</b>\n\nᴄᴏᴍᴇ ʙᴀᴄᴋ ꜱᴏᴏɴ ✨", parse_mode=PM_HTML)

# ─────────── ʀᴇꜰᴇʀ ───────────
def refer_stats(store, uid):
    mine = [r for r in store.find("referrals") if r.get("referrer") == str(uid)]
    conv = [r for r in mine if r.get("status") == "converted"]
    return len(mine), len(conv)

def ranking_text(store):
    agg = {}
    for r in store.c("referrals").values():
        ref = r.get("referrer")
        a = agg.setdefault(ref, [0, 0]); a[0] += 1
        if r.get("status") == "converted": a[1] += 1
    top = sorted(agg.items(), key=lambda kv: (-kv[1][1], -kv[1][0]))[:10]
    medals = ["🥇", "🥈", "🥉"]
    lines = [f"{medals[i] if i < 3 else '🔹'} <code>{ref}</code> — ✅ {conv}/{tot}"
             for i, (ref, (tot, conv)) in enumerate(top)]
    return "🏆 <b>ʀᴇꜰᴇʀʀᴀʟ ʀᴀɴᴋɪɴɢ</b>\n━━━━━━━━━━━━━━\n" + ("\n".join(lines) if lines else "ɴᴏ ʀᴇꜰᴇʀʀᴀʟꜱ ʏᴇᴛ.")

async def send_refer(c, chat_id, uid):
    store = c.store
    invited, conv = refer_stats(store, uid)
    rate = f"{(conv / invited * 100):.1f}" if invited else "0.0"
    link = f"https://t.me/{c.username}?start=ref_{uid}"
    txt = (f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ</b>\n━━━━━━━━━━━━━━\n"
           f"🔗 <code>{link}</code>\n\n"
           f"👥 ɪɴᴠɪᴛᴇᴅ ᴜꜱᴇʀꜱ: <b>{invited}</b>\n"
           f"✅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ ᴊᴏɪɴꜱ: <b>{conv}</b>\n"
           f"📈 ᴄᴏɴᴠᴇʀꜱɪᴏɴ ʀᴀᴛᴇ: <b>{rate}%</b>\n"
           f"🤖 ʙᴏᴛ: @{c.username}\n"
           f"🌍 ᴛᴏᴛᴀʟ ʙᴏᴛ ᴜꜱᴇʀꜱ: <b>{store.count('users')}</b>")
    kb = InlineKeyboardMarkup([
        [ubtn("🟢 ꜱʜᴀʀᴇ ʙᴏᴛ", f"https://t.me/share/url?url={quote(link)}&text={quote('🎬 ᴡᴀᴛᴄʜ ᴀɴɪᴍᴇ ꜰʀᴇᴇ!')}")],
        [btn("🔵 ᴄᴏᴘʏ ʟɪɴᴋ", "rf|link"), btn("🟣 ʀᴇꜰᴇʀʀᴀʟ ꜱᴛᴀᴛꜱ", "rf|stats")]])
    await c.send_message(chat_id, txt, parse_mode=PM_HTML, disable_web_page_preview=True, reply_markup=kb)

async def cmd_refer(c, m):
    await ensure_user(c, m.from_user)
    await send_refer(c, m.chat.id, m.from_user.id)

# ─────────── ᴜᴘʟᴏᴀᴅ ───────────
def upload_menu_kb():
    return InlineKeyboardMarkup([
        [btn("🟢 ᴀᴅᴅ ᴇᴘɪꜱᴏᴅᴇ", "up|ep"), btn("🔵 ɴᴇᴡ ꜱᴇᴀꜱᴏɴ", "up|ns")],
        [btn("🔴 ᴄᴀɴᴄᴇʟ", "up|cancel")]])

async def show_upload_menu(c, chat_id, edit_msg=None):
    txt = ("⬆️ <b>ᴜᴘʟᴏᴀᴅ ᴄᴇɴᴛᴇʀ</b>\n━━━━━━━━━━━━━━\n"
           "🟢 <b>ᴀᴅᴅ ᴇᴘɪꜱᴏᴅᴇ</b> — ꜱɪɴɢʟᴇ ᴇᴘɪꜱᴏᴅᴇ\n"
           "🔵 <b>ɴᴇᴡ ꜱᴇᴀꜱᴏɴ</b> — ʙᴀᴛᴄʜ ꜰʀᴏᴍ ᴇᴘ1\n"
           "🏁 /ᴅᴏɴᴇ • ❌ /ᴄᴀɴᴄᴇʟ")
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=upload_menu_kb(), parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=upload_menu_kb(), parse_mode=PM_HTML)

async def cmd_upload(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "upload"):
        await m.reply("❌ <b>ɴᴏ ᴜᴘʟᴏᴀᴅ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    s = get_sess(c, uid)
    if s and str(s.get("step", "")).startswith(("up_", "ns_")):
        if await perm_ok(c, uid, "restart_upload"):
            await show_upload_menu(c, m.chat.id); return
        await m.reply("♻️ <b>ᴜᴘʟᴏᴀᴅ ꜱᴇꜱꜱɪᴏɴ ᴀʟʀᴇᴀᴅʏ ᴀᴄᴛɪᴠᴇ!</b>\n\nꜱᴇɴᴅ /ᴅᴏɴᴇ ᴛᴏ ꜰɪɴɪꜱʜ ᴏʀ /ᴄᴀɴᴄᴇʟ",
                      parse_mode=PM_HTML); return
    set_sess(c, uid, "up_menu")
    await show_upload_menu(c, m.chat.id)

async def up_got_video(c, m):
    uid = m.from_user.id
    mtype, fid, tid = get_media(m)
    if not fid:
        await m.reply("📤 ꜱᴇɴᴅ ᴀ <b>ᴠɪᴅᴇᴏ</b> ꜰɪʟᴇ ɴᴏᴡ...", parse_mode=PM_HTML); return
    s = get_sess(c, uid)
    s["data"].update({"file_id": fid, "type": mtype, "thumb_id": tid,
                      "caption": m.caption or ""})
    s["step"] = "up_ref"
    await m.reply("🏷️ ꜱᴇɴᴅ ʀᴇꜰᴇʀᴇɴᴄᴇ:\n\n▸ Season 2 Episode 6\n▸ S2 E6",
                  parse_mode=PM_HTML, disable_web_page_preview=True)

async def up_got_ref(c, m):
    uid = m.from_user.id
    pe = parse_episode(m.text)
    if not pe:
        await m.reply(INVALID_FMT, parse_mode=PM_HTML); return
    s, e = pe
    sess = get_sess(c, uid)
    if await c.store.get("episodes", ep_id(s, e)):
        await m.reply(f"⚠️ <b>ꜱ{ꜱ}" .replace("ꜱ", "S") if False else f"⚠️ <b>ꜱ{s} ᴇ{e} ᴀʟʀᴇᴀᴅʏ ᴇxɪꜱᴛꜱ!</b>\n\nᴜꜱᴇ /ᴇᴅɪᴛ ᴛᴏ ʀᴇᴘʟᴀᴄᴇ ɪᴛ. ꜱᴇɴᴅ ᴀɴᴏᴛʜᴇʀ ʀᴇꜰᴇʀᴇɴᴄᴇ:",
                      parse_mode=PM_HTML)
        return
    d = sess["data"]
    await save_episode(c, uid, s, e, d["file_id"], d["type"], d.get("caption"), d.get("thumb_id"))
    d["added"] = d.get("added", 0) + 1
    sess["step"] = "up_video"
    await m.reply(f"✅ <b>ᴜᴘʟᴏᴀᴅᴇᴅ — ꜱ{ꜱ}" .replace("ꜱ", "S") if False else f"✅ <b>ᴜᴘʟᴏᴀᴅᴇᴅ — ꜱ{s} ᴇ{e}</b>\n\n📤 ꜱᴇɴᴅ ɴᴇxᴛ ᴠɪᴅᴇᴏ ᴏʀ ᴘʀᴇꜱꜱ 👇",
                  parse_mode=PM_HTML,
                  reply_markup=InlineKeyboardMarkup([[btn("🟢 ᴀᴅᴅ ᴀɴᴏᴛʜᴇʀ", "up|ep"), btn("🏁 ᴅᴏɴᴇ", "up|done")]]))

async def ns_got_season(c, m):
    uid = m.from_user.id
    txt = (m.text or "").strip()
    if not txt.isdigit() or not (1 <= int(txt) <= 999):
        await m.reply("🔢 ꜱᴇɴᴅ ᴀ ᴠᴀʟɪᴅ ꜱᴇᴀꜱᴏɴ ɴᴜᴍʙᴇʀ (ᴇx: 2):", parse_mode=PM_HTML); return
    if not (await perm_ok(c, uid, "seasons") or await perm_ok(c, uid, "upload")):
        await m.reply("❌ <b>ɴᴏ ꜱᴇᴀꜱᴏɴꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); clear_sess(c, uid); return
    s = get_sess(c, uid)
    s["data"].update({"ns_season": int(txt), "ns_ep": 1, "added": 0})
    s["step"] = "ns_video"
    await m.reply(f"🆕 <b>ꜱᴇᴀꜱᴏɴ {txt} ꜱᴛᴀʀᴛᴇᴅ — ᴇᴘɪꜱᴏᴅᴇ 1 ꜰʀᴏᴍ!</b>\n\n📤 ꜱᴇɴᴅ ᴠɪᴅᴇᴏꜱ ᴏɴᴇ ʙʏ ᴏɴᴇ...\n🏁 /ᴅᴏɴᴇ • ❌ /ᴄᴀɴᴄᴇʟ",
                  parse_mode=PM_HTML)

async def ns_got_video(c, m):
    uid = m.from_user.id
    mtype, fid, tid = get_media(m)
    if not fid:
        await m.reply("📤 ꜱᴇɴᴅ ᴀ <b>ᴠɪᴅᴇᴏ</b> ꜰɪʟᴇ:", parse_mode=PM_HTML); return
    s = get_sess(c, uid); d = s["data"]
    sn, en = d["ns_season"], d["ns_ep"]
    if await c.store.get("episodes", ep_id(sn, en)):
        await m.reply(f"⚠️ ꜱ{sn} ᴇ{en} ᴀʟʀᴇᴀᴅʏ ᴇxɪꜱᴛꜱ — ꜱᴋɪᴘᴘᴇᴅ!", parse_mode=PM_HTML)
        d["ns_ep"] = en + 1
        return
    await save_episode(c, uid, sn, en, fid, mtype, m.caption or "", tid)
    d["ns_ep"] = en + 1
    d["added"] = d.get("added", 0) + 1
    await m.reply(f"✅ <b>ꜱ{ꜱ}" .replace("ꜱ", "S") if False else f"✅ <b>ꜱ{sn} ᴇ{en} ᴀᴅᴅᴇᴅ!</b>\n\n📤 ꜱᴇɴᴅ ɴᴇxᴛ ᴠɪᴅᴇᴏ ᴏʀ /ᴅᴏɴᴇ", parse_mode=PM_HTML)

async def cmd_done(c, m):
    uid = m.from_user.id
    s = get_sess(c, uid)
    if s and s["step"] == "ns_video":
        d = s["data"]
        await m.reply(f"🏁 <b>ꜱᴇᴀꜱᴏɴ {d['ns_season']} ᴄᴏᴍᴘʟᴇᴛᴇ!</b>\n\n✅ {d.get('added', 0)} ᴇᴘɪꜱᴏᴅᴇꜱ ᴀᴅᴅᴇᴅ",
                      parse_mode=PM_HTML)
        await log_event(c, "🏁 ꜱᴇᴀꜱᴏɴ ʙᴀᴛᴄʜ ᴅᴏɴᴇ", f"ꜱ{d['ns_season']} • {d.get('added',0)} ᴇᴘꜱ", uid=uid)
        clear_sess(c, uid)
    elif s and str(s["step"]).startswith("up_"):
        await m.reply(f"🏁 <b>ᴜᴘʟᴏᴀᴅ ꜱᴇꜱꜱɪᴏɴ ꜰɪɴɪꜱʜᴇᴅ!</b>\n\n✅ {s['data'].get('added', 0)} ᴇᴘɪꜱᴏᴅᴇꜱ ᴀᴅᴅᴇᴅ",
                      parse_mode=PM_HTML)
        clear_sess(c, uid)
    else:
        await m.reply("❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴜᴘʟᴏᴀᴅ ꜱᴇꜱꜱɪᴏɴ.")

async def cmd_cancel(c, m):
    clear_sess(c, m.from_user.id)
    await m.reply("❌ <b>ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>", parse_mode=PM_HTML)

# ─────────── ᴇᴅɪᴛ / ᴅᴇʟᴇᴛᴇ ───────────
def edit_kb(s, e):
    return InlineKeyboardMarkup([
        [btn("🎬 ʀᴇᴘʟᴀᴄᴇ ᴠɪᴅᴇᴏ", f"ed|video|{s}:{e}"), btn("✏️ ᴇᴅɪᴛ ᴄᴀᴘᴛɪᴏɴ", f"ed|cap|{s}:{e}")],
        [btn("🖼️ ʀᴇᴘʟᴀᴄᴇ ᴛʜᴜᴍʙ", f"ed|thumb|{s}:{e}")],
        [btn("⬅️ ʙᴀᴄᴋ", "pan|refresh")]])

async def show_editor(c, chat_id, s, e):
    ep = await c.store.get("episodes", ep_id(s, e))
    if not ep:
        await c.send_message(chat_id, f"❌ ꜱ{s} ᴇ{e} ɴᴏᴛ ꜰᴏᴜɴᴅ!"); return
    txt = (f"✏️ <b>ᴇᴅɪᴛ — ꜱ{ꜱ}" .replace("ꜱ", "S") if False else f"✏️ <b>ᴇᴅɪᴛ — ꜱ{s} ᴇ{e}</b>\n━━━━━━━━━━━━━━\n"
           f"🎬 ᴛʏᴘᴇ: {ep.get('type','video')}\n"
           f"📝 ᴄᴀᴘᴛɪᴏɴ: {(ep.get('caption') or '—')[:80]}\n"
           f"🖼️ ᴛʜᴜᴍʙ: {'✅' if ep.get('thumb_id') or ep.get('thumb_path') else '❌'}\n"
           f"⏰ ᴜᴘᴅᴀᴛᴇᴅ: {dt(ep.get('updated_at', 0))}\n\nꜱᴇʟᴇᴄᴛ:")
    await c.send_message(chat_id, txt, reply_markup=edit_kb(s, e), parse_mode=PM_HTML)

async def cmd_edit(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "edit"):
        await m.reply("❌ <b>ɴᴏ ᴇᴅɪᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    ref = " ".join(m.command[1:])
    if ref:
        pe = parse_episode(ref)
        if not pe:
            await m.reply(INVALID_FMT, parse_mode=PM_HTML); return
        await show_editor(c, m.chat.id, *pe); return
    set_sess(c, uid, "ed_ref")
    await m.reply("✏️ ꜱᴇɴᴅ ᴇᴘɪꜱᴏᴅᴇ ʀᴇꜰᴇʀᴇɴᴄᴇ:\n\n▸ Season 1 Episode 4\n▸ S1 E4",
                  parse_mode=PM_HTML, disable_web_page_preview=True)

async def ed_got_ref(c, m):
    pe = parse_episode(m.text)
    if not pe:
        await m.reply(INVALID_FMT, parse_mode=PM_HTML); return
    clear_sess(c, m.from_user.id)
    await show_editor(c, m.chat.id, *pe)

async def cmd_delete(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "delete"):
        await m.reply("❌ <b>ɴᴏ ᴅᴇʟᴇᴛᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    ref = " ".join(m.command[1:])
    if not ref:
        set_sess(c, uid, "del_ref")
        await m.reply("🗑️ ꜱᴇɴᴅ ᴇᴘɪꜱᴏᴅᴇ ʀᴇꜰᴇʀᴇɴᴄᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ:\n\n▸ Season 1 Episode 4", parse_mode=PM_HTML)
        return
    pe = parse_episode(ref)
    if not pe:
        await m.reply(INVALID_FMT, parse_mode=PM_HTML); return
    await do_delete(c, m.chat.id, *pe)

async def do_delete(c, chat_id, s, e):
    if not await c.store.get("episodes", ep_id(s, e)):
        await c.send_message(chat_id, f"❌ ꜱ{s} ᴇ{e} ɴᴏᴛ ꜰᴏᴜɴᴅ!"); return
    await c.store.delete("episodes", ep_id(s, e))
    await log_event(c, "🗑️ ᴇᴘɪꜱᴏᴅᴇ ᴅᴇʟᴇᴛᴇᴅ", f"ꜱ{s} ᴇ{e}", important=True)
    await c.send_message(chat_id, f"🗑️ <b>ᴅᴇʟᴇᴛᴇᴅ — ꜱ{ꜱ}" .replace("ꜱ", "S") if False else f"🗑️ <b>ᴅᴇʟᴇᴛᴇᴅ — ꜱ{s} ᴇ{e}</b>", parse_mode=PM_HTML)

# ─────────── ʙʀᴏᴀᴅᴄᴀꜱᴛ ───────────
async def copy_any(c, chat_id, m):
    if m.text:
        return await c.send_message(chat_id, m.text, entities=m.entities, parse_mode=PM_OFF,
                                    disable_web_page_preview=True)
    cap = m.caption; cape = m.caption.entities if m.caption else None
    if m.photo:
        return await c.send_photo(chat_id, m.photo.file_id, caption=cap, caption_entities=cape, parse_mode=PM_OFF)
    if m.video:
        return await c.send_video(chat_id, m.video.file_id, caption=cap, caption_entities=cape, parse_mode=PM_OFF)
    if m.animation:
        return await c.send_animation(chat_id, m.animation.file_id, caption=cap, caption_entities=cape, parse_mode=PM_OFF)
    if m.audio:
        return await c.send_audio(chat_id, m.audio.file_id, caption=cap, caption_entities=cape, parse_mode=PM_OFF)
    if m.document:
        return await c.send_document(chat_id, m.document.file_id, caption=cap, caption_entities=cape, parse_mode=PM_OFF)
    if m.sticker:
        return await c.send_sticker(chat_id, m.sticker.file_id)
    if m.voice:
        return await c.send_voice(chat_id, m.voice.file_id, caption=cap, caption_entities=cape, parse_mode=PM_OFF)
    if m.video_note:
        return await c.send_video_note(chat_id, m.video_note.file_id)
    raise ValueError("ᴜɴꜱᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ")

async def edit_progress(msg, done, total, ok, fail):
    try:
        await msg.edit_text(f"📣 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ʀᴜɴɴɪɴɢ...</b>\n━━━━━━━━━━━━━━\n"
                            f"👥 ᴛᴏᴛᴀʟ: <b>{total}</b>\n📡 ꜱᴇɴᴛ: <b>{done}/{total}</b>\n"
                            f"✅ ꜱᴜᴄᴄᴇꜱꜱ: <b>{ok}</b>\n❌ ꜰᴀɪʟᴇᴅ: <b>{fail}</b>", parse_mode=PM_HTML)
    except FloodWait as f:
        await asyncio.sleep(f.value)
    except RPCError:
        pass

async def cmd_broadcast(c, m):
    uid = m.from_user.id
    src = m.reply_to_message
    args = m.command[1:]
    plan = []
    if c.is_factory and is_supreme(uid) and args:
        scope = args[0].lower()
        if scope == "all":
            for bid, cl in RUNNING.items():
                if cl.store.count("users") > 0:
                    plan.append((cl, f"@{cl.username}"))
            if not plan:
                await m.reply("❌ ɴᴏ ᴜꜱᴇʀꜱ ꜰᴏᴜɴᴅ."); return
        elif scope.isdigit():
            bid = int(scope)
            cl = RUNNING.get(bid)
            if not cl:
                await m.reply(f"🔴 ʙᴏᴛ {bid} ɴᴏᴛ ʀᴜɴɴɪɴɢ — ᴜꜱᴇ /ʀᴇꜱᴛᴀʀᴛ"); return
            plan = [(cl, f"@{cl.username}")]
        else:
            if not await perm_ok(c, uid, "broadcast"):
                await m.reply("❌ <b>ɴᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
            plan = [(c, f"@{c.username}")]
    else:
        if not await perm_ok(c, uid, "broadcast"):
            await m.reply("❌ <b>ɴᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
        plan = [(c, f"@{c.username}")]
    if src is None:
        await m.reply("📣 ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇꜱꜱᴀɢᴇ ᴡɪᴛʜ <code>/ʙʀᴏᴀᴅᴄᴀꜱᴛ</code>", parse_mode=PM_HTML); return
    status = await m.reply("📣 <b>ꜱᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀꜱᴛ...</b>", parse_mode=PM_HTML)
    await log_event(c, "📣 ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴛᴀʀᴛᴇᴅ", f"ʙʏ: {uid} | ꜱᴄᴏᴘᴇ: {', '.join(x[1] for x in plan)}",
                    important=True, uid=uid)
    total = sum(st.count("users") for _, st in plan) if False else sum(cl.store.count("users") for cl, _ in plan)
    done = ok = fail = 0
    for cl, label in plan:
        users = list(cl.store.c("users").keys())
        for u in users:
            try:
                await copy_any(cl, int(u), src)
                ok += 1
            except FloodWait as f:
                await asyncio.sleep(f.value)
                try:
                    await copy_any(cl, int(u), src); ok += 1
                except RPCError:
                    fail += 1
            except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):
                fail += 1
            except RPCError:
                fail += 1
            except Exception:
                fail += 1
            done += 1
            if done % 15 == 0:
                await edit_progress(status, done, total, ok, fail)
            await asyncio.sleep(0.05)
        await cl.store.put("broadcast_logs", secrets.token_hex(5),
                           {"scope": label, "total": len(users), "success": ok, "failed": fail,
                            "by": uid, "at": now()})
        await touch_active(cl)
    try:
        await status.edit_text(f"📣 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜰɪɴɪꜱʜᴇᴅ!</b>\n━━━━━━━━━━━━━━\n"
                               f"👥 ᴛᴏᴛᴀʟ: <b>{total}</b>\n✅ ꜱᴜᴄᴄᴇꜱꜱ: <b>{ok}</b>\n"
                               f"❌ ꜰᴀɪʟᴇᴅ: <b>{fail}</b>\n🎯 ʀᴀᴛᴇ: <b>{(ok/total*100 if total else 0):.1f}%</b>",
                               parse_mode=PM_HTML)
    except RPCError:
        pass
    await log_event(c, "📣 ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜰɪɴɪꜱʜᴇᴅ", f"✅ {ok} | ❌ {fail}", important=True, uid=uid)

# ─────────── ꜱᴛᴀᴛꜱ / ʟɪꜱᴛ ───────────
def store_db_size(store): return store.size()

def build_bot_stats(c):
    store = c.store
    users = store.count("users")
    today = sum(1 for u in store.c("users").values() if u.get("started_at", 0) >= DAY_START())
    eps = store.count("episodes")
    seasons = len({k.split(":")[0] for k in store.c("episodes")})
    admins = store.count("admins")
    bcs = store.count("broadcast_logs")
    meta = FACTORY.get_sync("bots", c.bot_id) if FACTORY else None
    created = dt(meta["created_at"]) if meta else dt(cfg(store).get("created_at", START_TS))
    return (f"📊 <b>ʙᴏᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ</b>\n━━━━━━━━━━━━━━\n"
            f"🤖 ʙᴏᴛ: @{c.username}\n"
            f"👥 ᴜꜱᴇʀꜱ: <b>{users}</b>\n"
            f"🆕 ᴛᴏᴅᴀʏ'ꜱ ᴜꜱᴇʀꜱ: <b>{today}</b>\n"
            f"🎬 ᴇᴘɪꜱᴏᴅᴇꜱ: <b>{eps}</b>\n"
            f"📚 ꜱᴇᴀꜱᴏɴꜱ: <b>{seasons}</b>\n"
            f"💾 ᴅʙ ꜱɪᴢᴇ: <b>{human_size(store_db_size(store))}</b>\n"
            f"🗄️ ꜱᴛᴏʀᴀɢᴇ ᴜꜱᴇᴅ: <b>{human_size(store.size())}</b>\n"
            f"⏱️ ᴜᴘᴛɪᴍᴇ: <b>{hms(now() - START_TS)}</b>\n"
            f"📅 ᴄʀᴇᴀᴛᴇᴅ: {created}\n"
            f"🛡️ ᴀᴅᴍɪɴꜱ: <b>{admins}</b>\n"
            f"📣 ʙʀᴏᴀᴅᴄᴀꜱᴛꜱ: <b>{bcs}</b>")

def build_global_stats():
    tb = FACTORY.count("bots") if FACTORY else 0
    tu = te = today = 0
    for st in [FACTORY] + list(STORES.values()):
        if st is None: continue
        tu += st.count("users")
        te += st.count("episodes")
        today += sum(1 for u in st.c("users").values() if u.get("started_at", 0) >= DAY_START())
    size = sum(os.path.getsize(os.path.join(DB_DIR, f)) for f in os.listdir(DB_DIR)
               if f.endswith(".json")) if os.path.isdir(DB_DIR) else 0
    return (f"🌐 <b>ꜱᴜᴘʀᴇᴍᴇ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ</b>\n━━━━━━━━━━━━━━\n"
            f"🤖 ᴛᴏᴛᴀʟ ʙᴏᴛꜱ: <b>{tb}</b> (🟢 {len(RUNNING) - 1 if FACTORY_CLIENT else len(RUNNING)} ʀᴜɴɴɪɴɢ)\n"
            f"👥 ᴛᴏᴛᴀʟ ᴜꜱᴇʀꜱ: <b>{tu}</b>\n"
            f"🎬 ᴛᴏᴛᴀʟ ᴇᴘɪꜱᴏᴅᴇꜱ: <b>{te}</b>\n"
            f"🆕 ᴛᴏᴅᴀʏ'ꜱ ᴜꜱᴇʀꜱ: <b>{today}</b>\n"
            f"💾 ꜱᴛᴏʀᴀɢᴇ: <b>{human_size(size)}</b>\n"
            f"⏱️ ᴜᴘᴛɪᴍᴇ: <b>{hms(now() - START_TS)}</b>")

async def cmd_stats(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "stats"):
        await m.reply("❌ <b>ɴᴏ ꜱᴛᴀᴛꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    if c.is_factory and is_supreme(uid):
        await m.reply(build_global_stats(), parse_mode=PM_HTML)
    else:
        await m.reply(build_bot_stats(c), parse_mode=PM_HTML)

async def cmd_list(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "list"):
        await m.reply("❌ <b>ɴᴏ ʟɪꜱᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    seasons = {}
    for k, v in c.store.c("episodes").items():
        seasons.setdefault(v["season"], []).append(v["episode"])
    if not seasons:
        await m.reply("📭 ɴᴏ ᴇᴘɪꜱᴏᴅᴇꜱ ʏᴇᴛ."); return
    text = f"📺 <b>ᴇᴘɪꜱᴏᴅᴇ ʟɪꜱᴛ</b>\n━━━━━━━━━━━━━━\n"
    for s in sorted(seasons):
        text += f"\n🟣 <b>ꜱᴇᴀꜱᴏɴ {s}</b>\n"
        for e in sorted(seasons[s]):
            text += f"   ▸ ᴇᴘɪꜱᴏᴅᴇ {e}\n"
    for part in chunk(text):
        try:
            await m.reply(part, parse_mode=PM_HTML, disable_web_page_preview=True)
        except RPCError:
            pass
        await asyncio.sleep(0.3)

# ─────────── ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ ───────────
def admin_panel_kb():
    return InlineKeyboardMarkup([
        [btn("🟢 ᴜᴘʟᴏᴀᴅ", "pan|upload"), btn("🔵 ᴇᴅɪᴛ", "pan|edit"), btn("🔴 ᴅᴇʟᴇᴛᴇ", "pan|del")],
        [btn("🟣 ʙʀᴏᴀᴅᴄᴀꜱᴛ", "pan|bc"), btn("🟠 ꜱᴛᴀᴛꜱ", "pan|stats"), btn("⚪ ʟɪꜱᴛ", "pan|list")],
        [btn("🔐 ꜰᴏʀᴄᴇ ꜱᴜʙ", "pan|fs"), btn("📝 ꜱᴛᴀʀᴛ ᴍꜱɢ", "pan|es"), btn("👥 ᴀᴅᴍɪɴꜱ", "pan|admins")]])

async def cmd_admin(c, m):
    uid = m.from_user.id
    doc = await c.store.get("admins", uid)
    if not doc and not is_supreme(uid):
        await m.reply("❌ ʏᴏᴜ'ʀᴇ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ ʜᴇʀᴇ."); return
    role = ROLE_NAME.get(doc["role"], doc["role"]) if doc else "👑 ꜱᴜᴘʀᴇᴍᴇ"
    await m.reply(ADMIN_PANEL_TXT.format(uname=c.username, role=role),
                  reply_markup=admin_panel_kb(), parse_mode=PM_HTML)

# ─────────── ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ (ɢɪᴠᴇ/ᴇᴅɪᴛ/ʀᴇᴍ) ───────────
def selector_text(d):
    return (f"👤 <b>{d.get('name','ᴜꜱᴇʀ')}</b> (<code>{d['uid']}</code>)\n"
            f"🏷️ ʀᴏʟᴇ: <b>{ROLE_NAME.get(d['role'], d['role'])}</b>\n\n"
            f"🎨 ᴛᴏɢɢʟᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ → 💾 ꜱᴀᴠᴇ")

def selector_kb(d):
    uid = d["uid"]; perms = set(d["perms"])
    rows = [[btn("🛠 ᴍᴀɴᴀɢᴇʀ", f"adm|role|{uid}|manager"), btn("⬆️ ᴜᴘʟᴏᴀᴅᴇʀ", f"adm|role|{uid}|uploader")],
            [btn("📣 ʙʀᴏᴀᴅᴄᴀꜱᴛᴇʀ", f"adm|role|{uid}|broadcaster"), btn("📊 ᴀɴᴀʟʏꜱᴛ", f"adm|role|{uid}|analyst")],
            [btn("⚙️ ᴄᴜꜱᴛᴏᴍ", f"adm|role|{uid}|custom")]]
    items = list(PERM_LABELS.items())
    for i in range(0, len(items), 2):
        rows.append([btn(("☑️ " if p in perms else "❌ ") + lbl, f"adm|t|{uid}|{p}") for p, lbl in items[i:i + 2]])
    rows.append([btn("💾 ꜱᴀᴠᴇ", f"adm|save|{uid}"), btn("🗑 ʀᴇᴍᴏᴠᴇ", f"adm|rem|{uid}")])
    rows.append([btn("⬅️ ʙᴀᴄᴋ", "pan|admins")])
    return InlineKeyboardMarkup(rows)

def msg_target(m):
    if m.reply_to_message and m.reply_to_message.from_user:
        tu = m.reply_to_message.from_user
        return tu.id, tu.first_name or str(tu.id)
    if len(m.command) > 1 and m.command[1].lstrip("-").isdigit():
        return int(m.command[1]), (" ".join(m.command[2:]) or m.command[1])
    return None, None

async def open_selector(c, m, t, name, must_exist=False):
    exist = await c.store.get("admins", t)
    if must_exist and not exist:
        await m.reply("❌ ᴛʜᴀᴛ ᴜꜱᴇʀ ɪꜱ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ."); return
    if exist and exist.get("role") == "owner":
        await m.reply("👑 ᴄʟᴏɴᴇ ᴏᴡɴᴇʀ'ꜱ ᴘᴇʀᴍꜱ ᴄᴀɴ'ᴛ ʙᴇ ᴄʜᴀɴɢᴇᴅ."); return
    d = {"uid": t, "name": hesc(name or (exist or {}).get("name") or str(t)),
         "perms": list(exist["permissions"]) if exist else [],
         "role": exist["role"] if exist else "custom", "new": exist is None}
    set_sess(c, m.from_user.id, "adm_edit", **d)
    await m.reply(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)

async def cmd_giveadmin(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "manage_admins"):
        await m.reply("❌ <b>ɴᴏ ᴍᴀɴᴀɢᴇ-ᴀᴅᴍɪɴꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    t, name = msg_target(m)
    if not t:
        set_sess(c, uid, "ga_target")
        await m.reply("👤 ʀᴇᴘʟʏ ᴛᴏ ᴜꜱᴇʀ ᴏʀ ꜱᴇɴᴅ ɪᴅ:\n<code>/ɢɪᴠᴇᴀᴅᴍɪɴ 123456789 ɴᴀᴍᴇ</code>".translate(_SMALL_MAP),
                      parse_mode=PM_HTML)
        return
    await open_selector(c, m, t, name)

async def cmd_editadmin(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "manage_admins"):
        await m.reply("❌ <b>ɴᴏ ᴍᴀɴᴀɢᴇ-ᴀᴅᴍɪɴꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    t, name = msg_target(m)
    if not t:
        set_sess(c, uid, "ea_target")
        await m.reply("✏️ ʀᴇᴘʟʏ ᴛᴏ ᴀᴅᴍɪɴ ᴏʀ ꜱᴇɴᴅ ɪᴅ:", parse_mode=PM_HTML); return
    await open_selector(c, m, t, name, must_exist=True)

async def cmd_remadmin(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "manage_admins"):
        await m.reply("❌ <b>ɴᴏ ᴍᴀɴᴀɢᴇ-ᴀᴅᴍɪɴꜱ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    t, _ = msg_target(m)
    if not t:
        set_sess(c, uid, "ra_target")
        await m.reply("🗑 ʀᴇᴘʟʏ ᴛᴏ ᴀᴅᴍɪɴ ᴏʀ ꜱᴇɴᴅ ɪᴅ:", parse_mode=PM_HTML); return
    tgt = await c.store.get("admins", t)
    if not tgt:
        await m.reply("❌ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ."); return
    if tgt.get("role") == "owner":
        await m.reply("👑 ᴄʟᴏɴᴇ ᴏᴡɴᴇʀ ᴄᴀɴ'ᴛ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ!"); return
    await c.store.delete("admins", t)
    await log_event(c, "🚫 ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ", f"ᴀᴅᴍɪɴ: {t}", important=True, uid=t)
    await m.reply("🗑 <b>ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ!</b>", parse_mode=PM_HTML)

async def show_admins_list(c, chat_id, edit_msg=None):
    docs = c.store.find("admins")
    order = {"owner": 0, "manager": 1, "uploader": 2, "broadcaster": 3, "analyst": 4, "custom": 5}
    docs.sort(key=lambda d: order.get(d.get("role"), 9))
    if not docs:
        txt, kb = "👥 ɴᴏ ᴀᴅᴍɪɴꜱ ʏᴇᴛ.", admin_panel_kb()
    else:
        rows = [[btn(f"{ROLE_NAME.get(d['role'],'⚙️')} {d.get('name','?')[:18]}",
                     f"adm|view|{d['_id']}") for d in docs[i:i + 2]] for i in range(0, len(docs), 2)]
        rows.append([btn("⬅️ ʙᴀᴄᴋ", "pan|refresh")])
        txt, kb = f"👥 <b>ᴀᴅᴍɪɴꜱ ({len(docs)})</b>\n\nᴛᴀᴘ ᴛᴏ ᴇᴅɪᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ:", InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

# ─────────── ꜰᴏʀᴄᴇ-ꜱᴜʙ & ꜱᴇᴛᴛɪɴɢꜱ ───────────
def fs_panel_kb():
    return InlineKeyboardMarkup([
        [btn("🟢 ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟ", "fs|public"), btn("🔵 ᴘʀɪᴠᴀᴛᴇ ʀᴇQᴜᴇꜱᴛ", "fs|private")],
        [btn("🔴 ᴅɪꜱᴀʙʟᴇ", "fs|off"), btn("🧾 ʟᴏɢ ᴄʜᴀɴɴᴇʟ", "fs|logch")]])

async def show_fs_panel(c, chat_id, edit_msg=None):
    st = cfg(c.store)
    mode = st.get("fs_mode", "off")
    mtxt = {"off": "❴🔴❵ ᴏꜰꜰ", "public": "❴🟢❵ ᴘᴜʙʟɪᴄ", "private": "❴🔵❵ ᴘʀɪᴠᴀᴛᴇ ʀᴇQᴜᴇꜱᴛ"}.get(mode, mode)
    ch = f"@{st['fs_username']}" if st.get("fs_username") else (st.get("fs_channel") or "—")
    txt = (f"🔐 <b>ꜰᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ</b>\n━━━━━━━━━━━━━━\n"
           f"📊 ꜱᴛᴀᴛᴜꜱ: <b>{mtxt}</b>\n📢 ᴄʜᴀɴɴᴇʟ: <code>{ch}</code>\n"
           f"🧾 ʟᴏɢ ᴄʜ: <code>{st.get('log_channel') or '—'}</code>\n\n"
           "🟢 ᴘᴜʙʟɪᴄ = ᴍᴇᴍʙᴇʀꜱʜɪᴘ ᴄʜᴇᴄᴋ\n🔵 ᴘʀɪᴠᴀᴛᴇ = ᴊᴏɪɴ ʀᴇQᴜᴇꜱᴛ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ")
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=fs_panel_kb(), parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=fs_panel_kb(), parse_mode=PM_HTML)

async def cmd_setfs(c, m):
    if not await perm_ok(c, m.from_user.id, "forcesub"):
        await m.reply("❌ <b>ɴᴏ ꜰᴏʀᴄᴇ-ꜱᴜʙ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    await show_fs_panel(c, m.chat.id)

async def validate_channel(c, ref):
    try:
        chat = await c.get_chat(ref)
    except RPCError:
        return None
    try:
        mem = await c.get_chat_member(chat.id, "me")
        if mem.status not in (CMS.OWNER, CMS.ADMINISTRATOR):
            return None
    except RPCError:
        return None
    return chat

async def fs_got_channel(c, m, mode):
    ref = (m.text or "").strip()
    chat = await validate_channel(c, ref)
    if not chat:
        await m.reply("❌ <b>ᴄᴀɴ'ᴛ ᴀᴄᴄᴇꜱꜱ ᴄʜᴀɴɴᴇʟ!</b> (ʙᴏᴛ ᴍᴜꜱᴛ ʙᴇ ᴀᴅᴍɪɴ)\nꜱᴇɴᴅ ᴀɢᴀɪɴ ᴏʀ /ᴄᴀɴᴄᴇʟ", parse_mode=PM_HTML)
        return
    store = c.store
    if mode == "public":
        if not chat.username:
            await m.reply("❌ ᴛʜɪꜱ ɪꜱ ᴀ ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ — ᴜꜱᴇ 🔵 ᴘʀɪᴠᴀᴛᴇ ᴍᴏᴅᴇ.", parse_mode=PM_HTML); return
        await set_cfg(store, fs_mode="public", fs_channel=chat.id, fs_username=chat.username)
        await m.reply(f"✅ <b>ᴘᴜʙʟɪᴄ ꜰꜱ ᴏɴ!</b>\n\n📢 @{chat.username}", parse_mode=PM_HTML)
    else:
        try:
            link = await c.create_chat_invite_link(chat.id, creates_join_request=True)
        except RPCError:
            await m.reply("❌ ɪɴᴠɪᴛᴇ ʟɪɴᴋ ꜰᴀɪʟᴇᴅ — ɢɪᴠᴇ ʙᴏᴛ ɪɴᴠɪᴛᴇ ᴘᴇʀᴍɪꜱꜱɪᴏɴ.", parse_mode=PM_HTML); return
        await set_cfg(store, fs_mode="private", fs_channel=chat.id, fs_link=link.invite_link,
                      fs_username=chat.username or "")
        await m.reply(f"✅ <b>ᴘʀɪᴠᴀᴛᴇ ʀᴇQᴜᴇꜱᴛ ꜰꜱ ᴏɴ!</b>\n\n🔗 ʟɪɴᴋ ʀᴇᴀᴅʏ — ᴊᴏɪɴ ʀᴇQᴜᴇꜱᴛꜱ ᴀᴜᴛᴏ-ᴀᴘᴘʀᴏᴠᴇ ʜᴏɴɢᴇ", parse_mode=PM_HTML)
    await log_event(c, "🔐 ꜰᴏʀᴄᴇ-ꜱᴜʙ ᴄʜᴀɴɢᴇᴅ", f"ᴍᴏᴅᴇ: {mode} | ᴄʜᴀᴛ: {chat.id}", important=True)
    clear_sess(c, m.from_user.id)

async def fs_got_logch(c, m):
    chat = await validate_channel(c, (m.text or "").strip())
    if not chat:
        await m.reply("❌ ʙᴏᴛ ᴄʜᴀɴɴᴇʟ ᴍᴇɪɴ ᴀᴅᴍɪɴ ɴʜɪ ʜᴀɪ / ᴄᴀɴ'ᴛ ᴀᴄᴄᴇꜱꜱ. ᴀɢᴀɪɴ ꜱᴇɴᴅ ᴋᴀʀᴏ ᴏʀ /ᴄᴀɴᴄᴇʟ", parse_mode=PM_HTML)
        return
    await set_cfg(c.store, log_channel=chat.id)
    clear_sess(c, m.from_user.id)
    await m.reply(f"🧾 <b>ʟᴏɢ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛ!</b>\n\n📥 <code>{chat.id}</code>", parse_mode=PM_HTML)
    await log_event(c, "🧾 ʟᴏɢ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛ", f"{chat.id}")

# ─────────── ᴇᴅɪᴛ ꜱᴛᴀʀᴛ ───────────
async def cmd_editstart(c, m):
    if not await perm_ok(c, m.from_user.id, "editstart"):
        await m.reply("❌ <b>ɴᴏ ᴇᴅɪᴛ-ꜱᴛᴀʀᴛ ᴘᴇʀᴍɪꜱꜱɪᴏɴ!</b>", parse_mode=PM_HTML); return
    if len(m.command) > 1 and m.command[1].lower() == "reset":
        await c.store.put("settings", "start", {"type": "text", "text": DEFAULT_START})
        await m.reply("♻️ ꜱᴛᴀʀᴛ ᴍꜱɢ ʀᴇꜱᴇᴛ ᴛᴏ ᴅᴇꜰᴀᴜʟᴛ!"); return
    set_sess(c, m.from_user.id, "es_media")
    await m.reply("📝 ʀᴇᴘʟʏ/ꜱᴇɴᴅ ᴛʜᴇ ɴᴇᴡ ꜱᴛᴀʀᴛ ᴍᴇꜱꜱᴀɢᴇ:\n\n"
                  "▸ ᴛᴇxᴛ / ᴘʜᴏᴛᴏ / ᴠɪᴅᴇᴏ / ᴀɴɪᴍᴀᴛɪᴏɴ / ᴅᴏᴄᴜᴍᴇɴᴛ\n"
                  "▸ ᴠᴀʀꜱ: {name} {username} {botname}\n"
                  "▸ ʀᴇꜱᴇᴛ: /ᴇᴅɪᴛꜱᴛᴀʀᴛ ʀᴇꜱᴇᴛ".translate(_SMALL_MAP).replace("{name}", "{name}"),
                  parse_mode=PM_HTML, disable_web_page_preview=True)

async def es_got(c, m):
    uid = m.from_user.id
    if m.text and not m.media_group_id:
        await c.store.put("settings", "start", {"type": "text", "text": m.text})
        kind = "ᴛᴇxᴛ"
    else:
        mtype, fid, _ = get_media(m)
        if m.photo:
            mtype, fid = "photo", m.photo.file_id
        if not fid:
            await m.reply("❌ ꜱᴇɴᴅ ᴛᴇxᴛ ᴏʀ ᴍᴇᴅɪᴀ!", parse_mode=PM_HTML); return
        await c.store.put("settings", "start", {"type": mtype, "text": m.caption or "", "file_id": fid})
        kind = mtype
    clear_sess(c, uid)
    await m.reply(f"✅ <b>ꜱᴛᴀʀᴛ ᴍꜱɢ ᴜᴘᴅᴀᴛᴇᴅ!</b> ({kind})\n\n⚡ ɪɴꜱᴛᴀɴᴛʟʏ ᴀᴄᴛɪᴠᴇ!", parse_mode=PM_HTML)
    await log_event(c, "📝 ꜱᴛᴀʀᴛ ᴍꜱɢ ᴇᴅɪᴛᴇᴅ", kind, important=True, uid=uid)

# ─────────── ᴄʟᴏɴᴇ ꜰᴀᴄᴛᴏʀʏ ───────────
async def cmd_clone(c, m):
    if not c.is_factory: return
    uid = m.from_user.id
    s = get_sess(c, uid)
    if s and s.get("step") == "clone_token":
        await m.reply("⏳ ᴛᴏᴋᴇɴ ᴋᴀ ᴡᴀɪᴛ ʜᴏ ʀʜᴀ ʜᴀɪ — ꜱᴇɴᴅ ɪᴛ ᴏʀ /ᴄᴀɴᴄᴇʟ"); return
    set_sess(c, uid, "clone_token")
    await m.reply(CLONE_PROMPT, reply_markup=InlineKeyboardMarkup([[btn("🔴 ᴄᴀɴᴄᴇʟ", "cl|cancel")]]),
                  parse_mode=PM_HTML, disable_web_page_preview=True)

async def clone_token(c, m):
    uid = m.from_user.id
    sess = get_sess(c, uid)
    if not sess or sess.get("step") != "clone_token": return
    tok = (m.text or "").strip()
    if not re.match(r"^\d{6,12}:[A-Za-z0-9_-]{30,}$", tok):
        await m.reply("❌ ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ ꜰᴏʀᴍᴀᴛ — ᴀɢᴀɪɴ ꜱᴇɴᴅ ᴋᴀʀᴏ ᴏʀ /ᴄᴀɴᴄᴇʟ"); return
    pre = int(tok.split(":", 1)[0])
    if FACTORY.get_sync("bots", pre) or (FACTORY_CLIENT and pre == FACTORY_CLIENT.bot_id):
        clear_sess(c, uid)
        await m.reply("⚠️ <b>ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ᴀʟʀᴇᴀᴅʏ ʀᴇɢɪꜱᴛᴇʀᴇᴅ!</b>", parse_mode=PM_HTML); return
    st = await m.reply("⏳ ᴠᴀʟɪᴅᴀᴛɪɴɢ ᴛᴏᴋᴇɴ & ꜱᴛᴀʀᴛɪɴɢ ʙᴏᴛ...")
    tmp = Client(name=f"cf{now()}", api_id=API_ID, api_hash=API_HASH, bot_token=tok,
                 in_memory=True, sleep_threshold=15)
    try:
        await tmp.start()
    except (AccessTokenInvalid, AccessTokenExpired):
        clear_sess(c, uid)
        await st.edit("❌ ɪɴᴠᴀʟɪᴅ/ʀᴇᴠᴏᴋᴇᴅ ᴛᴏᴋᴇɴ — @ʙᴏᴛꜰᴀᴛʜᴇʀ ꜱᴇ ꜰʀᴇꜱʜ ᴛᴏᴋᴇɴ ʟᴏ!"); return
    except Exception as e:
        LOG.error("ᴄʟᴏɴᴇ ꜱᴛᴀʀᴛ ꜰᴀɪʟ: %s", e)
        clear_sess(c, uid)
        await st.edit("⚠️ ʙᴏᴛ ꜱᴛᴀʀᴛ ɴʜɪ ʜᴜᴀ — ᴛʜᴏᴅɪ ᴅᴇʀ ʙᴀᴀᴅ ᴛʀʏ ᴋᴀʀᴏ."); return
    me = await tmp.get_me()
    if FACTORY_CLIENT and me.id == FACTORY_CLIENT.bot_id:
        await tmp.stop(); clear_sess(c, uid)
        await st.edit("⚠️ ʏᴇ ꜰᴀᴄᴛᴏʀʏ ɪᴛꜱᴇʟꜰ ʜᴀɪ!"); return
    if FACTORY.get_sync("bots", me.id):
        await tmp.stop(); clear_sess(c, uid)
        await st.edit(f"⚠️ @{me.username} ᴘᴇʜʟᴇ ꜱᴇ ʀᴇɢɪꜱᴛᴇʀᴇᴅ ʜᴀɪ!"); return
    store = get_store(me.id)
    await ensure_defaults(store)
    await set_cfg(store, owner_id=uid)
    await FACTORY.put("bots", me.id, {"_id": me.id, "username": me.username or str(me.id),
                                      "name": me.first_name or "ʙᴏᴛ", "owner_id": uid,
                                      "owner_name": m.from_user.first_name or str(uid),
                                      "token_enc": enc_token(tok), "created_at": now(), "last_active": now()})
    await store.put("admins", uid, {"_id": str(uid), "name": hesc(m.from_user.first_name or uid),
                                    "role": "owner", "permissions": list(PERMS), "added_by": 0, "at": now()})
    attach(tmp, me, store, is_factory=False)
    register_provider_handlers(tmp, is_factory=False)
    await apply_commands(tmp)
    RUNNING[me.id] = tmp
    clear_sess(c, uid)
    await st.edit(CLONE_SUCCESS.format(name=hesc(m.from_user.first_name or ""), uname=me.username, bid=me.id),
                  parse_mode=PM_HTML, disable_web_page_preview=True)
    await log_event(tmp, "🎉 ᴄʟᴏɴᴇ ᴄʀᴇᴀᴛᴇᴅ", f"ᴏᴡɴᴇʀ: {uid} (@{m.from_user.username})\nʙᴏᴛ: @{me.username} ({me.id})",
                    important=True, uid=uid)

# ─────────── ꜱᴜᴘʀᴇᴍᴇ ───────────
def build_botlist_text():
    lines = [f"🤖 <b>ʙᴏᴛ ʟɪꜱᴛ ({FACTORY.count('bots') if FACTORY else 0})</b>", "━━━━━━━━━━━━━━"]
    for meta in (FACTORY.find("bots") if FACTORY else []):
        bid = meta["_id"]
        st = STORES.get(bid)
        users = st.count("users") if st else 0
        eps = st.count("episodes") if st else 0
        running = "🟢" if bid in RUNNING else "🔴"
        size = human_size(st.size() if st else 0)
        lines.append(
            f"\n{running} <b>@{meta['username']}</b> — <code>{bid}</code>\n"
            f"👤 ᴏᴡɴᴇʀ: {hesc(meta.get('owner_name','?'))} (<code>{meta.get('owner_id')}</code>)\n"
            f"👥 ᴜꜱᴇʀꜱ: {users} | 🎬 ᴇᴘꜱ: {eps} | 🗄️ {size}\n"
            f"⏰ ʟᴀꜱᴛ ᴀᴄᴛɪᴠᴇ: {dt(meta.get('last_active', 0))}\n"
            f"📅 ᴄʀᴇᴀᴛᴇᴅ: {dt(meta.get('created_at', 0))}")
    if len(lines) == 2:
        lines.append("ɴᴏ ᴄʟᴏɴᴇꜱ ʏᴇᴛ — /ᴄʟᴏɴᴇ ꜱᴇ ʙᴀɴᴀᴏ!")
    return "\n".join(lines)

def build_db_report():
    files = sorted(f for f in os.listdir(DB_DIR) if f.endswith(".json")) if os.path.isdir(DB_DIR) else []
    total_users = total_eps = total_admins = 0
    seasons = set()
    colls = set()
    healthy = 0
    lines = ["🗄️ <b>ᴅᴀᴛᴀʙᴀꜱᴇ ɪɴꜱɪɢʜᴛꜱ</b>", "━━━━━━━━━━━━━━"]
    for f in files:
        path = os.path.join(DB_DIR, f)
        size = os.path.getsize(path)
        data = {}
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            healthy += 1
        except Exception:
            lines.append(f"🔴 <code>{f}</code> — ᴄᴏʀʀᴜᴘᴛ! ({human_size(size)})")
            continue
        u = len(data.get("users", {})); e = len(data.get("episodes", {}))
        total_users += u; total_eps += e; total_admins += len(data.get("admins", {}))
        for k in data.get("episodes", {}):
            seasons.add(k.split(":")[0])
        colls.update(data.keys())
        lines.append(f"🟢 <code>{f}</code> — 👥{u} 🎬{e} ({human_size(size)})")
    lines.append("━━━━━━━━━━━━━━")
    lines.append(f"🤖 ᴄʟᴏɴᴇꜱ: <b>{FACTORY.count('bots') if FACTORY else 0}</b>")
    lines.append(f"👥 ᴜꜱᴇʀꜱ: <b>{total_users}</b> | 🎬 ᴇᴘɪꜱᴏᴅᴇꜱ: <b>{total_eps}</b>")
    lines.append(f"📚 ꜱᴇᴀꜱᴏɴꜱ: <b>{len(seasons)}</b> | 🛡️ ᴀᴅᴍɪɴꜱ: <b>{total_admins}</b>")
    lines.append(f"🧾 ᴄᴏʟʟᴇᴄᴛɪᴏɴꜱ: <b>{len(colls)}</b>")
    lines.append(f"🧷 ɪɴᴅᴇxᴇꜱ: ᴋᴇʏᴇᴅ-ᴅᴏᴄꜱ (O(1) ʟᴏᴏᴋᴜᴘ) ✅")
    health = f"{(healthy / len(files) * 100):.0f}%" if files else "100%"
    lines.append(f"💚 ᴅʙ ʜᴇᴀʟᴛʜ: <b>{health}</b> ({healthy}/{len(files)} ꜰɪʟᴇꜱ)")
    lines.append(f"💾 ᴛᴏᴛᴀʟ: <b>{human_size(sum(os.path.getsize(os.path.join(DB_DIR, f)) for f in files))}</b>")
    return "\n".join(lines)

async def restart_all(status_msg, only=None):
    metas = FACTORY.find("bots", lambda d: only is None or d["_id"] == only)
    okc = fail = 0
    for meta in metas:
        bid = meta["_id"]
        old = RUNNING.get(bid)
        if old:
            try: await old.stop()
            except Exception: pass
            RUNNING.pop(bid, None)
        cl = await launch_clone(meta)
        if cl: okc += 1
        else: fail += 1
    try:
        await status_msg.edit_text(f"♻️ <b>ʀᴇꜱᴛᴀʀᴛ ᴄᴏᴍᴘʟᴇᴛᴇ!</b>\n\n✅ {okc} | ❌ {fail}", parse_mode=PM_HTML)
    except RPCError:
        pass
    await dev_log(f"♻️ ʙᴏᴛꜱ ʀᴇꜱᴛᴀʀᴛᴇᴅ — ✅{okc} ❌{fail}")

async def cmd_supreme(c, m):
    if not is_supreme(m.from_user.id): return
    kb = InlineKeyboardMarkup([
        [btn("🤖 ʙᴏᴛ ʟɪꜱᴛ", "sv|botlist"), btn("🗄️ ᴅᴀᴛᴀʙᴀꜱᴇ", "sv|db")],
        [btn("📊 ɢʟᴏʙᴀʟ ꜱᴛᴀᴛꜱ", "sv|stats"), btn("♻️ ʀᴇꜱᴛᴀʀᴛ ᴀʟʟ", "sv|restart")]])
    await m.reply(f"👑 <b>ꜱᴜᴘʀᴇᴍᴇ ᴘᴀɴᴇʟ</b>\n━━━━━━━━━━━━━━\n"
                  f"🤖 ʙᴏᴛꜱ: <b>{FACTORY.count('bots') if FACTORY else 0}</b>\n"
                  f"🟢 ʀᴜɴɴɪɴɢ: <b>{len(RUNNING) - (1 if FACTORY_CLIENT else 0)}</b>\n\n"
                  f"📣 ɢʟᴏʙᴀʟ ʙʀᴏᴀᴅᴄᴀꜱᴛ: <code>/ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴀʟʟ</code>\n"
                  f"🎯 ᴏɴᴇ ʙᴏᴛ: <code>/ʙʀᴏᴀᴅᴄᴀꜱᴛ 123456</code>",
                  reply_markup=kb, parse_mode=PM_HTML)

async def cmd_botlist(c, m):
    if not is_supreme(m.from_user.id): return
    for part in chunk(build_botlist_text()):
        try: await m.reply(part, parse_mode=PM_HTML, disable_web_page_preview=True)
        except RPCError: pass
        await asyncio.sleep(0.3)

async def cmd_db(c, m):
    if not is_supreme(m.from_user.id): return
    await m.reply(build_db_report(), parse_mode=PM_HTML, disable_web_page_preview=True)

async def cmd_restart(c, m):
    if not is_supreme(m.from_user.id): return
    only = None
    if len(m.command) > 1 and m.command[1].isdigit():
        only = int(m.command[1])
    status = await m.reply("♻️ ɢʀᴀᴄᴇꜰᴜʟʟʏ ʀᴇꜱᴛᴀʀᴛɪɴɢ ᴄʟᴏɴᴇꜱ...")
    await restart_all(status, only)

# ═════════════════════ ᴄᴀʟʟʙᴀᴄᴋ ʜᴀɴᴅʟᴇʀꜱ ═════════════════════
async def cb_upload(c, q, parts):
    uid = q.from_user.id
    act = parts[1]
    if act == "ep":
        if not await perm_ok(c, uid, "upload"):
            await q_safe(q, "❌ ɴᴏ ᴜᴘʟᴏᴀᴅ ᴘᴇʀᴍ!"); return
        s = get_sess(c, uid) or {"step": "up_video", "data": {"added": 0}}
        s["step"] = "up_video"; SESSIONS[(c.bot_id, uid)] = s
        await q_safe(q, "📤 ᴠɪᴅᴇᴏ ꜱᴇɴᴅ ᴋᴀʀᴏ")
        try: await q.message.edit_text("📤 <b>ᴠɪᴅᴇᴏ ꜱᴇɴᴅ ᴋᴀʀᴏ</b> (ᴄᴀᴘᴛɪᴏɴ ᴏᴘᴛɪᴏɴᴀʟ):\n\n❌ /ᴄᴀɴᴄᴇʟ", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "ns":
        if not (await perm_ok(c, uid, "seasons") or await perm_ok(c, uid, "upload")):
            await q_safe(q, "❌ ɴᴏ ꜱᴇᴀꜱᴏɴꜱ ᴘᴇʀᴍ!"); return
        set_sess(c, uid, "ns_season")
        await q_safe(q, "🆕 ꜱᴇᴀꜱᴏɴ ɴᴜᴍʙᴇʀ?")
        try: await q.message.edit_text("🆕 <b>ꜱᴇᴀꜱᴏɴ ɴᴜᴍʙᴇʀ ꜱᴇɴᴅ ᴋᴀʀᴏ</b> (ᴇx: 2):", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "done":
        s = get_sess(c, uid)
        n = s["data"].get("added", 0) if s else 0
        clear_sess(c, uid)
        await q_safe(q, f"🏁 ᴅᴏɴᴇ — {n} ᴇᴘꜱ!")
        try: await q.message.edit_text(f"🏁 <b>ᴜᴘʟᴏᴀᴅ ꜰɪɴɪꜱʜᴇᴅ!</b>\n\n✅ {n} ᴇᴘɪꜱᴏᴅᴇꜱ ᴀᴅᴅᴇᴅ", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "cancel":
        clear_sess(c, uid)
        await q_safe(q, "❌ ᴄᴀɴᴄᴇʟʟᴇᴅ")
        try: await q.message.edit_text("❌ <b>ᴜᴘʟᴏᴀᴅ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>", parse_mode=PM_HTML)
        except RPCError: pass

async def cb_edit(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "edit"):
        await q_safe(q, "❌ ɴᴏ ᴇᴅɪᴛ ᴘᴇʀᴍ!"); return
    act, ref = parts[1], parts[2]
    s, e = map(int, ref.split(":"))
    ep = await c.store.get("episodes", ep_id(s, e))
    if not ep:
        await q_safe(q, "❌ ɴᴏᴛ ꜰᴏᴜɴᴅ!"); return
    if act == "video":
        set_sess(c, uid, "ed_video", s=s, e=e)
        await q_safe(q, "🎬 ɴᴇᴡ ᴠɪᴅᴇᴏ ꜱᴇɴᴅ ᴋᴀʀᴏ")
        try: await q.message.edit_text(f"🎬 <b>ꜱ{s} ᴇ{e} — ɴᴇᴡ ᴠɪᴅᴇᴏ ꜱᴇɴᴅ ᴋᴀʀᴏ:</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "cap":
        if not await perm_ok(c, uid, "captions"):
            await q_safe(q, "❌ ɴᴏ ᴄᴀᴘᴛɪᴏɴꜱ ᴘᴇʀᴍ!"); return
        set_sess(c, uid, "ed_cap", s=s, e=e)
        await q_safe(q, "✏️ ɴᴇᴡ ᴄᴀᴘᴛɪᴏɴ ꜱᴇɴᴅ ᴋᴀʀᴏ")
        try: await q.message.edit_text(f"✏️ <b>ꜱ{s} ᴇ{e} — ɴᴇᴡ ᴄᴀᴘᴛɪᴏɴ ᴛᴇxᴛ ꜱᴇɴᴅ ᴋᴀʀᴏ:</b>\n\nᴠᴀʀꜱ: {{season}} {{episode}} {{botname}}", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "thumb":
        if not await perm_ok(c, uid, "thumb"):
            await q_safe(q, "❌ ɴᴏ ᴛʜᴜᴍʙ ᴘᴇʀᴍ!"); return
        set_sess(c, uid, "ed_thumb", s=s, e=e)
        await q_safe(q, "🖼️ ᴛʜᴜᴍʙ ꜱᴇɴᴅ ᴋᴀʀᴏ")
        try: await q.message.edit_text(f"🖼️ <b>ꜱ{s} ᴇ{e} — ᴛʜᴜᴍʙ ᴘʜᴏᴛᴏ ꜱᴇɴᴅ ᴋᴀʀᴏ:</b>\n\n(ᴏʀ ꜱᴇɴᴅ 'remove' ᴛᴏ ᴄʟᴇᴀʀ)", parse_mode=PM_HTML)
        except RPCError: pass

async def ed_apply(c, m, kind):
    uid = m.from_user.id
    s = get_sess(c, uid); d = s["data"]; sn, en = d["s"], d["e"]
    ep = await c.store.get("episodes", ep_id(sn, en))
    if not ep:
        clear_sess(c, uid); await m.reply("❌ ɴᴏᴛ ꜰᴏᴜɴᴅ!"); return
    if kind == "video":
        mtype, fid, tid = get_media(m)
        if not fid:
            await m.reply("🎬 <b>ᴠɪᴅᴇᴏ ꜱᴇɴᴅ ᴋᴀʀᴏ!</b>", parse_mode=PM_HTML); return
        upd = {"file_id": fid, "type": mtype, "updated_at": now()}
        if tid: upd["thumb_id"] = tid; upd["thumb_path"] = None
        await c.store.update("episodes", ep_id(sn, en), **upd)
        await log_event(c, "✏️ ᴇᴘɪꜱᴏᴅᴇ ᴇᴅɪᴛᴇᴅ", f"ꜱ{sn} ᴇ{en} — ᴠɪᴅᴇᴏ ʀᴇᴘʟᴀᴄᴇᴅ", important=True, uid=uid)
    elif kind == "cap":
        await c.store.update("episodes", ep_id(sn, en), caption=m.text or "", updated_at=now())
        await log_event(c, "✏️ ᴇᴘɪꜱᴏᴅᴇ ᴇᴅɪᴛᴇᴅ", f"ꜱ{sn} ᴇ{en} — ᴄᴀᴘᴛɪᴏɴ", important=True, uid=uid)
    elif kind == "thumb":
        if (m.text or "").strip().lower() == "remove":
            await c.store.update("episodes", ep_id(sn, en), thumb_id=None, thumb_path=None, updated_at=now())
        else:
            tid = m.photo.file_id if m.photo else (m.video.thumbs[0].file_id if m.video and m.video.thumbs else None)
            if not tid:
                await m.reply("🖼️ ᴘʜᴏᴛᴏ ꜱᴇɴᴅ ᴋᴀʀᴏ!", parse_mode=PM_HTML); return
            path = os.path.join(THUMB_DIR, f"{c.bot_id}_{sn}_{en}.jpg")
            try: await c.download_media(tid, file_name=path)
            except RPCError: path = None
            await c.store.update("episodes", ep_id(sn, en), thumb_id=tid, thumb_path=path, updated_at=now())
        await log_event(c, "✏️ ᴇᴘɪꜱᴏᴅᴇ ᴇᴅɪᴛᴇᴅ", f"ꜱ{sn} ᴇ{en} — ᴛʜᴜᴍʙ", important=True, uid=uid)
    clear_sess(c, uid)
    await m.reply(f"✅ <b>ᴜᴘᴅᴀᴛᴇᴅ — ꜱ{ꜱ}" .replace("ꜱ", "S") if False else f"✅ <b>ᴜᴘᴅᴀᴛᴇᴅ — ꜱ{sn} ᴇ{en}</b>\n\n⚡ ɪɴꜱᴛᴀɴᴛʟʏ ᴇꜰꜰᴇᴄᴛɪᴠᴇ!",
                  parse_mode=PM_HTML)
    await show_editor(c, m.chat.id, sn, en)

async def cb_panel(c, q, parts):
    uid = q.from_user.id
    act = parts[1]
    checks = {"upload": "upload", "edit": "edit", "del": "delete", "bc": "broadcast",
              "stats": "stats", "list": "list", "fs": "forcesub", "es": "editstart"}
    if act in checks and not await perm_ok(c, uid, checks[act]):
        await q_safe(q, f"❌ ɴᴏ {checks[act]} ᴘᴇʀᴍ!"); return
    if act == "upload":
        await q_safe(q, "⬆️"); set_sess(c, uid, "up_menu")
        await show_upload_menu(c, None, edit_msg=q.message)
    elif act == "edit":
        await q_safe(q, "✏️"); set_sess(c, uid, "ed_ref")
        try: await q.message.edit_text("✏️ <b>ᴇᴘɪꜱᴏᴅᴇ ʀᴇꜰᴇʀᴇɴᴄᴇ ꜱᴇɴᴅ ᴋᴀʀᴏ:</b>\n▸ S1 E4", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "del":
        await q_safe(q, "🗑"); set_sess(c, uid, "del_ref")
        try: await q.message.edit_text("🗑️ <b>ᴅᴇʟᴇᴛᴇ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ ʀᴇꜰᴇʀᴇɴᴄᴇ ꜱᴇɴᴅ ᴋᴀʀᴏ:</b>\n▸ Season 1 Episode 4", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "bc":
        await q_safe(q, "📣")
        try: await q.message.edit_text("📣 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ:</b> ᴋɪꜱɪ ʙʜɪ ᴍᴇꜱꜱᴀɢᴇ ᴘᴇ /ʙʀᴏᴀᴅᴄᴀsᴛ ʀᴇᴘʟʏ ᴋᴀʀᴏ".replace("ꜱ", "s"), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "stats":
        await q_safe(q, "📊")
        await c.send_message(uid, build_bot_stats(c), parse_mode=PM_HTML)
    elif act == "list":
        await q_safe(q, "📋")
        await send_list_to(c, uid)
    elif act == "fs":
        await q_safe(q, "🔐"); await show_fs_panel(c, None, edit_msg=q.message)
    elif act == "es":
        await q_safe(q, "📝"); set_sess(c, uid, "es_media")
        try: await q.message.edit_text("📝 <b>ɴᴇᴡ ꜱᴛᴀʀᴛ ᴍꜱɢ ꜱᴇɴᴅ ᴋᴀʀᴏ</b> (ᴛᴇxᴛ/ᴘʜᴏᴛᴏ/ᴠɪᴅᴇᴏ)...", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "admins":
        await q_safe(q, "👥"); await show_admins_list(c, None, edit_msg=q.message)
    elif act == "refresh":
        await q_safe(q, "🔄")
        doc = await c.store.get("admins", uid)
        role = ROLE_NAME.get(doc["role"], doc["role"]) if doc else "👑 ꜱᴜᴘʀᴇᴍᴇ"
        try: await q.message.edit_text(ADMIN_PANEL_TXT.format(uname=c.username, role=role),
                                       reply_markup=admin_panel_kb(), parse_mode=PM_HTML)
        except RPCError: pass

async def send_list_to(c, chat_id):
    seasons = {}
    for k, v in c.store.c("episodes").items():
        seasons.setdefault(v["season"], []).append(v["episode"])
    if not seasons:
        await c.send_message(chat_id, "📭 ɴᴏ ᴇᴘɪꜱᴏᴅᴇꜱ ʏᴇᴛ."); return
    text = "📺 <b>ᴇᴘɪꜱᴏᴅᴇ ʟɪꜱᴛ</b>\n━━━━━━━━━━━━━━\n"
    for s in sorted(seasons):
        text += f"\n🟣 <b>ꜱᴇᴀꜱᴏɴ {s}</b>\n"
        for e in sorted(seasons[s]):
            text += f"   ▸ ᴇᴘɪꜱᴏᴅᴇ {e}\n"
    for part in chunk(text):
        try: await c.send_message(chat_id, part, parse_mode=PM_HTML, disable_web_page_preview=True)
        except RPCError: pass
        await asyncio.sleep(0.3)

async def cb_fs(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "forcesub"):
        await q_safe(q, "❌ ɴᴏ ꜰꜱ ᴘᴇʀᴍ!"); return
    act = parts[1]
    if act == "off":
        await set_cfg(c.store, fs_mode="off")
        await log_event(c, "🔐 ꜰᴏʀᴄᴇ-ꜱᴜʙ ᴄʜᴀɴɢᴇᴅ", "ᴏꜰꜰ", important=True)
        await q_safe(q, "🔴 ꜰꜱ ᴏꜰꜰ!")
        await show_fs_panel(c, None, edit_msg=q.message)
    elif act in ("public", "private", "logch"):
        step = {"public": "fs_public", "private": "fs_private", "logch": "fs_logch"}[act]
        set_sess(c, uid, step)
        prompts = {"public": "🟢 <b>ᴘᴜʙʟɪᴄ ᴄʜᴀɴɴᴇʟ</b> ᴋᴀ @ᴜꜱᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ ꜱᴇɴᴅ ᴋᴀʀᴏ:\n(ʙᴏᴛ ᴀᴅᴍɪɴ ʜᴏɴᴀ ᴄʜᴀʜɪʏᴇ)",
                   "private": "🔵 <b>ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀɴɴᴇʟ</b> ᴋᴀ @ᴜꜱᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ ꜱᴇɴᴅ ᴋᴀʀᴏ:\n(ʙᴏᴛ ᴀᴅᴍɪɴ + ɪɴᴠɪᴛᴇ ᴘᴇʀᴍ)",
                   "logch": "🧾 <b>ʟᴏɢ ᴄʜᴀɴɴᴇʟ</b> ᴋᴀ @ᴜꜱᴇʀɴᴀᴍᴇ ᴏʀ ɪᴅ ꜱᴇɴᴅ ᴋᴀʀᴏ:"}
        await q_safe(q, act)
        try: await q.message.edit_text(prompts[act], parse_mode=PM_HTML)
        except RPCError: pass

async def cb_adm(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "manage_admins"):
        await q_safe(q, "❌ ɴᴏ ᴍᴀɴᴀɢᴇ-ᴀᴅᴍɪɴꜱ ᴘᴇʀᴍ!"); return
    action = parts[1]; tuid = int(parts[2])
    tgt = await c.store.get("admins", tuid)
    if tgt and tgt.get("role") == "owner" and action in ("t", "role", "rem"):
        await q_safe(q, "👑 ᴄʟᴏɴᴇ ᴏᴡɴᴇʀ ᴘʀᴏᴛᴇᴄᴛᴇᴅ!", True); return
    sess = get_sess(c, uid)
    if sess and sess.get("step") == "adm_edit" and sess["data"].get("uid") == tuid:
        d = sess["data"]
    else:
        d = {"uid": tuid, "name": (tgt or {}).get("name", "ᴜꜱᴇʀ"),
             "perms": list((tgt or {}).get("permissions", [])),
             "role": (tgt or {}).get("role", "custom"), "new": tgt is None}
    if action == "t":
        perm = parts[3]
        if perm in d["perms"]: d["perms"].remove(perm)
        else: d["perms"].append(perm)
        SESSIONS[(c.bot_id, uid)] = {"step": "adm_edit", "data": d}
        await q_safe(q, "✅ ᴛᴏɢɢʟᴇᴅ — 💾 ꜱᴀᴠᴇ ʙʜɪ ᴋᴀʀᴏ!")
        try: await q.message.edit_text(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)
        except RPCError: pass
    elif action == "role":
        role = parts[3]
        d["role"] = role; d["perms"] = list(ROLE_PRESETS.get(role, []))
        SESSIONS[(c.bot_id, uid)] = {"step": "adm_edit", "data": d}
        await q_safe(q, f"🎨 {ROLE_NAME.get(role, role)} ᴘʀᴇꜱᴇᴛ!")
        try: await q.message.edit_text(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)
        except RPCError: pass
    elif action == "save":
        was_new = tgt is None
        await c.store.put("admins", tuid, {"_id": str(tuid), "name": d.get("name", "ᴜꜱᴇʀ"), "role": d["role"],
                                           "permissions": d["perms"], "added_by": uid, "at": now()})
        await apply_admin_commands(c, tuid)
        SESSIONS.pop((c.bot_id, uid), None)
        await q_safe(q, "💾 ꜱᴀᴠᴇᴅ! ᴅʙ ᴜᴘᴅᴀᴛᴇᴅ ✅")
        await log_event(c, "🛡️ ᴀᴅᴍɪɴ ᴀᴅᴅᴇᴅ" if was_new else "🔐 ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴇᴅɪᴛᴇᴅ",
                        f"ᴀᴅᴍɪɴ: {tuid} | ʀᴏʟᴇ: {d['role']} | ᴘᴇʀᴍꜱ: {','.join(d['perms']) or '—'}",
                        important=True, uid=tuid)
        d["new"] = False
        try: await q.message.edit_text(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)
        except RPCError: pass
    elif action == "rem":
        await c.store.delete("admins", tuid)
        SESSIONS.pop((c.bot_id, uid), None)
        await q_safe(q, "🗑 ʀᴇᴍᴏᴠᴇᴅ!")
        await log_event(c, "🚫 ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ", f"ᴀᴅᴍɪɴ: {tuid}", important=True, uid=tuid)
        try: await q.message.edit_text("🗑 <b>ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ.</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif action == "view":
        if not tgt:
            await q_safe(q, "❌ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ!"); return
        SESSIONS[(c.bot_id, uid)] = {"step": "adm_edit", "data": d}
        await q_safe(q, "👁")
        try: await q.message.edit_text(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)
        except RPCError: pass

async def cb_supreme(c, q, parts):
    if not is_supreme(q.from_user.id):
        await q_safe(q, "❌ ꜱᴜᴘʀᴇᴍᴇ ᴏɴʟʏ!"); return
    act = parts[1]
    if act == "botlist":
        await q_safe(q, "🤖")
        for part in chunk(build_botlist_text()):
            try: await q.message.reply(part, parse_mode=PM_HTML, disable_web_page_preview=True)
            except RPCError: pass
    elif act == "db":
        await q_safe(q, "🗄️")
        try: await q.message.reply(build_db_report(), parse_mode=PM_HTML, disable_web_page_preview=True)
        except RPCError: pass
    elif act == "stats":
        await q_safe(q, "📊")
        try: await q.message.reply(build_global_stats(), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "restart":
        await q_safe(q, "♻️ ʀᴇꜱᴛᴀʀᴛɪɴɢ...")
        await restart_all(q.message)

# ─────────── ᴍᴀꜱᴛᴇʀ ᴄᴀʟʟʙᴀᴄᴋ ───────────
async def h_callback(c, q):
    try:
        if not q.from_user: 
            try: await q.answer()
            except RPCError: pass
            return
        uid = q.from_user.id
        data = q.data or ""
        if data == "ckfs":
            ok, kb = await fs_state(c, uid)
            if ok:
                await q_safe(q, "✅ ᴠᴇʀɪꜰɪᴇᴅ!")
                user = await c.store.get("users", uid) or await ensure_user(c, q.from_user)
                await convert_referral(c, uid)
                try: await q.message.delete()
                except RPCError: pass
                await send_start_content(c, uid, user)
            else:
                await unauthorized(c, uid)
                await q_safe(q, "❌ ꜱᴛɪʟʟ ɴᴏᴛ ᴠᴇʀɪꜰɪᴇᴅ — ᴊᴏɪɴ ꜰɪʀꜱᴛ!")
        elif data.startswith("next|"):
            await q_safe(q, "▶️ ʟᴏᴀᴅɪɴɢ...")
            s, e = map(int, data.split("|")[1].split(":"))
            user = await c.store.get("users", uid)
            found = await send_episode(c, uid, s, e + 1, user)
            if not found:
                if await c.store.get("episodes", ep_id(s + 1, 1)):
                    try: await c.send_message(uid, f"🎉 <b>ꜱᴇᴀꜱᴏɴ {s} ꜰɪɴɪꜱʜᴇᴅ!</b>\n\n▶️ ꜱᴛᴀʀᴛɪɴɢ ꜱᴇᴀꜱᴏɴ {s + 1}...", parse_mode=PM_HTML)
                    except RPCError: pass
                    await send_episode(c, uid, s + 1, 1, user)
                else:
                    try: await c.send_message(uid, COMING_SOON, parse_mode=PM_HTML)
                    except RPCError: pass
        elif data.startswith("sea|"):
            await q_safe(q, "📚")
            sn = int(data.split("|")[1])
            eps = sorted(int(k.split(":")[1]) for k in c.store.c("episodes") if k.startswith(f"{sn}:"))
            if eps:
                txt = (f"📚 <b>ꜱᴇᴀꜱᴏɴ {sn}</b>\n\n" + "  ".join(f"ᴇ{x}" for x in eps) +
                       f"\n\n▶️ ꜱᴇɴᴅ ʟɪᴋᴇ: <code>S{sn} E{eps[0]}</code>")
                try: await q.message.reply(txt, parse_mode=PM_HTML)
                except RPCError: pass
        elif data == "fmt":
            await q_safe(q, "🔍")
            try: await q.message.reply(INVALID_FMT, parse_mode=PM_HTML)
            except RPCError: pass
        elif data == "rf|menu":
            await q_safe(q, "🎁"); await send_refer(c, uid, uid)
        elif data == "rf|link":
            link = f"https://t.me/{c.username}?start=ref_{uid}"
            await q_safe(q, "🔗 ʟɪɴᴋ ʙʜᴇᴊ ᴅɪʏᴀ!")
            try: await c.send_message(uid, f"🔗 <code>{link}</code>", parse_mode=PM_HTML, disable_web_page_preview=True)
            except RPCError: pass
        elif data == "rf|stats":
            await q_safe(q, "🏆")
            try: await q.message.reply(ranking_text(c.store), parse_mode=PM_HTML)
            except RPCError: pass
        elif data == "cloneme":
            if not c.is_factory: return
            set_sess(c, uid, "clone_token")
            await q_safe(q, "🤖 ᴛᴏᴋᴇɴ ꜱᴇɴᴅ ᴋᴀʀᴏ")
            try: await q.message.reply(CLONE_PROMPT, parse_mode=PM_HTML, disable_web_page_preview=True,
                                       reply_markup=InlineKeyboardMarkup([[btn("🔴 ᴄᴀɴᴄᴇʟ", "cl|cancel")]]))
            except RPCError: pass
        elif data == "cl|cancel":
            clear_sess(c, uid)
            await q_safe(q, "❌ ᴄᴀɴᴄᴇʟʟᴇᴅ")
            try: await q.message.edit_text("❌ <b>ᴄʟᴏɴᴇ ᴄᴀɴᴄᴇʟʟᴇᴅ.</b>", parse_mode=PM_HTML)
            except RPCError: pass
        elif data.startswith("up|"):
            await cb_upload(c, q, data.split("|"))
        elif data.startswith("ed|"):
            await cb_edit(c, q, data.split("|"))
        elif data.startswith("pan|"):
            await cb_panel(c, q, data.split("|"))
        elif data.startswith("fs|"):
            await cb_fs(c, q, data.split("|"))
        elif data.startswith("adm|"):
            await cb_adm(c, q, data.split("|"))
        elif data.startswith("sv|"):
            await cb_supreme(c, q, data.split("|"))
        else:
            try: await q.answer()
            except RPCError: pass
    except FloodWait as f:
        await asyncio.sleep(f.value)
    except Exception as e:
        LOG.exception("ᴄᴀʟʟʙᴀᴄᴋ ᴇʀʀᴏʀ")
        await dev_log(f"⚠️ ᴄᴀʟʟʙᴀᴄᴋ ᴇʀʀᴏʀ @{c.username}: {e!r}")

# ═════════════════════ ɢᴇɴᴇʀɪᴄ ᴍꜱɢ (ꜱᴇꜱꜱɪᴏɴꜱ + ᴇᴘɪꜱᴏᴅᴇꜱ) ═════════════════════
async def route_session(c, m, s):
    uid = m.from_user.id
    step = s.get("step")
    if step == "clone_token":
        await clone_token(c, m)
    elif step == "up_video":
        await up_got_video(c, m)
    elif step == "up_ref" and m.text:
        await up_got_ref(c, m)
    elif step == "ns_season" and m.text:
        await ns_got_season(c, m)
    elif step == "ns_video":
        await ns_got_video(c, m)
    elif step == "ed_ref" and m.text:
        await ed_got_ref(c, m)
    elif step == "ed_video":
        await ed_apply(c, m, "video")
    elif step == "ed_cap" and m.text:
        await ed_apply(c, m, "cap")
    elif step == "ed_thumb":
        await ed_apply(c, m, "thumb")
    elif step == "del_ref" and m.text:
        pe = parse_episode(m.text)
        if not pe:
            await m.reply(INVALID_FMT, parse_mode=PM_HTML); return
        clear_sess(c, uid)
        await do_delete(c, m.chat.id, *pe)
    elif step == "es_media":
        await es_got(c, m)
    elif step == "fs_public" and m.text:
        await fs_got_channel(c, m, "public")
    elif step == "fs_private" and m.text:
        await fs_got_channel(c, m, "private")
    elif step == "fs_logch" and m.text:
        await fs_got_logch(c, m)
    elif step == "ga_target" and m.text:
        t, name = msg_target(m)
        if not t and (m.text or "").strip().isdigit():
            t = int(m.text.strip()); name = str(t)
        if not t:
            await m.reply("👤 ɪᴅ ꜱᴇɴᴅ ᴋᴀʀᴏ ᴏʀ ʀᴇᴘʟʏ ᴋᴀʀᴏ:"); return
        clear_sess(c, uid)
        await open_selector(c, m, t, name)
    elif step == "ea_target" and m.text:
        t, name = msg_target(m)
        if not t and (m.text or "").strip().isdigit():
            t = int(m.text.strip()); name = str(t)
        if not t:
            await m.reply("❌ ɪᴅ ꜱᴇɴᴅ ᴋᴀʀᴏ:"); return
        clear_sess(c, uid)
        await open_selector(c, m, t, name, must_exist=True)
    elif step == "ra_target" and m.text:
        t, _ = msg_target(m)
        if not t and (m.text or "").strip().isdigit():
            t = int(m.text.strip())
        if not t:
            await m.reply("❌ ɪᴅ ꜱᴇɴᴅ ᴋᴀʀᴏ:"); return
        clear_sess(c, uid)
        tgt = await c.store.get("admins", t)
        if not tgt: await m.reply("❌ ɴᴏᴛ ᴀɴ ᴀᴅᴍɪɴ."); return
        if tgt.get("role") == "owner": await m.reply("👑 ᴏᴡɴᴇʀ ᴄᴀɴ'ᴛ ʙᴇ ʀᴇᴍᴏᴠᴇᴅ!"); return
        await c.store.delete("admins", t)
        await log_event(c, "🚫 ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ", f"ᴀᴅᴍɪɴ: {t}", important=True, uid=t)
        await m.reply("🗑 <b>ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ!</b>", parse_mode=PM_HTML)

async def h_generic(c, m):
    try:
        if not m.from_user: return
        uid = m.from_user.id
        s = get_sess(c, uid)
        if s:
            await route_session(c, m, s); return
        if m.text and not m.text.startswith("/"):
            await episode_request(c, m)
    except FloodWait as f:
        await asyncio.sleep(f.value)
    except Exception as e:
        LOG.exception("ɢᴇɴᴇʀɪᴄ ᴇʀʀᴏʀ")
        await dev_log(f"⚠️ ᴇʀʀᴏʀ @{c.username}: {e!r}")

# ═════════════════════ ᴄᴏᴍᴍᴀɴᴅ ᴅɪꜱᴘᴀᴛᴄʜᴇʀ ═════════════════════
CMD_MAP = {
    "upload": cmd_upload, "edit": cmd_edit, "delete": cmd_delete, "broadcast": cmd_broadcast,
    "stats": cmd_stats, "list": cmd_list, "admin": cmd_admin, "setfs": cmd_setfs,
    "editstart": cmd_editstart, "giveadmin": cmd_giveadmin, "editadmin": cmd_editadmin,
    "remadmin": cmd_remadmin, "done": cmd_done, "cancel": cmd_cancel,
    "clone": cmd_clone, "supreme": cmd_supreme, "botlist": cmd_botlist,
    "db": cmd_db, "restart": cmd_restart,
}

async def h_admin_cmds(c, m):
    try:
        name = m.command[0].lstrip("/").lower()
        if name in FACTORY_ONLY and not c.is_factory:
            return
        fn = CMD_MAP.get(name)
        if fn:
            await fn(c, m)
    except FloodWait as f:
        await asyncio.sleep(f.value)
    except Exception as e:
        LOG.exception("ᴄᴍᴅ ᴇʀʀᴏʀ %s", name if 'name' in dir() else '?')
        await dev_log(f"⚠️ ᴄᴏᴍᴍᴀɴᴅ ᴇʀʀᴏʀ @{c.username}: {e!r}")
        try: await m.reply("⚠️ ᴇʀʀᴏʀ — ᴛʀʏ ᴀɢᴀɪɴ.")
        except RPCError: pass

async def h_join_request(c, update, users, chats):
    try:
        req = getattr(update, "bot_chat_join_request", None)
        if not req: return
        st = cfg(c.store)
        if st.get("fs_mode") != "private" or req.chat_id != st.get("fs_channel"):
            return
        uid = req.user_id
        u = await c.store.get("users", uid)
        if not u:
            u = {"_id": str(uid), "first_name": "ᴜꜱᴇʀ", "username": "", "started_at": now(),
                 "last_seen": now(), "fs_verified": True}
            await c.store.put("users", uid, u)
        await c.store.update("users", uid, fs_verified=True, fs_request=True)
        ap = getattr(c, "approve_chat_join_request", None)
        if ap:
            try: await ap(req.chat_id, uid)
            except RPCError: pass
        await convert_referral(c, uid)
        await log_event(c, "✅ ꜰꜱ ʀᴇQᴜᴇꜱᴛ ᴀᴘᴘʀᴏᴠᴇᴅ", f"ᴜꜱᴇʀ: {uid}", uid=uid)
        try:
            await c.send_message(uid, "✅ <b>ᴀᴄᴄᴇꜱꜱ ᴀᴘᴘʀᴏᴠᴇᴅ!</b>\n\n▶️ ᴀʙ ꜱᴇɴᴅ ᴋᴀʀᴏ: S1 E1", parse_mode=PM_HTML)
        except RPCError:
            pass
    except Exception as e:
        LOG.exception("ᴊᴏɪɴ ʀᴇQᴜᴇꜱᴛ ᴇʀʀᴏʀ")
        await dev_log(f"⚠️ ᴊᴏɪɴ ʀᴇQᴜᴇꜱᴛ ᴇʀʀᴏʀ: {e!r}")

# ═════════════════════ ʀᴇɢɪꜱᴛʀᴀᴛɪᴏɴ ═════════════════════
F_START = filters.command("start") & filters.private & filters.incoming
F_REFER = filters.command("refer") & filters.private & filters.incoming
F_CMD = filters.command(ALL_CMDS) & filters.private & filters.incoming
F_GEN = filters.private & filters.incoming & ~filters.command(ALL_CMDS) & ~filters.service

def register_provider_handlers(c, is_factory):
    c.add_handler(MessageHandler(h_start := cmd_start, F_START), 0)
    c.add_handler(MessageHandler(cmd_refer, F_REFER), 0)
    c.add_handler(MessageHandler(h_admin_cmds, F_CMD), 0)
    c.add_handler(CallbackQueryHandler(h_callback), 0)
    c.add_handler(MessageHandler(h_generic, F_GEN), 1)
    c.add_handler(RawUpdateHandler(h_join_request), -1)

def attach(c, me, store, is_factory):
    c.bot_id = me.id
    c.username = me.username or f"bot{me.id}"
    c.is_factory = is_factory
    c.store = store

async def launch_clone(meta):
    bid = meta["_id"]
    try:
        token = dec_token(meta["token_enc"])
    except Exception as e:
        LOG.error("ᴛᴏᴋᴇɴ ᴅᴇᴄʀʏᴘᴛ ꜰᴀɪʟ %s: %s", bid, e)
        return None
    c = Client(name=f"clone_{bid}", api_id=API_ID, api_hash=API_HASH, bot_token=token,
               in_memory=True, sleep_threshold=15)
    try:
        await c.start()
    except (AccessTokenInvalid, AccessTokenExpired):
        LOG.error("ᴄʟᴏɴᴇ %s ᴛᴏᴋᴇɴ ɪɴᴠᴀʟɪᴅ", bid)
        return None
    except Exception as e:
        LOG.error("ᴄʟᴏɴᴇ %s ꜱᴛᴀʀᴛ ꜰᴀɪʟ: %s", bid, e)
        return None
    me = await c.get_me()
    store = get_store(bid)
    await ensure_defaults(store)
    attach(c, me, store, is_factory=False)
    register_provider_handlers(c, is_factory=False)
    await apply_commands(c)
    RUNNING[bid] = c
    if FACTORY:
        await FACTORY.update("bots", bid, last_active=now(), username=me.username or meta.get("username", str(bid)))
    LOG.info("🟢 ᴄʟᴏɴᴇ ʟɪᴠᴇ: @%s (%s)", me.username, bid)
    return c

# ═════════════════════ ᴀᴜᴛᴏ-ᴄʟᴇᴀɴᴜᴘ ═════════════════════
async def run_cleanup():
    t = now()
    for meta in list(FACTORY.find("bots")):
        bid = meta["_id"]
        st = STORES.get(bid)
        if st is None:
            if not os.path.exists(clone_path(bid)): continue
            st = Store(clone_path(bid)); STORES[bid] = st
        users = st.count("users"); eps = st.count("episodes")
        inactive_days = (t - meta.get("last_active", meta.get("created_at", t))) / 86400
        if eps == 0 and users < CLONE_MIN_USERS and inactive_days >= CLONE_INACTIVE_DAYS:
            LOG.info("🗑 ᴄʟᴇᴀɴᴜᴘ: @%s (%s)", meta.get("username"), bid)
            old = RUNNING.pop(bid, None)
            if old:
                try: await old.stop()
                except Exception: pass
            STORES.pop(bid, None)
            try: os.remove(st.path)
            except OSError: pass
            await FACTORY.delete("bots", bid)
            await dev_log(f"🗑️ ᴄʟᴏɴᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ: @{meta.get('username')} ({bid})\n"
                          f"ᴜꜱᴇʀꜱ: {users} | ᴇᴘꜱ: 0 | ɪɴᴀᴄᴛɪᴠᴇ: {inactive_days:.1f}ᴅ")

async def cleanup_loop():
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        try:
            await run_cleanup()
            for st in STORES.values():
                if st._dirty: await st.flush()
        except Exception as e:
            LOG.exception("ᴄʟᴇᴀɴᴜᴘ ᴇʀʀᴏʀ")
            await dev_log(f"⚠️ ᴄʟᴇᴀɴᴜᴘ ᴇʀʀᴏʀ: {e!r}")

# ═════════════════════ ᴍᴀɪɴ ═════════════════════
async def main():
    global FACTORY, FACTORY_CLIENT
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)

    if not (API_ID and API_HASH and BOT_TOKEN):
        print("❌ ᴄᴏɴꜰɪɢ ɪɴᴄᴏᴍᴘʟᴇᴛᴇ! app.py ᴋᴇ ᴛᴏᴘ ᴘᴇ API_ID / API_HASH / BOT_TOKEN ʙʜᴀʀᴏ.")
        return

    FACTORY = Store(os.path.join(DB_DIR, "factory.json"))
    for col in _COLLECTIONS + ["bots", "developer_logs"]:
        FACTORY.c(col)  # ᴇɴꜱᴜʀᴇ ᴄᴏʟʟᴇᴄᴛɪᴏɴꜱ + ᴋᴇʏᴇᴅ ɪɴᴅᴇxᴇꜱ
    await ensure_defaults(FACTORY)
    if SUPREMES:
        await set_cfg(FACTORY, owner_id=SUPREMES[0])
    LOG.info("🗄️ ꜰᴀᴄᴛᴏʀʏ ᴅʙ ʀᴇᴀᴅʏ — %s", FACTORY.path)

    fc = Client("factory", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,
                in_memory=True, sleep_threshold=15)
    await fc.start()
    me = await fc.get_me()
    attach(fc, me, FACTORY, is_factory=True)
    FACTORY_CLIENT = fc
    RUNNING[me.id] = fc
    register_provider_handlers(fc, is_factory=True)
    await apply_commands(fc)
    LOG.info("🟢 ꜰᴀᴄᴛᴏʀʏ ʟɪᴠᴇ: @%s (%s)", me.username, me.id)
    await dev_log(f"🚀 ꜰᴀᴄᴛᴏʀʏ ꜱᴛᴀʀᴛᴇᴅ: @{me.username} ({me.id})\n🤖 ᴄʟᴏɴᴇꜱ ʀᴇꜱᴛᴏʀᴇᴅ...")

    okc = fail = 0
    for meta in list(FACTORY.find("bots")):
        cl = await launch_clone(meta)
        if cl: okc += 1
        else: fail += 1
    LOG.info("♻️ ʀᴇꜱᴛᴏʀᴇᴅ ᴄʟᴏɴᴇꜱ — ✅%d ❌%d", okc, fail)

    asyncio.create_task(cleanup_loop())

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try: loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError): pass

    print(f"\n{'═'*55}\n  🏭 {FACTORY_NAME} ɪꜱ ʟɪᴠᴇ — @'{me.username}'\n  🤖 ᴄʟᴏɴᴇꜱ: {len(FACTORY.c('bots'))} | ᴅʙ: JSON ({DB_DIR}/)\n{'═'*55}\n")
    await stop.wait()

    LOG.info("🛑 ꜱʜᴜᴛᴛɪɴɢ ᴅᴏᴡɴ...")
    await dev_log("🛑 ꜰᴀᴄᴛᴏʀʏ ꜱᴛᴏᴘᴘᴇᴅ ɢʀᴀᴄᴇꜰᴜʟʟʏ.")
    for c in list(RUNNING.values()):
        try: await c.stop()
        except Exception: pass
    for st in STORES.values():
        await st.flush()
    await FACTORY.flush()
    LOG.info("✅ ʙʏᴇ!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
