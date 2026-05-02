@echo off
chcp 65001 >nul
set PYTHONUTF8=1

cd /d C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main

set LOG=logs\otomatik_guncelle.log
if not exist logs mkdir logs

echo. >> %LOG%
echo ========================================== >> %LOG%
echo IDDAA OTOMATIK GUNCELLEME BASLADI >> %LOG%
echo Tarih Saat: %date% %time% >> %LOG%
echo ========================================== >> %LOG%

echo [1/3] Oranlar cekiliyor... >> %LOG%
python -X utf8 scraper_full.py >> %LOG% 2>&1

echo. >> %LOG%
echo [2/3] Skorlar eslestiriliyor... >> %LOG%
python -X utf8 skor_json_eslestir.py >> %LOG% 2>&1

echo. >> %LOG%
echo [3/3] GitHub'a yukleniyor... >> %LOG%
git add -A >> %LOG% 2>&1
git commit -m "Otomatik guncelleme %date% %time%" >> %LOG% 2>&1
git push >> %LOG% 2>&1

echo. >> %LOG%
echo TAMAMLANDI >> %LOG%
echo Tarih Saat: %date% %time% >> %LOG%
echo ========================================== >> %LOG%