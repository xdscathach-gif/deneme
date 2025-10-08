# -*- coding: utf-8 -*-
"""
Yönetici paneli - Token ve IP yönetimi
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
import logging
from datetime import datetime, timedelta
from typing import Callable

from core.auth import TokenAuthenticator

logger = logging.getLogger(__name__)

class AdminPanel:
    """Yönetici yönetim paneli"""
    
    def __init__(self, parent, db_manager, settings, theme_manager, animation_manager, 
                 user_data, run_async_func: Callable, logout_callback: Callable):
        self.parent = parent
        self.db = db_manager
        self.settings = settings
        self.theme = theme_manager
        self.animation = animation_manager
        self.user_data = user_data
        self.run_async = run_async_func
        self.logout_callback = logout_callback
        
        self.auth = TokenAuthenticator(db_manager, settings)
        
        # Ana frame
        self.main_frame = ttk.Frame(parent)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        self.setup_ui()
        self.load_initial_data()
        
        # Animasyonlu giriş
        self.animation.fade_in(self.main_frame)
    
    def setup_ui(self):
        """Kullanıcı arayüzünü kurulum"""
        # Üst bar
        self.create_header()
        
        # Ana içerik
        self.content_frame = ttk.Frame(self.main_frame)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Notebook (tab control)
        self.notebook = ttk.Notebook(self.content_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab'ları oluştur
        self.create_dashboard_tab()
        self.create_token_management_tab()
        self.create_ip_security_tab()
        self.create_user_management_tab()
        self.create_system_logs_tab()
    
    def create_header(self):
        """Üst bar oluştur"""
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, padx=20, pady=(10, 0))
        
        # Sol taraf - başlık ve kullanıcı bilgisi
        left_frame = ttk.Frame(header_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        title_label = ttk.Label(
            left_frame,
            text="👑 Yönetici Paneli",
            font=("Segoe UI", 16, "bold")
        )
        title_label.pack(anchor=tk.W)
        
        user_info = f"Hoş geldiniz, {self.user_data.get('username', 'Admin')} • {datetime.now().strftime('%d.%m.%Y %H:%M')}"
        user_label = ttk.Label(
            left_frame,
            text=user_info,
            font=("Segoe UI", 9)
        )
        user_label.pack(anchor=tk.W)
        
        # Sağ taraf - butonlar
        right_frame = ttk.Frame(header_frame)
        right_frame.pack(side=tk.RIGHT)
        
        # Yenile butonu
        refresh_btn = ttk.Button(
            right_frame,
            text="🔄 Yenile",
            command=self.refresh_all_data
        )
        refresh_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Çıkış butonu
        logout_btn = ttk.Button(
            right_frame,
            text="🚪 Çıkış",
            command=self.logout_callback
        )
        logout_btn.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Ayırıcı
        separator = ttk.Separator(self.main_frame, orient='horizontal')
        separator.pack(fill=tk.X, padx=20, pady=5)
    
    def create_dashboard_tab(self):
        """Dashboard tab'ı oluştur"""
        self.dashboard_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dashboard_frame, text="📊 Dashboard")
        
        # İstatistik kartları
        stats_frame = ttk.Frame(self.dashboard_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        # İstatistik kartları için grid
        self.create_stat_card(stats_frame, "👥 Toplam Kullanıcı", "0", 0, 0)
        self.create_stat_card(stats_frame, "🔑 Aktif Token", "0", 0, 1)
        self.create_stat_card(stats_frame, "🤖 Aktif Userbot", "0", 0, 2)
        self.create_stat_card(stats_frame, "🚫 Yasaklı IP", "0", 0, 3)
        
        # Son aktiviteler
        activity_frame = ttk.LabelFrame(self.dashboard_frame, text="📋 Son Aktiviteler", padding=10)
        activity_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Aktivite listesi
        columns = ('Zaman', 'Kullanıcı', 'İşlem', 'IP')
        self.activity_tree = ttk.Treeview(activity_frame, columns=columns, show='headings', height=8)
        
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=150)
        
        # Scrollbar
        activity_scroll = ttk.Scrollbar(activity_frame, orient=tk.VERTICAL, command=self.activity_tree.yview)
        self.activity_tree.configure(yscrollcommand=activity_scroll.set)
        
        self.activity_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        activity_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_stat_card(self, parent, title: str, value: str, row: int, col: int):
        """İstatistik kartı oluştur"""
        card_frame = ttk.LabelFrame(parent, text=title, padding=15)
        card_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        
        value_label = ttk.Label(
            card_frame,
            text=value,
            font=("Segoe UI", 18, "bold")
        )
        value_label.pack()
        
        # Grid ağırlıkları
        parent.grid_columnconfigure(col, weight=1)
        
        return value_label
    
    def create_token_management_tab(self):
        """Token yönetimi tab'ı oluştur"""
        self.token_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.token_frame, text="🔑 Token Yönetimi")
        
        # Üst butonlar
        button_frame = ttk.Frame(self.token_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        create_token_btn = ttk.Button(
            button_frame,
            text="➕ Yeni Token Oluştur",
            command=self.create_new_token,
            style="Accent.TButton"
        )
        create_token_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        revoke_token_btn = ttk.Button(
            button_frame,
            text="🗑️ Token İptal Et",
            command=self.revoke_selected_token
        )
        revoke_token_btn.pack(side=tk.LEFT)
        
        # Token listesi
        token_columns = ('Token ID', 'Kullanıcı', 'Oluşturulma', 'Son Kullanım', 'Cihaz', 'Durum')
        self.token_tree = ttk.Treeview(self.token_frame, columns=token_columns, show='headings')
        
        for col in token_columns:
            self.token_tree.heading(col, text=col)
            self.token_tree.column(col, width=120)
        
        # Scrollbar
        token_scroll = ttk.Scrollbar(self.token_frame, orient=tk.VERTICAL, command=self.token_tree.yview)
        self.token_tree.configure(yscrollcommand=token_scroll.set)
        
        self.token_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        token_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_ip_security_tab(self):
        """IP güvenlik tab'ı oluştur"""
        self.ip_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.ip_frame, text="🛡️ IP Güvenlik")
        
        # Üst butonlar
        ip_button_frame = ttk.Frame(self.ip_frame)
        ip_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        ban_ip_btn = ttk.Button(
            ip_button_frame,
            text="🚫 IP Yasakla",
            command=self.ban_selected_ip
        )
        ban_ip_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        unban_ip_btn = ttk.Button(
            ip_button_frame,
            text="✅ Yasağı Kaldır",
            command=self.unban_selected_ip
        )
        unban_ip_btn.pack(side=tk.LEFT)
        
        # IP listesi
        ip_columns = ('IP Adresi', 'Kullanıcı', 'İlk Görülme', 'Son Görülme', 'Cihaz', 'Durum', 'Yasak Nedeni')
        self.ip_tree = ttk.Treeview(self.ip_frame, columns=ip_columns, show='headings')
        
        for col in ip_columns:
            self.ip_tree.heading(col, text=col)
            self.ip_tree.column(col, width=100)
        
        # Scrollbar
        ip_scroll = ttk.Scrollbar(self.ip_frame, orient=tk.VERTICAL, command=self.ip_tree.yview)
        self.ip_tree.configure(yscrollcommand=ip_scroll.set)
        
        self.ip_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ip_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_user_management_tab(self):
        """Kullanıcı yönetimi tab'ı oluştur"""
        self.user_mgmt_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.user_mgmt_frame, text="👥 Kullanıcı Yönetimi")
        
        # Kullanıcı işlemleri
        user_button_frame = ttk.Frame(self.user_mgmt_frame)
        user_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        premium_btn = ttk.Button(
            user_button_frame,
            text="💎 Premium Ver",
            command=self.give_premium
        )
        premium_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        limit_btn = ttk.Button(
            user_button_frame,
            text="📊 Limit Ayarla",
            command=self.set_user_limit
        )
        limit_btn.pack(side=tk.LEFT)
        
        # Kullanıcı listesi
        user_columns = ('ID', 'Kullanıcı Adı', 'E-posta', 'Premium', 'Limit', 'Kayıt Tarihi', 'Son Giriş')
        self.user_tree = ttk.Treeview(self.user_mgmt_frame, columns=user_columns, show='headings')
        
        for col in user_columns:
            self.user_tree.heading(col, text=col)
            self.user_tree.column(col, width=100)
        
        # Scrollbar
        user_scroll = ttk.Scrollbar(self.user_mgmt_frame, orient=tk.VERTICAL, command=self.user_tree.yview)
        self.user_tree.configure(yscrollcommand=user_scroll.set)
        
        self.user_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        user_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_system_logs_tab(self):
        """Sistem logları tab'ı oluştur"""
        self.logs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.logs_frame, text="📋 Sistem Logları")
        
        # Log filtreleme
        filter_frame = ttk.LabelFrame(self.logs_frame, text="Filtrele", padding=10)
        filter_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(filter_frame, text="İşlem Türü:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.log_filter_var = tk.StringVar(value="Tümü")
        filter_combo = ttk.Combobox(
            filter_frame,
            textvariable=self.log_filter_var,
            values=["Tümü", "LOGIN", "LOGOUT", "TOKEN_CREATED", "TOKEN_REVOKED", "IP_BANNED"],
            state="readonly",
            width=15
        )
        filter_combo.pack(side=tk.LEFT, padx=(0, 10))
        
        filter_btn = ttk.Button(
            filter_frame,
            text="🔍 Filtrele",
            command=self.apply_log_filter
        )
        filter_btn.pack(side=tk.LEFT)
        
        # Log listesi
        log_columns = ('Zaman', 'Kullanıcı', 'İşlem', 'Detay', 'IP')
        self.log_tree = ttk.Treeview(self.logs_frame, columns=log_columns, show='headings', height=15)
        
        for col in log_columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=120)
        
        # Scrollbar
        log_scroll = ttk.Scrollbar(self.logs_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=log_scroll.set)
        
        self.log_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def load_initial_data(self):
        """İlk verileri yükle"""
        self.load_dashboard_data()
        self.load_token_data()
        self.load_ip_data()
        self.load_user_data()
        self.load_log_data()
    
    def load_dashboard_data(self):
        """Dashboard verilerini yükle"""
        def load_data():
            try:
                # İstatistikleri al
                user_count = self.run_async(
                    self.db._fetchone("SELECT COUNT(*) as count FROM users WHERE is_active = TRUE")
                )
                
                token_count = self.run_async(
                    self.db._fetchone(
                        "SELECT COUNT(*) as count FROM tokens WHERE is_active = TRUE AND (expires_at IS NULL OR expires_at > ?)",
                        (datetime.now().isoformat(),)
                    )
                )
                
                userbot_count = self.run_async(
                    self.db._fetchone("SELECT COUNT(*) as count FROM userbots")
                )
                
                banned_ip_count = self.run_async(
                    self.db._fetchone("SELECT COUNT(DISTINCT ip_address) as count FROM ip_security WHERE is_banned = TRUE")
                )
                
                # Son aktiviteler
                recent_logs = self.run_async(self.db.get_recent_logs(10))
                
                # UI güncelle
                self.parent.after(0, lambda: self.update_dashboard_stats({
                    'users': user_count['count'] if user_count else 0,
                    'tokens': token_count['count'] if token_count else 0,
                    'userbots': userbot_count['count'] if userbot_count else 0,
                    'banned_ips': banned_ip_count['count'] if banned_ip_count else 0,
                    'recent_logs': recent_logs
                }))
                
            except Exception as e:
                logger.error(f"Dashboard veri yükleme hatası: {e}")
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_dashboard_stats(self, stats):
        """Dashboard istatistiklerini güncelle"""
        # İstatistik kartlarını güncelle (implementation gerekli)
        pass
    
    def create_new_token(self):
        """Yeni token oluştur"""
        # Dialog açarak kullanıcı bilgilerini al
        dialog = TokenCreationDialog(self.parent, self.auth, self.db)
        result = dialog.show()
        
        if result:
            self.load_token_data()
            messagebox.showinfo("Başarılı", f"Token oluşturuldu!\n\nToken: {result['token']}\n\nBu token'ı güvenli bir yerde saklayın.")
    
    def revoke_selected_token(self):
        """Seçili token'ı iptal et"""
        selection = self.token_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen iptal edilecek token'ı seçin.")
            return
        
        token_id = self.token_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Onay", f"'{token_id}' token'ını iptal etmek istediğinizden emin misiniz?"):
            def revoke_token():
                try:
                    success = self.run_async(self.auth.revoke_token("", self.user_data['user_id']))
                    if success:
                        self.parent.after(0, lambda: [
                            self.load_token_data(),
                            messagebox.showinfo("Başarılı", "Token başarıyla iptal edildi.")
                        ])
                    else:
                        self.parent.after(0, lambda: messagebox.showerror("Hata", "Token iptal edilemedi."))
                except Exception as e:
                    logger.error(f"Token iptal hatası: {e}")
                    self.parent.after(0, lambda: messagebox.showerror("Hata", f"Token iptal edilirken hata: {e}"))
            
            threading.Thread(target=revoke_token, daemon=True).start()
    
    def load_token_data(self):
        """Token verilerini yükle"""
        def load_data():
            try:
                tokens = self.run_async(self.auth.get_active_tokens())
                self.parent.after(0, lambda: self.update_token_tree(tokens))
            except Exception as e:
                logger.error(f"Token veri yükleme hatası: {e}")
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_token_tree(self, tokens):
        """Token ağacını güncelle"""
        # Mevcut verileri temizle
        for item in self.token_tree.get_children():
            self.token_tree.delete(item)
        
        # Yeni verileri ekle
        for token in tokens:
            created_at = datetime.fromisoformat(token['created_at']).strftime('%d.%m.%Y %H:%M')
            last_used = "Hiç" if not token['last_used'] else datetime.fromisoformat(token['last_used']).strftime('%d.%m.%Y %H:%M')
            
            self.token_tree.insert('', 'end', values=(
                token['token_id'],
                token['username'],
                created_at,
                last_used,
                token['device_info'] or "Bilinmiyor",
                "Aktif"
            ))
    
    def load_ip_data(self):
        """IP verilerini yükle"""
        def load_data():
            try:
                ips = self.run_async(
                    self.db._fetchall(
                        """SELECT ip.*, u.username FROM ip_security ip
                           LEFT JOIN users u ON ip.user_id = u.user_id
                           ORDER BY ip.last_seen DESC"""
                    )
                )
                self.parent.after(0, lambda: self.update_ip_tree(ips))
            except Exception as e:
                logger.error(f"IP veri yükleme hatası: {e}")
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_ip_tree(self, ips):
        """IP ağacını güncelle"""
        # Mevcut verileri temizle
        for item in self.ip_tree.get_children():
            self.ip_tree.delete(item)
        
        # Yeni verileri ekle
        for ip in ips:
            first_seen = datetime.fromisoformat(ip['first_seen']).strftime('%d.%m.%Y %H:%M')
            last_seen = datetime.fromisoformat(ip['last_seen']).strftime('%d.%m.%Y %H:%M')
            status = "Yasaklı" if ip['is_banned'] else "Normal"
            
            self.ip_tree.insert('', 'end', values=(
                ip['ip_address'],
                ip['username'] or "Bilinmiyor",
                first_seen,
                last_seen,
                ip['device_info'] or "Bilinmiyor",
                status,
                ip['ban_reason'] or ""
            ))
    
    def ban_selected_ip(self):
        """Seçili IP'yi yasakla"""
        selection = self.ip_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen yasaklanacak IP'yi seçin.")
            return
        
        ip_address = self.ip_tree.item(selection[0])['values'][0]
        
        # Yasak nedeni sor
        reason = simpledialog.askstring("Yasak Nedeni", f"'{ip_address}' IP'sini neden yasaklıyorsunuz?")
        if not reason:
            return
        
        def ban_ip():
            try:
                self.run_async(self.db.ban_ip(ip_address, reason, 60))  # 1 saat yasak
                self.parent.after(0, lambda: [
                    self.load_ip_data(),
                    messagebox.showinfo("Başarılı", f"IP adresi yasaklandı: {ip_address}")
                ])
            except Exception as e:
                logger.error(f"IP yasaklama hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"IP yasaklanırken hata: {e}"))
        
        threading.Thread(target=ban_ip, daemon=True).start()
    
    def unban_selected_ip(self):
        """Seçili IP'nin yasağını kaldır"""
        selection = self.ip_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen yasağı kaldırılacak IP'yi seçin.")
            return
        
        ip_address = self.ip_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Onay", f"'{ip_address}' IP'sinin yasağını kaldırmak istediğinizden emin misiniz?"):
            def unban_ip():
                try:
                    self.run_async(self.db.unban_ip(ip_address))
                    self.parent.after(0, lambda: [
                        self.load_ip_data(),
                        messagebox.showinfo("Başarılı", f"IP yasağı kaldırıldı: {ip_address}")
                    ])
                except Exception as e:
                    logger.error(f"IP yasak kaldırma hatası: {e}")
                    self.parent.after(0, lambda: messagebox.showerror("Hata", f"IP yasağı kaldırılırken hata: {e}"))
            
            threading.Thread(target=unban_ip, daemon=True).start()
    
    def load_user_data(self):
        """Kullanıcı verilerini yükle"""
        def load_data():
            try:
                users = self.run_async(
                    self.db._fetchall(
                        "SELECT * FROM users WHERE is_active = TRUE ORDER BY created_at DESC"
                    )
                )
                self.parent.after(0, lambda: self.update_user_tree(users))
            except Exception as e:
                logger.error(f"Kullanıcı veri yükleme hatası: {e}")
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_user_tree(self, users):
        """Kullanıcı ağacını güncelle"""
        # Mevcut verileri temizle
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)
        
        # Yeni verileri ekle
        for user in users:
            premium_status = "Evet" if user['premium_expiry_date'] and datetime.fromisoformat(user['premium_expiry_date']) > datetime.now() else "Hayır"
            created_at = datetime.fromisoformat(user['created_at']).strftime('%d.%m.%Y')
            last_login = "Hiç" if not user['last_login'] else datetime.fromisoformat(user['last_login']).strftime('%d.%m.%Y %H:%M')
            
            self.user_tree.insert('', 'end', values=(
                user['user_id'],
                user['username'],
                user['email'] or "Yok",
                premium_status,
                user['account_limit'],
                created_at,
                last_login
            ))
    
    def give_premium(self):
        """Kullanıcıya premium ver"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen premium verilecek kullanıcıyı seçin.")
            return
        
        user_id = self.user_tree.item(selection[0])['values'][0]
        username = self.user_tree.item(selection[0])['values'][1]
        
        # Süre sor
        days = simpledialog.askinteger("Premium Süre", f"'{username}' kullanıcısına kaç gün premium verilsin?", minvalue=1, maxvalue=365)
        if not days:
            return
        
        def give_premium():
            try:
                expiry_date = datetime.now() + timedelta(days=days)
                self.run_async(
                    self.db._execute(
                        "UPDATE users SET premium_start_date = ?, premium_expiry_date = ? WHERE user_id = ?",
                        (datetime.now().isoformat(), expiry_date.isoformat(), user_id)
                    )
                )
                
                self.parent.after(0, lambda: [
                    self.load_user_data(),
                    messagebox.showinfo("Başarılı", f"{username} kullanıcısına {days} gün premium verildi.")
                ])
            except Exception as e:
                logger.error(f"Premium verme hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"Premium verilirken hata: {e}"))
        
        threading.Thread(target=give_premium, daemon=True).start()
    
    def set_user_limit(self):
        """Kullanıcı limitini ayarla"""
        selection = self.user_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen limitini ayarlanacak kullanıcıyı seçin.")
            return
        
        user_id = self.user_tree.item(selection[0])['values'][0]
        username = self.user_tree.item(selection[0])['values'][1]
        current_limit = self.user_tree.item(selection[0])['values'][4]
        
        # Yeni limit sor
        new_limit = simpledialog.askinteger(
            "Hesap Limiti", 
            f"'{username}' kullanıcısının yeni hesap limiti?\n(Mevcut: {current_limit})", 
            minvalue=0, maxvalue=999,
            initialvalue=current_limit
        )
        if new_limit is None:
            return
        
        def set_limit():
            try:
                self.run_async(
                    self.db._execute(
                        "UPDATE users SET account_limit = ? WHERE user_id = ?",
                        (new_limit, user_id)
                    )
                )
                
                self.parent.after(0, lambda: [
                    self.load_user_data(),
                    messagebox.showinfo("Başarılı", f"{username} kullanıcısının hesap limiti {new_limit} olarak ayarlandı.")
                ])
            except Exception as e:
                logger.error(f"Limit ayarlama hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"Limit ayarlanırken hata: {e}"))
        
        threading.Thread(target=set_limit, daemon=True).start()
    
    def load_log_data(self):
        """Log verilerini yükle"""
        def load_data():
            try:
                logs = self.run_async(self.db.get_recent_logs(200))
                self.parent.after(0, lambda: self.update_log_tree(logs))
            except Exception as e:
                logger.error(f"Log veri yükleme hatası: {e}")
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_log_tree(self, logs):
        """Log ağacını güncelle"""
        # Mevcut verileri temizle
        for item in self.log_tree.get_children():
            self.log_tree.delete(item)
        
        # Yeni verileri ekle
        for log in logs:
            timestamp = datetime.fromisoformat(log['timestamp']).strftime('%d.%m.%Y %H:%M:%S')
            
            self.log_tree.insert('', 'end', values=(
                timestamp,
                log['username'] or "Sistem",
                log['action'],
                log['details'] or "",
                log['ip_address'] or ""
            ))
    
    def apply_log_filter(self):
        """Log filtresini uygula"""
        filter_value = self.log_filter_var.get()
        # Filter implementation gerekli
        self.load_log_data()
    
    def refresh_all_data(self):
        """Tüm verileri yenile"""
        self.load_initial_data()
        messagebox.showinfo("Bilgi", "Veriler yenilendi.")
    
    def destroy(self):
        """Widget'ı temizle"""
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.destroy()


