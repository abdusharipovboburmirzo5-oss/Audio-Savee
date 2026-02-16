"""
Utility functions for the Instagram Downloader Bot
"""
import re
import os
import logging
from typing import Optional, Tuple, List
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import httpx
from config import Config

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def is_valid_url(url: str) -> bool:
    """
    Check if URL is matching any supported platform
    """
    for pattern in Config.ALL_PATTERNS:
        if re.search(pattern, url):
            return True
    return False

def extract_instagram_shortcode(url: str) -> Optional[str]:
    """
    Extract shortcode from Instagram URL
    
    Args:
        url: Instagram URL
        
    Returns:
        Shortcode if found, None otherwise
    """
    patterns = [
        r'instagram\.com/(?:p|reel|tv)/([A-Za-z0-9_-]+)',
        r'instagram\.com/stories/[\w.-]+/(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_file_size(filepath: str) -> int:
    """
    Get file size in bytes
    
    Args:
        filepath: Path to file
        
    Returns:
        File size in bytes
    """
    try:
        return os.path.getsize(filepath)
    except Exception as e:
        logger.error(f"Error getting file size: {e}")
        return 0

def is_file_too_large(filepath: str, max_size: int = None) -> bool:
    """
    Check if file exceeds maximum size
    
    Args:
        filepath: Path to file
        max_size: Maximum size in bytes (default from config)
        
    Returns:
        True if file is too large, False otherwise
    """
    if max_size is None:
        max_size = Config.MAX_FILE_SIZE
    
    file_size = get_file_size(filepath)
    return file_size > max_size

def format_file_size(size_bytes: int) -> str:
    """
    Format file size to human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "5.2 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def clean_song_title(title: str) -> str:
    """Clean song title for better search results"""
    # Remove common extra terms in brackets/parentheses
    noise_terms = ['official', 'video', 'music', 'audio', 'hd', '4k', 'lyrics', 'clip', 'mv', 'full', 'version', 'remastered']
    pattern = r'[\(\[][^\]\)]*(?:' + '|'.join(noise_terms) + r')[^\]\)]*[\)\]]'
    title = re.sub(pattern, '', title, flags=re.IGNORECASE)
    # Remove standalone noisy words
    for term in noise_terms:
        title = re.sub(rf'\b{term}\b', '', title, flags=re.IGNORECASE)
    # Remove extra whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def clean_filename(filename: str) -> str:
    """
    Clean filename by removing invalid characters
    
    Args:
        filename: Original filename
        
    Returns:
        Cleaned filename
    """
    # Remove invalid characters
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Limit length
    if len(filename) > 200:
        name, ext = os.path.splitext(filename)
        filename = name[:200-len(ext)] + ext
    return filename

def cleanup_file(filepath: str) -> None:
    """
    Delete file if it exists
    
    Args:
        filepath: Path to file to delete
    """
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Cleaned up file: {filepath}")
    except Exception as e:
        logger.error(f"Error cleaning up file {filepath}: {e}")

async def run_ffmpeg(args: list) -> bool:
    """Run ffmpeg command asynchronously"""
    import asyncio
    try:
        process = await asyncio.create_subprocess_exec(
            'ffmpeg', *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        await process.communicate()
        return process.returncode == 0
    except Exception as e:
        logger.error(f"FFmpeg error: {e}")
        return False

async def mute_video(input_path: str) -> Optional[str]:
    """Mute video by removing audio stream"""
    output_path = input_path.rsplit('.', 1)[0] + "_muted.mp4"
    success = await run_ffmpeg(['-y', '-i', input_path, '-an', '-vcodec', 'copy', output_path])
    return output_path if success and os.path.exists(output_path) else None

async def change_video_speed(input_path: str, speed: float) -> Optional[str]:
    """Change video speed (affects both video and audio)"""
    output_path = input_path.rsplit('.', 1)[0] + f"_speed_{speed}.mp4"
    # pts_factor = 1/speed
    # tempo = speed
    pts = 1.0 / speed
    tempo = speed
    
    # ffmpeg filters for speed
    v_filter = f"setpts={pts}*PTS"
    a_filter = f"atempo={tempo}"
    
    # Handle multiple atempo if speed is out of [0.5, 2.0] range
    if tempo > 2.0:
        a_filter = ",".join([f"atempo=2.0"] * int(tempo // 2) + ([f"atempo={tempo%2}"] if tempo%2 > 0.5 else []))
    elif tempo < 0.5:
        a_filter = "atempo=0.5,atempo=0.5" # 0.25x example
        
    success = await run_ffmpeg([
        '-y', '-i', input_path, 
        '-filter_complex', f"[0:v]{v_filter}[v];[0:a]{a_filter}[a]", 
        '-map', '[v]', '-map', '[a]', output_path
    ])
    return output_path if success and os.path.exists(output_path) else None

async def convert_to_voice(input_path: str) -> Optional[str]:
    """Convert audio/video to Telegram voice message (opus/ogg)"""
    output_path = input_path.rsplit('.', 1)[0] + ".ogg"
    success = await run_ffmpeg([
        '-y', '-i', input_path, 
        '-acodec', 'libopus', '-b:a', '32k', '-vbr', 'on', 
        '-compression_level', '10', output_path
    ])
    return output_path if success and os.path.exists(output_path) else None

def get_content_type(url: str) -> str:
    """
    Determine content type and platform
    """
    if 'instagram.com' in url:
        if '/reel/' in url: return 'reel'
        if '/p/' in url: return 'post'
        if '/stories/' in url: return 'story'
        return 'instagram'
    elif 'tiktok.com' in url:
        return 'tiktok'
    elif 'pinterest.com' in url or 'pin.it' in url:
        return 'pinterest'
    elif 'youtube.com' in url or 'youtu.be' in url or 'youtube.be' in url:
        return 'youtube'
    elif 'facebook.com' in url or 'fb.watch' in url:
        return 'facebook'
    return 'video'

async def generate_lyrics_card(text: str, title: str, artist: str) -> Optional[str]:
    """Generate a beautiful image with lyrics using Pillow"""
    try:
        # Create image with gradient background
        width, height = 1080, 1350
        image = Image.new('RGB', (width, height), (30, 30, 30))
        draw = ImageDraw.Draw(image)
        
        # Add a subtle gradient or background color
        for i in range(height):
            r = int(30 + (i / height) * 40)
            g = int(30 + (i / height) * 20)
            b = int(50 + (i / height) * 30)
            draw.line([(0, i), (width, i)], fill=(r, g, b))

        # Try to load a nice font, fallback to default
        try:
            # You might need to adjust font path for Windows
            font_title = ImageFont.truetype("arial.ttf", 60)
            font_artist = ImageFont.truetype("arial.ttf", 40)
            font_lyrics = ImageFont.truetype("arial.ttf", 35)
        except:
            font_title = ImageFont.load_default()
            font_artist = ImageFont.load_default()
            font_lyrics = ImageFont.load_default()

        # Draw Title and Artist
        draw.text((width//2, 150), title, font=font_title, fill=(255, 255, 255), anchor="mm")
        draw.text((width//2, 220), artist, font=font_artist, fill=(180, 180, 180), anchor="mm")
        
        # Draw Divider
        draw.line([(200, 280), (width-200, 280)], fill=(100, 100, 100), width=2)

        # Draw Lyrics with wrapping
        margin = 100
        y_text = 350
        max_width = width - (margin * 2)
        
        lines = []
        for line in text.split('\n')[:25]: # Limit lines to avoid overflow
            if len(line.strip()) == 0: continue
            # Simple manual wrapping
            if len(line) > 50:
                lines.append(line[:50] + "...")
            else:
                lines.append(line)
        
        for line in lines:
            draw.text((width//2, y_text), line, font=font_lyrics, fill=(240, 240, 240), anchor="mm")
            y_text += 50
            if y_text > height - 100: break

        # Add Bot credit
        draw.text((width//2, height-80), "@InstaAudio_Bot orqali tayyorlandi", font=font_artist, fill=(120, 120, 120), anchor="mm")

        output_path = os.path.join(Config.DOWNLOAD_DIR, f"lyrics_{hash(text)}.png")
        image.save(output_path)
        return output_path
    except Exception as e:
        logger.error(f"Error generating lyrics card: {e}")
        return None

async def translate_text(text: str, target_lang: str = 'uz') -> str:
    """Translate text using a free API (simplified)"""
    try:
        if not text: return ""
        # Using a simple free translation API (Example: MyMemory or similar)
        # Note: For production, consider Google Translate or DeepL API
        url = f"https://api.mymemory.translated.net/get?q={text[:500]}&langpair=auto|{target_lang}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            if resp.status_code == 200:
                data = resp.json()
                return data.get('responseData', {}).get('translatedText', text)
        return text
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return text
