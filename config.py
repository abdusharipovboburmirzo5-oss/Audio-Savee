"""
Configuration module for Instagram Downloader Bot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration settings"""
    
    # Telegram Bot Settings
    BOT_TOKEN = os.getenv('BOT_TOKEN', '').strip()
    
    # Debug token presence (masked)
    import logging
    logger = logging.getLogger(__name__)
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN is EMPTY! Check Hugging Face Secrets.")
    else:
        # Show first 5 and last 5 chars for verification
        logger.info(f"✅ BOT_TOKEN detected: {BOT_TOKEN[:5]}...{BOT_TOKEN[-5:]} (Length: {len(BOT_TOKEN)})")

    ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '')
    REQUIRED_CHANNEL = "@Abdusharipovuz"
    CHANNEL_URL = "https://t.me/Abdusharipovuz"
    
    # Download Settings
    DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR', 'downloads')
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 50000000))  # 50MB default
    
    # Language Settings
    DEFAULT_LANGUAGE = os.getenv('DEFAULT_LANGUAGE', 'uz')
    SUPPORTED_LANGUAGES = ['uz', 'ru', 'en']
    
    # Platform Patterns
    URL_PATTERNS = {
        'instagram': r'https?://(?:www\.)?instagram\.com/(?:p|reel|tv|stories)/[\w-]+/?',
        'tiktok': r'https?://(?:www\.)?tiktok\.com/(?:@[\w.-]+/video/\d+|[\w.-]+)/?',
        'pinterest': r'https?://(?:www\.)?pinterest\.com/pin/\d+/?|https?://pin\.it/[\w-]+',
        'youtube': r'https?://(?:www\.)?(?:youtube\.com/shorts/|youtu\.be/)[\w-]+/?',
    }
    
    # Combined pattern for initial check
    ALL_PATTERNS = [
        r'https?://(?:www\.)?instagram\.com/.*',
        r'https?://(?:www\.)?tiktok\.com/.*',
        r'https?://(?:www\.)?pinterest\.com/pin/.*',
        r'https?://pin\.it/.*',
        r'https?://(?:www\.)?youtube\.com/.*',
        r'https?://youtu\.be/.*',
    ]
    
    # yt-dlp Options
    YT_DLP_OPTIONS = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
        'format': 'best',
        'outtmpl': os.path.join(DOWNLOAD_DIR, '%(id)s.%(ext)s'),
    }
    
    # FFmpeg Options
    FFMPEG_OPTIONS = {
        'audio_codec': 'mp3',
        'audio_bitrate': '192k',
    }
    
    @staticmethod
    def ensure_download_dir():
        """Create download directory if it doesn't exist"""
        if not os.path.exists(Config.DOWNLOAD_DIR):
            os.makedirs(Config.DOWNLOAD_DIR)

# Ensure download directory exists
Config.ensure_download_dir()
