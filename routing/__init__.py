# Routing module - Layer 1 Fast Path
from .intent_router import get_intent_router, classify_command, RouteResult
from .function_executor import get_function_executor, ExecutionResult
