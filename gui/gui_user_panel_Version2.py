# create_stat_card metodunun devamı

    def create_stat_card(self, parent, title: str, value: str, row: int, col: int):
        """İstatistik kartı oluştur"""
        card_frame = ttk.LabelFrame(parent, text=title, padding=15)
        card_frame.grid(row=row, column=col, padx=10, pady=5, sticky="ew")
        
        value_label = ttk.Label(
            card_frame,
            text=value,
            font=("Segoe UI", 16, "bold")
        )
        value_label.pack()
        
        # Grid ağırlıkları
        parent.grid_columnconfigure(col, weight=1)
        
        return value_label
    
    def create_accounts_tab(self):
        """Hesaplar tab'ı oluştur"""
        self.accounts_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.accounts_frame, text="🤖 Hesaplarım")
        
        # Üst butonlar
        button_frame = ttk.Frame(self.accounts_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_btn = ttk.Button(
            button_frame,
            text="➕ Hesap Ekle",
            command=self.show_add_account_dialog,
            style="Accent.TButton"
        )
        add_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_btn = ttk.Button(
            button_frame,
            text="🗑️ Seçili Hesabı Sil",
            command=self.delete_selected_account
        )
        delete_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        settings_btn = ttk.Button(
            button_frame,
            text="⚙️ Hesap Ayarları",
            command=self.show_account_settings
        )
        settings_btn.pack(side=tk.LEFT)
        
        # Hesap listesi
        account_columns = ('Oturum Adı', 'Telefon', 'Durum', 'Oto Mesaj', 'Oto Cevap', 'Son Aktivite')
        self.account_tree = ttk.Treeview(self.accounts_frame, columns=account_columns, show='headings')
        
        for col in account_columns:
            self.account_tree.heading(col, text=col)
            self.account_tree.column(col, width=120)
        
        # Çift tıklama olayı
        self.account_tree.bind('<Double-1>', self.on_account_double_click)
        
        # Scrollbar
        account_scroll = ttk.Scrollbar(self.accounts_frame, orient=tk.VERTICAL, command=self.account_tree.yview)
        self.account_tree.configure(yscrollcommand=account_scroll.set)
        
        self.account_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        account_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_automation_tab(self):
        """Otomasyon tab'ı oluştur"""
        self.automation_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.automation_frame, text="🚀 Otomasyon")
        
        # Sol panel - Seçili hesap ayarları
        left_panel = ttk.LabelFrame(self.automation_frame, text="⚙️ Hesap Ayarları", padding=10)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Hesap seçici
        ttk.Label(left_panel, text="Hesap Seç:", font=("Segoe UI", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.selected_account_var = tk.StringVar()
        self.account_combo = ttk.Combobox(
            left_panel,
            textvariable=self.selected_account_var,
            state="readonly",
            width=30
        )
        self.account_combo.pack(fill=tk.X, pady=(0, 15))
        self.account_combo.bind('<<ComboboxSelected>>', self.on_account_selected)
        
        # Otomatik mesaj ayarları
        auto_msg_frame = ttk.LabelFrame(left_panel, text="📤 Otomatik Mesaj", padding=10)
        auto_msg_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_msg_enabled = tk.BooleanVar()
        auto_msg_check = ttk.Checkbutton(
            auto_msg_frame,
            text="Otomatik mesaj gönderimi aktif",
            variable=self.auto_msg_enabled,
            command=self.toggle_auto_message
        )
        auto_msg_check.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(auto_msg_frame, text="Mesaj Metni:").pack(anchor=tk.W)
        self.auto_msg_text = tk.Text(auto_msg_frame, height=4, wrap=tk.WORD)
        self.auto_msg_text.pack(fill=tk.X, pady=(5, 10))
        
        # Zaman ayarları
        time_frame = ttk.Frame(auto_msg_frame)
        time_frame.pack(fill=tk.X)
        
        ttk.Label(time_frame, text="Küme Aralığı (sn):").pack(side=tk.LEFT)
        self.delay_min_var = tk.IntVar(value=30)
        self.delay_max_var = tk.IntVar(value=90)
        
        ttk.Spinbox(time_frame, from_=10, to=300, textvariable=self.delay_min_var, width=8).pack(side=tk.LEFT, padx=(5, 5))
        ttk.Label(time_frame, text="-").pack(side=tk.LEFT)
        ttk.Spinbox(time_frame, from_=10, to=300, textvariable=self.delay_max_var, width=8).pack(side=tk.LEFT, padx=(5, 10))
        
        ttk.Label(time_frame, text="Tur Aralığı (dk):").pack(side=tk.LEFT)
        self.loop_cooldown_var = tk.IntVar(value=60)
        ttk.Spinbox(time_frame, from_=10, to=1440, textvariable=self.loop_cooldown_var, width=8).pack(side=tk.LEFT, padx=(5, 0))
        
        # Otomatik cevap ayarları
        auto_reply_frame = ttk.LabelFrame(left_panel, text="💬 Otomatik Cevap", padding=10)
        auto_reply_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.auto_reply_enabled = tk.BooleanVar()
        auto_reply_check = ttk.Checkbutton(
            auto_reply_frame,
            text="DM otomatik cevap aktif",
            variable=self.auto_reply_enabled,
            command=self.toggle_auto_reply
        )
        auto_reply_check.pack(anchor=tk.W, pady=(0, 10))
        
        ttk.Label(auto_reply_frame, text="Cevap Metni:").pack(anchor=tk.W)
        self.auto_reply_text = tk.Text(auto_reply_frame, height=3, wrap=tk.WORD)
        self.auto_reply_text.pack(fill=tk.X, pady=(5, 0))
        
        # Kaydet butonu
        save_btn = ttk.Button(
            left_panel,
            text="💾 Ayarları Kaydet",
            command=self.save_automation_settings,
            style="Accent.TButton"
        )
        save_btn.pack(fill=tk.X, pady=(15, 0))
        
        # Sağ panel - Filtreler ve İstisna Sohbetler
        right_panel = ttk.Frame(self.automation_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Filtreler
        filters_frame = ttk.LabelFrame(right_panel, text="🎯 Otomatik Yanıt Filtreleri", padding=10)
        filters_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        filter_button_frame = ttk.Frame(filters_frame)
        filter_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_filter_btn = ttk.Button(
            filter_button_frame,
            text="➕ Filtre Ekle",
            command=self.add_filter
        )
        add_filter_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_filter_btn = ttk.Button(
            filter_button_frame,
            text="🗑️ Sil",
            command=self.delete_selected_filter
        )
        delete_filter_btn.pack(side=tk.LEFT)
        
        # Filtre listesi
        filter_columns = ('Tetikleyici', 'Yanıt', 'Durum')
        self.filter_tree = ttk.Treeview(filters_frame, columns=filter_columns, show='headings', height=6)
        
        for col in filter_columns:
            self.filter_tree.heading(col, text=col)
            self.filter_tree.column(col, width=100)
        
        filter_scroll = ttk.Scrollbar(filters_frame, orient=tk.VERTICAL, command=self.filter_tree.yview)
        self.filter_tree.configure(yscrollcommand=filter_scroll.set)
        
        self.filter_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        filter_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        # İstisna sohbetler
        excluded_frame = ttk.LabelFrame(right_panel, text="🚫 İstisna Sohbetler", padding=10)
        excluded_frame.pack(fill=tk.BOTH, expand=True)
        
        excluded_button_frame = ttk.Frame(excluded_frame)
        excluded_button_frame.pack(fill=tk.X, pady=(0, 10))
        
        add_excluded_btn = ttk.Button(
            excluded_button_frame,
            text="➕ İstisna Ekle",
            command=self.add_excluded_chat
        )
        add_excluded_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_excluded_btn = ttk.Button(
            excluded_button_frame,
            text="🗑️ Sil",
            command=self.delete_selected_excluded
        )
        delete_excluded_btn.pack(side=tk.LEFT)
        
        # İstisna listesi
        excluded_columns = ('Sohbet ID', 'Sohbet Adı')
        self.excluded_tree = ttk.Treeview(excluded_frame, columns=excluded_columns, show='headings', height=6)
        
        for col in excluded_columns:
            self.excluded_tree.heading(col, text=col)
            self.excluded_tree.column(col, width=120)
        
        excluded_scroll = ttk.Scrollbar(excluded_frame, orient=tk.VERTICAL, command=self.excluded_tree.yview)
        self.excluded_tree.configure(yscrollcommand=excluded_scroll.set)
        
        self.excluded_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        excluded_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_settings_tab(self):
        """Ayarlar tab'ı oluştur"""
        self.settings_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_frame, text="⚙️ Ayarlar")
        
        # Genel ayarlar
        general_frame = ttk.LabelFrame(self.settings_frame, text="🔧 Genel Ayarlar", padding=15)
        general_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Tema seçimi
        theme_frame = ttk.Frame(general_frame)
        theme_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(theme_frame, text="Tema:").pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.settings.current_theme)
        theme_combo = ttk.Combobox(
            theme_frame,
            textvariable=self.theme_var,
            values=list(self.settings.THEMES.keys()),
            state="readonly",
            width=15
        )
        theme_combo.pack(side=tk.LEFT, padx=(10, 0))
        theme_combo.bind('<<ComboboxSelected>>', self.change_theme)
        
        # Bildirim ayarları
        notification_frame = ttk.LabelFrame(self.settings_frame, text="🔔 Bildirimler", padding=15)
        notification_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.desktop_notifications = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            notification_frame,
            text="Masaüstü bildirimleri",
            variable=self.desktop_notifications
        ).pack(anchor=tk.W)
        
        self.sound_notifications = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            notification_frame,
            text="Ses bildirimleri",
            variable=self.sound_notifications
        ).pack(anchor=tk.W)
        
        # Hesap bilgileri
        account_info_frame = ttk.LabelFrame(self.settings_frame, text="👤 Hesap Bilgileri", padding=15)
        account_info_frame.pack(fill=tk.X, pady=(0, 10))
        
        info_text = (
            f"👤 Kullanıcı: {self.user_data.get('username', 'Bilinmiyor')}\n"
            f"🔑 Token: {self.user_data.get('token', 'Yok')[:20]}...\n"
            f"📊 Hesap Limiti: Loading...\n"
            f"💎 Premium Durumu: Loading..."
        )
        
        self.account_info_label = ttk.Label(
            account_info_frame,
            text=info_text,
            font=("Consolas", 9)
        )
        self.account_info_label.pack(anchor=tk.W)
        
        # Gelişmiş ayarlar
        advanced_frame = ttk.LabelFrame(self.settings_frame, text="🔬 Gelişmiş Ayarlar", padding=15)
        advanced_frame.pack(fill=tk.X)
        
        # Veritabanı temizleme
        cleanup_btn = ttk.Button(
            advanced_frame,
            text="🧹 Veritabanını Temizle",
            command=self.cleanup_database
        )
        cleanup_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Log dosyalarını temizle
        clear_logs_btn = ttk.Button(
            advanced_frame,
            text="📋 Log Dosyalarını Temizle",
            command=self.clear_logs
        )
        clear_logs_btn.pack(anchor=tk.W, pady=(0, 10))
        
        # Ayarları dışa aktar
        export_btn = ttk.Button(
            advanced_frame,
            text="📤 Ayarları Dışa Aktar",
            command=self.export_settings
        )
        export_btn.pack(anchor=tk.W)
    
    def load_initial_data(self):
        """İlk verileri yükle"""
        self.load_dashboard_data()
        self.load_accounts_data()
        self.load_account_info()
    
    def load_dashboard_data(self):
        """Dashboard verilerini yükle"""
        def load_data():
            try:
                user_id = self.user_data['user_id']
                
                # Hesap sayıları
                total_accounts = self.run_async(
                    self.db._fetchone(
                        "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ?",
                        (user_id,)
                    )
                )
                
                active_accounts = self.run_async(
                    self.db._fetchone(
                        "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ? AND (is_auto_message_active = TRUE OR is_auto_reply_active = TRUE)",
                        (user_id,)
                    )
                )
                
                # Kullanıcı bilgileri
                user_info = self.run_async(
                    self.db.get_user(user_id)
                )
                
                # UI güncelle
                self.parent.after(0, lambda: self.update_dashboard_stats({
                    'total_accounts': total_accounts['count'] if total_accounts else 0,
                    'active_accounts': active_accounts['count'] if active_accounts else 0,
                    'sent_messages': 0,  # Bu özellik eklenebilir
                    'account_limit': user_info['account_limit'] if user_info else 2
                }))
                
            except Exception as e:
                logger.error(f"Dashboard veri yükleme hatası: {e}")
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_dashboard_stats(self, stats):
        """Dashboard istatistiklerini güncelle"""
        self.total_accounts_label.config(text=str(stats['total_accounts']))
        self.active_accounts_label.config(text=str(stats['active_accounts']))
        self.sent_messages_label.config(text=str(stats['sent_messages']))
        self.account_limit_label.config(text=str(stats['account_limit']))
    
    def load_accounts_data(self):
        """Hesap verilerini yükle"""
        def load_data():
            try:
                user_id = self.user_data['user_id']
                accounts = self.run_async(
                    self.db._fetchall(
                        "SELECT * FROM userbots WHERE owner_id = ? ORDER BY created_at DESC",
                        (user_id,)
                    )
                )
                
                self.parent.after(0, lambda: self.update_accounts_tree(accounts))
                self.parent.after(0, lambda: self.update_account_combo(accounts))
                
            except Exception as e:
                logger.error(f"Hesap veri yükleme hatası: {e}")
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def update_accounts_tree(self, accounts):
        """Hesap ağacını güncelle"""
        # Mevcut verileri temizle
        for item in self.account_tree.get_children():
            self.account_tree.delete(item)
        
        # Yeni verileri ekle
        for account in accounts:
            auto_msg_status = "✅ Aktif" if account['is_auto_message_active'] else "❌ Pasif"
            auto_reply_status = "✅ Aktif" if account['is_auto_reply_active'] else "❌ Pasif"
            last_activity = "Hiç" if not account['last_activity'] else datetime.fromisoformat(account['last_activity']).strftime('%d.%m.%Y %H:%M')
            
            self.account_tree.insert('', 'end', values=(
                account['session_name'],
                account['phone_number'] or "Bilinmiyor",
                account['status'] or "inactive",
                auto_msg_status,
                auto_reply_status,
                last_activity
            ))
    
    def update_account_combo(self, accounts):
        """Hesap combobox'ını güncelle"""
        account_names = [acc['session_name'] for acc in accounts]
        self.account_combo['values'] = account_names
        if account_names and not self.selected_account_var.get():
            self.selected_account_var.set(account_names[0])
            self.on_account_selected()
    
    def load_account_info(self):
        """Hesap bilgilerini yükle"""
        def load_data():
            try:
                user_id = self.user_data['user_id']
                user_info = self.run_async(self.db.get_user(user_id))
                
                if user_info:
                    premium_status = "Aktif"
                    if user_info['premium_expiry_date']:
                        expiry = datetime.fromisoformat(user_info['premium_expiry_date'])
                        if expiry < datetime.now():
                            premium_status = "Süresi Dolmuş"
                        else:
                            remaining_days = (expiry - datetime.now()).days
                            premium_status = f"Aktif ({remaining_days} gün kaldı)"
                    else:
                        premium_status = "Yok"
                    
                    info_text = (
                        f"👤 Kullanıcı: {self.user_data.get('username', 'Bilinmiyor')}\n"
                        f"🔑 Token: {self.user_data.get('token', 'Yok')[:20]}...\n"
                        f"📊 Hesap Limiti: {user_info['account_limit']}\n"
                        f"💎 Premium Durumu: {premium_status}"
                    )
                    
                    self.parent.after(0, lambda: self.account_info_label.config(text=info_text))
                
            except Exception as e:
                logger.error(f"Hesap bilgisi yükleme hatası: {e}")
        
        threading.Thread(target=load_data, daemon=True).start()
    
    def show_add_account_dialog(self):
        """Hesap ekleme dialog'unu göster"""
        dialog = AddAccountDialog(self.parent, self.userbot_manager, self.user_data['user_id'])
        result = dialog.show()
        
        if result:
            self.load_accounts_data()
            messagebox.showinfo("Başarılı", f"'{result}' hesabı başarıyla eklendi!")
    
    def delete_selected_account(self):
        """Seçili hesabı sil"""
        selection = self.account_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silinecek hesabı seçin.")
            return
        
        session_name = self.account_tree.item(selection[0])['values'][0]
        
        if messagebox.askyesno("Onay", f"'{session_name}' hesabını kalıcı olarak silmek istediğinizden emin misiniz?\n\nBu işlem geri alınamaz!"):
            def delete_account():
                try:
                    success = self.run_async(self.userbot_manager.delete_account(session_name))
                    if success:
                        self.parent.after(0, lambda: [
                            self.load_accounts_data(),
                            messagebox.showinfo("Başarılı", f"'{session_name}' hesabı başarıyla silindi.")
                        ])
                    else:
                        self.parent.after(0, lambda: messagebox.showerror("Hata", "Hesap silinemedi."))
                except Exception as e:
                    logger.error(f"Hesap silme hatası: {e}")
                    self.parent.after(0, lambda: messagebox.showerror("Hata", f"Hesap silinirken hata: {e}"))
            
            threading.Thread(target=delete_account, daemon=True).start()
    
    def show_account_settings(self):
        """Hesap ayarlarını göster"""
        selection = self.account_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen ayarlanacak hesabı seçin.")
            return
        
        session_name = self.account_tree.item(selection[0])['values'][0]
        self.selected_account_var.set(session_name)
        self.notebook.select(2)  # Otomasyon tab'ına geç
        self.on_account_selected()
    
    def on_account_double_click(self, event):
        """Hesaba çift tıklandığında"""
        self.show_account_settings()
    
    def on_account_selected(self, event=None):
        """Hesap seçildiğinde çağrılır"""
        session_name = self.selected_account_var.get()
        if not session_name:
            return
        
        def load_account_settings():
            try:
                # Hesap ayarlarını yükle
                account_data = self.run_async(
                    self.db._fetchone(
                        "SELECT * FROM userbots WHERE session_name = ?",
                        (session_name,)
                    )
                )
                
                if account_data:
                    # Filtreler
                    filters = self.run_async(
                        self.db._fetchall(
                            "SELECT * FROM filters WHERE session_name = ?",
                            (session_name,)
                        )
                    )
                    
                    # İstisna sohbetler
                    excluded_chats = self.run_async(
                        self.db._fetchall(
                            "SELECT * FROM excluded_chats WHERE session_name = ?",
                            (session_name,)
                        )
                    )
                    
                    # UI güncelle
                    self.parent.after(0, lambda: self.update_automation_ui({
                        'account': dict(account_data),
                        'filters': [dict(f) for f in filters],
                        'excluded_chats': [dict(e) for e in excluded_chats]
                    }))
                
            except Exception as e:
                logger.error(f"Hesap ayarları yükleme hatası: {e}")
        
        threading.Thread(target=load_account_settings, daemon=True).start()
    
    def update_automation_ui(self, data):
        """Otomasyon UI'sını güncelle"""
        account = data['account']
        
        # Otomatik mesaj ayarları
        self.auto_msg_enabled.set(account['is_auto_message_active'])
        self.auto_msg_text.delete(1.0, tk.END)
        if account['auto_message_text']:
            self.auto_msg_text.insert(1.0, account['auto_message_text'])
        
        # Zaman ayarları
        if account['message_delay_range']:
            try:
                min_delay, max_delay = map(int, account['message_delay_range'].split('-'))
                self.delay_min_var.set(min_delay)
                self.delay_max_var.set(max_delay)
            except:
                pass
        
        self.loop_cooldown_var.set(account['loop_cooldown_minutes'] or 60)
        
        # Otomatik cevap ayarları
        self.auto_reply_enabled.set(account['is_auto_reply_active'])
        self.auto_reply_text.delete(1.0, tk.END)
        if account['auto_reply_text']:
            self.auto_reply_text.insert(1.0, account['auto_reply_text'])
        
        # Filtreleri güncelle
        self.update_filters_tree(data['filters'])
        
        # İstisna sohbetleri güncelle
        self.update_excluded_tree(data['excluded_chats'])
    
    def update_filters_tree(self, filters):
        """Filtre ağacını güncelle"""
        for item in self.filter_tree.get_children():
            self.filter_tree.delete(item)
        
        for filter_data in filters:
            status = "✅ Aktif" if filter_data['is_active'] else "❌ Pasif"
            self.filter_tree.insert('', 'end', values=(
                filter_data['trigger'],
                filter_data['response'][:30] + "..." if len(filter_data['response']) > 30 else filter_data['response'],
                status
            ))
    
    def update_excluded_tree(self, excluded_chats):
        """İstisna sohbet ağacını güncelle"""
        for item in self.excluded_tree.get_children():
            self.excluded_tree.delete(item)
        
        for chat in excluded_chats:
            self.excluded_tree.insert('', 'end', values=(
                chat['chat_id'],
                chat['chat_title'] or "Bilinmiyor"
            ))
    
    def toggle_auto_message(self):
        """Otomatik mesajı aç/kapat"""
        session_name = self.selected_account_var.get()
        if not session_name:
            return
        
        enabled = self.auto_msg_enabled.get()
        
        def toggle_message():
            try:
                self.run_async(
                    self.userbot_manager.toggle_auto_message(session_name, enabled)
                )
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Başarılı", 
                    f"Otomatik mesaj {'açıldı' if enabled else 'kapatıldı'}."
                ))
            except Exception as e:
                logger.error(f"Otomatik mesaj toggle hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"İşlem başarısız: {e}"))
        
        threading.Thread(target=toggle_message, daemon=True).start()
    
    def toggle_auto_reply(self):
        """Otomatik cevabı aç/kapat"""
        session_name = self.selected_account_var.get()
        if not session_name:
            return
        
        enabled = self.auto_reply_enabled.get()
        
        def toggle_reply():
            try:
                self.run_async(
                    self.userbot_manager.toggle_auto_reply(session_name, enabled)
                )
                self.parent.after(0, lambda: messagebox.showinfo(
                    "Başarılı", 
                    f"Otomatik cevap {'açıldı' if enabled else 'kapatıldı'}."
                ))
            except Exception as e:
                logger.error(f"Otomatik cevap toggle hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"İşlem başarısız: {e}"))
        
        threading.Thread(target=toggle_reply, daemon=True).start()
    
    def save_automation_settings(self):
        """Otomasyon ayarlarını kaydet"""
        session_name = self.selected_account_var.get()
        if not session_name:
            messagebox.showwarning("Uyarı", "Lütfen bir hesap seçin.")
            return
        
        # Ayarları topla
        settings = {
            'auto_message_text': self.auto_msg_text.get(1.0, tk.END).strip(),
            'message_delay_range': f"{self.delay_min_var.get()}-{self.delay_max_var.get()}",
            'loop_cooldown_minutes': self.loop_cooldown_var.get(),
            'auto_reply_text': self.auto_reply_text.get(1.0, tk.END).strip(),
        }
        
        def save_settings():
            try:
                self.run_async(
                    self.userbot_manager.update_account_settings(session_name, settings)
                )
                self.parent.after(0, lambda: messagebox.showinfo("Başarılı", "Ayarlar kaydedildi."))
            except Exception as e:
                logger.error(f"Ayar kaydetme hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"Ayarlar kaydedilemedi: {e}"))
        
        threading.Thread(target=save_settings, daemon=True).start()
    
    def add_filter(self):
        """Filtre ekle"""
        session_name = self.selected_account_var.get()
        if not session_name:
            messagebox.showwarning("Uyarı", "Lütfen bir hesap seçin.")
            return
        
        dialog = FilterDialog(self.parent, "add")
        result = dialog.show()
        
        if result:
            def add_filter():
                try:
                    self.run_async(
                        self.db._execute(
                            "INSERT INTO filters (session_name, trigger, response) VALUES (?, ?, ?)",
                            (session_name, result['trigger'], result['response'])
                        )
                    )
                    self.parent.after(0, lambda: [
                        self.on_account_selected(),
                        messagebox.showinfo("Başarılı", "Filtre eklendi.")
                    ])
                except Exception as e:
                    logger.error(f"Filtre ekleme hatası: {e}")
                    self.parent.after(0, lambda: messagebox.showerror("Hata", f"Filtre eklenemedi: {e}"))
            
            threading.Thread(target=add_filter, daemon=True).start()
    
    def delete_selected_filter(self):
        """Seçili filtreyi sil"""
        selection = self.filter_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silinecek filtreyi seçin.")
            return
        
        trigger = self.filter_tree.item(selection[0])['values'][0]
        session_name = self.selected_account_var.get()
        
        if messagebox.askyesno("Onay", f"'{trigger}' filtresini silmek istediğinizden emin misiniz?"):
            def delete_filter():
                try:
                    self.run_async(
                        self.db._execute(
                            "DELETE FROM filters WHERE session_name = ? AND trigger = ?",
                            (session_name, trigger)
                        )
                    )
                    self.parent.after(0, lambda: [
                        self.on_account_selected(),
                        messagebox.showinfo("Başarılı", "Filtre silindi.")
                    ])
                except Exception as e:
                    logger.error(f"Filtre silme hatası: {e}")
                    self.parent.after(0, lambda: messagebox.showerror("Hata", f"Filtre silinemedi: {e}"))
            
            threading.Thread(target=delete_filter, daemon=True).start()
    
    def add_excluded_chat(self):
        """İstisna sohbet ekle"""
        session_name = self.selected_account_var.get()
        if not session_name:
            messagebox.showwarning("Uyarı", "Lütfen bir hesap seçin.")
            return
        
        chat_identifier = simpledialog.askstring(
            "İstisna Sohbet Ekle",
            "Sohbet ID'sini veya @kullaniciadi girin:"
        )
        
        if not chat_identifier:
            return
        
        def add_excluded():
            try:
                # Sohbet bilgilerini al ve ekle
                success = self.run_async(
                    self.userbot_manager.add_excluded_chat(session_name, chat_identifier)
                )
                
                if success:
                    self.parent.after(0, lambda: [
                        self.on_account_selected(),
                        messagebox.showinfo("Başarılı", "İstisna sohbet eklendi.")
                    ])
                else:
                    self.parent.after(0, lambda: messagebox.showerror("Hata", "Sohbet bulunamadı veya eklenemedi."))
            except Exception as e:
                logger.error(f"İstisna ekleme hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"İstisna eklenemedi: {e}"))
        
        threading.Thread(target=add_excluded, daemon=True).start()
    
    def delete_selected_excluded(self):
        """Seçili istisnayı sil"""
        selection = self.excluded_tree.selection()
        if not selection:
            messagebox.showwarning("Uyarı", "Lütfen silinecek istisnayı seçin.")
            return
        
        chat_id = self.excluded_tree.item(selection[0])['values'][0]
        session_name = self.selected_account_var.get()
        
        if messagebox.askyesno("Onay", f"'{chat_id}' sohbetini istisna listesinden çıkarmak istediğinizden emin misiniz?"):
            def delete_excluded():
                try:
                    self.run_async(
                        self.db._execute(
                            "DELETE FROM excluded_chats WHERE session_name = ? AND chat_id = ?",
                            (session_name, int(chat_id))
                        )
                    )
                    self.parent.after(0, lambda: [
                        self.on_account_selected(),
                        messagebox.showinfo("Başarılı", "İstisna silindi.")
                    ])
                except Exception as e:
                    logger.error(f"İstisna silme hatası: {e}")
                    self.parent.after(0, lambda: messagebox.showerror("Hata", f"İstisna silinemedi: {e}"))
            
            threading.Thread(target=delete_excluded, daemon=True).start()
    
    def start_all_userbots(self):
        """Tüm userbot'ları başlat"""
        def start_all():
            try:
                user_id = self.user_data['user_id']
                success = self.run_async(
                    self.userbot_manager.start_all_user_userbots(user_id)
                )
                
                if success:
                    self.parent.after(0, lambda: [
                        self.load_accounts_data(),
                        messagebox.showinfo("Başarılı", "Tüm userbot'lar başlatıldı.")
                    ])
                else:
                    self.parent.after(0, lambda: messagebox.showwarning("Uyarı", "Bazı userbot'lar başlatılamadı."))
            except Exception as e:
                logger.error(f"Toplu başlatma hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"Userbot'lar başlatılamadı: {e}"))
        
        threading.Thread(target=start_all, daemon=True).start()
    
    def stop_all_userbots(self):
        """Tüm userbot'ları durdur"""
        def stop_all():
            try:
                user_id = self.user_data['user_id']
                success = self.run_async(
                    self.userbot_manager.stop_all_user_userbots(user_id)
                )
                
                if success:
                    self.parent.after(0, lambda: [
                        self.load_accounts_data(),
                        messagebox.showinfo("Başarılı", "Tüm userbot'lar durduruldu.")
                    ])
                else:
                    self.parent.after(0, lambda: messagebox.showwarning("Uyarı", "Bazı userbot'lar durdurulamadı."))
            except Exception as e:
                logger.error(f"Toplu durdurma hatası: {e}")
                self.parent.after(0, lambda: messagebox.showerror("Hata", f"Userbot'lar durdurulamadı: {e}"))
        
        threading.Thread(target=stop_all, daemon=True).start()
    
    def change_theme(self, event=None):
        """Temayı değiştir"""
        new_theme = self.theme_var.get()
        self.settings.current_theme = new_theme
        self.theme.apply_theme(self.parent)
        messagebox.showinfo("Bilgi", f"Tema '{new_theme}' olarak değiştirildi.")
    
    def cleanup_database(self):
        """Veritabanını temizle"""
        if messagebox.askyesno("Onay", "Eski verileri temizlemek istediğinizden emin misiniz?\n\nBu işlem eski logları ve kullanılmayan verileri silecektir."):
            def cleanup():
                try:
                    # Eski logları temizle (30 günden eski)
                    cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
                    self.run_async(
                        self.db._execute(
                            "DELETE FROM system_logs WHERE timestamp < ?",
                            (cutoff_date,)
                        )
                    )
                    
                    # Eski DM geçmişini temizle
                    self.run_async(
                        self.db._execute(
                            "DELETE FROM dm_history WHERE timestamp < ?",
                            (cutoff_date,)
                        )
                    )
                    
                    # Veritabanını optimize et
                    self.run_async(self.db._execute("VACUUM"))
                    
                    self.parent.after(0, lambda: messagebox.showinfo("Başarılı", "Veritabanı temizlendi."))
                    
                except Exception as e:
                    logger.error(f"Veritabanı temizleme hatası: {e}")
                    self.parent.after(0, lambda: messagebox.showerror("Hata", f"Temizleme başarısız: {e}"))
            
            threading.Thread(target=cleanup, daemon=True).start()
    
    def clear_logs(self):
        """Log dosyalarını temizle"""
        if messagebox.askyesno("Onay", "Log dosyalarını temizlemek istediğinizden emin misiniz?"):
            try:
                import os
                log_dir = self.settings.data_dir / "logs"
                if log_dir.exists():
                    for log_file in log_dir.glob("*.log"):
                        log_file.unlink()
                
                messagebox.showinfo("Başarılı", "Log dosyaları temizlendi.")
            except Exception as e:
                logger.error(f"Log temizleme hatası: {e}")
                messagebox.showerror("Hata", f"Log dosyaları temizlenemedi: {e}")
    
    def export_settings(self):
        """Ayarları dışa aktar"""
        from tkinter import filedialog
        import json
        
        file_path = filedialog.asksaveasfilename(
            title="Ayarları Kaydet",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            def export():
                try:
                    user_id = self.user_data['user_id']
                    
                    # Kullanıcı verilerini al
                    user_data = self.run_async(self.db.get_user(user_id))
                    accounts = self.run_async(
                        self.db._fetchall(
                            "SELECT * FROM userbots WHERE owner_id = ?",
                            (user_id,)
                        )
                    )
                    
                    export_data = {
                        'user_info': dict(user_data) if user_data else {},
                        'accounts': [dict(acc) for acc in accounts],
                        'export_date': datetime.now().isoformat(),
                        'version': self.settings.APP_VERSION
                    }
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                    
                    self.parent.after(0, lambda: messagebox.showinfo("Başarılı", f"Ayarlar '{file_path}' dosyasına kaydedildi."))
                    
                except Exception as e:
                    logger.error(f"Ayar dışa aktarma hatası: {e}")
                    self.parent.after(0, lambda: messagebox.showerror("Hata", f"Dışa aktarma başarısız: {e}"))
            
            threading.Thread(target=export, daemon=True).start()
    
    def refresh_data(self):
        """Tüm verileri yenile"""
        self.load_initial_data()
        messagebox.showinfo("Bilgi", "Veriler yenilendi.")
    
    def destroy(self):
        """Widget'ı temizle"""
        if hasattr(self, 'main_frame') and self.main_frame:
            self.main_frame.destroy()


class AddAccountDialog:
    """Hesap ekleme dialog'u"""
    
    def __init__(self, parent, userbot_manager, user_id):
        self.parent = parent
        self.userbot_manager = userbot_manager
        self.user_id = user_id
        self.result = None
        
        # Dialog penceresi
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Yeni Userbot Hesabı Ekle")
        self.dialog.geometry("450x400")
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
        title_label = ttk.Label(main_frame, text="🤖 Yeni Userbot Hesabı", font=("Segoe UI", 14, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Uyarı
        warning_frame = ttk.Frame(main_frame)
        warning_frame.pack(fill=tk.X, pady=(0, 20))
        
        warning_text = (
            "⚠️ DİKKAT: Bu işlem Telegram'ın kullanım şartlarını ihlal edebilir.\n"
            "Hesabınızın yasaklanma riski vardır. Tüm sorumluluk size aittir."
        )
        warning_label = ttk.Label(
            warning_frame,
            text=warning_text,
            foreground="red",
            font=("Segoe UI", 9),
            wraplength=400
        )
        warning_label.pack()
        
        # Oturum adı
        ttk.Label(main_frame, text="Oturum Adı:").pack(anchor=tk.W)
        self.session_entry = ttk.Entry(main_frame, width=40)
        self.session_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Telefon numarası
        ttk.Label(main_frame, text="Telefon Numarası (+90xxxxxxxxxx):").pack(anchor=tk.W)
        self.phone_entry = ttk.Entry(main_frame, width=40)
        self.phone_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Doğrulama kodu (başlangıçta gizli)
        self.code_frame = ttk.Frame(main_frame)
        
        ttk.Label(self.code_frame, text="Doğrulama Kodu:").pack(anchor=tk.W)
        self.code_entry = ttk.Entry(self.code_frame, width=20)
        self.code_entry.pack(anchor=tk.W, pady=(5, 15))
        
        # 2FA şifresi (başlangıçta gizli)
        self.password_frame = ttk.Frame(main_frame)
        
        ttk.Label(self.password_frame, text="2FA Şifresi (varsa):").pack(anchor=tk.W)
        self.password_entry = ttk.Entry(self.password_frame, width=30, show="*")
        self.password_entry.pack(anchor=tk.W, pady=(5, 15))
        
        # Durum etiketi
        self.status_label = ttk.Label(main_frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(pady=(0, 20))
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        self.action_btn = ttk.Button(
            button_frame, 
            text="📤 Kod Gönder", 
            command=self.send_code,
            style="Accent.TButton"
        )
        self.action_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = ttk.Button(button_frame, text="❌ İptal", command=self.dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
        
        # Durum
        self.current_step = "phone"  # phone, code, password, complete
    
    def send_code(self):
        """Doğrulama kodu gönder"""
        session_name = self.session_entry.get().strip()
        phone_number = self.phone_entry.get().strip()
        
        if not session_name or not phone_number:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return
        
        self.action_btn.config(state='disabled', text="📤 Kod gönderiliyor...")
        self.status_label.config(text="Telegram'a doğrulama kodu gönderiliyor...")
        
        def send_code_thread():
            try:
                result = self.run_async_in_thread(
                    self.userbot_manager.start_account_creation(session_name, phone_number)
                )
                
                if result['success']:
                    self.dialog.after(0, lambda: self.show_code_step())
                else:
                    self.dialog.after(0, lambda: self.handle_error(result['error']))
                    
            except Exception as e:
                self.dialog.after(0, lambda: self.handle_error(str(e)))
        
        threading.Thread(target=send_code_thread, daemon=True).start()
    
    def show_code_step(self):
        """Kod girişi adımını göster"""
        self.current_step = "code"
        self.code_frame.pack(fill=tk.X)
        self.action_btn.config(state='normal', text="✅ Kodu Doğrula", command=self.verify_code)
        self.status_label.config(text="✅ Kod gönderildi! Lütfen Telegram'dan gelen kodu girin.")
        self.code_entry.focus()
    
    def verify_code(self):
        """Kodu doğrula"""
        code = self.code_entry.get().strip().replace(" ", "")
        
        if not code:
            messagebox.showerror("Hata", "Lütfen doğrulama kodunu girin.")
            return
        
        self.action_btn.config(state='disabled', text="🔄 Doğrulanıyor...")
        self.status_label.config(text="Kod doğrulanıyor...")
        
        def verify_code_thread():
            try:
                session_name = self.session_entry.get().strip()
                result = self.run_async_in_thread(
                    self.userbot_manager.verify_phone_code(session_name, code)
                )
                
                if result['success']:
                    if result['needs_password']:
                        self.dialog.after(0, lambda: self.show_password_step())
                    else:
                        self.dialog.after(0, lambda: self.complete_account_creation())
                else:
                    self.dialog.after(0, lambda: self.handle_error(result['error']))
                    
            except Exception as e:
                self.dialog.after(0, lambda: self.handle_error(str(e)))
        
        threading.Thread(target=verify_code_thread, daemon=True).start()
    
    def show_password_step(self):
        """2FA şifre adımını göster"""
        self.current_step = "password"
        self.password_frame.pack(fill=tk.X)
        self.action_btn.config(state='normal', text="🔐 Şifreyi Doğrula", command=self.verify_password)
        self.status_label.config(text="🔐 2FA aktif! Lütfen şifrenizi girin.")
        self.password_entry.focus()
    
    def verify_password(self):
        """2FA şifresini doğrula"""
        password = self.password_entry.get()
        
        if not password:
            messagebox.showerror("Hata", "Lütfen 2FA şifrenizi girin.")
            return
        
        self.action_btn.config(state='disabled', text="🔄 Doğrulanıyor...")
        self.status_label.config(text="Şifre doğrulanıyor...")
        
        def verify_password_thread():
            try:
                session_name = self.session_entry.get().strip()
                result = self.run_async_in_thread(
                    self.userbot_manager.verify_2fa_password(session_name, password)
                )
                
                if result['success']:
                    self.dialog.after(0, lambda: self.complete_account_creation())
                else:
                    self.dialog.after(0, lambda: self.handle_error(result['error']))
                    
            except Exception as e:
                self.dialog.after(0, lambda: self.handle_error(str(e)))
        
        threading.Thread(target=verify_password_thread, daemon=True).start()
    
    def complete_account_creation(self):
        """Hesap oluşturmayı tamamla"""
        self.action_btn.config(state='disabled', text="✅ Tamamlanıyor...")
        self.status_label.config(text="Hesap kaydediliyor...")
        
        def complete_thread():
            try:
                session_name = self.session_entry.get().strip()
                phone_number = self.phone_entry.get().strip()
                
                result = self.run_async_in_thread(
                    self.userbot_manager.complete_account_creation(session_name, phone_number, self.user_id)
                )
                
                if result['success']:
                    self.result = session_name
                    self.dialog.after(0, lambda: [
                        self.status_label.config(text="✅ Hesap başarıyla eklendi!"),
                        self.dialog.after(2000, self.dialog.destroy)
                    ])
                else:
                    self.dialog.after(0, lambda: self.handle_error(result['error']))
                    
            except Exception as e:
                self.dialog.after(0, lambda: self.handle_error(str(e)))
        
        threading.Thread(target=complete_thread, daemon=True).start()
    
    def handle_error(self, error_message: str):
        """Hata durumunu işle"""
        self.action_btn.config(state='normal')
        self.status_label.config(text=f"❌ Hata: {error_message}")
        
        # Butonu eski haline getir
        if self.current_step == "phone":
            self.action_btn.config(text="📤 Kod Gönder", command=self.send_code)
        elif self.current_step == "code":
            self.action_btn.config(text="✅ Kodu Doğrula", command=self.verify_code)
        elif self.current_step == "password":
            self.action_btn.config(text="🔐 Şifreyi Doğrula", command=self.verify_password)
        
        messagebox.showerror("Hata", error_message)
    
    def run_async_in_thread(self, coro):
        """Async işlemi thread içinde çalıştır"""
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    def show(self):
        """Dialog'u göster ve sonucu döndür"""
        self.dialog.wait_window()
        return self.result


class FilterDialog:
    """Filtre ekleme/düzenleme dialog'u"""
    
    def __init__(self, parent, mode="add", filter_data=None):
        self.parent = parent
        self.mode = mode
        self.filter_data = filter_data or {}
        self.result = None
        
        # Dialog penceresi
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Filtre Ekleme" if mode == "add" else "Filtre Düzenleme")
        self.dialog.geometry("400x250")
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
        title = "➕ Yeni Filtre Ekle" if self.mode == "add" else "✏️ Filtre Düzenle"
        title_label = ttk.Label(main_frame, text=title, font=("Segoe UI", 12, "bold"))
        title_label.pack(pady=(0, 20))
        
        # Tetikleyici kelime
        ttk.Label(main_frame, text="Tetikleyici Kelime:").pack(anchor=tk.W)
        self.trigger_entry = ttk.Entry(main_frame, width=40)
        self.trigger_entry.pack(fill=tk.X, pady=(5, 15))
        
        if self.filter_data.get('trigger'):
            self.trigger_entry.insert(0, self.filter_data['trigger'])
        
        # Yanıt metni
        ttk.Label(main_frame, text="Yanıt Metni:").pack(anchor=tk.W)
        self.response_text = tk.Text(main_frame, height=4, wrap=tk.WORD)
        self.response_text.pack(fill=tk.X, pady=(5, 20))
        
        if self.filter_data.get('response'):
            self.response_text.insert(1.0, self.filter_data['response'])
        
        # Butonlar
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        save_btn = ttk.Button(
            button_frame, 
            text="💾 Kaydet", 
            command=self.save_filter,
            style="Accent.TButton"
        )
        save_btn.pack(side=tk.RIGHT, padx=(10, 0))
        
        cancel_btn = ttk.Button(button_frame, text="❌ İptal", command=self.dialog.destroy)
        cancel_btn.pack(side=tk.RIGHT)
    
    def save_filter(self):
        """Filtreyi kaydet"""
        trigger = self.trigger_entry.get().strip()
        response = self.response_text.get(1.0, tk.END).strip()
        
        if not trigger or not response:
            messagebox.showerror("Hata", "Lütfen tüm alanları doldurun.")
            return
        
        self.result = {
            'trigger': trigger,
            'response': response
        }
        
        self.dialog.destroy()
    
    def show(self):
        """Dialog'u göster ve sonucu döndür"""
        self.dialog.wait_window()
        return self.result