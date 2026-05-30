import os
import json
import uuid
import yt_dlp
import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# ================= CONFIG =================
BOT_TOKEN = ""

CHANNEL = "@socialhublk1"
GROUP = "@SOCIAL_HUB_LK2"

OWNER_ID = 6554061816

ADMIN_FILE = "admins.json"

# ================= LOGGING =================
logging.basicConfig(level=logging.INFO)

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
        "🔥 TikTok | Instagram | Facebook"
    )

def ui_processing():
    return "⏳ Processing your request..."

def ui_done():
    return "✅ Download complete 🎬"

def ui_error():
    return "❌ Failed to download"

def ui_admin():
    return (
        "🛠 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟\n\n"
        "➕ /addadmin <id>\n"
        "➖ /removeadmin <id>\n"
        "👑 /admins\n"
        "📢 /broadcast <msg>"
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
    except:
        return False


# ================= DOWNLOAD =================
def download_video(url):
    filename = f"{uuid.uuid4()}.mp4"

    ydl_opts = {
        "outtmpl": filename,
        "format": "mp4/best",
        "quiet": True,
        "noplaylist": True
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    return filename


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text("❌ Join channel & group first!")
        return

    if "http" not in text:
        await update.message.reply_text("❌ Send valid link")
        return

    # ADS
    await update.message.reply_text("📢 Sponsored: Join @socialhublk1 ⚡")

    # FAKE ANIMATION
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

        await update.message.reply_video(video=open(file, "rb"))

        os.remove(file)

        await update.message.reply_text(ui_done())

    except:
        await update.message.reply_text(ui_error())


# ================= ADMIN PANEL =================
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text(ui_admin())


# ================= ADD ADMIN =================
async def addadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    new_id = int(context.args[0])
    ADMIN_IDS.add(new_id)
    save_admins(ADMIN_IDS)

    await update.message.reply_text("✅ Admin added 👑")


# ================= REMOVE ADMIN =================
async def removeadmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update.effective_user.id):
        return

    rem_id = int(context.args[0])
    ADMIN_IDS.discard(rem_id)
    save_admins(ADMIN_IDS)

    await update.message.reply_text("🗑 Admin removed")


# ================= LIST ADMINS =================
async def admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    await update.message.reply_text(
        "👑 Admin List:\n" + "\n".join(str(x) for x in ADMIN_IDS)
    )


# ================= BROADCAST =================
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    msg = " ".join(context.args)

    await update.message.reply_text(f"📢 Sent:\n{msg}")


# ================= MAIN =================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CommandHandler("addadmin", addadmin))
    app.add_handler(CommandHandler("removeadmin", removeadmin))
    app.add_handler(CommandHandler("admins", admins))
    app.add_handler(CommandHandler("broadcast", broadcast))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))

    print("🚀 BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
