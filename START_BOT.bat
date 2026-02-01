@echo off
cd /d "%~dp0"
echo ========================================================
echo   MERCURE SYSTEM - DIGITAL CONCIERGE LAUNCHER
echo ========================================================
echo.
echo Sedang menyiapkan sistem...
echo Mohon tunggu sebentar...
echo.

python run_with_ngrok.py

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Terjadi kesalahan saat menjalankan program.
    echo Mohon periksa pesan error di atas.
    pause
)
