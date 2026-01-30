"""
AURA User Configuration
Persistent user settings stored in ~/.aura/user_config.json
"""

import os
import json
from pathlib import Path
from typing import Any, Optional


class UserConfig:
    """
    Manages user configuration that persists across sessions.
    Settings are stored in ~/.aura/user_config.json
    """
    
    DEFAULT_CONFIG = {
        "user_name": "User",
        "email_signature": "",
        "preferred_tone": "professional",
        "voice_enabled": True,
        "hands_free_timeout": 30,
        "theme": "dark",
    }
    
    def __init__(self):
        self.config_dir = Path.home() / ".aura"
        self.config_file = self.config_dir / "user_config.json"
        self.config = self.DEFAULT_CONFIG.copy()
        self._load()
    
    def _load(self):
        """Load configuration from file."""
        try:
            self.config_dir.mkdir(exist_ok=True)
            
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # Merge with defaults (so new settings get default values)
                    self.config.update(saved)
                print(f"[Config] Loaded user config for {self.config.get('user_name', 'User')}")
        except Exception as e:
            print(f"[Config] Could not load config: {e}")
    
    def _save(self):
        """Save configuration to file."""
        try:
            self.config_dir.mkdir(exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            print(f"[Config] Saved user config")
        except Exception as e:
            print(f"[Config] Could not save config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a config value and save."""
        self.config[key] = value
        self._save()
    
    @property
    def user_name(self) -> str:
        return self.config.get("user_name", "User")
    
    @user_name.setter
    def user_name(self, value: str):
        self.set("user_name", value)
    
    @property
    def email_signature(self) -> str:
        return self.config.get("email_signature", self.user_name)
    
    @email_signature.setter
    def email_signature(self, value: str):
        self.set("email_signature", value)
    
    @property
    def preferred_tone(self) -> str:
        return self.config.get("preferred_tone", "professional")
    
    @preferred_tone.setter
    def preferred_tone(self, value: str):
        self.set("preferred_tone", value)
    
    @property
    def voice_enabled(self) -> bool:
        return self.config.get("voice_enabled", True)
    
    @voice_enabled.setter
    def voice_enabled(self, value: bool):
        self.set("voice_enabled", value)


# Global instance
user_config = UserConfig()


def get_user_name() -> str:
    """Get the user's configured name."""
    return user_config.user_name


def set_user_name(name: str) -> None:
    """Set the user's name."""
    user_config.user_name = name


# Test
if __name__ == "__main__":
    print(f"Current user: {user_config.user_name}")
    user_config.user_name = "Cyriac"
    print(f"Updated user: {user_config.user_name}")
    print(f"Config file: {user_config.config_file}")
