# -*- coding: utf-8 -*-
"""
Ana uygulama penceresi
"""

import tkinter as tk
from tkinter import ttk
import asyncio
import threading
import logging
from typing import Optional

from .login_window import LoginWindow
from .admin_panel import AdminPanel
from .user_panel import UserPanel
from .components.themes import ThemeManager
from .components.animations import AnimationManager

logger = logging.getLogger(__name__)

class MainApplication:
    """Ana uygulama sınıfı"""
    
    def __init__(self, db_manager, settings):
        self.db = db_manager
        self.settings = settings
        self.root: Optional[tk.Tk] = None
        self.current_user = None
        self.current_panel = None
        
        # Tema ve animasyon yöneticileri
        self.theme_manager = ThemeManager(settings)
        self.animation_manager = AnimationManager()
        
        # Asyncio event loop
        self.loop = None
        self.loop_thread = None
    
    async def initialize(self):
        """Uygulama başlatma"""
        # Ana pencereyi oluştur
        self.root = tk.Tk()
        self.root.title(self.settings.APP_NAME)
        self.root.geometry(f"{self.settings.WINDOW_WIDTH}x{self.settings.WINDOW_HEIGHT}")
        self.root.minsize(self.settings.MIN_WIDTH, self.settings.MIN_HEIGHT)
        
        # İkon ayarla (varsa)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
        
        # Tema uygula
        self.theme_manager.apply_theme(self.root)
        
        # Pencere kapama olayını yakala
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Event loop'u başlat
        self._start_event_loop()
        
        # Giriş ekranını göster
        self.show_login()
    
    def _start_event_loop(self):
        """Asyncio event loop'unu ayrı thread'de başlat"""
        def run_loop():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.run_forever()
        
        self.loop_thread = threading.Thread(target=run_loop, daemon=True)
        self.loop_thread.start()
    
    def run_async(self, coro):
        """Async fonksiyonu güvenli şekilde çalıştır"""
        if self.loop and not self.loop.is_closed():
            future = asyncio.run_coroutine_threadsafe(coro, self.loop)
            return future.result(timeout=10)
    
    def show_login(self):
        """Giriş ekranını göster"""
        if self.current_panel:
            self.current_panel.destroy()
        
        self.current_panel = LoginWindow(
            self.root, self.db, self.settings,
            self.theme_manager, self.animation_manager,
            self.on_login_success
        )
    
    def on_login_success(self, user_data):
        """Başarılı giriş sonrası çağrılır"""
        self.current_user = user_data
        
        if self.current_panel:
            self.current_panel.destroy()
        
        if user_data.get('is_admin'):
            self.current_panel = AdminPanel(
                self.root, self.db, self.settings,
                self.theme_manager, self.animation_manager,
                user_data, self.run_async, self.logout
            )
        else:
            self.current_panel = UserPanel(
                self.root, self.db, self.settings,
                self.theme_manager, self.animation_manager,
                user_data, self.run_async, self.logout
            )
    
    def logout(self):
        """Çıkış yap"""
        self.current_user = None
        self.show_login()
        
        # Çıkış logunu kaydet
        if self.current_user:
            self.run_async(
                self.db.log_action(
                    self.current_user.get('user_id'),
                    "LOGOUT",
                    "User logged out"
                )
            )
    
    def on_closing(self):
        """Uygulama kapatılırken çağrılır"""
        self.cleanup()
        self.root.destroy()
    
    def cleanup(self):
        """Temizlik işlemleri"""
        if self.loop and not self.loop.is_closed():
            self.loop.call_soon_threadsafe(self.loop.stop)
        
        if self.loop_thread and self.loop_thread.is_alive():
            self.loop_thread.join(timeout=1)
    
    def run(self):
        """Ana döngüyü başlat"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            logger.info("Uygulama kullanıcı tarafından sonlandırıldı")
        finally:
            self.cleanup()