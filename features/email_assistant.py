"""
AURA Email Assistant
Autonomous email drafting, composing, and sending.

Features:
- Draft emails with Gemini AI
- Copy to clipboard for easy paste
- Open default email client with pre-filled content
- (Optional) Send via SMTP if configured
"""

import os
import re
import webbrowser
import subprocess
from pathlib import Path
from typing import Tuple, Optional
from urllib.parse import quote


class EmailAssistant:
    """
    AI-powered email assistant.
    
    Capabilities:
    - Draft professional emails based on natural language
    - Copy to clipboard
    - Open in default email client (mailto:)
    - Send via Outlook/Gmail if configured
    """
    
    def __init__(self):
        self._ai_client = None
        self.drafts_dir = Path.home() / "Documents" / "AURA_Drafts"
        self.drafts_dir.mkdir(exist_ok=True)
    
    @property
    def ai_client(self):
        """Lazy load AI client"""
        if self._ai_client is None:
            try:
                from ai.client import ai_client
                self._ai_client = ai_client
            except ImportError as e:
                print(f"[Email] AI client not available: {e}")
        return self._ai_client
    
    def draft_email(self, instruction: str, recipient: str = None, 
                    tone: str = "professional") -> Tuple[bool, str, dict]:
        """
        Draft an email based on natural language instruction.
        
        Args:
            instruction: What the email should say (e.g., "ask for a day off tomorrow")
            recipient: Optional recipient name/email
            tone: professional, casual, formal, friendly
            
        Returns:
            (success, message, email_dict with subject, body, to)
        """
        if not self.ai_client:
            return False, "AI client not available.", {}
        
        print(f"\n{'='*50}")
        print(f"📧 AURA Email Assistant")
        print(f"{'='*50}")
        print(f"📝 Request: {instruction}")
        print(f"👤 Recipient: {recipient or 'Not specified'}")
        print(f"🎨 Tone: {tone}")
        print(f"{'='*50}\n")
        
        prompt = f"""You are an expert email writer. Draft an email based on this request:

REQUEST: {instruction}
RECIPIENT: {recipient or 'Not specified'}
TONE: {tone}

        # Get user name from config
        try:
            from config.user_config import get_user_name
            user_name = get_user_name()
        except ImportError:
            user_name = "User"

IMPORTANT: Return ONLY a JSON object with these fields:
{{
    "subject": "Email subject line",
    "body": "Full email body with proper greeting and signature. Sign off with '{user_name}' as the name.",
    "to": "{recipient or ''}"
}}

Do NOT include any markdown formatting or explanation. Return ONLY the JSON."""

        try:
            response = self.ai_client.client.models.generate_content(
                model=self.ai_client.model,
                contents=prompt,
            )
            
            result_text = response.text.strip()
            
            # Clean JSON if wrapped in markdown
            if result_text.startswith("```"):
                result_text = re.sub(r'^```\w*\n?', '', result_text)
                result_text = re.sub(r'\n?```$', '', result_text)
            
            import json
            email_data = json.loads(result_text)
            
            subject = email_data.get("subject", "")
            body = email_data.get("body", "")
            to = email_data.get("to", recipient or "")
            
            print(f"✅ Email drafted!")
            print(f"📋 Subject: {subject}")
            print(f"📄 Body length: {len(body)} chars")
            
            return True, "Email drafted successfully!", {
                "subject": subject,
                "body": body,
                "to": to
            }
            
        except Exception as e:
            print(f"❌ Draft failed: {e}")
            return False, f"Failed to draft email: {e}", {}
    
    def copy_to_clipboard(self, text: str) -> bool:
        """Copy text to clipboard."""
        try:
            import subprocess
            # Use Windows clip command
            process = subprocess.Popen(
                ['clip'],
                stdin=subprocess.PIPE,
                shell=True
            )
            process.communicate(text.encode('utf-8'))
            return True
        except Exception as e:
            print(f"[Email] Clipboard error: {e}")
            return False
    
    def open_in_email_client(self, to: str = "", subject: str = "", body: str = "") -> bool:
        """
        Open the default email client with pre-filled content using mailto: link.
        """
        try:
            # Build mailto URL
            mailto = f"mailto:{quote(to)}?subject={quote(subject)}&body={quote(body)}"
            webbrowser.open(mailto)
            print(f"📬 Opened email client with draft")
            return True
        except Exception as e:
            print(f"❌ Could not open email client: {e}")
            return False
    
    def open_outlook_draft(self, to: str = "", subject: str = "", body: str = "") -> bool:
        """
        Open Outlook with a new email draft (Windows only).
        """
        try:
            import subprocess
            
            # Try Outlook COM automation
            ps_script = f'''
$outlook = New-Object -ComObject Outlook.Application
$mail = $outlook.CreateItem(0)
$mail.To = "{to}"
$mail.Subject = "{subject.replace('"', "'")}"
$mail.Body = @"
{body.replace('"', "'")}
"@
$mail.Display()
'''
            subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
            print(f"📬 Opened Outlook with draft")
            return True
        except Exception as e:
            print(f"❌ Outlook automation failed: {e}")
            # Fallback to mailto
            return self.open_in_email_client(to, subject, body)
    
    def save_draft(self, subject: str, body: str, to: str = "") -> str:
        """Save draft to file for reference."""
        from datetime import datetime
        
        # Create filename from subject
        safe_subject = "".join(c if c.isalnum() or c in " -_" else "_" for c in subject[:30])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{safe_subject}.txt"
        
        filepath = self.drafts_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"To: {to}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"\n{'-'*40}\n\n")
            f.write(body)
        
        print(f"💾 Saved draft to: {filepath}")
        return str(filepath)


# Global instance
email_assistant = EmailAssistant()


def draft_email(instruction: str, recipient: str = None, 
                tone: str = "professional", 
                action: str = "clipboard") -> Tuple[bool, str]:
    """
    Draft an email and perform an action.
    
    Args:
        instruction: What the email should say
        recipient: Who it's for
        tone: professional, casual, formal, friendly
        action: clipboard, open, outlook, save
        
    Returns:
        (success, message)
    """
    success, msg, email_data = email_assistant.draft_email(instruction, recipient, tone)
    
    if not success:
        return False, msg
    
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")
    to = email_data.get("to", "")
    
    # Perform the requested action
    if action == "clipboard":
        full_email = f"Subject: {subject}\n\n{body}"
        if email_assistant.copy_to_clipboard(full_email):
            return True, f"Email drafted and copied to clipboard! Subject: {subject}"
        else:
            return True, f"Email drafted but clipboard failed. Subject: {subject}"
    
    elif action == "open":
        email_assistant.open_in_email_client(to, subject, body)
        return True, f"Email drafted and opened in your email client!"
    
    elif action == "outlook":
        email_assistant.open_outlook_draft(to, subject, body)
        return True, f"Email drafted and opened in Outlook!"
    
    elif action == "save":
        filepath = email_assistant.save_draft(subject, body, to)
        return True, f"Email saved to {filepath}"
    
    else:
        # Default: copy to clipboard
        full_email = f"Subject: {subject}\n\n{body}"
        email_assistant.copy_to_clipboard(full_email)
        return True, f"Email drafted! Subject: {subject}"


# Test
if __name__ == "__main__":
    print("Testing Email Assistant...")
    
    success, message = draft_email(
        instruction="Ask my manager for a day off tomorrow due to a doctor's appointment",
        recipient="manager@company.com",
        tone="professional",
        action="clipboard"
    )
    
    print(f"\nResult: {message}")
