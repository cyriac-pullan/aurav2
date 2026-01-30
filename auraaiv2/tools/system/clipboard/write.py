"""Tool: system.clipboard.write - Delegates to root utils.advanced_control (SINGLE OS BOUNDARY)."""

from typing import Dict, Any
from ...base import Tool

try:
    from .._root_bridge import ac
    _AC = ac
except ImportError:
    _AC = None


class WriteClipboard(Tool):
    """Write clipboard via root advanced_control only."""

    @property
    def name(self) -> str:
        return "system.clipboard.write"

    @property
    def description(self) -> str:
        return "Writes text content to the system clipboard"

    @property
    def risk_level(self) -> str:
        return "low"

    @property
    def side_effects(self) -> list[str]:
        return ["clipboard_modified"]

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
        return {
            "type": "object",
            "properties": {"text": {"type": "string", "description": "Text to copy to clipboard"}},
            "required": ["text"]
        }

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self.validate_args(args):
            raise ValueError(f"Invalid arguments for {self.name}")
        if not _AC:
            return {"status": "error", "error": "Root advanced_control not available"}
        text = args.get("text")
        if text is None:
            return {"status": "error", "error": "Required argument 'text' not provided"}
        if not isinstance(text, str):
            text = str(text)
        try:
            ok = _AC.copy_to_clipboard(text)
            return {"status": "success" if ok else "error"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
