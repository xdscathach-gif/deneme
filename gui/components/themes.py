# -*- coding: utf-8 -*-
"""
Tema yönetim sistemi
"""

import tkinter as tk
from tkinter import ttk

class ThemeManager:
    """Tema yönetici sınıfı"""
    
    def __init__(self, settings):
        self.settings = settings
        self.current_theme = settings.current_theme
        self.style = None
    
    def apply_theme(self, root):
        """Temayı uygula"""
        self.style = ttk.Style(root)
        
        # Tema renklerini al
        colors = self.settings.THEMES[self.current_theme]
        
        # Ana tema ayarları
        self.style.theme_use('clam')  # Base theme
        
        # Root window ayarları
        root.configure(bg=colors['bg_primary'])
        
        # Genel widget stillerini ayarla
        self.configure_general_styles(colors)
        self.configure_button_styles(colors)
        self.configure_frame_styles(colors)
        self.configure_entry_styles(colors)
        self.configure_treeview_styles(colors)
        self.configure_notebook_styles(colors)
        self.configure_labelframe_styles(colors)
    
    def configure_general_styles(self, colors):
        """Genel stil ayarları"""
        # Label
        self.style.configure(
            'TLabel',
            background=colors['bg_primary'],
            foreground=colors['text_primary'],
            font=('Segoe UI', 9)
        )
        
        # Checkbutton
        self.style.configure(
            'TCheckbutton',
            background=colors['bg_primary'],
            foreground=colors['text_primary'],
            focuscolor='none'
        )
        
        # Radiobutton
        self.style.configure(
            'TRadiobutton',
            background=colors['bg_primary'],
            foreground=colors['text_primary'],
            focuscolor='none'
        )
        
        # Scale
        self.style.configure(
            'TScale',
            background=colors['bg_primary'],
            troughcolor=colors['bg_secondary'],
            lightcolor=colors['accent'],
            darkcolor=colors['accent']
        )
        
        # Progressbar
        self.style.configure(
            'TProgressbar',
            background=colors['accent'],
            troughcolor=colors['bg_secondary'],
            bordercolor=colors['border'],
            lightcolor=colors['accent'],
            darkcolor=colors['accent']
        )
        
        # Scrollbar
        self.style.configure(
            'TScrollbar',
            background=colors['bg_secondary'],
            troughcolor=colors['bg_primary'],
            bordercolor=colors['border'],
            arrowcolor=colors['text_secondary'],
            darkcolor=colors['bg_tertiary'],
            lightcolor=colors['bg_secondary']
        )
        
        # Separator
        self.style.configure(
            'TSeparator',
            background=colors['border']
        )
    
    def configure_button_styles(self, colors):
        """Buton stillerini ayarla"""
        # Normal buton
        self.style.configure(
            'TButton',
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            bordercolor=colors['border'],
            focuscolor='none',
            padding=(10, 5)
        )
        
        self.style.map(
            'TButton',
            background=[
                ('active', colors['bg_tertiary']),
                ('pressed', colors['accent']),
                ('disabled', colors['bg_primary'])
            ],
            foreground=[
                ('disabled', colors['text_secondary'])
            ]
        )
        
        # Accent buton (vurgulu)
        self.style.configure(
            'Accent.TButton',
            background=colors['accent'],
            foreground='white',
            bordercolor=colors['accent'],
            focuscolor='none',
            padding=(12, 6),
            font=('Segoe UI', 9, 'bold')
        )
        
        self.style.map(
            'Accent.TButton',
            background=[
                ('active', self._darken_color(colors['accent'])),
                ('pressed', self._darken_color(colors['accent'], 0.3))
            ]
        )
        
        # Success buton
        self.style.configure(
            'Success.TButton',
            background=colors['success'],
            foreground='white',
            bordercolor=colors['success'],
            focuscolor='none'
        )
        
        # Warning buton
        self.style.configure(
            'Warning.TButton',
            background=colors['warning'],
            foreground='white',
            bordercolor=colors['warning'],
            focuscolor='none'
        )
        
        # Error buton
        self.style.configure(
            'Error.TButton',
            background=colors['error'],
            foreground='white',
            bordercolor=colors['error'],
            focuscolor='none'
        )
    
    def configure_frame_styles(self, colors):
        """Frame stillerini ayarla"""
        self.style.configure(
            'TFrame',
            background=colors['bg_primary'],
            bordercolor=colors['border']
        )
        
        # Card-like frame
        self.style.configure(
            'Card.TFrame',
            background=colors['bg_secondary'],
            relief='flat',
            borderwidth=1,
            bordercolor=colors['border']
        )
    
    def configure_entry_styles(self, colors):
        """Entry stillerini ayarla"""
        self.style.configure(
            'TEntry',
            fieldbackground=colors['bg_secondary'],
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            bordercolor=colors['border'],
            insertcolor=colors['text_primary'],
            selectbackground=colors['accent'],
            selectforeground='white'
        )
        
        self.style.map(
            'TEntry',
            focuscolor=[('!focus', colors['border']), ('focus', colors['accent'])]
        )
        
        # Combobox
        self.style.configure(
            'TCombobox',
            fieldbackground=colors['bg_secondary'],
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            bordercolor=colors['border'],
            arrowcolor=colors['text_secondary'],
            selectbackground=colors['accent'],
            selectforeground='white'
        )
        
        self.style.map(
            'TCombobox',
            focuscolor=[('!focus', colors['border']), ('focus', colors['accent'])]
        )
        
        # Spinbox
        self.style.configure(
            'TSpinbox',
            fieldbackground=colors['bg_secondary'],
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            bordercolor=colors['border'],
            arrowcolor=colors['text_secondary']
        )
    
    def configure_treeview_styles(self, colors):
        """Treeview stillerini ayarla"""
        self.style.configure(
            'Treeview',
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            fieldbackground=colors['bg_secondary'],
            bordercolor=colors['border'],
            selectbackground=colors['accent'],
            selectforeground='white'
        )
        
        self.style.configure(
            'Treeview.Heading',
            background=colors['bg_tertiary'],
            foreground=colors['text_primary'],
            bordercolor=colors['border'],
            font=('Segoe UI', 9, 'bold')
        )
        
        self.style.map(
            'Treeview.Heading',
            background=[('active', colors['accent'])]
        )
        
        # Zebra striping effect
        self.style.configure(
            'Treeview',
            rowheight=25
        )
    
    def configure_notebook_styles(self, colors):
        """Notebook stillerini ayarla"""
        self.style.configure(
            'TNotebook',
            background=colors['bg_primary'],
            bordercolor=colors['border'],
            tabmargins=[2, 5, 2, 0]
        )
        
        self.style.configure(
            'TNotebook.Tab',
            background=colors['bg_secondary'],
            foreground=colors['text_primary'],
            bordercolor=colors['border'],
            padding=[15, 8],
            font=('Segoe UI', 9)
        )
        
        self.style.map(
            'TNotebook.Tab',
            background=[
                ('selected', colors['accent']),
                ('active', colors['bg_tertiary'])
            ],
            foreground=[
                ('selected', 'white'),
                ('active', colors['text_primary'])
            ]
        )
    
    def configure_labelframe_styles(self, colors):
        """LabelFrame stillerini ayarla"""
        self.style.configure(
            'TLabelframe',
            background=colors['bg_primary'],
            bordercolor=colors['border'],
            relief='solid',
            borderwidth=1
        )
        
        self.style.configure(
            'TLabelframe.Label',
            background=colors['bg_primary'],
            foreground=colors['text_primary'],
            font=('Segoe UI', 9, 'bold')
        )
    
    def _darken_color(self, color, factor=0.1):
        """Rengi koyulaştır"""
        if color.startswith('#'):
            # Hex color
            try:
                r = int(color[1:3], 16)
                g = int(color[3:5], 16)
                b = int(color[5:7], 16)
                
                r = max(0, int(r * (1 - factor)))
                g = max(0, int(g * (1 - factor)))
                b = max(0, int(b * (1 - factor)))
                
                return f"#{r:02x}{g:02x}{b:02x}"
            except:
                return color
        return color
    
    def change_theme(self, theme_name):
        """Temayı değiştir"""
        if theme_name in self.settings.THEMES:
            self.current_theme = theme_name
            self.settings.current_theme = theme_name
            return True
        return False