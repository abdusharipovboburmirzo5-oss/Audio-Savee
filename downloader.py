import os
import logging
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional, Dict, Any, List
import yt_dlp
from config import Config
from utils import cleanup_file, get_file_size

logger = logging.getLogger(__name__)

class InstagramDownloader:
    """Universal downloader for Instagram, TikTok, and YouTube"""
    
    def __init__(self):
        """Initialize downloader with default options"""
        self.download_dir = Config.DOWNLOAD_DIR
        Config.ensure_download_dir()
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.search_cache = {} # Cache for search results: {query: (results, timestamp)}
        self.download_cache = {} # Cache for file paths: {url: (filepath, timestamp)}
        self.cache_ttl = 3600 # 1 hour
    
    def _get_ydl_opts(self, url: str = None, custom_opts: Dict = None, progress_hook=None) -> Dict:
        """Get base yt-dlp options"""
        opts = {
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(self.download_dir, '%(id)s.%(ext)s'),
            'quiet': False,
            'no_warnings': False,
            'noplaylist': True,
            'nocheckcertificate': True,
            'no_color': True,
            'socket_timeout': 15,
            'retries': 3,
            'extract_flat': False,
            'merge_output_format': 'mp4',
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls', 'translated_subs'],
                    'player_client': ['mweb', 'android', 'ios'],
                    'player_skip': ['configs'],
                },
                'tiktok': {'app_version': '20.2.1', 'manifest_app_version': '20.2.1'},
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Sec-Fetch-Mode': 'navigate',
            },
            'noprogress': True,
            'prefer_free_formats': True, # Stick to simpler formats
            'concurrent_fragment_downloads': 5,
            'external_downloader_args': {'ffmpeg': ['-loglevel', 'panic']},
            'check_formats': False, # Speed up info extraction
            'force_ipv4': True, # Forces IPv4 which is often more stable on Render
            'max_filesize': Config.MAX_FILE_SIZE, # Limit file size
        }
        
        # Look for cookies.txt to bypass persistent blocks
        cookies_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cookies.txt')
        if os.path.exists(cookies_path):
            # Surgical Bypass: YouTube mobile clients (android/ios) fail if cookies are provided.
            # We only use cookies for YouTube if specifically forced or for other platforms.
            is_youtube = url and ('youtube.com' in url or 'youtu.be' in url or 'ytsearch' in url)
            if not is_youtube:
                opts['cookiefile'] = cookies_path
                logger.warning(f"🍪 Bypass Active: Using cookies.txt for {url or 'platform'}")
            else:
                logger.warning(f"🛡️ Mobile Bypass: Skipping cookies for YouTube stability")
        else:
            logger.warning("⚠️ Bypass Warning: cookies.txt NOT found!")

        if url and ('youtube.com' in url or 'youtu.be' in url or 'ytsearch' in url):
            # Dynamic Bypass: skip webpage for DOWNLOADS (429), but keep for SEARCH
            if 'ytsearch' not in url:
                opts['extractor_args']['youtube']['skip'].append('webpage')
                logger.warning(f"🛡️ Download Bypass: Skipping webpage for {url}")
            else:
                logger.warning(f"🔍 Search Mode: Allowing webpage for search query")
        
        return opts

    async def _run_sync(self, func, *args, **kwargs):
        """Run a synchronous function in a thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, lambda: func(*args, **kwargs))

    async def download_video(self, url: str, quality: str = 'best', progress_hook=None) -> Optional[Dict[str, Any]]:
        """Download video with persistent caching"""
        from database import db
        cached = db.get_cached_file(url, 'video')
        if cached:
            logger.info(f"Found persistent video cache for: {url}")
            return cached
            
        result = await self._run_sync(self._download_video_sync, url, quality, progress_hook)
        if result and os.path.exists(result['filepath']):
            db.add_to_file_cache(url, result['filepath'], result['title'], 'video')
        return result

    def _download_video_sync(self, url: str, quality: str = 'best', progress_hook=None) -> Optional[Dict[str, Any]]:
        try:
            ydl_opts = self._get_ydl_opts(url=url, progress_hook=progress_hook)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading video from: {url}")
                info = ydl.extract_info(url, download=True)
                if info:
                    # Get the actual filepath from requested_downloads if available
                    downloads = info.get('requested_downloads', [])
                    if downloads and 'filepath' in downloads[0]:
                        filepath = downloads[0]['filepath']
                    else:
                        filepath = ydl.prepare_filename(info)
                    
                    # Ensure extension is consistent (sometimes it's .webm.mp4 etc)
                    if not os.path.exists(filepath):
                        # Try to find file with the same ID in download dir
                        file_id = info.get('id')
                        for f in os.listdir(self.download_dir):
                            if f.startswith(file_id) and f.endswith(('.mp4', '.mkv', '.webm')):
                                filepath = os.path.join(self.download_dir, f)
                                break

                    return {
                        'filepath': filepath,
                        'title': info.get('title', 'Video'),
                        'duration': info.get('duration', 0),
                        'thumbnail': info.get('thumbnail'),
                        'uploader': info.get('uploader', ''),
                        'filesize': get_file_size(filepath),
                        'platform': info.get('extractor_key', '').lower()
                    }
        except Exception as e:
            logger.error(f"Error downloading video: {e}")
            return None

    async def download_photo(self, url: str) -> Optional[Dict[str, Any]]:
        """Download photo asynchronously"""
        return await self._run_sync(self._download_photo_sync, url)

    def _download_photo_sync(self, url: str) -> Optional[Dict[str, Any]]:
        try:
            ydl_opts = self._get_ydl_opts(url=url, custom_opts={'writethumbnail': True})
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    filepath = ydl.prepare_filename(info)
                    if info.get('ext') in ['mp4', 'webm']:
                        thumbnail_path = filepath.rsplit('.', 1)[0] + '.jpg'
                        if os.path.exists(thumbnail_path):
                            cleanup_file(filepath)
                            filepath = thumbnail_path
                    return {
                        'filepath': filepath,
                        'title': info.get('title', 'Photo'),
                        'uploader': info.get('uploader', ''),
                        'filesize': get_file_size(filepath),
                    }
        except Exception as e:
            logger.error(f"Error downloading photo: {e}")
            return None

    async def search_music(self, query: str, limit: int = 1) -> Optional[List[Dict]]:
        """Search for music asynchronously"""
        return await self._run_sync(self._search_music_sync, query, limit)

    def _search_music_sync(self, query: str, limit: int = 1) -> Optional[List[Dict]]:
        import time
        # Check cache
        cache_key = f"{query}_{limit}"
        if cache_key in self.search_cache:
            results, timestamp = self.search_cache[cache_key]
            if time.time() - timestamp < self.cache_ttl:
                logger.info(f"Using cached results for: {query}")
                return results

        try:
            # Use base options for search too to benefit from bypasses
            ydl_opts = self._get_ydl_opts(url=query, custom_opts={
                'format': 'bestaudio/best', 
                'extract_flat': True,  # Fast search
                'socket_timeout': 10,
            })
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{limit}:{query}"
                logger.info(f"Searching music with query: {search_query}")
                info = ydl.extract_info(search_query, download=False)
                if info and 'entries' in info:
                    logger.info(f"Found {len(info['entries'])} results for query: {query}")
                    results = [{
                        'id': e.get('id'),
                        'title': e.get('title'),
                        'url': e.get('url') or f"https://www.youtube.com/watch?v={e.get('id')}",
                        'duration': e.get('duration'),
                        'uploader': e.get('uploader'),
                    } for e in info['entries']]
                    # Update cache
                    self.search_cache[cache_key] = (results, time.time())
                    return results
        except Exception as e:
            logger.error(f"Error searching music for query '{query}': {e}")
            return None

    async def search_music_versions(self, song_name: str, artist: str = '') -> Dict[str, Optional[Dict[str, Any]]]:
        """Search for different versions of a song in parallel with validation"""
        query_base = f"{artist} {song_name}" if artist else song_name
        versions = {
            'original': query_base,
            '8d': f"{query_base} 8D audio",
            'slowed': f"{query_base} slowed reverb",
            'concert': f"{query_base} concert live",
            'bass': f"{query_base} bass boosted",
            'nightcore': f"{query_base} nightcore",
        }
        keys = list(versions.keys())
        tasks = [self.search_music(q, limit=1) for q in versions.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results = {}
        for i, key in enumerate(keys):
            found = results[i][0] if results[i] else None
            # Validate if the found song is actually related to the original
            if found and key != 'original':
                # Pass both original title and artist for better validation
                if not self._is_similar_title(song_name, found['title'], artist):
                    logger.warning(f"Discarding unrelated result for {key}: '{found['title']}' for original '{song_name}' by '{artist}'")
                    found = None
            final_results[key] = found
            
        logger.info(f"Parallel version search for '{query_base}' completed with validation")
        return final_results

    def _is_similar_title(self, original: str, found: str, artist: str = '') -> bool:
        """Check if found title is similar enough to original"""
        from utils import clean_song_title
        orig_clean = clean_song_title(original).lower()
        found_clean = clean_song_title(found).lower()
        artist_clean = artist.lower() if artist else ''
        
        # Keywords from original title
        keywords = [w for w in orig_clean.split() if len(w) > 2]
        if not keywords: return True # too short to validate
        
        matches = sum(1 for k in keywords if k in found_clean)
        
        # If artist is provided, it's good if it matches, but don't strictly reject
        # unless it's a completely different artist name
        if artist_clean:
            artist_keywords = [w for w in artist_clean.split() if len(w) > 2]
            artist_match = any(ak in found_clean for ak in artist_keywords)
            # If uploader is available, check it too
            uploader_clean = found.get('uploader', '').lower() if isinstance(found, dict) else ''
            uploader_match = any(ak in uploader_clean for ak in artist_keywords) if uploader_clean else False
            
            # Relax: only reject if it's very likely a different song
            # (e.g. found title has a completely different artist name)
            pass 

        return (matches / len(keywords)) >= 0.4 # Relaxed: At least 40% keywords match

    async def download_audio(self, url: str, progress_hook=None) -> Optional[Dict[str, Any]]:
        """Download audio with persistent caching and parallel metadata"""
        from database import db
        cached = db.get_cached_file(url, 'audio')
        if cached:
            logger.info(f"Found persistent audio cache for: {url}")
            return cached

        result = await self._run_sync(self._download_audio_sync, url, progress_hook)
        if result and os.path.exists(result['filepath']):
            db.add_to_file_cache(url, result['filepath'], result['title'], 'audio')
            # Add metadata asynchronously without blocking the result return
            asyncio.create_task(self.add_metadata(
                result['filepath'], 
                result['title'], 
                result['uploader'], 
                result.get('thumbnail')
            ))
        return result

    def _download_audio_sync(self, url: str, progress_hook=None) -> Optional[Dict[str, Any]]:
        try:
            # Standard format selection that usually works best with signature solver
            ydl_opts = self._get_ydl_opts(url=url, custom_opts={
                'format': 'ba/b',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'quiet': False, # Allow some logging in case of error
                'no_warnings': False,
            }, progress_hook=progress_hook)
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                logger.info(f"Downloading audio from: {url}")
                info = ydl.extract_info(url, download=True)
                if info:
                    # Get the actual filepath from requested_downloads if available
                    downloads = info.get('requested_downloads', [])
                    if downloads and 'filepath' in downloads[0]:
                        filepath = downloads[0]['filepath']
                    else:
                        filepath = ydl.prepare_filename(info)
                    
                    return {
                        'filepath': filepath,
                        'title': info.get('title', 'Audio'),
                        'uploader': info.get('uploader', ''),
                        'filesize': get_file_size(filepath),
                        'ext': info.get('ext', 'mp3'),
                        'thumbnail': info.get('thumbnail')
                    }
        except Exception as e:
            logger.error(f"Error downloading audio: {e}")
            return None

    async def download_profile_pic(self, username: str) -> Optional[Dict[str, Any]]:
        return await self._run_sync(self._download_profile_pic_sync, username)

    async def get_playlist_entries(self, url: str) -> list:
        """Get all URLs from a playlist"""
        return await self._run_sync(self._get_playlist_entries_sync, url)

    def _get_playlist_entries_sync(self, url: str) -> list:
        try:
            ydl_opts = {'extract_flat': 'in_playlist', 'quiet': True, 'no_warnings': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if 'entries' in info:
                    return [e['url'] for e in info['entries'] if 'url' in e]
                return [url] # Single item
        except Exception as e:
            logger.error(f"Error getting playlist entries: {e}")
            return []

    def _download_profile_pic_sync(self, username: str) -> Optional[Dict[str, Any]]:
        try:
            url = f"https://www.instagram.com/{username}/"
            ydl_opts = {'writethumbnail': True, 'skip_download': True, 
                        'outtmpl': os.path.join(self.download_dir, f'{username}_profile.%(ext)s'),
                        'quiet': True}
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    for ext in ['jpg', 'jpeg', 'png', 'webp']:
                        filepath = os.path.join(self.download_dir, f'{username}_profile.{ext}')
                        if os.path.exists(filepath):
                            return {'filepath': filepath, 'username': username, 'filesize': get_file_size(filepath)}
        except Exception as e:
            logger.error(f"Error downloading profile picture: {e}")
            return None

    async def add_metadata(self, filepath: str, title: str, artist: str, thumbnail_url: str = None):
        """Add metadata and album art to audio file (MP3 or M4A)"""
        if not os.path.exists(filepath): return
        
        try:
            import httpx
            ext = filepath.rsplit('.', 1)[-1].lower()
            
            thumbnail_data = None
            if thumbnail_url:
                async with httpx.AsyncClient() as client:
                    try:
                        resp = await client.get(thumbnail_url, timeout=10.0)
                        if resp.status_code == 200:
                            thumbnail_data = resp.content
                    except Exception as te:
                        logger.warning(f"Could not download thumbnail: {te}")
            
            if ext == 'mp3':
                from mutagen.mp3 import MP3
                from mutagen.id3 import ID3, TIT2, TPE1, APIC, error
                audio = MP3(filepath, ID3=ID3)
                try: audio.add_tags()
                except error: pass
                audio.tags.add(TIT2(encoding=3, text=title))
                audio.tags.add(TPE1(encoding=3, text=artist))
                if thumbnail_data:
                    audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=thumbnail_data))
                audio.save()
            elif ext == 'm4a':
                from mutagen.mp4 import MP4, MP4Cover
                audio = MP4(filepath)
                audio["\xa9nam"] = title
                audio["\xa9ART"] = artist
                if thumbnail_data:
                    audio["covr"] = [MP4Cover(thumbnail_data, imageformat=MP4Cover.FORMAT_JPEG)]
                audio.save()
                
            logger.info(f"Metadata and cover art added to {filepath}")
        except Exception as e:
            logger.error(f"Error adding metadata to {filepath}: {e}")

# Singleton instance
downloader = InstagramDownloader()
