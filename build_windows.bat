@echo off
echo Building Windows executable...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Install/upgrade pyinstaller and requests
echo Installing dependencies...
pip install --upgrade pyinstaller requests

echo.
echo Building executable...
pyinstaller --onefile --console --name sports_scraper sports_scraper.py

echo.
echo Build complete!
echo The executable is located at: dist\sports_scraper.exe
echo.
pause
