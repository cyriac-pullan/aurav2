"""Tool: system.desktop.empty_recycle_bin - Delegates to root after confirm gate (SINGLE OS BOUNDARY)."""

import logging
from typing import Dict, Any
from ...base import Tool

try:
    from .._root_bridge import wsu
    _WSU = wsu
except ImportError:
    _WSU = None


class EmptyRecycleBin(Tool):
    """Empty Recycle Bin via root windows_system. REQUIRES confirm=true."""

    @property
    def name(self) -> str:
        return "system.desktop.empty_recycle_bin"

    @property
    def description(self) -> str:
        return "Permanently deletes all files in the Recycle Bin. REQUIRES confirm=true."

    @property
    def risk_level(self) -> str:
        return "high"

    @property
    def side_effects(self) -> list[str]:
        return ["permanent_data_loss", "recycle_bin_emptied"]

    @property
    def stabilization_time_ms(self) -> int:
        return 500

    @property
    def reversible(self) -> bool:
        return False

    @property
    def requires_visual_confirmation(self) -> bool:
        return False

    @property
    def requires_focus(self) -> bool:
        return False

    @property
    def requires_unlocked_screen(self) -> bool:
        return True

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {"confirm": {"type": "boolean", "description": "Must be true to execute. Safety gate."}},
            "required": ["confirm"]
        }

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if args.get("confirm") is not True:
            logging.warning("Empty recycle bin BLOCKED - confirm not True")
            return {"status": "refused", "error": "SAFETY GATE: Requires confirm=true.", "required": {"confirm": True}}
        if not _WSU:
            return {"status": "error", "error": "Root windows_system not available"}
        ok = _WSU.empty_recycle_bin()
        return {"status": "success" if ok else "error", "action": "empty_recycle_bin"}
