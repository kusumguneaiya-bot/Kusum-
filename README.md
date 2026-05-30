# 🎬 Social Hub Video Downloader Bot

A Telegram bot that downloads videos from TikTok, Instagram, Facebook, and other platforms.

## ✨ Features

- 📥 Download videos from multiple platforms (TikTok, Instagram, Facebook, etc.)
- ⚡ Fast HD quality downloads
- 👑 Admin panel for managing admins
- 📢 Broadcast messages to users
- 🔐 Force join channel and group verification
- 🎨 Beautiful UI with inline buttons

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kusumguneaiya-bot/Kusum-.git
   cd Kusum-
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your:
   - `BOT_TOKEN`: Get it from [@BotFather](https://t.me/botfather) on Telegram
   - `CHANNEL`: Your channel username
   - `GROUP`: Your group username
   - `OWNER_ID`: Your Telegram user ID

4. **Run the bot**
   ```bash
   python bot.py
   ```

## 📋 Commands

### User Commands
- `/start` - Start the bot and see welcome message

### Admin Commands
- `/admin` - Show admin panel
- `/addadmin <id>` - Add new admin (Owner only)
- `/removeadmin <id>` - Remove admin (Owner only)
- `/admins` - List all admins
- `/broadcast <message>` - Broadcast message to users

## 🔧 Configuration

Edit `bot.py` to customize:

```python
BOT_TOKEN = "your_bot_token"        # Get from @BotFather
CHANNEL = "@socialhublk1"           # Your channel
GROUP = "@SOCIAL_HUB_LK2"           # Your group
OWNER_ID = 6554061816               # Your user ID
```

## 🛠 Admin System

- **Owner**: Has full control, can add/remove admins
- **Admins**: Can use admin commands
- **Users**: Can only download videos
- Admin IDs are saved in `admins.json`

## 📦 File Structure

```
Kusum-/
├── bot.py              # Main bot file
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables example
├── admins.json        # Admin list (auto-generated)
└── README.md          # This file
```

## 🌐 Supported Platforms

- TikTok
- Instagram
- Facebook
- YouTube
- Twitter
- And many more (powered by yt-dlp)

## ⚙️ How It Works

1. User sends a video link
2. Bot checks if user joined channel & group
3. Shows fake loading animation
4. Downloads video using yt-dlp
5. Sends video to user
6. Deletes temporary file

## 🔐 Security

- Force join verification
- Admin system for protection
- Owner-only critical commands
- User ID based access control

## 📝 Notes

- Videos are temporarily stored during download
- Large videos may take time to download
- Make sure bot has admin rights in channel/group
- Users must join both channel and group to download

## 🤝 Contributing

Feel free to fork and submit pull requests!

## 📄 License

This project is open source.

## 🆘 Troubleshooting

**Bot doesn't respond:**
- Check if BOT_TOKEN is correct
- Ensure bot has proper permissions
- Check bot is running: `python bot.py`

**Download fails:**
- Check internet connection
- Verify the video URL is valid
- Some platforms may block yt-dlp

**Force join not working:**
- Make sure channel/group usernames are correct
- Bot should be admin in both channel/group
- User must actually join the channel/group

## 📧 Support

For issues, create a GitHub issue or contact the bot owner.

---

**Made with ❤️ by kusumguneaiya-bot**
