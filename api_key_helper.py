"""
API Key Helper - Utilities for managing API keys
"""

import keyring
import json
from pathlib import Path


def get_api_key():
    """Get stored API key from Windows Credential Manager"""
    try:
        api_key = keyring.get_password("AURA", "api_key")
        return api_key
    except Exception as e:
        print(f"Error reading API key: {e}")
        return None


def get_api_provider():
    """Get stored API provider"""
    try:
        provider = keyring.get_password("AURA", "api_provider")
        return provider if provider else "openrouter"
    except Exception as e:
        print(f"Error reading API provider: {e}")
        return "openrouter"


def set_api_key(provider, api_key):
    """Save API key to Windows Credential Manager"""
    try:
        keyring.set_password("AURA", "api_provider", provider)
        keyring.set_password("AURA", "api_key", api_key)
        
        # Also save to config file
        config_dir = Path.home() / ".aura"
        config_dir.mkdir(exist_ok=True)
        
        config_file = config_dir / "config.json"
        config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
                
        config["api_provider"] = provider
        config["setup_complete"] = True
        
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
            
        return True
    except Exception as e:
        print(f"Error saving API key: {e}")
        return False


def delete_api_key():
    """Delete stored API key"""
    try:
        keyring.delete_password("AURA", "api_key")
        keyring.delete_password("AURA", "api_provider")
        return True
    except Exception as e:
        print(f"Error deleting API key: {e}")
        return False


def has_api_key():
    """Check if API key is configured"""
    api_key = get_api_key()
    return api_key is not None and len(api_key) > 0
