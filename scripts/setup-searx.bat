@echo off
echo Creating Python virtual environment...
python -m venv searx-venv

call searx-venv\Scripts\activate
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing SearxNG...
pip install git+https://github.com/searxng/searxng.git

echo.
echo ✅ Done!
echo To run SearxNG:
echo   call searx-venv\Scripts\activate
echo   python -m searx.webapp
pause
