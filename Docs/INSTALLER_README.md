# Quick Start - AURA Professional Installer

## For End Users (Downloading AURA)

1. **Download** `AURA-Setup.exe`
2. **Double-click** to install
3. **Follow** the installation wizard
4. **Launch** AURA from Start Menu
5. **Complete** first-run API setup

That's it! No Python or technical knowledge needed.

---

## For Developers (Building the Installer)

### Prerequisites
- Python 3.8+ installed ✅
- Download Inno Setup 6: https://jrsoftware.org/isdl.php

### Build Steps

```bash
# One command to build everything:
build_complete_installer.bat
```

**Output:** `installer_output\AURA-Setup.exe`

### What Gets Created

```
AURA-Setup.exe (50-80MB)
├── Professional install wizard
├── Standalone AURA.exe (no Python needed)
├── Desktop shortcut (optional)
├── Start Menu entry
├── Auto-start option
└── Uninstaller
```

---

## Distribution Checklist

- [ ] Build installer: `build_complete_installer.bat`
- [ ] Test on your machine
- [ ] Test on clean VM (recommended)
- [ ] Upload `AURA-Setup.exe` to hosting
- [ ] Share download link

---

## Support

**Build Issues?** See `BUILD_INSTALLER_GUIDE.md`
**Runtime Issues?** See `WIZARD_INSTALLATION.md`

**Links:**
- Full Build Guide: `BUILD_INSTALLER_GUIDE.md`
- Wizard Guide: `WIZARD_INSTALLATION.md`
- Inno Setup: https://jrsoftware.org/isdl.php
