# AURA: Advanced Agentic AI System

> **AURA** is a hybrid AI operating system that combines **sub-15ms local reflexes** with advanced agentic reasoning. It acts as a "microkernel for AI"—a single, unified interface for your digital life on Windows.

**Mandatory for contributors:** AURA uses a hybrid architecture where **all execution flows through a single safe executor**, with local intent mapping and unified tool exposure. Redundant execution paths are intentionally eliminated. Do not reintroduce duplicate execution, OS calls, or routing logic elsewhere.

---

## Table of Contents

- [Features](#-features)
- [Architecture Overview](#-architecture-overview)
- [The Four Layers](#-the-four-layers)
- [Request Flow](#-request-flow)
- [Architectural Laws (Single Source of Truth)](#-architectural-laws-single-source-of-truth)
- [Directory Structure](#-directory-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Running AURA](#-running-aura)
- [Scripts & Build](#-scripts--build)
- [Example Commands](#-example-commands)
- [Fast Path & Performance](#-fast-path--performance)
- [Development Guide](#-development-guide)
- [Security & Safety](#-security--safety)
- [License](#-license)

---

## Features

| Feature | Description |
|--------|-------------|
| **0-token local reflex** | Commands like "volume up", "open Spotify", "take screenshot" execute in &lt;15ms with no LLM calls. |
| **Gemini fallback** | Unmatched commands get single-shot Python code generation (Layer 1.5). |
| **Agentic planning (V2)** | Complex, multi-step tasks are decomposed and executed by the Aura V2 orchestrator. |
| **Self-healing & learning** | Failed commands trigger retries; successful Gemini code can be promoted to local capabilities. |
| **Floating widget** | Always-on-top JARVIS-style UI with wake word, TTS, and conversational butler mode. |
| **Single OS boundary** | All Windows API usage is centralized in `utils/windows_system.py`; no scattered OS calls. |
| **Single execution authority** | All tool and code execution goes through `auraaiv2/execution/executor.py` and `ai/code_executor.py`. |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT (Voice / Text)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  CORE: HybridOrchestrator (SINGLE DECISION MAKER)                           │
│  core/hybrid_orchestrator.py                                                │
│  • Routes every command through exactly one path                            │
│  • No duplicate routing logic elsewhere                                     │
└─────────────────────────────────────────────────────────────────────────────┘
     │                    │                    │                    │
     ▼                    ▼                    ▼                    ▼
┌──────────┐    ┌──────────────────┐    ┌──────────────┐    ┌─────────────────┐
│ LAYER 1  │    │ LAYER 1.5        │    │ LAYER 2      │    │ LAYER 3         │
│ Local    │    │ Gemini Fallback  │    │ Agentic V2   │    │ Self-Healing    │
│ Reflex   │    │ (code gen)       │    │ (planning)   │    │ (learning)      │
│ 0 tokens │    │ ~100–500 tokens  │    │ V2 executor  │    │ skill promotion │
└──────────┘    └──────────────────┘    └──────────────┘    └─────────────────┘
     │                    │                    │                    │
     └────────────────────┴────────────────────┴────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SINGLE EXECUTION AUTHORITY                                                 │
│  • auraaiv2/execution/executor.py  (tool execution)                         │
│  • ai/code_executor.py             (Python exec() — only place allowed)     │
└─────────────────────────────────────────────────────────────────────────────┘
                                        │
                                        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  SINGLE OS BOUNDARY                                                         │
│  utils/windows_system.py  (volume, brightness, apps, media, files, etc.)   │
│  utils/advanced_control.py (keyboard, mouse, clipboard, terminal)            │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## The Four Layers

### Layer 1: Local Reflex (0-token latency)

| Item | Detail |
|------|--------|
| **Path** | `routing/intent_router.py` → `LocalIntentResolver` (in `routing/function_executor.py`) |
| **Role** | Map natural language to a tool name + args using regex and keyword matching. No LLM. |
| **Speed** | &lt;15ms end-to-end. |
| **Cost** | $0.00. |
| **Examples** | "Set volume to 50", "Open Spotify", "Take screenshot", "Mute", "Lock computer". |
| **Confidence** | Executed only when confidence ≥ 0.85. Lower confidence falls through to Layer 1.5 or 2. |

### Layer 1.5: Gemini Fallback

| Item | Detail |
|------|--------|
| **Path** | `core/hybrid_orchestrator.py` → `_handle_layer_1_gemini_fallback` |
| **Role** | When Layer 1 does not match, use Gemini to generate single-shot Python code. |
| **Execution** | Generated code runs via V2 executor’s `run_python` tool (single execution authority). |
| **Examples** | "Calculate the square root of 5293", "Open the file I was working on yesterday". |
| **Learning** | Successful, reusable code can be promoted to Layer 1 via `capability_manager.add_capability()` (only promotion API). |

### Layer 2: Agentic Reasoning (Aura V2)

| Item | Detail |
|------|--------|
| **Path** | `auraaiv2/` — `core/orchestrator.py`, `execution/executor.py`, `tools/`, `agents/` |
| **Role** | Multi-step tasks: plan → decompose → execute tools via the single executor. |
| **Components** | Planner Agent, Decomposition Gate, Task Decomposition Agent, Tool Executor. |
| **Tools** | File ops, system (audio, display, power, desktop, clipboard, input), apps, and root bridge (`outside_bridge` to `utils/windows_system` and `utils/advanced_control`). |
| **Examples** | "Generate a Python calculator app", "Create a folder on Desktop and save a note there". |

### Layer 3: Self-Healing & Learning

| Item | Detail |
|------|--------|
| **Path** | `learning/self_improvement.py`, `learning/capability_manager.py` |
| **Role** | Retry failed commands; install missing pip packages; promote successful Gemini code to local capabilities. |
| **Rule** | Skill promotion only via `learning/self_improvement.py` and `capability_manager.add_capability()`. No hidden learning in tools or executor. |

---

## Request Flow

1. **User** speaks or types a command.
2. **Widget / CLI** sends the command to `ui/bridge.py` (AuraV2Bridge) or directly to `core/hybrid_orchestrator.py`.
3. **HybridOrchestrator** (single decision maker):
   - Tries **Layer 1**: local intent router → if high confidence, resolve intent to tool name + args → execute via V2 executor → return.
   - Else tries **Layer 1.5**: Gemini code generation → execute via V2 `run_python` → optionally promote to capability → return.
   - Else **Layer 2**: hand off to Aura V2 orchestrator (plan → execute steps via same executor).
   - On failure, **Layer 3** can retry or promote.
4. **Executor** (single authority) runs only tools or code from the registry; OS actions go through **utils/windows_system** and **utils/advanced_control** (single OS boundary).

---

## Architectural Laws (Single Source of Truth)

Do not violate these; they keep the system maintainable and safe.

| Law | Rule |
|-----|------|
| **Code execution** | All execution goes through `auraaiv2/execution/executor.py` (tools) and `ai/code_executor.py` (Python `exec()`). No `exec()` outside `ai/code_executor.py`. |
| **OS interaction** | Only `utils/windows_system.py` and `utils/advanced_control.py` may call Windows APIs. All tools that need OS actions use these or the `auraaiv2/tools/outside_bridge` wrappers. |
| **Routing** | All routing decisions are made in `core/hybrid_orchestrator.py`. Do not duplicate routing logic elsewhere. |
| **One promotion API** | Skill promotion only in `learning/self_improvement.py` and via `capability_manager.add_capability()`. No learning logic in tools or executor. |
| **Fast path** | After any change to routing, executor, or tools, run `Scripts/verify_fast_path.py` and compare latency so the fast path stays fast. |

---

## Is only the `auraaiv2` folder required?

**No.** For the full AURA app (widget, hybrid routing, single OS boundary), you need the **whole `agent` repo**, not just `auraaiv2`.

| What | Role |
|------|------|
| **agent (root)** | Entry point (widget, scripts), hybrid orchestrator (`core/`), Layer 1 routing (`routing/`), AI client & code executor (`ai/`), **single OS boundary** (`utils/`), config, learning, UI bridge, features (app creator, email). |
| **auraaiv2/** | **Layer 2** only: agentic orchestrator, tool executor, tools. It **depends on the root** for: `utils.windows_system`, `utils.advanced_control`, `ai.code_executor`, `features.app_creator`, `features.email_assistant` (via `outside_bridge` and `_root_bridge`). |

So:

- **Widget / hybrid flow** → Runs from **agent** root; `core/hybrid_orchestrator` uses **auraaiv2** as one layer. Root + auraaiv2 are both required.
- **Standalone auraaiv2** → You can run `auraaiv2/main.py` alone (e.g. for V2-only tests), but then `outside_bridge` will not see root `utils`/`ai`/`features` unless the **current working directory and `sys.path`** include the **agent** root. So even “standalone” V2 is designed to live inside the agent repo.

**Summary:** Keep the full folder structure. `auraaiv2` is a required **subfolder**, not a standalone app in this project.

---

## Directory Structure

```
agent/
├── ai/                          # AI clients and code execution
│   ├── __init__.py
│   ├── client.py                # Gemini client (google-genai), code generation
│   └── code_executor.py         # SINGLE exec() BOUNDARY — safe Python execution
├── config/
│   ├── __init__.py
│   ├── config.py                # App config, API keys, security settings
│   └── user_config.py           # User preferences
├── core/                        # The "brain"
│   ├── __init__.py
│   ├── context.py               # LocalContext, AuraState, AuraMode
│   └── hybrid_orchestrator.py   # SINGLE DECISION MAKER — routes all commands
├── features/                    # High-level features
│   ├── __init__.py
│   ├── app_creator.py           # Agentic app generation (Gemini + test loop)
│   └── email_assistant.py      # Email drafting
├── learning/                    # Layer 3 — self-healing and learning
│   ├── __init__.py
│   ├── capability_manager.py   # Capabilities, add_capability (only promotion API)
│   ├── memory_manager.py       # Long-term memory (Supermemory)
│   └── self_improvement.py     # Retry, pip install, skill promotion
├── routing/                     # Layer 1 — fast path
│   ├── __init__.py
│   ├── intent_router.py         # Local intent classification (regex/keyword/fuzzy)
│   └── function_executor.py    # LocalIntentResolver + bridge FunctionExecutor
├── ui/                          # User interface
│   ├── __init__.py
│   ├── bridge.py                # AuraV2Bridge — widget ↔ hybrid orchestrator
│   ├── response_generator.py   # Confirmations, greetings, failures
│   └── wake_word.py            # Wake word and command extraction
├── utils/                       # SINGLE OS BOUNDARY (root)
│   ├── __init__.py
│   ├── windows_system.py       # Volume, brightness, apps, media, files, lock, etc.
│   ├── advanced_control.py     # Keyboard, mouse, clipboard, terminal
│   └── tts_manager.py          # Text-to-speech
├── aura_floating_widget/        # JARVIS-style floating UI
│   ├── aura_widget.py          # PyQt5 widget, wake word, TTS, bridge integration
│   └── start_aura_widget.bat
├── auraaiv2/                    # Layer 2 — agentic V2
│   ├── agents/                 # Intent, planner, decomposition gate, TDA
│   ├── core/                   # Orchestrator, pipelines, response, tool_resolver
│   ├── execution/
│   │   └── executor.py         # SINGLE EXECUTION AUTHORITY (tool execution)
│   ├── tools/
│   │   ├── base.py, registry.py, loader.py
│   │   ├── outside_bridge.py  # Exposes root utils as V2 tools
│   │   ├── system/            # Audio, display, power, desktop, clipboard, etc.
│   │   │   └── _root_bridge.py # Delegates to root utils (no direct OS here)
│   │   ├── files/             # Create, read, write, move, delete files
│   │   └── memory/            # Facts, recent context
│   ├── models/                 # Model manager, providers (Gemini, Ollama, OpenRouter)
│   ├── memory/                 # Ambient, facts
│   ├── config/                 # runtime, models, settings
│   ├── main.py                 # Standalone V2 entry (optional)
│   └── requirements.txt
├── Scripts/
│   ├── verify_fast_path.py    # KEEP FOREVER — latency check after changes
│   ├── run_widget.bat         # Launch floating widget
│   ├── install_aura_widget.bat
│   ├── build_exe.bat, build_installer.bat, build_complete_installer.bat
│   └── test_wizard.bat
├── Installer/                  # PyInstaller spec, Inno Setup script, icon
├── .env.example                # Template for .env
├── .gitignore
├── README.md                   # This file
└── requirements.txt
```

---

## Installation

### Prerequisites

- **Python** 3.10 or 3.11+ (3.13 supported)
- **Windows** 10 or 11
- **Git** (optional, for cloning)

### 1. Clone or download

```bash
git clone <your-repo-url>
cd agent
```

### 2. Virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Key dependencies: `google-generativeai`, `google-genai`, `PyQt5`, `rapidfuzz`, `pyautogui`, `pycaw`, `screen-brightness-control`, `SpeechRecognition`, `pyttsx3`, `requests`, `supermemory` (optional, for long-term memory).

### 4. Environment variables

Copy the example env file and set at least the Gemini API key:

```bash
copy .env.example .env
```

Edit `.env`:

```ini
# Required for Layer 1.5 and conversation
GEMINI_API_KEY=your_gemini_api_key_here

# Optional
SUPERMEMORY_API_KEY=your_supermemory_key   # Long-term memory
USER_NAME=Sir
WAKE_WORD=aura
```

Config is also loaded from `%USERPROFILE%\.aura\.env` if present.

---

## Configuration

| Source | Purpose |
|--------|---------|
| **.env** (root or `~/.aura/.env`) | `GEMINI_API_KEY`, `SUPERMEMORY_API_KEY`, `USER_NAME`, `WAKE_WORD`, etc. |
| **config/config.py** | API provider/model, security (timeout, code length), paths (config dir, capabilities, learning data). |
| **config/user_config.py** | User preferences. |
| **auraaiv2/config/** | V2 runtime, model YAMLs (local/hosted/hybrid). |

Capabilities and learning data are stored under `%USERPROFILE%\.ai_assistant\` by default (configurable in config).

---

## Running AURA

### Floating widget (recommended)

```bash
# From repo root
Scripts\run_widget.bat
# or
python aura_floating_widget\aura_widget.py
```

First-time setup: run `Scripts\install_aura_widget.bat` to create venv, install deps, and optionally run the API key wizard.

### Programmatic use

```python
from core.hybrid_orchestrator import hybrid_brain

response, success, used_llm = hybrid_brain.process("Set volume to 50", None)
```

### Widget integration

The widget uses `ui/bridge.py` (AuraV2Bridge), which calls `hybrid_brain.process()` so all commands go through the same four-layer flow.

---

## Scripts & Build

| Script | Purpose |
|--------|---------|
| **Scripts/run_widget.bat** | Launch the floating widget. |
| **Scripts/install_aura_widget.bat** | First-time install: venv, deps, API wizard, desktop shortcut. |
| **Scripts/verify_fast_path.py** | **Keep forever.** Run after routing/executor/tool changes; compare latency to keep fast path &lt;100ms. |
| **Scripts/build_exe.bat** | Build standalone executable (PyInstaller). |
| **Scripts/build_installer.bat** | Build installer (e.g. Inno Setup). |
| **Scripts/test_wizard.bat** | Run API key / setup wizard. |

Run fast path verification from repo root:

```bash
python Scripts/verify_fast_path.py
```

---

## Example Commands

| Command | Layer | Description |
|--------|--------|-------------|
| "Set volume to 50" | 1 | Local reflex, &lt;15ms. |
| "Mute" / "Unmute" | 1 | Local. |
| "Open Spotify" / "Open Chrome" | 1 | Local. |
| "Take screenshot" | 1 | Local. |
| "Lock computer" | 1 | Local. |
| "What's the meaning of life?" | 1.5 / conversation | Gemini chat. |
| "Calculate the square root of 5293" | 1.5 | Gemini code gen → run_python. |
| "Generate a Python calculator app" | 2 | V2 planner + executor + file tools. |
| "Create a folder on Desktop and save a note" | 2 | Multi-step V2. |

---

## Fast Path & Performance

- **Script:** `Scripts/verify_fast_path.py`
- **Purpose:** Ensure ToolExecutor load and execution stay within latency bounds (e.g. &lt;100ms for a simple tool call).
- **When:** After any change to routing, executor, or tools. Compare before/after.
- **Rule:** Keep this script forever; do not delete it. Most systems regress performance silently; this one is checked explicitly.

---

## Development Guide

### Adding a new local command (Layer 1)

1. Add patterns or keywords in `routing/intent_router.py` and map to a function name + args.
2. Ensure that function name is resolved to a V2 tool in `routing/function_executor.py` (LocalIntentResolver) and that the tool is registered (e.g. via `auraaiv2/tools/outside_bridge.py` or a system tool delegating to root).
3. Run `Scripts/verify_fast_path.py`.

### Adding a new OS action

1. Implement the function in **one place only:** `utils/windows_system.py` or `utils/advanced_control.py`.
2. Expose it as a V2 tool in `auraaiv2/tools/outside_bridge.py` if the orchestrator should call it by name.
3. Do not add Windows API calls in auraaiv2 tools; use `_root_bridge` to call root utils.

### Running tests

- Root project: add tests under e.g. `tests/` and run with `pytest`.
- Aura V2: `auraaiv2/tests/` and `auraaiv2/test_scripts/` (e.g. `python -m pytest auraaiv2/tests/`).

---

## Security & Safety

- **Execution:** All code execution is funneled through `ai/code_executor.py` (with optional timeout and validation). No `exec()` elsewhere.
- **OS:** All OS interaction is in `utils/windows_system.py` and `utils/advanced_control.py`. No direct Windows API usage in agents or tools.
- **API keys:** Stored in `.env` or `~/.aura/.env`; not committed. Use `.env.example` as a template.
- **Tool risk:** Tools declare risk levels; the executor can enforce safety policy. Empty Recycle Bin and similar actions use confirmation where implemented.

---

## License

See repository license file. Use at your own risk; the project can execute actions on your Windows system and call external APIs.

---

**AURA** — *Automating the Unautomatable.*
