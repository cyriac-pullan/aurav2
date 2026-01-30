"""
Outside Bridge - Allows V2 ToolExecutor to access root windows_system_utils functions.

This bridge creates V2-compatible Tool wrappers around the powerful functions
in the root `windows_system_utils.py`, making them available to the Agentic planner.
"""

import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add root to path to import outside modules
root_path = Path(__file__).parent.parent.parent
if str(root_path) not in sys.path:
    sys.path.insert(0, str(root_path))

from tools.base import Tool
from tools.registry import get_registry

# Import root utilities
try:
    from utils import windows_system as wsu
    WSU_AVAILABLE = True
except ImportError as e:
    logging.error(f"Could not import windows_system_utils: {e}")
    WSU_AVAILABLE = False

try:
    from utils import advanced_control as ac
    AC_AVAILABLE = True
except ImportError as e:
    logging.error(f"Could not import advanced_control: {e}")
    AC_AVAILABLE = False

# Import Code Executor
try:
    from ai.code_executor import executor as code_executor
    CODE_EXEC_AVAILABLE = True
except ImportError as e:
    logging.error(f"Could not import ai.code_executor: {e}")
    CODE_EXEC_AVAILABLE = False

try:
    from features import app_creator
    APP_CREATOR_AVAILABLE = True
except ImportError as e:
    logging.error(f"Could not import features.app_creator: {e}")
    APP_CREATOR_AVAILABLE = False

try:
    from features import email_assistant
    EMAIL_AVAILABLE = True
except ImportError as e:
    logging.error(f"Could not import features.email_assistant: {e}")
    EMAIL_AVAILABLE = False



class OutsideFunctionTool(Tool):
    """Generic wrapper to expose a windows_system_utils function as a V2 Tool."""
    
    def __init__(self, func_name: str, description: str, schema: Dict[str, Any], 
                 risk_level: str = "medium", requires_focus: bool = False, 
                 requires_unlocked_screen: bool = True, source_module: Any = None):
        self._name = func_name
        self._description = description
        self._schema = schema
        self._risk_level = risk_level
        self._requires_focus = requires_focus
        self._requires_unlocked_screen = requires_unlocked_screen
        self._func = getattr(source_module, func_name, None) if source_module else None
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def description(self) -> str:
        return self._description
    
    @property
    def schema(self) -> Dict[str, Any]:
        return self._schema
    
    @property
    def risk_level(self) -> str:
        return self._risk_level
    
    @property
    def requires_focus(self) -> bool:
        return self._requires_focus

    @property
    def requires_unlocked_screen(self) -> bool:
        return self._requires_unlocked_screen

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not self._func:
            return {"status": "error", "error": f"Function {self._name} not available"}
        try:
            result = self._func(**args)
            # Normalize result to V2 format
            if isinstance(result, bool):
                return {"status": "success" if result else "error"}
            elif isinstance(result, tuple) and len(result) == 2:
                return {"status": "success" if result[0] else "error", "message": str(result[1])}
            elif isinstance(result, dict):
                return result
            else:
                return {"status": "success", "result": result}
        except Exception as e:
            logging.error(f"OutsideFunctionTool.execute error for {self._name}: {e}")
            return {"status": "error", "error": str(e)}


class RunPythonTool(Tool):
    """Executes Python code safely using the AI code executor environment."""

    @property
    def name(self) -> str:
        return "run_python"

    @property
    def description(self) -> str:
        return "Execute Python code in a safe environment. Use this for calculations, data processing, or creating apps."

    @property
    def schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Valid Python code to execute"
                }
            },
            "required": ["code"]
        }

    @property
    def risk_level(self) -> str:
        return "high"  # Creating code is high risk

    def execute(self, args: Dict[str, Any]) -> Dict[str, Any]:
        if not CODE_EXEC_AVAILABLE:
            return {"status": "error", "error": "Code executor not available"}
        
        code = args.get("code", "")
        if not code:
            return {"status": "error", "error": "No code provided"}

        success, output, result = code_executor.execute(code)
        
        if success:
            return {
                "status": "success",
                "output": output,
                "result": str(result)
            }
        else:
            return {
                "status": "error",
                "error": output  # output contains error message in failure case
            }


