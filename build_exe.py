#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PyInstaller ile executable oluşturma script'i
Python 3.11+ uyumlu
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Proje bilgileri
APP_NAME = "Modern Userbot Manager"
APP_VERSION = "2.0.0"
APP_AUTHOR = "Userbot Manager Team"
APP_DESCRIPTION = "Gelişmiş Telegram Userbot Yönetim Sistemi"

# Dosya yolları
PROJECT_ROOT = Path(__file__).parent
MAIN_SCRIPT = PROJECT_ROOT / "main.py"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"
ASSETS_DIR = PROJECT_ROOT / "assets"

def clean_build_dirs():
    """Build dizinlerini temizle"""
    print("🧹 Build dizinleri temizleniyor...")
    
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"   ✓ {directory.name} temizlendi")

def create_spec_file():
    """PyInstaller spec dosyası oluştur"""
    print("📄 Spec dosyası oluşturuluyor...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Proje kök dizini
project_root = Path(r"{PROJECT_ROOT}")

a = Analysis(
    [r"{MAIN_SCRIPT}"],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Config dosyaları
        (str(project_root / "config" / "*.py"), "config"),
        
        # Core modülleri
        (str(project_root / "core" / "*.py"), "core"),
        
        # GUI modülleri
        (str(project_root / "gui" / "*.py"), "gui"),
        (str(project_root / "gui" / "components" / "*.py"), "gui/components"),
        
        # Assets (varsa)
        # (str(project_root / "assets"), "assets"),
    ],
    hiddenimports=[
        # Pyrogram bağımlılıkları
        'pyrogram',
        'pyrogram.client',
        'pyrogram.errors',
        'pyrogram.filters',
        'pyrogram.handlers',
        'pyrogram.types',
        'pyrogram.enums',
        
        # TgCrypto
        'TgCrypto',
        
        # Async ve threading
        'asyncio',
        'threading',
        'concurrent.futures',
        
        # Tkinter
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        
        # Veritabanı
        'sqlite3',
        
        # JSON ve datetime
        'json',
        'datetime',
        'time',
        
        # HTTP
        'requests',
        'urllib3',
        
        # Güvenlik
        'jwt',
        'hashlib',
        'secrets',
        'cryptography',
        
        # Sistem
        'pathlib',
        'logging',
        'os',
        'sys',
        
        # Proje modülleri
        'config',
        'config.settings',
        'config.database',
        'core',
        'core.auth',
        'core.userbot_manager',
        'core.security',
        'gui',
        'gui.main_window',
        'gui.login_window',
        'gui.admin_panel',
        'gui.user_panel',
        'gui.components',
        'gui.components.themes',
        'gui.components.animations',
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        # Test modülleri
        'pytest',
        'unittest',
        
        # Development tools
        'pip',
        'setuptools',
        
        # Jupyter
        'jupyter',
        'IPython',
        
        # Matplotlib (kullanılmıyorsa)
        'matplotlib',
        'numpy',
        'pandas',
        
        # Web frameworks
        'django',
        'flask',
        'fastapi',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME.replace(" ", "_")}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI uygulaması
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version_info.txt',
    icon=str(project_root / "assets" / "icon.ico") if (project_root / "assets" / "icon.ico").exists() else None,
)
'''
    
    spec_file = PROJECT_ROOT / f"{APP_NAME.replace(' ', '_')}.spec"
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"   ✓ Spec dosyası oluşturuldu: {spec_file.name}")
    return spec_file

def create_version_info():
    """Windows için version info dosyası oluştur"""
    if sys.platform != 'win32':
        return
    
    print("📋 Version info dosyası oluşturuluyor...")
    
    version_parts = APP_VERSION.split('.')
    while len(version_parts) < 4:
        version_parts.append('0')
    
    version_info_content = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    prodvers=({version_parts[0]}, {version_parts[1]}, {version_parts[2]}, {version_parts[3]}),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u'{APP_AUTHOR}'),
            StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
            StringStruct(u'FileVersion', u'{APP_VERSION}'),
            StringStruct(u'InternalName', u'{APP_NAME}'),
            StringStruct(u'LegalCopyright', u'Copyright © 2024 {APP_AUTHOR}'),
            StringStruct(u'OriginalFilename', u'{APP_NAME.replace(" ", "_")}.exe'),
            StringStruct(u'ProductName', u'{APP_NAME}'),
            StringStruct(u'ProductVersion', u'{APP_VERSION}')
          ]
        )
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    version_file = PROJECT_ROOT / "version_info.txt"
    with open(version_file, 'w', encoding='utf-8') as f:
        f.write(version_info_content)
    
    print(f"   ✓ Version info oluşturuldu: {version_file.name}")

def check_dependencies():
    """Gerekli bağımlılıkları kontrol et"""
    print("🔍 Bağımlılıklar kontrol ediliyor...")
    
    required_packages = {
        'pyrogram': 'pyrogram',
        'TgCrypto': 'TgCrypto', 
        'PyJWT': 'jwt',  # Import adı farklı
        'requests': 'requests',
        'PyInstaller': 'PyInstaller'
    }
    
    missing_packages = []
    
    for package_name, import_name in required_packages.items():
        try:
            __import__(import_name)
            print(f"   ✓ {package_name}")
        except ImportError:
            missing_packages.append(package_name)
            print(f"   ❌ {package_name} (eksik)")
    
    if missing_packages:
        print(f"\n❌ Eksik paketler: {', '.join(missing_packages)}")
        print("Yüklemek için: pip install " + " ".join(missing_packages))
        
        # Otomatik yükleme seçeneği
        choice = input("\nEksik paketleri şimdi yüklemek ister misiniz? (e/h): ").lower()
        if choice == 'e':
            try:
                subprocess.run([sys.executable, '-m', 'pip', 'install'] + missing_packages, check=True)
                print("✅ Paketler başarıyla yüklendi!")
                return True
            except subprocess.CalledProcessError:
                print("❌ Paket yükleme başarısız!")
                return False
        else:
            return False
    
    print("   ✅ Tüm bağımlılıklar mevcut")
    return True
def build_executable(spec_file):
    """Executable'ı oluştur"""
    print("🔨 Executable oluşturuluyor...")
    
    cmd = [
        sys.executable, '-m', 'PyInstaller',
        '--clean',
        '--noconfirm',
        str(spec_file)
    ]
    
    print(f"   Komut: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print("   ✅ Build başarılı!")
        
        # Build çıktısını göster
        if result.stdout:
            print("   📋 Build çıktısı:")
            for line in result.stdout.split('\n')[-10:]:  # Son 10 satır
                if line.strip():
                    print(f"      {line}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Build hatası: {e}")
        if e.stderr:
            print("   Hata detayları:")
            for line in e.stderr.split('\n'):
                if line.strip():
                    print(f"      {line}")
        return False

def optimize_executable():
    """Executable'ı optimize et"""
    print("⚡ Executable optimize ediliyor...")
    
    exe_name = f"{APP_NAME.replace(' ', '_')}.exe"
    exe_path = DIST_DIR / exe_name
    
    if not exe_path.exists():
        print(f"   ❌ Executable bulunamadı: {exe_path}")
        return False
    
    # Dosya boyutunu göster
    file_size = exe_path.stat().st_size
    size_mb = file_size / (1024 * 1024)
    print(f"   📏 Dosya boyutu: {size_mb:.2f} MB")
    
    # UPX ile sıkıştırma (varsa)
    try:
        upx_result = subprocess.run(['upx', '--version'], capture_output=True)
        if upx_result.returncode == 0:
            print("   🗜️ UPX ile sıkıştırılıyor...")
            subprocess.run(['upx', '--best', str(exe_path)], check=True)
            
            new_size = exe_path.stat().st_size
            new_size_mb = new_size / (1024 * 1024)
            compression_ratio = (1 - new_size / file_size) * 100
            
            print(f"   ✅ Sıkıştırma tamamlandı: {new_size_mb:.2f} MB (%{compression_ratio:.1f} küçültme)")
        else:
            print("   ℹ️ UPX bulunamadı, sıkıştırma atlandı")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("   ℹ️ UPX sıkıştırması başarısız veya mevcut değil")
    
    return True

def create_installer():
    """NSIS installer oluştur (opsiyonel)"""
    if sys.platform != 'win32':
        return
    
    print("📦 Installer script'i oluşturuluyor...")
    
    nsis_script = f'''
