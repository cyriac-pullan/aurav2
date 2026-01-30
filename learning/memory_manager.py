"""
AURA Memory Manager - Supermemory Integration

Provides long-term memory and skill sharing across users via Supermemory.ai.

Layers:
    1. Session (local_context.py) - Short-term, per-session
    2. Personal Memory - User's private facts/preferences
    3. Shared Knowledge - Community tips and facts
    4. Shared Skills - Executable code learned by any user
"""

import os
import json
import logging
from typing import Optional, Dict, Any, List

# Lazy import to avoid startup errors if not configured
_supermemory_client = None


def _get_client():
    """Lazy load Supermemory client"""
    global _supermemory_client
    if _supermemory_client is None:
        api_key = os.getenv('SUPERMEMORY_API_KEY')
        if not api_key:
            logging.warning("SUPERMEMORY_API_KEY not set - memory features disabled")
            return None
        try:
            from supermemory import Supermemory
            _supermemory_client = Supermemory()
            logging.info("Supermemory client initialized")
        except ImportError:
            logging.error("supermemory package not installed. Run: pip install supermemory")
            return None
        except Exception as e:
            logging.error(f"Failed to initialize Supermemory: {e}")
            return None
    return _supermemory_client


class MemoryManager:
    """
    Manages long-term memory and skill sharing via Supermemory.
    
    Container tags:
        - user_id: Personal memory for each user
        - SKILLS_TAG: Shared executable skills
        - KNOWLEDGE_TAG: Shared knowledge/facts
    """
    
    SKILLS_TAG = "aura_skills"      # Shared skills pool
    KNOWLEDGE_TAG = "aura_global"   # Shared knowledge pool
    
    def __init__(self, user_id: str = None):
        """
        Initialize MemoryManager.
        
        Args:
            user_id: Unique user identifier. Defaults to AURA_USER_ID env var
                     or machine-based ID.
        """
        self.user_id = user_id or self._get_default_user_id()
        self._enabled = bool(os.getenv('SUPERMEMORY_API_KEY'))
        
        if self._enabled:
            logging.info(f"MemoryManager initialized for user: {self.user_id}")
        else:
            logging.info("MemoryManager running in offline mode (no API key)")
    
    def _get_default_user_id(self) -> str:
        """Get default user ID from environment or generate one"""
        # Try environment variable first
        user_id = os.getenv('AURA_USER_ID')
        if user_id:
            return user_id
        
        # Fall back to machine-based ID
        try:
            import uuid
            return f"user_{uuid.getnode()}"
        except:
            return "default_user"
    
    @property
    def client(self):
        """Get Supermemory client"""
        return _get_client()
    
    @property
    def is_enabled(self) -> bool:
        """Check if memory features are enabled"""
        return self._enabled and self.client is not None
    
    # ═══════════════════════════════════════════════════════════════
    # PERSONAL MEMORY
    # ═══════════════════════════════════════════════════════════════
    
    def add_personal(self, content: str) -> bool:
        """
        Store personal memory for this user.
        
        Args:
            content: Text to remember (facts, preferences, etc.)
            
        Returns:
            True if stored successfully
        """
        if not self.is_enabled:
            logging.debug("Memory disabled - skipping add_personal")
            return False
        
        try:
            self.client.add(content=content, container_tags=[self.user_id])
            logging.info(f"Stored personal memory: {content[:50]}...")
            return True
        except Exception as e:
            logging.error(f"Failed to store personal memory: {e}")
            return False
    
    def search_personal(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search personal memories.
        
        Args:
            query: Search query
            limit: Max results to return
            
        Returns:
            List of matching memories
        """
        if not self.is_enabled:
            return []
        
        try:
            results = self.client.search.memories(q=query, container_tag=self.user_id, limit=limit)
            # Results come back in results.results, not results.memories
            items = results.results if results and hasattr(results, 'results') else []
            return items
        except Exception as e:
            logging.error(f"Failed to search personal memory: {e}")
            return []
    
    def get_user_profile(self, query: str = "") -> Dict[str, Any]:
        """
        Get user profile (static + dynamic context).
        
        Args:
            query: Optional query to focus the profile retrieval
            
        Returns:
            Dict with 'static' and 'dynamic' profile info
        """
        if not self.is_enabled:
            return {"static": [], "dynamic": [], "memories": []}
        
        try:
            profile = self.client.profile(container_tag=self.user_id, q=query)
            return {
                "static": profile.profile.static if profile.profile else [],
                "dynamic": profile.profile.dynamic if profile.profile else [],
                "memories": [r.get("memory", "") for r in profile.search_results.results] if profile.search_results else []
            }
        except Exception as e:
            logging.error(f"Failed to get user profile: {e}")
            return {"static": [], "dynamic": [], "memories": []}
    
    # ═══════════════════════════════════════════════════════════════
    # SHARED KNOWLEDGE
    # ═══════════════════════════════════════════════════════════════
    
    def add_shared_knowledge(self, content: str) -> bool:
        """
        Store shared knowledge accessible by all users.
        
        Args:
            content: Knowledge to share (tips, how-tos, facts)
            
        Returns:
            True if stored successfully
        """
        if not self.is_enabled:
            return False
        
        try:
            # Add metadata about who contributed
            enriched = f"[Contributed by {self.user_id}] {content}"
            self.client.add(content=enriched, container_tags=[self.KNOWLEDGE_TAG])
            logging.info(f"Stored shared knowledge: {content[:50]}...")
            return True
        except Exception as e:
            logging.error(f"Failed to store shared knowledge: {e}")
            return False
    
    def search_shared(self, query: str, limit: int = 5) -> List[Dict]:
        """
        Search shared knowledge.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching knowledge entries
        """
        if not self.is_enabled:
            return []
        
        try:
            results = self.client.search.memories(q=query, container_tag=self.KNOWLEDGE_TAG, limit=limit)
            items = results.results if results and hasattr(results, 'results') else []
            return items
        except Exception as e:
            logging.error(f"Failed to search shared knowledge: {e}")
            return []
    
    # ═══════════════════════════════════════════════════════════════
    # SHARED SKILLS (Executable Code)
    # ═══════════════════════════════════════════════════════════════
    
    def add_skill(self, skill_name: str, code: str, triggers: List[str], 
                  description: str = "") -> bool:
        """
        Store a learned skill for all users.
        
        Args:
            skill_name: Function name
            code: Executable Python code
            triggers: List of command phrases that trigger this skill
            description: What the skill does
            
        Returns:
            True if stored successfully
        """
        if not self.is_enabled:
            return False
        
        try:
            # Create searchable content (this gets summarized by Supermemory)
            searchable_content = f"Skill: {skill_name}. Triggers: {', '.join(triggers)}. {description}"
            
            # Store code in metadata (this is preserved exactly)
            self.client.add(
                content=searchable_content,
                container_tag=self.SKILLS_TAG,
                metadata={
                    "type": "skill",
                    "skill_name": skill_name,
                    "skill_code": code,
                    "triggers": json.dumps(triggers),
                    "description": description,
                    "created_by": self.user_id
                }
            )
            logging.info(f"Stored shared skill: {skill_name}")
            return True
        except Exception as e:
            logging.error(f"Failed to store skill: {e}")
            return False
    
    def search_skill(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Find a shared skill by command phrase.
        
        Args:
            query: Command phrase to search for
            
        Returns:
            Skill dict with 'name', 'code', 'triggers' or None
        """
        if not self.is_enabled:
            return None
        
        try:
            results = self.client.search.memories(
                q=query, 
                container_tag=self.SKILLS_TAG,
                limit=5,
                rerank=True
            )
            
            # Skills are in results.results
            items = results.results if results and hasattr(results, 'results') else []
            if not items:
                return None
            
            # Find first valid skill from metadata
            for item in items:
                try:
                    metadata = getattr(item, 'metadata', None)
                    if not metadata:
                        continue
                    
                    # Check if this is a skill
                    if metadata.get('type') == 'skill' and metadata.get('skill_code'):
                        # Reconstruct skill data from metadata
                        triggers = metadata.get('triggers', '[]')
                        if isinstance(triggers, str):
                            triggers = json.loads(triggers)
                        
                        return {
                            'name': metadata.get('skill_name', ''),
                            'code': metadata.get('skill_code', ''),
                            'triggers': triggers,
                            'description': metadata.get('description', ''),
                            'created_by': metadata.get('created_by', '')
                        }
                except (json.JSONDecodeError, TypeError, AttributeError) as e:
                    logging.debug(f"Error parsing skill metadata: {e}")
                    continue
            
            return None
        except Exception as e:
            logging.error(f"Failed to search skills: {e}")
            return None
    
    # ═══════════════════════════════════════════════════════════════
    # COMBINED CONTEXT
    # ═══════════════════════════════════════════════════════════════
    
    def get_context(self, query: str) -> Dict[str, Any]:
        """
        Get combined context from all memory layers.
        
        Args:
            query: Current user query
            
        Returns:
            Dict with personal profile, shared knowledge, and relevant skills
        """
        return {
            "personal": self.get_user_profile(query),
            "shared": self.search_shared(query, limit=3),
            "skills": self.search_skill(query)
        }
    
    def build_context_prompt(self, query: str) -> str:
        """
        Build a context string for LLM prompts.
        
        Args:
            query: Current user query
            
        Returns:
            Formatted context string to include in prompts
        """
        if not self.is_enabled:
            return ""
        
        context = self.get_context(query)
        parts = []
        
        # User profile
        profile = context.get("personal", {})
        if profile.get("static") or profile.get("dynamic"):
            parts.append("USER CONTEXT:")
            if profile.get("static"):
                parts.append(f"  Facts: {', '.join(profile['static'][:3])}")
            if profile.get("dynamic"):
                parts.append(f"  Recent: {', '.join(profile['dynamic'][:3])}")
        
        # Shared knowledge
        shared = context.get("shared", [])
        if shared:
            tips = [s.get("content", s.get("memory", ""))[:100] for s in shared[:2]]
            parts.append(f"COMMUNITY TIPS: {'; '.join(tips)}")
        
        return "\n".join(parts) if parts else ""


# Global instance (lazy initialization)
_memory_manager = None


def get_memory_manager(user_id: str = None) -> MemoryManager:
    """Get or create the global MemoryManager instance"""
    global _memory_manager
    if _memory_manager is None:
        _memory_manager = MemoryManager(user_id)
    return _memory_manager
