# AURA Changelog

## Version 1.0.0 - Professional Release (2026-01-19)

### ✨ Major Features

**API Key Wizard**
- Beautiful PyQt5 setup wizard for first-run experience
- Multi-provider support (OpenRouter, Gemini, OpenAI)
- Real-time API validation
- Secure storage via Windows Credential Manager
- Integrated into widget startup

**Professional Windows Installer**
- PyInstaller configuration for standalone .exe
- Inno Setup installer script (AURA-Setup.exe)
- No Python dependencies required for end users
- Start Menu integration
- Optional desktop shortcut and auto-start
- Professional uninstaller

**AURA v2 Intelligent Routing**
- 85%+ commands run locally (no API needed)
- Smart routing between local execution and LLM
- Token savings and cost reduction
- Wake word detection for hands-free mode

### 🎨 Improvements

**UI/UX**
- Floating widget with pulsing orb animation
- JARVIS-inspired dark theme
- Smooth animations and transitions
- Status indicators for different states

**Voice Control**
- Continuous hands-free listening
- Wake word detection ("Hey AURA")
- TTS manager for voice responses
- Speech recognition integration

**System Integration**
- Windows system utilities (brightness, volume, etc.)
- Application launching and control
- File operations
- Keyboard and mouse emulation

### 📦 Build System

**Created:**
- PyInstaller spec file with all dependencies
- Inno Setup installer configuration
- Build scripts (build_exe.bat, build_complete_installer.bat)
- Comprehensive build documentation

### 🧹 Codebase Cleanup

**Removed:**
- 14 redundant files (test files, duplicate docs, old launchers)
- Duplicate fix summary documentation (5 files)
- Old batch launchers (3 files)
- Test files (a.py, cars.pptx, etc.)

**Organized:**
- Created Scripts/ folder for batch files
- Created Installer/ folder for build files
- Created Docs/ folder for documentation
- Consolidated documentation into CHANGELOG.md

### 📚 Documentation

**Created:**
- README.md - Main project documentation
- AURA_V2_README.md - Technical documentation
- BUILD_INSTALLER_GUIDE.md - Complete build guide
- WIZARD_INSTALLATION.md - User installation guide
- INSTALLER_README.md - Quick start
- CHANGELOG.md - This file

### 🔧 Technical Details

**Dependencies:**
- PyQt5 - GUI framework
- keyring - Secure credential storage
- requests - API communication
- google-generativeai - Gemini integration
- openai - OpenAI integration
- pyttsx3 - Text-to-speech
- SpeechRecognition - Voice input
- PyInstaller - Executable bundling
- Inno Setup - Installer creation

**Structure:**
```
E:\agent\
├── Core Python Files (35 modules)
├── Scripts/ (8 batch files)
├── Installer/ (3 build files + icon)
├── Docs/ (5 documentation files)
├── aura_floating_widget/ (Main app)
├── README.md
├── requirements.txt
└── .env
```

---

## Previous Work

### Paint Automation Fix
- Fixed Paint application launching
- Improved app path resolution
- Better error handling

### Voice Dependencies
- Added TTS manager
- Improved voice output quality
- Fixed pyttsx3 integration

### AURA v2 Integration
- Intelligent local/LLM routing
- Wake word detection
- Hands-free continuous listening

---

## Coming Soon

### Future Enhancements
- Microsoft Store distribution (MSIX packaging)
- Auto-update functionality
- Plugin system for extensions
- Cloud sync for settings
- Multi-language support

---

**AURA is now ready for professional distribution!** 🚀
