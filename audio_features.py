"""
Advanced audio features including recognition, lyrics, and trimming
"""
import os
import asyncio
import logging
from typing import Optional, Dict, Any
from shazamio import Shazam
from lyricsgenius import Genius
from config import Config

logger = logging.getLogger(__name__)

class AudioFeatures:
    """Class to handle advanced audio intelligence features"""
    
    def __init__(self):
        self.shazam = Shazam()
        # Genius token can be added to .env later, for now we can try without or use a dummy
        self.genius = None
        genius_token = os.getenv('GENIUS_ACCESS_TOKEN')
        if genius_token:
            self.genius = Genius(genius_token)

    async def recognize_audio(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Recognize song from audio file using Shazam"""
        if not os.path.exists(filepath): return None
        
        import shutil
        if not shutil.which('ffprobe') and not shutil.which('ffmpeg'):
            logger.error("FFmpeg/FFprobe topilmadi. Shazam ishlashi uchun u o'rnatilgan bo'lishi kerak.")
            return None
            
        try:
            out = await self.shazam.recognize_song(filepath)
            if out and 'track' in out:
                track = out['track']
                return {
                    'title': track.get('title'),
                    'artist': track.get('subtitle'),
                    'genres': [g.get('name') for g in track.get('genres', {}).get('list', [])],
                    'thumbnail': track.get('images', {}).get('coverart'),
                    'shazam_url': track.get('url'),
                }
            return None
        except Exception as e:
            logger.error(f"Error recognizing audio: {e}")
            return None

    async def get_lyrics(self, title: str, artist: str = "") -> Optional[str]:
        """Get lyrics for a song"""
        if not self.genius:
            logger.warning("Genius API token not found, skipping lyrics search")
            return None
            
        try:
            song = await asyncio.to_thread(self.genius.search_song, title, artist)
            if song:
                return song.lyrics
            return None
        except Exception as e:
            logger.error(f"Error getting lyrics: {e}")
            return None

    async def trim_audio(self, filepath: str, start_sec: int, end_sec: int) -> Optional[str]:
        """Trim audio file using FFmpeg (requires FFmpeg in PATH)"""
        output_path = filepath.rsplit('.', 1)[0] + "_trimmed.mp3"
        
        # Check if ffmpeg is available
        import shutil
        if not shutil.which('ffmpeg'):
            logger.error("FFmpeg not found in PATH, audio trimming skipped")
            return None
            
        try:
            cmd = [
                'ffmpeg', '-y', '-i', filepath, 
                '-ss', str(start_sec), '-to', str(end_sec), 
                '-acodec', 'copy', output_path
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if os.path.exists(output_path):
                return output_path
            return None
        except Exception as e:
            logger.error(f"Error trimming audio: {e}")
            return None

    async def apply_effect(self, filepath: str, effect: str) -> Optional[str]:
        """Apply audio effects using FFmpeg"""
        if not os.path.exists(filepath): return None
        
        suffix = f"_{effect}.mp3"
        output_path = filepath.rsplit('.', 1)[0] + suffix
        
        # FFmpeg filters for different effects
        effects_map = {
            'bass_boost': 'bass=g=10:f=110:w=0.6',
            '8d': 'apulsator=hz=0.125',
            'slowed_reverb': 'atempo=0.85,aecho=0.8:0.88:60:0.4'
        }
        
        filter_str = effects_map.get(effect)
        if not filter_str:
            logger.error(f"Unknown effect: {effect}")
            return None
            
        import shutil
        if not shutil.which('ffmpeg'):
            logger.error("FFmpeg not found in PATH")
            return None
            
        try:
            cmd = [
                'ffmpeg', '-y', '-i', filepath,
                '-af', filter_str,
                output_path
            ]
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            
            if os.path.exists(output_path):
                return output_path
            return None
        except Exception as e:
            logger.error(f"Error applying effect {effect}: {e}")
            return None

# Singleton instance
audio_features = AudioFeatures()
