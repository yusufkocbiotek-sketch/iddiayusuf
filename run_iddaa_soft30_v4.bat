@echo off
setlocal enabledelayedexpansion

REM === PROJE DIZINI ===
set "PROJ=C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main"

REM === PYTHON ===
set "PYEXE=C:\Users\YUSUF\AppData\Local\Programs\Python\Python314\python.exe"

REM === SCRIPT ===
set "SCRIPT=%PROJ%\scraperyusuf_soft30_v4.py"

REM === LOG ===
if not exist "%PROJ%\logs" mkdir "%PROJ%\logs"
set "TS=%DATE:~-4%-%DATE:~3,2%-%DATE:~0,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%"
set "TS=%TS: =0%"
set "LOG=%PROJ%\logs\iddaa_soft30_v4_%TS%.log"

cd /d "%PROJ%"

echo ============================================================>> "%LOG%"
echo START: %DATE% %TIME%>> "%LOG%"
echo ============================================================>> "%LOG%"

REM === RUN ===
"%PYEXE%" "%SCRIPT%" >> "%LOG%" 2>&1

echo ============================================================>> "%LOG%"
echo END: %DATE% %TIME%>> "%LOG%"
echo ============================================================>> "%LOG%"

endlocal
exit /b 0