@echo off
title DEEPALL - IDDAA ORAN VE LISTE CEKME
color 0A
cls
echo ==========================================
echo   DEEPALL (IDDAA) ISLEMI BASLIYOR...
echo   Hedef: Liste ve Oranlarin Cekilmesi
echo ==========================================
echo.

REM --- PYTHON SCRIPTINI CALISTIR ---
call C:\Users\YUSUF\AppData\Local\Programs\Python\Python314\python.exe scraperyusuf_deepall_v1.py

REM --- HATA KONTROLU (Script calisti mi?) ---
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [KRITIK HATA] scraperyusuf_deepall_v1.py calistirilirken hata olustu!
    echo Lutfen yukaridaki hata mesajini kontrol et.
    echo Pencereyi kapatmak icin bir tusa basin...
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   GIT ISLEMLERI BASLIYOR...
echo ==========================================
echo.

REM --- GIT ISLEMLERI ---
git add .
git commit -m "🤖 Otomatik Guncelleme: Deepall ile Iddaa.com liste ve oranlari cekildi"
git pull --rebase origin main
git push

REM --- GIT PUSH SONUC KONTROLU ---
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [GIT HATASI] Push islemi basarisiz! (Cakisma veya baglanti sorunu)
    echo Lutfen hatayi kontrol et. Pencereyi kapatma.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo   ISLEM BASARILI!
echo   TUM VERILER GITHUB'A YUKLENDI.
echo   PENCERE 3 SANIYE SONRA OTOMATIK KAPANACAK...
echo ==========================================
timeout /t 3 >nul
exit