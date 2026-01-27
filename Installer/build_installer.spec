# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller Build Configuration for AURA Floating Widget
Creates a standalone Windows executable with all dependencies bundled
"""

import sys
import os

block_cipher = None

# Find Python DLL location and explicitly include it
# This ensures the Python DLL is bundled even if PyInstaller doesn't detect it automatically
python_dll_name = f'python{sys.version_info.major}{sys.version_info.minor}.dll'
python_dll_path = os.path.join(os.path.dirname(sys.executable), python_dll_name)

# Prepare binaries list - explicitly include Python DLL if it exists
binaries_list = []
if os.path.exists(python_dll_path):
    binaries_list.append((python_dll_path, '.'))
    print(f"INFO: Explicitly including Python DLL: {python_dll_path}")
else:
    print(f"WARNING: Python DLL not found at: {python_dll_path}")

# All Python files that need to be included
# NOTE:
# This .spec file lives in the "Installer" subfolder, while the main
# widget entry-point lives in the top-level "aura_floating_widget" folder.
# Use a relative path from this "Installer" directory to the script.
a = Analysis(
    ['..\\aura_floating_widget\\aura_widget.py'],
    pathex=['e:\\agent'],
    binaries=binaries_list,
    datas=[
        # API key helper for credential management
        ('..\\api_key_helper.py', '.'),
    ],
    hiddenimports=[
        # Core AURA modules
        'api_key_helper',
        'aura_v2_bridge',
        'wake_word_detector',
        'ai_client',
        'code_executor',
        'capability_manager',
        'self_improvement',
        'windows_system_utils',
        'tts_manager',
        'voice_input',
        'voice_interface',
        'intent_router',
        'function_executor',
        'response_generator',
        'local_context',
        'credit_manager',
        
        # PyQt5 modules
        'PyQt5.QtCore',
        'PyQt5.QtGui',
        'PyQt5.QtWidgets',
        
        # API providers
        'requests',
        'google.generativeai',
        'google.ai.generativelanguage',
        'openai',
        
        # Voice/Speech
        'pyttsx3',
        'pyttsx3.drivers',
        'pyttsx3.drivers.sapi5',
        'speech_recognition',
        
        # System utilities
        'keyring',
        'keyring.backends',
        'keyring.backends.Windows',
        
        # Other dependencies
        'json',
        'pathlib',
        'threading',
        'queue',
        'datetime',
        'math',
        'random',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AURA',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window - GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    # Icon path is relative to this "Installer" directory
    icon='jarvis_icon.ico',  # Use AURA icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AURA',
)
