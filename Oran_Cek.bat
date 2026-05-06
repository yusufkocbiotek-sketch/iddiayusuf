@echo off
setlocal EnableDelayedExpansion

title 🚀 ORAN ÇEKİCİ + OTOMATİK GIT PUSH (Başarılıysa)
echo.
echo =====================================================
echo          İDDAA ORAN ÇEKİCİ (scraper_full.py)
echo =====================================================
echo.

cd /d "%~dp0"

REM ─────────────────────────────────────────────────────
REM 1) Python script çalıştır
REM ─────────────────────────────────────────────────────
echo [1/4] Python dosyası çalıştırılıyor...
python scraper_full.py
set PYTHON_EXIT=%ERRORLEVEL%

if %PYTHON_EXIT% NEQ 0 (
    echo.
    echo ❌ Python script hata ile bitti (exit code: %PYTHON_EXIT%). Git işlemleri atlanıyor.
    goto END
)

echo ✅ Python script başarıyla tamamlandı.

REM ─────────────────────────────────────────────────────
REM 2) Git add
REM ─────────────────────────────────────────────────────
echo.
echo [2/4] Değişiklikler stage ediliyor (git add .)...
git add .
set GIT_ADD_EXIT=%ERRORLEVEL%

if %GIT_ADD_EXIT% NEQ 0 (
    echo ❌ git add başarısız oldu (exit code: %GIT_ADD_EXIT%). Push atlanıyor.
    goto END
)

echo ✅ git add tamamlandı.

REM ─────────────────────────────────────────────────────
REM 3) Git commit (timestamp ile)
REM ─────────────────────────────────────────────────────
echo.
echo [3/4] Commit oluşturuluyor...
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do (
    set "TIMESTAMP=%%a-%%b-%%c_%%d%%e"
)

git commit -m "Automated scrape update - %TIMESTAMP%"
set GIT_COMMIT_EXIT=%ERRORLEVEL%

if %GIT_COMMIT_EXIT% NEQ 0 (
    echo ⚠️ git commit başarısız oldu (exit code: %GIT_COMMIT_EXIT%).
    echo    (Muhtemelen çalışma dizininde commit edilecek değişiklik yok.)
    echo    Push işlemi atlanıyor.
    goto END
)

echo ✅ Commit oluşturuldu: "Automated scrape update - %TIMESTAMP%"

REM ─────────────────────────────────────────────────────
REM 4) Git push
REM ─────────────────────────────────────────────────────
echo.
echo [4/4] Değişiklikler uzak repoya gönderiliyor (git push)...
git push
set GIT_PUSH_EXIT=%ERRORLEVEL%

if %GIT_PUSH_EXIT% NEQ 0 (
    echo ❌ git push başarısız oldu (exit code: %GIT_PUSH_EXIT%).
    echo    Kontrol et: remote ayarı (git remote -v), branch adı, kimlik doğrulama (SSH/Token/Credential Manager).
    goto END
)

echo ✅ Git push başarıyla tamamlandı.

:END
echo.
echo =====================================================
echo İşlem tamamlandı.
endlocal