; Modern Userbot Manager Installer
!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{APP_VERSION}"
!define APP_PUBLISHER "{APP_AUTHOR}"
!define APP_EXE "{APP_NAME.replace(' ', '_')}.exe"

; MUI Settings
!include "MUI2.nsh"
!define MUI_ABORTWARNING

; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; Languages
!insertmacro MUI_LANGUAGE "Turkish"
!insertmacro MUI_LANGUAGE "English"

; Installer Info
Name "${{APP_NAME}}"
OutFile "dist/${{APP_NAME}}_v${{APP_VERSION}}_Setup.exe"
InstallDir "$PROGRAMFILES64\\${{APP_NAME}}"
RequestExecutionLevel admin

; Install Section
Section "Ana Program" SecMain
    SetOutPath "$INSTDIR"
    File "dist\\${{APP_EXE}}"
    
    ; Başlat menüsü kısayolu
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Kaldır.lnk" "$INSTDIR\\Uninstall.exe"
    
    ; Masaüstü kısayolu
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\${{APP_EXE}}"
    
    ; Uninstaller
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
    
    ; Registry
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
SectionEnd

; Uninstall Section
Section "Uninstall"
    Delete "$INSTDIR\\${{APP_EXE}}"
    Delete "$INSTDIR\\Uninstall.exe"
    
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\Kaldır.lnk"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    RMDir "$INSTDIR"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
SectionEnd
'''
    
    nsis_file = PROJECT_ROOT / "installer.nsi"
    with open(nsis_file, 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    print(f"   ✓ NSIS script oluşturuldu: {nsis_file.name}")
    print("   ℹ️ Installer oluşturmak için NSIS ile derleyin")

def cleanup_temp_files():
    """Geçici dosyaları temizle"""
    print("🧽 Geçici dosyalar temizleniyor...")
    
    temp_files = [
        PROJECT_ROOT / f"{APP_NAME.replace(' ', '_')}.spec",
        PROJECT_ROOT / "version_info.txt",
        PROJECT_ROOT / "installer.nsi"
    ]
    
    for temp_file in temp_files:
        if temp_file.exists():
            temp_file.unlink()
            print(f"   ✓ {temp_file.name} silindi")

def main():
    """Ana build fonksiyonu"""
    print(f"🚀 {APP_NAME} v{APP_VERSION} Build Süreci Başlıyor...")
    print("=" * 60)
    
    # 1. Bağımlılık kontrolü
    if not check_dependencies():
        print("\n❌ Build durduruluyor: Eksik bağımlılıklar")
        return False
    
    # 2. Build dizinlerini temizle
    clean_build_dirs()
    
    # 3. Version info oluştur
    create_version_info()
    
    # 4. Spec dosyası oluştur
    spec_file = create_spec_file()
    
    # 5. Executable oluştur
    if not build_executable(spec_file):
        print("\n❌ Build başarısız!")
        return False
    
    # 6. Optimize et
    optimize_executable()
    
    # 7. Installer script oluştur
    create_installer()
    
    # 8. Geçici dosyaları temizle
    cleanup_temp_files()
    
    print("\n" + "=" * 60)
    print("✅ Build süreci tamamlandı!")
    
    exe_path = DIST_DIR / f"{APP_NAME.replace(' ', '_')}.exe"
    if exe_path.exists():
        print(f"📁 Executable konumu: {exe_path}")
        print(f"📏 Dosya boyutu: {exe_path.stat().st_size / (1024*1024):.2f} MB")
    
    print("\n🎉 Modern Userbot Manager başarıyla oluşturuldu!")
    print("   • Executable'ı test etmeyi unutmayın")
    print("   • Windows Defender gibi antivirüsler tarafından yanlış pozitif alabilir")
    print("   • Gerekirse executable'ı güvenlik yazılımı istisna listesine ekleyin")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n⚠️ Build süreci kullanıcı tarafından iptal edildi")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Beklenmedik hata: {e}")
        sys.exit(1)
