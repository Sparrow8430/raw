@echo off
REM Create virtual environment
python -m venv searx-venv

REM Activate it
call searx-venv\Scripts\activate

REM Upgrade pip
python -m pip install --upgrade pip

REM Install SearxNG
pip install git+https://github.com/searxng/searxng.git

REM Tell user how to run
echo.
echo SearxNG installed.
echo Run your SearxNG server with:
echo   call searx-venv\Scripts\activate
echo   python -m searx.webapp
pause
