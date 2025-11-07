#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Optimized Telegram Group Management Bot with Multilingual Support
Features: NSFW Detection, Spam Protection, Blacklist/Whitelist Management
Languages: Turkish (tr), English (en), Hindi (hi)
"""

import logging
import sqlite3
import time
import re
import os
from functools import wraps
from threading import Lock
from collections import OrderedDict
from typing import Optional, Dict, Any, List, Tuple
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, User
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from telegram import error as telegram_error

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============================================================================
# TRANSLATIONS SYSTEM
# ============================================================================

TRANSLATIONS = {
    # Commands and Responses
    "start": {
        "tr": "👋 Merhaba {mention}!\n\nBen bir grup yönetim botuyum. /help komutunu kullanarak yeteneklerimi görebilirsin.",
        "en": "👋 Hello {mention}!\n\nI'm a group management bot. Use /help to see my capabilities.",
        "hi": "👋 नमस्ते {mention}!\n\nमैं एक समूह प्रबंधन बॉट हूं। मेरी क्षमताओं को देखने के लिए /help का उपयोग करें।"
    },
    "help": {
        "tr": """📚 **Yardım Menüsü**

**Temel Komutlar:**
/start - Botu başlat
/help - Bu yardım mesajı
/settings - Grup ayarları
/language - Dil değiştir

**Yönetici Komutları:**
/whitelist <kullanıcı> - Beyaz listeye ekle
/blacklist <kullanıcı> - Kara listeye ekle
/violations <kullanıcı> - İhlalleri görüntüle
/clearviolations <kullanıcı> - İhlalleri temizle

**Özellikler:**
✅ NSFW içerik algılama
✅ Spam koruması
✅ Kara/Beyaz liste yönetimi
✅ İhlal takibi
✅ Çok dilli destek""",
        "en": """📚 **Help Menu**

**Basic Commands:**
/start - Start the bot
/help - This help message
/settings - Group settings
/language - Change language

**Admin Commands:**
/whitelist <user> - Add to whitelist
/blacklist <user> - Add to blacklist
/violations <user> - View violations
/clearviolations <user> - Clear violations

**Features:**
✅ NSFW content detection
✅ Spam protection
✅ Blacklist/Whitelist management
✅ Violation tracking
✅ Multilingual support""",
        "hi": """📚 **सहायता मेनू**

**मूल आदेश:**
/start - बॉट प्रारंभ करें
/help - यह सहायता संदेश
/settings - समूह सेटिंग्स
/language - भाषा बदलें

**व्यवस्थापक आदेश:**
/whitelist <उपयोगकर्ता> - श्वेतसूची में जोड़ें
/blacklist <उपयोगकर्ता> - काली सूची में जोड़ें
/violations <उपयोगकर्ता> - उल्लंघन देखें
/clearviolations <उपयोगकर्ता> - उल्लंघन साफ़ करें

