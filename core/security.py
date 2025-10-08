# -*- coding: utf-8 -*-
"""
IP güvenlik ve güvenlik yönetim sistemi
"""

import socket
import requests
import logging
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class IPInfo:
    """IP adres bilgisi"""
    ip_address: str
    country: str
    city: str
    isp: str
    is_vpn: bool
    risk_score: int

@dataclass
class SecurityEvent:
    """Güvenlik olayı"""
    event_type: str
    ip_address: str
    user_id: Optional[int]
    description: str
    timestamp: datetime
    risk_level: str

class SecurityManager:
    """Güvenlik yönetici sınıfı"""
    
    def __init__(self, db_manager, settings):
        self.db = db_manager
        self.settings = settings
        
        # Güvenlik ayarları
        self.max_login_attempts = 5
        self.lockout_duration = 30  # dakika
        self.rate_limit_window = 60  # saniye
        self.max_requests_per_window = 10
        
        # IP risk skorları
        self.ip_risk_cache = {}
        self.request_counts = {}
    
    async def get_client_ip(self, request_headers: Dict = None) -> str:
        """İstemci IP adresini al"""
        try:
            # Gerçek uygulamada HTTP header'larından alınacak
            # Şimdilik localhost döndürüyoruz
            if request_headers:
                # X-Forwarded-For header'ını kontrol et
                forwarded_for = request_headers.get('X-Forwarded-For')
                if forwarded_for:
                    return forwarded_for.split(',')[0].strip()
                
                # X-Real-IP header'ını kontrol et
                real_ip = request_headers.get('X-Real-IP')
                if real_ip:
                    return real_ip
            
            # Gerçek IP'yi almaya çalış
            try:
                # Harici servise istek at
                response = requests.get('https://httpbin.org/ip', timeout=5)
                if response.status_code == 200:
                    return response.json().get('origin', '127.0.0.1')
            except:
                pass
            
            return '127.0.0.1'  # Fallback
            
        except Exception as e:
            logger.error(f"IP alma hatası: {e}")
            return '127.0.0.1'
    
    async def get_ip_info(self, ip_address: str) -> IPInfo:
        """IP adres bilgilerini al"""
        try:
            # Cache kontrolü
            if ip_address in self.ip_risk_cache:
                cache_data = self.ip_risk_cache[ip_address]
                if datetime.now() - cache_data['timestamp'] < timedelta(hours=1):
                    return cache_data['info']
            
            # Localhost kontrolü
            if ip_address in ['127.0.0.1', 'localhost', '::1']:
                info = IPInfo(
                    ip_address=ip_address,
                    country="Local",
                    city="Local",
                    isp="Local Network",
                    is_vpn=False,
                    risk_score=0
                )
                
                self.ip_risk_cache[ip_address] = {
                    'info': info,
                    'timestamp': datetime.now()
                }
                
                return info
            
            # Gerçek IP için bilgi al
            info = await self._fetch_ip_info(ip_address)
            
            # Cache'e kaydet
            self.ip_risk_cache[ip_address] = {
                'info': info,
                'timestamp': datetime.now()
            }
            
            return info
            
        except Exception as e:
            logger.error(f"IP bilgisi alma hatası {ip_address}: {e}")
            return IPInfo(
                ip_address=ip_address,
                country="Unknown",
                city="Unknown",
                isp="Unknown",
                is_vpn=False,
                risk_score=50  # Orta risk
            )
    
    async def _fetch_ip_info(self, ip_address: str) -> IPInfo:
        """Harici servislerden IP bilgisi al"""
        try:
            # ip-api.com servisini kullan (ücretsiz)
            url = f"http://ip-api.com/json/{ip_address}?fields=status,country,city,isp,proxy,hosting"
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: requests.get(url, timeout=10)
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    # Risk skoru hesapla
                    risk_score = 10  # Base risk
                    
                    if data.get('proxy', False) or data.get('hosting', False):
                        risk_score += 40
                    
                    # Bazı ülkeler için risk artışı
                    high_risk_countries = ['CN', 'RU', 'IR', 'KP']
                    if data.get('countryCode') in high_risk_countries:
                        risk_score += 20
                    
                    return IPInfo(
                        ip_address=ip_address,
                        country=data.get('country', 'Unknown'),
                        city=data.get('city', 'Unknown'),
                        isp=data.get('isp', 'Unknown'),
                        is_vpn=data.get('proxy', False) or data.get('hosting', False),
                        risk_score=min(risk_score, 100)
                    )
            
            # Başarısız olursa default değerler
            return IPInfo(
                ip_address=ip_address,
                country="Unknown",
                city="Unknown",
                isp="Unknown",
                is_vpn=False,
                risk_score=30
            )
            
        except Exception as e:
            logger.error(f"IP info fetch hatası: {e}")
            return IPInfo(
                ip_address=ip_address,
                country="Unknown",
                city="Unknown",
                isp="Unknown",
                is_vpn=False,
                risk_score=50
            )
    
    async def check_ip_security(self, ip_address: str, user_id: int = None) -> Tuple[bool, str]:
        """IP güvenlik kontrolü"""
        try:
            # IP yasaklı mı kontrol et
            if await self.db.is_ip_banned(ip_address):
                await self._log_security_event(
                    "IP_BLOCKED_ATTEMPT",
                    ip_address,
                    user_id,
                    "Yasaklı IP'den erişim denemesi",
                    "HIGH"
                )
                return False, "IP adresi yasaklanmış"
            
            # Rate limiting kontrolü
            if not await self._check_rate_limit(ip_address):
                await self._log_security_event(
                    "RATE_LIMIT_EXCEEDED",
                    ip_address,
                    user_id,
                    "Rate limit aşıldı",
                    "MEDIUM"
                )
                return False, "Çok fazla istek, lütfen bekleyin"
            
            # IP risk analizi
            ip_info = await self.get_ip_info(ip_address)
            
            if ip_info.risk_score > 80:
                await self._log_security_event(
                    "HIGH_RISK_IP",
                    ip_address,
                    user_id,
                    f"Yüksek riskli IP: Risk skoru {ip_info.risk_score}",
                    "HIGH"
                )
                
                # Otomatik yasaklama (çok yüksek risk)
                if ip_info.risk_score > 90:
                    await self.db.ban_ip(
                        ip_address,
                        f"Otomatik yasaklama: Risk skoru {ip_info.risk_score}",
                        60  # 1 saat
                    )
                    return False, "Güvenlik nedeniyle erişim engellendi"
            
            return True, "Güvenlik kontrolü başarılı"
            
        except Exception as e:
            logger.error(f"IP güvenlik kontrolü hatası: {e}")
            return True, "Güvenlik kontrolü tamamlanamadı"  # Fail-open
    
    async def _check_rate_limit(self, ip_address: str) -> bool:
        """Rate limiting kontrolü"""
        try:
            now = datetime.now()
            window_start = now - timedelta(seconds=self.rate_limit_window)
            
            # IP için istek sayısını kontrol et
            if ip_address not in self.request_counts:
                self.request_counts[ip_address] = []
            
            # Eski istekleri temizle
            self.request_counts[ip_address] = [
                timestamp for timestamp in self.request_counts[ip_address]
                if timestamp > window_start
            ]
            
            # Yeni isteği ekle
            self.request_counts[ip_address].append(now)
            
            # Limit kontrolü
            return len(self.request_counts[ip_address]) <= self.max_requests_per_window
            
        except Exception as e:
            logger.error(f"Rate limit kontrolü hatası: {e}")
            return True  # Fail-open
    
    async def record_login_attempt(self, ip_address: str, user_id: int, success: bool) -> bool:
        """Giriş denemesini kaydet"""
        try:
            # IP bilgilerini güncelle
            await self.db.log_ip_access(ip_address, user_id if success else None)
            
            if not success:
                # Başarısız giriş sayısını artır
                await self.db._execute(
                    """UPDATE ip_security SET login_attempts = login_attempts + 1 
                       WHERE ip_address = ?""",
                    (ip_address,)
                )
                
                # Başarısız giriş sayısını kontrol et
                result = await self.db._fetchone(
                    "SELECT login_attempts FROM ip_security WHERE ip_address = ?",
                    (ip_address,)
                )
                
                if result and result['login_attempts'] >= self.max_login_attempts:
                    # IP'yi geçici yasakla
                    await self.db.ban_ip(
                        ip_address,
                        f"Çok fazla başarısız giriş denemesi ({result['login_attempts']} deneme)",
                        self.lockout_duration
                    )
                    
                    await self._log_security_event(
                        "IP_AUTO_BANNED",
                        ip_address,
                        user_id,
                        f"Otomatik yasaklama: {result['login_attempts']} başarısız giriş",
                        "HIGH"
                    )
                    
                    return False
            else:
                # Başarılı giriş, sayacı sıfırla
                await self.db._execute(
                    "UPDATE ip_security SET login_attempts = 0 WHERE ip_address = ?",
                    (ip_address,)
                )
            
            return True
            
        except Exception as e:
            logger.error(f"Giriş deneme kaydı hatası: {e}")
            return True
    
    async def _log_security_event(self, event_type: str, ip_address: str, user_id: int, 
                                description: str, risk_level: str):
        """Güvenlik olayını kaydet"""
        try:
            event = SecurityEvent(
                event_type=event_type,
                ip_address=ip_address,
                user_id=user_id,
                description=description,
                timestamp=datetime.now(),
                risk_level=risk_level
            )
            
            # Veritabanına kaydet
            await self.db._execute(
                """INSERT INTO system_logs (user_id, action, details, ip_address) 
                   VALUES (?, ?, ?, ?)""",
                (user_id, event_type, f"{description} (Risk: {risk_level})", ip_address)
            )
            
            logger.warning(f"Güvenlik olayı: {event_type} - {description} (IP: {ip_address})")
            
        except Exception as e:
            logger.error(f"Güvenlik olayı kaydı hatası: {e}")
    
    async def get_security_report(self) -> Dict[str, Any]:
        """Güvenlik raporu oluştur"""
        try:
            # Son 24 saatteki güvenlik olayları
            yesterday = (datetime.now() - timedelta(days=1)).isoformat()
            
            security_events = await self.db._fetchall(
                """SELECT action, COUNT(*) as count FROM system_logs 
                   WHERE timestamp > ? AND action LIKE '%SECURITY%' OR action LIKE '%BAN%' OR action LIKE '%BLOCK%'
                   GROUP BY action""",
                (yesterday,)
            )
            
            # Yasaklı IP'ler
            banned_ips = await self.db._fetchall(
                "SELECT COUNT(DISTINCT ip_address) as count FROM ip_security WHERE is_banned = TRUE"
            )
            
            # Son giriş denemeleri
            login_attempts = await self.db._fetchall(
                """SELECT ip_address, SUM(login_attempts) as total_attempts 
                   FROM ip_security WHERE login_attempts > 0 
                   GROUP BY ip_address ORDER BY total_attempts DESC LIMIT 10"""
            )
            
            # Risk skorları yüksek IP'ler
            high_risk_ips = []
            for ip, cache_data in self.ip_risk_cache.items():
                if cache_data['info'].risk_score > 70:
                    high_risk_ips.append({
                        'ip': ip,
                        'risk_score': cache_data['info'].risk_score,
                        'country': cache_data['info'].country,
                        'is_vpn': cache_data['info'].is_vpn
                    })
            
            return {
                'security_events': [dict(event) for event in security_events],
                'banned_ip_count': banned_ips[0]['count'] if banned_ips else 0,
                'failed_login_attempts': [dict(attempt) for attempt in login_attempts],
                'high_risk_ips': high_risk_ips,
                'report_generated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Güvenlik raporu oluşturma hatası: {e}")
            return {}
    
    async def cleanup_old_data(self):
        """Eski güvenlik verilerini temizle"""
        try:
            # 30 günden eski sistem loglarını sil
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            await self.db._execute(
                "DELETE FROM system_logs WHERE timestamp < ?",
                (cutoff_date,)
            )
            
            # Süresi dolmuş IP yasaklarını kaldır
            current_time = datetime.now().isoformat()
            expired_bans = await self.db._fetchall(
                "SELECT ip_address FROM ip_security WHERE is_banned = TRUE AND ban_expires IS NOT NULL AND ban_expires < ?",
                (current_time,)
            )
            
            for ban in expired_bans:
                await self.db.unban_ip(ban['ip_address'])
                logger.info(f"IP yasağı süresi doldu, kaldırıldı: {ban['ip_address']}")
            
            # Cache temizleme
            current_time = datetime.now()
            expired_cache_keys = []
            
            for ip, cache_data in self.ip_risk_cache.items():
                if current_time - cache_data['timestamp'] > timedelta(hours=6):
                    expired_cache_keys.append(ip)
            
            for key in expired_cache_keys:
                del self.ip_risk_cache[key]
            
            # Rate limit verilerini temizle
            cutoff_time = current_time - timedelta(minutes=5)
            for ip in list(self.request_counts.keys()):
                self.request_counts[ip] = [
                    timestamp for timestamp in self.request_counts[ip]
                    if timestamp > cutoff_time
                ]
                if not self.request_counts[ip]:
                    del self.request_counts[ip]
            
            logger.info("Güvenlik verileri temizlendi")
            
        except Exception as e:
            logger.error(f"Güvenlik veri temizleme hatası: {e}")
    
    def generate_device_fingerprint(self, user_agent: str, screen_resolution: str = "", timezone: str = "") -> str:
        """Cihaz parmak izi oluştur"""
        try:
            # Basit cihaz parmak izi
            fingerprint_data = f"{user_agent}:{screen_resolution}:{timezone}"
            return hashlib.md5(fingerprint_data.encode()).hexdigest()
            
        except Exception as e:
            logger.error(f"Fingerprint oluşturma hatası: {e}")
            return "unknown"
    
    async def check_suspicious_activity(self, user_id: int, ip_address: str) -> Tuple[bool, List[str]]:
        """Şüpheli aktivite kontrolü"""
        try:
            warnings = []
            
            # Farklı IP'lerden giriş kontrolü
            user_ips = await self.db._fetchall(
                """SELECT DISTINCT ip_address, first_seen FROM ip_security 
                   WHERE user_id = ? AND first_seen > ? ORDER BY first_seen DESC""",
                (user_id, (datetime.now() - timedelta(days=7)).isoformat())
            )
            
            if len(user_ips) > 3:
                warnings.append(f"Son 7 günde {len(user_ips)} farklı IP'den giriş")
            
            # Gece saatleri aktivitesi
            current_hour = datetime.now().hour
            if 2 <= current_hour <= 5:
                warnings.append("Gece saatlerinde aktivite")
            
            # VPN/Proxy kullanımı
            ip_info = await self.get_ip_info(ip_address)
            if ip_info.is_vpn:
                warnings.append("VPN/Proxy kullanımı tespit edildi")
            
            # Yüksek risk skorlu IP
            if ip_info.risk_score > 60:
                warnings.append(f"Yüksek riskli IP (Risk: {ip_info.risk_score})")
            
            # Çok hızlı işlemler
            recent_actions = await self.db._fetchall(
                """SELECT COUNT(*) as count FROM system_logs 
                   WHERE user_id = ? AND timestamp > ? AND action NOT LIKE '%LOGIN%'""",
                (user_id, (datetime.now() - timedelta(minutes=5)).isoformat())
            )
            
            if recent_actions and recent_actions[0]['count'] > 10:
                warnings.append("Son 5 dakikada çok fazla işlem")
            
            # Şüpheli aktivite var mı?
            is_suspicious = len(warnings) >= 2 or any("VPN" in w or "Risk" in w for w in warnings)
            
            if is_suspicious:
                await self._log_security_event(
                    "SUSPICIOUS_ACTIVITY",
                    ip_address,
                    user_id,
                    f"Şüpheli aktivite tespit edildi: {', '.join(warnings)}",
                    "MEDIUM"
                )
            
            return is_suspicious, warnings
            
        except Exception as e:
            logger.error(f"Şüpheli aktivite kontrolü hatası: {e}")
            return False, []