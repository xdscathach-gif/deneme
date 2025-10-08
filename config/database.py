# -*- coding: utf-8 -*-
"""
Modern veritabanı yönetim sistemi
"""

import sqlite3
import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gelişmiş veritabanı yönetici sınıfı"""
    
    SCHEMA_VERSION = 6
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or "userbot_manager.db"
        self.connection: Optional[sqlite3.Connection] = None
        self._lock = asyncio.Lock()
    
    async def initialize(self):
        """Veritabanını başlat"""
        await self._connect()
        await self._create_tables()
        await self._upgrade_schema()
        logger.info("Veritabanı başarıyla başlatıldı")
    
    async def _connect(self):
        """Veritabanına bağlan"""
        self.connection = sqlite3.connect(
            self.db_path, 
            check_same_thread=False,
            isolation_level=None
        )
        self.connection.row_factory = sqlite3.Row
        
        # WAL modunu etkinleştir (daha iyi performans)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA synchronous=NORMAL")
        self.connection.execute("PRAGMA cache_size=10000")
    
    async def _create_tables(self):
        """Tabloları oluştur"""
        tables = [
            # Kullanıcılar tablosu
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                email TEXT,
                is_admin BOOLEAN DEFAULT FALSE,
                premium_start_date TEXT,
                premium_expiry_date TEXT,
                account_limit INTEGER DEFAULT 2,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_login DATETIME,
                is_active BOOLEAN DEFAULT TRUE
            )
            """,
            
            # Token yönetimi tablosu
            """
            CREATE TABLE IF NOT EXISTS tokens (
                token_id TEXT PRIMARY KEY,
                user_id INTEGER,
                token_hash TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                expires_at DATETIME,
                last_used DATETIME,
                is_active BOOLEAN DEFAULT TRUE,
                device_info TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
            )
            """,
            
            # IP güvenlik tablosu
            """
            CREATE TABLE IF NOT EXISTS ip_security (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ip_address TEXT NOT NULL,
                user_id INTEGER,
                token_id TEXT,
                device_info TEXT,
                location_info TEXT,
                first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_banned BOOLEAN DEFAULT FALSE,
                ban_reason TEXT,
                ban_expires DATETIME,
                login_attempts INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (token_id) REFERENCES tokens (token_id)
            )
            """,
            
            # Userbot hesapları tablosu
            """
            CREATE TABLE IF NOT EXISTS userbots (
                session_name TEXT PRIMARY KEY,
                owner_id INTEGER,
                phone_number TEXT,
                auto_message_text TEXT,
                auto_message_entities TEXT,
                message_delay_range TEXT DEFAULT '30-90',
                loop_cooldown_minutes INTEGER DEFAULT 60,
                is_auto_message_active BOOLEAN DEFAULT FALSE,
                auto_reply_text TEXT,
                auto_reply_entities TEXT,
                is_auto_reply_active BOOLEAN DEFAULT FALSE,
                last_suffix_index INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME,
                status TEXT DEFAULT 'inactive',
                FOREIGN KEY (owner_id) REFERENCES users (user_id) ON DELETE SET NULL
            )
            """,
            
            # Filtreler tablosu
            """
            CREATE TABLE IF NOT EXISTS filters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                trigger TEXT,
                response TEXT,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_name) REFERENCES userbots (session_name) ON DELETE CASCADE
            )
            """,
            
            # DM geçmişi tablosu
            """
            CREATE TABLE IF NOT EXISTS dm_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                sender_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_name, sender_id),
                FOREIGN KEY (session_name) REFERENCES userbots (session_name) ON DELETE CASCADE
            )
            """,
            
            # Hariç tutulan sohbetler tablosu
            """
            CREATE TABLE IF NOT EXISTS excluded_chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT NOT NULL,
                chat_id INTEGER NOT NULL,
                chat_title TEXT,
                added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(session_name, chat_id),
                FOREIGN KEY (session_name) REFERENCES userbots (session_name) ON DELETE CASCADE
            )
            """,
            
            # Sistem logları tablosu
            """
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                details TEXT,
                ip_address TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
            """
        ]
        
        for table_sql in tables:
            await self._execute(table_sql)
    
    async def _upgrade_schema(self):
        """Şema sürümünü yükselt"""
        current_version = await self._get_schema_version()
        
        if current_version >= self.SCHEMA_VERSION:
            return
        
        logger.info(f"Veritabanı şeması {current_version}'den {self.SCHEMA_VERSION}'e yükseltiliyor")
        
        # Sürüm bazlı yükseltmeler burada yapılacak
        if current_version < 6:
            # Yeni sütunlar ekle
            migrations = [
                "ALTER TABLE users ADD COLUMN email TEXT DEFAULT NULL",
                "ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE",
                "ALTER TABLE userbots ADD COLUMN phone_number TEXT DEFAULT NULL",
                "ALTER TABLE userbots ADD COLUMN status TEXT DEFAULT 'inactive'"
            ]
            
            for migration in migrations:
                try:
                    await self._execute(migration)
                except sqlite3.OperationalError:
                    # Sütun zaten varsa hatayı yoksay
                    pass
        
        await self._set_schema_version(self.SCHEMA_VERSION)
        logger.info("Şema yükseltmesi tamamlandı")
    
    async def _get_schema_version(self) -> int:
        """Mevcut şema sürümünü al"""
        result = await self._execute("PRAGMA user_version")
        return result[0][0] if result else 0
    
    async def _set_schema_version(self, version: int):
        """Şema sürümünü ayarla"""
        await self._execute(f"PRAGMA user_version = {version}")
    
    async def _execute(self, query: str, params: tuple = ()):
        """Güvenli SQL sorgusu çalıştır"""
        async with self._lock:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.fetchall()
    
    async def _fetchone(self, query: str, params: tuple = ()):
        """Tek kayıt getir"""
        result = await self._execute(query, params)
        return result[0] if result else None
    
    async def _fetchall(self, query: str, params: tuple = ()):
        """Tüm kayıtları getir"""
        return await self._execute(query, params)
    
    # Token yönetimi metodları
    async def create_token(self, user_id: int, token_hash: str, expires_at: datetime, device_info: str = None) -> str:
        """Yeni token oluştur"""
        token_id = f"token_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}"
        
        await self._execute(
            """INSERT INTO tokens (token_id, user_id, token_hash, expires_at, device_info) 
               VALUES (?, ?, ?, ?, ?)""",
            (token_id, user_id, token_hash, expires_at.isoformat(), device_info)
        )
        
        return token_id
    
    async def validate_token(self, token_hash: str) -> Optional[Dict]:
        """Token'ı doğrula"""
        result = await self._fetchone(
            """SELECT t.*, u.username FROM tokens t 
               JOIN users u ON t.user_id = u.user_id 
               WHERE t.token_hash = ? AND t.is_active = TRUE 
               AND (t.expires_at IS NULL OR t.expires_at > ?)""",
            (token_hash, datetime.now().isoformat())
        )
        
        if result:
            # Son kullanım zamanını güncelle
            await self._execute(
                "UPDATE tokens SET last_used = ? WHERE token_id = ?",
                (datetime.now().isoformat(), result['token_id'])
            )
            
            return dict(result)
        
        return None
    
    async def revoke_token(self, token_id: str):
        """Token'ı iptal et"""
        await self._execute(
            "UPDATE tokens SET is_active = FALSE WHERE token_id = ?",
            (token_id,)
        )
    
    # IP güvenlik metodları
    async def log_ip_access(self, ip_address: str, user_id: int = None, token_id: str = None, device_info: str = None):
        """IP erişimini kaydet"""
        existing = await self._fetchone(
            "SELECT id FROM ip_security WHERE ip_address = ? AND user_id = ?",
            (ip_address, user_id)
        )
        
        if existing:
            await self._execute(
                "UPDATE ip_security SET last_seen = ?, device_info = ? WHERE id = ?",
                (datetime.now().isoformat(), device_info, existing['id'])
            )
        else:
            await self._execute(
                """INSERT INTO ip_security (ip_address, user_id, token_id, device_info) 
                   VALUES (?, ?, ?, ?)""",
                (ip_address, user_id, token_id, device_info)
            )
    
    async def is_ip_banned(self, ip_address: str) -> bool:
        """IP'nin yasaklı olup olmadığını kontrol et"""
        result = await self._fetchone(
            """SELECT is_banned, ban_expires FROM ip_security 
               WHERE ip_address = ? AND is_banned = TRUE""",
            (ip_address,)
        )
        
        if not result:
            return False
        
        if result['ban_expires']:
            ban_expires = datetime.fromisoformat(result['ban_expires'])
            if datetime.now() > ban_expires:
                # Yasaklama süresi dolmuş, kaldır
                await self._execute(
                    "UPDATE ip_security SET is_banned = FALSE, ban_expires = NULL WHERE ip_address = ?",
                    (ip_address,)
                )
                return False
        
        return True
    
    async def ban_ip(self, ip_address: str, reason: str, duration_minutes: int = None):
        """IP'yi yasakla"""
        ban_expires = None
        if duration_minutes:
            ban_expires = (datetime.now() + timedelta(minutes=duration_minutes)).isoformat()
        
        await self._execute(
            """UPDATE ip_security SET is_banned = TRUE, ban_reason = ?, ban_expires = ? 
               WHERE ip_address = ?""",
            (reason, ban_expires, ip_address)
        )
    
    async def unban_ip(self, ip_address: str):
        """IP yasağını kaldır"""
        await self._execute(
            """UPDATE ip_security SET is_banned = FALSE, ban_reason = NULL, ban_expires = NULL 
               WHERE ip_address = ?""",
            (ip_address,)
        )
    
    # Kullanıcı metodları
