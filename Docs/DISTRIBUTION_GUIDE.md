# AURA Distribution Guide

How to build and share AURA with others.

## 📦 Quick Distribution (ZIP Method)

If you already have a built version in `dist\AURA\`:

1. **ZIP the entire `dist\AURA` folder** (includes `AURA.exe` + `_internal/`)
2. **Include** [QUICK_START.txt](file:///e:/agent/Installer/QUICK_START.txt) in the ZIP
3. Share the ZIP - recipients extract and run `AURA.exe`

> [!IMPORTANT]
> Never share your `.env` file - it contains your personal API key!

---

## 🛠️ Build the Installer

### Prerequisites
- **Python 3.8+** with dependencies installed (`pip install -r requirements.txt`)
- **PyInstaller** (`pip install pyinstaller`)
- **Inno Setup** (download from [jrsoftware.org](https://jrsoftware.org/isinfo.php))

### Step 1: Build the Executable
```batch
Scripts\build_exe.bat
```
This creates `dist\AURA\AURA.exe` with all dependencies bundled.

### Step 2: Build the Installer
```batch
Scripts\build_installer.bat
```
This creates `Installer\installer_output\AURA-Setup.exe` (~50-80 MB)

---

## 📋 What's Included in the Installer

| Feature | Description |
|---------|-------------|
| Desktop shortcut | Optional during install |
| Start Menu entry | Automatic |
| Startup launch | Optional (launches AURA at Windows boot) |
| First-run wizard | Prompts for API key setup |
| Clean uninstall | Removes all files and registry entries |

---

## 🔑 API Key Setup for Recipients

Recipients need their own API key. They can get one from:
- **OpenRouter** (recommended): [openrouter.ai](https://openrouter.ai/) - $5 free credit
- **Google AI Studio**: [aistudio.google.com](https://aistudio.google.com/) - Free tier available

On first launch, AURA will guide them through the API key setup wizard.

---

## 📁 Files NOT to Include

| File/Folder | Reason |
|-------------|--------|
| `.env` | Contains YOUR API key |
| `venv/` | User creates their own |
| `__pycache__/` | Generated files |
| `.git/` | Source control only |
