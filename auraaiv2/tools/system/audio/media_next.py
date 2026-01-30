"""Tool: system.audio.media_next - Delegates to root utils.windows_system (SINGLE OS BOUNDARY)."""

from typing import Dict, Any
from ...base import Tool

try:
    from .._root_bridge import wsu
    _WSU = wsu
except ImportError:
    _WSU = None


class MediaNext(Tool):
    """Next track via root windows_system only."""

    @property
    def name(self) -> str:
        return "system.audio.media_next"

    @property
    def description(self) -> str:
        return "Skip to next track"

    @property
    def risk_level(self) -> str:
        return "low"

    @property
    def side_effects(self) -> list[str]:
        return ["media_state_changed"]

    @property
    def stabilization_time_ms(self) -> int:
        return 50

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
        ok = _WSU.media_control("next")
        return {"status": "success" if ok else "error", "action": "media_next"}
