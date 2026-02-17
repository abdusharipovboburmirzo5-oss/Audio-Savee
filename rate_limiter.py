"""
Rate Limiter Module
Prevents spam and abuse by limiting user requests
"""
import time
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)

class RateLimiter:
    """Per-user rate limiting to prevent spam and abuse"""
    
    def __init__(self, max_messages=10, max_downloads=5, window_seconds=60):
        self.max_messages = max_messages          # Max messages per window
        self.max_downloads = max_downloads        # Max downloads per window
        self.window = window_seconds              # Window in seconds
        self._messages = defaultdict(list)        # user_id -> [timestamps]
        self._downloads = defaultdict(list)       # user_id -> [timestamps]
        self._blocked = {}                        # user_id -> unblock_time
        self._broadcast_cooldown = 0              # Global broadcast cooldown
    
    def _clean_old(self, timestamps: list, now: float) -> list:
        """Remove timestamps older than window"""
        cutoff = now - self.window
        return [t for t in timestamps if t > cutoff]
    
    def check_message(self, user_id: int) -> bool:
        """Check if user can send a message. Returns True if allowed."""
        now = time.time()
        
        # Check if user is temporarily blocked
        if user_id in self._blocked:
            if now < self._blocked[user_id]:
                return False
            else:
                del self._blocked[user_id]
        
        # Clean old timestamps and add new
        self._messages[user_id] = self._clean_old(self._messages[user_id], now)
        
        if len(self._messages[user_id]) >= self.max_messages:
            # Block user for 60 seconds
            self._blocked[user_id] = now + 60
            logger.warning(f"⚠️ Rate limit: User {user_id} blocked for spam ({self.max_messages} msgs/{self.window}s)")
            return False
        
        self._messages[user_id].append(now)
        return True
    
    def check_download(self, user_id: int) -> bool:
        """Check if user can do a download. Returns True if allowed."""
        now = time.time()
        
        self._downloads[user_id] = self._clean_old(self._downloads[user_id], now)
        
        if len(self._downloads[user_id]) >= self.max_downloads:
            logger.warning(f"⚠️ Rate limit: User {user_id} hit download limit ({self.max_downloads}/{self.window}s)")
            return False
        
        self._downloads[user_id].append(now)
        return True
    
    def check_broadcast(self) -> bool:
        """Check if broadcast is allowed (global cooldown: 1 hour)"""
        now = time.time()
        if now < self._broadcast_cooldown:
            return False
        self._broadcast_cooldown = now + 3600  # 1 hour cooldown
        return True
    
    def get_remaining_cooldown(self, user_id: int) -> int:
        """Get remaining cooldown seconds for blocked user"""
        if user_id in self._blocked:
            remaining = int(self._blocked[user_id] - time.time())
            return max(0, remaining)
        return 0
    
    def get_broadcast_cooldown(self) -> int:
        """Get remaining broadcast cooldown seconds"""
        remaining = int(self._broadcast_cooldown - time.time())
        return max(0, remaining)

# Global rate limiter instance
rate_limiter = RateLimiter(
    max_messages=10,   # 10 messages per minute
    max_downloads=5,   # 5 downloads per minute  
    window_seconds=60  # 1 minute window
)
