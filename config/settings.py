# -*- coding: utf-8 -*-
"""
Uygulama yapılandırma ayarları
"""

import os
from pathlib import Path
from typing import Dict, Any

class AppSettings:
    """Uygulama ayarları sınıfı"""
    
    # Uygulama bilgileri
    APP_NAME = "Modern Userbot Manager"
    APP_VERSION = "2.0.0"
    APP_AUTHOR = "Userbot Manager Team"
    
    # Telegram API bilgileri
    API_ID = 29573842
    API_HASH = "521f832c7ed941063d140cd84b1adc1a"
    
    # Yönetici bilgileri
    ADMIN_PASSWORD = "urkuncbaba11"
    
    # Veritabanı ayarları
    DATABASE_NAME = "userbot_manager.db"
    
    # GUI ayarları
    WINDOW_WIDTH = 1200
    WINDOW_HEIGHT = 800
    MIN_WIDTH = 800
    MIN_HEIGHT = 600
    
    # Güvenlik ayarları
    TOKEN_LENGTH = 32
    SESSION_TIMEOUT = 3600  # 1 saat
    MAX_LOGIN_ATTEMPTS = 5
    IP_BAN_DURATION = 1800  # 30 dakika
    
    # Tema ayarları
    THEMES = {
        "dark": {
            "bg_primary": "#1a1a1a",
            "bg_secondary": "#2d2d2d",
            "bg_tertiary": "#3d3d3d",
            "text_primary": "#ffffff",
            "text_secondary": "#cccccc",
            "accent": "#4a9eff",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
            "border": "#555555"
        },
        "light": {
            "bg_primary": "#ffffff",
            "bg_secondary": "#f5f5f5",
            "bg_tertiary": "#e0e0e0",
            "text_primary": "#000000",
            "text_secondary": "#666666",
            "accent": "#2196f3",
            "success": "#4caf50",
            "warning": "#ff9800",
            "error": "#f44336",
            "border": "#cccccc"
        }
    }
    
    # Animasyon ayarları
    ANIMATION_SPEED = 0.3
    FADE_DURATION = 0.2
    
    def __init__(self):
        self.current_theme = "dark"
        self.data_dir = self._get_data_dir()
        self.ensure_directories()
    
    def _get_data_dir(self) -> Path:
        """Veri dizinini al"""
        if os.name == 'nt':  # Windows
            data_dir = Path(os.environ.get('APPDATA', '.')) / self.APP_NAME
        else:  # Linux/Mac
            data_dir = Path.home() / f'.{self.APP_NAME.lower().replace(" ", "_")}'
        
        return data_dir
    
    def ensure_directories(self):
        """Gerekli dizinleri oluştur"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "logs").mkdir(exist_ok=True)
        (self.data_dir / "sessions").mkdir(exist_ok=True)
    
    def get_theme_color(self, color_name: str) -> str:
        """Tema rengini al"""
        return self.THEMES[self.current_theme].get(color_name, "#000000")
    
    def get_database_path(self) -> str:
        """Veritabanı yolunu al"""
        return str(self.data_dir / self.DATABASE_NAME)