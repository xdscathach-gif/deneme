# -*- coding: utf-8 -*-
"""
Gelişmiş IP deteksiyon ve güvenlik servisi
"""

import socket
import struct
import platform
import subprocess
import netifaces
from typing import Optional, Dict, List

class IPDetectionService:
    """IP deteksiyon servisi"""
    
    @staticmethod
    def get_local_ip() -> str:
        """Yerel IP adresini al"""
        try:
            # En güvenilir yöntem: Dış bağlantı simülasyonu
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("8.8.8.8", 80))
                return s.getsockname()[0]
        except:
            return "127.0.0.1"
    
    @staticmethod
    def get_public_ip() -> str:
        """Genel IP adresini al"""
        import requests
        services = [
            "https://httpbin.org/ip",
            "https://api.ipify.org?format=json",
            "https://jsonip.com",
            "https://api.my-ip.io/ip.json"
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    # Farklı servis formatları
                    if 'origin' in data:
                        return data['origin']
                    elif 'ip' in data:
                        return data['ip']
                    elif 'IP' in data:
                        return data['IP']
            except:
                continue
        
        return "Bilinmiyor"
    
    @staticmethod
    def get_network_interfaces() -> List[Dict]:
        """Ağ arayüzlerini listele"""
        try:
            interfaces = []
            for interface in netifaces.interfaces():
                addrs = netifaces.ifaddresses(interface)
                
                if netifaces.AF_INET in addrs:
                    for addr in addrs[netifaces.AF_INET]:
                        interfaces.append({
                            'interface': interface,
                            'ip': addr['addr'],
                            'netmask': addr.get('netmask', ''),
                            'broadcast': addr.get('broadcast', '')
                        })
            
            return interfaces
        except:
            return []
    
    @staticmethod
    def is_vpn_detected() -> bool:
        """VPN kullanımını tespit et"""
        try:
            # Yaygın VPN arayüz isimleri
            vpn_interfaces = ['tun', 'tap', 'vpn', 'ppp', 'wg']
            interfaces = netifaces.interfaces()
            
            for interface in interfaces:
                interface_lower = interface.lower()
                if any(vpn in interface_lower for vpn in vpn_interfaces):
                    return True
            
            # Windows için ek kontrol
            if platform.system() == "Windows":
                try:
                    result = subprocess.run(
                        ["netsh", "interface", "show", "interface"],
                        capture_output=True, text=True, timeout=5
                    )
                    output = result.stdout.lower()
                    vpn_keywords = ['vpn', 'tunnel', 'tap', 'openvpn', 'wireguard']
                    return any(keyword in output for keyword in vpn_keywords)
                except:
                    pass
            
            return False
        except:
            return False
    
    @staticmethod
    def get_system_info() -> Dict:
        """Sistem bilgilerini al"""
        try:
            return {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'hostname': socket.gethostname(),
                'local_ip': IPDetectionService.get_local_ip(),
                'public_ip': IPDetectionService.get_public_ip(),
                'vpn_detected': IPDetectionService.is_vpn_detected(),
                'interfaces': IPDetectionService.get_network_interfaces()
            }
        except Exception as e:
            return {'error': str(e)}