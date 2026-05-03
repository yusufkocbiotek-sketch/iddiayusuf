@echo off
chcp 65001 >nul
set PYTHONUTF8=1

cd /d C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main

set LOG=logs\skor_guncelle.log
if not exist logs mkdir logs

echo. >> %LOG%
echo ========================================== >> %LOG%
echo SKOR GUNCELLEME BASLADI >> %LOG%
echo Tarih Saat: %date% %time% >> %LOG%
echo ========================================== >> %LOG%

python -X utf8 skor_json_eslestir.py >> %LOG% 2>&1

git add -A >> %LOG% 2>&1
git commit -m "Otomatik skor guncelleme %date% %time%" >> %LOG% 2>&1
git push >> %LOG% 2>&1

echo TAMAMLANDI >> %LOG%