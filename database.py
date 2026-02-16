"""
Simple database module for user preferences and statistics
"""
import os
import sqlite3
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """Simple SQLite database for user data"""
    
    def __init__(self, db_path: str = 'bot_data.db'):
        """Initialize database connection"""
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language TEXT DEFAULT 'uz',
                    auto_audio INTEGER DEFAULT 0,
                    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    referred_by INTEGER,
                    balance FLOAT DEFAULT 0.0
                )
            ''')
            
            # Use PRAGMA to check if balance exists, if not add it (for existing DBs)
            cursor.execute("PRAGMA table_info(users)")
            columns = [col[1] for col in cursor.fetchall()]
            if 'balance' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN balance FLOAT DEFAULT 0.0")
            if 'referred_by' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN referred_by INTEGER")
            if 'is_premium' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN is_premium INTEGER DEFAULT 0")
            if 'premium_expiry' not in columns:
                cursor.execute("ALTER TABLE users ADD COLUMN premium_expiry TIMESTAMP")
            
            # Referrals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    user_id INTEGER PRIMARY KEY,
                    referrer_id INTEGER,
                    rewarded INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id)
                )
            ''')

            # Withdrawals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS withdrawals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount FLOAT,
                    card_number TEXT,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')

            # File Cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS file_cache (
                    url_hash TEXT PRIMARY KEY,
                    filepath TEXT,
                    title TEXT,
                    content_type TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Download history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    url TEXT,
                    title TEXT,
                    content_type TEXT,
                    download_type TEXT,
                    success INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            # Favorites table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    title TEXT,
                    url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            
            # Migration: Ensure auto_audio column exists
            try:
                cursor.execute('ALTER TABLE downloads ADD COLUMN title TEXT')
                conn.commit()
            except sqlite3.OperationalError:
                pass # Already exists
                
            conn.close()
            logger.info("Database initialized successfully")
        
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
    
    def add_user(self, user_id: int, username: str = None, 
                 first_name: str = None, last_name: str = None, referred_by: int = None) -> bool:
        """Add or update user in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO users (user_id, username, first_name, last_name, last_active, referred_by)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(user_id) DO UPDATE SET
                username=excluded.username,
                first_name=excluded.first_name,
                last_name=excluded.last_name,
                last_active=excluded.last_active
            ''', (user_id, username, first_name, last_name, datetime.now(), referred_by))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            logger.error(f"Error adding user: {e}")
            return False

    def get_cached_file(self, url: str, content_type: str = None) -> Optional[Dict[str, Any]]:
        """Get cached file info by URL hash and optional type"""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if content_type:
                cursor.execute('SELECT filepath, title, content_type FROM file_cache WHERE url_hash = ? AND content_type = ?', (url_hash, content_type))
            else:
                cursor.execute('SELECT filepath, title, content_type FROM file_cache WHERE url_hash = ?', (url_hash,))
            res = cursor.fetchone()
            conn.close()
            if res and os.path.exists(res[0]):
                return {'filepath': res[0], 'title': res[1], 'content_type': res[2]}
            return None
        except Exception as e:
            logger.error(f"Error getting cached file: {e}")
            return None

    def add_to_file_cache(self, url: str, filepath: str, title: str, content_type: str):
        """Cache a file path for a URL"""
        import hashlib
        url_hash = hashlib.md5(url.encode()).hexdigest()
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT OR REPLACE INTO file_cache (url_hash, filepath, title, content_type) VALUES (?, ?, ?, ?)', 
                           (url_hash, filepath, title, content_type))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error adding to file cache: {e}")

    def add_referral(self, user_id: int, referrer_id: int) -> bool:
        """Track a referral and reward the referrer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user was already referred (don't reward twice)
            cursor.execute('SELECT 1 FROM referrals WHERE user_id = ?', (user_id,))
            if cursor.fetchone():
                conn.close()
                return False

            cursor.execute('INSERT OR IGNORE INTO referrals (user_id, referrer_id, rewarded) VALUES (?, ?, 1)', (user_id, referrer_id))
            if cursor.rowcount > 0:
                # Reward referrer (e.g., 500 sum)
                cursor.execute('UPDATE users SET balance = balance + 500 WHERE user_id = ?', (referrer_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding referral: {e}")
            return False

    def is_premium(self, user_id: int) -> bool:
        """Check if user has an active premium subscription"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT is_premium, premium_expiry FROM users WHERE user_id = ?', (user_id,))
            res = cursor.fetchone()
            conn.close()
            
            if not res: return False
            is_prem, expiry = res
            if not is_prem: return False
            
            if expiry:
                expiry_dt = datetime.strptime(expiry, '%Y-%m-%d %H:%M:%S.%f') if isinstance(expiry, str) else expiry
                if datetime.now() > expiry_dt:
                    self.set_premium(user_id, False) # Auto-downgrade
                    return False
            return True
        except Exception as e:
            logger.error(f"Error checking premium: {e}")
            return False

    def set_premium(self, user_id: int, status: bool, days: int = 30) -> bool:
        """Set user's premium status"""
        from datetime import timedelta
        expiry = datetime.now() + timedelta(days=days) if status else None
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET is_premium = ?, premium_expiry = ? WHERE user_id = ?', 
                           (1 if status else 0, expiry, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error setting premium: {e}")
            return False

    def add_withdrawal(self, user_id: int, amount: float, card_number: str) -> bool:
        """Create a withdrawal request"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Deduct from balance
            cursor.execute('UPDATE users SET balance = balance - ? WHERE user_id = ? AND balance >= ?', (amount, user_id, amount))
            if cursor.rowcount == 0:
                conn.close()
                return False
                
            cursor.execute('INSERT INTO withdrawals (user_id, amount, card_number) VALUES (?, ?, ?)', (user_id, amount, card_number))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding withdrawal: {e}")
            return False

    def get_referral_count(self, user_id: int) -> int:
        """Get number of users referred by this user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM referrals WHERE referrer_id = ?', (user_id,))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting referral count: {e}")
            return 0
    
    def get_user_language(self, user_id: int) -> str:
        """Get user's preferred language"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT language FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            return result[0] if result else 'uz'
        
        except Exception as e:
            logger.error(f"Error getting user language: {e}")
            return 'uz'
    
    def set_user_language(self, user_id: int, language: str) -> bool:
        """Set user's preferred language"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE users SET language = ? WHERE user_id = ?
            ''', (language, user_id))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            logger.error(f"Error setting user language: {e}")
            return False
    
    def get_user_auto_audio(self, user_id: int) -> bool:
        """Get user's auto-audio preference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT auto_audio FROM users WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            conn.close()
            return bool(result[0]) if result else False
        except Exception as e:
            logger.error(f"Error getting auto-audio pref: {e}")
            return False

    def set_user_auto_audio(self, user_id: int, status: bool) -> bool:
        """Set user's auto-audio preference"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('UPDATE users SET auto_audio = ? WHERE user_id = ?', (1 if status else 0, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error setting auto-audio pref: {e}")
            return False

    def add_download(self, user_id: int, url: str, content_type: str, 
                    download_type: str, title: str = '', success: bool = True) -> bool:
        """Record a download in history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO downloads (user_id, url, title, content_type, download_type, success)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, url, title, content_type, download_type, 1 if success else 0))
            
            conn.commit()
            conn.close()
            return True
        
        except Exception as e:
            logger.error(f"Error adding download: {e}")
            return False
    
    def get_all_users(self) -> list:
        """Get all user IDs from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT user_id FROM users')
            users = [row[0] for row in cursor.fetchall()]
            conn.close()
            return users
        except Exception as e:
            logger.error(f"Error getting all users: {e}")
            return []

    def get_total_users_count(self) -> int:
        """Get total number of users"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM users')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting total users count: {e}")
            return 0

    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total downloads
            cursor.execute('''
                SELECT COUNT(*) FROM downloads WHERE user_id = ? AND success = 1
            ''', (user_id,))
            total_downloads = cursor.fetchone()[0]
            
            # Downloads by type
            cursor.execute('''
                SELECT download_type, COUNT(*) 
                FROM downloads 
                WHERE user_id = ? AND success = 1
                GROUP BY download_type
            ''', (user_id,))
            downloads_by_type = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_downloads': total_downloads,
                'downloads_by_type': downloads_by_type,
            }
        
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {'total_downloads': 0, 'downloads_by_type': {}}
    
    def get_top_downloads(self, limit: int = 10) -> list:
        """Get most popular downloads"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, COUNT(*) as count 
                FROM downloads 
                WHERE download_type IS NOT NULL AND title IS NOT NULL AND title != ''
                GROUP BY title 
                ORDER BY count DESC 
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting top downloads: {e}")
            return []

    def get_trending_music(self, limit: int = 10) -> list:
        """Get most popular downloads from the last 7 days"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT title, url, COUNT(*) as count 
                FROM downloads 
                WHERE download_type = 'audio' 
                AND title IS NOT NULL 
                AND title != ''
                AND created_at >= date('now', '-7 days')
                GROUP BY title 
                ORDER BY count DESC 
                LIMIT ?
            ''', (limit,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting trending music: {e}")
            return []

    def get_recent_downloads(self, user_id: int, limit: int = 5) -> list:
        """Get recent downloads for a specific user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT url, title, content_type, created_at 
                FROM downloads 
                WHERE user_id = ? AND success = 1 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (user_id, limit))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting recent downloads: {e}")
            return []

    def get_downloads_count_today(self) -> int:
        """Get number of downloads today"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM downloads 
                WHERE date(created_at) = date('now') AND success = 1
            ''')
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            logger.error(f"Error getting today's downloads count: {e}")
            return 0

    def log_action(self, user_id: int, action: str, details: str = '') -> bool:
        """Log user action"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO statistics (user_id, action, details)
                VALUES (?, ?, ?)
            ''', (user_id, action, details))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error logging action: {e}")
            return False

    def add_favorite(self, user_id: int, title: str, url: str) -> bool:
        """Add song to user's favorites"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO favorites (user_id, title, url) VALUES (?, ?, ?)', (user_id, title, url))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error adding favorite: {e}")
            return False

    def get_favorites(self, user_id: int) -> list:
        """Get user's favorite songs"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT title, url FROM favorites WHERE user_id = ? ORDER BY created_at DESC', (user_id,))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            logger.error(f"Error getting favorites: {e}")
            return []

    def remove_favorite(self, user_id: int, url: str) -> bool:
        """Remove song from favorites"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM favorites WHERE user_id = ? AND url = ?', (user_id, url))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Error removing favorite: {e}")
            return False

    def get_admin_stats(self) -> Dict[str, Any]:
        """Get overall bot statistics for admin"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users')
            total_users = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM downloads WHERE success = 1')
            total_downloads = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM downloads WHERE date(created_at) = date("now") AND success = 1')
            today_downloads = cursor.fetchone()[0]
            
            conn.close()
            return {
                'total_users': total_users,
                'total_downloads': total_downloads,
                'today_downloads': today_downloads
            }
        except Exception as e:
            logger.error(f"Error getting admin stats: {e}")
            return {}

# Singleton instance
db = Database()
