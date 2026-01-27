@echo off
REM =====================================================
REM  Build AURA Standalone Executable
REM  Uses PyInstaller to create standalone .exe
REM =====================================================

echo.
echo ========================================
echo  Building AURA Standalone Executable
echo ========================================
echo.

cd /d "%~dp0\.."

REM Clean previous builds
if exist "build" (
    echo Cleaning previous builds...
    rmdir /s /q build
)
if exist "dist" (
    rmdir /s /q dist
)

REM Build with PyInstaller
echo.
echo Building standalone executable...
echo This may take a few minutes...
echo.

REM NOTE:
REM The PyInstaller spec file lives in the "Installer" subfolder.
REM We must point PyInstaller at that relative path from the project root.
pyinstaller Installer\build_installer.spec --clean --noconfirm

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build Complete!
echo ========================================
echo.
echo Standalone executable created:
echo   dist\AURA\AURA.exe
echo.
echo You can test it by running:
echo   dist\AURA\AURA.exe
echo.
pause
