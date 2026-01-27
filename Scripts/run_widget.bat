@echo off
REM Launch AURA Floating Widget
REM Uses pythonw.exe for no console window

REM Change to parent directory (e:\agent)
cd /d "%~dp0\.."

if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Use pythonw for silent launch (no console)
if exist "venv\Scripts\pythonw.exe" (
    start "" venv\Scripts\pythonw.exe aura_floating_widget\aura_widget.py
) else (
    REM Fallback to regular python
    start "" python aura_floating_widget\aura_widget.py
)
