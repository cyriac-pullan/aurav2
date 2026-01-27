# Building Professional AURA Installer

## 🎯 Overview

This guide explains how to build `AURA-Setup.exe` - a professional Windows installer that works like apps you download from the internet.

## 📋 Prerequisites

### Required Software

1. **Python 3.8+** - Already installed ✅
2. **PyInstaller** - Already installed ✅
3. **Inno Setup 6** - Download from: https://jrsoftware.org/isdl.php

### Install Inno Setup

1. Download from https://jrsoftware.org/isdl.php
2. Run the installer (choose default options)
3. Inno Setup will be installed to: `C:\Program Files (x86)\Inno Setup 6\`

---

## 🚀 Quick Build

### Option 1: Complete Build (Recommended)

```bash
build_complete_installer.bat
```

This single command will:
1. ✅ Build standalone `AURA.exe` with PyInstaller
2. ✅ Create `AURA-Setup.exe` installer with Inno Setup
3. ✅ Output `installer_output\AURA-Setup.exe`

### Option 2: Step-by-Step Build

**Step 1: Build EXE**
```bash
build_exe.bat
```

**Step 2: Create Installer (requires Inno Setup)**
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_script.iss
```

---

## 📁 Build Files

| File | Purpose |
|------|---------|
| `build_installer.spec` | PyInstaller configuration |
| `installer_script.iss` | Inno Setup installer configuration |
| `build_exe.bat` | Builds standalone .exe |
| `build_complete_installer.bat` | Complete build process |
| `jarvis_icon.ico` | Application icon |

---

## 🎨 What Gets Built

### Standalone Executable

**Location:** `dist\AURA\AURA.exe`

**Contents:**
- AURA application (bundled Python + all dependencies)
- API Key Wizard
- All required DLLs and libraries
- No Python installation required!

**Size:** ~100-150MB (includes everything)

### Final Installer

**Location:** `installer_output\AURA-Setup.exe`

**What it does:**
- Professional install wizard with modern UI
- Installs to `C:\Program Files\AURA\`
- Creates Start Menu entry
- Optional desktop shortcut
- Optional auto-start at Windows startup
- Includes uninstaller

**Size:** ~50-80MB (compressed)

---

## 🧪 Testing

### Test Standalone EXE

After running `build_exe.bat`:

```bash
dist\AURA\AURA.exe
```

✅ Should launch without errors
✅ API wizard should appear (first run)
✅ No console window

### Test Installer

After running `build_complete_installer.bat`:

1. Double-click `installer_output\AURA-Setup.exe`
2. Follow installation wizard
3. Check Start Menu for "AURA" entry
4. Launch AURA from Start Menu
5. Verify it works correctly

### Test on Clean Machine (Recommended)

Best practice: Test on a VM without Python installed to ensure true standalone functionality.

---

## 🐛 Troubleshooting

### PyInstaller Errors

**Missing Module:**
```
ModuleNotFoundError: No module named 'xyz'
```

**Fix:** Add to `hiddenimports` in `build_installer.spec`:
```python
hiddenimports=[
    ...
    'xyz',  # Add missing module
]
```

**DLL Missing:**

Check `binaries` section in `.spec` file.

### Inno Setup Errors

**ISCC.exe not found:**
- Install Inno Setup from https://jrsoftware.org/isdl.php
- Verify installation path: `C:\Program Files (x86)\Inno Setup 6\`

**File not found errors:**
- Ensure `build_exe.bat` ran successfully first
- Check `dist\AURA\` folder exists with `AURA.exe`

### Runtime Errors

**API Key Wizard doesn't appear:**
- Check if `api_key_wizard.py` is in `datas` section
- Verify `api_key_helper.py` is included

**Voice features not working:**
- Ensure `pyttsx3` and dependencies are in `hiddenimports`
- Check Windows speech engines are installed

---

## 📦 Distribution

### What to Share

**Single File:**
```
installer_output\AURA-Setup.exe
```

That's it! Users just:
1. Download `AURA-Setup.exe`
2. Double-click to install
3. Launch from Start Menu

### Hosting Options

- **GitHub Releases** - Free hosting for open source
- **Google Drive / Dropbox** - Direct download link
- **Personal website** - Full control
- **Microsoft Store** - Professional distribution (requires MSIX)

---

## 🎯 Build Checklist

### Before Building

- [ ] All code tested and working
- [ ] `api_key_wizard.py` works correctly
- [ ] Icon file (`jarvis_icon.ico`) exists
- [ ] Version number updated in `installer_script.iss`
- [ ] PyInstaller installed (`pip install pyinstaller`)
- [ ] Inno Setup 6 installed

### Build Process

- [ ] Run `build_complete_installer.bat`
- [ ] Verify no errors in build output
- [ ] Test `dist\AURA\AURA.exe` manually
- [ ] Test `AURA-Setup.exe` installation
- [ ] Test on clean machine (if possible)

### Release

- [ ] Create release notes
- [ ] Test installer one final time
- [ ] Upload to distribution platform
- [ ] Share download link

---

## 🔧 Advanced Configuration

### Custom Icon

Replace `jarvis_icon.ico` with your own icon file, then rebuild.

### Change Install Location

Edit `installer_script.iss`:
```pascal
DefaultDirName={autopf}\YourAppName
```

### Add Auto-Start

Already included as optional checkbox during installation!

### Reduce Size

Edit `build_installer.spec`:
```python
excludes=[
    'matplotlib',
    'numpy',
    'pandas',
    # Add more unused libraries
]
```

---

## ✅ Success!

Once built, you have a **professional Windows installer** that:
- ✅ Works like apps downloaded from the internet
- ✅ No Python required for end users
- ✅ Professional install wizard
- ✅ Start Menu integration
- ✅ Proper uninstaller
- ✅ Single-file distribution

**AURA is now ready for professional distribution!** 🚀
