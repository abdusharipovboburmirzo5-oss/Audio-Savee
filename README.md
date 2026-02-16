---
title: Audio Save Bot
emoji: 🎵
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
---

# Instagram Downloader Telegram Bot

Professional Instagram content downloader bot similar to @savedinstabot.

## 🌟 Features

- ✅ **Instagram Reels** - Download Reels videos
- ✅ **Posts** - Download photos and videos from posts
- ✅ **Stories** - Download Instagram stories
- ✅ **IGTV** - Download IGTV videos
- ✅ **Audio Extraction** - Extract music/audio from videos as MP3
- ✅ **Profile Pictures** - Download HD profile pictures
- ✅ **Multi-language** - Uzbek, Russian, and English support
- ✅ **Quality Options** - Choose between HD and SD quality
- ✅ **Download History** - Track your downloads

## 📋 Requirements

- Python 3.8 or higher
- FFmpeg (for audio extraction)
- Telegram Bot Token (from @BotFather)

## 🚀 Installation

### 1. Install Python Dependencies

```bash
cd instagram_bot
pip install -r requirements.txt
```

### 2. Install FFmpeg

**Windows:**
1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract the archive
3. Add FFmpeg `bin` folder to your system PATH
4. Verify installation: `ffmpeg -version`

**Alternative (using Chocolatey):**
```bash
choco install ffmpeg
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 3. Configure Bot Token

The `.env` file is already configured with your bot token:
```
BOT_TOKEN=7637789321:AAHp_NpaqCJnlmVmXPh0OtioJme8wDhJ5ZA
ADMIN_CHAT_ID=5657790788
```

## 🎯 Usage

### Start the Bot

```bash
cd instagram_bot
python bot.py
```

### Using the Bot in Telegram

1. Open your bot in Telegram
2. Send `/start` to begin
3. Copy any Instagram link (Reels, Post, Story, IGTV)
4. Paste the link in the chat
5. Choose download format:
   - 🎥 **Video** - Download video file
   - 🎵 **Music** - Extract audio as MP3
   - 📷 **Photo** - Download photo

### Commands

- `/start` - Start the bot and see welcome message
- `/help` - Get help and instructions
- `/language` - Change bot language (Uzbek/Russian/English)

## 📁 Project Structure

```
instagram_bot/
├── bot.py                 # Main bot application
├── config.py             # Configuration settings
├── downloader.py         # Instagram downloader module
├── audio_extractor.py    # Audio extraction module
├── messages.py           # Multi-language messages
├── keyboards.py          # Inline keyboard layouts
├── utils.py              # Utility functions
├── database.py           # User database and statistics
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (your tokens)
├── .env.example          # Environment variables template
└── .gitignore           # Git ignore file
```

## 🔧 Configuration

Edit `.env` file to customize settings:

```env
# Bot Token from @BotFather
BOT_TOKEN=your_bot_token_here

# Your Telegram Chat ID for admin notifications
ADMIN_CHAT_ID=your_chat_id_here

# Download directory
DOWNLOAD_DIR=downloads

# Maximum file size (50MB for Telegram)
MAX_FILE_SIZE=50000000

# Default language (uz/ru/en)
DEFAULT_LANGUAGE=uz
```

## 🌐 Supported Languages

- 🇺🇿 **O'zbekcha** (Uzbek)
- 🇷🇺 **Русский** (Russian)
- 🇬🇧 **English**

## ⚠️ Important Notes

1. **Telegram File Size Limit**: Maximum 50MB per file
2. **Private Accounts**: Can only download from public accounts
3. **FFmpeg Required**: Audio extraction requires FFmpeg to be installed
4. **Instagram Limitations**: Some content may be restricted by Instagram

## 🐛 Troubleshooting

### Bot doesn't start
- Check if bot token is correct in `.env` file
- Make sure all dependencies are installed: `pip install -r requirements.txt`

### Audio extraction fails
- Verify FFmpeg is installed: `ffmpeg -version`
- Make sure FFmpeg is in your system PATH

### Download fails
- Check if the Instagram link is valid and public
- Some content may be geo-restricted or deleted

### File too large error
- Telegram has a 50MB file size limit
- Try downloading shorter videos or lower quality

## 📝 License

This project is for educational purposes only. Please respect Instagram's Terms of Service.

## 🤝 Support

For issues or questions, please check the troubleshooting section above.

## 🎉 Enjoy!

Your Instagram downloader bot is ready to use! Send any Instagram link to start downloading.