def register_outside_tools():
    """Registers key functions from windows_system_utils and advanced_control as V2 tools."""
    registry = get_registry()
    
    # 1. Register Code Executor
    if CODE_EXEC_AVAILABLE:
        try:
            if not registry.has("run_python"):
                registry.register(RunPythonTool())
                logging.info("Registered tool: run_python")
        except Exception as e:
            logging.warning(f"Could not register run_python: {e}")

    # 2. Register System Tools (utils/windows_system.py)
    if WSU_AVAILABLE:
        # Format: (name, desc, props, risk, requires_unlocked)
        wsu_tools = [
            ("set_system_volume", "Set system volume (0-100).", {"level": "integer"}, "low", False),
            ("get_system_volume", "Get system volume.", {}, "low", False),
            ("mute_system_volume", "Mute system volume.", {}, "low", False),
            ("unmute_system_volume", "Unmute system volume.", {}, "low", False),
            ("adjust_system_volume", "Adjust system volume relatively.", {"change": "integer"}, "low", False),
            ("open_application", "Open app by name.", {"app_name": "string"}, "low", True),
            ("close_application", "Close app by name.", {"app_name": "string"}, "medium", True),
            ("get_current_time", "Get current time/date.", {}, "low", False),
            ("take_screenshot", "Take screenshot to file.", {"path": "string"}, "low", False),
            ("lock_computer", "Lock screen.", {}, "medium", False),
            ("open_website", "Open URL.", {"url": "string"}, "low", True),
            ("google_search", "Search Google.", {"query": "string"}, "low", True),
            ("play_youtube", "Open YouTube.", {"query": "string"}, "low", True),
            ("play_spotify", "Open Spotify.", {"query": "string"}, "low", True),
            ("media_control", "Media keys.", {"action": "string"}, "low", False),
            ("create_file", "Create file.", {"file_name": "string", "content": "string", "location": "string"}, "medium", True),
            ("open_calculator", "Open calculator.", {}, "low", True),
            ("open_file_explorer", "Open File Explorer.", {"path": "string"}, "low", True),
            ("toggle_night_light", "Toggle Night Light.", {"enable": "boolean"}, "low", False),
            ("empty_recycle_bin", "Empty Recycle Bin.", {}, "medium", True),
            ("set_brightness", "Set screen brightness (0-100).", {"level": "integer"}, "low", False),
            ("adjust_brightness", "Adjust brightness by relative amount.", {"change": "integer"}, "low", False),
        ]

        for name, desc, props, risk, unlocked in wsu_tools:
            # Construct schema
            schema = {"type": "object", "properties": {k: {"type": v} for k, v in props.items()}}
            if props:
                schema["required"] = list(props.keys())
            
            tool = OutsideFunctionTool(
                name, desc, schema, 
                risk_level=risk, 
                source_module=wsu,
                requires_unlocked_screen=unlocked
            )
            if not registry.has(tool.name):
                registry.register(tool)

    # 3. Register Advanced Control Tools (utils/advanced_control.py)
    if AC_AVAILABLE:
        ac_tools = [
            ("run_terminal_command", "Run shell command.", {"command": "string", "timeout": "integer"}, "high"),
            ("open_terminal", "Open terminal window.", {}, "low"),
            ("type_text", "Type text via keyboard.", {"text": "string"}, "low"),
            ("press_key", "Press a key.", {"key": "string"}, "low"),
            ("hotkey", "Press key combo.", {"keys": "string"}, "low"), # keys="ctrl+c"
            ("mouse_click", "Click mouse.", {"x": "integer", "y": "integer", "button": "string"}, "low"),
            ("scroll", "Scroll mouse.", {"clicks": "integer"}, "low"),
            ("copy_to_clipboard", "Copy text.", {"text": "string"}, "low"),
            ("get_clipboard", "Get clipboard text.", {}, "low"),
        ]

        for name, desc, props, risk in ac_tools:
            schema = {"type": "object", "properties": {k: {"type": v} for k, v in props.items()}}
            # hotkey args need to be handled carefully in execute if signature is *keys
            # OutsideFunctionTool passes **args, so we need to ensure local function accepts them
            # advanced_control.hotkey is def hotkey(*keys). **{"keys": "a,b"} -> fails.
            # We need a wrapper for hotkey in advanced_control or specific handling here.
            # Since advanced_control.hotkey takes *keys, we can't simply pass keys="ctrl+c".
            # However, looking at advanced_control.py, I can wrap it or it accepts multiple args.
            # Let's check advanced_control.hotkey signature again. def hotkey(*keys).
            # The function_executor mapped "ctrl+c" string to splitted args.
            
            # I will create a special wrapper for hotkey in OutsideFunctionTool if name == "hotkey"
            # Or simplified: create a "custom_hotkey" function in outside_bridge and register that.
            
            tool = OutsideFunctionTool(name, desc, schema, risk_level=risk, source_module=ac)
            if name == "hotkey":
                # Override execute for hotkey to split string
                def custom_execute(self, args):
                    keys_str = args.get("keys", "")
                    keys = [k.strip() for k in keys_str.replace("+", " ").split()]
                    return self._func(*keys)
                import types
                tool.execute = types.MethodType(custom_execute, tool)

            if not registry.has(tool.name):
                registry.register(tool)

    # 4. Register Feature Tools
    if APP_CREATOR_AVAILABLE:
        # Wrapper for create_app
        # features/app_creator.py: create_app(description, app_name) -> (bool, msg, path)
        class AppCreatorTool(Tool):
            @property
            def name(self): return "create_agentic_app"
            @property
            def description(self): return "Create a python app from description."
            @property
            def schema(self): return {"type": "object", "properties": {"description": {"type": "string"}}, "required": ["description"]}
            @property
            def risk_level(self): return "high"
            def execute(self, args):
                creator = app_creator.AgenticAppCreator()
                success, msg, path = creator.create_app(args["description"])
                return {"status": "success" if success else "error", "message": msg, "path": path}
        
        registry.register(AppCreatorTool())

    if EMAIL_AVAILABLE:
        # features/email_assistant.py: draft_email(instruction, recipient...)
        class EmailDraftTool(Tool):
            @property
            def name(self): return "draft_email_agent" # distinct from intent name
            @property
            def description(self): return "Draft an email."
            @property
            def schema(self): return {"type": "object", "properties": {"instruction": {"type": "string"}, "recipient": {"type": "string"}}, "required": ["instruction"]}
            @property
            def risk_level(self): return "medium"
            def execute(self, args):
                success, msg = email_assistant.draft_email(args["instruction"], args.get("recipient", ""), action="clipboard")
                return {"status": "success" if success else "error", "message": msg}
        
        registry.register(EmailDraftTool())
    
    logging.info("Outside tools registration complete.")

# Auto-register when this module is imported
register_outside_tools()