**विशेषताएं:**
✅ NSFW सामग्री पहचान
✅ स्पैम सुरक्षा
✅ काली/श्वेत सूची प्रबंधन
✅ उल्लंघन ट्रैकिंग
✅ बहुभाषी समर्थन"""
    },
    "settings_menu": {
        "tr": "⚙️ **Grup Ayarları**\n\nAşağıdaki ayarları yapılandırabilirsiniz:",
        "en": "⚙️ **Group Settings**\n\nYou can configure the following settings:",
        "hi": "⚙️ **समूह सेटिंग्स**\n\nआप निम्नलिखित सेटिंग्स कॉन्फ़िगर कर सकते हैं:"
    },
    "language_menu": {
        "tr": "🌐 **Dil Seçimi**\n\nLütfen bir dil seçin:",
        "en": "🌐 **Language Selection**\n\nPlease select a language:",
        "hi": "🌐 **भाषा चयन**\n\nकृपया एक भाषा चुनें:"
    },
    "language_changed": {
        "tr": "✅ Dil başarıyla değiştirildi: {language}",
        "en": "✅ Language changed successfully: {language}",
        "hi": "✅ भाषा सफलतापूर्वक बदल दी गई: {language}"
    },
    # Button texts
    "btn_nsfw_detection": {
        "tr": "🔞 NSFW Algılama: {status}",
        "en": "🔞 NSFW Detection: {status}",
        "hi": "🔞 NSFW पहचान: {status}"
    },
    "btn_spam_protection": {
        "tr": "🛡️ Spam Koruması: {status}",
        "en": "🛡️ Spam Protection: {status}",
        "hi": "🛡️ स्पैम सुरक्षा: {status}"
    },
    "btn_whitelist": {
        "tr": "📝 Beyaz Liste ({count})",
        "en": "📝 Whitelist ({count})",
        "hi": "📝 श्वेतसूची ({count})"
    },
    "btn_blacklist": {
        "tr": "🚫 Kara Liste ({count})",
        "en": "🚫 Blacklist ({count})",
        "hi": "🚫 काली सूची ({count})"
    },
    "btn_violations": {
        "tr": "⚠️ İhlaller ({count})",
        "en": "⚠️ Violations ({count})",
        "hi": "⚠️ उल्लंघन ({count})"
    },
    "btn_language": {
        "tr": "🌐 Dil",
        "en": "🌐 Language",
        "hi": "🌐 भाषा"
    },
    "btn_back": {
        "tr": "« Geri",
        "en": "« Back",
        "hi": "« वापस"
    },
    "btn_close": {
        "tr": "✖️ Kapat",
        "en": "✖️ Close",
        "hi": "✖️ बंद करें"
    },
    "status_on": {
        "tr": "Açık ✅",
        "en": "On ✅",
        "hi": "चालू ✅"
    },
    "status_off": {
        "tr": "Kapalı ❌",
        "en": "Off ❌",
        "hi": "बंद ❌"
    },
    # Notification messages
    "nsfw_detected": {
        "tr": "⚠️ NSFW içerik algılandı! Mesaj silindi.",
        "en": "⚠️ NSFW content detected! Message deleted.",
        "hi": "⚠️ NSFW सामग्री का पता चला! संदेश हटा दिया गया।"
    },
    "spam_detected": {
        "tr": "⚠️ Spam algılandı! Kullanıcı uyarıldı.",
        "en": "⚠️ Spam detected! User warned.",
        "hi": "⚠️ स्पैम का पता चला! उपयोगकर्ता को चेतावनी दी गई।"
    },
    "user_blacklisted": {
        "tr": "🚫 {mention} kara listeye eklendi.",
        "en": "🚫 {mention} added to blacklist.",
        "hi": "🚫 {mention} काली सूची में जोड़ा गया।"
    },
    "user_whitelisted": {
        "tr": "✅ {mention} beyaz listeye eklendi.",
        "en": "✅ {mention} added to whitelist.",
        "hi": "✅ {mention} श्वेतसूची में जोड़ा गया।"
    },
    "violation_added": {
        "tr": "⚠️ {mention} için ihlal kaydedildi. Toplam: {count}",
        "en": "⚠️ Violation recorded for {mention}. Total: {count}",
        "hi": "⚠️ {mention} के लिए उल्लंघन दर्ज किया गया। कुल: {count}"
    },
    "violations_cleared": {
        "tr": "✅ {mention} için tüm ihlaller temizlendi.",
        "en": "✅ All violations cleared for {mention}.",
        "hi": "✅ {mention} के लिए सभी उल्लंघन साफ़ किए गए।"
    },
    # Error messages
    "error_admin_only": {
        "tr": "❌ Bu komutu sadece yöneticiler kullanabilir.",
        "en": "❌ Only admins can use this command.",
        "hi": "❌ केवल व्यवस्थापक ही इस कमांड का उपयोग कर सकते हैं।"
    },
    "error_group_only": {
        "tr": "❌ Bu komut sadece gruplarda kullanılabilir.",
        "en": "❌ This command can only be used in groups.",
        "hi": "❌ यह कमांड केवल समूहों में उपयोग की जा सकती है।"
    },
    "error_user_not_found": {
        "tr": "❌ Kullanıcı bulunamadı.",
        "en": "❌ User not found.",
        "hi": "❌ उपयोगकर्ता नहीं मिला।"
    },
    "error_general": {
        "tr": "❌ Bir hata oluştu: {error}",
        "en": "❌ An error occurred: {error}",
        "hi": "❌ एक त्रुटि हुई: {error}"
    },
    # List displays
    "whitelist_title": {
        "tr": "📝 **Beyaz Liste**\n\n{list}\n\nSayfa {page}/{total_pages}",
        "en": "📝 **Whitelist**\n\n{list}\n\nPage {page}/{total_pages}",
        "hi": "📝 **श्वेतसूची**\n\n{list}\n\nपृष्ठ {page}/{total_pages}"
    },
    "blacklist_title": {
        "tr": "🚫 **Kara Liste**\n\n{list}\n\nSayfa {page}/{total_pages}",
        "en": "🚫 **Blacklist**\n\n{list}\n\nPage {page}/{total_pages}",
        "hi": "🚫 **काली सूची**\n\n{list}\n\nपृष्ठ {page}/{total_pages}"
    },
    "violations_title": {
        "tr": "⚠️ **İhlaller**\n\n{list}\n\nSayfa {page}/{total_pages}",
        "en": "⚠️ **Violations**\n\n{list}\n\nPage {page}/{total_pages}",
        "hi": "⚠️ **उल्लंघन**\n\n{list}\n\nपृष्ठ {page}/{total_pages}"
    },
    "no_entries": {
        "tr": "Kayıt bulunamadı.",
        "en": "No entries found.",
        "hi": "कोई प्रविष्टि नहीं मिली।"
    },
    "btn_next": {
        "tr": "Sonraki »",
        "en": "Next »",
        "hi": "अगला »"
    },
    "btn_prev": {
        "tr": "« Önceki",
        "en": "« Previous",
        "hi": "« पिछला"
    },
}

# Language names for display
LANGUAGE_NAMES = {
    "tr": {"tr": "🇹🇷 Türkçe", "en": "🇹🇷 Turkish", "hi": "🇹🇷 तुर्की"},
    "en": {"tr": "🇬🇧 İngilizce", "en": "🇬🇧 English", "hi": "🇬🇧 अंग्रेज़ी"},
    "hi": {"tr": "🇮🇳 Hintçe", "en": "🇮🇳 Hindi", "hi": "🇮🇳 हिंदी"}
}

# LRU Cache for translations with max size
class LRUCache:
    """Simple LRU cache implementation with maximum size."""
    def __init__(self, max_size=1000):
        self.cache = OrderedDict()
        self.max_size = max_size
    
    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def set(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.max_size:
            # Remove least recently used item
            self.cache.popitem(last=False)

_translation_cache = LRUCache(max_size=1000)

def get_text(key: str, lang: str = "tr", **kwargs) -> str:
    """
    Get translated text with caching.
    
    Args:
        key: Translation key
        lang: Language code (tr, en, hi)
        **kwargs: Format parameters (e.g., mention, status, count)
    
    Returns:
        Formatted translated string
    """
    cache_key = f"{key}:{lang}:{str(kwargs)}"
    
    cached_value = _translation_cache.get(cache_key)
    if cached_value is not None:
        return cached_value
    
    # Get translation or fallback to Turkish
    text = TRANSLATIONS.get(key, {}).get(lang)
    if text is None:
        text = TRANSLATIONS.get(key, {}).get("tr", key)
        logger.warning(f"Translation missing for key='{key}' lang='{lang}'")
    
    # Format with parameters
    try:
        result = text.format(**kwargs)
        _translation_cache.set(cache_key, result)
        return result
    except KeyError as e:
        logger.error(f"Missing format parameter {e} for key '{key}'")
        return text


# ============================================================================
# DATABASE MANAGER WITH CONNECTION POOLING
# ============================================================================

class DatabaseManager:
    """Optimized database manager with connection pooling and caching."""
    
    def __init__(self, db_path: str = "bot_database.db", pool_size: int = 5):
        self.db_path = db_path
        self.pool_size = pool_size
        self.connection_pool: List[sqlite3.Connection] = []
        self.pool_lock = Lock()
        self._settings_cache: Dict[int, Dict[str, Any]] = {}
        self._cache_timestamps: Dict[int, float] = {}
        self.cache_ttl = 300  # 5 minutes TTL
        self._initialize_db()
        self._create_pool()
    
    def _create_pool(self):
        """Create connection pool."""
        with self.pool_lock:
            for _ in range(self.pool_size):
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.connection_pool.append(conn)
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get connection from pool."""
        with self.pool_lock:
            if self.connection_pool:
                return self.connection_pool.pop()
            else:
                # Create new connection if pool is empty
                conn = sqlite3.connect(self.db_path, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                return conn
    
    def _release_connection(self, conn: sqlite3.Connection):
        """Release connection back to pool."""
        with self.pool_lock:
            if len(self.connection_pool) < self.pool_size:
                self.connection_pool.append(conn)
            else:
                conn.close()
    
    def _initialize_db(self):
        """Initialize database schema with indexes."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Settings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                chat_id INTEGER PRIMARY KEY,
                nsfw_detection INTEGER DEFAULT 1,
                spam_protection INTEGER DEFAULT 1,
                max_violations INTEGER DEFAULT 3,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User preferences table for language
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id INTEGER,
                chat_id INTEGER,
                language TEXT DEFAULT 'tr',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, chat_id)
            )
        """)
        
        # Whitelist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS whitelist (
                chat_id INTEGER,
                user_id INTEGER,
                username TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        
        # Blacklist table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS blacklist (
                chat_id INTEGER,
                user_id INTEGER,
                username TEXT,
                reason TEXT,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (chat_id, user_id)
            )
        """)
        
        # Violations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                user_id INTEGER,
                violation_type TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_whitelist_chat ON whitelist(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_blacklist_chat ON blacklist(chat_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_violations_chat_user ON violations(chat_id, user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_violations_created ON violations(created_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_prefs_user ON user_preferences(user_id)")
        
        conn.commit()
        conn.close()
    
    def get_settings(self, chat_id: int, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get chat settings with caching.
        
        Args:
            chat_id: Chat ID
            use_cache: Whether to use cache
        
        Returns:
            Settings dictionary
        """
        # Check cache
        if use_cache and chat_id in self._settings_cache:
            cache_age = time.time() - self._cache_timestamps.get(chat_id, 0)
            if cache_age < self.cache_ttl:
                return self._settings_cache[chat_id].copy()
        
        # Fetch from database
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM settings WHERE chat_id = ?",
                (chat_id,)
            )
            row = cursor.fetchone()
            
            if row:
                settings = dict(row)
            else:
                # Create default settings
                cursor.execute(
                    "INSERT INTO settings (chat_id) VALUES (?)",
                    (chat_id,)
                )
                conn.commit()
                settings = {
                    'chat_id': chat_id,
                    'nsfw_detection': 1,
                    'spam_protection': 1,
                    'max_violations': 3
                }
            
            # Update cache
            self._settings_cache[chat_id] = settings.copy()
            self._cache_timestamps[chat_id] = time.time()
            
            return settings
        finally:
            self._release_connection(conn)
    
    def update_setting(self, chat_id: int, key: str, value: Any):
        """Update a setting and invalidate cache."""
        # Whitelist of allowed setting keys to prevent SQL injection
        allowed_keys = {'nsfw_detection', 'spam_protection', 'max_violations'}
        
        if key not in allowed_keys:
            raise ValueError(f"Invalid setting key: {key}")
        
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            # Now safe to use f-string since key is validated
            cursor.execute(
                f"UPDATE settings SET {key} = ?, updated_at = CURRENT_TIMESTAMP WHERE chat_id = ?",
                (value, chat_id)
            )
            conn.commit()
            
            # Invalidate cache
            if chat_id in self._settings_cache:
                del self._settings_cache[chat_id]
        finally:
            self._release_connection(conn)
    
    def get_user_language(self, user_id: int, chat_id: int) -> str:
        """Get user's preferred language."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT language FROM user_preferences WHERE user_id = ? AND chat_id = ?",
                (user_id, chat_id)
            )
            row = cursor.fetchone()
            return row['language'] if row else 'tr'
        finally:
            self._release_connection(conn)
    
    def set_user_language(self, user_id: int, chat_id: int, language: str):
        """Set user's preferred language."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO user_preferences (user_id, chat_id, language, updated_at)
                   VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                   ON CONFLICT(user_id, chat_id) DO UPDATE SET
                   language = excluded.language,
                   updated_at = CURRENT_TIMESTAMP""",
                (user_id, chat_id, language)
            )
            conn.commit()
        finally:
            self._release_connection(conn)
    
    def is_whitelisted(self, chat_id: int, user_id: int) -> bool:
        """Check if user is whitelisted."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM whitelist WHERE chat_id = ? AND user_id = ?",
                (chat_id, user_id)
            )
            return cursor.fetchone() is not None
        finally:
            self._release_connection(conn)
    
    def is_blacklisted(self, chat_id: int, user_id: int) -> bool:
        """Check if user is blacklisted."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM blacklist WHERE chat_id = ? AND user_id = ?",
                (chat_id, user_id)
            )
            return cursor.fetchone() is not None
        finally:
            self._release_connection(conn)
    
    def add_to_whitelist(self, chat_id: int, user_id: int, username: str):
        """Add user to whitelist."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO whitelist (chat_id, user_id, username)
                   VALUES (?, ?, ?)""",
                (chat_id, user_id, username)
            )
            conn.commit()
        finally:
            self._release_connection(conn)
    
    def add_to_blacklist(self, chat_id: int, user_id: int, username: str, reason: str = ""):
        """Add user to blacklist."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT OR REPLACE INTO blacklist (chat_id, user_id, username, reason)
                   VALUES (?, ?, ?, ?)""",
                (chat_id, user_id, username, reason)
            )
            conn.commit()
        finally:
            self._release_connection(conn)
    
    def add_violation(self, chat_id: int, user_id: int, violation_type: str, description: str = ""):
        """Add violation record."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO violations (chat_id, user_id, violation_type, description)
                   VALUES (?, ?, ?, ?)""",
                (chat_id, user_id, violation_type, description)
            )
            conn.commit()
        finally:
            self._release_connection(conn)
    
    def get_violation_count(self, chat_id: int, user_id: int) -> int:
        """Get violation count for user."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) as count FROM violations WHERE chat_id = ? AND user_id = ?",
                (chat_id, user_id)
            )
            return cursor.fetchone()['count']
        finally:
            self._release_connection(conn)
    
    def clear_violations(self, chat_id: int, user_id: int):
        """Clear all violations for a user."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM violations WHERE chat_id = ? AND user_id = ?",
                (chat_id, user_id)
            )
            conn.commit()
        finally:
            self._release_connection(conn)
    
    def get_list_count(self, chat_id: int, list_type: str) -> int:
        """Get count of items in a list (whitelist/blacklist/violations)."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            if list_type == 'whitelist':
                cursor.execute("SELECT COUNT(*) as count FROM whitelist WHERE chat_id = ?", (chat_id,))
            elif list_type == 'blacklist':
                cursor.execute("SELECT COUNT(*) as count FROM blacklist WHERE chat_id = ?", (chat_id,))
            elif list_type == 'violations':
                cursor.execute("SELECT COUNT(DISTINCT user_id) as count FROM violations WHERE chat_id = ?", (chat_id,))
            else:
                return 0
            return cursor.fetchone()['count']
        finally:
            self._release_connection(conn)
    
    def get_paginated_list(self, chat_id: int, list_type: str, page: int = 1, per_page: int = 10) -> Tuple[List[Dict], int]:
        """
        Get paginated list with lazy loading.
        
        Args:
            chat_id: Chat ID
            list_type: Type of list (whitelist/blacklist/violations)
            page: Page number
            per_page: Items per page
        
        Returns:
            Tuple of (items, total_pages)
        """
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            offset = (page - 1) * per_page
            
            if list_type == 'whitelist':
                cursor.execute(
                    """SELECT user_id, username, added_at FROM whitelist 
                       WHERE chat_id = ? ORDER BY added_at DESC LIMIT ? OFFSET ?""",
                    (chat_id, per_page, offset)
                )
                total_query = "SELECT COUNT(*) as count FROM whitelist WHERE chat_id = ?"
            elif list_type == 'blacklist':
                cursor.execute(
                    """SELECT user_id, username, reason, added_at FROM blacklist 
                       WHERE chat_id = ? ORDER BY added_at DESC LIMIT ? OFFSET ?""",
                    (chat_id, per_page, offset)
                )
                total_query = "SELECT COUNT(*) as count FROM blacklist WHERE chat_id = ?"
            elif list_type == 'violations':
                cursor.execute(
                    """SELECT user_id, COUNT(*) as count, MAX(created_at) as last_violation
                       FROM violations WHERE chat_id = ? 
                       GROUP BY user_id ORDER BY count DESC LIMIT ? OFFSET ?""",
                    (chat_id, per_page, offset)
                )
                total_query = "SELECT COUNT(DISTINCT user_id) as count FROM violations WHERE chat_id = ?"
            else:
                return [], 0
            
            items = [dict(row) for row in cursor.fetchall()]
            
            # Get total count
            cursor.execute(total_query, (chat_id,))
            total_count = cursor.fetchone()['count']
            total_pages = (total_count + per_page - 1) // per_page
            
            return items, total_pages
        finally:
            self._release_connection(conn)
    
    def close(self):
        """Close all connections."""
        with self.pool_lock:
            for conn in self.connection_pool:
                conn.close()
            self.connection_pool.clear()


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_user_mention(user: User) -> str:
    """Get user mention string."""
    name = user.full_name or user.username or "User"
    return f"[{name}](tg://user?id={user.id})"


