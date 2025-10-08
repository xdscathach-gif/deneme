# -*- coding: utf-8 -*-
"""
Animasyon sistemi
"""

import tkinter as tk
import threading
import time
from typing import Callable, Optional

class AnimationManager:
    """Animasyon yönetici sınıfı"""
    
    def __init__(self):
        self.active_animations = {}
    
    def fade_in(self, widget, duration=0.3, callback: Optional[Callable] = None):
        """Widget'ı fade-in efektiyle göster"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
        
        widget_id = id(widget)
        
        # Önceki animasyonu durdur
        if widget_id in self.active_animations:
            self.active_animations[widget_id] = False
        
        self.active_animations[widget_id] = True
        
        def animate():
            try:
                steps = 20
                step_duration = duration / steps
                
                for i in range(steps + 1):
                    if not self.active_animations.get(widget_id, False):
                        break
                    
                    if not widget.winfo_exists():
                        break
                    
                    alpha = i / steps
                    
                    # Alpha değerini widget'a uygula (platform bağımlı)
                    widget.after(0, lambda a=alpha: self._set_widget_alpha(widget, a))
                    
                    time.sleep(step_duration)
                
                # Animasyon tamamlandı
                if widget_id in self.active_animations:
                    del self.active_animations[widget_id]
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                # Hata durumunda animasyonu temizle
                if widget_id in self.active_animations:
                    del self.active_animations[widget_id]
        
        threading.Thread(target=animate, daemon=True).start()
    
    def fade_out(self, widget, duration=0.3, callback: Optional[Callable] = None):
        """Widget'ı fade-out efektiyle gizle"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
        
        widget_id = id(widget)
        
        # Önceki animasyonu durdur
        if widget_id in self.active_animations:
            self.active_animations[widget_id] = False
        
        self.active_animations[widget_id] = True
        
        def animate():
            try:
                steps = 20
                step_duration = duration / steps
                
                for i in range(steps + 1):
                    if not self.active_animations.get(widget_id, False):
                        break
                    
                    if not widget.winfo_exists():
                        break
                    
                    alpha = 1.0 - (i / steps)
                    
                    # Alpha değerini widget'a uygula
                    widget.after(0, lambda a=alpha: self._set_widget_alpha(widget, a))
                    
                    time.sleep(step_duration)
                
                # Animasyon tamamlandı
                if widget_id in self.active_animations:
                    del self.active_animations[widget_id]
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                # Hata durumunda animasyonu temizle
                if widget_id in self.active_animations:
                    del self.active_animations[widget_id]
        
        threading.Thread(target=animate, daemon=True).start()
    
    def slide_in(self, widget, direction='left', duration=0.4, callback: Optional[Callable] = None):
        """Widget'ı slide-in efektiyle göster"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
        
        widget_id = id(widget)
        
        # Önceki animasyonu durdur
        if widget_id in self.active_animations:
            self.active_animations[widget_id] = False
        
        self.active_animations[widget_id] = True
        
        def animate():
            try:
                # Widget'ın hedef pozisyonunu al
                widget.update_idletasks()
                target_x = widget.winfo_x()
                target_y = widget.winfo_y()
                
                # Başlangıç pozisyonunu hesapla
                if direction == 'left':
                    start_x = target_x - widget.winfo_width()
                    start_y = target_y
                elif direction == 'right':
                    start_x = target_x + widget.winfo_width()
                    start_y = target_y
                elif direction == 'top':
                    start_x = target_x
                    start_y = target_y - widget.winfo_height()
                else:  # bottom
                    start_x = target_x
                    start_y = target_y + widget.winfo_height()
                
                steps = 25
                step_duration = duration / steps
                
                for i in range(steps + 1):
                    if not self.active_animations.get(widget_id, False):
                        break
                    
                    if not widget.winfo_exists():
                        break
                    
                    progress = i / steps
                    # Easing function (ease-out)
                    progress = 1 - (1 - progress) ** 3
                    
                    current_x = start_x + (target_x - start_x) * progress
                    current_y = start_y + (target_y - start_y) * progress
                    
                    widget.after(0, lambda x=current_x, y=current_y: widget.place(x=x, y=y))
                    
                    time.sleep(step_duration)
                
                # Animasyon tamamlandı
                if widget_id in self.active_animations:
                    del self.active_animations[widget_id]
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                # Hata durumunda animasyonu temizle
                if widget_id in self.active_animations:
                    del self.active_animations[widget_id]
        
        threading.Thread(target=animate, daemon=True).start()
    
    def scale_in(self, widget, duration=0.3, callback: Optional[Callable] = None):
        """Widget'ı scale-in efektiyle göster"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
        
        widget_id = id(widget)
        
        # Bu animasyon tkinter'da sınırlı desteklenir
        # Basit bir opacity animasyonu olarak implement edilir
        self.fade_in(widget, duration, callback)
    
    def shake(self, widget, intensity=5, duration=0.5, callback: Optional[Callable] = None):
        """Widget'ı sallama efekti"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
        
        widget_id = id(widget)
        
        # Önceki animasyonu durdur
        if widget_id in self.active_animations:
            self.active_animations[widget_id] = False
        
        self.active_animations[widget_id] = True
        
        def animate():
            try:
                widget.update_idletasks()
                original_x = widget.winfo_x()
                original_y = widget.winfo_y()
                
                shakes = 10
                shake_duration = duration / shakes
                
                for i in range(shakes):
                    if not self.active_animations.get(widget_id, False):
                        break
                    
                    if not widget.winfo_exists():
                        break
                    
                    # Alternatif yönlerde hareket
                    offset_x = intensity * (1 if i % 2 == 0 else -1)
                    offset_y = intensity * (1 if (i // 2) % 2 == 0 else -1) * 0.5
                    
                    new_x = original_x + offset_x
                    new_y = original_y + offset_y
                    
                    widget.after(0, lambda x=new_x, y=new_y: widget.place(x=x, y=y))
                    
                    time.sleep(shake_duration / 2)
                    
                    # Orijinal pozisyona geri dön
                    widget.after(0, lambda x=original_x, y=original_y: widget.place(x=x, y=y))
                    
                    time.sleep(shake_duration / 2)
                
                # Animasyon tamamlandı
                if widget_id in self.active_animations:
                    del self.active_animations[widget_id]
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                # Hata durumunda animasyonu temizle
                if widget_id in self.active_animations:
                    del self.active_animations[widget_id]
        
        threading.Thread(target=animate, daemon=True).start()
    
    def pulse(self, widget, duration=1.0, cycles=3, callback: Optional[Callable] = None):
        """Widget'ı pulse efekti (büyüyüp küçülme)"""
        if not hasattr(widget, 'winfo_exists') or not widget.winfo_exists():
            return
        
        widget_id = id(widget)
        
        # Bu animasyon tkinter'da sınırlı, renk değişimi olarak implement edilebilir
        self._pulse_color(widget, duration, cycles, callback)
    
    def _pulse_color(self, widget, duration, cycles, callback):
        """Renk değişimi ile pulse efekti"""
        def animate():
            try:
                original_bg = widget.cget('background')
                pulse_color = '#ffff99'  # Sarı vurgu
                
                cycle_duration = duration / cycles
                steps_per_cycle = 20
                step_duration = cycle_duration / (steps_per_cycle * 2)
                
                for cycle in range(cycles):
                    # Fade to pulse color
                    for i in range(steps_per_cycle):
                        if not widget.winfo_exists():
                            return
                        
                        # Color interpolation burada basit tutuldu
                        widget.after(0, lambda: widget.configure(background=pulse_color))
                        time.sleep(step_duration)
                    
                    # Fade back to original
                    for i in range(steps_per_cycle):
                        if not widget.winfo_exists():
                            return
                        
                        widget.after(0, lambda: widget.configure(background=original_bg))
                        time.sleep(step_duration)
                
                if callback:
                    widget.after(0, callback)
                    
            except Exception as e:
                pass
        
        threading.Thread(target=animate, daemon=True).start()
    
    def _set_widget_alpha(self, widget, alpha):
        """Widget'ın alpha değerini ayarla (platform bağımlı)"""
        try:
            # Windows için
            if hasattr(widget, 'wm_attributes'):
                widget.wm_attributes('-alpha', alpha)
            else:
                # Diğer platformlar için alternatif yöntem
                # Bu durumda görünürlük ile simüle edilir
                if alpha < 0.1:
                    widget.configure(state='disabled')
                else:
                    widget.configure(state='normal')
        except:
            pass
    
    def stop_animation(self, widget):
        """Widget'ın animasyonunu durdur"""
        widget_id = id(widget)
        if widget_id in self.active_animations:
            self.active_animations[widget_id] = False
    
    def stop_all_animations(self):
        """Tüm animasyonları durdur"""
        for widget_id in list(self.active_animations.keys()):
            self.active_animations[widget_id] = False