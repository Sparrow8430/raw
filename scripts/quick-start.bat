@echo off
REM Pure Browser Project - Quick Start Script (Windows)

echo ========================================
echo   Pure Browser Project - Quick Start
echo ========================================
echo.

REM Check Python
echo Checking prerequisites...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python 3 not found. Please install Python 3.8+
    pause
    exit /b 1
)
echo [OK] Python 3 found

REM Check Node.js
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Node.js not found. Please install Node.js 18+
    pause
    exit /b 1
)
echo [OK] Node.js found

REM Setup SearxNG
echo.
echo [1/4] Setting up SearxNG...
if not exist searx-venv (
    call scripts\setup-searx.bat
) else (
    echo [OK] SearxNG already setup
)

REM Setup Protocol
echo.
echo [2/4] Setting up Protocol Server...
cd protocol
if not exist venv (
    python -m venv venv
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet
    echo [OK] Protocol dependencies installed
) else (
    echo [OK] Protocol already setup
)
cd ..

REM Setup Browser
echo.
echo [3/4] Setting up Browser...
cd browser
if not exist node_modules (
    call npm install
    echo [OK] Browser dependencies installed
) else (
    echo [OK] Browser already setup
)
cd ..

REM Create launch script
echo.
echo [4/4] Creating launch script...
(
echo @echo off
echo echo Starting Pure Browser Project...
echo echo.
echo.
echo REM Start SearxNG
echo start "SearxNG" cmd /k "call searx-venv\Scripts\activate.bat && set SEARXNG_SETTINGS_PATH=%%USERPROFILE%%\.pure\searxng\settings.yml && python -m searx.webapp"
echo.
echo REM Wait for SearxNG
echo timeout /t 5 /nobreak ^> nul
echo.
echo REM Start Protocol Server
echo start "Protocol Server" cmd /k "cd protocol && call venv\Scripts\activate.bat && python server.py"
echo.
echo REM Wait for Protocol Server
echo timeout /t 3 /nobreak ^> nul
echo.
echo REM Start Browser
echo cd browser
echo npm start
) > start-pure.bat

echo.
echo ========================================
echo          Setup Complete!
echo ========================================
echo.
echo Quick Start:
echo   start-pure.bat
echo.
echo Manual Start:
echo   Terminal 1: call searx-venv\Scripts\activate.bat ^&^& python -m searx.webapp
echo   Terminal 2: cd protocol ^&^& python server.py
echo   Terminal 3: cd browser ^&^& npm start
echo.
echo Connect to peer:
echo   cd protocol ^&^& python client.py ^<peer-ip^> 9000
echo.
echo Ready to explore Pure!
echo.
pause
