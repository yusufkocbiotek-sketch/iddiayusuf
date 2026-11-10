@echo off
cd /d "C:\Users\YUSUF\Desktop\iddiayusuf-main"
set PYTHONIOENCODING=utf-8
chcp 65001 >nul
"C:\Users\YUSUF\AppData\Local\Programs\Python\Python314\python.exe" -X utf8 -u "C:\Users\YUSUF\Desktop\iddiayusuf-main\nesine2.py" 2>&1 | powershell -Command "$input | Tee-Object -FilePath log_nesine.txt -Append"
pause