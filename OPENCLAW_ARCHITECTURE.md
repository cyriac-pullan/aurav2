# OpenClaw Architecture (Desktop Assistant)

This project now supports **OpenClaw branding** on top of the existing hybrid architecture.

## Core Architecture (unchanged)
- **Layer 1 (Fast path):** local intent routing.
- **Layer 1.5:** generated code fallback.
- **Layer 2:** AuraV2 agentic planner/executor.
- **Layer 3:** self-improvement and capability promotion.
- **Single execution authority:** `auraaiv2/execution/executor.py` + `ai/code_executor.py`.
- **Single OS boundary:** `utils/windows_system.py` + `utils/advanced_control.py`.

## OpenClaw Branding
- Assistant name is now configurable via:
  - `OPENCLAW_ASSISTANT_NAME`
  - `AURA_ASSISTANT_NAME`
- Default runtime assistant name is **OpenClaw**.

## Cross-platform functionality
To keep OpenClaw functional in non-Windows environments:
- fallback tools are registered for `get_current_time` and `get_system_volume` when Windows system APIs are unavailable;
- precondition checks in executor now skip Windows GUI imports unless a tool actually requires window introspection.

This lets core validation and basic assistant flows run in Linux/CI while preserving full Windows behavior where dependencies exist.
