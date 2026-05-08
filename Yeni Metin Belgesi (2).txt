@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo   İDDAA Oran Çekici - Otomatik Görev
echo ========================================
echo.

REM Python'un yüklü olup olmadığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ HATA: Python yüklü değil!
    echo.
    pause
    exit /b 1
)

REM Gerekli kütüphaneleri yükle
echo 📦 Kütüphaneler kontrol ediliyor...
pip install selenium webdriver-manager -q

REM Scripti çalıştır
echo.
echo 🚀 Scraper başlatılıyor...
python scraper_gecmis.py

REM Sonuç
if errorlevel 0 (
    echo.
    echo ✅ Scraper tamamlandı!
    echo.
    echo 💾 Dosyalar git'e ekleniyor...
    git add -A
    git commit -m "Otomatik güncelleme - Oranlar ve maç verileri"
    git push
    echo.
    echo 🎉 Push başarılı!
) else (
    echo.
    echo ❌ Scraper hatası!
)

pause