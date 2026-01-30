# AURA: Advanced Agentic AI System

> **AURA** is a hybrid AI operating system that combines sub-15ms local reflexes with advanced agentic reasoning. It is designed to be a "microkernel for AI", acting as a single, unified interface for your digital life.

**Architecture (mandatory for contributors):** Aura uses a hybrid architecture where **all execution flows through a single safe executor**, with local intent mapping and unified tool exposure. Redundant execution paths are intentionally eliminated. Do not reintroduce duplicate execution, OS calls, or routing logic elsewhere.

---

## 🧠 Core Architecture: The Hybrid Brain

AURA uses a Tiered Architecture to balance speed, cost, and intelligence.

### **Layer 1: Local Reflex (0-Token Latency)**
**Path:** `routing/intent_router.py` -> `LocalIntentResolver`
- **What it does:** Instantly map commands like "volume up", "open spotify", "take screenshot" to Python functions.
- **Speed:** <15ms execution time.
- **Cost:** $0.00 (No LLM calls).
- **Control:** Strict deterministic routing using regex and keyword matching.

### **Layer 1.5: Gemini Fallback**
**Path:** `core/hybrid_orchestrator.py`
- **What it does:** Catches commands that miss Layer 1. Uses Gemini Flash to generate single-shot Python code.
- **Example:** "Calculate the square root of 5293" or "Open the file I was working on yesterday".

### **Layer 2: Agentic Reasoning (Aura V2)**
**Path:** `auraaiv2/`
- **What it does:** Handles complex, multi-step tasks requiring planning.
- **Components:**
    - **PlannerAgent:** Decomposes tasks into steps.
    - **DecompositionGate:** Decides if a task needs planning or just a single tool.
    - **Executor:** The **Single Source of Truth** for actually running the code.

### **Layer 3: Self-Healing & Learning**
**Path:** `learning/self_improvement.py`
- **What it does:**
    - Automatically retries failed commands.
    - Installs missing pip packages (`scikit-learn`, `requests`, etc.) autonomously.
    - Promotes successful Gemini code to Layer 1 capability (Skill Promotion).

---

## 🏛️ Architectural Laws (Single Source of Truth)

To ensure stability, AURA enforces strict boundaries. **Do not violate these laws.**

1.  **Code Execution Law**:
    - **ALL** code execution must happen inside `auraaiv2/execution/executor.py`.
    - `LocalIntentResolver` only *plans* the tool call; it does NOT execute it.
    - `HybridOrchestrator` delegates to the V2 Executor.

2.  **OS Interaction Law**:
    - `utils/windows_system.py` is the **ONLY** place that touches Windows APIs (volume, brightness, media, files).
    - `tools/outside_bridge.py` exposes these functions as Tools.

3.  **Passive Learning Law**:
    - `self_improvement.py` owns the retry/fix loop.
    - Executors do not decide to learn; they only report success/failure.

4.  **One Promotion API Only**:
    - Skill promotion (adding capabilities, learning from success) happens **only** in `learning/self_improvement.py` and via `capability_manager.add_capability()`.
    - No hidden learning logic in tools or executor. If learning fragments again, duplication returns.

---

## ⚡ Fast Path & Performance

- **`Scripts/verify_fast_path.py`** — Keep this script forever. On any change to routing, executor, or tools: run it, compare latency before/after, and ensure the fast path stays fast. Most systems lose performance silently; this one does not.

---

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.10+
- Windows 10/11

### 1. Environment Setup
Create a `.env` file in the root directory:
```bash
GEMINI_API_KEY=AIzaSy...
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Note: AURA will auto-install missing packages during runtime if needed via Layer 3)*

### 3. Run AURA
```bash
python main.py
```

---

## 📂 Directory Structure

```
e:\agent\
├── core/                   # The "Brain" (Orchestrator)
│   ├── hybrid_orchestrator.py
│   └── context.py
├── routing/                # Layer 1 (Fast Path)
│   ├── intent_router.py
│   └── function_executor.py (LocalIntentResolver)
├── learning/               # Layer 3 (Self-Healing)
├── utils/                  # OS System APIs (SSOT)
│   ├── windows_system.py
│   ├── advanced_control.py
│   └── tts_manager.py
├── auraaiv2/               # Layer 2 (Agentic V2)
│   ├── execution/          # The V2 Executor
│   └── tools/              # Tool Registry
├── features/               # High-level Apps (App Creator, Email)
└── ui/                     # Interface (Butler, Widget)
```

---

## ⚡ Quick Start Commands

| Command | Layer | Description |
| :--- | :--- | :--- |
| **"Set volume to 50"** | 1 (Reflex) | <15ms execution. Instant. |
| **"Open Spotify"** | 1 (Reflex) | Launches app immediately. |
| **"Generate a python app for a calculator"** | 2 (Agentic) | V2 Planner creates code, writes file, tests it. |
| **"What's the meaning of life?"** | 1.5 (Gemini) | LLM chat response. |

---

> **AURA V2** - *Automating the Unautomatable.*
