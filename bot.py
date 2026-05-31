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
DOWNLOAD_DIR = "downloads"

# Create downloads directory if it doesn't exist
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ================= LOGGING =================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ================= STATS SYSTEM =================
def load_stats():
    try:
        with open(STATS_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            "total_users": 0, 
            "total_downloads": 0, 
            "start_time": str(datetime.now())
        }
    except Exception as e:
        logger.error(f"Error loading stats: {e}")
        return {
            "total_users": 0, 
            "total_downloads": 0, 
            "start_time": str(datetime.now())
        }

def save_stats(stats):
    try:
        with open(STATS_FILE, "w") as f:
            json.dump(stats, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving stats: {e}")

STATS = load_stats()

# ================= ADMIN SYSTEM =================
def load_admins():
    try:
        with open(ADMIN_FILE, "r") as f:
            return set(json.load(f))
    except FileNotFoundError:
        default_admins = {OWNER_ID, 8171368318, 8538967590}
        save_admins(default_admins)
        return default_admins
    except Exception as e:
        logger.error(f"Error loading admins: {e}")
        return {OWNER_ID}

def save_admins(admins):
    try:
        with open(ADMIN_FILE, "w") as f:
            json.dump(list(admins), f)
    except Exception as e:
        logger.error(f"Error saving admins: {e}")

ADMIN_IDS = load_admins()

def is_admin(user_id):
    return user_id in ADMIN_IDS

def is_owner(user_id):
    return user_id == OWNER_ID


# ================= UI SYSTEM =================
def ui_start():
    return (
        "✨ SOCIAL HUB DOWNLOADER ✨\n\n"
        "🎬 Send any video link\n"
        "⚡ Fast HD Download\n"
        "🔥 TikTok | Instagram | Facebook | YouTube"
    )

def ui_processing():
    return "⏳ Processing your request..."

def ui_done():
    return "✅ Download complete 🎬"

def ui_error(error_msg=""):
    if error_msg:
        return f"❌ Failed to download: {error_msg}"
    return "❌ Failed to download"

def ui_admin():
    return (
        "🛠 ADMIN PANEL\n\n"
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
        filename = os.path.join(DOWNLOAD_DIR, f"{uuid.uuid4()}.mp4")

        ydl_opts = {
            "outtmpl": filename[:-4],  # Remove .mp4 extension
            "format": "best[ext=mp4]/best",
            "quiet": True,
            "noplaylist": True,
            "socket_timeout": 30,
            "http_headers": {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            logger.info(f"Starting download: {url}")
            info = ydl.extract_info(url, download=True)
            downloaded_file = ydl.prepare_filename(info)
            
            if os.path.exists(downloaded_file):
                logger.info(f"Downloaded successfully: {downloaded_file}")
                return downloaded_file
            else:
                logger.error(f"File not found after download: {downloaded_file}")
                return None
            
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        return None


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    logger.info(f"User started: {user.id} - {user.first_name}")
    
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel", url="https://t.me/socialhublk1")],
        [InlineKeyboardButton("👥 Join Group", url="https://t.me/SOCIAL_HUB_LK2")]
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
    
    try:
        for i in range(2):
            await asyncio.sleep(1)
            await msg.edit_text("⏳ Processing.")
            await asyncio.sleep(1)
            await msg.edit_text("⏳ Processing..")
            await asyncio.sleep(1)
            await msg.edit_text("⏳ Processing...")

        file = download_video(text)

        if file and os.path.exists(file):
            file_size = os.path.getsize(file) / (1024 * 1024)  # Size in MB
            
            if file_size > 2048:  # 2GB limit for Telegram
                await update.message.reply_text(
                    f"❌ File too large ({file_size:.1f}MB). Telegram limit is 2GB"
                )
                os.remove(file)
                return
            
            with open(file, "rb") as video_file:
                await update.message.reply_video(video=video_file)
            
            os.remove(file)
            await update.message.reply_text(ui_done())
            
            # Update stats
            STATS["total_downloads"] += 1
            save_stats(STATS)
            logger.info(f"Download successful for user: {user.id}")
        else:
            await update.message.reply_text(ui_error("Could not download file"))
            logger.warning(f"Download failed for user {user.id}")

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
    except Exception as e:
        logger.error(f"Error adding admin: {e}")
        await update.message.reply_text("❌ Error adding admin")


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
    except Exception as e:
        logger.error(f"Error removing admin: {e}")
        await update.message.reply_text("❌ Error removing admin")


# ================= LIST ADMINS =================
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only command")
        return

    if ADMIN_IDS:
        admin_list = "\n".join(f"• {x}" for x in sorted(ADMIN_IDS))
        await update.message.reply_text(f"👑 Admin List:\n{admin_list}")
    else:
        await update.message.reply_text("👑 No admins found")


# ================= STATS =================
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Admin only command")
        return

    stats_text = (
        f"📊 BOT STATS\n\n"
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
    await update.message.reply_text(f"📢 Broadcast:\n{msg}")


# ================= ERROR HANDLER =================
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Update caused error: {context.error}")


# ================= MAIN =================
def main():
    logger.info("=" * 50)
    logger.info("🚀 Starting Telegram Bot...")
    logger.info("=" * 50)
    
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

    # Error handler
    app.add_error_handler(error_handler)

    logger.info("✅ Bot handlers configured")
    print("\n🚀 BOT RUNNING...\n")
    
    try:
        app.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
        print("\n✅ Bot stopped gracefully")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n❌ Fatal error: {e}")


if __name__ == "__main__":
    main()
