"""
SINGLE OS BOUNDARY - Delegate to root utils.windows_system only.
All auraaiv2 system tools MUST use this; no direct Windows/pycaw/ctypes here.
"""
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent.parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

try:
    from utils import windows_system as wsu
    from utils import advanced_control as ac
    WSU_AVAILABLE = True
    AC_AVAILABLE = True
except ImportError:
    wsu = None
    ac = None
    WSU_AVAILABLE = False
    AC_AVAILABLE = False
