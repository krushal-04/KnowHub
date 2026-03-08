@echo off
title KnowledgeShare Setup
color 0A

echo.
echo  ==========================================
echo   KnowledgeShare - Windows Setup
echo  ==========================================
echo.

REM Check Python
echo [1/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python not found!
    echo  Download from: https://python.org
    echo  Make sure to check "Add Python to PATH"
    pause
    exit /b 1
)
python --version
echo  OK
echo.

REM Create venv
echo [2/6] Creating virtual environment...
if exist "venv\" (
    echo  Already exists, skipping.
) else (
    python -m venv venv
    echo  Created venv\
)
echo.

REM Activate
echo [3/6] Activating virtual environment...
call venv\Scripts\activate.bat
echo  Active
echo.

REM Upgrade pip
echo [4/6] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo  Done
echo.

REM Install packages
echo [5/6] Installing Django and packages...
pip install -r requirements.txt
if errorlevel 1 (
    echo  ERROR: Installation failed. Check your internet connection.
    pause
    exit /b 1
)
echo.

REM Migrate + seed
echo [6/6] Setting up database...
python manage.py migrate
echo.
python setup_demo.py

echo.
echo  ==========================================
echo   DONE! Now run:
echo.
echo   venv\Scripts\activate
echo   python manage.py runserver
echo.
echo   Then open: http://127.0.0.1:8000
echo  ==========================================
echo.
pause
