"""
╔══════════════════════════════════════════════════════════════════╗
║           ᴀɴɪᴍᴇ ʙᴏᴛ ꜰᴀᴄᴛᴏʀʏ — ᴘʀᴏᴅᴜᴄᴛɪᴏɴ ʀᴇᴀᴅʏ               ║
║   ᴊꜱᴏɴ ᴅᴀᴛᴀʙᴀꜱᴇ • ᴇɴᴄʀʏᴘᴛᴇᴅ ᴛᴏᴋᴇɴꜱ • ᴀᴜᴛᴏ ᴄᴏᴍᴍᴀɴᴅꜱ           ║
╚══════════════════════════════════════════════════════════════════╝
"""
import asyncio, base64, hashlib, html, json, logging, os, re, secrets, signal, time
from urllib.parse import quote

from pyrogram import Client, filters, enums
from pyrogram.types import (Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup,
                            BotCommand, BotCommandScopeDefault, BotCommandScopeChat)
try:
    from pyrogram.types import LinkPreviewOptions
    LPO_DISABLE = LinkPreviewOptions(is_disabled=True)
except ImportError:
    LPO_DISABLE = None
from pyrogram.handlers import MessageHandler, CallbackQueryHandler, RawUpdateHandler
from pyrogram.errors import (FloodWait, RPCError, UserNotParticipant, AccessTokenInvalid,
                             AccessTokenExpired, UserIsBlocked, InputUserDeactivated,
                             PeerIdInvalid, ChatAdminRequired)

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
DEFAULT_SUPREME_ID: int = 7524032836
SUPREME_IDS: str = "7524032836"      # <-- ᴄᴏᴍᴍᴀ ꜱᴇᴘᴀʀᴀᴛᴇᴅ ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴜꜱᴇʀ ɪᴅꜱ (ᴇx: "12345,67890")
LOG_CHANNEL_ID: int = 0              # <-- ɢʟᴏʙᴀʟ ʟᴏɢ ᴄʜᴀɴɴᴇʟ ɪᴅ (0 = ᴏꜰꜰ)
FACTORY_NAME: str = "Anime Bot Factory"
CLONE_BOT_ID_TOKEN: str = ""         # <-- ᴏᴘᴛɪᴏɴᴀʟ ᴇxᴛʀᴀ ꜱᴇᴄʀᴇᴛ ꜰᴏʀ ᴛᴏᴋᴇɴ ᴇɴᴄʀʏᴘᴛɪᴏɴ
DB_DIR: str = "data"                 # ᴊꜱᴏɴ ᴅᴀᴛᴀʙᴀꜱᴇ ꜰᴏʟᴅᴇʀ
THUMB_DIR: str = "thumbs"            # ᴛʜᴜᴍʙɴᴀɪʟ ᴄᴀᴄʜᴇ ꜰᴏʟᴅᴇʀ
CLEANUP_INTERVAL: int = 3600         # ꜱᴇᴄᴏɴᴅꜱ — ᴀᴜᴛᴏ-ᴄʟᴇᴀɴᴜᴘ ᴄʜᴇᴄᴋ
CLONE_INACTIVE_DAYS: int = 3         # ɪɴᴀᴄᴛɪᴠᴇ ᴅᴀʏꜱ ʙᴇꜰᴏʀᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ
CLONE_MIN_USERS: int = 100           # ᴜꜱᴇʀꜱ >= ᴛʜɪꜱ = ɴᴇᴠᴇʀ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇ

# (ᴏᴘᴛɪᴏɴᴀʟ) ᴇɴᴠ ᴠᴀʀꜱ ᴏᴠᴇʀʀɪᴅᴇ — ᴄᴏᴅᴇ ᴠᴀʟᴜᴇꜱ ᴘʀɪᴏʀɪᴛʏ ᴡʜᴇɴ ꜱᴇᴛ
API_ID = int(os.getenv("API_ID") or API_ID or 0)
API_HASH = os.getenv("API_HASH") or API_HASH
BOT_TOKEN = os.getenv("BOT_TOKEN") or BOT_TOKEN
SUPREME_IDS = os.getenv("SUPREME_IDS") or SUPREME_IDS or "7524032836"
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID") or LOG_CHANNEL_ID or 0)
FACTORY_NAME = os.getenv("FACTORY_NAME") or FACTORY_NAME
CLONE_BOT_ID_TOKEN = os.getenv("CLONE_BOT_ID_TOKEN") or CLONE_BOT_ID_TOKEN

SUPREMES = {DEFAULT_SUPREME_ID} | {int(x) for x in SUPREME_IDS.replace(" ", "").split(",") if x.strip().isdigit()}

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

START_TS = None
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

def btn(text, cb): return InlineKeyboardButton(sc(text), callback_data=cb)
def ubtn(text, url): return InlineKeyboardButton(sc(text), url=url)

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
    "👋 <b>ʜᴇʟʟᴏ {name}!</b>\n\n"
    f"🎯 ɪ'ᴍ <b>{{botname}}</b> — ʏᴏᴜʀ ᴀɴɪᴍᴇ ᴘʀᴏᴠɪᴅᴇʀ ʙᴏᴛ.\n\n"
    "📺 <b> Tap below button to select anime and enjoy watching! ✨</b>")

DEFAULT_CAPTION = "🎬 <b>ꜱᴇᴀꜱᴏɴ {season} • ᴇᴘɪꜱᴏᴅᴇ {episode}</b>\n\n🤖 @{botname}"

COMING_SOON = ("🔔 <b>ᴄᴏᴍɪɴɢ ꜱᴏᴏɴ</b>\n\n"
               "New episodes are not uploaded yet.\nPlease check again later.")

INVALID_FMT = (
    "❌ <b>ɪɴᴠᴀʟɪᴅ ꜰᴏʀᴍᴀᴛ!</b>\n\n"
    "✅ <b>ᴛʀʏ ʟɪᴋᴇ ᴛʜɪꜱ:</b>\n"
    "━━━━━━━━━━━━━━\n"
    "▸ Season 1 Episode 4\n▸ S1 E4\n▸ s1e4\n▸ 1x4\n▸ Anime Keyword or Name")

CLONE_PROMPT = (
    "🤖 <b>ᴄʀᴇᴀᴛᴇ ʏᴏᴜʀ ᴏᴡɴ ᴀɴɪᴍᴇ ʙᴏᴛ</b>\n━━━━━━━━━━━━━━\n\n"
    "1️⃣ Open @BotFather\n"
    "2️⃣ /newbot → Set name & username\n"
    f"3️⃣ Copy token and send here\n\n"
    "🔐 <b>ꜱᴇᴄᴜʀɪᴛʏ:</b> Tokens are stored <u>ENCRYPTED</u> — never in plaintext.\n\n"
    "⏳ <b>ɴᴏᴡ ꜱᴇɴᴅ ʏᴏᴜʀ ʙᴏᴛ ᴛᴏᴋᴇɴ:</b>")

CLONE_SUCCESS = (
    "🎉 <b>ᴄʟᴏɴᴇ ᴄʀᴇᴀᴛᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!</b>\n━━━━━━━━━━━━━━\n\n"
    "🤖 ʙᴏᴛ: <b>@{uname}</b>\n"
    "🆔: <code>{bid}</code>\n"
    "👤 ᴏᴡɴᴇʀ: <b>{name}</b>\n\n"
    "✅ ʙᴏᴛ ꜱᴛᴀʀᴛᴇᴅ + ᴄᴏᴍᴍᴀɴᴅꜱ ᴀᴜᴛᴏ-ꜱᴇᴛ\n\n"
    "📌 <b>ɴᴇxᴛ ꜱᴛᴇᴘꜱ:</b>\n"
    "▸ /setfs — Force Subscribe\n"
    "▸ /editstart — Customize Start Msg\n"
    "▸ /upload — Add Anime Episodes\n\n"
    "🚀 ʏᴏᴜʀ ʙᴏᴛ ɪꜱ ʟɪᴠᴇ ɴᴏᴡ!")

ADMIN_PANEL_TXT = (
    "🛠 <b>ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ</b>\n━━━━━━━━━━━━━━\n"
    "🤖 ʙᴏᴛ: @{uname}\n"
    "👤 ʏᴏᴜ: <b>{role}</b>\n\n"
    "⬇️ ꜱᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ:")

# ═════════════════════ ᴘᴇʀᴍɪꜱꜱɪᴏɴꜱ & ʀᴏʟᴇꜱ ═════════════════════
PERMS = ["upload", "edit", "delete", "broadcast", "forcesub", "editstart", "stats",
         "manage_admins", "thumb", "captions", "seasons", "list", "restart_upload", "ban_users"]

PERM_LABELS = {
    "upload": "Upload Episodes", "edit": "Edit Episodes", "delete": "Delete Episodes",
    "broadcast": "Broadcast", "forcesub": "Force Subscribe", "editstart": "Edit Start Msg",
    "stats": "View Statistics", "manage_admins": "Manage Admins", "thumb": "Upload Thumbnail",
    "captions": "Manage Captions", "seasons": "Manage Seasons", "list": "Use /list",
    "restart_upload": "Restart Upload Session", "ban_users": "Ban/Unban Users",
}

ROLE_PRESETS = {
    "owner": list(PERMS),
    "manager": ["manage_admins", "broadcast", "upload", "edit", "delete", "stats",
                "forcesub", "editstart", "captions", "thumb", "seasons", "list", "restart_upload", "ban_users"],
    "uploader": ["upload", "edit", "seasons", "captions", "thumb", "list"],
    "broadcaster": ["broadcast"],
    "analyst": ["stats", "list"],
    "custom": [],
}
ROLE_NAME = {"owner": "👑 Owner", "manager": "🛠 Manager", "uploader": "⬆️ Uploader",
             "broadcaster": "📣 Broadcaster", "analyst": "📊 Analyst", "custom": "⚙️ Custom"}

# ═════════════════════ ᴄᴏᴍᴍᴀɴᴅ ꜱᴇᴛꜱ (ᴀᴜᴛᴏ-ꜱᴇᴛ ɪɴ ᴛᴇʟᴇɢʀᴀᴍ) ═════════════════════
USER_CMD_RAW = [("start", "Start Bot"), ("help", "Help & Commands"), ("refer", "Refer & Earn")]
ADMIN_CMD_RAW = [("upload", "Add Episodes"), ("edit", "Edit Episode"), ("delete", "Delete Episode"),
                 ("broadcast", "Send Updates"), ("stats", "Statistics"), ("list", "Episode List"),
                 ("listsearch", "Search Anime List"), ("admin", "Admin Panel"), ("setfs", "Force Subscribe"),
                 ("editstart", "Set Start Msg"), ("giveadmin", "Add Admin"), ("editadmin", "Edit Admin"),
                 ("remadmin", "Remove Admin"), ("ban", "Ban User"), ("unban", "Unban User"),
                 ("seasonend", "Mark Season Ended"), ("coming", "Mark Coming Soon"),
                 ("done", "Finish Upload"), ("cancel", "Cancel Session")]
FACTORY_CMD_RAW = [("clone", "Create Your Bot")]
SUPREME_CMD_RAW = [("supreme", "Supreme Panel"), ("botlist", "All Bots"), ("db", "Database"), ("restart", "Restart Clones")]

ALL_CMDS = ["start", "refer"] + [x[0] for x in ADMIN_CMD_RAW + FACTORY_CMD_RAW + SUPREME_CMD_RAW]
FACTORY_ONLY = {"clone", "supreme", "rajpapa", "botlist", "db", "restart"}

# ═════════════════════ ɢʟᴏʙᴀʟ ꜱᴛᴀᴛᴇ ═════════════════════
RUNNING = {}        # bot_id -> Client
STORES = {}         # bot_id -> Store
SESSIONS = {}       # (bot_id, uid) -> {"step":..., "data":{...}}
RATE = {}
LAST_UNAUTH = {}
ACTIVE_THRO = {}
FACTORY = None      # factory Store
FACTORY_CLIENT = None

_COLLECTIONS = ["users", "animes", "episodes", "admins", "settings", "referrals", "broadcast_logs", "activity"]

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
                LOG.error("DB Load Failed %s: %s", self.path, e)
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

def migrate_store_if_needed(store):
    eps = store.c("episodes")
    legacy_keys = [k for k in list(eps.keys()) if k.count(":") == 1 or "anime_id" not in eps[k]]
    if not legacy_keys:
        return
    animes = store.c("animes")
    if "default" not in animes:
        animes["default"] = {"_id": "default", "title": "Default Anime", "created_at": now(), "seasons": {}}
    for old_k in legacy_keys:
        doc = eps.pop(old_k)
        s = doc.get("season", 1)
        e = doc.get("episode", 1)
        doc["anime_id"] = "default"
        new_k = f"default:{s}:{e}"
        doc["_id"] = new_k
        eps[new_k] = doc
    store.flush_soon()

async def ensure_defaults(store):
    st = store.c("settings")
    if "cfg" not in st:
        st["cfg"] = {"fs_mode": "off", "fs_channel": 0, "fs_username": "", "fs_link": "",
                     "log_channel": 0, "caption": "", "owner_id": None, "created_at": now()}
        store.flush_soon()
    if "start" not in st:
        st["start"] = {"type": "text", "text": DEFAULT_START}
        store.flush_soon()
    migrate_store_if_needed(store)

# ═════════════════════ ᴛᴏᴋᴇɴ ᴇɴᴄʀʏᴘᴛɪᴏɴ (ɴᴏ ᴘʟᴀɪɴᴛᴇxᴛ!) ═════════════════════
_FER = None
def _fernet():
    from cryptography.fernet import Fernet
    secret = (str(API_HASH) + ":" + str(CLONE_BOT_ID_TOKEN or "anime-factory-v1")).encode()
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(secret).digest()))

def enc_token(t):
    global _FER
    _FER = _FER or _fernet()
    return _FER.encrypt(t.encode()).decode()

def dec_token(e):
    global _FER
    _FER = _FER or _fernet()
    return _FER.decrypt(e.encode()).decode()

# ═════════════════════ ᴇᴘɪꜱᴏᴅᴇ ᴘᴀʀꜱᴇʀ & ꜰʟᴇxɪʙʟᴇ ꜰɪʟᴛᴇʀ ═════════════════════
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

def flexible_search(episodes_dict, query):
    if not query or not query.strip():
        return []

    q_str = query.strip()

    # 1. Check exact sX eY match
    exact = parse_episode(q_str)
    if exact:
        s, e = exact
        eid = f"{s}:{e}"
        if eid in episodes_dict:
            return [episodes_dict[eid]]

    # 2. Extract partial filters from query
    q_lower = q_str.lower()

    # Check season filter (e.g. season 2, s2)
    m_season = re.search(r"\b(?:season|s)\s*(\d{1,3})\b", q_lower)
    target_season = int(m_season.group(1)) if m_season else None

    # Check episode filter (e.g. episode 4, ep 4, e4)
    m_ep = re.search(r"\b(?:episode|ep|e)\s*(\d{1,3})\b", q_lower)
    target_ep = int(m_ep.group(1)) if m_ep else None

    # Clean query text keywords
    clean_kw = q_lower
    clean_kw = re.sub(r"\b(?:season|s)\s*\d{1,3}\b", "", clean_kw)
    clean_kw = re.sub(r"\b(?:episode|ep|e)\s*\d{1,3}\b", "", clean_kw)
    clean_kw = re.sub(r"\b\d{1,3}\s*[x×]\s*\d{1,3}\b", "", clean_kw)
    keywords = [w for w in re.split(r"\s+", clean_kw.strip()) if len(w) > 1]

    results = []
    for eid, ep in episodes_dict.items():
        s = ep.get("season")
        e = ep.get("episode")
        caption = (ep.get("caption") or "").lower()

        if target_season is not None and s != target_season:
            continue

        if target_ep is not None and e != target_ep:
            continue

        if keywords:
            searchable = f"{caption} season {s} episode {e} s{s} e{e}"
            if not all(kw in searchable for kw in keywords):
                continue

        results.append(ep)

    results.sort(key=lambda x: (x.get("season", 0), x.get("episode", 0)))
    return results

def make_anime_id(title):
    clean = re.sub(r"[^a-zA-Z0-9]+", "_", title.strip().lower()).strip("_")
    return clean or f"anime_{now()}"

def ep_id(aid, s, e): return f"{aid}:{s}:{e}"

async def get_or_create_anime(store, title):
    title_clean = title.strip()
    for anime in store.find("animes"):
        if anime.get("title", "").strip().lower() == title_clean.lower():
            return anime
    aid = make_anime_id(title_clean)
    doc = {"_id": aid, "title": title_clean, "created_at": now(), "seasons": {}}
    await store.put("animes", aid, doc)
    return doc

def get_media(m):
    if m.video:
        return "video", m.video.file_id, (m.video.thumbs[0].file_id if m.video.thumbs else None)
    if m.animation:
        return "animation", m.animation.file_id, (m.animation.thumbs[0].file_id if m.animation.thumbs else None)
    if m.document:
        return "document", m.document.file_id, (m.document.thumbs[0].file_id if m.document.thumbs else None)
    return None, None, None

# ═════════════════════ ꜱᴇꜱꜱɪᴏɴ / ʀᴀᴛᴇ / ᴘᴇʀᴍꜱ ═════════════════════
def get_sess(c, user_id): return SESSIONS.get((c.bot_id, user_id))
def set_sess(c, user_id, step, **data):
    data.pop("user_id", None)
    SESSIONS[(c.bot_id, user_id)] = {"step": step, "data": data}
def clear_sess(c, user_id): SESSIONS.pop((c.bot_id, user_id), None)

def rate_ok(c, uid):
    k = (c.bot_id, uid); t = now()
    if t - RATE.get(k, 0) < 2.5: return False
    RATE[k] = t; return True

def is_supreme(uid):
    if not uid:
        return False
    try:
        return int(uid) in SUPREMES
    except (ValueError, TypeError):
        return False

async def is_user_banned(c, uid):
    u = await c.store.get("users", str(uid)) or await c.store.get("users", uid)
    return bool(u and u.get("is_banned"))

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
                                              link_preview_options=LPO_DISABLE)
        except RPCError:
            pass

async def log_event(c, event, detail="", important=False, uid=None):
    await c.store.put("activity", secrets.token_hex(5),
                      {"event": event, "detail": detail, "uid": uid, "at": now()})
    text = f"{event}\n{detail}\n🤖 @{c.username} | {dt(now())}"
    lc = cfg(c.store).get("log_channel", 0)
    if lc:
        try: await c.send_message(lc, text, parse_mode=PM_OFF, link_preview_options=LPO_DISABLE)
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
    await log_event(c, "🚫 ᴜɴᴀᴜᴛʜᴏʀɪᴢᴇᴅ ᴀᴄᴄᴇꜱꜱ ᴀᴛᴛᴇᴍᴘᴛ", f"User: {uid}", important=True, uid=uid)

async def q_safe(q, text, alert=False):
    try: await q.answer(sc(text), show_alert=alert)
    except RPCError: pass

# ═════════════════════ ᴀᴜᴛᴏ ᴄᴏᴍᴍᴀɴᴅꜱ (ꜱᴇᴛᴍʏᴄᴏᴍᴍᴀɴᴅꜱ) ═════════════════════
def _cmds(lst): return [BotCommand(a, sc(b)) for a, b in lst]

async def apply_admin_commands(c, uid):
    lst = USER_CMD_RAW + ADMIN_CMD_RAW + (FACTORY_CMD_RAW if c.is_factory else []) + (SUPREME_CMD_RAW if is_supreme(uid) else [])
    try:
        await c.set_bot_commands(_cmds(lst), scope=BotCommandScopeChat(chat_id=int(uid)))
    except Exception as e:
        LOG.debug("set_bot_commands admin failed: %s", e)

async def apply_commands(c):
    base = USER_CMD_RAW + (FACTORY_CMD_RAW if c.is_factory else [])
    try:
        await c.set_bot_commands(_cmds(base), scope=BotCommandScopeDefault())
    except Exception as e:
        LOG.debug("set_bot_commands default failed: %s", e)
    for uid in list(c.store.c("admins").keys()):
        await apply_admin_commands(c, int(uid))
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
    await log_event(c, "🆕 ɴᴇᴡ ᴜꜱᴇʀ", f"Chat: {uid} (@{u['username']})", important=True, uid=tu.id)
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
        await log_event(c, "🤝 ʀᴇꜰᴇʀʀᴀʟ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ", f"Ref: {r['referrer']} → {uid}", uid=uid)
        try:
            await c.send_message(int(r["referrer"]), "🎉 <b>ɴᴇᴡ ʀᴇꜰᴇʀʀᴀʟ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟ!</b>\n\n🎁 Keep sharing!", parse_mode=PM_HTML)
        except RPCError:
            pass

def render_text(template, user, c):
    name = hesc(user.get("first_name") or "User")
    uname = hesc(user.get("username") or user.get("_id", ""))
    return (template.replace("{name}", name).replace("{username}", uname)
            .replace("{botname}", hesc(c.username)))

