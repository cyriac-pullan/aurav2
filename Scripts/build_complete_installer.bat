@echo off
REM =====================================================
REM  Build Complete AURA Installer
REM  Step 1: Build EXE with PyInstaller
REM  Step 2: Create installer with Inno Setup
REM =====================================================

echo.
echo ========================================
echo  AURA Complete Installer Builder
echo ========================================
echo.

cd /d "%~dp0"

REM Check if PyInstaller is installed
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo ERROR: PyInstaller not installed!
    echo Installing PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller
        pause
        exit /b 1
    )
)

REM Step 1: Build standalone EXE
echo ========================================
echo  Step 1: Building Standalone Executable
echo ========================================
echo.

call build_exe.bat
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

REM Check if Inno Setup is installed
if not exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    echo.
    echo ========================================
    echo  Inno Setup Not Found
    echo ========================================
    echo.
    echo Please install Inno Setup 6 from:
    echo https://jrsoftware.org/isdl.php
    echo.
    echo After installation, run this script again.
    echo.
    pause
    exit /b 0
)

REM Step 2: Create installer with Inno Setup
echo.
echo ========================================
echo  Step 2: Creating Installer Package
echo ========================================
echo.

"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss

if errorlevel 1 (
    echo.
    echo ERROR: Installer creation failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  SUCCESS! Installer Created
echo ========================================
echo.
echo Your installer is ready:
echo   installer_output\AURA-Setup.exe
echo.
echo File size info:
dir /b installer_output\AURA-Setup.exe | find "AURA-Setup.exe"

echo.
echo You can now distribute AURA-Setup.exe to users!
echo They just need to double-click it to install AURA.
echo.
pause
