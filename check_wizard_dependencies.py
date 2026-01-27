"""
Check all dependencies for AURA API Key Wizard
"""

import sys

print("=" * 60)
print("AURA Wizard - Dependency Checker")
print("=" * 60)
print()

dependencies = {
    "PyQt5": "PyQt5",
    "keyring": "keyring",
    "requests": "requests (for OpenRouter)",
    "google.generativeai": "google-generativeai (for Gemini)",
    "openai": "openai (for OpenAI)",
}

missing = []
installed = []

for module, package in dependencies.items():
    try:
        __import__(module)
        installed.append(f"✅ {package}")
    except ImportError:
        missing.append(f"❌ {package}")

print("Installed Dependencies:")
for item in installed:
    print(f"  {item}")

if missing:
    print()
    print("Missing Dependencies:")
    for item in missing:
        print(f"  {item}")
    print()
    print("To install missing dependencies:")
    for item in missing:
        package = item.split("❌ ")[1]
        print(f"  pip install {package}")
else:
    print()
    print("✅ All dependencies installed!")
    print()
    print("You can now run:")
    print("  - test_wizard.bat")
    print("  - python api_key_wizard.py")

print()
print("=" * 60)