# Kullanıcı metodları
    async def create_user(self, username: str, email: str = None) -> int:
        """Yeni kullanıcı oluştur"""
        cursor = await self._execute(
            "INSERT INTO users (username, email) VALUES (?, ?)",
            (username, email)
        )
        return cursor.lastrowid
    
    async def get_user(self, user_id: int) -> Optional[Dict]:
        """Kullanıcı bilgilerini al"""
        result = await self._fetchone(
            "SELECT * FROM users WHERE user_id = ? AND is_active = TRUE",
            (user_id,)
        )
        return dict(result) if result else None
    
    async def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Kullanıcı adıyla kullanıcı bul"""
        result = await self._fetchone(
            "SELECT * FROM users WHERE username = ? AND is_active = TRUE",
            (username,)
        )
        return dict(result) if result else None
    
    # Sistem log metodları
    async def log_action(self, user_id: int, action: str, details: str = None, ip_address: str = None):
        """Sistem eylemi kaydet"""
        await self._execute(
            "INSERT INTO system_logs (user_id, action, details, ip_address) VALUES (?, ?, ?, ?)",
            (user_id, action, details, ip_address)
        )
    
    async def get_recent_logs(self, limit: int = 100) -> List[Dict]:
        """Son sistem loglarını al"""
        results = await self._fetchall(
            """SELECT sl.*, u.username FROM system_logs sl 
               LEFT JOIN users u ON sl.user_id = u.user_id 
               ORDER BY sl.timestamp DESC LIMIT ?""",
            (limit,)
        )
        return [dict(row) for row in results]
    
    async def close(self):
        """Veritabanı bağlantısını kapat"""
        if self.connection:
            self.connection.close()
            self.connection = None