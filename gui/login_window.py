# -*- coding: utf-8 -*-
"""
Modern giriş ekranı - Callback düzeltmesi
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import logging
import asyncio
import time
from typing import Callable

from core.auth import TokenAuthenticator

logger = logging.getLogger(__name__)

class LoginWindow:
    """Modern giriş ekranı sınıfı"""
    
    def __init__(self, parent, db_manager, settings, theme_manager, animation_manager, success_callback: Callable):
        self.parent = parent
        self.db = db_manager
        self.settings = settings
        self.theme = theme_manager
        self.animation = animation_manager
        self.success_callback = success_callback
        
        # Stats label referansı
        self.stats_label = None
        
        # Login işlemi için lock
        self._login_lock = threading.Lock()
        self._login_in_progress = False
        
        self.auth = TokenAuthenticator(db_manager, settings)
        
        # Ana frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_ui()
        
        # Animasyonlu giriş
        try:
            self.animation.fade_in(self.main_frame)
        except:
            pass  # Animasyon hatası durumunda devam et
        
        logger.info(f"LoginWindow başlatıldı, callback: {success_callback}")
    
    def setup_ui(self):
        """Kullanıcı arayüzünü kurulum"""
        # Ana container
        self.container = ttk.Frame(self.main_frame)
        self.container.place(relx=0.5, rely=0.5, anchor='center')
        
        # Logo ve başlık
        title_frame = ttk.Frame(self.container)
        title_frame.pack(pady=(0, 30))
        
        title_label = ttk.Label(
            title_frame,
            text="🤖 Modern Userbot Manager",
            font=("Segoe UI", 24, "bold")
        )
        title_label.pack()
        
        subtitle_label = ttk.Label(
            title_frame,
            text="Gelişmiş Telegram Userbot Yönetim Sistemi",
            font=("Segoe UI", 10)
        )
        subtitle_label.pack(pady=(5, 0))
        
        # Login kartı
        self.login_card = ttk.LabelFrame(
            self.container,
            text="Giriş Yap",
            padding=30
        )
        self.login_card.pack(pady=20, padx=40, fill=tk.X)
        
        # Tab control
        self.notebook = ttk.Notebook(self.login_card)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Kullanıcı girişi tab
        self.user_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_frame, text="👤 Kullanıcı Girişi")
        self.setup_user_login()
        
        # Yönetici girişi tab
        self.admin_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.admin_frame, text="👑 Yönetici Girişi")
        self.setup_admin_login()
        
        # Alt bilgi
        info_frame = ttk.Frame(self.container)
        info_frame.pack(pady=(20, 0))
        
        try:
            version = getattr(self.settings, 'APP_VERSION', '1.0.0')
        except:
            version = '1.0.0'
        
        info_label = ttk.Label(
            info_frame,
            text=f"Sürüm {version} • Python 3.11+ Uyumlu",
            font=("Segoe UI", 8)
        )
        info_label.pack()
        
        # İstatistikler - başlangıçta boş stats label oluştur
        self.stats_label = ttk.Label(
            self.container,
            text="📊 İstatistikler yükleniyor...",
            font=("Segoe UI", 9),
            foreground="gray"
        )
        self.stats_label.pack(pady=(10, 0))
        
        # İstatistikleri yükle
        self.load_stats()
    
    def setup_user_login(self):
        """Kullanıcı giriş formunu kurulum"""
        # Token girişi
        token_label = ttk.Label(self.user_frame, text="🔑 Erişim Token'ı:")
        token_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.token_entry = ttk.Entry(
            self.user_frame,
            font=("Consolas", 10),
            width=50,
            show="*"
        )
        self.token_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Enter key binding for token entry
        self.token_entry.bind('<Return>', self.on_token_enter)
        self.token_entry.bind('<KP_Enter>', self.on_token_enter)  # Numpad Enter
        
        # Token göster/gizle
        self.show_token_var = tk.BooleanVar()
        show_token_check = ttk.Checkbutton(
            self.user_frame,
            text="Token'ı göster",
            variable=self.show_token_var,
            command=self.toggle_token_visibility
        )
        show_token_check.pack(anchor=tk.W, pady=(0, 15))
        
        # Giriş butonu
        self.user_login_btn = ttk.Button(
            self.user_frame,
            text="🚀 Giriş Yap",
            command=self.user_login,
            style="Accent.TButton"
        )
        self.user_login_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Bilgi metni
        info_text = (
            "💡 Token'ınız yoksa yöneticiden talep edebilirsiniz.\n"
            "🔒 Token'ınız güvenlidir ve şifrelenerek saklanır.\n"
            "⌨️ Enter tuşu ile de giriş yapabilirsiniz."
        )
        info_label = ttk.Label(
            self.user_frame,
            text=info_text,
            font=("Segoe UI", 9),
            foreground="gray"
        )
        info_label.pack(anchor=tk.W)
    
    def setup_admin_login(self):
        """Yönetici giriş formunu kurulum"""
        # Şifre girişi
        password_label = ttk.Label(self.admin_frame, text="🔐 Yönetici Şifresi:")
        password_label.pack(anchor=tk.W, pady=(0, 5))
        
        self.password_entry = ttk.Entry(
            self.admin_frame,
            font=("Consolas", 12),
            width=30,
            show="*"
        )
        self.password_entry.pack(fill=tk.X, pady=(0, 15))
        
        # Enter key binding for password entry
        self.password_entry.bind('<Return>', self.on_password_enter)
        self.password_entry.bind('<KP_Enter>', self.on_password_enter)  # Numpad Enter
        
        # Şifre göster/gizle
        self.show_password_var = tk.BooleanVar()
        show_password_check = ttk.Checkbutton(
            self.admin_frame,
            text="Şifreyi göster",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        show_password_check.pack(anchor=tk.W, pady=(0, 15))
        
        # Giriş butonu
        self.admin_login_btn = ttk.Button(
            self.admin_frame,
            text="👑 Yönetici Girişi",
            command=self.admin_login,
            style="Accent.TButton"
        )
        self.admin_login_btn.pack(fill=tk.X, pady=(0, 10))
        
        # Uyarı metni
        warning_text = (
            "⚠️ Yönetici paneline sadece yetkili kişiler erişebilir.\n"
            "🛡️ Tüm yönetici işlemleri loglanır ve izlenir.\n"
            "⌨️ Enter tuşu ile de giriş yapabilirsiniz."
        )
        warning_label = ttk.Label(
            self.admin_frame,
            text=warning_text,
            font=("Segoe UI", 9),
            foreground="orange"
        )
        warning_label.pack(anchor=tk.W)
    
    def on_token_enter(self, event):
        """Token entry'de Enter tuşuna basıldığında"""
        try:
            self.user_login()
        except Exception as e:
            logger.error(f"Token enter hatası: {e}")
    
    def on_password_enter(self, event):
        """Password entry'de Enter tuşuna basıldığında"""
        try:
            self.admin_login()
        except Exception as e:
            logger.error(f"Password enter hatası: {e}")
    
    def toggle_token_visibility(self):
        """Token görünürlüğünü değiştir"""
        try:
            show = self.show_token_var.get()
            self.token_entry.config(show="" if show else "*")
        except Exception as e:
            logger.error(f"Token görünürlük hatası: {e}")
    
    def toggle_password_visibility(self):
        """Şifre görünürlüğünü değiştir"""
        try:
            show = self.show_password_var.get()
            self.password_entry.config(show="" if show else "*")
        except Exception as e:
            logger.error(f"Şifre görünürlük hatası: {e}")
    
    def user_login(self):
        """Kullanıcı girişi işlemi"""
        if self._login_in_progress:
            return
        
        try:
            token = self.token_entry.get().strip()
            
            if not token:
                messagebox.showerror("Hata", "Lütfen token'ınızı girin.")
                return
            
            # Login durumunu set et
            self._login_in_progress = True
            
            # Butonu devre dışı bırak
            self.user_login_btn.config(state='disabled', text="Giriş yapılıyor...")
            
            logger.info("Kullanıcı girişi başlatılıyor...")
            
            # Thread güvenli giriş işlemi
            def safe_user_login():
                error_message = None
                result = None
                
                try:
                    ip_address = "127.0.0.1"
                    
                    logger.info("Auth.user_login çağrılıyor...")
                    result = self.run_async_in_thread(
                        self.auth.user_login(token, ip_address)
                    )
                    logger.info(f"Auth.user_login sonucu: {result}")
                    
                except Exception as e:
                    logger.error(f"Kullanıcı giriş hatası: {e}")
                    error_message = str(e)
                
                finally:
                    self._login_in_progress = False
                
                # UI güncellemesini ana thread'e gönder
                def update_ui():
                    if error_message:
                        self.handle_login_error(error_message, False)
                    else:
                        self.handle_login_result(result, False)
                
                try:
                    self.parent.after(0, update_ui)
                except Exception as ui_error:
                    logger.error(f"UI güncelleme hatası: {ui_error}")
            
            # Thread başlat
            threading.Thread(target=safe_user_login, daemon=True).start()
            
        except Exception as e:
            logger.error(f"User login setup hatası: {e}")
            self._login_in_progress = False
            self.user_login_btn.config(state='normal', text="🚀 Giriş Yap")
            messagebox.showerror("Hata", f"Giriş başlatılamadı: {e}")
    
    def admin_login(self):
        """Yönetici girişi işlemi - Geliştirilmiş debug"""
        if self._login_in_progress:
            logger.warning("Login zaten devam ediyor, yeni girişim engellendi")
            return
        
        try:
            password = self.password_entry.get()
            
            if not password:
                messagebox.showerror("Hata", "Lütfen şifrenizi girin.")
                return
            
            logger.info("Admin girişi başlatılıyor...")
            
            # Login durumunu set et
            self._login_in_progress = True
            
            # Butonu devre dışı bırak
            self.admin_login_btn.config(state='disabled', text="Giriş yapılıyor...")
            
            # Geliştirilmiş admin giriş işlemi
            def robust_admin_login():
                error_message = None
                result = None
                
                try:
                    ip_address = "127.0.0.1"
                    
                    logger.info(f"Admin şifre kontrolü: {password[:3]}...")
                    logger.info("Auth.admin_login çağrılıyor...")
                    
                    # Timeout ile async call
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(
                            self.run_async_in_thread_with_timeout,
                            self.auth.admin_login(password, ip_address),
                            timeout=30  # 30 saniye timeout
                        )
                        result = future.result()
                    
                    logger.info(f"Auth.admin_login sonucu: {result}")
                    
                    if not result:
                        error_message = "Admin login sonucu None döndü"
                    
                except Exception as e:
                    logger.error(f"Admin login hatası: {e}")
                    error_message = str(e)
                
                finally:
                    self._login_in_progress = False
                
                # UI güncellemesini ana thread'e gönder
                def update_ui():
                    try:
                        if error_message:
                            self.handle_login_error(error_message, True)
                        else:
                            self.handle_login_result(result, True)
                    except Exception as ui_error:
                        logger.error(f"UI güncelleme hatası: {ui_error}")
                        self.admin_login_btn.config(state='normal', text="👑 Yönetici Girişi")
                        messagebox.showerror("Hata", f"UI güncelleme hatası: {ui_error}")
                
                try:
                    self.parent.after(0, update_ui)
                except Exception as after_error:
                    logger.error(f"After hatası: {after_error}")
            
            # Thread başlat
            threading.Thread(target=robust_admin_login, daemon=True).start()
            
        except Exception as e:
            logger.error(f"Admin login setup hatası: {e}")
            self._login_in_progress = False
            self.admin_login_btn.config(state='normal', text="👑 Yönetici Girişi")
            messagebox.showerror("Hata", f"Giriş başlatılamadı: {e}")
    
    def handle_login_result(self, result, is_admin: bool):
        """Giriş sonucunu işle - Callback debug eklendi"""
        try:
            logger.info(f"Login result handling: {result}, is_admin: {is_admin}")
            
            # Butonları tekrar aktif et
            if is_admin:
                self.admin_login_btn.config(state='normal', text="👑 Yönetici Girişi")
            else:
                self.user_login_btn.config(state='normal', text="🚀 Giriş Yap")
            
            if result and hasattr(result, 'success') and result.success:
                # Başarılı giriş
                user_data = {
                    'user_id': getattr(result, 'user_id', None),
                    'username': getattr(result, 'username', 'Unknown'),
                    'token': getattr(result, 'token', ''),
                    'is_admin': getattr(result, 'is_admin', is_admin)
                }
                
                logger.info(f"Başarılı giriş: {user_data}")
                logger.info(f"Success callback: {self.success_callback}")
                
                # Hoş geldin mesajı
                messagebox.showinfo("Başarılı", f"Hoş geldiniz, {user_data['username']}!")
                
                # Callback'i güvenli şekilde çağır
                try:
                    logger.info("Success callback çağrılıyor...")
                    
                    # Animasyon olmadan direkt callback
                    if self.success_callback:
                        self.success_callback(user_data)
                        logger.info("Success callback başarıyla çağrıldı")
                    else:
                        logger.error("Success callback None!")
                        messagebox.showerror("Hata", "Callback fonksiyonu bulunamadı!")
                        
                except Exception as callback_error:
                    logger.error(f"Callback çağırma hatası: {callback_error}")
                    messagebox.showerror("Hata", f"Panel açılırken hata oluştu: {callback_error}")
                    
                    # Fallback: Manuel panel açma denemeleri
                    try:
                        # Ana uygulama nesnesini bul ve manuel olarak panel aç
                        self.manual_panel_switch(user_data)
                    except Exception as manual_error:
                        logger.error(f"Manuel panel açma hatası: {manual_error}")
                        messagebox.showerror("Kritik Hata", "Panel açılamadı, lütfen uygulamayı yeniden başlatın!")
                
            else:
                # Hatalı giriş
                error_msg = getattr(result, 'error_message', 'Bilinmeyen hata')
                logger.warning(f"Giriş başarısız: {error_msg}")
                messagebox.showerror("Giriş Hatası", error_msg)
                
                # Form alanlarını temizle
                self.clear_form_fields(is_admin)
                
        except Exception as e:
            logger.error(f"Login result handling hatası: {e}")
            # Butonları tekrar aktif et
            if is_admin:
                self.admin_login_btn.config(state='normal', text="👑 Yönetici Girişi")
            else:
                self.user_login_btn.config(state='normal', text="🚀 Giriş Yap")
            messagebox.showerror("Hata", f"Giriş sonucu işlenirken hata oluştu: {e}")
    
    def manual_panel_switch(self, user_data):
        """Manuel panel değiştirme denemesi"""
        try:
            logger.info("Manuel panel açma denemesi başlatılıyor...")
            
            # Parent widget'ın ana uygulama nesnesini bul
            root = self.parent
            while root.master:
                root = root.master
            
            logger.info(f"Root widget bulundu: {root}")
            
            # Root'ta main application nesnesini ara
            if hasattr(root, '_main_app'):
                main_app = root._main_app
                logger.info(f"Main app bulundu: {main_app}")
                
                if hasattr(main_app, 'on_login_success'):
                    logger.info("on_login_success metodu çağrılıyor...")
                    main_app.on_login_success(user_data)
                    return
            
            # Alternatif: Widget hiyerarşisinde ara
            for child in root.winfo_children():
                if hasattr(child, 'on_login_success'):
                    logger.info(f"on_login_success child'da bulundu: {child}")
                    child.on_login_success(user_data)
                    return
            
            raise Exception("Panel açma metodu bulunamadı")
            
        except Exception as e:
            logger.error(f"Manuel panel açma hatası: {e}")
            raise
    
    def handle_login_error(self, error_message: str, is_admin: bool):
        """Giriş hatasını işle"""
        try:
            logger.error(f"Login error: {error_message}, is_admin: {is_admin}")
            
            # Butonları tekrar aktif et
            if is_admin:
                self.admin_login_btn.config(state='normal', text="👑 Yönetici Girişi")
            else:
                self.user_login_btn.config(state='normal', text="🚀 Giriş Yap")
            
            # Hata mesajını kullanıcı dostu hale getir
            if "UNIQUE constraint failed" in error_message:
                error_message = "Sistem yoğun, lütfen birkaç saniye bekleyip tekrar deneyin."
            elif "timeout" in error_message.lower():
                error_message = "İşlem zaman aşımına uğradı, lütfen tekrar deneyin."
            elif "None döndü" in error_message:
                error_message = "Giriş işlemi tamamlanamadı, lütfen tekrar deneyin."
            
            messagebox.showerror("Giriş Hatası", f"Giriş yapılırken hata oluştu:\n{error_message}")
            
            # Form alanlarını temizle
            self.clear_form_fields(is_admin)
            
        except Exception as e:
            logger.error(f"Login error handling hatası: {e}")
    
    def clear_form_fields(self, is_admin: bool):
        """Form alanlarını temizle"""
        try:
            if is_admin:
                self.password_entry.delete(0, tk.END)
            else:
                self.token_entry.delete(0, tk.END)
        except Exception as e:
            logger.error(f"Form temizleme hatası: {e}")
    
    def run_async_in_thread(self, coro):
        """Async işlemi thread içinde çalıştır"""
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        except Exception as e:
            logger.error(f"Async işlem hatası: {e}")
            raise
        finally:
            if loop:
                try:
                    loop.close()
                except:
                    pass
    
    def run_async_in_thread_with_timeout(self, coro, timeout=30):
        """Timeout ile async işlemi çalıştır"""
        loop = None
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(asyncio.wait_for(coro, timeout=timeout))
        except asyncio.TimeoutError:
            logger.error(f"Async işlem timeout ({timeout}s)")
            raise Exception(f"İşlem zaman aşımına uğradı ({timeout}s)")
        except Exception as e:
            logger.error(f"Async işlem hatası: {e}")
            raise
        finally:
            if loop:
                try:
                    loop.close()
                except:
                    pass
    
    def load_stats(self):
        """İstatistikleri yükle"""
        def safe_load_stats():
            try:
                # Basit istatistikler
                user_count = self.run_async_in_thread(
                    self.db._fetchone("SELECT COUNT(*) as count FROM users WHERE is_active = TRUE")
                )
                
                # İstatistik metni hazırla
                count = user_count['count'] if user_count and 'count' in user_count else 0
                stats_text = f"👥 {count} Aktif Kullanıcı"
                
                # UI güncelle - thread-safe şekilde
                def update_stats():
                    try:
                        if self.stats_label and self.stats_label.winfo_exists():
                            self.stats_label.config(text=stats_text)
                    except Exception as e:
                        logger.error(f"Stats UI update hatası: {e}")
                
                try:
                    self.parent.after(0, update_stats)
                except:
                    pass
                
            except Exception as e:
                logger.error(f"İstatistik yükleme hatası: {e}")
                # Hata durumunda varsayılan metin göster
                def show_error():
                    try:
                        if self.stats_label and self.stats_label.winfo_exists():
                            self.stats_label.config(text="📊 İstatistikler yüklenemedi")
                    except:
                        pass
                
                try:
                    self.parent.after(0, show_error)
                except:
                    pass
        
        threading.Thread(target=safe_load_stats, daemon=True).start()
    
    def destroy(self):
        """Widget'ı temizle"""
        try:
            # Login durumunu sıfırla
            self._login_in_progress = False
            
            # Ana frame'i temizle
            if hasattr(self, 'main_frame') and self.main_frame:
                self.main_frame.destroy()
        except Exception as e:
            logger.error(f"Widget temizleme hatası: {e}")