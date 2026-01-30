"""
Verify Fast Path integrity: ToolExecutor load time and execution latency.

KEEP THIS SCRIPT FOREVER.
- On any change to routing, executor, or tools: run this script.
- Compare latency before/after; ensure fast path stays fast.
- Most systems lose performance silently. Yours won't.

Run from repo root: python Scripts/verify_fast_path.py
"""
import time
import sys
import logging
from pathlib import Path

# Repo root (parent of Scripts)
_repo_root = Path(__file__).resolve().parent.parent
if str(_repo_root) not in sys.path:
    sys.path.insert(0, str(_repo_root))
if str(_repo_root / "auraaiv2") not in sys.path:
    sys.path.insert(0, str(_repo_root / "auraaiv2"))

try:
    import config.config
    print("DEBUG: config.config imported successfully")
    print("DEBUG: config object:", config.config.config)
except ImportError as e:
    print(f"DEBUG: Failed to import config.config: {e}")

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')


def verify_fast_path():
    print("--- Verifying Fast Path Integrity ---")

    t0 = time.time()
    from auraaiv2.execution.executor import ToolExecutor
    t_import = (time.time() - t0) * 1000
    print(f"Import ToolExecutor: {t_import:.2f} ms")

    heavy_modules = ['learning.self_improvement', 'ai.client', 'google.generativeai']
    for mod in heavy_modules:
        if mod in sys.modules:
            print(f"WARNING: {mod} is loaded!")
        else:
            print(f"Success: {mod} is NOT loaded.")

    t0 = time.time()
    executor = ToolExecutor()
    t_init = (time.time() - t0) * 1000
    print(f"Init ToolExecutor: {t_init:.2f} ms")

    import auraaiv2.tools.outside_bridge

    t0 = time.time()
    result = executor.execute_step("get_current_time", {})
    t_exec = (time.time() - t0) * 1000

    print(f"Execute 'get_current_time': {t_exec:.2f} ms")
    print(f"Result: {result}")

    if t_exec > 100:
        print("FAILURE: Execution took > 100ms")
    else:
        print("SUCCESS: Execution < 100ms")

    t0 = time.time()
    result = executor.execute_step("get_system_volume", {})
    t_exec_vol = (time.time() - t0) * 1000
    print(f"Execute 'get_system_volume': {t_exec_vol:.2f} ms")

    if t_exec_vol > 100:
        print("FAILURE: Volume Execution took > 100ms")
    else:
        print("SUCCESS: Volume Execution < 100ms")


if __name__ == "__main__":
    verify_fast_path()
