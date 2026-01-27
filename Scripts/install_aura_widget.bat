@echo off
REM =====================================================
REM  AURA Floating Widget - Complete Installation
REM  Sets up dependencies, API keys, and shortcuts
REM =====================================================

echo.
echo ========================================
echo  AURA Floating Widget Installer
echo ========================================
echo.

REM Change to parent directory (e:\agent)
cd /d "%~dp0\.."

REM Check if Python is installed
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)
echo   Python found!

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo.
    echo [2/5] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo   Virtual environment created!
) else (
    echo.
    echo [2/5] Virtual environment already exists
)

REM Activate virtual environment
echo.
echo [3/5] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)

REM Install dependencies
echo.
echo [4/5] Installing dependencies...
echo   This may take a few minutes...
echo.

REM Core dependencies
pip install --upgrade pip >nul 2>&1
pip install PyQt5 >nul 2>&1
pip install keyring >nul 2>&1
pip install pyttsx3 >nul 2>&1
pip install SpeechRecognition >nul 2>&1
pip install pyaudio >nul 2>&1
pip install requests >nul 2>&1
pip install google-generativeai >nul 2>&1
pip install openai >nul 2>&1

echo   Dependencies installed!

REM Run API Key Wizard (first-run setup)
echo.
echo [5/5] Starting AURA Setup Wizard...
echo.
python api_key_wizard.py
if errorlevel 1 (
    echo.
    echo Setup wizard cancelled or failed
    echo You can run it again later with: test_wizard.bat
)

REM Create desktop shortcut
echo.
echo ========================================
echo  Creating Desktop Shortcut...
echo ========================================
python create_desktop_shortcut.py

echo.
echo ========================================
echo  Installation Complete!
echo ========================================
echo.
echo  AURA is ready to use!
echo.
echo  To launch AURA:
echo    - Double-click the desktop shortcut
echo    - Or run: run_widget.bat
echo.
pause
