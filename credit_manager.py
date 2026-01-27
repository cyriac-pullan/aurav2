"""
AURA Credit Manager
Manages credit-based API usage tracking for hybrid monetization model
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class CreditManager:
    """
    Manages user credits and subscription status
    
    Free tier: All local commands (no credits needed)
    Paid tier: Credits for Gemini API calls
    Unlimited: Subscription bypasses credit checks
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize credit manager
        
        Args:
            storage_path: Path to store credit data (default: ~/.aura/credits.json)
        """
        if storage_path is None:
            storage_path = os.path.join(
                Path.home(), 
                '.aura', 
                'credits.json'
            )
            
        self.storage_path = storage_path
        self.data = self.load_data()
        
    def load_data(self) -> Dict:
        """Load credit data from storage"""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading credit data: {e}")
                return self.get_default_data()
        else:
            return self.get_default_data()
            
    def get_default_data(self) -> Dict:
        """Get default credit data structure"""
        return {
            "balance": 0,
            "unlimited_subscription": {
                "active": False,
                "expires_at": None,
                "stripe_subscription_id": None
            },
            "usage_history": [],
            "purchase_history": [],
            "stats": {
                "total_commands": 0,
                "local_commands": 0,
                "api_commands": 0,
                "total_credits_purchased": 0,
                "total_credits_used": 0
            }
        }
        
    def save_data(self):
        """Save credit data to storage"""
        try:
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            with open(self.storage_path, 'w') as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving credit data: {e}")
            
    def get_balance(self) -> int:
        """Get current credit balance"""
        return self.data.get("balance", 0)
        
    def add_credits(self, amount: int, package_id: str, transaction_id: str):
        """
        Add credits to user's balance
        
        Args:
            amount: Number of credits to add
            package_id: Package identifier (e.g., 'starter', 'popular')
            transaction_id: Payment transaction ID
        """
        self.data["balance"] = self.data.get("balance", 0) + amount
        self.data["stats"]["total_credits_purchased"] = \
            self.data["stats"].get("total_credits_purchased", 0) + amount
            
        # Record purchase
        purchase = {
            "timestamp": datetime.now().isoformat(),
            "package_id": package_id,
            "amount": amount,
            "transaction_id": transaction_id
        }
        self.data.setdefault("purchase_history", []).append(purchase)
        
        self.save_data()
        logger.info(f"Added {amount} credits. New balance: {self.data['balance']}")
        
    def deduct_credits(self, amount: int = 1, command: str = ""):
        """
        Deduct credits for API usage
        
        Args:
            amount: Number of credits to deduct (default: 1)
            command: The command that used credits
        """
        if self.has_unlimited_subscription():
            # Unlimited subscription - no deduction
            self.record_usage(command, 0, unlimited=True)
            return True
            
        if self.data["balance"] < amount:
            logger.warning(f"Insufficient credits. Required: {amount}, Available: {self.data['balance']}")
            return False
            
        self.data["balance"] -= amount
        self.data["stats"]["total_credits_used"] = \
            self.data["stats"].get("total_credits_used", 0) + amount
            
        self.record_usage(command, amount)
        self.save_data()
        
        return True
        
    def check_credits(self, required: int = 1) -> bool:
        """
        Check if user has enough credits
        
        Args:
            required: Number of credits required
            
        Returns:
            True if user has enough credits or unlimited subscription
        """
        if self.has_unlimited_subscription():
            return True
            
        return self.data["balance"] >= required
        
    def record_usage(self, command: str, credits_used: int, unlimited: bool = False):
        """
        Record command usage for analytics
        
        Args:
            command: The command executed
            credits_used: Credits used (0 for local commands)
            unlimited: Whether unlimited subscription was used
        """
        usage = {
            "timestamp": datetime.now().isoformat(),
            "command": command,
            "credits_used": credits_used,
            "unlimited": unlimited,
            "balance_after": self.data["balance"]
        }
        
        self.data.setdefault("usage_history", []).append(usage)
        
        # Update stats
        self.data["stats"]["total_commands"] = \
            self.data["stats"].get("total_commands", 0) + 1
            
        if credits_used == 0 and not unlimited:
            self.data["stats"]["local_commands"] = \
                self.data["stats"].get("local_commands", 0) + 1
        else:
            self.data["stats"]["api_commands"] = \
                self.data["stats"].get("api_commands", 0) + 1
                
        # Keep only last 1000 usage records
        if len(self.data["usage_history"]) > 1000:
            self.data["usage_history"] = self.data["usage_history"][-1000:]
            
        self.save_data()
        
    def has_unlimited_subscription(self) -> bool:
        """Check if user has active unlimited subscription"""
        sub = self.data.get("unlimited_subscription", {})
        
        if not sub.get("active", False):
            return False
            
        # Check expiration
        expires_at = sub.get("expires_at")
        if expires_at:
            expiry = datetime.fromisoformat(expires_at)
            if datetime.now() > expiry:
                # Subscription expired
                self.data["unlimited_subscription"]["active"] = False
                self.save_data()
                return False
                
        return True
        
    def activate_unlimited_subscription(
        self, 
        subscription_id: str, 
        expires_at: Optional[datetime] = None
    ):
        """
        Activate unlimited subscription
        
        Args:
            subscription_id: Stripe subscription ID
            expires_at: Expiration date (None for monthly recurring)
        """
        self.data["unlimited_subscription"] = {
            "active": True,
            "expires_at": expires_at.isoformat() if expires_at else None,
            "stripe_subscription_id": subscription_id,
            "activated_at": datetime.now().isoformat()
        }
        
        self.save_data()
        logger.info("Unlimited subscription activated")
        
    def cancel_unlimited_subscription(self):
        """Cancel unlimited subscription"""
        self.data["unlimited_subscription"]["active"] = False
        self.save_data()
        logger.info("Unlimited subscription cancelled")
        
    def get_usage_stats(self) -> Dict:
        """Get usage statistics"""
        stats = self.data.get("stats", {})
        
        # Calculate percentages
        total = stats.get("total_commands", 0)
        local = stats.get("local_commands", 0)
        api = stats.get("api_commands", 0)
        
        local_percentage = (local / total * 100) if total > 0 else 0
        
        return {
            "balance": self.data["balance"],
            "unlimited_active": self.has_unlimited_subscription(),
            "total_commands": total,
            "local_commands": local,
            "api_commands": api,
            "local_percentage": round(local_percentage, 1),
            "total_credits_purchased": stats.get("total_credits_purchased", 0),
            "total_credits_used": stats.get("total_credits_used", 0),
            "credits_remaining": self.data["balance"]
        }
        
    def get_recent_usage(self, limit: int = 10) -> List[Dict]:
        """
        Get recent usage history
        
        Args:
            limit: Number of recent records to return
            
        Returns:
            List of recent usage records
        """
        history = self.data.get("usage_history", [])
        return history[-limit:]
        
    def should_show_low_balance_warning(self) -> bool:
        """Check if low balance warning should be shown"""
        if self.has_unlimited_subscription():
            return False
            
        threshold = 100  # Show warning below 100 credits
        return self.data["balance"] < threshold and self.data["balance"] > 0
        
    def reset_balance(self, new_balance: int = 0):
        """
        Reset credit balance (for testing/admin purposes)
        
        Args:
            new_balance: New balance to set
        """
        logger.warning(f"Resetting balance from {self.data['balance']} to {new_balance}")
        self.data["balance"] = new_balance
        self.save_data()


# Singleton instance
_credit_manager_instance = None


def get_credit_manager() -> CreditManager:
    """Get global credit manager instance"""
    global _credit_manager_instance
    if _credit_manager_instance is None:
        _credit_manager_instance = CreditManager()
    return _credit_manager_instance


if __name__ == "__main__":
    # Test credit manager
    logging.basicConfig(level=logging.INFO)
    
    cm = CreditManager()
    
    print("Credit Manager Test")
    print("=" * 50)
    print(f"Current balance: {cm.get_balance()}")
    print(f"Has unlimited: {cm.has_unlimited_subscription()}")
    
    # Simulate purchase
    cm.add_credits(1000, "starter", "test_txn_123")
    print(f"After purchase: {cm.get_balance()}")
    
    # Simulate usage
    cm.record_usage("set brightness to 50", 0)  # Local command
    cm.deduct_credits(1, "what is AI?")  # API command
    
    # Stats
    stats = cm.get_usage_stats()
    print("\nUsage Stats:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
