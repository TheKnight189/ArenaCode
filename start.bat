@echo off
chcp 65001 > nul
title CodeArena Server
cls
echo ===================================================================
echo             CODEARENA - HE THONG QUAN TRI NGUOI DUNG
echo ===================================================================
echo.
echo Dang kiem tra moi truong Python...
python --version
if errorlevel 1 (
    echo [LOI] Khong tim thay Python. Vui long cai dat Python 3.10+ de chay backend.
    pause
    exit /b
)

echo.
echo Dang cai dat/kiem tra thu vien can thiet tu requirements.txt...
python -m pip install -r requirements.txt --quiet

echo.
echo Dang khoi chay CodeArena Backend Server tai cong 8000...
echo Mo trinh duyet tai: http://localhost:8000
start http://localhost:8000

python run_server.py
pause

