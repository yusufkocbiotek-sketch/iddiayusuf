@echo off
title 🕵️ SKOR ÇEKİCİ - SPORDB MATCHER
echo.
echo =====================================================
echo          SPORDB SKOR GÜNCELLEYİCİ (skor_json_eslestir.py)
echo =====================================================
echo.

cd /d "%~dp0"

echo Python dosyası çalıştırılıyor...
python skor_json_eslestir.py

echo.
echo =====================================================
echo İşlem tamamlandı. Pencereyi kapatmak için bir tuşa basın...
pause