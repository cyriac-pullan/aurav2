"""Branding helpers for assistant identity.

Supports OpenClaw rebranding without touching core logic.
"""

import os


def assistant_name() -> str:
    """Return configured assistant name.

    Priority:
    1. OPENCLAW_ASSISTANT_NAME
    2. AURA_ASSISTANT_NAME
    3. default "OpenClaw"
    """
    return (
        os.getenv("OPENCLAW_ASSISTANT_NAME")
        or os.getenv("AURA_ASSISTANT_NAME")
        or "OpenClaw"
    )
