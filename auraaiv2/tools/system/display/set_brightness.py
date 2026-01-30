"""Tool: system.display.set_brightness - Delegates to root utils.windows_system (SINGLE OS BOUNDARY)."""

import logging
from typing import Dict, Any
from ...base import Tool

try:
    from .._root_bridge import wsu
    _WSU = wsu
except ImportError:
    _WSU = None


class SetBrightness(Tool):
    """Set display brightness via root windows_system only."""

    @property
    def name(self) -> str:
        return "system.display.set_brightness"

    @property
    def description(self) -> str:
        return "Sets the display brightness to a specific level (0-100)"

    @property
    def risk_level(self) -> str:
        return "low"

    @property
    def side_effects(self) -> list[str]:
        return ["display_brightness_changed"]

    @property
    def stabilization_time_ms(self) -> int:
        return 100

    @property
    def reversible(self) -> bool:
        return True

    @property
    def requires_visual_confirmation(self) -> bool:
        return True

    @property
    def requires_focus(self) -> bool:
        return False

    @property
    def requires_unlocked_screen(self) -> bool:
        return False

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {"level": {"type": "integer", "minimum": 0, "maximum": 100, "description": "Brightness level (0-100)"}},
            "required": ["level"]
        }

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_args(args):
            raise ValueError(f"Invalid arguments for {self.name}")
        if not _WSU:
            return {"status": "error", "error": "Root windows_system not available"}
        level = args.get("level")
        if level is None or not 0 <= level <= 100:
            return {"status": "error", "error": "level must be 0-100"}
        ok = _WSU.set_brightness(level)
        return {"status": "success" if ok else "error", "level": level}
