@echo off
setlocal

set "PROJ=C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main"
set "PYEXE=C:\Users\YUSUF\AppData\Local\Programs\Python\Python314\python.exe"
set "SCRIPT=%PROJ%\scraperyusuf_deepall_v1.py"

if not exist "%PROJ%\logs" mkdir "%PROJ%\logs"

REM timestamp (Windows locale'ye göre değişebilir; boşlukları 0 yapıyoruz)
set "TS=%DATE:~-4%-%DATE:~3,2%-%DATE:~0,2%_%TIME:~0,2%-%TIME:~3,2%-%TIME:~6,2%"
set "TS=%TS: =0%"

set "LOG=%PROJ%\logs\deepall_%TS%.log"

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Set-Location '%PROJ%';" ^
  "& '%PYEXE%' '%SCRIPT%' *>> '%LOG%';" ^
  "exit $LASTEXITCODE"

endlocal
exit /b 0