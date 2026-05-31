import os
import json
import uuid
import yt_dlp
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = "8849528575:AAFJByyjdMfpkHqHIf_Rcvt13ZUaVNKe6fw"

CHANNEL = "@socialhublk1"
GROUP = "@SOCIAL_HUB_LK2"

OWNER_ID = 6554061816

ADMIN_FILE = "admins.json"
STATS_FILE = "stats.json"

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ================= STATS SYSTEM =================
def load_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except:
        return {"total_users": 0, "total_downloads": 0, "start_time": str(datetime.now())}

def save_stats(stats):
    with open(STATS_FILE, "w") as f:
        json.dump(stats, f, indent=4)

STATS = load_stats()

# ================= ADMIN SYSTEM =================
def load_admins():
    try:
        with open(ADMIN_FILE, "r") as f:
            return set(json.load(f))
    except:
        return {OWNER_ID, 8171368318, 8538967590}

def save_admins(admins):
    with open(ADMIN_FILE, "w") as f:
        json.dump(list(admins), f)

ADMIN_IDS = load_admins()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_owner(user_id):
    return user_id == OWNER_ID


# ================= UI SYSTEM =================
def ui_start():
    return (
        "✨ 𝗦𝗢𝗖𝗜𝗔𝗟 𝗛𝗨𝗕 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗𝗘𝗥 ✨\n\n"
        "🎬 Send any video link\n"
        "⚡ Fast HD Download\n"
        "🔥 TikTok | Instagram | Facebook | YouTube"
    )

def ui_processing():
    return "⏳ Processing your request..."

def ui_done():
    return "✅ Download complete 🎬"

def ui_error(error_msg=""):
    return f"❌ Failed to download{f': {error_msg}' if error_msg else ''}"

def ui_admin():
    return (
        "🛠 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟\n\n"
        "➕ /addadmin <id>\n"
        "➖ /removeadmin <id>\n"
        "👑 /admins\n"
        "📢 /broadcast <msg>\n"
        "📊 /stats"
    )


# ================= FORCE JOIN =================
async def check_join(bot, user_id):
    try:
        c = await bot.get_chat_member(CHANNEL, user_id)
        g = await bot.get_chat_member(GROUP, user_id)

        return (
            c.status in ["member", "administrator", "creator"] and
            g.status in ["member", "administrator", "creator"]
        )
    except Exception as e:
        logger.error(f"Force join check error: {e}")
        return False


# ================= DOWNLOAD =================
def download_video(url):
    try:
        filename = f"downloads/{uuid.uuid4()}.mp4"
        os.makedirs("downloads", exist_ok=True)

        ydl_opts = {
            "outtmpl": filename,
            "format": "best[ext=mp4]/best",
            "quiet": False,
            "noplaylist": True,
            "socket_timeout": 30,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Downloading: {url}")
            ydl.download([url])

        if os.path.exists(filename):
            logger.info(f"Downloaded: {filename}")
            return filename
        else:
            return None
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return None


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User started: {user.id} - {user.first_name}")
    
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/socialhublk1")],
        [InlineKeyboardButton("👥 Join Group", url=f"https://t.me/SOCIAL_HUB_LK2")]
    ]

    await update.message.reply_text(
        ui_start(),
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================= MESSAGE HANDLER =================
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # FORCE JOIN
    if not await check_join(context.bot, user.id):
        await update.message.reply_text(
            "❌ Please join our channel and group first!\n\n"
            "📢 @socialhublk1\n"
            "👥 @SOCIAL_HUB_LK2"
        )
        return

    if "http" not in text:
        await update.message.reply_text("❌ Please send a valid link")
        return

    # ADS
    await update.message.reply_text("📢 Sponsored: Join @socialhublk1 ⚡")

    # PROCESSING
    msg = await update.message.reply_text("⏳ Processing")
    for i in range(2):
        await asyncio.sleep(1)
        await msg.edit_text("⏳ Processing.")
        await asyncio.sleep(1)
        await msg.edit_text("⏳ Processing..")
        await asyncio.sleep(1)
        await msg.edit_text("⏳ Processing...")

    try:
        file = download_video(text)

        if file and os.path.exists(file):
            await update.message.reply_video(video=open(file, "rb"))
            os.remove(file)
            await update.message.reply_text(ui_done())
            
            # Update stats
            STATS["total_downloads"] += 1
            save_stats(STATS)
            logger.info(f"Download successful for user: {user.id}")
        else:
            await update.message.reply_text(ui_error("Could not download file"))

    except Exception as e:
        error_msg = str(e)[:50]
        await update.message.reply_text(ui_error(error_msg))
        logger.error(f"Handler error for user {user.id}: {e}")


# ================= ADMIN PANEL =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only command")
        return

    await update.message.reply_text(ui_admin())


# ================= ADD ADMIN =================
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Owner only command")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /addadmin <user_id>")
        return

    try:
        new_id = int(context.args[0])
        ADMIN_IDS.add(new_id)
        save_admins(ADMIN_IDS)
        logger.info(f"Admin added: {new_id}")
        await update.message.reply_text(f"✅ Admin {new_id} added 👑")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")


# ================= REMOVE ADMIN =================
async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        await update.message.reply_text("❌ Owner only command")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /removeadmin <user_id>")
        return

    try:
        rem_id = int(context.args[0])
        ADMIN_IDS.discard(rem_id)
        save_admins(ADMIN_IDS)
        logger.info(f"Admin removed: {rem_id}")
        await update.message.reply_text(f"🗑 Admin {rem_id} removed")
    except ValueError:
        await update.message.reply_text("❌ Invalid user ID")


# ================= LIST ADMINS =================
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only command")
        return

    admin_list = "\n".join(str(x) for x in ADMIN_IDS)
    await update.message.reply_text(f"👑 Admin List:\n{admin_list}")


# ================= STATS =================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only command")
        return

    stats_text = (
        f"📊 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗦\n\n"
        f"👥 Total Users: {STATS.get('total_users', 0)}\n"
        f"⬇️ Total Downloads: {STATS.get('total_downloads', 0)}\n"
        f"⏱️ Running Since: {STATS.get('start_time', 'N/A')}\n"
    )
    await update.message.reply_text(stats_text)


# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only command")
        return

    if not context.args:
        await update.message.reply_text("❌ Usage: /broadcast <message>")
        return

    msg = " ".join(context.args)
    await update.message.reply_text(f"📢 Broadcast set:\n{msg}\n\n(Note: Multi-user broadcast requires database)")


# ================= MAIN =================
def main():
    logger.info("🚀 Starting Telegram Bot...")
    
    app = Application.builder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("admins", admins))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))

    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    logger.info("✅ Bot handlers configured")
    print("🚀 BOT RUNNING...")
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    main()
