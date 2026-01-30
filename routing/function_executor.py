"""
Local Intent Resolver + Function Executor (Bridge compatibility).

- LocalIntentResolver: Maps local intents to V2 tool names (used by HybridOrchestrator).
- FunctionExecutor / ExecutionResult: Used by ui.bridge for _execute_local and _handle_gemini.
  Delegates to V2 ToolExecutor and ai.code_executor so there is a single execution path.
"""

from typing import Dict, Any, Tuple, Optional
import logging
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    """Result of executing a function or raw code (used by ui.bridge)."""
    success: bool
    result: Any = None


@dataclass
class ResolvedIntent:
    tool_name: str
    tool_args: Dict[str, Any]
    confidence: float = 1.0


class LocalIntentResolver:
    """
    Resolver for Layer 1 (Local Reflex) intents.
    Maps high-speed intents to standard V2 Tools.
    """
    
    def __init__(self):
        self.mappings = self._initialize_mappings()

    def _initialize_mappings(self) -> Dict[str, str]:
        """Maps intent names to tool names directly where 1:1."""
        return {
            "set_volume": "set_system_volume",
            "mute_volume": "mute_system_volume",
            "unmute_volume": "unmute_system_volume",
            "get_volume": "get_system_volume",
            
            "set_brightness": "set_brightness",
            # increase/decrease handled dynamically
            
            "open_application": "open_application",
            "close_application": "close_application",
            
            "google_search": "google_search",
            "play_youtube": "play_youtube",
            "play_spotify": "play_spotify",
            
            "run_terminal_command": "run_terminal_command",
            "type_text": "type_text",
            "press_key": "press_key",
            
            "create_file": "create_file",
            "take_screenshot": "take_screenshot",
            "lock_computer": "lock_computer",
            "empty_recycle_bin": "empty_recycle_bin",
            
            "toggle_night_light": "toggle_night_light",
            
            "create_app": "create_agentic_app",
            "send_email": "draft_email_agent"
        }

    def resolve(self, intent_name: str, args: Dict[str, Any]) -> Optional[ResolvedIntent]:
        """
        Resolves an intent into a V2 Tool execution plan.
        
        Args:
            intent_name: The classified intent (e.g. "increase_volume")
            args: Extracted entities/arguments
            
        Returns:
            ResolvedIntent or None if no mapping exists.
        """
        if not args:
            args = {}
            
        # 1. Handle dynamic mappings (logic transformations)
        if intent_name == "increase_volume":
            change = args.get("change", 10) # Default +10
            return ResolvedIntent("adjust_system_volume", {"change": int(change)})
            
        if intent_name == "decrease_volume":
            change = args.get("change", 10)
            return ResolvedIntent("adjust_system_volume", {"change": -int(change)})
            
        if intent_name == "increase_brightness":
            change = args.get("change", 10)
            return ResolvedIntent("adjust_brightness", {"change": int(change)})
            
        if intent_name == "decrease_brightness":
            change = args.get("change", 10)
            return ResolvedIntent("adjust_brightness", {"change": -int(change)})

        if intent_name == "play_media":
            return ResolvedIntent("media_control", {"action": "play_pause"})
        
        if intent_name == "next_track":
            return ResolvedIntent("media_control", {"action": "next"})
            
        if intent_name == "previous_track":
            return ResolvedIntent("media_control", {"action": "previous"})

        if intent_name == "click_mouse":
             # Args might be x, y or empty (click current)
             return ResolvedIntent("mouse_click", args)

        if intent_name == "scroll_up":
             return ResolvedIntent("scroll", {"clicks": 200})
        
        if intent_name == "scroll_down":
             return ResolvedIntent("scroll", {"clicks": -200})
             
        # 2. Handle 1:1 mappings
        tool_name = self.mappings.get(intent_name)
        if tool_name:
            return ResolvedIntent(tool_name, args)
            
        # 3. No match
        logging.warning(f"LocalIntentResolver: No mapping for intent '{intent_name}'")
        return None

def get_intent_resolver():
    return LocalIntentResolver()


# ---------------------------------------------------------------------------
# FunctionExecutor - Bridge compatibility (delegates to V2 + code_executor)
# ---------------------------------------------------------------------------

class FunctionExecutor:
    """
    Executor used by ui.bridge for local and Gemini fallback execution.
    Delegates to V2 ToolExecutor (intent -> tool) and ai.code_executor (raw code).
    """

    def __init__(self):
        self._resolver = LocalIntentResolver()
        self._v2_executor = None
        self._v2_path = Path(__file__).resolve().parent.parent / "auraaiv2"

    @property
    def v2_executor(self):
        """Lazy-load V2 ToolExecutor."""
        if self._v2_executor is None:
            if str(self._v2_path) not in sys.path:
                sys.path.insert(0, str(self._v2_path))
            try:
                from auraaiv2.execution.executor import ToolExecutor
                import auraaiv2.tools.outside_bridge
                auraaiv2.tools.outside_bridge.register_outside_tools()
                self._v2_executor = ToolExecutor()
            except Exception as e:
                logging.error(f"FunctionExecutor: could not load V2 executor: {e}")
        return self._v2_executor

    def execute(self, function_name: str, args: Dict[str, Any]) -> ExecutionResult:
        """Execute a local function by name (resolves to V2 tool and runs it)."""
        resolved = self._resolver.resolve(function_name, args or {})
        if not resolved:
            return ExecutionResult(False, None)
        ex = self.v2_executor
        if not ex:
            return ExecutionResult(False, None)
        try:
            out = ex.execute_step(resolved.tool_name, resolved.tool_args)
            ok = out.get("status") == "success"
            return ExecutionResult(ok, out.get("result") or out.get("message") or out.get("output"))
        except Exception as e:
            logging.error(f"FunctionExecutor.execute error: {e}")
            return ExecutionResult(False, str(e))

    def execute_raw(self, code: str) -> ExecutionResult:
        """Execute raw Python code via ai.code_executor."""
        try:
            from ai.code_executor import executor as code_executor
            success, output, result = code_executor.execute(code)
            return ExecutionResult(success, output if output else result)
        except Exception as e:
            logging.error(f"FunctionExecutor.execute_raw error: {e}")
            return ExecutionResult(False, str(e))


_function_executor_instance = None


def get_function_executor() -> FunctionExecutor:
    """Return singleton FunctionExecutor for bridge compatibility."""
    global _function_executor_instance
    if _function_executor_instance is None:
        _function_executor_instance = FunctionExecutor()
    return _function_executor_instance