def get_official_link(c):
    link = cfg(c.store).get("official_link") or c.store.c("settings").get("official_link")
    if link:
        return link
    if FACTORY:
        link = cfg(FACTORY).get("official_link") or FACTORY.c("settings").get("official_link")
        if link:
            return link
    return "https://t.me"

async def send_start_content(c, chat_id, user, edit_msg=None):
    s = c.store.c("settings").get("start") or {"type": "text", "text": DEFAULT_START}
    text = render_text(s.get("text") or DEFAULT_START, user or {}, c)
    off_link = get_official_link(c)
    rows = [
        [ubtn("📢 ᴏꜰꜰɪᴄɪᴀʟ ᴄʜᴀɴɴᴇʟ", off_link), btn("🤖 ᴄʟᴏɴᴇ ʙᴏᴛ", "cloneme")],
        [btn("📺 ꜱᴇʟᴇᴄᴛ ᴀɴɪᴍᴇ", "usr|anime_list")]
    ]

    c_btns = (c.store.c("settings").get("custom_buttons") or {}).get("list", [])
    for r in c_btns:
        row_arr = [ubtn(b["text"], b["url"]) for b in r if isinstance(b, dict) and "text" in b and "url" in b]
        if row_arr:
            rows.append(row_arr)

    kb = InlineKeyboardMarkup(rows)
    t = s.get("type", "text")

    if edit_msg is not None:
        try:
            if edit_msg.text:
                await edit_msg.edit_text(text, parse_mode=PM_HTML, reply_markup=kb, link_preview_options=LPO_DISABLE)
                return
            elif edit_msg.caption:
                await edit_msg.edit_caption(caption=text, parse_mode=PM_HTML, reply_markup=kb)
                return
        except RPCError:
            try:
                await edit_msg.delete()
            except RPCError:
                pass

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
                                 link_preview_options=LPO_DISABLE)
    except RPCError as e:
        LOG.warning("Start content fallback: %s", e)
        try:
            await c.send_message(chat_id, text, parse_mode=PM_HTML, reply_markup=kb,
                                 link_preview_options=LPO_DISABLE)
        except RPCError:
            pass

# ═════════════════════ ᴇᴘɪꜱᴏᴅᴇ ᴅᴇʟɪᴠᴇʀʏ & ꜱᴇᴀʀᴄʜ ═════════════════════
def build_caption(c, ep, user):
    st = cfg(c.store)
    base = ep.get("caption") or st.get("caption") or DEFAULT_CAPTION
    name = hesc(user.get("first_name") or "Anime Fan") if user else "Anime Fan"
    uname = hesc(user.get("username") or "—") if user else "—"
    return (base.replace("{season}", str(ep["season"])).replace("{episode}", str(ep["episode"]))
                .replace("{name}", name).replace("{username}", uname)
                .replace("{botname}", c.username or "bot"))

async def resolve_thumb(c, ep):
    p = ep.get("thumb_path")
    if p and os.path.exists(p): return p
    tid = ep.get("thumb_id")
    if not tid: return None
    os.makedirs(THUMB_DIR, exist_ok=True)
    path = os.path.join(THUMB_DIR, f"{c.bot_id}_{ep.get('anime_id','default')}_{ep['season']}_{ep['episode']}.jpg")
    try:
        out = await c.download_media(tid, file_name=path)
        ep["thumb_path"] = out or path
        c.store.flush_soon()
        return ep["thumb_path"]
    except Exception:
        return None

async def save_episode(c, uid, aid, s, e, file_id, mtype, caption, thumb_id, quality=None):
    existing = await c.store.get("episodes", ep_id(aid, s, e))
    if existing:
        fids = existing.get("file_ids") or ([existing["file_id"]] if existing.get("file_id") else [])
        if file_id not in fids:
            fids.append(file_id)
        existing["file_ids"] = fids
        existing["file_id"] = fids[0]
        qualities = existing.get("qualities") or {}
        if quality:
            qualities[quality] = file_id
        existing["qualities"] = qualities
        existing["updated_at"] = now()
        if caption: existing["caption"] = caption
        if thumb_id: existing["thumb_id"] = thumb_id
        await c.store.put("episodes", ep_id(aid, s, e), existing)
        doc = existing
    else:
        qualities = {quality: file_id} if quality else {}
        doc = {"_id": ep_id(aid, s, e), "anime_id": aid, "season": s, "episode": e, "file_id": file_id, "file_ids": [file_id], "qualities": qualities, "type": mtype,
               "caption": caption or "", "thumb_id": thumb_id, "thumb_path": None,
               "uploaded_by": uid, "created_at": now(), "updated_at": now()}
        await c.store.put("episodes", doc["_id"], doc)
    await touch_active(c)
    anime = await c.store.get("animes", aid)
    title = anime.get("title") if anime else aid
    await log_event(c, "🎬 ᴇᴘɪꜱᴏᴅᴇ ᴜᴘʟᴏᴀᴅᴇᴅ", f"Anime: {title}\nSeason: {s} | Episode: {e}\nUploaded by: {uid}", important=True, uid=uid)
    return doc

async def show_user_anime_list(c, chat_id, page=1, edit_msg=None):
    animes = c.store.find("animes")
    animes.sort(key=lambda x: x.get("title", "").lower())
    per_page = 10
    total = len(animes)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    page_animes = animes[start_idx:start_idx + per_page]

    rows = []
    # 2 columns per row, up to 5 rows (10 items total)
    for i in range(0, len(page_animes), 2):
        pair = page_animes[i:i + 2]
        row_btns = [btn(a.get("title", "Anime")[:18], f"usr|anime|{a['_id']}") for a in pair]
        rows.append(row_btns)

    # Navigation buttons for pagination
    if total_pages > 1:
        nav = []
        if page > 1:
            nav.append(btn("◀️ ᴘʀᴇᴠ", f"usr|anime_list|{page - 1}"))
        nav.append(btn(f"📄 {page}/{total_pages}", "ignore"))
        if page < total_pages:
            nav.append(btn("ɴᴇxᴛ ▶️", f"usr|anime_list|{page + 1}"))
        rows.append(nav)

    rows.append([btn("🔍 ꜱᴇᴀʀᴄʜ ᴀɴɪᴍᴇ", "usr|search_anime")])
    rows.append([btn("🔙 ʙᴀᴄᴋ", "usr|home")])

    txt = f"📺 <b>ꜱᴇʟᴇᴄᴛ ᴀɴɪᴍᴇ</b> (Total: <b>{total}</b>):"
    kb = InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try:
            if edit_msg.text:
                await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
            elif edit_msg.caption:
                await edit_msg.delete()
                await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError:
            await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def show_user_season_list(c, chat_id, aid, edit_msg=None):
    anime = await c.store.get("animes", aid)
    title = anime.get("title", "Anime") if anime else "Anime"
    banner_fid = anime.get("banner_file_id") if anime else None
    banner_cap = anime.get("banner_caption") if anime else None

    eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid]
    s_set = {v["season"] for v in eps if "season" in v}
    st_map = (anime or {}).get("seasons", {})
    s_set.update(int(k) for k in st_map.keys() if str(k).isdigit())
    seasons = sorted(s_set)
    rows = []
    # 2 columns layout for seasons
    for i in range(0, len(seasons), 2):
        pair = seasons[i:i + 2]
        rows.append([btn(f"📚 ꜱᴇᴀꜱᴏɴ {sn}", f"usr|season|{aid}|{sn}") for sn in pair])
    rows.append([btn("🔙 ʙᴀᴄᴋ", "usr|anime_list")])

    txt = f"📺 <b>{hesc(title)} — ꜱᴇʟᴇᴄᴛ ꜱᴇᴀꜱᴏɴ:</b>"
    if banner_cap:
        txt = f"📺 <b>{hesc(title)}</b>\n\n{banner_cap}\n\n<b>ꜱᴇʟᴇᴄᴛ ꜱᴇᴀꜱᴏɴ:</b>"

    kb = InlineKeyboardMarkup(rows)

    if edit_msg is not None:
        try:
            if banner_fid:
                if edit_msg.photo or edit_msg.caption is not None:
                    await edit_msg.edit_caption(caption=txt, reply_markup=kb, parse_mode=PM_HTML)
                    return
                else:
                    await edit_msg.delete()
            else:
                if edit_msg.text:
                    await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
                    return
                else:
                    await edit_msg.delete()
        except RPCError:
            pass

    if banner_fid:
        try:
            await c.send_photo(chat_id, banner_fid, caption=txt, reply_markup=kb, parse_mode=PM_HTML)
            return
        except RPCError:
            pass
    await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def show_user_episode_list(c, chat_id, aid, sn, page=1, edit_msg=None):
    anime = await c.store.get("animes", aid)
    title = anime.get("title", "Anime") if anime else "Anime"
    st_map = (anime or {}).get("seasons", {})
    s_info = st_map.get(str(sn), {}) if isinstance(st_map.get(str(sn)), dict) else {}
    s_banner_fid = s_info.get("banner_file_id")
    s_banner_cap = s_info.get("banner_caption")

    eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid and v.get("season") == sn]
    eps.sort(key=lambda x: x.get("episode", 0))

    per_page = 10
    total = len(eps)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))

    start_idx = (page - 1) * per_page
    page_eps = eps[start_idx:start_idx + per_page]

    rows = []
    # 2 columns layout for episodes
    for i in range(0, len(page_eps), 2):
        pair = page_eps[i:i + 2]
        rows.append([btn(f"🎬 ᴇᴘɪꜱᴏᴅᴇ {ep.get('episode', 0)}", f"usr|ep|{aid}|{sn}|{ep.get('episode', 0)}") for ep in pair])

    if total_pages > 1:
        nav = []
        if page > 1:
            nav.append(btn("◀️ ᴘʀᴇᴠ", f"usr|season|{aid}|{sn}|{page - 1}"))
        nav.append(btn(f"📄 {page}/{total_pages}", "ignore"))
        if page < total_pages:
            nav.append(btn("ɴᴇxᴛ ▶️", f"usr|season|{aid}|{sn}|{page + 1}"))
        rows.append(nav)

    rows.append([btn("🔙 ʙᴀᴄᴋ", f"usr|anime|{aid}")])

    txt = f"📺 <b>{hesc(title)} • ꜱᴇᴀꜱᴏɴ {sn} — ꜱᴇʟᴇᴄᴛ ᴇᴘɪꜱᴏᴅᴇ:</b>"
    if s_banner_cap:
        txt = f"📺 <b>{hesc(title)} • ꜱᴇᴀꜱᴏɴ {sn}</b>\n\n{s_banner_cap}\n\n<b>ꜱᴇʟᴇᴄᴛ ᴇᴘɪꜱᴏᴅᴇ:</b>"

    kb = InlineKeyboardMarkup(rows)

    if edit_msg is not None:
        try:
            if s_banner_fid:
                if edit_msg.photo or edit_msg.caption is not None:
                    await edit_msg.edit_caption(caption=txt, reply_markup=kb, parse_mode=PM_HTML)
                    return
                else:
                    await edit_msg.delete()
            else:
                if edit_msg.text:
                    await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
                    return
                else:
                    await edit_msg.delete()
        except RPCError:
            pass

    if s_banner_fid:
        try:
            await c.send_photo(chat_id, s_banner_fid, caption=txt, reply_markup=kb, parse_mode=PM_HTML)
            return
        except RPCError:
            pass
    await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def send_episode(c, chat_id, aid, s, e, user=None, req_quality=None):
    ep = await c.store.get("episodes", ep_id(aid, s, e))
    if not ep:
        return False
    if user is None:
        user = await c.store.get("users", str(chat_id))

    chosen_quality = req_quality or (user.get("pref_quality") if user else None)
    qualities = ep.get("qualities") or {}

    file_ids = []
    if qualities:
        if chosen_quality and chosen_quality in qualities:
            file_ids = [qualities[chosen_quality]]
        else:
            for q in [chosen_quality, "720p", "1080p", "480p"]:
                if q in qualities:
                    file_ids = [qualities[q]]
                    chosen_quality = q
                    break
            if not file_ids:
                q_k = list(qualities.keys())[0]
                file_ids = [qualities[q_k]]
                chosen_quality = q_k
    else:
        file_ids = ep.get("file_ids") or ([ep["file_id"]] if ep.get("file_id") else [])

    if not file_ids:
        return False

    caption = build_caption(c, ep, user)
    if chosen_quality:
        caption += f"\n\n⚙️ <b>Quality: {chosen_quality}</b>"

    q_param = chosen_quality or "default"
    kb = InlineKeyboardMarkup([
        [btn("▶️ ɴᴇxᴛ ᴇᴘɪꜱᴏᴅᴇ ▶️", f"next|{aid}:{s}:{e}|{q_param}")],
        [btn("⚙️ ᴄʜᴀɴɢᴇ Qᴜᴀʟɪᴛʏ", f"usr|ep_q_menu|{aid}|{s}|{e}"), btn("🏠 ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", "usr|home")]
    ])
    thumb = await resolve_thumb(c, ep)

    total_files = len(file_ids)
    for idx, fid in enumerate(file_ids):
        is_last = (idx == total_files - 1)
        reply_kb = kb if is_last else None
        sent = False
        t = ep.get("type", "video")
        for attempt in range(2):
            try:
                if t == "animation":
                    await c.send_animation(chat_id, fid, caption=(caption if is_last else None), parse_mode=PM_HTML, reply_markup=reply_kb)
                elif t == "document":
                    await c.send_document(chat_id, fid, caption=(caption if is_last else None), parse_mode=PM_HTML, reply_markup=reply_kb, thumb=thumb)
                else:
                    await c.send_video(chat_id, fid, caption=(caption if is_last else None), parse_mode=PM_HTML, reply_markup=reply_kb, thumb=thumb)
                sent = True
                break
            except FloodWait as fw:
                if attempt == 0:
                    await asyncio.sleep(min(fw.value, 60))
            except RPCError as ex:
                LOG.error("send_episode file sending error: %s", ex)
                break
        if not sent and is_last and total_files == 1:
            try: await c.send_message(chat_id, "⚠️ <b>ꜰᴀɪʟᴇᴅ ᴛᴏ ꜱᴇɴᴅ ꜰɪʟᴇ.</b> Try again later.", parse_mode=PM_HTML)
            except RPCError: pass
            return True

    await touch_active(c)
    await c.store.put("activity", secrets.token_hex(5),
                      {"event": "📤 ᴇᴘɪꜱᴏᴅᴇ ꜱᴇɴᴛ", "detail": f"S{s} E{e} → {chat_id}", "uid": chat_id, "at": now()})
    return True

