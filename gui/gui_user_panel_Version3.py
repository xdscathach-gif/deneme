# FilterDialog sınıfının devamı

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