"""Tool: system.clipboard.read - Delegates to root utils.advanced_control (SINGLE OS BOUNDARY)."""

from typing import Dict, Any
from ...base import Tool

try:
    from .._root_bridge import ac
    _AC = ac
except ImportError:
    _AC = None


class ReadClipboard(Tool):
    """Read clipboard via root advanced_control only."""

    @property
    def name(self) -> str:
        return "system.clipboard.read"

    @property
    def description(self) -> str:
        return "Reads text content from the system clipboard"

    @property
    def risk_level(self) -> str:
        return "low"

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
        if not _AC:
            return {"status": "error", "error": "Root advanced_control not available"}
        try:
            content = _AC.get_clipboard()
            return {"status": "success", "content": content, "length": len(content)}
        except Exception as e:
            return {"status": "error", "error": str(e)}
