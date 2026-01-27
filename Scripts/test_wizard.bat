@echo off
REM Test AURA API Key Wizard

echo.
echo ========================================
echo  Testing AURA API Key Setup Wizard
echo ========================================
echo.

REM Change to parent directory (e:\agent)
cd /d "%~dp0\.."

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Run the wizard
echo Launching API Key Wizard...
python api_key_wizard.py

pause
