"""Tool: system.audio.get_volume - Delegates to root utils.windows_system (SINGLE OS BOUNDARY)."""

from typing import Dict, Any
from ...base import Tool

try:
    from .._root_bridge import wsu
    _WSU = wsu
except ImportError:
    _WSU = None


class GetVolume(Tool):
    """Get current system volume via root windows_system only."""

    @property
    def name(self) -> str:
        return "system.audio.get_volume"

    @property
    def description(self) -> str:
        return "Returns the current system volume level (0-100)"

    @property
    def risk_level(self) -> str:
        return "none"

    @property
    def side_effects(self) -> list[str]:
        return []

    @property
    def stabilization_time_ms(self) -> int:
        return 0

    @property
    def reversible(self) -> bool:
        return True

    @property
    def requires_visual_confirmation(self) -> bool:
        return False

    @property
    def requires_focus(self) -> bool:
        return False

    @property
    def requires_unlocked_screen(self) -> bool:
        return False

    @property
    def schema(self) -> Dict[str, Any]:
        return {"type": "object", "properties": {}, "required": []}

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_args(args):
            raise ValueError(f"Invalid arguments for {self.name}")
        if not _WSU:
            return {"status": "error", "error": "Root windows_system not available"}
        try:
            level = _WSU.get_current_volume()
            return {"status": "success", "volume": level}
        except Exception as e:
            return {"status": "error", "error": str(e)}
