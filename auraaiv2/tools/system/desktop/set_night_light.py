"""Tool: system.desktop.set_night_light - Delegates to root utils.windows_system (SINGLE OS BOUNDARY)."""

from typing import Dict, Any
from ...base import Tool

try:
    from .._root_bridge import wsu
    _WSU = wsu
except ImportError:
    _WSU = None


class SetNightLight(Tool):
    """Set Night Light via root windows_system only."""

    @property
    def name(self) -> str:
        return "system.desktop.set_night_light"

    @property
    def description(self) -> str:
        return "Enables or disables Windows Night Light (blue light filter)"

    @property
    def risk_level(self) -> str:
        return "low"

    @property
    def side_effects(self) -> list[str]:
        return ["display_state_changed"]

    @property
    def stabilization_time_ms(self) -> int:
        return 300

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
        return True

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {"enabled": {"type": "boolean", "description": "True to enable, False to disable"}},
            "required": ["enabled"]
        }

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_args(args):
            raise ValueError(f"Invalid arguments for {self.name}")
        if not _WSU:
            return {"status": "error", "error": "Root windows_system not available"}
        enabled = args.get("enabled")
        if enabled is None:
            return {"status": "error", "error": "Required argument 'enabled' not provided"}
        ok = _WSU.toggle_night_light(enable=enabled)
        return {"status": "success" if ok else "error", "enabled": enabled}
