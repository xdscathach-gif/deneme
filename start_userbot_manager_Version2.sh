#!/bin/bash

# Modern Userbot Manager Startup Script
# Linux/Mac için

set -e

# Renkli çıktı
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logo
echo -e "${BLUE}"
echo "  ███╗   ███╗ ██████╗ ██████╗ ███████╗██████╗ ███╗   ██╗"
echo "  ████╗ ████║██╔═══██╗██╔══██╗██╔════╝██╔══██╗████╗  ██║"
echo "  ██╔████╔██║██║   ██║██║  ██║█████╗  ██████╔╝██╔██╗ ██║"
echo "  ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  ██╔══██╗██║╚██╗██║"
echo "  ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗██║  ██║██║ ╚████║"
echo "  ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝"
echo ""
echo "             USERBOT MANAGER v2.0.0"
echo "             Python 3.11+ Uyumlu"
echo -e "${NC}"

# Python kontrolü
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}[HATA]${NC} Python3 bulunamadı!"
    echo "Python 3.11+ yüklendiğinden emin olun."
    exit 1
fi

# Python versiyonu kontrolü
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
REQUIRED_VERSION="3.11"

if (( $(echo "$PYTHON_VERSION < $REQUIRED_VERSION" | bc -l) )); then
    echo -e "${YELLOW}[UYARI]${NC} Python $PYTHON_VERSION tespit edildi. Python $REQUIRED_VERSION+ önerilir."
fi

# Sanal ortam kontrolü
if [ -d "venv" ]; then
    echo -e "${GREEN}[BILGI]${NC} Sanal ortam etkinleştiriliyor..."
    source venv/bin/activate
fi

# Bağımlılık kontrolü
echo -e "${BLUE}[BILGI]${NC} Bağımlılıklar kontrol ediliyor..."

if ! python3 -c "import pyrogram" 2>/dev/null; then
    echo -e "${YELLOW}[UYARI]${NC} Gerekli paketler bulunamadı!"
    read -p "Yüklemek istiyor musunuz? (e/h): " choice
    
    if [[ $choice == "e" || $choice == "E" ]]; then
        echo -e "${BLUE}[BILGI]${NC} Paketler yükleniyor..."
        pip3 install -r requirements.txt
        
        if [ $? -ne 0 ]; then
            echo -e "${RED}[HATA]${NC} Paket yükleme başarısız!"
            exit 1
        fi
    else
        echo -e "${BLUE}[BILGI]${NC} Yükleme iptal edildi."
        exit 1
    fi
fi

# Izinleri kontrol et
echo -e "${BLUE}[BILGI]${NC} Dosya izinleri kontrol ediliyor..."
chmod +x main.py 2>/dev/null || true

# Uygulama başlatma
echo -e "${GREEN}[BILGI]${NC} Modern Userbot Manager başlatılıyor..."
echo ""

python3 main.py

exit_code=$?

if [ $exit_code -ne 0 ]; then
    echo ""
    echo -e "${RED}[HATA]${NC} Uygulama beklenmedik şekilde sonlandı!"
    echo "Hata kodu: $exit_code"
fi

echo ""
echo -e "${GREEN}[BILGI]${NC} Uygulama sonlandırıldı."