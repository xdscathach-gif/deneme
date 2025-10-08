#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Userbot Manager
Telegram Userbot Yönetim Sistemi
Python 3.11+ Uyumlu
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Proje kök dizinini sys.path'e ekle
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainApplication
from config.database import DatabaseManager
from config.settings import AppSettings

# Logging yapılandırması
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('userbot_manager.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class UserbotManagerApp:
    """Ana uygulama sınıfı"""
    
    def __init__(self):
        self.settings = AppSettings()
        self.db_manager = DatabaseManager()
        self.main_app = None
        
    async def initialize(self):
        """Uygulama başlatma işlemleri"""
        try:
            logger.info("Userbot Manager başlatılıyor...")
            
            # Veritabanını başlat
            await self.db_manager.initialize()
            logger.info("Veritabanı başlatıldı")
            
            # GUI'yi başlat
            self.main_app = MainApplication(self.db_manager, self.settings)
            await self.main_app.initialize()
            
            logger.info("Uygulama başarıyla başlatıldı")
            
        except Exception as e:
            logger.error(f"Uygulama başlatma hatası: {e}")
            raise
    
    def run(self):
        """Uygulamayı çalıştır"""
        try:
            # Asyncio event loop'u başlat
            if sys.platform == "win32":
                asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            # Uygulamayı başlat
            loop.run_until_complete(self.initialize())
            self.main_app.run()
            
        except KeyboardInterrupt:
            logger.info("Uygulama kullanıcı tarafından sonlandırıldı")
        except Exception as e:
            logger.error(f"Kritik hata: {e}")
        finally:
            if self.main_app:
                self.main_app.cleanup()
            if hasattr(self, 'db_manager'):
                asyncio.run(self.db_manager.close())

def main():
    """Ana giriş noktası"""
    if getattr(sys, 'frozen', False):
        # PyInstaller ile derlenmişse
        os.chdir(sys._MEIPASS)
    
    app = UserbotManagerApp()
    app.run()

if __name__ == "__main__":
    main()