async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check if user is admin."""
    if not update.effective_chat or update.effective_chat.type == 'private':
        return True
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    
    try:
        member = await context.bot.get_chat_member(chat_id, user_id)
        return member.status in ['creator', 'administrator']
    except telegram_error.TelegramError as e:
        logger.warning(f"Failed to check admin status for user {user_id} in chat {chat_id}: {e}")
        return False


def admin_only(func):
    """Decorator to restrict command to admins only."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not await is_admin(update, context):
            lang = db.get_user_language(update.effective_user.id, update.effective_chat.id)
            await update.message.reply_text(get_text("error_admin_only", lang))
            return
        return await func(update, context)
    return wrapper


def group_only(func):
    """Decorator to restrict command to groups only."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat.type == 'private':
            lang = db.get_user_language(update.effective_user.id, update.effective_chat.id)
            await update.message.reply_text(get_text("error_group_only", lang))
            return
        return await func(update, context)
    return wrapper


# ============================================================================
# CONTENT MODERATION
# ============================================================================

# NSFW keywords configuration - can be extended or loaded from file
NSFW_KEYWORDS = [
    'nsfw', 'porn', 'xxx', 'sex', 'nude', 'naked',
    # Add more keywords as needed
    # In production, load from configuration file or database
]

def detect_nsfw(text: str, custom_keywords: List[str] = None) -> bool:
    """
    Simple NSFW content detection.
    In production, use a proper ML model or API.
    
    Args:
        text: Text to check
        custom_keywords: Optional custom keyword list (overrides default)
    
    Returns:
        True if NSFW content detected
    """
    keywords = custom_keywords if custom_keywords is not None else NSFW_KEYWORDS
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in keywords)


def detect_spam(text: str, user_message_count: int = 0) -> bool:
    """
    Simple spam detection.
    Checks for:
    - Excessive caps
    - Repeated characters
    - Too many messages in short time
    """
    # Check excessive caps (>70% uppercase)
    if len(text) > 10:
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if caps_ratio > 0.7:
            return True
    
    # Check repeated characters (more than 5 times)
    if re.search(r'(.)\1{5,}', text):
        return True
    
    # Check message flood (simplified - in production use time-based tracking)
    if user_message_count > 5:
        return True
    
    return False


# ============================================================================
# COMMAND HANDLERS
# ============================================================================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command handler."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    lang = db.get_user_language(user.id, chat_id)
    
    mention = get_user_mention(user)
    message = get_text("start", lang, mention=mention)
    
    await update.message.reply_text(message, parse_mode='Markdown')
    logger.info(f"User {user.id} started bot in chat {chat_id}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command handler."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    lang = db.get_user_language(user.id, chat_id)
    
    message = get_text("help", lang)
    await update.message.reply_text(message, parse_mode='Markdown')


async def language_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Language selection command."""
    user = update.effective_user
    chat_id = update.effective_chat.id
    lang = db.get_user_language(user.id, chat_id)
    
    keyboard = []
    for lang_code in ['tr', 'en', 'hi']:
        lang_name = LANGUAGE_NAMES[lang_code][lang]
        keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")])
    
    keyboard.append([InlineKeyboardButton(get_text("btn_close", lang), callback_data="close")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = get_text("language_menu", lang)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')


def build_settings_menu(chat_id: int, lang: str) -> Tuple[str, InlineKeyboardMarkup]:
    """
    Build settings menu markup and message.
    Extracted to avoid code duplication and recursive Update creation.
    
    Args:
        chat_id: Chat ID
        lang: Language code
    
    Returns:
        Tuple of (message_text, reply_markup)
    """
    # Get settings from cache
    settings = db.get_settings(chat_id, use_cache=True)
    
    # Get counts with single query each
    whitelist_count = db.get_list_count(chat_id, 'whitelist')
    blacklist_count = db.get_list_count(chat_id, 'blacklist')
    violations_count = db.get_list_count(chat_id, 'violations')
    
    # Pre-compute button data
    nsfw_status = get_text("status_on" if settings['nsfw_detection'] else "status_off", lang)
    spam_status = get_text("status_on" if settings['spam_protection'] else "status_off", lang)
    
    # Build keyboard efficiently
    keyboard = [
        [InlineKeyboardButton(
            get_text("btn_nsfw_detection", lang, status=nsfw_status),
            callback_data="toggle_nsfw"
        )],
        [InlineKeyboardButton(
            get_text("btn_spam_protection", lang, status=spam_status),
            callback_data="toggle_spam"
        )],
        [InlineKeyboardButton(
            get_text("btn_whitelist", lang, count=whitelist_count),
            callback_data="view_whitelist_1"
        )],
        [InlineKeyboardButton(
            get_text("btn_blacklist", lang, count=blacklist_count),
            callback_data="view_blacklist_1"
        )],
        [InlineKeyboardButton(
            get_text("btn_violations", lang, count=violations_count),
            callback_data="view_violations_1"
        )],
        [InlineKeyboardButton(get_text("btn_language", lang), callback_data="language")],
        [InlineKeyboardButton(get_text("btn_close", lang), callback_data="close")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    message = get_text("settings_menu", lang)
    
    return message, reply_markup


@admin_only
@group_only
async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Settings command handler with optimized UI rendering."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    lang = db.get_user_language(user_id, chat_id)
    
    message, reply_markup = build_settings_menu(chat_id, lang)
    await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')


@admin_only
@group_only
async def whitelist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add user to whitelist."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    lang = db.get_user_language(user_id, chat_id)
    
    # Get target user from reply or command args
    target_user = None
    target_user_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
    elif context.args:
        # Try to parse user ID
        try:
            target_user_id = int(context.args[0])
            # Try to get user info from chat
            try:
                member = await context.bot.get_chat_member(chat_id, target_user_id)
                target_user = member.user
            except telegram_error.TelegramError:
                # User info not available, use ID only
                logger.warning(f"Could not fetch user info for ID {target_user_id}")
        except ValueError:
            await update.message.reply_text(get_text("error_user_not_found", lang))
            return
    
    if not target_user_id:
        await update.message.reply_text(get_text("error_user_not_found", lang))
        return
    
    username = target_user.username if target_user else str(target_user_id)
    db.add_to_whitelist(chat_id, target_user_id, username)
    
    mention = get_user_mention(target_user) if target_user else f"User {target_user_id}"
    message = get_text("user_whitelisted", lang, mention=mention)
    await update.message.reply_text(message, parse_mode='Markdown')
    logger.info(f"User {target_user_id} added to whitelist in chat {chat_id}")


@admin_only
@group_only
async def blacklist_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add user to blacklist."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    lang = db.get_user_language(user_id, chat_id)
    
    # Get target user from reply or command args
    target_user = None
    target_user_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
    elif context.args:
        try:
            target_user_id = int(context.args[0])
            # Try to get user info from chat
            try:
                member = await context.bot.get_chat_member(chat_id, target_user_id)
                target_user = member.user
            except telegram_error.TelegramError:
                logger.warning(f"Could not fetch user info for ID {target_user_id}")
        except ValueError:
            await update.message.reply_text(get_text("error_user_not_found", lang))
            return
    
    if not target_user_id:
        await update.message.reply_text(get_text("error_user_not_found", lang))
        return
    
    reason = " ".join(context.args[1:]) if len(context.args) > 1 else ""
    username = target_user.username if target_user else str(target_user_id)
    db.add_to_blacklist(chat_id, target_user_id, username, reason)
    
    mention = get_user_mention(target_user) if target_user else f"User {target_user_id}"
    message = get_text("user_blacklisted", lang, mention=mention)
    await update.message.reply_text(message, parse_mode='Markdown')
    logger.info(f"User {target_user_id} added to blacklist in chat {chat_id}")


@admin_only
@group_only
async def violations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """View violations for a user."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    lang = db.get_user_language(user_id, chat_id)
    
    # Get target user
    target_user = None
    target_user_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
    elif context.args:
        try:
            target_user_id = int(context.args[0])
            try:
                member = await context.bot.get_chat_member(chat_id, target_user_id)
                target_user = member.user
            except telegram_error.TelegramError:
                logger.warning(f"Could not fetch user info for ID {target_user_id}")
        except ValueError:
            await update.message.reply_text(get_text("error_user_not_found", lang))
            return
    
    if not target_user_id:
        # Show all violations
        items, total_pages = db.get_paginated_list(chat_id, 'violations', page=1)
        if not items:
            await update.message.reply_text(get_text("no_entries", lang))
            return
        
        list_text = "\n".join([f"• User {item['user_id']}: {item['count']} violations" for item in items])
        message = get_text("violations_title", lang, list=list_text, page=1, total_pages=total_pages)
        await update.message.reply_text(message, parse_mode='Markdown')
    else:
        # Show violations for specific user
        count = db.get_violation_count(chat_id, target_user_id)
        mention = get_user_mention(target_user) if target_user else f"User {target_user_id}"
        await update.message.reply_text(
            f"{mention}: {count} violations",
            parse_mode='Markdown'
        )


@admin_only
@group_only
async def clear_violations_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Clear violations for a user."""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    lang = db.get_user_language(user_id, chat_id)
    
    # Get target user
    target_user = None
    target_user_id = None
    
    if update.message.reply_to_message:
        target_user = update.message.reply_to_message.from_user
        target_user_id = target_user.id
    elif context.args:
        try:
            target_user_id = int(context.args[0])
            try:
                member = await context.bot.get_chat_member(chat_id, target_user_id)
                target_user = member.user
            except telegram_error.TelegramError:
                logger.warning(f"Could not fetch user info for ID {target_user_id}")
        except ValueError:
            await update.message.reply_text(get_text("error_user_not_found", lang))
            return
    
    if not target_user_id:
        await update.message.reply_text(get_text("error_user_not_found", lang))
        return
    
    db.clear_violations(chat_id, target_user_id)
    mention = get_user_mention(target_user) if target_user else f"User {target_user_id}"
    message = get_text("violations_cleared", lang, mention=mention)
    await update.message.reply_text(message, parse_mode='Markdown')
    logger.info(f"Violations cleared for user {target_user.id} in chat {chat_id}")


# ============================================================================
# CALLBACK QUERY HANDLERS (OPTIMIZED)
# ============================================================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Optimized callback query handler with caching and pre-computed data.
    Target: <0.5 seconds response time
    """
    query = update.callback_query
    await query.answer()  # Answer immediately to prevent timeout
    
    chat_id = query.message.chat_id
    user_id = query.from_user.id
    data = query.data
    
    # Get user language from cache
    lang = db.get_user_language(user_id, chat_id)
    
    # Parse callback data efficiently
    if data == "close":
        await query.message.delete()
        return
    
    elif data.startswith("lang_"):
        # Language change
        new_lang = data.split("_")[1]
        db.set_user_language(user_id, chat_id, new_lang)
        
        lang_name = LANGUAGE_NAMES[new_lang][new_lang]
        message = get_text("language_changed", new_lang, language=lang_name)
        await query.edit_message_text(message)
        logger.info(f"User {user_id} changed language to {new_lang}")
        return
    
    elif data == "language":
        # Show language menu
        keyboard = []
        for lang_code in ['tr', 'en', 'hi']:
            lang_name = LANGUAGE_NAMES[lang_code][lang]
            keyboard.append([InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")])
        
        keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="back_settings")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = get_text("language_menu", lang)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    elif data == "back_settings":
        # Return to settings menu (use helper function)
        message, reply_markup = build_settings_menu(chat_id, lang)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    elif data == "toggle_nsfw":
        # Toggle NSFW detection
        settings = db.get_settings(chat_id, use_cache=False)
        new_value = 0 if settings['nsfw_detection'] else 1
        db.update_setting(chat_id, 'nsfw_detection', new_value)
        
        # Refresh settings menu using helper function
        message, reply_markup = build_settings_menu(chat_id, lang)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    elif data == "toggle_spam":
        # Toggle spam protection
        settings = db.get_settings(chat_id, use_cache=False)
        new_value = 0 if settings['spam_protection'] else 1
        db.update_setting(chat_id, 'spam_protection', new_value)
        
        # Refresh settings menu using helper function
        message, reply_markup = build_settings_menu(chat_id, lang)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return
    
    elif data.startswith("view_whitelist_") or data.startswith("view_blacklist_") or data.startswith("view_violations_"):
        # View paginated lists with lazy loading
        parts = data.split("_")
        list_type = parts[1]
        page = int(parts[2])
        
        items, total_pages = db.get_paginated_list(chat_id, list_type, page=page, per_page=10)
        
        if not items:
            await query.edit_message_text(get_text("no_entries", lang))
            return
        
        # Format list based on type
        if list_type == "whitelist":
            list_text = "\n".join([f"• {item['username']} (ID: {item['user_id']})" for item in items])
            message = get_text("whitelist_title", lang, list=list_text, page=page, total_pages=total_pages)
        elif list_type == "blacklist":
            list_text = "\n".join([f"• {item['username']} (ID: {item['user_id']})" for item in items])
            message = get_text("blacklist_title", lang, list=list_text, page=page, total_pages=total_pages)
        else:  # violations
            list_text = "\n".join([f"• User {item['user_id']}: {item['count']} violations" for item in items])
            message = get_text("violations_title", lang, list=list_text, page=page, total_pages=total_pages)
        
        # Build navigation buttons
        keyboard = []
        nav_row = []
        
        if page > 1:
            nav_row.append(InlineKeyboardButton(
                get_text("btn_prev", lang),
                callback_data=f"view_{list_type}_{page-1}"
            ))
        
        if page < total_pages:
            nav_row.append(InlineKeyboardButton(
                get_text("btn_next", lang),
                callback_data=f"view_{list_type}_{page+1}"
            ))
        
        if nav_row:
            keyboard.append(nav_row)
        
        keyboard.append([InlineKeyboardButton(get_text("btn_back", lang), callback_data="back_settings")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        return


# ============================================================================
# MESSAGE HANDLERS
# ============================================================================

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all messages for content moderation."""
    if not update.message or not update.message.text:
        return
    
    chat_id = update.effective_chat.id
    user = update.effective_user
    text = update.message.text
    
    # Skip if private chat
    if update.effective_chat.type == 'private':
        return
    
    # Skip if user is whitelisted
    if db.is_whitelisted(chat_id, user.id):
        return
    
    # Check if user is blacklisted
    if db.is_blacklisted(chat_id, user.id):
        await update.message.delete()
        return
    
    # Get settings
    settings = db.get_settings(chat_id, use_cache=True)
    lang = db.get_user_language(user.id, chat_id)
    
    # NSFW detection
    if settings['nsfw_detection'] and detect_nsfw(text):
        await update.message.delete()
        db.add_violation(chat_id, user.id, 'nsfw', 'NSFW content detected')
        
        mention = get_user_mention(user)
        count = db.get_violation_count(chat_id, user.id)
        
        warning_msg = get_text("nsfw_detected", lang)
        violation_msg = get_text("violation_added", lang, mention=mention, count=count)
        
        await context.bot.send_message(
            chat_id,
            f"{warning_msg}\n{violation_msg}",
            parse_mode='Markdown'
        )
        
        # Auto-ban if max violations reached
        if count >= settings['max_violations']:
            db.add_to_blacklist(chat_id, user.id, user.username or user.first_name, "Max violations reached")
        
        logger.info(f"NSFW content detected from user {user.id} in chat {chat_id}")
        return
    
    # Spam detection
    if settings['spam_protection'] and detect_spam(text):
        db.add_violation(chat_id, user.id, 'spam', 'Spam detected')
        
        mention = get_user_mention(user)
        count = db.get_violation_count(chat_id, user.id)
        
        warning_msg = get_text("spam_detected", lang)
        violation_msg = get_text("violation_added", lang, mention=mention, count=count)
        
        await context.bot.send_message(
            chat_id,
            f"{warning_msg}\n{violation_msg}",
            parse_mode='Markdown'
        )
        
        # Auto-ban if max violations reached
        if count >= settings['max_violations']:
            db.add_to_blacklist(chat_id, user.id, user.username or user.first_name, "Max violations reached")
        
        logger.info(f"Spam detected from user {user.id} in chat {chat_id}")
        return


# ============================================================================
# ERROR HANDLER
# ============================================================================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    if update and update.effective_chat:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id if update.effective_user else 0
        lang = db.get_user_language(user_id, chat_id) if user_id else 'tr'
        
        error_msg = get_text("error_general", lang, error=str(context.error))
        
        try:
            if update.message:
                await update.message.reply_text(error_msg)
            elif update.callback_query:
                await update.callback_query.message.reply_text(error_msg)
        except telegram_error.TelegramError as e:
            logger.error(f"Failed to send error message: {e}")


# ============================================================================
# MAIN FUNCTION
# ============================================================================

# Global database instance
db: DatabaseManager = None

def main():
    """Main function to run the bot."""
    global db
    
    # Initialize database
    db = DatabaseManager()
    
    # Bot token from environment variable
    TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
    
    if TOKEN == 'YOUR_BOT_TOKEN_HERE':
        logger.error("Bot token not set! Please set BOT_TOKEN environment variable.")
        logger.error("Example: export BOT_TOKEN='your-bot-token-here'")
        return
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("language", language_command))
    application.add_handler(CommandHandler("whitelist", whitelist_command))
    application.add_handler(CommandHandler("blacklist", blacklist_command))
    application.add_handler(CommandHandler("violations", violations_command))
    application.add_handler(CommandHandler("clearviolations", clear_violations_command))
    
    # Register callback query handler
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Register message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    
    # Register error handler
    application.add_error_handler(error_handler)
    
    # Start bot
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
