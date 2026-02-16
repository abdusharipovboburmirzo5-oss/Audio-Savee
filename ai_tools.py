import logging
import asyncio
import os
import yt_dlp
from typing import Optional

logger = logging.getLogger(__name__)

class AITools:
    """Class for AI-related operations like summaries and transcriptions"""
    
    def __init__(self):
        pass

    async def get_youtube_summary(self, url: str) -> Optional[str]:
        """Get a summary of a YouTube video based on its transcript"""
        try:
            # We use yt-dlp to get the description and some metadata as a "summary" placeholder
            # Real transcript analysis would require an LLM or specific transcript API
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = await asyncio.to_thread(ydl.extract_info, url, download=False)
                if not info: return None
                
                title = info.get('title')
                description = info.get('description', '')
                
                # Simple summary: Title + First part of description
                summary = f"🎬 <b>{title}</b>\n\n"
                if description:
                    # Take first 500 chars of description as a summary
                    summary += "📚 <b>Asosiy mavzular:</b>\n"
                    lines = [l.strip() for l in description.split('\n') if l.strip()]
                    summary += "\n".join(lines[:5])
                else:
                    summary += "ℹ️ Ushbu video haqida batafsil ma'lumot yo'q."
                
                return summary
        except Exception as e:
            logger.error(f"Error getting YouTube summary: {e}")
            return None

    async def transcribe_audio(self, filepath: str) -> Optional[str]:
        """Convert audio to text (transcription)"""
        # Note: True transcription requires speech-to-text models like Whisper.
        # This is a placeholder that explains the feature for the user.
        try:
            if not os.path.exists(filepath): return None
            # Placeholder for future Whisper API/Local implementation
            return "🎙 <b>Ovozli xabar matnga aylantirildi:</b>\n\n(Bu funksiya Whisper AI bilan ulanishi kutilmoqda. Hozircha namunaviy matn.)\n\n- Salom, qandaysiz?\n- Bu audio fayldagi gaplarni yozib beradi."
        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return None

ai_tools = AITools()
