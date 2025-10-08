# -*- coding: utf-8 -*-
"""
Token tabanlı kimlik doğrulama sistemi - Kesin çözüm
"""

import hashlib
import secrets
import jwt
import logging
import uuid
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class AuthResult:
    """Kimlik doğrulama sonucu"""
    success: bool
    user_id: Optional[int] = None
    username: Optional[str] = None
    token: Optional[str] = None
    error_message: Optional[str] = None
    is_admin: bool = False

class TokenAuthenticator:
    """Token tabanlı kimlik doğrulama sınıfı"""
    
    def __init__(self, db_manager, settings):
        self.db = db_manager
        self.settings = settings
        self.secret_key = self._get_or_create_secret_key()
        self._token_id_counter = 0
        self._lock = threading.Lock()
    
    def _get_or_create_secret_key(self) -> str:
        """JWT için gizli anahtar oluştur veya al"""
        return secrets.token_hex(32)
    
    def generate_token(self, length: int = None) -> str:
        """Güvenli token oluştur"""
        if length is None:
            length = getattr(self.settings, 'TOKEN_LENGTH', 32)
        return secrets.token_urlsafe(length)
    
    def generate_absolutely_unique_token_id(self, prefix: str = "") -> str:
        """Kesinlikle benzersiz token ID oluştur"""
        with self._lock:
            # Nanosecond precision + counter + UUID
            timestamp_ns = time.time_ns()  # Nanosecond precision
            self._token_id_counter += 1
            unique_uuid = str(uuid.uuid4()).replace('-', '')
            
            if prefix:
                return f"{prefix}_{timestamp_ns}_{self._token_id_counter}_{unique_uuid[:8]}"
            else:
                return f"tok_{timestamp_ns}_{self._token_id_counter}_{unique_uuid[:8]}"
    
    def hash_token(self, token: str) -> str:
        """Token'ı hash'le"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    async def admin_login(self, password: str, ip_address: str = None) -> AuthResult:
        """Yönetici girişi - Basitleştirilmiş versiyon"""
        try:
            admin_password = getattr(self.settings, 'ADMIN_PASSWORD', 'admin123')
            if password != admin_password:
                await self.db.log_action(
                    None, "ADMIN_LOGIN_FAILED", 
                    f"Wrong password attempt", ip_address
                )
                return AuthResult(
                    success=False, 
                    error_message="Hatalı yönetici şifresi"
                )
            
            # Yönetici kullanıcısını kontrol et veya oluştur
            admin_user = await self.db.get_user_by_username("admin")
            if not admin_user:
                admin_id = await self.db.create_user("admin")
                await self.db._execute(
                    "UPDATE users SET is_admin = TRUE WHERE user_id = ?",
                    (admin_id,)
                )
            else:
                admin_id = admin_user['user_id']
            
            # TÜM ADMIN TOKEN'LARINI SİL (tek admin oturumu)
            await self.db._execute(
                "DELETE FROM tokens WHERE user_id = ?",
                (admin_id,)
            )
            
            # Yeni token oluştur
            admin_token = self.generate_token()
            token_hash = self.hash_token(admin_token)
            expires_at = datetime.now() + timedelta(hours=8)
            
            # Kesinlikle benzersiz token ID
            max_attempts = 10
            token_created = False
            
            for attempt in range(max_attempts):
                try:
                    unique_token_id = self.generate_absolutely_unique_token_id("admin")
                    
                    await self.db._execute(
                        """INSERT INTO tokens (token_id, user_id, token_hash, created_at, expires_at, device_info, is_active)
                           VALUES (?, ?, ?, ?, ?, ?, TRUE)""",
                        (unique_token_id, admin_id, token_hash, datetime.now().isoformat(), 
                         expires_at.isoformat(), "Admin Panel")
                    )
                    
                    token_created = True
                    break
                    
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e):
                        logger.warning(f"Token ID çakışması, deneme {attempt + 1}")
                        # Kısa bir bekle ve tekrar dene
                        await asyncio.sleep(0.01)  # 10ms bekle
                        continue
                    else:
                        raise e
            
            if not token_created:
                return AuthResult(
                    success=False,
                    error_message="Token oluşturulamadı, lütfen tekrar deneyin"
                )
            
            # IP log (opsiyonel)
            if ip_address:
                try:
                    await self.db.log_ip_access(ip_address, admin_id, unique_token_id, "Admin Login")
                except:
                    pass  # IP log hatası önemli değil
            
            await self.db.log_action(
                admin_id, "ADMIN_LOGIN_SUCCESS", 
                "Admin panel login", ip_address
            )
            
            return AuthResult(
                success=True,
                user_id=admin_id,
                username="admin",
                token=admin_token,
                is_admin=True
            )
            
        except Exception as e:
            logger.error(f"Admin login hatası: {e}")
            return AuthResult(
                success=False,
                error_message=f"Sistm hatası, lütfen tekrar deneyin"
            )
    
    async def user_login(self, token: str, ip_address: str = None) -> AuthResult:
        """Kullanıcı token girişi"""
        try:
            if not token or len(token) < 10:
                return AuthResult(
                    success=False,
                    error_message="Geçersiz token formatı"
                )
            
            # IP yasaklı mı kontrol et
            if ip_address:
                try:
                    if await self.db.is_ip_banned(ip_address):
                        return AuthResult(
                            success=False,
                            error_message="IP adresiniz yasaklı"
                        )
                except:
                    pass  # IP kontrolü opsiyonel
            
            token_hash = self.hash_token(token)
            token_data = await self.db.validate_token(token_hash)
            
            if not token_data:
                return AuthResult(
                    success=False,
                    error_message="Geçersiz veya süresi dolmuş token"
                )
            
            # IP bilgilerini güncelle (opsiyonel)
            if ip_address:
                try:
                    await self.db.log_ip_access(
                        ip_address, token_data['user_id'], 
                        token_data['token_id'], "User Login"
                    )
                except:
                    pass
            
            await self.db.log_action(
                token_data['user_id'], "USER_LOGIN_SUCCESS",
                f"Token login: {token_data['token_id']}", ip_address
            )
            
            return AuthResult(
                success=True,
                user_id=token_data['user_id'],
                username=token_data['username'],
                token=token,
                is_admin=token_data.get('is_admin', False)
            )
            
        except Exception as e:
            logger.error(f"User login hatası: {e}")
            return AuthResult(
                success=False,
                error_message=f"Giriş hatası, lütfen tekrar deneyin"
            )
    
    async def create_user_token(self, username: str, email: str = None, 
                              expires_days: int = 30, device_info: str = None) -> Tuple[str, int]:
        """Kullanıcı için yeni token oluştur"""
        try:
            # Kullanıcıyı kontrol et veya oluştur
            user = await self.db.get_user_by_username(username)
            if not user:
                user_id = await self.db.create_user(username, email)
            else:
                user_id = user['user_id']
            
            # Token oluştur
            token = self.generate_token()
            token_hash = self.hash_token(token)
            expires_at = datetime.now() + timedelta(days=expires_days)
            
            # Benzersiz token ID oluştur
            max_attempts = 5
            for attempt in range(max_attempts):
                try:
                    unique_token_id = self.generate_absolutely_unique_token_id("user")
                    
                    await self.db._execute(
                        """INSERT INTO tokens (token_id, user_id, token_hash, created_at, expires_at, device_info, is_active)
                           VALUES (?, ?, ?, ?, ?, ?, TRUE)""",
                        (unique_token_id, user_id, token_hash, datetime.now().isoformat(), 
                         expires_at.isoformat(), device_info or "Unknown Device")
                    )
                    break
                    
                except Exception as e:
                    if "UNIQUE constraint failed" in str(e) and attempt < max_attempts - 1:
                        continue
                    else:
                        raise e
            
            await self.db.log_action(
                user_id, "TOKEN_CREATED",
                f"New token created: {unique_token_id}"
            )
            
            return token, user_id
            
        except Exception as e:
            logger.error(f"Token oluşturma hatası: {e}")
            raise
    
    async def revoke_token(self, token: str, admin_user_id: int) -> bool:
        """Token'ı iptal et"""
        try:
            token_hash = self.hash_token(token)
            token_data = await self.db.validate_token(token_hash)
            
            if not token_data:
                return False
            
            await self.db.revoke_token(token_data['token_id'])
            
            await self.db.log_action(
                admin_user_id, "TOKEN_REVOKED",
                f"Token revoked: {token_data['token_id']} for user {token_data['user_id']}"
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Token iptal hatası: {e}")
            return False
    
    async def get_active_tokens(self) -> list:
        """Aktif token listesini al"""
        try:
            return await self.db._fetchall(
                """SELECT t.token_id, t.user_id, u.username, t.created_at, 
                          t.last_used, t.device_info
                   FROM tokens t
                   JOIN users u ON t.user_id = u.user_id
                   WHERE t.is_active = TRUE 
                   AND (t.expires_at IS NULL OR t.expires_at > ?)
                   ORDER BY t.last_used DESC""",
                (datetime.now().isoformat(),)
            )
        except Exception as e:
            logger.error(f"Aktif token listesi alma hatası: {e}")
            return []
    
    def create_jwt_token(self, user_id: int, username: str, is_admin: bool = False) -> str:
        """JWT token oluştur"""
        try:
            payload = {
                'user_id': user_id,
                'username': username,
                'is_admin': is_admin,
                'exp': datetime.utcnow() + timedelta(hours=1),
                'iat': datetime.utcnow()
            }
            
            return jwt.encode(payload, self.secret_key, algorithm='HS256')
            
        except Exception as e:
            logger.error(f"JWT token oluşturma hatası: {e}")
            raise
    
    def verify_jwt_token(self, token: str) -> Optional[Dict]:
        """JWT token'ı doğrula"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token süresi dolmuş")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Geçersiz JWT token")
            return None
        except Exception as e:
            logger.error(f"JWT token doğrulama hatası: {e}")
            return None