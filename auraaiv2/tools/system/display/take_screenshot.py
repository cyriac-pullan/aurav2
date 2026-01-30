"""Tool: system.display.take_screenshot - Delegates to root utils.windows_system (SINGLE OS BOUNDARY)."""

from typing import Dict, Any
from ...base import Tool

try:
    from .._root_bridge import wsu
    _WSU = wsu
except ImportError:
    _WSU = None


class TakeScreenshot(Tool):
    """Take screenshot via root windows_system only (saves to desktop)."""

    @property
    def name(self) -> str:
        return "system.display.take_screenshot"

    @property
    def description(self) -> str:
        return "Takes a screenshot and saves it to the desktop"

    @property
    def risk_level(self) -> str:
        return "low"

    @property
    def side_effects(self) -> list[str]:
        return ["file_created"]

    @property
    def stabilization_time_ms(self) -> int:
        return 100

    @property
    def reversible(self) -> bool:
        return True

    @property
    def requires_visual_confirmation(self) -> bool:
        return False

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "save_location": {"type": "string", "description": "Ignored; root saves to desktop"},
                "custom_path": {"type": "string", "description": "Ignored"}
            },
            "required": []
        }

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_args(args):
            raise ValueError(f"Invalid arguments for {self.name}")
        if not _WSU:
            return {"status": "error", "error": "Root windows_system not available"}
        ok = _WSU.take_screenshot()
        return {"status": "success" if ok else "error", "path": "desktop"}
