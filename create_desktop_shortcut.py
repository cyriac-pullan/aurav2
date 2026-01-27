"""
Create Desktop Shortcut for AURA Floating Widget
"""

import os
import sys
from pathlib import Path
import winshell
from win32com.client import Dispatch

def create_shortcut():
    """Create a desktop shortcut for AURA"""
    try:
        # Get paths
        desktop = Path(winshell.desktop())
        script_dir = Path(__file__).parent.absolute()
        
        # Python executable in venv
        python_exe = script_dir / "venv" / "Scripts" / "pythonw.exe"
        if not python_exe.exists():
            python_exe = script_dir / "venv" / "Scripts" / "python.exe"
        
        # Target script
        widget_script = script_dir / "aura_floating_widget" / "aura_widget.py"
        
        # Shortcut path
        shortcut_path = desktop / "AURA Assistant.lnk"
        
        # Create shortcut
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.TargetPath = str(python_exe)
        shortcut.Arguments = f'"{widget_script}"'
        shortcut.WorkingDirectory = str(script_dir)
        shortcut.IconLocation = str(python_exe)
        shortcut.Description = "AURA - AI Voice Assistant"
        shortcut.save()
        
        print(f"✅ Desktop shortcut created: {shortcut_path}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to create shortcut: {e}")
        print(f"   You can manually run: {script_dir}\\run_widget.bat")
        return False

if __name__ == "__main__":
    # Try to install winshell if not available
    try:
        import winshell
    except ImportError:
        print("Installing winshell...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "winshell", "pywin32"], 
                      capture_output=True)
        import winshell
    
    create_shortcut()
