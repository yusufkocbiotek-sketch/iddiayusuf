@echo off
title SPORDB SKOR GUNCELLEME VE YUKLEME
color 0B
cls
echo ==========================================
echo   SPORDB DETAYLI SKOR CEKME BASLIYOR...
echo ==========================================
echo.

REM Python Scriptini Çalıştır
call C:\Users\YUSUF\AppData\Local\Programs\Python\Python314\python.exe skor_json_eslestir.py

REM Hata Kontrolü
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] skor_json_eslestir.py calisirken hata olustu!
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
git commit -m "🤖 Otomatik Guncelleme: SPORDB detayli skorlar ve IY verileri islendi"
git pull --rebase origin main
git push

REM Git Push Sonuç Kontrolü
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [HATA] Git push basarisiz!
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