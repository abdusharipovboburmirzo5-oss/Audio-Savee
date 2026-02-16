"""
Audio extraction module using FFmpeg
"""
import os
import logging
import subprocess
from typing import Optional, Dict, Any
from config import Config
from utils import cleanup_file, get_file_size

logger = logging.getLogger(__name__)

class AudioExtractor:
    """Extract and convert audio from video files"""
    
    def __init__(self):
        """Initialize audio extractor"""
        self.download_dir = Config.DOWNLOAD_DIR
        Config.ensure_download_dir()
    
    def extract_audio(self, video_path: str, output_format: str = 'mp3') -> Optional[str]:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to video file
            output_format: Output audio format (mp3, m4a, etc.)
            
        Returns:
            Path to extracted audio file, or None if failed
        """
        try:
            if not os.path.exists(video_path):
                logger.error(f"Video file not found: {video_path}")
                return None
            
            # Create output filename
            base_name = os.path.splitext(video_path)[0]
            audio_path = f"{base_name}.{output_format}"
            
            # FFmpeg command to extract audio
            command = [
                'ffmpeg',
                '-i', video_path,
                '-vn',  # No video
                '-acodec', 'libmp3lame' if output_format == 'mp3' else 'copy',
                '-ab', Config.FFMPEG_OPTIONS['audio_bitrate'],
                '-y',  # Overwrite output file
                audio_path
            ]
            
            logger.info(f"Extracting audio from: {video_path}")
            
            # Run FFmpeg
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0 and os.path.exists(audio_path):
                logger.info(f"Audio extracted successfully: {audio_path}")
                return audio_path
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"Error extracting audio: {e}")
            return None
    
    def convert_audio(self, input_path: str, output_format: str = 'mp3', 
                     bitrate: str = '192k') -> Optional[str]:
        """
        Convert audio file to different format
        
        Args:
            input_path: Path to input audio file
            output_format: Output format (mp3, m4a, wav, etc.)
            bitrate: Audio bitrate
            
        Returns:
            Path to converted audio file, or None if failed
        """
        try:
            if not os.path.exists(input_path):
                logger.error(f"Audio file not found: {input_path}")
                return None
            
            # Create output filename
            base_name = os.path.splitext(input_path)[0]
            output_path = f"{base_name}_converted.{output_format}"
            
            # FFmpeg command
            command = [
                'ffmpeg',
                '-i', input_path,
                '-acodec', 'libmp3lame' if output_format == 'mp3' else 'copy',
                '-ab', bitrate,
                '-y',
                output_path
            ]
            
            logger.info(f"Converting audio: {input_path} -> {output_path}")
            
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0 and os.path.exists(output_path):
                logger.info(f"Audio converted successfully: {output_path}")
                return output_path
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return None
        
        except Exception as e:
            logger.error(f"Error converting audio: {e}")
            return None
    
    def get_audio_info(self, audio_path: str) -> Optional[Dict[str, Any]]:
        """
        Get information about audio file
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Dict with audio information, or None if failed
        """
        try:
            if not os.path.exists(audio_path):
                return None
            
            command = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                audio_path
            ]
            
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if result.returncode == 0:
                import json
                info = json.loads(result.stdout)
                
                format_info = info.get('format', {})
                stream_info = info.get('streams', [{}])[0]
                
                return {
                    'duration': float(format_info.get('duration', 0)),
                    'bitrate': int(format_info.get('bit_rate', 0)),
                    'codec': stream_info.get('codec_name', ''),
                    'sample_rate': int(stream_info.get('sample_rate', 0)),
                    'filesize': get_file_size(audio_path),
                }
        
        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            return None
