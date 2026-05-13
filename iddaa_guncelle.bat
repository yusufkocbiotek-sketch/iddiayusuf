@echo off
title IDDAA GUNCELLEME VE YUKLEME
color 0A
cls
echo ==========================================
echo   IDDAA.COM VERI CEKME ISLEMI BASLIYOR...
echo ==========================================
echo.

REM Python Scriptini Çalıştır
call C:\Users\YUSUF\AppData\Local\Programs\Python\Python314\python.exe final_scraper.py

REM Hata Kontrolü (Eğer script hata verirse buradan çıkma)
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] final_scraper.py calisirken hata olustu!
    echo Lutfen hatayi kontrol et, pencereyi kapatma.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   GIT ISLEMLERI BASLIYOR...
echo ==========================================
echo.

REM Git İşlemleri
git add .
git commit -m "🤖 Otomatik Guncelleme: Iddaa.com verileri cekildi"
git pull --rebase origin main
git push

REM Git Push Sonuç Kontrolü
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Git push basarisiz! (Cakisma veya baglanti sorunu olabilir)
    echo Lutfen hatayi kontrol et, pencereyi kapatma.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   ISLEM BASARILI! PENCERE KAPANIYOR...
echo ==========================================
timeout /t 2 >nul
exit