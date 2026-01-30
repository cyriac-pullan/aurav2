"""System tools - OS-level operations.

SINGLE OS BOUNDARY: All system tools that duplicate root behavior MUST delegate
to root utils.windows_system or utils.advanced_control via _root_bridge.
No direct Windows/pycaw/ctypes in this package; see _root_bridge.py.
"""