# ═════════════════════ ᴄᴏᴍᴍᴀɴᴅ ʜᴀɴᴅʟᴇʀꜱ ═════════════════════
async def cmd_start(c, m):
    uid = m.from_user.id
    if await is_user_banned(c, uid):
        try: await m.reply("❌ <b>You are banned from using this bot!</b>", parse_mode=PM_HTML)
        except RPCError: pass
        return
    user = await ensure_user(c, m.from_user)
    payload = m.command[1] if len(m.command) > 1 else ""
    if payload.startswith("anime_"):
        aid = payload[6:]
        await c.store.update("users", str(uid), pending_anime=aid)
    elif payload.startswith("ref_"):
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
            await m.reply("🔐 <b>ᴀᴄᴄᴇꜱꜱ ʟᴏᴄᴋᴇᴅ!</b>\n\nJoin the channel then press ✅ ᴠᴇʀɪꜰʏ.",
                          reply_markup=kb, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError:
            pass
        return
    await convert_referral(c, uid)
    user_doc = await c.store.get("users", str(uid)) or user
    pending_anime = user_doc.get("pending_anime") if user_doc else None
    if pending_anime:
        await c.store.update("users", str(uid), pending_anime=None)
        await show_user_season_list(c, m.chat.id, pending_anime)
        return
    await send_start_content(c, m.chat.id, user)

async def episode_request(c, m):
    uid = m.from_user.id
    if not rate_ok(c, uid): return
    ok, kb = await fs_state(c, uid)
    if not ok:
        await unauthorized(c, uid)
        try:
            await m.reply("🔐 <b>ᴀᴄᴄᴇꜱꜱ ʟᴏᴄᴋᴇᴅ!</b> Join the channel first.",
                          reply_markup=kb, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError:
            pass
        return

    query = (m.text or "").strip()
    matches = flexible_search(c.store.c("episodes"), query)

    if len(matches) == 1:
        ep = matches[0]
        await send_episode(c, uid, ep["season"], ep["episode"])
        return

    if len(matches) > 1:
        rows = []
        for ep in matches[:10]:
            s, e = ep["season"], ep["episode"]
            rows.append([btn(f"🎬 ꜱᴇᴀꜱᴏɴ {s} • ᴇᴘɪꜱᴏᴅᴇ {e}", f"ep|{s}:{e}")])

        txt = (f"🔍 <b>ꜱᴇᴀʀᴄʜ ʀᴇꜱᴜʟᴛꜱ ꜰᴏʀ:</b> <code>{hesc(query)}</code>\n"
               f"━━━━━━━━━━━━━━\n"
               f"✨ Found <b>{len(matches)}</b> matching episodes!\n"
               f"👇 Tap below to watch:")
        await m.reply(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        return

    # No matches found -> Show clean guide + available season buttons
    seasons = sorted({int(k.split(":")[0]) for k in c.store.c("episodes")})
    if seasons:
        kb_rows = [[btn(f"📚 ꜱᴇᴀꜱᴏɴ {x}", f"sea|{x}") for x in seasons[:5]]]
        await m.reply(f"❌ <b>ɴᴏ ᴇᴘɪꜱᴏᴅᴇꜱ ꜰᴏᴜɴᴅ ꜰᴏʀ:</b> <code>{hesc(query)}</code>\n\n"
                      f"💡 <b>ᴛʀʏ ꜱᴇᴀʀᴄʜɪɴɢ:</b>\n"
                      f"▸ S1 E4 / Season 1 Episode 4\n"
                      f"▸ Season 1 / S1\n"
                      f"▸ Anime Keyword\n\n"
                      f"📚 <b>ᴀᴠᴀɪʟᴀʙʟᴇ ꜱᴇᴀꜱᴏɴꜱ:</b>",
                      reply_markup=InlineKeyboardMarkup(kb_rows), parse_mode=PM_HTML)
    else:
        await m.reply("❌ <b>ɴᴏ ᴇᴘɪꜱᴏᴅᴇꜱ ᴜᴘʟᴏᴀᴅᴇᴅ ʏᴇᴛ!</b>\n\nCome back soon ✨", parse_mode=PM_HTML)

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
    return "🏆 <b>ʀᴇꜰᴇʀʀᴀʟ ʀᴀɴᴋɪɴɢ</b>\n━━━━━━━━━━━━━━\n" + ("\n".join(lines) if lines else "No referrals yet.")

async def send_refer(c, chat_id, uid):
    store = c.store
    invited, conv = refer_stats(store, uid)
    rate = f"{(conv / invited * 100):.1f}" if invited else "0.0"
    link = f"https://t.me/{c.username}?start=ref_{uid}"
    txt = (f"🎁 <b>ʀᴇꜰᴇʀ & ᴇᴀʀɴ</b>\n━━━━━━━━━━━━━━\n"
           f"🔗 <code>{link}</code>\n\n"
           f"👥 Invited Users: <b>{invited}</b>\n"
           f"✅ Successful Joins: <b>{conv}</b>\n"
           f"📈 Conversion Rate: <b>{rate}%</b>\n"
           f"🤖 Bot: @{c.username}\n"
           f"🌍 Total Bot Users: <b>{store.count('users')}</b>")
    kb = InlineKeyboardMarkup([
        [ubtn("🟢 ꜱʜᴀʀᴇ ʙᴏᴛ", f"https://t.me/share/url?url={quote(link)}&text={quote('🎬 Watch Anime Free!')}")],
        [btn("🔵 ᴄᴏᴘʏ ʟɪɴᴋ", "rf|link"), btn("🟣 ʀᴇꜰᴇʀʀᴀʟ ꜱᴛᴀᴛꜱ", "rf|stats")]])
    await c.send_message(chat_id, txt, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE, reply_markup=kb)

async def cmd_refer(c, m):
    uid = m.from_user.id
    if await is_user_banned(c, uid):
        try: await m.reply("❌ <b>You are banned from using this bot!</b>", parse_mode=PM_HTML)
        except RPCError: pass
        return
    await ensure_user(c, m.from_user)
    await send_refer(c, m.chat.id, m.from_user.id)

async def cmd_help(c, m):
    uid = m.from_user.id
    if await is_user_banned(c, uid):
        try: await m.reply("❌ <b>You are banned from using this bot!</b>", parse_mode=PM_HTML)
        except RPCError: pass
        return
    user = await ensure_user(c, m.from_user)
    is_adm = is_supreme(uid) or (await c.store.get("admins", uid) is not None)

    txt = ("❓ <b>ʜᴇʟᴘ & ᴄᴏᴍᴍᴀɴᴅꜱ</b>\n━━━━━━━━━━━━━━\n\n"
           "👤 <b>ᴜꜱᴇʀ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>\n"
           "▸ /start — Start Bot & Main Menu\n"
           "▸ /help — Show Available Commands\n"
           "▸ /refer — Refer Friends & Check Stats\n\n"
           "💡 <b>ʜᴏᴡ ᴛᴏ ꜰɪɴᴅ ᴇᴘɪꜱᴏᴅᴇꜱ:</b>\n"
           "▸ Tap <b>📺 ꜱᴇʟᴇᴄᴛ ᴀɴɪᴍᴇ</b> in main menu\n"
           "▸ Or send query directly: <code>S1 E4</code> or <code>Anime Name</code>\n")

    if c.is_factory:
        txt += "\n🤖 <b>ꜰᴀᴄᴛᴏʀʏ ᴄᴏᴍᴍᴀɴᴅ:</b>\n▸ /clone — Create your own bot\n"

    if is_adm:
        txt += ("\n🛠 <b>ᴀᴅᴍɪɴ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>\n"
                "▸ /admin — Open Admin Control Panel\n"
                "▸ /upload — Add Anime Episodes\n"
                "▸ /edit — Edit Anime / Season / Episode\n"
                "▸ /delete — Delete Anime or Episode\n"
                "▸ /broadcast — Broadcast Message to Users\n"
                "▸ /stats — View Bot Statistics\n"
                "▸ /list — View Anime List\n"
                "▸ /listsearch — Search Uploaded Episodes\n"
                "▸ /setfs — Configure Force Subscribe\n"
                "▸ /editstart — Customize Start Message\n"
                "▸ /giveadmin — Add New Admin\n"
                "▸ /editadmin — Modify Admin Rights\n"
                "▸ /remadmin — Remove Admin\n"
                "▸ /ban — Ban User\n"
                "▸ /unban — Unban User\n"
                "▸ /seasonend — Mark Season Ended\n"
                "▸ /coming — Mark Season Coming Soon\n"
                "▸ /done — Finish Upload Session\n"
                "▸ /cancel — Cancel Active Session\n")

    if is_supreme(uid):
        txt += ("\n👑 <b>ꜱᴜᴘʀᴇᴍᴇ ᴄᴏᴍᴍᴀɴᴅꜱ:</b>\n"
                "▸ /supreme — Supreme Control Panel\n"
                "▸ /botlist — View All Cloned Bots\n"
                "▸ /db — Database Insights & Health\n"
                "▸ /restart — Gracefully Restart Clones\n")

    kb = InlineKeyboardMarkup([[btn("🏠 ʙᴀᴄᴋ ᴛᴏ ʜᴏᴍᴇ", "usr|home")]])
    await m.reply(txt, reply_markup=kb, parse_mode=PM_HTML)

# ─────────── ᴜᴘʟᴏᴀᴅ ───────────
async def show_upload_menu(c, chat_id, edit_msg=None):
    animes = c.store.find("animes")
    animes.sort(key=lambda x: x.get("title", "").lower())
    rows = [[btn("➕ ᴀᴅᴅ ᴀɴɪᴍᴇ", "up|add_anime")]]
    for a in animes:
        rows.append([btn(a.get("title", "Anime"), f"up|sel_anime|{a['_id']}")])
    rows.append([btn("🔴 ᴄᴀɴᴄᴇʟ", "up|cancel")])
    txt = ("⬆️ <b>ᴜᴘʟᴏᴀᴅ ᴄᴇɴᴛᴇʀ</b>\n━━━━━━━━━━━━━━\n"
           "Select an anime to upload episodes or add a new anime:")
    kb = InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def show_upload_options(c, chat_id, aid, edit_msg=None):
    anime = await c.store.get("animes", aid)
    title = anime.get("title", "Anime") if anime else "Anime"
    rows = [
        [btn("🟢 ᴀᴅᴅ ᴇᴘɪꜱᴏᴅᴇ", f"up|add_ep|{aid}"), btn("🔵 ɴᴇᴡ ꜱᴇᴀꜱᴏɴ", f"up|new_sea|{aid}")],
        [btn("🔴 ᴄᴀɴᴄᴇʟ", "up|cancel")]
    ]
    txt = f"📺 <b>{hesc(title)}</b>\n━━━━━━━━━━━━━━\nSelect option to add episode or new season:"
    kb = InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def show_upload_season_select(c, chat_id, aid, edit_msg=None):
    anime = await c.store.get("animes", aid)
    title = anime.get("title", "Anime") if anime else "Anime"
    eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid]
    s_set = {v["season"] for v in eps if "season" in v}
    st_map = (anime or {}).get("seasons", {})
    s_set.update(int(k) for k in st_map.keys() if str(k).isdigit())
    seasons = sorted(s_set)

    rows = [[btn("🔵 ɴᴇᴡ ꜱᴇᴀꜱᴏɴ", f"up|new_sea|{aid}")]]
    for sn in seasons:
        rows.append([btn(f"📚 ꜱᴇᴀꜱᴏɴ {sn}", f"up|sel_ep_season|{aid}|{sn}")])
    rows.append([btn("🔴 ᴄᴀɴᴄᴇʟ", "up|cancel")])

    txt = f"📚 <b>{hesc(title)} — ꜱᴇʟᴇᴄᴛ ꜱᴇᴀꜱᴏɴ ᴛᴏ ᴀᴅᴅ ᴇᴘɪꜱᴏᴅᴇ:</b>"
    kb = InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def show_admin_anime_select(c, chat_id, title="📺 <b>ꜱᴇʟᴇᴄᴛ ᴀɴɪᴍᴇ:</b>", edit_msg=None, extra_prefix="adm_sel_anime"):
    animes = c.store.find("animes")
    animes.sort(key=lambda x: x.get("title", "").lower())
    rows = []
    for a in animes:
        rows.append([btn(a.get("title", "Anime"), f"{extra_prefix}|{a['_id']}")])
    rows.append([btn("❌ ᴄᴀɴᴄᴇʟ", "up|cancel")])
    kb = InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(title, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, title, reply_markup=kb, parse_mode=PM_HTML)

async def cmd_seasonend(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "upload"):
        await m.reply("❌ <b>NO UPLOAD PERMISSION!</b>", parse_mode=PM_HTML); return
    set_sess(c, uid, "status_anime", target_status="seasonend")
    await show_admin_anime_select(c, m.chat.id, title="🏁 <b>ꜱᴇʟᴇᴄᴛ ᴀɴɪᴍᴇ ꜰᴏʀ /seasonend:</b>")

async def cmd_coming(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "upload"):
        await m.reply("❌ <b>NO UPLOAD PERMISSION!</b>", parse_mode=PM_HTML); return
    set_sess(c, uid, "status_anime", target_status="coming")
    await show_admin_anime_select(c, m.chat.id, title="🔔 <b>ꜱᴇʟᴇᴄᴛ ᴀɴɪᴍᴇ ꜰᴏʀ /coming:</b>")

async def cmd_upload(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "upload"):
        await m.reply("❌ <b>NO UPLOAD PERMISSION!</b>", parse_mode=PM_HTML); return
    s = get_sess(c, uid)
    if s and str(s.get("step", "")).startswith(("up_", "ns_")):
        if await perm_ok(c, uid, "restart_upload"):
            await show_upload_menu(c, m.chat.id); return
        await m.reply("♻️ <b>UPLOAD SESSION ALREADY ACTIVE!</b>\n\nSend /done to finish or /cancel",
                      parse_mode=PM_HTML); return
    set_sess(c, uid, "up_menu")
    await show_upload_menu(c, m.chat.id)

async def up_got_video(c, m):
    uid = m.from_user.id
    mtype, fid, tid = get_media(m)
    if not fid:
        await m.reply("📤 Send a <b>video</b> file now...", parse_mode=PM_HTML); return
    s = get_sess(c, uid)
    d = s["data"]
    aid, sn, en = d["anime_id"], d["season"], d["episode"]
    anime = await c.store.get("animes", aid)
    title = anime.get("title", "Anime") if anime else "Anime"

    d["pending_file"] = {"fid": fid, "mtype": mtype, "caption": m.caption or "", "tid": tid}

    kb = InlineKeyboardMarkup([
        [btn("📱 480p", "up_q|480p"), btn("🎬 720p", "up_q|720p"), btn("🖥️ 1080p", "up_q|1080p")],
        [btn("⚙️ Default / Auto", "up_q|default")]
    ])

    await m.reply(f"📹 <b>{hesc(title)} — S{sn} E{en} Video Received!</b>\n\n👇 <b>Select Quality for this upload:</b>",
                  reply_markup=kb, parse_mode=PM_HTML)

async def ns_got_season(c, m):
    uid = m.from_user.id
    txt = (m.text or "").strip()
    if not txt.isdigit() or not (1 <= int(txt) <= 999):
        await m.reply("🔢 Send a valid season number (ex: 2):", parse_mode=PM_HTML); return
    if not (await perm_ok(c, uid, "seasons") or await perm_ok(c, uid, "upload")):
        await m.reply("❌ <b>NO SEASONS PERMISSION!</b>", parse_mode=PM_HTML); clear_sess(c, uid); return
    s = get_sess(c, uid)
    aid = s["data"]["anime_id"]
    sn = int(txt)
    anime = await c.store.get("animes", aid)
    title = anime.get("title", "Anime") if anime else "Anime"
    s["data"].update({"season": sn, "episode": 1, "added": 0})
    s["step"] = "ns_video"
    await m.reply(f"🆕 <b>{hesc(title)} — Season {sn} Started — Episode 1!</b>\n\n📤 Send videos one by one...\n🏁 /done • ❌ /cancel",
                  parse_mode=PM_HTML)

async def ns_got_video(c, m):
    uid = m.from_user.id
    mtype, fid, tid = get_media(m)
    if not fid:
        await m.reply("📤 Send a <b>video</b> file:", parse_mode=PM_HTML); return
    s = get_sess(c, uid); d = s["data"]
    aid, sn, en = d["anime_id"], d["season"], d["episode"]
    anime = await c.store.get("animes", aid)
    title = anime.get("title", "Anime") if anime else "Anime"

    d["pending_file"] = {"fid": fid, "mtype": mtype, "caption": m.caption or "", "tid": tid}

    kb = InlineKeyboardMarkup([
        [btn("📱 480p", "up_q|480p"), btn("🎬 720p", "up_q|720p"), btn("🖥️ 1080p", "up_q|1080p")],
        [btn("⚙️ Default / Auto", "up_q|default")]
    ])

    await m.reply(f"📹 <b>{hesc(title)} — S{sn} E{en} Video Received!</b>\n\n👇 <b>Select Quality for this upload:</b>",
                  reply_markup=kb, parse_mode=PM_HTML)

async def cmd_done(c, m):
    uid = m.from_user.id
    s = get_sess(c, uid)
    if s and s["step"] == "ns_video":
        d = s["data"]
        sn_val = d.get("season") or d.get("ns_season") or "?"
        await m.reply(f"🏁 <b>Season {sn_val} Complete!</b>\n\n✅ {d.get('added', 0)} episodes added",
                      parse_mode=PM_HTML)
        await log_event(c, "🏁 ꜱᴇᴀꜱᴏɴ ʙᴀᴛᴄʜ ᴅᴏɴᴇ", f"S{sn_val} • {d.get('added',0)} eps", uid=uid)
        clear_sess(c, uid)
    elif s and str(s["step"]).startswith("up_"):
        await m.reply(f"🏁 <b>Upload Session Finished!</b>\n\n✅ {s['data'].get('added', 0)} episodes added",
                      parse_mode=PM_HTML)
        clear_sess(c, uid)
    else:
        await m.reply("❌ No active upload session.")

async def cmd_cancel(c, m):
    clear_sess(c, m.from_user.id)
    await m.reply("❌ <b>Cancelled!</b>", parse_mode=PM_HTML)

# ─────────── ᴇᴅɪᴛ / ᴅᴇʟᴇᴛᴇ ───────────
def edit_kb(aid, s, e):
    return InlineKeyboardMarkup([
        [btn("🎬 Replace Video", f"ed|video|{aid}:{s}:{e}"), btn("✏️ Edit Caption", f"ed|cap|{aid}:{s}:{e}")],
        [btn("🖼️ Replace Thumb", f"ed|thumb|{aid}:{s}:{e}")],
        [btn("⬅️ Back", "pan|refresh")]])

async def show_editor(c, chat_id, aid, s, e):
    ep = await c.store.get("episodes", ep_id(aid, s, e))
    if not ep:
        await c.send_message(chat_id, f"❌ S{s} E{e} not found!"); return
    anime = await c.store.get("animes", aid)
    title = anime.get("title", "Anime") if anime else "Anime"
    txt = (f"✏️ <b>Edit — {hesc(title)} (S{s} E{e})</b>\n━━━━━━━━━━━━━━\n"
           f"🎬 Type: {ep.get('type','video')}\n"
           f"📝 Caption: {(ep.get('caption') or '—')[:80]}\n"
           f"🖼️ Thumb: {'✅' if ep.get('thumb_id') or ep.get('thumb_path') else '❌'}\n"
           f"⏰ Updated: {dt(ep.get('updated_at', 0))}\n\nSelect:")
    await c.send_message(chat_id, txt, reply_markup=edit_kb(aid, s, e), parse_mode=PM_HTML)

async def show_admin_edit_menu(c, chat_id, edit_msg=None):
    animes = c.store.find("animes")
    animes.sort(key=lambda x: x.get("title", "").lower())
    rows = []
    for a in animes:
        rows.append([btn(a.get("title", "Anime"), f"adm_edit|anime|{a['_id']}")])
    rows.append([btn("🔙 ʙᴀᴄᴋ", "pan|refresh")])
    txt = "✏️ <b>ADMIN EDIT PANEL — SELECT ANIME TO EDIT:</b>"
    kb = InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def show_admin_delete_menu(c, chat_id, edit_msg=None):
    rows = [
        [btn("🗑️ ʀᴇᴍᴏᴠᴇ ᴀɴɪᴍᴇ", "adm_del|sel_anime_remove")],
        [btn("🎬 ʀᴇᴍᴏᴠᴇ ᴇᴘɪꜱᴏᴅᴇ", "adm_del|sel_anime_ep")],
        [btn("🔙 ʙᴀᴄᴋ", "pan|refresh")]
    ]
    txt = "🗑️ <b>ADMIN DELETE PANEL — SELECT OPTION:</b>"
    kb = InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def cb_adm_edit_menu(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "edit"):
        await q_safe(q, "❌ NO EDIT PERMISSION!"); return
    act = parts[1]
    if act == "anime":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        rows = [
            [btn("🖼️ Edit Anime Banner", f"adm_edit|edit_abanner|{aid}")],
            [btn("📝 Edit Anime Caption", f"adm_edit|edit_acap|{aid}")],
            [btn("📚 Edit Season Banner/Caption", f"adm_edit|sel_season|{aid}")],
            [btn("🎬 Edit Episode", f"adm_edit|sel_ep_season|{aid}")],
            [btn("🔙 ʙᴀᴄᴋ", "pan|edit")]
        ]
        txt = f"✏️ <b>EDIT OPTIONS FOR:</b> <code>{hesc(title)}</code>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "edit_abanner":
        aid = parts[2]
        set_sess(c, uid, "edit_anime_banner", anime_id=aid)
        await q_safe(q, "🖼️ Send Banner Image")
        try: await q.message.edit_text("🖼️ <b>Send new banner photo for this Anime:</b>\n\n(or send 'remove' to delete banner)", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "edit_acap":
        aid = parts[2]
        set_sess(c, uid, "edit_anime_caption", anime_id=aid)
        await q_safe(q, "📝 Send Caption")
        try: await q.message.edit_text("📝 <b>Send new caption/description for this Anime:</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "sel_season":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid]
        s_set = {v["season"] for v in eps if "season" in v}
        st_map = (anime or {}).get("seasons", {})
        s_set.update(int(k) for k in st_map.keys() if str(k).isdigit())
        seasons = sorted(s_set)
        rows = []
        for sn in seasons:
            rows.append([btn(f"📚 Season {sn}", f"adm_edit|edit_season_opts|{aid}|{sn}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", f"adm_edit|anime|{aid}")])
        txt = "📚 <b>SELECT SEASON TO EDIT BANNER/CAPTION:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "edit_season_opts":
        aid, sn = parts[2], int(parts[3])
        rows = [
            [btn("🖼️ Edit Season Banner", f"adm_edit|edit_sbanner|{aid}|{sn}")],
            [btn("📝 Edit Season Caption", f"adm_edit|edit_scap|{aid}|{sn}")],
            [btn("🔙 ʙᴀᴄᴋ", f"adm_edit|sel_season|{aid}")]
        ]
        txt = f"📚 <b>EDIT SEASON {sn} OPTIONS:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "edit_sbanner":
        aid, sn = parts[2], int(parts[3])
        set_sess(c, uid, "edit_season_banner", anime_id=aid, season=sn)
        await q_safe(q, "🖼️ Send Banner Image")
        try: await q.message.edit_text(f"🖼️ <b>Send new banner photo for Season {sn}:</b>\n\n(or send 'remove' to delete banner)", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "edit_scap":
        aid, sn = parts[2], int(parts[3])
        set_sess(c, uid, "edit_season_caption", anime_id=aid, season=sn)
        await q_safe(q, "📝 Send Caption")
        try: await q.message.edit_text(f"📝 <b>Send new caption text for Season {sn}:</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "sel_ep_season":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid]
        s_set = {v["season"] for v in eps if "season" in v}
        seasons = sorted(s_set)
        rows = []
        for sn in seasons:
            rows.append([btn(f"📚 Season {sn}", f"adm_edit|sel_ep_list|{aid}|{sn}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", f"adm_edit|anime|{aid}")])
        txt = "🎬 <b>SELECT SEASON TO EDIT EPISODES:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "sel_ep_list":
        aid, sn = parts[2], int(parts[3])
        eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid and v.get("season") == sn]
        eps.sort(key=lambda x: x.get("episode", 0))
        rows = []
        for ep in eps:
            en = ep.get("episode", 0)
            rows.append([btn(f"🎬 Episode {en}", f"adm_edit|show_editor|{aid}|{sn}|{en}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", f"adm_edit|sel_ep_season|{aid}")])
        txt = f"🎬 <b>SEASON {sn} — SELECT EPISODE TO EDIT:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "show_editor":
        aid, sn, en = parts[2], int(parts[3]), int(parts[4])
        await show_editor(c, q.message.chat.id, aid, sn, en)

async def cb_adm_del_menu(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "delete"):
        await q_safe(q, "❌ NO DELETE PERMISSION!"); return
    act = parts[1]
    if act == "sel_anime_remove":
        animes = c.store.find("animes")
        animes.sort(key=lambda x: x.get("title", "").lower())
        rows = []
        for a in animes:
            rows.append([btn(a.get("title", "Anime"), f"adm_del|confirm_1|{a['_id']}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", "pan|del")])
        txt = "🗑️ <b>SELECT ANIME TO REMOVE COMPLETELY:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "confirm_1":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        rows = [
            [btn("⚠️ YES, DELETE (1/3)", f"adm_del|confirm_2|{aid}")],
            [btn("❌ CANCEL", "pan|del")]
        ]
        txt = f"⚠️ <b>CONFIRM DELETION (1/3)</b>\n\nAre you sure you want to delete <b>{hesc(title)}</b> and ALL its episodes?"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "confirm_2":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        rows = [
            [btn("🚨 REALLY DELETE? (2/3)", f"adm_del|confirm_3|{aid}")],
            [btn("❌ CANCEL", "pan|del")]
        ]
        txt = f"🚨 <b>CONFIRM DELETION (2/3)</b>\n\nThis action cannot be undone! Delete <b>{hesc(title)}</b>?"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "confirm_3":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        rows = [
            [btn("🔥 FINAL CONFIRM (3/3) - REMOVE NOW", f"adm_del|do_remove_anime|{aid}")],
            [btn("❌ CANCEL", "pan|del")]
        ]
        txt = f"🔥 <b>FINAL WARNING (3/3)</b>\n\nClicking below will PERMANENTLY REMOVE <b>{hesc(title)}</b>!"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "do_remove_anime":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        # Delete anime document
        await c.store.delete("animes", aid)
        # Delete all episodes for this anime
        eps = [k for k, v in c.store.c("episodes").items() if v.get("anime_id") == aid]
        for k in eps:
            await c.store.delete("episodes", k)
        await log_event(c, "🗑️ ᴀɴɪᴍᴇ ʀᴇᴍᴏᴠᴇᴅ", f"Anime {aid} ({title}) + {len(eps)} eps removed", important=True, uid=uid)
        await q_safe(q, "🗑️ Anime Removed!")
        try: await q.message.edit_text(f"✅ <b>Anime '{hesc(title)}' and all its episodes have been completely deleted!</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "sel_anime_ep":
        animes = c.store.find("animes")
        animes.sort(key=lambda x: x.get("title", "").lower())
        rows = []
        for a in animes:
            rows.append([btn(a.get("title", "Anime"), f"adm_del|ep_season|{a['_id']}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", "pan|del")])
        txt = "🎬 <b>SELECT ANIME TO REMOVE EPISODE FROM:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "ep_season":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid]
        s_set = {v["season"] for v in eps if "season" in v}
        seasons = sorted(s_set)
        rows = []
        for sn in seasons:
            rows.append([btn(f"📚 Season {sn}", f"adm_del|ep_list|{aid}|{sn}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", "adm_del|sel_anime_ep")])
        txt = "📚 <b>SELECT SEASON:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "ep_list":
        aid, sn = parts[2], int(parts[3])
        eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid and v.get("season") == sn]
        eps.sort(key=lambda x: x.get("episode", 0))
        rows = []
        for ep in eps:
            en = ep.get("episode", 0)
            rows.append([btn(f"🎬 Episode {en}", f"adm_del|preview_ep|{aid}|{sn}|{en}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", f"adm_del|ep_season|{aid}")])
        txt = f"🎬 <b>SEASON {sn} — SELECT EPISODE TO REMOVE:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "preview_ep":
        aid, sn, en = parts[2], int(parts[3]), int(parts[4])
        ep = await c.store.get("episodes", ep_id(aid, sn, en))
        if not ep:
            await q_safe(q, "❌ Not found!"); return
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        rows = [
            [btn("🗑️ DELETE THIS EPISODE", f"adm_del|do_delete_ep|{aid}|{sn}|{en}")],
            [btn("❌ CANCEL / BACK", f"adm_del|ep_list|{aid}|{sn}")]
        ]
        fids = ep.get("file_ids") or ([ep["file_id"]] if ep.get("file_id") else [])
        txt = (f"🔍 <b>EPISODE PREVIEW & CONFIRM:</b>\n\n"
               f"📺 Anime: <b>{hesc(title)}</b>\n"
               f"📚 Season: <b>{sn}</b> | Episode: <b>{en}</b>\n"
               f"📁 Video files: <b>{len(fids)}</b>\n"
               f"📝 Caption: {(ep.get('caption') or '—')[:80]}")
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "do_delete_ep":
        aid, sn, en = parts[2], int(parts[3]), int(parts[4])
        await do_delete(c, q.message.chat.id, aid, sn, en)
        await q_safe(q, f"🗑️ Deleted S{sn} E{en}")

async def cb_adm_list_menu(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "list"):
        await q_safe(q, "❌ NO LIST PERMISSION!"); return
    act = parts[1]
    if act == "menu":
        animes = c.store.find("animes")
        animes.sort(key=lambda x: x.get("title", "").lower())
        rows = []
        for a in animes:
            rows.append([btn(a.get("title", "Anime"), f"adm_list|detail|{a['_id']}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", "pan|refresh")])
        txt = "📋 <b>ADMIN ANIME LIST — CLICK ANIME FOR DETAILS:</b>"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "detail":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid]
        seasons = {}
        for ep in eps:
            seasons.setdefault(ep["season"], []).append(ep["episode"])
        txt = f"📺 <b>{hesc(title)}</b>\n━━━━━━━━━━━━━━\n"
        if not seasons:
            txt += "\n📭 No episodes uploaded yet."
        else:
            for s in sorted(seasons):
                eps_sorted = sorted(seasons[s])
                eps_str = ", ".join(f"E{e}" for e in eps_sorted)
                txt += f"\n🟣 <b>Season {s}</b>\n   ▸ {eps_str}\n"
        rows = [[btn("🔙 ʙᴀᴄᴋ", "adm_list|menu")]]
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass

async def cmd_edit(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "edit"):
        await m.reply("❌ <b>NO EDIT PERMISSION!</b>", parse_mode=PM_HTML); return
    await show_admin_edit_menu(c, m.chat.id)

async def cmd_delete(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "delete"):
        await m.reply("❌ <b>NO DELETE PERMISSION!</b>", parse_mode=PM_HTML); return
    await show_admin_delete_menu(c, m.chat.id)

async def do_delete(c, chat_id, aid, s, e):
    ep = await c.store.get("episodes", ep_id(aid, s, e))
    if not ep:
        await c.send_message(chat_id, f"❌ S{s} E{e} not found for this anime!", parse_mode=PM_HTML); return
    await c.store.delete("episodes", ep_id(aid, s, e))
    await log_event(c, "🗑️ ᴇᴘɪꜱᴏᴅᴇ ᴅᴇʟᴇᴛᴇᴅ", f"{aid} S{s} E{e}", important=True)
    await c.send_message(chat_id, f"🗑️ <b>Deleted — S{s} E{e}</b>", parse_mode=PM_HTML)

# ─────────── ʙʀᴏᴀᴅᴄᴀꜱᴛ ───────────
async def copy_any(c, chat_id, m):
    if m.text:
        return await c.send_message(chat_id, m.text, entities=m.entities, parse_mode=PM_OFF,
                                    link_preview_options=LPO_DISABLE)
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
    raise ValueError("Unsupported Media")

async def edit_progress(msg, done, total, ok, fail):
    try:
        await msg.edit_text(f"📣 <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ʀᴜɴɴɪɴɢ...</b>\n━━━━━━━━━━━━━━\n"
                            f"👥 Total: <b>{total}</b>\n📡 Sent: <b>{done}/{total}</b>\n"
                            f"✅ Success: <b>{ok}</b>\n❌ Failed: <b>{fail}</b>", parse_mode=PM_HTML)
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
                await m.reply("❌ No users found."); return
        elif scope.isdigit():
            bid = int(scope)
            cl = RUNNING.get(bid)
            if not cl:
                await m.reply(f"🔴 Bot {bid} not running — use /restart"); return
            plan = [(cl, f"@{cl.username}")]
        else:
            if not await perm_ok(c, uid, "broadcast"):
                await m.reply("❌ <b>NO BROADCAST PERMISSION!</b>", parse_mode=PM_HTML); return
            plan = [(c, f"@{c.username}")]
    else:
        if not await perm_ok(c, uid, "broadcast"):
            await m.reply("❌ <b>NO BROADCAST PERMISSION!</b>", parse_mode=PM_HTML); return
        plan = [(c, f"@{c.username}")]
    if src is None:
        await m.reply("📣 Reply to any message with <code>/broadcast</code>", parse_mode=PM_HTML); return
    status = await m.reply("📣 <b>Starting broadcast...</b>", parse_mode=PM_HTML)
    await log_event(c, "📣 ʙʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴛᴀʀᴛᴇᴅ", f"By: {uid} | Scope: {', '.join(x[1] for x in plan)}",
                    important=True, uid=uid)
    total = sum(cl.store.count("users") for cl, _ in plan)
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
                               f"👥 Total: <b>{total}</b>\n✅ Success: <b>{ok}</b>\n"
                               f"❌ Failed: <b>{fail}</b>\n🎯 Rate: <b>{(ok/total*100 if total else 0):.1f}%</b>",
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
    animes_cnt = store.count("animes")
    eps = store.count("episodes")
    seasons_cnt = len({f"{v.get('anime_id')}:{v.get('season')}" for v in store.c("episodes").values() if "season" in v})
    admins = store.count("admins")
    bcs = store.count("broadcast_logs")
    meta = FACTORY.get_sync("bots", c.bot_id) if FACTORY else None
    created = dt(meta["created_at"]) if meta else dt(cfg(store).get("created_at", START_TS))
    return (f"📊 <b>ʙᴏᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ</b>\n━━━━━━━━━━━━━━\n"
            f"🤖 Bot: @{c.username}\n"
            f"👥 Users: <b>{users}</b>\n"
            f"🆕 Today's Users: <b>{today}</b>\n"
            f"📺 Total Animes: <b>{animes_cnt}</b>\n"
            f"📚 Total Seasons: <b>{seasons_cnt}</b>\n"
            f"🎬 Total Episodes: <b>{eps}</b>\n"
            f"💾 DB Size: <b>{human_size(store_db_size(store))}</b>\n"
            f"🗄️ Storage Used: <b>{human_size(store.size())}</b>\n"
            f"⏱️ Uptime: <b>{hms(now() - START_TS)}</b>\n"
            f"📅 Created: {created}\n"
            f"🛡️ Admins: <b>{admins}</b>\n"
            f"📣 Broadcasts: <b>{bcs}</b>")

def build_global_stats():
    tb = FACTORY.count("bots") if FACTORY else 0
    tu = ta = ts = te = today = 0
    for st in [FACTORY] + list(STORES.values()):
        if st is None: continue
        tu += st.count("users")
        ta += st.count("animes")
        te += st.count("episodes")
        ts += len({f"{v.get('anime_id')}:{v.get('season')}" for v in st.c("episodes").values() if "season" in v})
        today += sum(1 for u in st.c("users").values() if u.get("started_at", 0) >= DAY_START())
    size = sum(os.path.getsize(os.path.join(DB_DIR, f)) for f in os.listdir(DB_DIR)
               if f.endswith(".json")) if os.path.isdir(DB_DIR) else 0
    return (f"🌐 <b>ꜱᴜᴘʀᴇᴍᴇ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ</b>\n━━━━━━━━━━━━━━\n"
            f"🤖 Total Bots: <b>{tb}</b> (🟢 {len(RUNNING) - 1 if FACTORY_CLIENT else len(RUNNING)} running)\n"
            f"👥 Total Users: <b>{tu}</b>\n"
            f"📺 Total Animes: <b>{ta}</b>\n"
            f"📚 Total Seasons: <b>{ts}</b>\n"
            f"🎬 Total Episodes: <b>{te}</b>\n"
            f"🆕 Today's Users: <b>{today}</b>\n"
            f"💾 Storage: <b>{human_size(size)}</b>\n"
            f"⏱️ Uptime: <b>{hms(now() - START_TS)}</b>")

async def cmd_stats(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "stats"):
        await m.reply("❌ <b>NO STATS PERMISSION!</b>", parse_mode=PM_HTML); return
    if c.is_factory and is_supreme(uid):
        await m.reply(build_global_stats(), parse_mode=PM_HTML)
    else:
        await m.reply(build_bot_stats(c), parse_mode=PM_HTML)

async def cmd_list(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "list"):
        await m.reply("❌ <b>NO LIST PERMISSION!</b>", parse_mode=PM_HTML); return
    animes = c.store.find("animes")
    animes.sort(key=lambda x: x.get("title", "").lower())
    if not animes:
        await m.reply("📭 No animes uploaded yet.", parse_mode=PM_HTML); return
    text = "📺 <b>ᴀɴɪᴍᴇ ʟɪꜱᴛ</b>\n━━━━━━━━━━━━━━\n\n"
    for a in animes:
        text += f"• <b>{hesc(a.get('title'))}</b>\n"
    text += "\n🔍 <b>Send /listsearch to search uploaded season and episode list for any anime!</b>"
    for part in chunk(text):
        try: await m.reply(part, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError: pass
        await asyncio.sleep(0.3)

async def cmd_listsearch(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "list"):
        await m.reply("❌ <b>NO LIST PERMISSION!</b>", parse_mode=PM_HTML); return
    query = " ".join(m.command[1:]).strip()
    if query:
        await show_anime_content_list(c, m.chat.id, query)
        return
    set_sess(c, uid, "listsearch_title")
    await m.reply("🔍 <b>Send the Anime Name to view uploaded seasons and episodes:</b>", parse_mode=PM_HTML)

async def show_anime_content_list(c, chat_id, query):
    query_clean = query.strip().lower()
    animes = c.store.find("animes")
    matched = None
    for a in animes:
        if a.get("title", "").strip().lower() == query_clean:
            matched = a
            break
    if not matched:
        for a in animes:
            if query_clean in a.get("title", "").strip().lower():
                matched = a
                break
    if not matched:
        await c.send_message(chat_id, f"❌ <b>No anime found matching:</b> <code>{hesc(query)}</code>", parse_mode=PM_HTML)
        return
    aid = matched["_id"]
    title = matched.get("title", "Anime")
    eps = [v for v in c.store.c("episodes").values() if v.get("anime_id") == aid]
    seasons = {}
    for ep in eps:
        seasons.setdefault(ep["season"], []).append(ep["episode"])
    text = f"📺 <b>{hesc(title)} — ꜱᴇᴀꜱᴏɴ & ᴇᴘɪꜱᴏᴅᴇ ʟɪꜱᴛ</b>\n━━━━━━━━━━━━━━\n"
    if not seasons:
        text += "\n📭 No episodes uploaded yet."
    else:
        for s in sorted(seasons):
            eps_sorted = sorted(seasons[s])
            eps_str = ", ".join(f"E{e}" for e in eps_sorted)
            text += f"\n🟣 <b>Season {s}</b>\n   ▸ {eps_str}\n"
    for part in chunk(text):
        try: await c.send_message(chat_id, part, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError: pass
        await asyncio.sleep(0.3)

# ─────────── ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ ───────────
def admin_panel_kb():
    return InlineKeyboardMarkup([
        [btn("🟢 Upload", "pan|upload"), btn("🔵 Edit", "pan|edit"), btn("🔴 Delete", "pan|del")],
        [btn("🟣 Broadcast", "pan|bc"), btn("🟠 Stats", "pan|stats"), btn("⚪ List", "adm_list|menu")],
        [btn("🔐 Force Sub", "pan|fs"), btn("📝 Start Msg", "pan|es"), btn("👥 Admins", "pan|admins")],
        [btn("🧾 Log Channel", "pan|logch"), btn("📢 Official Link", "pan|set_offlink"), btn("🚫 Ban User", "pan|banuser")],
        [btn("🔗 Anime Links", "pan|anlinks"), btn("🔗 Custom Buttons", "pan|cbtn"), btn("🧹 Clear Database", "pan|cleardb")]])

def log_panel_kb():
    return InlineKeyboardMarkup([
        [btn("📥 Set Log Channel", "log|set"), btn("🔴 Disable Log Channel", "log|off")],
        [btn("🔙 ʙᴀᴄᴋ", "pan|refresh")]
    ])

async def show_log_panel(c, chat_id, edit_msg=None):
    st = cfg(c.store)
    lc = st.get("log_channel") or "—"
    txt = (f"🧾 <b>ʟᴏɢ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛᴛɪɴɢꜱ</b>\n━━━━━━━━━━━━━━\n"
           f"📥 Log Channel ID: <code>{lc}</code>\n\n"
           f"🔔 Receive notifications for:\n"
           f"▸ Bot Start\n"
           f"▸ Episode Uploads\n"
           f"▸ Anime & Season Updates")
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=log_panel_kb(), parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=log_panel_kb(), parse_mode=PM_HTML)

async def cmd_admin(c, m):
    uid = m.from_user.id
    doc = await c.store.get("admins", uid)
    if not doc and not is_supreme(uid):
        await m.reply("❌ You're not an admin here."); return
    role = ROLE_NAME.get(doc["role"], doc["role"]) if doc else "👑 Supreme"
    await m.reply(ADMIN_PANEL_TXT.format(uname=c.username, role=role),
                  reply_markup=admin_panel_kb(), parse_mode=PM_HTML)

# ─────────── ᴀᴅᴍɪɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ (ɢɪᴠᴇ/ᴇᴅɪᴛ/ʀᴇᴍ) ───────────
def selector_text(d):
    return (f"👤 <b>{d.get('name','User')}</b> (<code>{d['uid']}</code>)\n"
            f"🏷️ Role: <b>{ROLE_NAME.get(d['role'], d['role'])}</b>\n\n"
            f"🎨 Toggle Permissions → 💾 Save")

def selector_kb(d):
    uid = d["uid"]; perms = set(d["perms"])
    rows = [[btn("🛠 Manager", f"adm|role|{uid}|manager"), btn("⬆️ Uploader", f"adm|role|{uid}|uploader")],
            [btn("📣 Broadcaster", f"adm|role|{uid}|broadcaster"), btn("📊 Analyst", f"adm|role|{uid}|analyst")],
            [btn("⚙️ Custom", f"adm|role|{uid}|custom")]]
    items = list(PERM_LABELS.items())
    for i in range(0, len(items), 2):
        rows.append([btn(("☑️ " if p in perms else "❌ ") + lbl, f"adm|t|{uid}|{p}") for p, lbl in items[i:i + 2]])
    rows.append([btn("💾 Save", f"adm|save|{uid}"), btn("🗑 Remove", f"adm|rem|{uid}")])
    rows.append([btn("⬅️ Back", "pan|admins")])
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
        await m.reply("❌ That user is not an admin."); return
    if exist and exist.get("role") == "owner":
        await m.reply("👑 Clone owner's permissions cannot be changed."); return
    d = {"uid": t, "name": hesc(name or (exist or {}).get("name") or str(t)),
         "perms": list(exist["permissions"]) if exist else [],
         "role": exist["role"] if exist else "custom", "new": exist is None}
    set_sess(c, m.from_user.id, "adm_edit", **d)
    await m.reply(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)

async def cmd_giveadmin(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "manage_admins"):
        await m.reply("❌ <b>NO MANAGE-ADMINS PERMISSION!</b>", parse_mode=PM_HTML); return
    t, name = msg_target(m)
    if not t:
        set_sess(c, uid, "ga_target")
        await m.reply("👤 Reply to user or send ID:\n<code>/giveadmin 123456789 Name</code>",
                      parse_mode=PM_HTML)
        return
    await open_selector(c, m, t, name)

async def cmd_editadmin(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "manage_admins"):
        await m.reply("❌ <b>NO MANAGE-ADMINS PERMISSION!</b>", parse_mode=PM_HTML); return
    t, name = msg_target(m)
    if not t:
        set_sess(c, uid, "ea_target")
        await m.reply("✏️ Reply to admin or send ID:", parse_mode=PM_HTML); return
    await open_selector(c, m, t, name, must_exist=True)

async def cmd_remadmin(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "manage_admins"):
        await m.reply("❌ <b>NO MANAGE-ADMINS PERMISSION!</b>", parse_mode=PM_HTML); return
    t, _ = msg_target(m)
    if not t:
        set_sess(c, uid, "ra_target")
        await m.reply("🗑 Reply to admin or send ID:", parse_mode=PM_HTML); return
    tgt = await c.store.get("admins", t)
    if not tgt:
        await m.reply("❌ Not an admin."); return
    if tgt.get("role") == "owner":
        await m.reply("👑 Clone owner cannot be removed!"); return
    await c.store.delete("admins", t)
    await log_event(c, "🚫 ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ", f"Admin: {t}", important=True, uid=t)
    await m.reply("🗑 <b>Admin removed!</b>", parse_mode=PM_HTML)

async def cmd_ban(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "ban_users"):
        await m.reply("❌ <b>NO BAN PERMISSION!</b>", parse_mode=PM_HTML); return
    t, name = msg_target(m)
    if not t:
        set_sess(c, uid, "ban_target")
        await m.reply("🚫 Reply to user or send ID to ban:\n<code>/ban 123456789</code>", parse_mode=PM_HTML); return
    t_str = str(t)
    if is_supreme(t) or (await c.store.get("admins", t_str)) or (await c.store.get("admins", t)):
        await m.reply("❌ Cannot ban an Admin / Supreme Owner!", parse_mode=PM_HTML); return
    u = await c.store.get("users", t_str) or await c.store.get("users", t) or {"_id": t_str, "first_name": name or t_str, "started_at": now(), "last_seen": now()}
    u["is_banned"] = True
    u["banned_by"] = uid
    u["banned_at"] = now()
    await c.store.put("users", t_str, u)
    await log_event(c, "🚫 ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ", f"User: {t_str}", important=True, uid=uid)
    await m.reply(f"🚫 <b>User {t_str} has been banned!</b>", parse_mode=PM_HTML)

async def cmd_unban(c, m):
    uid = m.from_user.id
    if not await perm_ok(c, uid, "ban_users"):
        await m.reply("❌ <b>NO UNBAN PERMISSION!</b>", parse_mode=PM_HTML); return
    t, _ = msg_target(m)
    if not t:
        set_sess(c, uid, "unban_target")
        await m.reply("🟢 Reply to user or send ID to unban:\n<code>/unban 123456789</code>", parse_mode=PM_HTML); return
    t_str = str(t)
    u = await c.store.get("users", t_str) or await c.store.get("users", t)
    if not u or not u.get("is_banned"):
        await m.reply("ℹ️ User is not banned.", parse_mode=PM_HTML); return
    u["is_banned"] = False
    await c.store.put("users", t_str, u)
    await log_event(c, "🟢 ᴜꜱᴇʀ ᴜɴʙᴀɴɴᴇᴅ", f"User: {t_str}", important=True, uid=uid)
    await m.reply(f"🟢 <b>User {t_str} has been unbanned!</b>", parse_mode=PM_HTML)

async def show_ban_panel(c, chat_id, edit_msg=None):
    banned_users = [u for u in c.store.find("users") if u.get("is_banned")]
    rows = [
        [btn("🚫 Ban User by ID", "banui|ban_prompt"), btn("🟢 Unban User by ID", "banui|unban_prompt")]
    ]
    for u in banned_users[:8]:
        uname = u.get("first_name") or u.get("username") or u["_id"]
        rows.append([btn(f"🟢 Unban {uname[:16]}", f"banui|do_unban|{u['_id']}")])
    rows.append([btn("🔙 ʙᴀᴄᴋ", "pan|refresh")])

    txt = (f"🚫 <b>ʙᴀɴ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴘᴀɴᴇʟ</b>\n━━━━━━━━━━━━━━\n"
           f"👥 Total Banned Users: <b>{len(banned_users)}</b>\n\n"
           f"Select an option or tap on a banned user to unban:")
    kb = InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

async def cb_ban_ui(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "ban_users"):
        await q_safe(q, "❌ NO BAN PERMISSION!"); return
    act = parts[1]
    if act == "ban_prompt":
        set_sess(c, uid, "ban_target")
        await q_safe(q, "🚫 Send User ID")
        try: await q.message.edit_text("🚫 <b>Send User ID to ban:</b>\n\n(or send /cancel)", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "unban_prompt":
        set_sess(c, uid, "unban_target")
        await q_safe(q, "🟢 Send User ID")
        try: await q.message.edit_text("🟢 <b>Send User ID to unban:</b>\n\n(or send /cancel)", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "do_unban":
        t_str = parts[2]
        u = await c.store.get("users", t_str)
        if u:
            u["is_banned"] = False
            await c.store.put("users", t_str, u)
        await q_safe(q, "🟢 User Unbanned!")
        await show_ban_panel(c, None, edit_msg=q.message)

async def show_admins_list(c, chat_id, edit_msg=None):
    docs = c.store.find("admins")
    order = {"owner": 0, "manager": 1, "uploader": 2, "broadcaster": 3, "analyst": 4, "custom": 5}
    docs.sort(key=lambda d: order.get(d.get("role"), 9))
    if not docs:
        txt, kb = "👥 No admins yet.", admin_panel_kb()
    else:
        rows = [[btn(f"{ROLE_NAME.get(d['role'],'⚙️')} {d.get('name','?')[:18]}",
                     f"adm|view|{d['_id']}") for d in docs[i:i + 2]] for i in range(0, len(docs), 2)]
        rows.append([btn("⬅️ Back", "pan|refresh")])
        txt, kb = f"👥 <b>Admins ({len(docs)})</b>\n\nTap to edit permissions:", InlineKeyboardMarkup(rows)
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=kb, parse_mode=PM_HTML)

# ─────────── ꜰᴏʀᴄᴇ-ꜱᴜʙ & ꜱᴇᴛᴛɪɴɢꜱ ───────────
def fs_panel_kb():
    return InlineKeyboardMarkup([
        [btn("🟢 Public Channel", "fs|public"), btn("🔵 Private Request", "fs|private")],
        [btn("🔴 Disable", "fs|off"), btn("🧾 Log Channel", "fs|logch")]])

async def show_fs_panel(c, chat_id, edit_msg=None):
    st = cfg(c.store)
    mode = st.get("fs_mode", "off")
    mtxt = {"off": "🔴 OFF", "public": "🟢 PUBLIC", "private": "🔵 PRIVATE REQUEST"}.get(mode, mode)
    ch = f"@{st['fs_username']}" if st.get("fs_username") else (st.get("fs_channel") or "—")
    txt = (f"🔐 <b>ꜰᴏʀᴄᴇ ꜱᴜʙꜱᴄʀɪʙᴇ</b>\n━━━━━━━━━━━━━━\n"
           f"📊 Status: <b>{mtxt}</b>\n📢 Channel: <code>{ch}</code>\n"
           f"🧾 Log Ch: <code>{st.get('log_channel') or '—'}</code>\n\n"
           "🟢 Public = Membership Check\n🔵 Private = Join Request Auto-Approve")
    if edit_msg is not None:
        try: await edit_msg.edit_text(txt, reply_markup=fs_panel_kb(), parse_mode=PM_HTML)
        except RPCError: pass
    else:
        await c.send_message(chat_id, txt, reply_markup=fs_panel_kb(), parse_mode=PM_HTML)

async def cmd_setfs(c, m):
    if not await perm_ok(c, m.from_user.id, "forcesub"):
        await m.reply("❌ <b>NO FORCE-SUB PERMISSION!</b>", parse_mode=PM_HTML); return
    await show_fs_panel(c, m.chat.id)

async def validate_channel(c, ref):
    if not ref:
        return None
    ref_str = str(ref).strip()
    if "t.me/" in ref_str:
        ref_str = ref_str.split("t.me/")[-1].strip("/")
        if ref_str.startswith("c/"):
            ref_str = ref_str[2:]
            if ref_str.isdigit():
                ref_str = f"-100{ref_str}"

    candidates = []
    if ref_str.lstrip("-").isdigit():
        val = int(ref_str)
        candidates.append(val)
        if val > 0:
            candidates.append(int(f"-100{val}"))
    else:
        if not ref_str.startswith("@") and not ref_str.startswith("http"):
            candidates.append(f"@{ref_str}")
        candidates.append(ref_str)

    chat = None
    for cand in candidates:
        try:
            chat = await c.get_chat(cand)
            if chat:
                break
        except RPCError:
            continue

    if not chat:
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
        await m.reply("❌ <b>CAN'T ACCESS CHANNEL!</b> (Bot must be admin)\nSend again or /cancel", parse_mode=PM_HTML)
        return
    store = c.store
    if mode == "public":
        if not chat.username:
            await m.reply("❌ This is a private channel — use 🔵 Private Mode.", parse_mode=PM_HTML); return
        await set_cfg(store, fs_mode="public", fs_channel=chat.id, fs_username=chat.username)
        await m.reply(f"✅ <b>Public ForceSub ON!</b>\n\n📢 @{chat.username}", parse_mode=PM_HTML)
    else:
        link_str = None
        try:
            res = await c.create_chat_invite_link(chat.id, creates_join_request=True)
            link_str = getattr(res, "invite_link", None) or str(res)
        except RPCError:
            try:
                res = await c.create_chat_invite_link(chat.id)
                link_str = getattr(res, "invite_link", None) or str(res)
            except RPCError:
                try:
                    link_str = await c.export_chat_invite_link(chat.id)
                except RPCError:
                    link_str = getattr(chat, "invite_link", None)
        if not link_str:
            await m.reply("❌ Invite link creation failed — give bot invite permission.", parse_mode=PM_HTML); return
        await set_cfg(store, fs_mode="private", fs_channel=chat.id, fs_link=link_str,
                      fs_username=chat.username or "")
        await m.reply(f"✅ <b>Private Request ForceSub ON!</b>\n\n🔗 Link Ready — Join requests will auto-approve.", parse_mode=PM_HTML)
    await log_event(c, "🔐 ꜰᴏʀᴄᴇ-ꜱᴜʙ ᴄʜᴀɴɢᴇᴅ", f"Mode: {mode} | Chat: {chat.id}", important=True)
    clear_sess(c, m.from_user.id)

async def fs_got_logch(c, m):
    chat = await validate_channel(c, (m.text or "").strip())
    if not chat:
        await m.reply("❌ Bot is not admin / cannot access channel. Send again or /cancel", parse_mode=PM_HTML)
        return
    await set_cfg(c.store, log_channel=chat.id)
    clear_sess(c, m.from_user.id)
    await m.reply(f"🧾 <b>Log Channel Set!</b>\n\n📥 <code>{chat.id}</code>", parse_mode=PM_HTML)
    await log_event(c, "🧾 ʟᴏɢ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛ", f"{chat.id}")

# ─────────── ᴇᴅɪᴛ ꜱᴛᴀʀᴛ ───────────
async def cmd_editstart(c, m):
    if not await perm_ok(c, m.from_user.id, "editstart"):
        await m.reply("❌ <b>NO EDIT-START PERMISSION!</b>", parse_mode=PM_HTML); return
    if len(m.command) > 1 and m.command[1].lower() == "reset":
        await c.store.put("settings", "start", {"type": "text", "text": DEFAULT_START})
        await m.reply("♻️ Start message reset to default!"); return
    set_sess(c, m.from_user.id, "es_media")
    await m.reply("📝 Reply/Send the new start message:\n\n"
                  "▸ Text / Photo / Video / Animation / Document\n"
                  "▸ Vars: {name} {username} {botname}\n"
                  "▸ Reset: /editstart reset",
                  parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)

async def es_got(c, m):
    uid = m.from_user.id
    if m.text and not m.media_group_id:
        await c.store.put("settings", "start", {"type": "text", "text": m.text})
        kind = "Text"
    else:
        mtype, fid, _ = get_media(m)
        if m.photo:
            mtype, fid = "photo", m.photo.file_id
        if not fid:
            await m.reply("❌ Send text or media!", parse_mode=PM_HTML); return
        await c.store.put("settings", "start", {"type": mtype, "text": m.caption or "", "file_id": fid})
        kind = mtype
    clear_sess(c, uid)
    await m.reply(f"✅ <b>Start message updated!</b> ({kind})\n\n⚡ Instantly active!", parse_mode=PM_HTML)
    await log_event(c, "📝 ꜱᴛᴀʀᴛ ᴍꜱɢ ᴇᴅɪᴛᴇᴅ", kind, important=True, uid=uid)

# ─────────── ᴄʟᴏɴᴇ ꜰᴀᴄᴛᴏʀʏ ───────────
async def cmd_clone(c, m):
    uid = m.from_user.id
    ok, fs_kb = await fs_state(c, uid)
    if not ok:
        await unauthorized(c, uid)
        try:
            await m.reply("🔐 <b>ᴀᴄᴄᴇꜱꜱ ʟᴏᴄᴋᴇᴅ!</b>\n\nYou must join the required channel before creating your bot clone. Press ✅ ᴠᴇʀɪꜰʏ after joining.",
                          reply_markup=fs_kb, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError: pass
        return
    s = get_sess(c, uid)
    if s and s.get("step") == "clone_token":
        await m.reply("⏳ Waiting for token — send it or /cancel"); return
    set_sess(c, uid, "clone_token")
    await m.reply(CLONE_PROMPT, reply_markup=InlineKeyboardMarkup([[btn("🔴 ᴄᴀɴᴄᴇʟ", "cl|cancel")]]),
                  parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)

async def clone_token(c, m):
    uid = m.from_user.id
    sess = get_sess(c, uid)
    if not sess or sess.get("step") != "clone_token": return
    tok = (m.text or "").strip()
    if not re.match(r"^\d{6,12}:[A-Za-z0-9_-]{30,}$", tok):
        await m.reply("❌ Invalid token format — send again or /cancel"); return
    pre = int(tok.split(":", 1)[0])
    if FACTORY.get_sync("bots", pre) or (FACTORY_CLIENT and pre == FACTORY_CLIENT.bot_id):
        clear_sess(c, uid)
        await m.reply("⚠️ <b>This bot is already registered!</b>", parse_mode=PM_HTML); return
    st = await m.reply("⏳ Validating token & starting bot...")
    tmp = Client(name=f"cf{now()}", api_id=API_ID, api_hash=API_HASH, bot_token=tok,
                 in_memory=True, sleep_threshold=15)
    try:
        await tmp.start()
    except (AccessTokenInvalid, AccessTokenExpired):
        clear_sess(c, uid)
        await st.edit("❌ Invalid/Revoked token — get a fresh token from @BotFather!"); return
    except Exception as e:
        LOG.error("Clone start failed: %s", e)
        clear_sess(c, uid)
        await st.edit("⚠️ Failed to start bot — try again in a moment."); return
    me = await tmp.get_me()
    if FACTORY_CLIENT and me.id == FACTORY_CLIENT.bot_id:
        await tmp.stop(); clear_sess(c, uid)
        await st.edit("⚠️ This is the Factory Bot itself!"); return
    if FACTORY.get_sync("bots", me.id):
        await tmp.stop(); clear_sess(c, uid)
        await st.edit(f"⚠️ @{me.username} is already registered!"); return
    store = get_store(me.id)
    await ensure_defaults(store)
    await set_cfg(store, owner_id=uid)
    await FACTORY.put("bots", me.id, {"_id": me.id, "username": me.username or str(me.id),
                                      "name": me.first_name or "Bot", "owner_id": uid,
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
                  parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
    await log_event(tmp, "🎉 ᴄʟᴏɴᴇ ᴄʀᴇᴀᴛᴇᴅ", f"Owner: {uid} (@{m.from_user.username})\nBot: @{me.username} ({me.id})",
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
            f"👤 Owner: {hesc(meta.get('owner_name','?'))} (<code>{meta.get('owner_id')}</code>)\n"
            f"👥 Users: {users} | 🎬 Eps: {eps} | 🗄️ {size}\n"
            f"⏰ Last Active: {dt(meta.get('last_active', 0))}\n"
            f"📅 Created: {dt(meta.get('created_at', 0))}")
    if len(lines) == 2:
        lines.append("No clones yet — use /clone to create!")
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
            lines.append(f"🔴 <code>{f}</code> — CORRUPT! ({human_size(size)})")
            continue
        u = len(data.get("users", {})); e = len(data.get("episodes", {}))
        total_users += u; total_eps += e; total_admins += len(data.get("admins", {}))
        for k in data.get("episodes", {}):
            seasons.add(k.split(":")[0])
        colls.update(data.keys())
        lines.append(f"🟢 <code>{f}</code> — 👥{u} 🎬{e} ({human_size(size)})")
    lines.append("━━━━━━━━━━━━━━")
    lines.append(f"🤖 Clones: <b>{FACTORY.count('bots') if FACTORY else 0}</b>")
    lines.append(f"👥 Users: <b>{total_users}</b> | 🎬 Episodes: <b>{total_eps}</b>")
    lines.append(f"📚 Seasons: <b>{len(seasons)}</b> | 🛡️ Admins: <b>{total_admins}</b>")
    lines.append(f"🧾 Collections: <b>{len(colls)}</b>")
    lines.append(f"🧷 Indexes: Keyed-Docs (O(1) Lookup) ✅")
    health = f"{(healthy / len(files) * 100):.0f}%" if files else "100%"
    lines.append(f"💚 DB Health: <b>{health}</b> ({healthy}/{len(files)} files)")
    lines.append(f"💾 Total: <b>{human_size(sum(os.path.getsize(os.path.join(DB_DIR, f)) for f in files))}</b>")
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
        await status_msg.edit_text(f"♻️ <b>Restart Complete!</b>\n\n✅ {okc} | ❌ {fail}", parse_mode=PM_HTML)
    except RPCError:
        pass
    await dev_log(f"♻️ Bots restarted — ✅{okc} ❌{fail}")

async def supreme_panel_kb():
    return InlineKeyboardMarkup([
        [btn("📢 Official Channel Link", "sv|set_offlink"), btn("🤖 Manage Bots", "sv|manage_bots")],
        [btn("🗄️ Database Insights", "sv|db"), btn("📊 Global Stats", "sv|stats")],
        [btn("♻️ Restart Clones", "sv|restart"), btn("🔐 Clone ForceSub", "sv|setfs")],
        [btn("📣 Global Broadcast", "sv|bc_all")]])

async def cmd_supreme(c, m):
    if not is_supreme(m.from_user.id): return
    kb = await supreme_panel_kb()
    await m.reply(f"👑 <b>ꜱᴜᴘʀᴇᴍᴇ ᴘᴀɴᴇʟ</b> (/rajpapa)\n━━━━━━━━━━━━━━\n"
                  f"🤖 Total Bots: <b>{FACTORY.count('bots') if FACTORY else 0}</b>\n"
                  f"🟢 Active Running: <b>{len(RUNNING) - (1 if FACTORY_CLIENT else 0)}</b>\n\n"
                  f"📣 Global Broadcast: <code>/broadcast all</code>\n"
                  f"🎯 Single Bot Broadcast: <code>/broadcast 123456</code>",
                  reply_markup=kb, parse_mode=PM_HTML)

async def cmd_botlist(c, m):
    if not is_supreme(m.from_user.id): return
    for part in chunk(build_botlist_text()):
        try: await m.reply(part, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError: pass
        await asyncio.sleep(0.3)

async def cmd_db(c, m):
    if not is_supreme(m.from_user.id): return
    await m.reply(build_db_report(), parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)

async def cmd_restart(c, m):
    if not is_supreme(m.from_user.id): return
    only = None
    if len(m.command) > 1 and m.command[1].isdigit():
        only = int(m.command[1])
    status = await m.reply("♻️ Gracefully restarting clones...")
    await restart_all(status, only)

# ═════════════════════ ᴄᴀʟʟʙᴀᴄᴋ ʜᴀɴᴅʟᴇʀꜱ ═════════════════════
async def cb_upload(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "upload"):
        await q_safe(q, "❌ NO UPLOAD PERM!"); return
    if parts[0] == "up_q":
        act = "q"
        q_val = parts[1] if len(parts) > 1 and parts[1] != "default" else None
    else:
        act = parts[1] if len(parts) > 1 else ""
        q_val = parts[2] if len(parts) > 2 and parts[2] != "default" else None

    if act == "q":
        s = get_sess(c, uid)
        if not s or "pending_file" not in s["data"]:
            await q_safe(q, "❌ Upload session expired or no video pending!"); return
        d = s["data"]
        aid, sn, en = d["anime_id"], d["season"], d["episode"]
        pf = d.pop("pending_file")
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"

        await save_episode(c, uid, aid, sn, en, pf["fid"], pf["mtype"], pf["caption"], pf["tid"], quality=q_val)
        d["added"] = d.get("added", 0) + 1
        d["episode"] = en + 1

        q_str = f" ({q_val})" if q_val else ""
        await q_safe(q, f"✅ Saved S{sn} E{en}{q_str}")

        kb = InlineKeyboardMarkup([
            [btn(f"➕ Add Another Quality for S{sn} E{en}", f"up|same_ep|{aid}|{sn}|{en}"), btn(f"▶️ Next Ep (E{en + 1})", f"up|next_ep|{aid}|{sn}|{en + 1}")],
            [btn("🏁 Mark Season Ended", f"up_st|seasonend|{aid}|{sn}"), btn("🔔 Mark Coming Soon", f"up_st|coming|{aid}|{sn}")],
            [btn("➕ More Episodes Coming", f"up_st|more_episodes|{aid}|{sn}")],
            [btn("🏁 Finish Upload (/done)", "up|done")]
        ])

        try:
            await q.message.edit_text(f"✅ <b>{hesc(title)} — S{sn} E{en}{q_str} Added!</b>\n\n📤 Send video for Episode {en + 1} or select an option below:",
                                     reply_markup=kb, parse_mode=PM_HTML)
        except RPCError:
            pass
        return
    elif act == "same_ep":
        aid, sn, en = parts[2], int(parts[3]), int(parts[4])
        s = get_sess(c, uid)
        if s: s["data"]["episode"] = en
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        await q_safe(q, f"📤 Send video for S{sn} E{en}")
        try: await q.message.edit_text(f"📤 <b>Send video for another quality of {hesc(title)} — Season {sn} Episode {en}:</b>", parse_mode=PM_HTML)
        except RPCError: pass
        return
    elif act == "next_ep":
        aid, sn, next_en = parts[2], int(parts[3]), int(parts[4])
        s = get_sess(c, uid)
        if s: s["data"]["episode"] = next_en
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        await q_safe(q, f"📤 Send video for S{sn} E{next_en}")
        try: await q.message.edit_text(f"📤 <b>Send video for {hesc(title)} — Season {sn} Episode {next_en}:</b>", parse_mode=PM_HTML)
        except RPCError: pass
        return
    elif act == "add_anime":
        set_sess(c, uid, "up_new_anime_name")
        await q_safe(q, "📝 Send Anime Name")
        try: await q.message.edit_text("📝 <b>Send the name of the new anime:</b>\n\n❌ /cancel", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "sel_anime":
        aid = parts[2]
        await q_safe(q, "📺 Options")
        await show_upload_options(c, q.message.chat.id, aid, edit_msg=q.message)
    elif act == "add_ep":
        aid = parts[2]
        await q_safe(q, "🟢 Add Episode")
        await show_upload_season_select(c, q.message.chat.id, aid, edit_msg=q.message)
    elif act == "sel_ep_season":
        aid, sn = parts[2], int(parts[3])
        eps = [v.get("episode", 0) for v in c.store.c("episodes").values() if v.get("anime_id") == aid and v.get("season") == sn]
        next_ep = (max(eps) + 1) if eps else 1
        set_sess(c, uid, "up_video", anime_id=aid, season=sn, episode=next_ep, added=0)
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        await q_safe(q, f"📤 S{sn} E{next_ep}")
        try: await q.message.edit_text(f"📤 <b>Send video for {hesc(title)} — Season {sn} Episode {next_ep}:</b>\n\nSend video file now...\n🏁 /done • ❌ /cancel", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "new_sea":
        aid = parts[2]
        set_sess(c, uid, "ns_season", anime_id=aid)
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        await q_safe(q, "🆕 New Season")
        try: await q.message.edit_text(f"🆕 <b>Send Season Number for {hesc(title)}</b> (ex: 2):", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "done":
        s = get_sess(c, uid)
        n = s["data"].get("added", 0) if s else 0
        clear_sess(c, uid)
        await q_safe(q, f"🏁 Done — {n} eps!")
        try: await q.message.edit_text(f"🏁 <b>Upload Finished!</b>\n\n✅ {n} episodes added", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "cancel":
        clear_sess(c, uid)
        await q_safe(q, "❌ Cancelled")
        try: await q.message.edit_text("❌ <b>Upload cancelled.</b>", parse_mode=PM_HTML)
        except RPCError: pass

async def cb_edit(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "edit"):
        await q_safe(q, "❌ NO EDIT PERM!"); return
    act, ref = parts[1], parts[2]
    aid, sn_s, en_s = ref.split(":")
    s, e = int(sn_s), int(en_s)
    ep = await c.store.get("episodes", ep_id(aid, s, e))
    if not ep:
        await q_safe(q, "❌ NOT FOUND!"); return
    if act == "video":
        set_sess(c, uid, "ed_video", aid=aid, s=s, e=e)
        await q_safe(q, "🎬 Send New Video")
        try: await q.message.edit_text(f"🎬 <b>S{s} E{e} — Send new video:</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "cap":
        if not await perm_ok(c, uid, "captions"):
            await q_safe(q, "❌ NO CAPTIONS PERM!"); return
        set_sess(c, uid, "ed_cap", aid=aid, s=s, e=e)
        await q_safe(q, "✏️ Send New Caption")
        try: await q.message.edit_text(f"✏️ <b>S{s} E{e} — Send new caption text:</b>\n\nVars: {{season}} {{episode}} {{botname}}", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "thumb":
        if not await perm_ok(c, uid, "thumb"):
            await q_safe(q, "❌ NO THUMB PERM!"); return
        set_sess(c, uid, "ed_thumb", aid=aid, s=s, e=e)
        await q_safe(q, "🖼️ Send Thumb Photo")
        try: await q.message.edit_text(f"🖼️ <b>S{s} E{e} — Send thumbnail photo:</b>\n\n(or send 'remove' to clear)", parse_mode=PM_HTML)
        except RPCError: pass

async def ed_apply(c, m, kind):
    uid = m.from_user.id
    s = get_sess(c, uid); d = s["data"]; aid, sn, en = d["aid"], d["s"], d["e"]
    ep = await c.store.get("episodes", ep_id(aid, sn, en))
    if not ep:
        clear_sess(c, uid); await m.reply("❌ Not found!"); return
    if kind == "video":
        mtype, fid, tid = get_media(m)
        if not fid:
            await m.reply("🎬 <b>Send video file!</b>", parse_mode=PM_HTML); return
        upd = {"file_id": fid, "file_ids": [fid], "qualities": {}, "type": mtype, "updated_at": now()}
        if tid:
            p = ep.get("thumb_path")
            if p and os.path.exists(p):
                try: os.remove(p)
                except OSError: pass
            upd["thumb_id"] = tid
            upd["thumb_path"] = None
        await c.store.update("episodes", ep_id(aid, sn, en), **upd)
        await log_event(c, "✏️ ᴇᴘɪꜱᴏᴅᴇ ᴇᴅɪᴛᴇᴅ", f"{aid} S{sn} E{en} — Video Replaced", important=True, uid=uid)
    elif kind == "cap":
        await c.store.update("episodes", ep_id(aid, sn, en), caption=m.text or "", updated_at=now())
        await log_event(c, "✏️ ᴇᴘɪꜱᴏᴅᴇ ᴇᴅɪᴛᴇᴅ", f"{aid} S{sn} E{en} — Caption Updated", important=True, uid=uid)
    elif kind == "thumb":
        p = ep.get("thumb_path")
        if p and os.path.exists(p):
            try: os.remove(p)
            except OSError: pass
        if (m.text or "").strip().lower() == "remove":
            await c.store.update("episodes", ep_id(aid, sn, en), thumb_id=None, thumb_path=None, updated_at=now())
        else:
            tid = m.photo.file_id if m.photo else (m.video.thumbs[0].file_id if m.video and m.video.thumbs else None)
            if not tid:
                await m.reply("🖼️ Send photo!", parse_mode=PM_HTML); return
            os.makedirs(THUMB_DIR, exist_ok=True)
            path = os.path.join(THUMB_DIR, f"{c.bot_id}_{aid}_{sn}_{en}.jpg")
            try: await c.download_media(tid, file_name=path)
            except Exception: path = None
            await c.store.update("episodes", ep_id(aid, sn, en), thumb_id=tid, thumb_path=path, updated_at=now())
        await log_event(c, "✏️ ᴇᴘɪꜱᴏᴅᴇ ᴇᴅɪᴛᴇᴅ", f"{aid} S{sn} E{en} — Thumb Updated", important=True, uid=uid)
    clear_sess(c, uid)
    await m.reply(f"✅ <b>Updated — S{sn} E{en}</b>\n\n⚡ Instantly effective!",
                  parse_mode=PM_HTML)
    await show_editor(c, m.chat.id, aid, sn, en)

async def cb_panel(c, q, parts):
    uid = q.from_user.id
    act = parts[1]
    checks = {"upload": "upload", "edit": "edit", "del": "delete", "bc": "broadcast",
              "stats": "stats", "list": "list", "fs": "forcesub", "es": "editstart"}
    if act in checks and not await perm_ok(c, uid, checks[act]):
        await q_safe(q, f"❌ NO {checks[act].upper()} PERM!"); return
    if act == "upload":
        await q_safe(q, "⬆️"); set_sess(c, uid, "up_menu")
        await show_upload_menu(c, None, edit_msg=q.message)
    elif act == "edit":
        await q_safe(q, "✏️")
        await show_admin_edit_menu(c, q.message.chat.id, edit_msg=q.message)
    elif act == "del":
        await q_safe(q, "🗑")
        await show_admin_delete_menu(c, q.message.chat.id, edit_msg=q.message)
    elif act == "bc":
        await q_safe(q, "📣")
        try: await q.message.edit_text("📣 <b>Broadcast:</b> Reply to any message with /broadcast", parse_mode=PM_HTML)
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
        try: await q.message.edit_text("📝 <b>Send new start message</b> (text/photo/video)...", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "admins":
        await q_safe(q, "👥"); await show_admins_list(c, None, edit_msg=q.message)
    elif act == "logch":
        await q_safe(q, "🧾 Log Channel"); await show_log_panel(c, None, edit_msg=q.message)
    elif act == "banuser":
        await q_safe(q, "🚫 Ban System"); await show_ban_panel(c, None, edit_msg=q.message)
    elif act == "set_offlink":
        set_sess(c, uid, "pan_offlink_input")
        await q_safe(q, "📢 Send Official Link")
        try: await q.message.edit_text("📢 <b>Send your bot's Official Channel Link (URL):</b>\n\nExample: <code>https://t.me/YourChannel</code>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "anlinks":
        await q_safe(q, "🔗 Anime Links")
        animes = c.store.find("animes")
        animes.sort(key=lambda x: x.get("title", "").lower())
        rows = []
        for a in animes:
            rows.append([btn(a.get("title", "Anime")[:24], f"pan|gen_anlink|{a['_id']}")])
        rows.append([btn("🔙 ʙᴀᴄᴋ", "pan|refresh")])
        txt = "🔗 <b>ANIME REFERRAL LINKS GENERATOR</b>\n━━━━━━━━━━━━━━\nSelect an anime below to get its unique share link:"
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "gen_anlink":
        aid = parts[2]
        anime = await c.store.get("animes", aid)
        title = anime.get("title", "Anime") if anime else "Anime"
        link = f"https://t.me/{c.username}?start=anime_{aid}"
        await q_safe(q, "🔗 Link Generated!")
        txt = (f"🔗 <b>UNIQUE ANIME LINK GENERATED!</b>\n━━━━━━━━━━━━━━\n"
               f"📺 Anime: <b>{hesc(title)}</b>\n\n"
               f"🚀 <b>Shareable Link:</b>\n<code>{link}</code>\n\n"
               f"💡 <i>When users click this link, they will be prompted to join ForceSub (if enabled) and then taken directly to {hesc(title)}!</i>")
        kb = InlineKeyboardMarkup([
            [ubtn("🟢 SHARE LINK", f"https://t.me/share/url?url={quote(link)}&text={quote('🎬 Watch ' + title)}")],
            [btn("🔙 BACK TO ANIME LIST", "pan|anlinks")]
        ])
        try: await q.message.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError: pass
    elif act == "cbtn":
        await q_safe(q, "🔗 Custom Buttons")
        c_btns = (c.store.c("settings").get("custom_buttons") or {}).get("list", [])
        txt = f"🔗 <b>CUSTOM INLINE BUTTONS MANAGER</b>\n━━━━━━━━━━━━━━\n\nTotal Rows Configured: <b>{len(c_btns)}</b>\n\nAdd custom URL buttons to the start message below:"
        rows = [
            [btn("➕ Add 1 Button", "pan|add_cbtn_1"), btn("➕ Add 2 Buttons (1 Row)", "pan|add_cbtn_2")],
            [btn("🗑 Clear All Custom Buttons", "pan|clear_cbtns")],
            [btn("🔙 ʙᴀᴄᴋ", "pan|refresh")]
        ]
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "add_cbtn_1":
        set_sess(c, uid, "cbtn_add_1")
        await q_safe(q, "➕ Send Button Details")
        try: await q.message.edit_text("🔗 <b>Send Button Text & Link in this format:</b>\n\n<code>Button Text | https://t.me/example</code>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "add_cbtn_2":
        set_sess(c, uid, "cbtn_add_2")
        await q_safe(q, "➕ Send 2 Buttons Details")
        try: await q.message.edit_text("🔗 <b>Send 2 Buttons for 1 row in this format:</b>\n\n<code>Text 1 | https://link1.com || Text 2 | https://link2.com</code>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "clear_cbtns":
        await c.store.put("settings", "custom_buttons", {"list": []})
        await q_safe(q, "🗑 Custom Buttons Cleared!")
        try: await q.message.edit_text("✅ <b>All custom buttons removed!</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "cleardb":
        await q_safe(q, "🧹 Clear DB")
        rows = [
            [btn("⚠️ YES, CLEAR DATABASE NOW", "pan|do_cleardb")],
            [btn("❌ CANCEL", "pan|refresh")]
        ]
        txt = ("⚠️ <b>CONFIRM DATABASE DELETION</b>\n━━━━━━━━━━━━━━\n"
               "Are you sure you want to clear this bot's database?\n\n"
               "🔥 <b>All uploaded animes, seasons, episodes, and users will be permanently deleted!</b>")
        try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "do_cleardb":
        if not (is_supreme(uid) or (await c.store.get("admins", uid) or {}).get("role") == "owner"):
            await q_safe(q, "❌ ONLY OWNER CAN CLEAR DATABASE!", alert=True); return
        await delete_bot_db(c.bot_id)
        await q_safe(q, "🧹 Database Cleared!")
        try: await q.message.edit_text("✅ <b>Bot Database has been completely cleared and reset!</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "refresh":
        await q_safe(q, "🔄")
        doc = await c.store.get("admins", uid)
        role = ROLE_NAME.get(doc["role"], doc["role"]) if doc else "👑 Supreme"
        try: await q.message.edit_text(ADMIN_PANEL_TXT.format(uname=c.username, role=role),
                                       reply_markup=admin_panel_kb(), parse_mode=PM_HTML)
        except RPCError: pass

async def send_list_to(c, chat_id):
    seasons = {}
    for k, v in c.store.c("episodes").items():
        seasons.setdefault(v["season"], []).append(v["episode"])
    if not seasons:
        await c.send_message(chat_id, "📭 No episodes yet."); return
    text = "📺 <b>ᴇᴘɪꜱᴏᴅᴇ ʟɪꜱᴛ</b>\n━━━━━━━━━━━━━━\n"
    for s in sorted(seasons):
        text += f"\n🟣 <b>Season {s}</b>\n"
        for e in sorted(seasons[s]):
            text += f"   ▸ Episode {e}\n"
    for part in chunk(text):
        try: await c.send_message(chat_id, part, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError: pass
        await asyncio.sleep(0.3)

async def cb_log(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "manage_admins") and not await perm_ok(c, uid, "forcesub"):
        await q_safe(q, "❌ NO PERMISSION!"); return
    act = parts[1]
    if act == "set":
        set_sess(c, uid, "log_set")
        await q_safe(q, "📥 Send Log Channel")
        try: await q.message.edit_text("🧾 <b>Send Log Channel @username or Chat ID:</b>\n\n(Bot must be an admin in the channel)", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "off":
        await set_cfg(c.store, log_channel=0)
        await q_safe(q, "🔴 Log Channel Disabled!")
        await show_log_panel(c, None, edit_msg=q.message)
        await log_event(c, "🧾 ʟᴏɢ ᴄʜᴀɴɴᴇʟ ᴅɪꜱᴀʙʟᴇᴅ", "Log Channel set to 0", important=True)

async def cb_fs(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "forcesub"):
        await q_safe(q, "❌ NO FS PERM!"); return
    act = parts[1]
    if act == "off":
        await set_cfg(c.store, fs_mode="off")
        await log_event(c, "🔐 ꜰᴏʀᴄᴇ-ꜱᴜʙ ᴄʜᴀɴɢᴇᴅ", "OFF", important=True)
        await q_safe(q, "🔴 ForceSub OFF!")
        await show_fs_panel(c, None, edit_msg=q.message)
    elif act in ("public", "private", "logch"):
        step = {"public": "fs_public", "private": "fs_private", "logch": "fs_logch"}[act]
        set_sess(c, uid, step)
        prompts = {"public": "🟢 <b>Send Public Channel @username or ID:</b>\n(Bot must be admin)",
                   "private": "🔵 <b>Send Private Channel @username or ID:</b>\n(Bot must be admin + invite perm)",
                   "logch": "🧾 <b>Send Log Channel @username or ID:</b>"}
        await q_safe(q, act)
        try: await q.message.edit_text(prompts[act], parse_mode=PM_HTML)
        except RPCError: pass

async def cb_adm(c, q, parts):
    uid = q.from_user.id
    if not await perm_ok(c, uid, "manage_admins"):
        await q_safe(q, "❌ NO MANAGE-ADMINS PERM!"); return
    action = parts[1]; tuid = int(parts[2])
    tgt = await c.store.get("admins", tuid)
    if tgt and tgt.get("role") == "owner" and action in ("t", "role", "rem"):
        await q_safe(q, "👑 Clone owner protected!", True); return
    sess = get_sess(c, uid)
    if sess and sess.get("step") == "adm_edit" and sess["data"].get("uid") == tuid:
        d = sess["data"]
    else:
        d = {"uid": tuid, "name": (tgt or {}).get("name", "User"),
             "perms": list((tgt or {}).get("permissions", [])),
             "role": (tgt or {}).get("role", "custom"), "new": tgt is None}
    if action == "t":
        perm = parts[3]
        if perm in d["perms"]: d["perms"].remove(perm)
        else: d["perms"].append(perm)
        SESSIONS[(c.bot_id, uid)] = {"step": "adm_edit", "data": d}
        await q_safe(q, "✅ Toggled — press Save!")
        try: await q.message.edit_text(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)
        except RPCError: pass
    elif action == "role":
        role = parts[3]
        d["role"] = role; d["perms"] = list(ROLE_PRESETS.get(role, []))
        SESSIONS[(c.bot_id, uid)] = {"step": "adm_edit", "data": d}
        await q_safe(q, f"🎨 {ROLE_NAME.get(role, role)} Preset!")
        try: await q.message.edit_text(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)
        except RPCError: pass
    elif action == "save":
        was_new = tgt is None
        await c.store.put("admins", tuid, {"_id": str(tuid), "name": d.get("name", "User"), "role": d["role"],
                                           "permissions": d["perms"], "added_by": uid, "at": now()})
        await apply_admin_commands(c, tuid)
        SESSIONS.pop((c.bot_id, uid), None)
        await q_safe(q, "💾 Saved! DB updated ✅")
        await log_event(c, "🛡️ ᴀᴅᴍɪɴ ᴀᴅᴅᴇᴅ" if was_new else "🔐 ᴘᴇʀᴍɪꜱꜱɪᴏɴ ᴇᴅɪᴛᴇᴅ",
                        f"Admin: {tuid} | Role: {d['role']} | Perms: {','.join(d['perms']) or '—'}",
                        important=True, uid=tuid)
        d["new"] = False
        try: await q.message.edit_text(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)
        except RPCError: pass
    elif action == "rem":
        await c.store.delete("admins", tuid)
        SESSIONS.pop((c.bot_id, uid), None)
        await q_safe(q, "🗑 Removed!")
        await log_event(c, "🚫 ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ", f"Admin: {tuid}", important=True, uid=tuid)
        try: await q.message.edit_text("🗑 <b>Admin removed.</b>", parse_mode=PM_HTML)
        except RPCError: pass
    elif action == "view":
        if not tgt:
            await q_safe(q, "❌ Not an admin!"); return
        SESSIONS[(c.bot_id, uid)] = {"step": "adm_edit", "data": d}
        await q_safe(q, "👁")
        try: await q.message.edit_text(selector_text(d), reply_markup=selector_kb(d), parse_mode=PM_HTML)
        except RPCError: pass

async def delete_clone_bot(bid):
    meta = FACTORY.get_sync("bots", bid)
    if not meta: return False
    old = RUNNING.pop(bid, None)
    if old:
        try: await old.stop()
        except Exception: pass
    STORES.pop(bid, None)
    cpath = clone_path(bid)
    if os.path.exists(cpath):
        try: os.remove(cpath)
        except OSError: pass
    await FACTORY.delete("bots", bid)
    await dev_log(f"🗑️ ᴄʟᴏɴᴇ ᴅᴇʟᴇᴛᴇᴅ ʙʏ ꜱᴜᴘʀᴇᴍᴇ: @{meta.get('username')} ({bid})")
    return True

async def delete_bot_db(bid):
    st = get_store(bid)
    st.data = {}
    st.flush_soon()
    await ensure_defaults(st)
    meta = FACTORY.get_sync("bots", bid)
    if meta:
        owner_id = meta.get("owner_id")
        if owner_id:
            await set_cfg(st, owner_id=owner_id)
            await st.put("admins", owner_id, {"_id": str(owner_id), "name": meta.get("owner_name", "Owner"),
                                              "role": "owner", "permissions": list(PERMS), "added_by": 0, "at": now()})
    await dev_log(f"🧹 ʙᴏᴛ ᴅᴀᴛᴀʙᴀꜱᴇ ᴄʟᴇᴀʀᴇᴅ: {bid}")

async def show_supreme_bot_list(c, q):
    bots = FACTORY.find("bots") if FACTORY else []
    bots.sort(key=lambda x: x.get("username", "").lower())
    rows = []
    for meta in bots:
        bid = meta["_id"]
        uname = meta.get("username") or str(bid)
        status = "🔴 BANNED" if meta.get("is_banned") else ("🟢 LIVE" if bid in RUNNING else "⚪ OFF")
        rows.append([btn(f"{uname} [{status}]", f"sv|bot_manage|{bid}")])
    rows.append([btn("🔙 Back to Supreme Panel", "sv|panel")])
    txt = f"🤖 <b>SUPREME CLONE BOTS MANAGER ({len(bots)})</b>\n\nSelect a bot to manage (Ban, Unban, Delete Clone, Clear Database):"
    try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
    except RPCError: pass

async def show_bot_control_menu(c, q, bid):
    meta = FACTORY.get_sync("bots", bid)
    if not meta:
        await q_safe(q, "❌ Bot not found!"); return
    st = STORES.get(bid)
    users = st.count("users") if st else 0
    eps = st.count("episodes") if st else 0
    is_b = meta.get("is_banned", False)
    run_s = "🟢 RUNNING" if bid in RUNNING else ("🔴 BANNED" if is_b else "⚪ STOPPED")
    rows = [
        [btn("🟢 UNBAN BOT" if is_b else "🔴 BAN BOT", f"sv|toggle_bot_ban|{bid}")],
        [btn("🧹 CLEAR DB", f"sv|confirm_cleardb|{bid}"), btn("🗑️ DELETE CLONE", f"sv|confirm_delbot|{bid}")],
        [btn("♻️ RESTART BOT", f"sv|restart_one|{bid}")],
        [btn("🔙 Back to Bot List", "sv|manage_bots")]
    ]
    txt = (f"🤖 <b>MANAGE BOT:</b> @{meta.get('username')}\n━━━━━━━━━━━━━━\n"
           f"🆔 Bot ID: <code>{bid}</code>\n"
           f"👤 Owner: {hesc(meta.get('owner_name','?'))} (<code>{meta.get('owner_id')}</code>)\n"
           f"📊 Status: <b>{run_s}</b>\n"
           f"👥 Users: <b>{users}</b> | 🎬 Episodes: <b>{eps}</b>\n"
           f"📅 Created: {dt(meta.get('created_at', 0))}")
    try: await q.message.edit_text(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
    except RPCError: pass

async def cb_supreme(c, q, parts):
    if not is_supreme(q.from_user.id):
        await q_safe(q, "❌ Supreme Only!"); return
    act = parts[1]
    if act == "panel":
        kb = await supreme_panel_kb()
        txt = (f"👑 <b>ꜱᴜᴘʀᴇᴍᴇ ᴘᴀɴᴇʟ</b> (/rajpapa)\n━━━━━━━━━━━━━━\n"
               f"🤖 Total Bots: <b>{FACTORY.count('bots') if FACTORY else 0}</b>\n"
               f"🟢 Active Running: <b>{len(RUNNING) - (1 if FACTORY_CLIENT else 0)}</b>\n\n"
               f"📣 Global Broadcast: <code>/broadcast all</code>\n"
               f"🎯 Single Bot Broadcast: <code>/broadcast 123456</code>")
        try: await q.message.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "manage_bots" or act == "botlist":
        await q_safe(q, "🤖")
        await show_supreme_bot_list(c, q)
    elif act == "bot_manage":
        bid = int(parts[2])
        await show_bot_control_menu(c, q, bid)
    elif act == "toggle_bot_ban":
        bid = int(parts[2])
        meta = FACTORY.get_sync("bots", bid)
        if meta:
            new_b = not meta.get("is_banned", False)
            await FACTORY.update("bots", bid, is_banned=new_b)
            if new_b:
                old = RUNNING.pop(bid, None)
                if old:
                    try: await old.stop()
                    except Exception: pass
                await q_safe(q, "🔴 Bot Banned & Stopped!")
            else:
                await q_safe(q, "🟢 Bot Unbanned! Launching...")
                await launch_clone(meta)
            await show_bot_control_menu(c, q, bid)
    elif act == "confirm_cleardb":
        bid = int(parts[2])
        rows = [[btn("⚠️ YES, CLEAR DB NOW", f"sv|do_cleardb|{bid}")], [btn("❌ CANCEL", f"sv|bot_manage|{bid}")]]
        try: await q.message.edit_text(f"⚠️ <b>Are you sure you want to clear database for bot {bid}?</b>\n\nAll episodes and users will be reset!", reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "do_cleardb":
        bid = int(parts[2])
        await delete_bot_db(bid)
        await q_safe(q, "🧹 Database Cleared!")
        await show_bot_control_menu(c, q, bid)
    elif act == "confirm_delbot":
        bid = int(parts[2])
        rows = [[btn("🔥 YES, DELETE CLONE BOT", f"sv|do_delbot|{bid}")], [btn("❌ CANCEL", f"sv|bot_manage|{bid}")]]
        try: await q.message.edit_text(f"🔥 <b>PERMANENT DELETION:</b>\n\nDelete Clone Bot {bid} and all its data?", reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "do_delbot":
        bid = int(parts[2])
        await delete_clone_bot(bid)
        await q_safe(q, "🗑️ Bot Deleted!")
        await show_supreme_bot_list(c, q)
    elif act == "restart_one":
        bid = int(parts[2])
        await q_safe(q, "♻️ Restarting...")
        await restart_all(q.message, only=bid)
    elif act == "db":
        await q_safe(q, "🗄️")
        try: await q.message.reply(build_db_report(), parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
        except RPCError: pass
    elif act == "stats":
        await q_safe(q, "📊")
        try: await q.message.reply(build_global_stats(), parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "restart":
        await q_safe(q, "♻️ Restarting...")
        await restart_all(q.message)
    elif act == "set_offlink":
        set_sess(c, q.from_user.id, "sv_offlink_input")
        await q_safe(q, "📢 Send Official Link")
        try: await q.message.edit_text("📢 <b>Send Global Official Channel Link (URL):</b>\n\nExample: <code>https://t.me/YourOfficialChannel</code>", parse_mode=PM_HTML)
        except RPCError: pass
    elif act == "setfs":
        await q_safe(q, "🔐 Force Sub")
        await show_fs_panel(c, None, edit_msg=q.message)
    elif act == "bc_all":
        await q_safe(q, "📣")
        try: await q.message.reply("📣 <b>To broadcast to ALL clones:</b>\nReply to any message with <code>/broadcast all</code>", parse_mode=PM_HTML)
        except RPCError: pass

# ─────────── ᴍᴀꜱᴛᴇʀ ᴄᴀʟʟʙᴀᴄᴋ ───────────
async def h_callback(c, q):
    try:
        if not q.from_user:
            try: await q.answer()
            except RPCError: pass
            return
        uid = q.from_user.id
        if await is_user_banned(c, uid):
            await q_safe(q, "❌ You are banned from using this bot!", alert=True)
            return
        data = q.data or ""
        if data == "ckfs":
            ok, kb = await fs_state(c, uid)
            if ok:
                await q_safe(q, "✅ Verified!")
                user = await c.store.get("users", uid) or await ensure_user(c, q.from_user)
                await convert_referral(c, uid)
                try: await q.message.delete()
                except RPCError: pass
                user_doc = await c.store.get("users", str(uid))
                pending_anime = user_doc.get("pending_anime") if user_doc else None
                if pending_anime:
                    await c.store.update("users", str(uid), pending_anime=None)
                    await show_user_season_list(c, uid, pending_anime)
                else:
                    await send_start_content(c, uid, user)
            else:
                await unauthorized(c, uid)
                await q_safe(q, "❌ Still not verified — join channel first!")
        elif data == "usr|home":
            await q_safe(q, "🏠 Home")
            user = await c.store.get("users", uid) or await ensure_user(c, q.from_user)
            await send_start_content(c, uid, user, edit_msg=q.message)
        elif data == "usr|anime_list" or data.startswith("usr|anime_list|"):
            parts = data.split("|")
            page = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 1
            await q_safe(q, "📺 Anime List")
            await show_user_anime_list(c, uid, page=page, edit_msg=q.message)
        elif data == "usr|search_anime":
            set_sess(c, uid, "usr_search_anime")
            await q_safe(q, "🔍 Search Anime")
            kb = InlineKeyboardMarkup([[btn("🔙 ʙᴀᴄᴋ", "usr|anime_list")]])
            try:
                await q.message.edit_text("🔍 <b>Send the name or keyword of the anime to search:</b>", reply_markup=kb, parse_mode=PM_HTML)
            except RPCError:
                await c.send_message(uid, "🔍 <b>Send the name or keyword of the anime to search:</b>", reply_markup=kb, parse_mode=PM_HTML)
        elif data.startswith("usr|anime|"):
            aid = data.split("|")[2]
            await q_safe(q, "📚 Season List")
            await show_user_season_list(c, uid, aid, edit_msg=q.message)
        elif data.startswith("usr|season|"):
            parts = data.split("|")
            aid, sn = parts[2], int(parts[3])
            page = int(parts[4]) if len(parts) > 4 and parts[4].isdigit() else 1
            await q_safe(q, f"🎬 Season {sn}")
            await show_user_episode_list(c, uid, aid, sn, page=page, edit_msg=q.message)
        elif data.startswith("usr|ep|") or data.startswith("usr|ep_q_menu|"):
            parts = data.split("|")
            aid, sn, en = parts[2], int(parts[3]), int(parts[4])
            ep = await c.store.get("episodes", ep_id(aid, sn, en))
            qualities = ep.get("qualities") or {} if ep else {}
            if qualities:
                await q_safe(q, "🎬 Select Quality")
                anime = await c.store.get("animes", aid)
                title = anime.get("title", "Anime") if anime else "Anime"
                avail = [q_k for q_k in ["480p", "720p", "1080p"] if q_k in qualities] or list(qualities.keys())
                q_btns = [btn(f"🎬 {q_k}", f"usr|ep_q|{aid}|{sn}|{en}|{q_k}") for q_k in avail]
                rows = [q_btns, [btn("🔙 ʙᴀᴄᴋ", f"usr|season|{aid}|{sn}")]]
                txt = f"📺 <b>{hesc(title)} • S{sn} E{en}</b>\n━━━━━━━━━━━━━━\n👇 <b>Select Quality / Quality Chunein:</b>"
                kb = InlineKeyboardMarkup(rows)
                try: await q.message.edit_text(txt, reply_markup=kb, parse_mode=PM_HTML)
                except RPCError:
                    try: await c.send_message(uid, txt, reply_markup=kb, parse_mode=PM_HTML)
                    except RPCError: pass
            else:
                await q_safe(q, "▶️ Loading Episode...")
                user = await c.store.get("users", uid)
                await send_episode(c, uid, aid, sn, en, user)
        elif data.startswith("usr|ep_q|"):
            parts = data.split("|")
            aid, sn, en, q_val = parts[2], int(parts[3]), int(parts[4]), parts[5]
            await c.store.update("users", str(uid), pref_quality=q_val)
            await q_safe(q, f"▶️ Loading S{sn} E{en} ({q_val})...")
            user = await c.store.get("users", str(uid))
            await send_episode(c, uid, aid, sn, en, user, req_quality=q_val)
        elif data.startswith("next|"):
            await q_safe(q, "▶️ Loading Next...")
            parts = data.split("|")
            ep_info = parts[1].split(":")
            aid = ep_info[0]
            s, e = int(ep_info[1]), int(ep_info[2])
            req_q = parts[2] if len(parts) > 2 and parts[2] != "default" else None
            user = await c.store.get("users", uid)
            found = await send_episode(c, uid, aid, s, e + 1, user, req_quality=req_q)
            if not found:
                anime = await c.store.get("animes", aid)
                st_map = (anime or {}).get("seasons", {})
                status = st_map.get(str(s), {}).get("status") if isinstance(st_map.get(str(s)), dict) else st_map.get(str(s))
                if status == "seasonend":
                    kb = InlineKeyboardMarkup([
                        [btn("📚 ꜱᴇʟᴇᴄᴛ ɴᴇxᴛ ꜱᴇᴀꜱᴏɴ", f"usr|anime|{aid}")],
                        [btn("🏠 ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", "usr|home")]
                    ])
                    try: await c.send_message(uid, f"🎉 <b>ꜱᴇᴀꜱᴏɴ {s} ᴇɴᴅᴇᴅ!</b>\n\nAll episodes for this season have been uploaded.", parse_mode=PM_HTML, reply_markup=kb)
                    except RPCError: pass
                else:
                    kb = InlineKeyboardMarkup([[btn("🏠 ʙᴀᴄᴋ ᴛᴏ ꜱᴛᴀʀᴛ", "usr|home")]])
                    try: await c.send_message(uid, COMING_SOON, parse_mode=PM_HTML, reply_markup=kb)
                    except RPCError: pass
        elif data.startswith("sea|"):
            await q_safe(q, "📚")
            sn = int(data.split("|")[1])
            eps = sorted(int(k.split(":")[1]) for k in c.store.c("episodes") if k.startswith(f"{sn}:"))
            if eps:
                txt = (f"📚 <b>ꜱᴇᴀꜱᴏɴ {sn}</b>\n\n" + "  ".join(f"ᴇ{x}" for x in eps) +
                       f"\n\n▶️ Send query: <code>S{sn} E{eps[0]}</code>")
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
            await q_safe(q, "🔗 Link sent!")
            try: await c.send_message(uid, f"🔗 <code>{link}</code>", parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
            except RPCError: pass
        elif data == "rf|stats":
            await q_safe(q, "🏆")
            try: await q.message.reply(ranking_text(c.store), parse_mode=PM_HTML)
            except RPCError: pass
        elif data == "cloneme":
            ok, fs_kb = await fs_state(c, uid)
            if not ok:
                await unauthorized(c, uid)
                await q_safe(q, "🔐 Access Locked!", alert=True)
                try: await q.message.reply("🔐 <b>ᴀᴄᴄᴇꜱꜱ ʟᴏᴄᴋᴇᴅ!</b>\n\nYou must join the required channel before creating your bot clone. Press ✅ ᴠᴇʀɪꜰʏ after joining.", reply_markup=fs_kb, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE)
                except RPCError: pass
                return
            set_sess(c, uid, "clone_token")
            await q_safe(q, "🤖 Send Bot Token")
            try: await q.message.reply(CLONE_PROMPT, parse_mode=PM_HTML, link_preview_options=LPO_DISABLE,
                                       reply_markup=InlineKeyboardMarkup([[btn("🔴 ᴄᴀɴᴄᴇʟ", "cl|cancel")]]))
            except RPCError: pass
        elif data == "cl|cancel":
            clear_sess(c, uid)
            await q_safe(q, "❌ Cancelled")
            try: await q.message.edit_text("❌ <b>Clone creation cancelled.</b>", parse_mode=PM_HTML)
            except RPCError: pass
        elif data.startswith("up_st|"):
            parts = data.split("|")
            st_val, aid, sn = parts[1], parts[2], int(parts[3])
            anime = await c.store.get("animes", aid)
            if anime:
                seasons = anime.setdefault("seasons", {})
                s_info = seasons.setdefault(str(sn), {})
                s_info["status"] = st_val
                s_info["updated_at"] = now()
                await c.store.update("animes", aid, seasons=seasons)
            st_labels = {"seasonend": "🏁 Season Ended", "coming": "🔔 Coming Soon", "more_episodes": "➕ More Episodes Coming"}
            label = st_labels.get(st_val, st_val)
            await q_safe(q, f"✅ Season {sn} marked: {label}")
            await log_event(c, "📝 ꜱᴇᴀꜱᴏɴ ꜱᴛᴀᴛᴜꜱ ᴜᴘᴅᴀᴛᴇᴅ", f"Anime: {aid}\nSeason: {sn}\nStatus: {label}", important=True, uid=uid)
            try: await q.message.edit_text(f"✅ <b>Season {sn} status set to: {label}</b>", parse_mode=PM_HTML)
            except RPCError: pass
        elif data.startswith("adm_sel_anime|"):
            aid = data.split("|")[1]
            sess = get_sess(c, uid)
            if sess and sess.get("step") == "status_anime":
                st = sess["data"].get("target_status")
                set_sess(c, uid, "status_season", aid=aid, target_status=st)
                await q_safe(q, "🔢 Send Season Number")
                try: await q.message.edit_text(f"🔢 <b>Send Season Number to mark as {st.upper()}:</b>\n\n(ex: 1)", parse_mode=PM_HTML)
                except RPCError: pass
        elif data.startswith("adm_edit|"):
            await cb_adm_edit_menu(c, q, data.split("|"))
        elif data.startswith("adm_del|"):
            await cb_adm_del_menu(c, q, data.split("|"))
        elif data.startswith("adm_list|"):
            await cb_adm_list_menu(c, q, data.split("|"))
        elif data.startswith("up|") or data.startswith("up_q|"):
            await cb_upload(c, q, data.split("|"))
        elif data.startswith("ed|"):
            await cb_edit(c, q, data.split("|"))
        elif data.startswith("pan|"):
            await cb_panel(c, q, data.split("|"))
        elif data.startswith("fs|"):
            await cb_fs(c, q, data.split("|"))
        elif data.startswith("log|"):
            await cb_log(c, q, data.split("|"))
        elif data.startswith("banui|"):
            await cb_ban_ui(c, q, data.split("|"))
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
        LOG.exception("Callback error")
        await dev_log(f"⚠️ Callback error @{c.username}: {e!r}")

# ═════════════════════ ɢᴇɴᴇʀɪᴄ ᴍꜱɢ (ꜱᴇꜱꜱɪᴏɴꜱ + ᴇᴘɪꜱᴏᴅᴇꜱ) ═════════════════════
async def route_session(c, m, s):
    uid = m.from_user.id
    step = s.get("step")
    if step == "sv_offlink_input" and m.text:
        link = m.text.strip()
        if not link.startswith("http"):
            await m.reply("❌ Send a valid URL starting with http:// or https://", parse_mode=PM_HTML); return
        await set_cfg(FACTORY, official_link=link)
        await FACTORY.put("settings", "official_link", link)
        clear_sess(c, uid)
        await m.reply(f"✅ <b>Global Official Channel Link updated!</b>\n\n📢 <code>{link}</code>", parse_mode=PM_HTML)
    elif step == "pan_offlink_input" and m.text:
        link = m.text.strip()
        if not link.startswith("http"):
            await m.reply("❌ Send a valid URL starting with http:// or https://", parse_mode=PM_HTML); return
        await set_cfg(c.store, official_link=link)
        await c.store.put("settings", "official_link", link)
        clear_sess(c, uid)
        await m.reply(f"✅ <b>Bot Official Channel Link updated!</b>\n\n📢 <code>{link}</code>", parse_mode=PM_HTML)
    elif step == "cbtn_add_1" and m.text:
        parts = [x.strip() for x in m.text.split("|") if x.strip()]
        if len(parts) < 2 or not parts[1].startswith("http"):
            await m.reply("❌ <b>Invalid format!</b> Use: <code>Text | https://link.com</code>", parse_mode=PM_HTML); return
        curr = (c.store.c("settings").get("custom_buttons") or {}).get("list", [])
        curr.append([{"text": parts[0], "url": parts[1]}])
        await c.store.put("settings", "custom_buttons", {"list": curr})
        clear_sess(c, uid)
        await m.reply("✅ <b>Custom button added!</b>", parse_mode=PM_HTML)
    elif step == "cbtn_add_2" and m.text:
        rows_in = [r.strip() for r in m.text.split("||") if r.strip()]
        if len(rows_in) != 2:
            await m.reply("❌ <b>Invalid format!</b> Use: <code>Text 1 | https://link1.com || Text 2 | https://link2.com</code>", parse_mode=PM_HTML); return
        p1 = [x.strip() for x in rows_in[0].split("|") if x.strip()]
        p2 = [x.strip() for x in rows_in[1].split("|") if x.strip()]
        if len(p1) < 2 or len(p2) < 2 or not p1[1].startswith("http") or not p2[1].startswith("http"):
            await m.reply("❌ <b>Invalid format!</b> Links must start with http/https.", parse_mode=PM_HTML); return
        curr = (c.store.c("settings").get("custom_buttons") or {}).get("list", [])
        curr.append([{"text": p1[0], "url": p1[1]}, {"text": p2[0], "url": p2[1]}])
        await c.store.put("settings", "custom_buttons", {"list": curr})
        clear_sess(c, uid)
        await m.reply("✅ <b>Row of 2 custom buttons added!</b>", parse_mode=PM_HTML)
    elif step == "clone_token":
        await clone_token(c, m)
    elif step == "up_new_anime_name":
        title = (m.text or "").strip()
        if not title:
            await m.reply("❌ Send a valid anime name!", parse_mode=PM_HTML); return
        anime = await get_or_create_anime(c.store, title)
        set_sess(c, uid, "up_new_anime_thumb", anime_id=anime["_id"])
        await m.reply(f"🖼️ <b>Send Thumbnail / Banner Image for {hesc(title)}:</b>\n\n(or send /skip to skip image)", parse_mode=PM_HTML)
    elif step == "up_new_anime_thumb":
        d = s["data"]
        aid = d["anime_id"]
        anime = await c.store.get("animes", aid)
        if m.text and m.text.strip().lower() == "/skip":
            fid = None
        elif m.photo:
            fid = m.photo.file_id
        else:
            await m.reply("🖼️ Send a photo or /skip:", parse_mode=PM_HTML); return
        d["banner_file_id"] = fid
        set_sess(c, uid, "up_new_anime_cap", **d)
        await m.reply("📝 <b>Send Caption / Description for this Anime:</b>\n\n(or send /skip to skip caption)", parse_mode=PM_HTML)
    elif step == "up_new_anime_cap":
        d = s["data"]
        aid = d["anime_id"]
        cap = "" if (m.text and m.text.strip().lower() == "/skip") else (m.text or m.caption or "")
        await c.store.update("animes", aid, banner_file_id=d.get("banner_file_id"), banner_caption=cap)
        set_sess(c, uid, "up_new_season_num", anime_id=aid)
        await m.reply("🔢 <b>Send Season Number to add (ex: 1):</b>", parse_mode=PM_HTML)
    elif step == "up_new_season_num":
        txt = (m.text or "").strip()
        if not txt.isdigit() or not (1 <= int(txt) <= 999):
            await m.reply("🔢 Send a valid season number (ex: 1):", parse_mode=PM_HTML); return
        sn = int(txt)
        d = s["data"]
        d["season"] = sn
        set_sess(c, uid, "up_new_season_thumb", **d)
        await m.reply(f"🖼️ <b>Send Thumbnail / Banner Image for Season {sn}:</b>\n\n(or send /skip to skip)", parse_mode=PM_HTML)
    elif step == "up_new_season_thumb":
        d = s["data"]
        if m.text and m.text.strip().lower() == "/skip":
            fid = None
        elif m.photo:
            fid = m.photo.file_id
        else:
            await m.reply("🖼️ Send a photo or /skip:", parse_mode=PM_HTML); return
        d["season_banner_file_id"] = fid
        set_sess(c, uid, "up_new_season_cap", **d)
        await m.reply(f"📝 <b>Send Caption / Description for Season {d['season']}:</b>\n\n(or send /skip to skip)", parse_mode=PM_HTML)
    elif step == "up_new_season_cap":
        d = s["data"]
        aid = d["anime_id"]
        sn = d["season"]
        cap = "" if (m.text and m.text.strip().lower() == "/skip") else (m.text or m.caption or "")
        anime = await c.store.get("animes", aid)
        if anime:
            seasons = anime.setdefault("seasons", {})
            seasons[str(sn)] = {"banner_file_id": d.get("season_banner_file_id"), "banner_caption": cap, "updated_at": now()}
            await c.store.update("animes", aid, seasons=seasons)
        set_sess(c, uid, "up_video", anime_id=aid, season=sn, episode=1, added=0)
        await m.reply(f"📤 <b>Send Video for Season {sn} Episode 1:</b>\n\nSend videos one by one...\n🏁 Send /done when finished or /cancel", parse_mode=PM_HTML)
    elif step == "edit_anime_banner":
        aid = s["data"]["anime_id"]
        if m.text and m.text.strip().lower() == "remove":
            fid = None
        elif m.photo:
            fid = m.photo.file_id
        else:
            await m.reply("🖼️ Send photo or 'remove':", parse_mode=PM_HTML); return
        await c.store.update("animes", aid, banner_file_id=fid)
        await log_event(c, "📝 ᴀɴɪᴍᴇ ᴜᴘᴅᴀᴛᴇᴅ", f"Anime: {aid}\nAction: Banner Photo Updated", important=True, uid=uid)
        clear_sess(c, uid)
        await m.reply("✅ <b>Anime banner updated!</b>", parse_mode=PM_HTML)
    elif step == "edit_anime_caption":
        aid = s["data"]["anime_id"]
        cap = m.text or m.caption or ""
        await c.store.update("animes", aid, banner_caption=cap)
        await log_event(c, "📝 ᴀɴɪᴍᴇ ᴜᴘᴅᴀᴛᴇᴅ", f"Anime: {aid}\nAction: Caption/Description Updated", important=True, uid=uid)
        clear_sess(c, uid)
        await m.reply("✅ <b>Anime caption updated!</b>", parse_mode=PM_HTML)
    elif step == "edit_season_banner":
        d = s["data"]; aid, sn = d["anime_id"], d["season"]
        if m.text and m.text.strip().lower() == "remove":
            fid = None
        elif m.photo:
            fid = m.photo.file_id
        else:
            await m.reply("🖼️ Send photo or 'remove':", parse_mode=PM_HTML); return
        anime = await c.store.get("animes", aid)
        if anime:
            seasons = anime.setdefault("seasons", {})
            s_dict = seasons.setdefault(str(sn), {})
            s_dict["banner_file_id"] = fid
            s_dict["updated_at"] = now()
            await c.store.update("animes", aid, seasons=seasons)
        await log_event(c, "📝 ꜱᴇᴀꜱᴏɴ ᴜᴘᴅᴀᴛᴇᴅ", f"Anime: {aid}\nSeason: {sn}\nAction: Season Banner Updated", important=True, uid=uid)
        clear_sess(c, uid)
        await m.reply(f"✅ <b>Season {sn} banner updated!</b>", parse_mode=PM_HTML)
    elif step == "edit_season_caption":
        d = s["data"]; aid, sn = d["anime_id"], d["season"]
        cap = m.text or m.caption or ""
        anime = await c.store.get("animes", aid)
        if anime:
            seasons = anime.setdefault("seasons", {})
            s_dict = seasons.setdefault(str(sn), {})
            s_dict["banner_caption"] = cap
            s_dict["updated_at"] = now()
            await c.store.update("animes", aid, seasons=seasons)
        await log_event(c, "📝 ꜱᴇᴀꜱᴏɴ ᴜᴘᴅᴀᴛᴇᴅ", f"Anime: {aid}\nSeason: {sn}\nAction: Season Caption Updated", important=True, uid=uid)
        clear_sess(c, uid)
        await m.reply(f"✅ <b>Season {sn} caption updated!</b>", parse_mode=PM_HTML)
    elif step == "usr_search_anime" and m.text:
        query = m.text.strip().lower()
        clear_sess(c, uid)
        all_animes = c.store.find("animes")
        matched = [a for a in all_animes if query in a.get("title", "").strip().lower()]
        if not matched:
            kb = InlineKeyboardMarkup([[btn("🔍 ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ", "usr|search_anime")], [btn("🔙 ʙᴀᴄᴋ", "usr|anime_list")]])
            await m.reply(f"❌ <b>No anime found matching:</b> <code>{hesc(m.text)}</code>", reply_markup=kb, parse_mode=PM_HTML)
            return
        rows = []
        for i in range(0, len(matched[:10]), 2):
            pair = matched[i:i + 2]
            rows.append([btn(a.get("title", "Anime")[:18], f"usr|anime|{a['_id']}") for a in pair])
        rows.append([btn("🔍 ꜱᴇᴀʀᴄʜ ᴀɢᴀɪɴ", "usr|search_anime"), btn("🔙 ʙᴀᴄᴋ", "usr|anime_list")])
        txt = f"🔍 <b>ꜱᴇᴀʀᴄʜ ʀᴇꜱᴜʟᴛꜱ ꜰᴏʀ:</b> <code>{hesc(m.text)}</code>\n\nFound <b>{len(matched)}</b> anime:"
        await m.reply(txt, reply_markup=InlineKeyboardMarkup(rows), parse_mode=PM_HTML)
    elif step == "up_video":
        await up_got_video(c, m)
    elif step == "ns_season" and m.text:
        await ns_got_season(c, m)
    elif step == "ns_video":
        await ns_got_video(c, m)
    elif step == "ed_se_input" and m.text:
        pe = parse_episode(m.text)
        if not pe:
            await m.reply(INVALID_FMT, parse_mode=PM_HTML); return
        s, e = pe
        d = s["data"]
        aid = d["anime_id"]
        if not await c.store.get("episodes", ep_id(aid, s, e)):
            await m.reply(f"❌ <b>S{s} E{e} not found for this anime!</b>", parse_mode=PM_HTML); return
        clear_sess(c, uid)
        await show_editor(c, m.chat.id, aid, s, e)
    elif step == "ed_video":
        await ed_apply(c, m, "video")
    elif step == "ed_cap" and m.text:
        await ed_apply(c, m, "cap")
    elif step == "ed_thumb":
        await ed_apply(c, m, "thumb")
    elif step == "del_se_input" and m.text:
        pe = parse_episode(m.text)
        if not pe:
            await m.reply(INVALID_FMT, parse_mode=PM_HTML); return
        s, e = pe
        d = s["data"]
        aid = d["anime_id"]
        clear_sess(c, uid)
        await do_delete(c, m.chat.id, aid, s, e)
    elif step == "es_media":
        await es_got(c, m)
    elif step == "fs_public" and m.text:
        await fs_got_channel(c, m, "public")
    elif step == "fs_private" and m.text:
        await fs_got_channel(c, m, "private")
    elif step == "fs_logch" and m.text:
        await fs_got_logch(c, m)
    elif step == "log_set" and m.text:
        chat = await validate_channel(c, m.text.strip())
        if not chat:
            await m.reply("❌ Bot is not admin / cannot access channel. Send again or /cancel", parse_mode=PM_HTML)
            return
        await set_cfg(c.store, log_channel=chat.id)
        clear_sess(c, uid)
        await m.reply(f"🧾 <b>Log Channel Set!</b>\n\n📥 <code>{chat.id}</code>", parse_mode=PM_HTML)
        await log_event(c, "🧾 ʟᴏɢ ᴄʜᴀɴɴᴇʟ ꜱᴇᴛ", f"{chat.id}", important=True)
    elif step == "status_season" and m.text:
        txt = m.text.strip()
        if not txt.isdigit():
            await m.reply("❌ Send a valid season number (ex: 1):", parse_mode=PM_HTML); return
        sn = txt
        d = s["data"]
        aid = d["aid"]
        st = d["target_status"]
        anime = await c.store.get("animes", aid)
        if anime:
            seasons = anime.setdefault("seasons", {})
            seasons[str(sn)] = {"status": st, "updated_at": now()}
            await c.store.update("animes", aid, seasons=seasons)
        clear_sess(c, uid)
        st_text = "Season Ended 🏁" if st == "seasonend" else "Coming Soon 🔔"
        await log_event(c, "📝 ꜱᴇᴀꜱᴏɴ ꜱᴛᴀᴛᴜꜱ ᴜᴘᴅᴀᴛᴇᴅ", f"Anime: {aid}\nSeason: {sn}\nStatus: {st_text}", important=True, uid=uid)
        await m.reply(f"✅ <b>Season {sn} marked as {st_text}!</b>", parse_mode=PM_HTML)
    elif step == "ga_target" and m.text:
        t, name = msg_target(m)
        if not t and (m.text or "").strip().isdigit():
            t = int(m.text.strip()); name = str(t)
        if not t:
            await m.reply("👤 Send User ID or reply:"); return
        clear_sess(c, uid)
        await open_selector(c, m, t, name)
    elif step == "ea_target" and m.text:
        t, name = msg_target(m)
        if not t and (m.text or "").strip().isdigit():
            t = int(m.text.strip()); name = str(t)
        if not t:
            await m.reply("❌ Send User ID:"); return
        clear_sess(c, uid)
        await open_selector(c, m, t, name, must_exist=True)
    elif step == "ra_target" and m.text:
        t, _ = msg_target(m)
        if not t and (m.text or "").strip().isdigit():
            t = int(m.text.strip())
        if not t:
            await m.reply("❌ Send User ID:"); return
        clear_sess(c, uid)
        tgt = await c.store.get("admins", t)
        if not tgt: await m.reply("❌ Not an admin."); return
        if tgt.get("role") == "owner": await m.reply("👑 Clone owner cannot be removed!"); return
        await c.store.delete("admins", t)
        await log_event(c, "🚫 ᴀᴅᴍɪɴ ʀᴇᴍᴏᴠᴇᴅ", f"Admin: {t}", important=True, uid=t)
        await m.reply("🗑 <b>Admin removed!</b>", parse_mode=PM_HTML)
    elif step == "ban_target" and m.text:
        t, name = msg_target(m)
        if not t and (m.text or "").strip().isdigit():
            t = int(m.text.strip()); name = str(t)
        if not t:
            await m.reply("🚫 Send User ID:"); return
        clear_sess(c, uid)
        if is_supreme(t) or (await c.store.get("admins", t)):
            await m.reply("❌ Cannot ban an Admin / Supreme Owner!", parse_mode=PM_HTML); return
        u = await c.store.get("users", t) or {"_id": str(t), "first_name": name or str(t), "started_at": now(), "last_seen": now()}
        u["is_banned"] = True
        u["banned_by"] = uid
        u["banned_at"] = now()
        await c.store.put("users", t, u)
        await log_event(c, "🚫 ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ", f"User: {t}", important=True, uid=uid)
        await m.reply(f"🚫 <b>User {t} has been banned!</b>", parse_mode=PM_HTML)
    elif step == "unban_target" and m.text:
        t, _ = msg_target(m)
        if not t and (m.text or "").strip().isdigit():
            t = int(m.text.strip())
        if not t:
            await m.reply("🟢 Send User ID:"); return
        clear_sess(c, uid)
        u = await c.store.get("users", t)
        if not u or not u.get("is_banned"):
            await m.reply("ℹ️ User is not banned.", parse_mode=PM_HTML); return
        u["is_banned"] = False
        await c.store.put("users", t, u)
        await log_event(c, "🟢 ᴜꜱᴇʀ ᴜɴʙᴀɴɴᴇᴅ", f"User: {t}", important=True, uid=uid)
        await m.reply(f"🟢 <b>User {t} has been unbanned!</b>", parse_mode=PM_HTML)

async def h_generic(c, m):
    try:
        if not m.from_user: return
        uid = m.from_user.id
        if await is_user_banned(c, uid):
            try: await m.reply("❌ <b>You are banned from using this bot!</b>", parse_mode=PM_HTML)
            except RPCError: pass
            return
        s = get_sess(c, uid)
        if s:
            await route_session(c, m, s); return
        if m.text and not m.text.startswith("/"):
            user = await c.store.get("users", str(uid))
            await send_start_content(c, m.chat.id, user)
    except FloodWait as f:
        await asyncio.sleep(f.value)
    except Exception as e:
        LOG.exception("Generic error")
        await dev_log(f"⚠️ Error @{c.username}: {e!r}")

# ═════════════════════ ᴄᴏᴍᴍᴀɴᴅ ᴅɪꜱᴘᴀᴛᴄʜᴇʀ ═════════════════════
CMD_MAP = {
    "start": cmd_start, "help": cmd_help, "refer": cmd_refer,
    "upload": cmd_upload, "edit": cmd_edit, "delete": cmd_delete, "broadcast": cmd_broadcast,
    "stats": cmd_stats, "list": cmd_list, "listsearch": cmd_listsearch, "admin": cmd_admin, "setfs": cmd_setfs,
    "editstart": cmd_editstart, "giveadmin": cmd_giveadmin, "editadmin": cmd_editadmin,
    "remadmin": cmd_remadmin, "ban": cmd_ban, "unban": cmd_unban,
    "seasonend": lambda c, m: cmd_seasonend(c, m), "coming": lambda c, m: cmd_coming(c, m),
    "done": cmd_done, "cancel": cmd_cancel,
    "clone": cmd_clone, "rajpapa": cmd_supreme, "supreme": cmd_supreme, "botlist": cmd_botlist,
    "db": cmd_db, "restart": cmd_restart,
}

async def h_admin_cmds(c, m):
    try:
        uid = m.from_user.id if m.from_user else 0
        if uid and await is_user_banned(c, uid):
            try: await m.reply("❌ <b>You are banned from using this bot!</b>", parse_mode=PM_HTML)
            except RPCError: pass
            return
        name = m.command[0].lstrip("/").lower()
        if name in FACTORY_ONLY and not c.is_factory and not is_supreme(uid):
            return
        fn = CMD_MAP.get(name)
        if fn:
            await fn(c, m)
    except FloodWait as f:
        await asyncio.sleep(f.value)
    except Exception as e:
        LOG.exception("Command error %s", name if 'name' in dir() else '?')
        await dev_log(f"⚠️ Command error @{c.username}: {e!r}")
        try: await m.reply("⚠️ Error — try again.")
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
            u = {"_id": str(uid), "first_name": "User", "username": "", "started_at": now(),
                 "last_seen": now(), "fs_verified": True}
            await c.store.put("users", uid, u)
        await c.store.update("users", uid, fs_verified=True, fs_request=True)
        ap = getattr(c, "approve_chat_join_request", None)
        if ap:
            try: await ap(req.chat_id, uid)
            except RPCError: pass
        await convert_referral(c, uid)
        await log_event(c, "✅ ꜰꜱ ʀᴇQᴜᴇꜱᴛ ᴀᴘᴘʀᴏᴠᴇᴅ", f"User: {uid}", uid=uid)
        try:
            await c.send_message(uid, "✅ <b>ᴀᴄᴄᴇꜱꜱ ᴀᴘᴘʀᴏᴠᴇᴅ!</b>\n\n▶️ Now send: S1 E1 or Anime Keyword", parse_mode=PM_HTML)
        except RPCError:
            pass
    except Exception as e:
        LOG.exception("Join request error")
        await dev_log(f"⚠️ Join request error: {e!r}")

# ═════════════════════ ʀᴇɢɪꜱᴛʀᴀᴛɪᴏɴ ═════════════════════
F_START = filters.command("start") & filters.private & filters.incoming
F_HELP = filters.command("help") & filters.private & filters.incoming
F_REFER = filters.command("refer") & filters.private & filters.incoming
F_CMD = filters.command(ALL_CMDS) & filters.private & filters.incoming
F_GEN = filters.private & filters.incoming & ~filters.command(ALL_CMDS) & ~filters.service

def register_provider_handlers(c, is_factory):
    c.add_handler(MessageHandler(cmd_start, F_START), 0)
    c.add_handler(MessageHandler(cmd_help, F_HELP), 0)
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
    if meta.get("is_banned"):
        LOG.warning("Clone %s is banned, skipping launch.", bid)
        return None
    try:
        token = dec_token(meta["token_enc"])
    except Exception as e:
        LOG.error("Token decrypt failed %s: %s", bid, e)
        return None
    c = Client(name=f"clone_{bid}", api_id=API_ID, api_hash=API_HASH, bot_token=token,
               in_memory=True, sleep_threshold=15)
    try:
        await c.start()
    except (AccessTokenInvalid, AccessTokenExpired):
        LOG.error("Clone %s token invalid", bid)
        return None
    except Exception as e:
        LOG.error("Clone %s start failed: %s", bid, e)
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
    await log_event(c, "🚀 ʙᴏᴛ ꜱᴛᴀʀᴛᴇᴅ", f"Bot @{me.username} ({bid}) live", important=True)
    LOG.info("🟢 Clone Live: @%s (%s)", me.username, bid)
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
            LOG.info("🗑 Cleanup: @%s (%s)", meta.get("username"), bid)
            old = RUNNING.pop(bid, None)
            if old:
                try: await old.stop()
                except Exception: pass
            STORES.pop(bid, None)
            try: os.remove(st.path)
            except OSError: pass
            await FACTORY.delete("bots", bid)
            await dev_log(f"🗑️ ᴄʟᴏɴᴇ ᴀᴜᴛᴏ-ᴅᴇʟᴇᴛᴇᴅ: @{meta.get('username')} ({bid})\n"
                          f"Users: {users} | Eps: 0 | Inactive: {inactive_days:.1f}d")

async def cleanup_loop():
    while True:
        await asyncio.sleep(CLEANUP_INTERVAL)
        try:
            await run_cleanup()
            for st in STORES.values():
                if st._dirty: await st.flush()
        except Exception as e:
            LOG.exception("Cleanup error")
            await dev_log(f"⚠️ Cleanup error: {e!r}")

# ═════════════════════ ᴍᴀɪɴ ═════════════════════
async def main():
    global FACTORY, FACTORY_CLIENT
    os.makedirs(DB_DIR, exist_ok=True)
    os.makedirs(THUMB_DIR, exist_ok=True)

    if not (API_ID and API_HASH and BOT_TOKEN):
        print("❌ Config incomplete! Fill API_ID / API_HASH / BOT_TOKEN at top of app.py or in environment.")
        return

    FACTORY = Store(os.path.join(DB_DIR, "factory.json"))
    for col in _COLLECTIONS + ["bots", "developer_logs"]:
        FACTORY.c(col)
    await ensure_defaults(FACTORY)
    if SUPREMES:
        await set_cfg(FACTORY, owner_id=SUPREMES[0])
    LOG.info("🗄️ Factory DB Ready — %s", FACTORY.path)

    fc = Client("factory", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN,
                in_memory=True, sleep_threshold=15)
    await fc.start()
    me = await fc.get_me()
    attach(fc, me, FACTORY, is_factory=True)
    FACTORY_CLIENT = fc
    RUNNING[me.id] = fc
    register_provider_handlers(fc, is_factory=True)
    await apply_commands(fc)
    await log_event(fc, "🚀 ʙᴏᴛ ꜱᴛᴀʀᴛᴇᴅ", f"Factory Bot @{me.username} ({me.id}) live", important=True)
    LOG.info("🟢 Factory Live: @%s (%s)", me.username, me.id)
    await dev_log(f"🚀 Factory Started: @{me.username} ({me.id})\n🤖 Restoring clones...")

    okc = fail = 0
    for meta in list(FACTORY.find("bots")):
        cl = await launch_clone(meta)
        if cl: okc += 1
        else: fail += 1
    LOG.info("♻️ Restored Clones — ✅%d ❌%d", okc, fail)

    asyncio.create_task(cleanup_loop())

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try: loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError): pass

    print(f"\n{'═'*55}\n  🏭 {FACTORY_NAME} IS LIVE — @{me.username}\n  🤖 Clones: {len(FACTORY.c('bots'))} | DB: JSON ({DB_DIR}/)\n{'═'*55}\n")
    await stop.wait()

    LOG.info("🛑 Shutting down...")
    await dev_log("🛑 Factory stopped gracefully.")
    for c in list(RUNNING.values()):
        try: await c.stop()
        except Exception: pass
    for st in STORES.values():
        await st.flush()
    await FACTORY.flush()
    LOG.info("✅ Bye!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
