# -*- coding: utf-8 -*-
"""
Modern userbot yönetim sistemi
"""

import asyncio
import json
import random
import logging
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Pyrogram import'ları
from pyrogram import Client, errors, filters as pyro_filters, types as pyro_types
from pyrogram.handlers import MessageHandler as PyrogramMessageHandler
from pyrogram.enums import ChatType, MessageEntityType
from pyrogram.errors import (
    SessionPasswordNeeded, PhoneCodeInvalid, PasswordHashInvalid, 
    PhoneCodeExpired, UserDeactivated, FloodWait
)

logger = logging.getLogger(__name__)

class UserbotManager:
    """Modern userbot yönetim sınıfı"""
    
    def __init__(self, db_manager, settings):
        self.db = db_manager
        self.settings = settings
        
        # Aktif client'lar ve görevler
        self.active_clients: Dict[str, Client] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.pending_codes: Dict[str, Dict] = {}  # Telefon kodu bekleyen hesaplar
        
        # Cihaz bilgileri (güvenlik için rastgele)
        self.device_models = [
            "PC 64bit", "iPhone 14 Pro Max", "Samsung SM-S908N", 
            "Xiaomi 2201116SG", "Google Pixel 7 Pro", "iPhone 13", 
            "Samsung SM-G998B", "OnePlus 11", "Huawei P50 Pro"
        ]
        
        self.system_versions = [
            "Windows 10", "iOS 16.5.1", "Android 13.0", "macOS 13.4.1", 
            "iOS 17.5", "Windows 11", "Android 14.0", "Linux Ubuntu 22.04"
        ]
        
        self.app_versions = [
            "4.8.10", "9.7.5", "4.9.1", "10.13.1", "9.6.3", "10.14.2", "4.9.5"
        ]
    
    async def start_account_creation(self, session_name: str, phone_number: str) -> Dict[str, Any]:
        """Hesap oluşturma sürecini başlat"""
        try:
            # Oturum adının benzersiz olduğunu kontrol et
            existing = await self.db._fetchone(
                "SELECT 1 FROM userbots WHERE session_name = ?",
                (session_name,)
            )
            
            if existing:
                return {
                    'success': False,
                    'error': 'Bu oturum adı zaten kullanımda!'
                }
            
            # Rastgele cihaz bilgileri
            device_model = random.choice(self.device_models)
            system_version = random.choice(self.system_versions)
            app_version = random.choice(self.app_versions)
            
            # Client oluştur
            session_path = self.settings.data_dir / "sessions" / f"{session_name}.session"
            
            client = Client(
                str(session_path),
                api_id=self.settings.API_ID,
                api_hash=self.settings.API_HASH,
                device_model=device_model,
                system_version=system_version,
                app_version=app_version,
                workdir=str(self.settings.data_dir / "sessions"),
                sleep_threshold=60
            )
            
            # Client'ı bağla
            await client.connect()
            
            # Telefon numarasına kod gönder
            sent_code = await client.send_code(phone_number)
            
            # Bekleyen kodlar listesine ekle
            self.pending_codes[session_name] = {
                'client': client,
                'phone_number': phone_number,
                'phone_code_hash': sent_code.phone_code_hash,
                'created_at': datetime.now()
            }
            
            logger.info(f"Telefon kodu gönderildi: {session_name} -> {phone_number}")
            
            return {
                'success': True,
                'message': 'Doğrulama kodu gönderildi'
            }
            
        except errors.PhoneNumberInvalid:
            return {
                'success': False,
                'error': 'Geçersiz telefon numarası formatı'
            }
        except errors.PhoneNumberBanned:
            return {
                'success': False,
                'error': 'Bu telefon numarası Telegram tarafından yasaklanmış'
            }
        except errors.ApiIdInvalid:
            return {
                'success': False,
                'error': 'Geçersiz API ID veya Hash'
            }
        except Exception as e:
            logger.error(f"Hesap oluşturma başlatma hatası: {e}")
            return {
                'success': False,
                'error': f'Beklenmedik hata: {str(e)}'
            }
    
    async def verify_phone_code(self, session_name: str, code: str) -> Dict[str, Any]:
        """Telefon doğrulama kodunu kontrol et"""
        try:
            if session_name not in self.pending_codes:
                return {
                    'success': False,
                    'error': 'Geçersiz oturum veya kod süresi dolmuş'
                }
            
            pending = self.pending_codes[session_name]
            client = pending['client']
            phone_number = pending['phone_number']
            phone_code_hash = pending['phone_code_hash']
            
            # Kodu doğrula
            try:
                await client.sign_in(phone_number, phone_code_hash, code.replace(" ", ""))
                
                # Başarılı, 2FA gerekmedi
                return {
                    'success': True,
                    'needs_password': False,
                    'message': 'Giriş başarılı'
                }
                
            except SessionPasswordNeeded:
                # 2FA gerekli
                return {
                    'success': True,
                    'needs_password': True,
                    'message': '2FA şifresi gerekli'
                }
            
        except PhoneCodeInvalid:
            return {
                'success': False,
                'error': 'Geçersiz doğrulama kodu'
            }
        except PhoneCodeExpired:
            return {
                'success': False,
                'error': 'Doğrulama kodu süresi dolmuş'
            }
        except Exception as e:
            logger.error(f"Kod doğrulama hatası: {e}")
            return {
                'success': False,
                'error': f'Doğrulama hatası: {str(e)}'
            }
    
    async def verify_2fa_password(self, session_name: str, password: str) -> Dict[str, Any]:
        """2FA şifresini doğrula"""
        try:
            if session_name not in self.pending_codes:
                return {
                    'success': False,
                    'error': 'Geçersiz oturum'
                }
            
            pending = self.pending_codes[session_name]
            client = pending['client']
            
            # 2FA şifresini kontrol et
            await client.check_password(password)
            
            return {
                'success': True,
                'message': '2FA doğrulaması başarılı'
            }
            
        except PasswordHashInvalid:
            return {
                'success': False,
                'error': 'Yanlış 2FA şifresi'
            }
        except Exception as e:
            logger.error(f"2FA doğrulama hatası: {e}")
            return {
                'success': False,
                'error': f'2FA hatası: {str(e)}'
            }
    
    async def complete_account_creation(self, session_name: str, phone_number: str, user_id: int) -> Dict[str, Any]:
        """Hesap oluşturmayı tamamla"""
        try:
            if session_name not in self.pending_codes:
                return {
                    'success': False,
                    'error': 'Geçersiz oturum'
                }
            
            pending = self.pending_codes[session_name]
            client = pending['client']
            
            # Client'ı kapat
            await client.disconnect()
            
            # Veritabanına hesabı kaydet
            await self.db._execute(
                """INSERT INTO userbots (session_name, owner_id, phone_number, created_at, status) 
                   VALUES (?, ?, ?, ?, ?)""",
                (session_name, user_id, phone_number, datetime.now().isoformat(), 'inactive')
            )
            
            # Bekleyen kodlardan kaldır
            del self.pending_codes[session_name]
            
            # Log kaydet
            await self.db.log_action(
                user_id, "USERBOT_CREATED", 
                f"New userbot account created: {session_name}"
            )
            
            logger.info(f"Userbot hesabı başarıyla oluşturuldu: {session_name}")
            
            return {
                'success': True,
                'message': 'Hesap başarıyla eklendi'
            }
            
        except Exception as e:
            logger.error(f"Hesap oluşturma tamamlama hatası: {e}")
            
            # Temizlik işlemi
            if session_name in self.pending_codes:
                try:
                    await self.pending_codes[session_name]['client'].disconnect()
                except:
                    pass
                del self.pending_codes[session_name]
            
            return {
                'success': False,
                'error': f'Hesap kaydedilemedi: {str(e)}'
            }
    
    async def start_userbot_client(self, session_name: str) -> bool:
        """Userbot client'ını başlat"""
        try:
            if session_name in self.active_clients:
                if self.active_clients[session_name].is_connected:
                    return True
                else:
                    # Bağlantı kopmuşsa temizle
                    del self.active_clients[session_name]
            
            # Session dosyasının yolunu belirle
            session_path = self.settings.data_dir / "sessions" / f"{session_name}.session"
            
            if not session_path.exists():
                logger.error(f"Session dosyası bulunamadı: {session_path}")
                return False
            
            # Rastgele cihaz bilgileri
            device_model = random.choice(self.device_models)
            system_version = random.choice(self.system_versions)
            app_version = random.choice(self.app_versions)
            
            # Client oluştur
            client = Client(
                str(session_path),
                api_id=self.settings.API_ID,
                api_hash=self.settings.API_HASH,
                device_model=device_model,
                system_version=system_version,
                app_version=app_version,
                workdir=str(self.settings.data_dir / "sessions"),
                sleep_threshold=60
            )
            
            # Handler'ları ekle
            self._add_client_handlers(client, session_name)
            
            # Client'ı başlat
            await client.start()
            
            # Aktif client'lar listesine ekle
            self.active_clients[session_name] = client
            
            # Durumu güncelle
            await self.db._execute(
                "UPDATE userbots SET status = ?, last_activity = ? WHERE session_name = ?",
                ('active', datetime.now().isoformat(), session_name)
            )
            
            logger.info(f"Userbot client başlatıldı: {session_name}")
            return True
            
        except UserDeactivated:
            logger.error(f"Hesap deaktive edilmiş: {session_name}")
            await self.db._execute(
                "UPDATE userbots SET status = ? WHERE session_name = ?",
                ('deactivated', session_name)
            )
            return False
            
        except Exception as e:
            logger.error(f"Client başlatma hatası {session_name}: {e}")
            await self.db._execute(
                "UPDATE userbots SET status = ? WHERE session_name = ?",
                ('error', session_name)
            )
            return False
    
    def _add_client_handlers(self, client: Client, session_name: str):
        """Client'a handler'ları ekle"""
        
        # Otomatik DM cevap handler'ı
        async def auto_reply_handler(client: Client, message: pyro_types.Message):
            try:
                if not message.from_user or message.from_user.is_bot or message.from_user.is_self:
                    return
                
                # Ayarları kontrol et
                settings = await self.db._fetchone(
                    "SELECT is_auto_reply_active, auto_reply_text, auto_reply_entities FROM userbots WHERE session_name = ?",
                    (session_name,)
                )
                
                if not settings or not settings['is_auto_reply_active'] or not settings['auto_reply_text']:
                    return
                
                sender_id = message.from_user.id
                
                # Bu kullanıcıya daha önce cevap verilmiş mi?
                history = await self.db._fetchone(
                    "SELECT 1 FROM dm_history WHERE session_name = ? AND sender_id = ?",
                    (session_name, sender_id)
                )
                
                if history:
                    return  # Daha önce cevap verilmiş
                
                # Cevap gönder
                text = settings['auto_reply_text']
                entities = self._reconstruct_entities(settings['auto_reply_entities'])
                
                await message.reply_text(text, entities=entities)
                
                # Geçmişe kaydet
                await self.db._execute(
                    "INSERT INTO dm_history (session_name, sender_id) VALUES (?, ?)",
                    (session_name, sender_id)
                )
                
                logger.info(f"Otomatik DM cevabı gönderildi: {session_name} -> {sender_id}")
                
            except Exception as e:
                logger.error(f"DM handler hatası {session_name}: {e}")
        
        # Filtre handler'ı
        async def filter_handler(client: Client, message: pyro_types.Message):
            try:
                if not message.text or (message.from_user and (message.from_user.is_bot or message.from_user.is_self)):
                    return
                
                # Aktif filtreleri al
                filters_data = await self.db._fetchall(
                    "SELECT trigger, response FROM filters WHERE session_name = ? AND is_active = TRUE",
                    (session_name,)
                )
                
                if not filters_data:
                    return
                
                msg_text_lower = message.text.lower()
                
                for filter_item in filters_data:
                    if filter_item['trigger'].lower() in msg_text_lower:
                        await message.reply_text(filter_item['response'])
                        logger.info(f"Filtre tetiklendi: {session_name} -> {filter_item['trigger']}")
                        break
                        
            except Exception as e:
                logger.error(f"Filter handler hatası {session_name}: {e}")
        
        # Handler'ları ekle
        client.add_handler(PyrogramMessageHandler(auto_reply_handler, pyro_filters.private))
        client.add_handler(PyrogramMessageHandler(filter_handler, pyro_filters.group))
    
    async def stop_userbot_client(self, session_name: str) -> bool:
        """Userbot client'ını durdur"""
        try:
            # Çalışan görevleri durdur
            if session_name in self.running_tasks:
                task = self.running_tasks[session_name]
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=5.0)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass
                del self.running_tasks[session_name]
            
            # Client'ı durdur
            if session_name in self.active_clients:
                client = self.active_clients[session_name]
                if client.is_connected:
                    await client.stop()
                del self.active_clients[session_name]
            
            # Durumu güncelle
            await self.db._execute(
                "UPDATE userbots SET status = ? WHERE session_name = ?",
                ('inactive', session_name)
            )
            
            logger.info(f"Userbot client durduruldu: {session_name}")
            return True
            
        except Exception as e:
            logger.error(f"Client durdurma hatası {session_name}: {e}")
            return False
    
    async def delete_account(self, session_name: str) -> bool:
        """Userbot hesabını tamamen sil"""
        try:
            # Client'ı durdur
            await self.stop_userbot_client(session_name)
            
            # Veritabanından tüm ilgili verileri sil
            delete_queries = [
                "DELETE FROM dm_history WHERE session_name = ?",
                "DELETE FROM excluded_chats WHERE session_name = ?",
                "DELETE FROM filters WHERE session_name = ?",
                "DELETE FROM userbots WHERE session_name = ?"
            ]
            
            for query in delete_queries:
                await self.db._execute(query, (session_name,))
            
            # Session dosyasını sil
            session_path = self.settings.data_dir / "sessions" / f"{session_name}.session"
            if session_path.exists():
                session_path.unlink()
            
            logger.info(f"Userbot hesabı silindi: {session_name}")
            return True
            
        except Exception as e:
            logger.error(f"Hesap silme hatası {session_name}: {e}")
            return False
    
    async def toggle_auto_message(self, session_name: str, enabled: bool) -> bool:
        """Otomatik mesajı aç/kapat"""
        try:
            await self.db._execute(
                "UPDATE userbots SET is_auto_message_active = ? WHERE session_name = ?",
                (enabled, session_name)
            )
            
            if enabled:
                # Client'ı başlat
                await self.start_userbot_client(session_name)
                
                # Otomatik mesaj görevini başlat
                if session_name not in self.running_tasks:
                    task = asyncio.create_task(self._auto_message_loop(session_name))
                    self.running_tasks[session_name] = task
            else:
                # Görevleri durdur
                if session_name in self.running_tasks:
                    self.running_tasks[session_name].cancel()
                    del self.running_tasks[session_name]
                
                # İhtiyaç yoksa client'ı durdur
                await self._stop_if_idle(session_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Auto message toggle hatası {session_name}: {e}")
            return False
    
    async def toggle_auto_reply(self, session_name: str, enabled: bool) -> bool:
        """Otomatik cevabı aç/kapat"""
        try:
            await self.db._execute(
                "UPDATE userbots SET is_auto_reply_active = ? WHERE session_name = ?",
                (enabled, session_name)
            )
            
            if enabled:
                # Client'ı başlat
                await self.start_userbot_client(session_name)
            else:
                # İhtiyaç yoksa client'ı durdur
                await self._stop_if_idle(session_name)
            
            return True
            
        except Exception as e:
            logger.error(f"Auto reply toggle hatası {session_name}: {e}")
            return False
    
    async def update_account_settings(self, session_name: str, settings: Dict[str, Any]) -> bool:
        """Hesap ayarlarını güncelle"""
        try:
            update_query = """
                UPDATE userbots SET 
                    auto_message_text = ?,
                    message_delay_range = ?,
                    loop_cooldown_minutes = ?,
                    auto_reply_text = ?
                WHERE session_name = ?
            """
            
            await self.db._execute(
                update_query,
                (
                    settings.get('auto_message_text'),
                    settings.get('message_delay_range'),
                    settings.get('loop_cooldown_minutes'),
                    settings.get('auto_reply_text'),
                    session_name
                )
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Ayar güncelleme hatası {session_name}: {e}")
            return False
    
    async def add_excluded_chat(self, session_name: str, chat_identifier: str) -> bool:
        """İstisna sohbet ekle"""
        try:
            # Client'ı kontrol et
            if session_name not in self.active_clients:
                await self.start_userbot_client(session_name)
            
            if session_name not in self.active_clients:
                return False
            
            client = self.active_clients[session_name]
            
            # Sohbeti bul
            chat = await client.get_chat(chat_identifier)
            
            # Veritabanına ekle
            await self.db._execute(
                "INSERT OR IGNORE INTO excluded_chats (session_name, chat_id, chat_title) VALUES (?, ?, ?)",
                (session_name, chat.id, chat.title or f"{chat.first_name} {chat.last_name or ''}".strip())
            )
            
            return True
            
        except Exception as e:
            logger.error(f"İstisna sohbet ekleme hatası {session_name}: {e}")
            return False
    
    async def start_all_user_userbots(self, user_id: int) -> bool:
        """Kullanıcının tüm userbot'larını başlat"""
        try:
            accounts = await self.db._fetchall(
                "SELECT session_name FROM userbots WHERE owner_id = ?",
                (user_id,)
            )
            
            success_count = 0
            
            for account in accounts:
                session_name = account['session_name']
                
                if await self.start_userbot_client(session_name):
                    # Otomatik mesaj aktifse görev başlat
                    settings = await self.db._fetchone(
                        "SELECT is_auto_message_active FROM userbots WHERE session_name = ?",
                        (session_name,)
                    )
                    
                    if settings and settings['is_auto_message_active']:
                        if session_name not in self.running_tasks:
                            task = asyncio.create_task(self._auto_message_loop(session_name))
                            self.running_tasks[session_name] = task
                    
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Toplu başlatma hatası {user_id}: {e}")
            return False
    
    async def stop_all_user_userbots(self, user_id: int) -> bool:
        """Kullanıcının tüm userbot'larını durdur"""
        try:
            accounts = await self.db._fetchall(
                "SELECT session_name FROM userbots WHERE owner_id = ?",
                (user_id,)
            )
            
            success_count = 0
            
            for account in accounts:
                session_name = account['session_name']
                
                if await self.stop_userbot_client(session_name):
                    success_count += 1
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Toplu durdurma hatası {user_id}: {e}")
            return False
    
    async def _auto_message_loop(self, session_name: str):
        """Otomatik mesaj gönderme döngüsü"""
        try:
            while True:
                try:
                    # Ayarları kontrol et
                    settings = await self.db._fetchone(
                        "SELECT * FROM userbots WHERE session_name = ?",
                        (session_name,)
                    )
                    
                    if not settings or not settings['is_auto_message_active'] or not settings['auto_message_text']:
                        break
                    
                    # Client'ı kontrol et
                    if session_name not in self.active_clients:
                        await self.start_userbot_client(session_name)
                        continue
                    
                    client = self.active_clients[session_name]
                    if not client.is_connected:
                        await self.start_userbot_client(session_name)
                        continue
                    
                    # Mesaj gönderme parametreleri
                    message_text = settings['auto_message_text']
                    delay_range = settings['message_delay_range'] or '30-90'
                    loop_cooldown = settings['loop_cooldown_minutes'] or 60
                    
                    min_delay, max_delay = map(int, delay_range.split('-'))
                    entities = self._reconstruct_entities(settings['auto_message_entities'])
                    
                    # İstisna sohbetleri al
                    excluded_chats = await self.db._fetchall(
                        "SELECT chat_id FROM excluded_chats WHERE session_name = ?",
                        (session_name,)
                    )
                    excluded_ids = {row['chat_id'] for row in excluded_chats}
                    
                    # Grup sohbetlerini al
                    dialogs = []
                    async for dialog in client.get_dialogs():
                        if dialog.chat and dialog.chat.type in [ChatType.GROUP, ChatType.SUPERGROUP]:
                            if dialog.chat.id not in excluded_ids:
                                dialogs.append(dialog)
                    
                    if not dialogs:
                        logger.warning(f"Mesaj gönderilecek grup bulunamadı: {session_name}")
                        await asyncio.sleep(loop_cooldown * 60)
                        continue
                    
                    # Gruplara mesaj gönder
                    batch_size = 3
                    logger.info(f"Mesaj gönderme başladı: {session_name} ({len(dialogs)} grup)")
                    
                    for i in range(0, len(dialogs), batch_size):
                        batch = dialogs[i:i+batch_size]
                        
                        for dialog in batch:
                            # Durum kontrolü
                            current_settings = await self.db._fetchone(
                                "SELECT is_auto_message_active FROM userbots WHERE session_name = ?",
                                (session_name,)
                            )
                            
                            if not current_settings or not current_settings['is_auto_message_active']:
                                logger.info(f"Otomatik mesaj durduruldu: {session_name}")
                                return
                            
                            try:
                                # Suffix oluştur
                                suffix = await self._get_next_suffix(session_name)
                                final_message = f"{message_text}\n\n{suffix}"
                                
                                # Mesaj gönder
                                await client.send_message(
                                    dialog.chat.id,
                                    text=final_message,
                                    entities=entities
                                )
                                
                                logger.info(f"Mesaj gönderildi: {session_name} -> {dialog.chat.title}")
                                
                            except (errors.UserBannedInChannel, errors.ChatWriteForbidden, errors.ChannelPrivate):
                                logger.warning(f"Mesaj gönderilemedi (izin yok): {dialog.chat.title}")
                            except FloodWait as e:
                                wait_time = e.value + 5
                                logger.warning(f"FloodWait: {wait_time}s bekleniyor")
                                await asyncio.sleep(wait_time)
                            except Exception as e:
                                logger.error(f"Mesaj gönderme hatası: {e}")
                            
                            await asyncio.sleep(1)  # Küçük gecikme
                        
                        # Batch arasında gecikme
                        if i + batch_size < len(dialogs):
                            random_delay = random.randint(min_delay, max_delay)
                            logger.info(f"Küme aralığı: {random_delay}s bekleniyor")
                            await asyncio.sleep(random_delay)
                    
                    # Tur tamamlandı, bekleme
                    logger.info(f"Tur tamamlandı: {session_name}, {loop_cooldown}dk bekleniyor")
                    await asyncio.sleep(loop_cooldown * 60)
                    
                except (ConnectionError, asyncio.TimeoutError) as e:
                    logger.warning(f"Bağlantı hatası {session_name}: {e}, 60s sonra tekrar denenecek")
                    await self.stop_userbot_client(session_name)
                    await asyncio.sleep(60)
                    
        except asyncio.CancelledError:
            logger.info(f"Otomatik mesaj görevi iptal edildi: {session_name}")
        except Exception as e:
            logger.error(f"Otomatik mesaj döngüsü hatası {session_name}: {e}")
        finally:
            if session_name in self.running_tasks:
                del self.running_tasks[session_name]
    
    async def _get_next_suffix(self, session_name: str) -> str:
        """Sonraki suffix'i oluştur"""
        try:
            # Karakter seti
            chars = list('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789@#₺_&-()/*";!?.,~`|•π÷×}¢][™}%£\\∆')
            total_chars = len(chars)
            
            # Mevcut index'i al
            result = await self.db._fetchone(
                "SELECT last_suffix_index FROM userbots WHERE session_name = ?",
                (session_name,)
            )
            
            current_index = result['last_suffix_index'] if result else 0
            
            # 3 karakterli suffix oluştur
            suffix = []
            temp_index = current_index
            for _ in range(3):
                suffix.append(chars[temp_index % total_chars])
                temp_index //= total_chars
            
            # Sonraki index'i kaydet
            next_index = (current_index + 1) % (total_chars ** 3)
            await self.db._execute(
                "UPDATE userbots SET last_suffix_index = ? WHERE session_name = ?",
                (next_index, session_name)
            )
            
            return ''.join(suffix)
            
        except Exception as e:
            logger.error(f"Suffix oluşturma hatası: {e}")
            return secrets.token_hex(3)  # Fallback
    
    def _reconstruct_entities(self, entities_json: str) -> List:
        """JSON'dan entity'leri yeniden oluştur"""
        if not entities_json:
            return []
        
        try:
            entities_list = json.loads(entities_json)
            reconstructed = []
            
            for e_dict in entities_list:
                entity_type_str = e_dict.get('type', '').split('.')[-1].upper()
                
                if hasattr(MessageEntityType, entity_type_str):
                    e_dict['type'] = getattr(MessageEntityType, entity_type_str)
                else:
                    continue
                
                if 'custom_emoji_id' in e_dict and e_dict['custom_emoji_id']:
                    e_dict['custom_emoji_id'] = int(e_dict['custom_emoji_id'])
                
                if 'user' in e_dict and e_dict['user']:
                    e_dict['user'] = pyro_types.User(**e_dict['user'])
                
                reconstructed.append(pyro_types.MessageEntity(**e_dict))
            
            return reconstructed
            
        except Exception as e:
            logger.error(f"Entity reconstruction hatası: {e}")
            return []
    
    async def _stop_if_idle(self, session_name: str):
        """Gerekmediyse client'ı durdur"""
        try:
            settings = await self.db._fetchone(
                "SELECT is_auto_message_active, is_auto_reply_active FROM userbots WHERE session_name = ?",
                (session_name,)
            )
            
            filters_exist = await self.db._fetchone(
                "SELECT 1 FROM filters WHERE session_name = ? AND is_active = TRUE",
                (session_name,)
            )
            
            # Hiçbir aktif özellik yoksa durdur
            if not (settings and (settings['is_auto_message_active'] or settings['is_auto_reply_active'])) and not filters_exist:
                await self.stop_userbot_client(session_name)
                
        except Exception as e:
            logger.error(f"Idle check hatası {session_name}: {e}")
    
    async def cleanup_expired_codes(self):
        """Süresi dolmuş kodları temizle"""
        try:
            cutoff_time = datetime.now() - timedelta(minutes=15)
            
            expired_sessions = []
            for session_name, data in self.pending_codes.items():
                if data['created_at'] < cutoff_time:
                    expired_sessions.append(session_name)
            
            for session_name in expired_sessions:
                try:
                    await self.pending_codes[session_name]['client'].disconnect()
                except:
                    pass
                del self.pending_codes[session_name]
                logger.info(f"Süresi dolmuş kod temizlendi: {session_name}")
        # UserbotManager sınıfının devamı

        except Exception as e:
            logger.error(f"Kod temizleme hatası: {e}")
    
    async def get_userbot_stats(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcının userbot istatistiklerini al"""
        try:
            # Toplam hesap sayısı
            total_accounts = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ?",
                (user_id,)
            )
            
            # Aktif hesap sayısı
            active_accounts = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ? AND status = 'active'",
                (user_id,)
            )
            
            # Otomatik mesaj aktif hesaplar
            auto_msg_active = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ? AND is_auto_message_active = TRUE",
                (user_id,)
            )
            
            # Otomatik cevap aktif hesaplar
            auto_reply_active = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ? AND is_auto_reply_active = TRUE",
                (user_id,)
            )
            
            # Toplam filtre sayısı
            total_filters = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM filters f JOIN userbots u ON f.session_name = u.session_name WHERE u.owner_id = ?",
                (user_id,)
            )
            
            return {
                'total_accounts': total_accounts['count'] if total_accounts else 0,
                'active_accounts': active_accounts['count'] if active_accounts else 0,
                'auto_message_active': auto_msg_active['count'] if auto_msg_active else 0,
                'auto_reply_active': auto_reply_active['count'] if auto_reply_active else 0,
                'total_filters': total_filters['count'] if total_filters else 0
            }
            
        except Exception as e:
            logger.error(f"İstatistik alma hatası {user_id}: {e}")
            return {}
    
    async def shutdown(self):
        """Tüm client'ları güvenli şekilde kapat"""
        try:
            # Tüm görevleri iptal et
            for session_name, task in list(self.running_tasks.items()):
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=5.0)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass
            
            self.running_tasks.clear()
            
            # Tüm client'ları kapat
            for session_name, client in list(self.active_clients.items()):
                try:
                    if client.is_connected:
                        await client.stop()
                except Exception as e:
                    logger.error(f"Client kapatma hatası {session_name}: {e}")
            
            self.active_clients.clear()
            
            # Bekleyen kodları temizle
            for session_name, data in list(self.pending_codes.items()):
                try:
                    await data['client'].disconnect()
                except:
                    pass
            
            self.pending_codes.clear()
            
            logger.info("Userbot manager kapatıldı")
            
        except Exception as e:
            logger.error(f"Shutdown hatası: {e}")