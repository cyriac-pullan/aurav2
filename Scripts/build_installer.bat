@echo off
REM =====================================================
REM  Build AURA Windows Installer
REM  Requires: Inno Setup installed
REM =====================================================

echo.
echo ========================================
echo  Building AURA Windows Installer
echo ========================================
echo.

cd /d "%~dp0\.."

REM Check if dist\AURA exists
if not exist "dist\AURA\AURA.exe" (
    echo ERROR: dist\AURA\AURA.exe not found!
    echo.
    echo Please run build_exe.bat first to create the executable.
    pause
    exit /b 1
)

REM Create output directory
if not exist "Installer\installer_output" mkdir "Installer\installer_output"

REM Copy quick start guide to dist folder
if exist "Installer\QUICK_START.txt" (
    copy "Installer\QUICK_START.txt" "dist\AURA\" >nul
)

echo Building installer with Inno Setup...
echo.

set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" (
    echo ERROR: Inno Setup Compiler not found!
    echo Please install from: https://jrsoftware.org/isinfo.php
    pause
    exit /b 1
)

"%ISCC%" "Installer\installer_script.iss"

if errorlevel 1 (
    echo.
    echo ERROR: Installer build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Installer Build Complete!
echo ========================================
echo.
echo Installer created:
echo   Installer\installer_output\AURA-Setup.exe
echo.
echo You can now share this file with others!
echo.
pause
