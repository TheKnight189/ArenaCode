@echo off
chcp 65001 > nul
cd /d "%~dp0"
title CodeArena Backend Server [Port 8000]
cls
echo ===================================================================
echo             CODEARENA - HE THONG AUTOMATED ONLINE JUDGE
echo ===================================================================
echo.
echo [*] Kiem tra moi truong Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python! Vui long cai dat Python 3.10+ tren may tinh.
    echo       Tai ve tai: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [*] Kiem tra cac thu vien can thiet...
python -c "import fastapi, uvicorn, pydantic" >nul 2>&1
if errorlevel 1 (
    echo [*] Dang cai dat thu vien lan dau tu requirements.txt...
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo [LOI] Cai dat thu vien that bai. Vui long kiem tra ket noi mang.
        pause
        exit /b 1
    )
)

echo.
echo ===================================================================
echo   MAY CHU BACKEND DANG KHOI CHAY TAI: http://localhost:8000
echo   - Cong Sinh Vien:       http://localhost:8000/student
echo   - Cong Giang Vien:      http://localhost:8000/teacher
echo   - Cong Quan Tri (Admin):http://localhost:8000/admin
echo   - Tai lieu API Swagger: http://localhost:8000/docs
echo ===================================================================
echo.
echo [*] Tu dong mo trinh duyet Web CodeArena...
start http://localhost:8000

echo [*] Dang khoi chay Uvicorn... Nhan Ctrl + C de dung server.
echo.
python run_server.py
pause