class TokenCreationDialog:
    """Token oluşturma dialog'u"""
    
    def __init__(self, parent, auth_manager, db_manager):
        self.parent = parent
        self.auth = auth_manager
        self.db = db_manager
        self.result = None
        
        # Dialog penceresi
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yeni Token Oluştur")
        self.dialog.geometry("400x300")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.setup_ui()
        
        # Pencereyi ortala
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
    
    def setup_ui(self):
        """Dialog UI'sını kur"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Başlık
        title_label = ttk.Label(main_frame, text="🔑 Yeni Token Oluştur", font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Kullanıcı adı
        ttk.Label(main_frame, text="Kullanıcı Adı:").pack(anchor=tk.W)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill=tk.X, pady=(5, 15))
        
        # E-posta
        ttk.Label(main_frame, text="E-posta (opsiyonel):").pack(anchor=tk.W)
        self.email_entry = ttk.Entry(main_frame, width=30)
        self.email_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Süre
        ttk.Label(main_frame, text="Geçerlilik Süresi (gün):").pack(anchor=tk.W)
        self.days_var = tk.IntVar(value=30)
        days_spinbox = ttk.Spinbox(main_frame, from_=1, to=365, textvariable=self.days_var, width=10)
        days_spinbox.pack(anchor=tk.W, pady=(5, 15))
        
        # Cihaz bilgisi
        ttk.Label(main_frame, text="Cihaz Bilgisi (opsiyonel):").pack(anchor=tk.W)
        self.device_entry = ttk.Entry(main_frame, width=30)
        self.device_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        create_btn = ttk.Button(button_frame, text="Oluştur", command=self.create_token, style="Accent.TButton")
        create_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = ttk.Button(button_frame, text="İptal", command=self.dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
    
    def create_token(self):
        """Token oluştur"""
        username = self.username_entry.get().strip()
        if not username:
            messagebox.showerror("Hata", "Kullanıcı adı gerekli!")
            return
        
        email = self.email_entry.get().strip() or None
        days = self.days_var.get()
        device_info = self.device_entry.get().strip() or None
        
        def create_token_thread():
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                token, user_id = loop.run_until_complete(
                    self.auth.create_user_token(username, email, days, device_info)
                )
                
                self.result = {'token': token, 'user_id': user_id}
                self.dialog.after(0, self.dialog.destroy)
                
            except Exception as e:
                self.dialog.after(0, lambda: messagebox.showerror("Hata", f"Token oluşturulamadı: {e}"))
            finally:
                loop.close()
        
        threading.Thread(target=create_token_thread, daemon=True).start()
    
    def show(self):
        """Dialog'u göster ve sonucu döndür"""
        self.dialog.wait_window()
        return self.result