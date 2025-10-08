# UserbotManager sınıfının devamı

        except Exception as e:
            logger.error(f"Kod temizleme hatası: {e}")
    
    async def get_userbot_stats(self, user_id: int) -> Dict[str, Any]:
        """Kullanıcının userbot istatistiklerini al"""
        try:
            # Toplam hesap sayısı
            total_accounts = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ?",
                (user_id,)
            )
            
            # Aktif hesap sayısı
            active_accounts = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ? AND status = 'active'",
                (user_id,)
            )
            
            # Otomatik mesaj aktif hesaplar
            auto_msg_active = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ? AND is_auto_message_active = TRUE",
                (user_id,)
            )
            
            # Otomatik cevap aktif hesaplar
            auto_reply_active = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM userbots WHERE owner_id = ? AND is_auto_reply_active = TRUE",
                (user_id,)
            )
            
            # Toplam filtre sayısı
            total_filters = await self.db._fetchone(
                "SELECT COUNT(*) as count FROM filters f JOIN userbots u ON f.session_name = u.session_name WHERE u.owner_id = ?",
                (user_id,)
            )
            
            return {
                'total_accounts': total_accounts['count'] if total_accounts else 0,
                'active_accounts': active_accounts['count'] if active_accounts else 0,
                'auto_message_active': auto_msg_active['count'] if auto_msg_active else 0,
                'auto_reply_active': auto_reply_active['count'] if auto_reply_active else 0,
                'total_filters': total_filters['count'] if total_filters else 0
            }
            
        except Exception as e:
            logger.error(f"İstatistik alma hatası {user_id}: {e}")
            return {}
    
    async def shutdown(self):
        """Tüm client'ları güvenli şekilde kapat"""
        try:
            # Tüm görevleri iptal et
            for session_name, task in list(self.running_tasks.items()):
                if not task.done():
                    task.cancel()
                    try:
                        await asyncio.wait_for(task, timeout=5.0)
                    except (asyncio.CancelledError, asyncio.TimeoutError):
                        pass
            
            self.running_tasks.clear()
            
            # Tüm client'ları kapat
            for session_name, client in list(self.active_clients.items()):
                try:
                    if client.is_connected:
                        await client.stop()
                except Exception as e:
                    logger.error(f"Client kapatma hatası {session_name}: {e}")
            
            self.active_clients.clear()
            
            # Bekleyen kodları temizle
            for session_name, data in list(self.pending_codes.items()):
                try:
                    await data['client'].disconnect()
                except:
                    pass
            
            self.pending_codes.clear()
            
            logger.info("Userbot manager kapatıldı")
            
        except Exception as e:
            logger.error(f"Shutdown hatası: {e}")