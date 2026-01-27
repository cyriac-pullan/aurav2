# AURA API Key Wizard - Installation Guide

## 📦 Quick Start

### **Option 1: Complete Installation (Recommended)**
```bash
install_aura_widget.bat
```

This will:
1. ✅ Check Python installation
2. ✅ Create virtual environment
3. ✅ Install all dependencies
4. ✅ Launch API key setup wizard
5. ✅ Create desktop shortcut

### **Option 2: Just Test the Wizard**
```bash
test_wizard.bat
```

### **Option 3: Launch AURA Widget**
```bash
run_widget.bat
```
Or use the desktop shortcut after installation.

---

## 🎯 What the Wizard Does

The AURA API Key Wizard provides a beautiful first-run experience that:
- **Welcomes** users to AURA
- **Guides** them to choose an AI provider (OpenRouter, Gemini, or OpenAI)
- **Helps** them get and enter their API key
- **Verifies** the API key works correctly
- **Securely stores** the key in Windows Credential Manager

---

## 🔑 Getting API Keys

### **OpenRouter (Recommended)**
- **Cost**: ~$0.001 per request, free credits included
- **Sign up**: https://openrouter.ai/keys
- **Why**: Cheapest rates, many models available

### **Google Gemini**
- **Cost**: Free tier (60 requests/min)
- **Sign up**: https://aistudio.google.com/app/apikey
- **Why**: Generous free tier, fast responses

### **OpenAI**
- **Cost**: ~$0.002 per request
- **Sign up**: https://platform.openai.com/api-keys
- **Why**: High quality, ChatGPT API

---

## 🎨 Wizard Features

✨ **Beautiful UI**
- Modern dark theme with gradient backgrounds
- Smooth animations and transitions
- JARVIS-inspired aesthetics

🔒 **Secure Storage**
- Uses Windows Credential Manager (native)
- No plain-text storage
- Keys are encrypted by Windows

✅ **API Validation**
- Tests your API key before saving
- Real API call verification
- Clear error messages

💡 **Helpful Guidance**
- Step-by-step instructions
- Direct links to API provider signup pages
- Transparent pricing information

---

## 📁 Files Created

After installation:
- `~/.aura/config.json` - Configuration (no sensitive data)
- Windows Credential Manager - Encrypted API key
- Desktop shortcut - Quick launch

---

## 🔧 Manual Setup (Advanced)

If you prefer manual configuration:

```python
from api_key_helper import set_api_key

# Set your API key
set_api_key("openrouter", "sk-or-v1-...")
```

Or directly in Windows:
1. Open Credential Manager
2. Add Windows Credential
3. Internet/Network Address: `AURA`
4. User: `api_key`
5. Password: Your API key

---

## 🚀 First Launch Experience

When you first run AURA:

1. **Wizard appears automatically** (if no API key detected)
2. **Choose your provider** (OpenRouter, Gemini, or OpenAI)
3. **Get your API key** (follow the wizard's instructions)
4. **Paste and verify** (wizard tests the connection)
5. **Start using AURA!** (widget launches automatically)

---

## ❓ Troubleshooting

### Wizard doesn't appear
- Make sure no API key is already configured
- Delete `~/.aura/config.json` to trigger first-run
- Run `test_wizard.bat` directly

### API key validation fails
- Double-check you copied the full key
- Ensure no extra spaces
- Try regenerating the key from your provider

### Dependencies missing
- Run `install_aura_widget.bat` again
- Check Python version (3.8+ required)
- Install PyQt5: `pip install PyQt5`

---

## 💡 Tips

- **85%+ commands run locally** - Most AURA commands don't use your API!
- **Change API key anytime** - Run `test_wizard.bat` to reconfigure
- **Multiple providers** - Switch between providers easily
- **Privacy first** - Your API key never leaves your PC

---

## 🎉 You're Ready!

After setup, just say **"Hey AURA"** and give voice commands!

Try:
- "What time is it?"
- "Open Notepad"
- "Tell me a joke"
- "Set brightness to 50%"

Most commands work offline! 🚀
