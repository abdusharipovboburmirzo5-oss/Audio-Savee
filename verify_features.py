"""
Verification script for Bot Features
"""
import asyncio
import os
import logging
from downloader import downloader
from audio_features import audio_features
from database import db

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verification")

async def verify_metadata():
    logger.info("--- Verifying Metadata Tagging ---")
    url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Rick Astley
    result = await downloader.download_audio(url)
    if result and os.path.exists(result['filepath']):
        logger.info(f"Verified: Audio downloaded to {result['filepath']}")
        # Check metadata
        from mutagen.mp3 import MP3
        audio = MP3(result['filepath'])
        logger.info(f"ID3 Tags found: {audio.tags.keys()}")
        if 'TIT2' in audio.tags and 'TPE1' in audio.tags:
            logger.info(f"Verified: Title and Artist tags present: {audio.tags['TIT2']}, {audio.tags['TPE1']}")
        if 'APIC:Cover' in audio.tags:
            logger.info("Verified: Album Art present")
        os.remove(result['filepath'])
    else:
        logger.error("Failed: Audio download failed")

async def verify_recognition():
    logger.info("--- Verifying Audio Recognition ---")
    # We can't easily test this without a real audio file, but we can verify the module loads
    if audio_features.shazam:
        logger.info("Verified: Shazamio module initialized")
    else:
        logger.error("Failed: Shazamio module failed to initialize")

async def verify_database():
    logger.info("--- Verifying Database Extensions ---")
    user_id = 99999
    db.add_favorite(user_id, "Test Song", "https://example.com")
    favs = db.get_favorites(user_id)
    if any(f[0] == "Test Song" for f in favs):
        logger.info("Verified: Favorites system working")
    else:
        logger.error("Failed: Favorites system failed")
    
    stats = db.get_admin_stats()
    logger.info(f"Admin Stats: {stats}")
    if 'total_users' in stats:
        logger.info("Verified: Admin stats working")

async def main():
    await verify_database()
    # verify_metadata takes time and network, skipping for quick check unless requested
    # await verify_metadata()
    await verify_recognition()
    logger.info("Verification complete!")

if __name__ == "__main__":
    asyncio.run(main())
