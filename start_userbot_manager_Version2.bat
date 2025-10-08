@echo off
title Modern Userbot Manager

echo.
echo  ███╗   ███╗ ██████╗ ██████╗ ███████╗██████╗ ███╗   ██╗
echo  ████╗ ████║██╔═══██╗██╔══██╗██╔════╝██╔══██╗████╗  ██║
echo  ██╔████╔██║██║   ██║██║  ██║█████╗  ██████╔╝██╔██╗ ██║
echo  ██║╚██╔╝██║██║   ██║██║  ██║██╔══╝  ██╔══██╗██║╚██╗██║
echo  ██║ ╚═╝ ██║╚██████╔╝██████╔╝███████╗██║  ██║██║ ╚████║
echo  ╚═╝     ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝
echo.
echo             USERBOT MANAGER v2.0.0
echo             Python 3.11+ Uyumlu
echo.

REM Python versiyonu kontrolü
python --version >nul 2>&1
if errorlevel 1 (
    echo [HATA] Python bulunamadı!
    echo Python 3.11+ yüklendiğinden emin olun.
    pause
    exit /b 1
)

REM Sanal ortam kontrolü
if exist "venv\Scripts\activate.bat" (
    echo [BILGI] Sanal ortam etkinleştiriliyor...
    call venv\Scripts\activate.bat
)

REM Bağımlılık kontrolü
echo [BILGI] Bağımlılıklar kontrol ediliyor...
pip show pyrogram >nul 2>&1
if errorlevel 1 (
    echo [UYARI] Gerekli paketler bulunamadı!
    echo Yüklemek istiyor musunuz? (E/H)
    set /p choice="Seçiminiz: "
    if /i "%choice%"=="E" (
        echo [BILGI] Paketler yükleniyor...
        pip install -r requirements.txt
        if errorlevel 1 (
            echo [HATA] Paket yükleme başarısız!
            pause
            exit /b 1
        )
    ) else (
        echo [BILGI] Yükleme iptal edildi.
        pause
        exit /b 1
    )
)

REM Uygulama başlatma
echo [BILGI] Modern Userbot Manager başlatılıyor...
echo.

python main.py

if errorlevel 1 (
    echo.
    echo [HATA] Uygulama beklenmedik şekilde sonlandı!
    echo Hata kodu: %errorlevel%
)

echo.
echo [BILGI] Uygulama sonlandırıldı.
pause