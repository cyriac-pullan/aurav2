"""
AURA Hybrid Orchestrator
Location: core/hybrid_orchestrator.py

# =============================================================================
# SINGLE DECISION MAKER
# Routing decisions MUST NOT be duplicated elsewhere.
# =============================================================================

The 'Unified Brain' contract:
1. Local Reflexes First (0 token, regex/keyword)
2. Agentic Reasoning Second (V2 Decomposition/Planning)
3. Safe Execution + Healing (V2 Guards + Outside Improvement Engine)
"""

import logging
from typing import Dict, Any, Tuple, Optional

# Layer 1 Components (Routing)
from routing.intent_router import get_intent_router
from routing.function_executor import get_intent_resolver
from ui.response_generator import get_response_generator
from core.context import get_context

# Layer 2 Components (V2) - Lazy load to avoid circularity or bloat
import sys
from pathlib import Path

# Layer 3/Learning
from learning.self_improvement import improvement_engine
from learning.capability_manager import capability_manager

# Gemini Client for Fallback
try:
    from ai.client import ai_client
    AI_CLIENT_AVAILABLE = True
except ImportError:
    AI_CLIENT_AVAILABLE = False
    ai_client = None


class HybridOrchestrator:
    """
    Core brain orchestrating the transition from reflex to reasoning.
    
    Flow:
    1. Layer 1 (Local): High-confidence regex/keyword matches (0 tokens)
    2. Layer 1.5 (Gemini Fallback): Low-confidence -> LLM code generation
    3. Layer 2 (Agentic): Complex multi-step tasks -> V2 Decomposition
    4. Layer 3 (Healing): Failure -> Self-Improvement Engine
    """
    
    def __init__(self):
        logging.info("Aura Hybrid Architecture: Initializing Unified Brain...")
        self.local_router = get_intent_router()
        self.intent_resolver = get_intent_resolver()
        self.response_gen = get_response_generator()
        self.context = get_context()
        self.capability_mgr = capability_manager
        
        # Layer 2: Agentic V2 (Lazy load)
        self._v2_brain = None
        self.v2_path = Path(__file__).parent.parent / "auraaiv2"
        
        # Stats
        self.stats = {
            "layer1_local": 0,
            "layer1_gemini_fallback": 0,
            "layer2_agentic": 0,
            "layer3_healing": 0,
            "skills_promoted": 0,
        }

    @property
    def v2_brain(self):
        """Lazy load the V2 Orchestrator only when needed."""
        if self._v2_brain is None:
            if str(self.v2_path) not in sys.path:
                sys.path.insert(0, str(self.v2_path))
            try:
                from core.orchestrator import Orchestrator
                self._v2_brain = Orchestrator()
                logging.info("Layer 2: Aura V2 Orchestrator loaded")
            except Exception as e:
                logging.error(f"Failed to load V2 Brain: {e}")
        return self._v2_brain

    def process(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> Tuple[str, bool, bool]:
        """
        Main entry point for command execution.
        Returns: (response_text, success, used_llm)
        """
        logging.info(f"Hybrid Brain: '{user_input[:50]}'")
        
        # =========================================================================
        # LAYER 1: LOCAL REFLEX (Outside) - 0 Tokens
        # =========================================================================
        local_result = self._handle_layer_1_local(user_input, context)
        if local_result:
            self.stats["layer1_local"] += 1
            return local_result[0], local_result[1], False
        
        # =========================================================================
        # LAYER 1.5: GEMINI FALLBACK (For low-confidence or no-match commands)
        # =========================================================================
        # If Layer 1 doesn't have a strong match, use Gemini to generate code.
        # This restores v1 behavior where ANY command can work.
        gemini_result = self._handle_layer_1_gemini_fallback(user_input, context)
        if gemini_result[1]:  # If successful
            self.stats["layer1_gemini_fallback"] += 1
            return gemini_result
            
        # =========================================================================
        # LAYER 2: AGENTIC REASONING (Aura V2) 
        # =========================================================================
        # Invoked if Layer 1 fails. For complex, multi-step tasks.
        logging.info("LAYER 2: Falling back to Agentic Reasoning")
        self.stats["layer2_agentic"] += 1
        v2_result = self._handle_layer_2_agentic(user_input, context)
        
        # =========================================================================
        # LAYER 3: SAFE EXECUTION + SELF-HEALING (Learning Loop)
        # =========================================================================
        return self._handle_layer_3_execution(v2_result, user_input, context)

    def _handle_layer_1_local(self, user_input: str, context: Optional[Dict[str, Any]]) -> Optional[Tuple[str, bool]]:
        """
        Attempts to route the command via regex/keyword mapping.
        Returns Tuple[response, success] if matched, else None.
        """
        try:
            route_result = self.local_router.classify(user_input, self.context)
            
            # Strict contract: Only execute if it's a high-confidence local match
            if route_result.match_type != "none" and route_result.confidence >= 0.85:
                logging.info(f"Layer 1 Match: {route_result.function} (conf={route_result.confidence:.2f})")
                
                # Resolve intent to V2 Tool Call
                resolved_plan = self.intent_resolver.resolve(
                    intent_name=route_result.function,
                    args=route_result.args
                )
                
                if resolved_plan:
                    logging.info(f"Resolved to Tool: {resolved_plan.tool_name}")
                    
                    # DELEGATE TO V2 EXECUTOR (The SSOT Executor)
                    exec_result = self.v2_brain.executor.execute_step(
                        tool_name=resolved_plan.tool_name,
                        args=resolved_plan.tool_args
                    )
                    
                    success = exec_result.get("status") == "success"
                    
                    # Track successful execution
                    self.capability_mgr.record_execution(
                        command=user_input,
                        success=success,
                        function_name=route_result.function
                    )
                    
                    # Generate simple confirmation
                    response = self.response_gen.confirmation(
                        result=success,
                        context={
                            "function": route_result.function,
                            "value": route_result.args.get("level"),
                            "app": route_result.args.get("app_name"),
                            "message": exec_result.get("message") or exec_result.get("error")
                        }
                    )
                    return response, success
                else:
                    logging.warning("Layer 1 matched but Resolver found no mapping. Falling back.")

        except Exception as e:
            logging.error(f"Layer 1 Error: {e}")
            
        return None

    def _handle_layer_1_gemini_fallback(self, user_input: str, context: Optional[Dict[str, Any]]) -> Tuple[str, bool, bool]:
        """
        Uses Gemini to generate and execute code for any command.
        This is the v1-like behavior for handling arbitrary commands.
        """
        if not AI_CLIENT_AVAILABLE or not ai_client:
            return self.response_gen.failure(), False, True
            
        try:
            code = ai_client.generate_code(user_input, context=context or {})
            if code:
                # DELEGATE TO V2 EXECUTOR (SSOT for Code Execution)
                exec_result = self.v2_brain.executor.execute_step(
                    tool_name="run_python",
                    args={"code": code}
                )
                
                success = exec_result.get("status") == "success"
                output = exec_result.get("output", "")
                
                self.capability_mgr.record_execution(
                    command=user_input,
                    success=success,
                    function_name="generated_code"
                )
                
                # If successful and reusable, save as a new capability
                if success and self._is_reusable_function(code):
                    try:
                        self.capability_mgr.add_capability(code, user_input, success=True)
                        self.stats["skills_promoted"] += 1
                        logging.info(f"Promoted skill from Gemini: {user_input[:30]}")
                    except Exception as e:
                        logging.warning(f"Could not promote skill: {e}")
                
                # Return the result
                if output and len(output) > 10:
                    return output, success, True
                else:
                    return self.response_gen.confirmation(success), success, True
                    
        except Exception as e:
            logging.error(f"Gemini Fallback Error: {e}")
            
        return self.response_gen.failure(), False, True

    def _handle_layer_2_agentic(self, user_input: str, context: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calls V2 Orchestrator to solve complex, multi-step tasks.
        """
        if not self.v2_brain:
            return {"status": "error", "response": "V2 Brain not available"}
            
        try:
            return self.v2_brain.process(user_input)
        except Exception as e:
            logging.error(f"Layer 2 Execution Error: {e}")
            return {"status": "error", "error": str(e), "response": "I encountered an error planning this task."}

    def _handle_layer_3_execution(self, v2_result: Dict[str, Any], user_input: str, context: Optional[Dict[str, Any]]) -> Tuple[str, bool, bool]:
        """
        Evaluates the V2 result, triggers self-healing if needed, 
        and performs Circular Learning (Skill Promotion).
        """
        status = v2_result.get("status", "error")
        response = v2_result.get("response", "Task completed.")
        success = status in ["success", "partial"]
        
        # 1. TRIGGER SELF-HEALING (If Layer 2 failed)
        if status in ["failure", "error"]:
            error_msg = v2_result.get("error", "Unknown execution error")
            code = v2_result.get("code", "")  # If any code was generated
            
            logging.info(f"Layer 3: Triggering Self-Healing for: {error_msg}")
            self.stats["layer3_healing"] += 1
            
            improved, msg, output = improvement_engine.handle_execution_failure(
                user_input, code, error_msg
            )
            
            if improved:
                logging.info("Layer 3: Self-healing successful.")
                return msg, True, True

        # 2. CIRCULAR LEARNING (Skill Promotion)
        if success and v2_result.get("mode") == "multi":
            self._promote_to_local_tool(v2_result, user_input)

        return response, success, True

    def _promote_to_local_tool(self, v2_result: Dict[str, Any], user_input: str):
        """
        Promotes a successful agentic task to a local skill for future 0-token execution.
        """
        # For now, we log the intent. A full implementation would:
        # 1. Extract the sequence of tool calls from v2_result.
        # 2. Generate a deterministic function from those calls.
        # 3. Add it to intent_router.py's FUNCTION_REGISTRY.
        logging.info(f"Layer 3: Evaluating skill promotion for: {user_input[:40]}...")
        # TODO: Implement full skill extraction and registration
        pass

    def _is_reusable_function(self, code: str) -> bool:
        """Determine if code is a reusable function worth saving."""
        return "def " in code and code.count("def ") <= 2
    
    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        return self.stats


# Singleton access
hybrid_brain = HybridOrchestrator()
