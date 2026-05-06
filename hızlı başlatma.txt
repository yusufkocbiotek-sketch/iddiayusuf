@echo off
setlocal EnableDelayedExpansion

title ⚽ IDDAA FULL OTOMASYON (AUTO GIT PUSH)
color 0E

echo ============================================================
echo    ⚽ IDDAA FULL OTOMASYON BASLATILIYOR...
echo ============================================================
echo.

cd /d "C:\Users\YUSUF\OneDrive\Desktop\iddiayusuf-main"

REM ───────────────────────────────────────────────────────────
REM 1) ORANLAR ÇEK
REM ───────────────────────────────────────────────────────────
echo.
echo [1/3] 📊 ORANLAR CEKILIYOR...
echo ============================================================
python scraper_full.py
set PYTHON1_EXIT=%ERRORLEVEL%

if %PYTHON1_EXIT% NEQ 0 (
    echo.
    echo ❌ scraper_full.py hata ile bitti (exit code: %PYTHON1_EXIT%). Git push atlanıyor.
    goto END
)

echo.
echo ✅ Oranlar cekildi! 5 saniye bekleniyor...
timeout /t 5 /nobreak >nul

REM ───────────────────────────────────────────────────────────
REM 2) SKORLAR EŞLEŞTİR
REM ───────────────────────────────────────────────────────────
echo.
echo [2/3] ⚽ SKORLAR ESLESTIRILIYOR...
echo ============================================================
python skor_json_eslestir.py
set PYTHON2_EXIT=%ERRORLEVEL%

if %PYTHON2_EXIT% NEQ 0 (
    echo.
    echo ❌ skor_json_eslestir.py hata ile bitti (exit code: %PYTHON2_EXIT%). Git push atlanıyor.
    goto END
)

echo.
echo ✅ Skorlar eslestirildi!
timeout /t 3 /nobreak >nul

REM ───────────────────────────────────────────────────────────
REM 3) GIT PUSH (OTOMATİK)
REM ───────────────────────────────────────────────────────────
echo.
echo [3/3] 📌 GIT PUSH ISLEMI (OTOMATIK)
echo ============================================================
echo.

echo 🚀 Değişiklikler stage ediliyor (git add -A)...
git add -A
set GIT_ADD_EXIT=%ERRORLEVEL%

if %GIT_ADD_EXIT% NEQ 0 (
    echo ❌ git add başarısız oldu (exit code: %GIT_ADD_EXIT%). Push atlanıyor.
    goto END
)

echo ✅ git add tamamlandı.

REM Timestamp ile commit mesajı
for /f "tokens=1-4 delims=/:. " %%a in ("%date% %time%") do (
    set "TIMESTAMP=%%a-%%b-%%c_%%d%%e"
)

echo 📝 Commit oluşturuluyor: "Oranlar ve skorlar otomatik guncellendi - %TIMESTAMP%"
git commit -m "Oranlar ve skorlar otomatik guncellendi - %TIMESTAMP%"
set GIT_COMMIT_EXIT=%ERRORLEVEL%

if %GIT_COMMIT_EXIT% NEQ 0 (
    echo ⚠️ git commit başarısız oldu (exit code: %GIT_COMMIT_EXIT%).
    echo    (Muhtemelen commit edilecek değişiklik yok.) Push atlanıyor.
    goto END
)

echo ✅ Commit oluşturuldu.

echo ⬆️ Uzak repoya gönderiliyor (git push origin main)...
git push origin main
set GIT_PUSH_EXIT=%ERRORLEVEL%

if %GIT_PUSH_EXIT% NEQ 0 (
    echo ❌ git push başarısız oldu (exit code: %GIT_PUSH_EXIT%).
    echo    Kontrol et: remote ayarı (git remote -v), branch adı (main), kimlik doğrulama (SSH / Token / Credential Manager).
    goto END
)

echo ✅ Siteye başarıyla gönderildi!

:END
echo.
echo ============================================================
echo    🎉 TUM ISLEMLER TAMAMLANDI!
echo ============================================================
echo.

endlocal