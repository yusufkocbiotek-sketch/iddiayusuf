@echo off
setlocal enabledelayedexpansion

REM === PROJE DIZINI ===
set "PROJ=C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main"

REM === PYTHON ===
set "PYEXE=C:\Users\YUSUF\AppData\Local\Programs\Python\Python314\python.exe"

REM === LOG DOSYASI ===
set "LOG=%PROJ%\logs\skor_update_%DATE:~-4%-%DATE:~3,2%-%DATE:~0,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%.log"
set "LOG=%LOG: =0%"

if not exist "%PROJ%\logs" mkdir "%PROJ%\logs"

cd /d "%PROJ%"

echo ============================================================ >> "%LOG%"
echo START: %DATE% %TIME% >> "%LOG%"
echo ============================================================ >> "%LOG%"

REM === 1) SKOR SCRIPT ===
"%PYEXE%" "%PROJ%\skor_json_eslestir.py" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: skor_json_eslestir.py failed >> "%LOG%"
  goto :end
)

REM === 2) GIT (degisiklik varsa commit/push) ===
git add public/data/mac.json public/data/skorlar_spordb.json public/data/gecmis_maclar.json >> "%LOG%" 2>&1

REM staged degisiklik var mi?
git diff --cached --quiet
if %errorlevel%==0 (
  echo INFO: No changes to commit. >> "%LOG%"
  goto :end
)

set "MSG=Skor guncelleme (son 5 gun) %DATE% %TIME%"
git commit -m "%MSG%" >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: git commit failed >> "%LOG%"
  goto :end
)

git push origin main >> "%LOG%" 2>&1
if errorlevel 1 (
  echo ERROR: git push failed >> "%LOG%"
  goto :end
)

echo OK: Completed successfully. >> "%LOG%"

:end
echo END: %DATE% %TIME% >> "%LOG%"
endlocal
exit /b 0