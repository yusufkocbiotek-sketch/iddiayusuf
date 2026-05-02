@echo off
chcp 65001 >nul

cd /d C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main

set LOG=logs\otomatik_guncelle.log

if not exist logs mkdir logs

echo. >> %LOG%
echo ========================================== >> %LOG%
echo IDDAA OTOMATIK GUNCELLEME BASLADI >> %LOG%
echo Tarih Saat: %date% %time% >> %LOG%
echo ========================================== >> %LOG%

echo [1/4] Oranlar cekiliyor... >> %LOG%
python scraper_full.py >> %LOG% 2>&1

echo. >> %LOG%
echo [2/4] Gecmis maclar guncelleniyor... >> %LOG%
python scraper_gecmis.py >> %LOG% 2>&1

echo. >> %LOG%
echo [3/4] Skorlar eslestiriliyor... >> %LOG%
python skor_json_eslestir.py >> %LOG% 2>&1

echo. >> %LOG%
echo [4/4] GitHub'a yukleniyor... >> %LOG%
git add -A >> %LOG% 2>&1
git commit -m "Otomatik guncelleme %date% %time%" >> %LOG% 2>&1
git push >> %LOG% 2>&1

echo. >> %LOG%
echo TAMAMLANDI >> %LOG%
echo Tarih Saat: %date% %time% >> %LOG%
echo ========================================== >> %LOG%