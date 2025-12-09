"""In-memory event store for predictions."""
from collections import deque
from datetime import datetime
from typing import List, Dict, Optional


class PredictionStore:
    """In-memory event store for predictions."""
    
    def __init__(self, maxlen: int = 2000):
        """
        Initialize the prediction store.
        
        Args:
            maxlen: Maximum number of events to store (default: 2000)
        """
        self.events = deque(maxlen=maxlen)
    
    def add_event(self, event: Dict):
        """
        Add a prediction event to the store.
        
        Args:
            event: Dictionary containing prediction data. Must include:
                - timestamp (or will be set to current time)
                - src_ip, dst_ip, src_port, dst_port, protocol
                - is_attack, attack_type, binary_confidence, severity
        """
        # Ensure timestamp exists
        if "timestamp" not in event or event["timestamp"] is None:
            event["timestamp"] = datetime.utcnow().isoformat()
        
        # Add event at the left (newest first)
        self.events.appendleft(event)
    
    def get_recent(self, limit: int = 100) -> List[Dict]:
        """
        Get recent prediction events.
        
        Args:
            limit: Maximum number of events to return (default: 100)
            
        Returns:
            List of event dictionaries, newest first
        """
        return list(self.events)[:limit]
    
    def get_all(self) -> List[Dict]:
        """
        Get all stored events.
        
        Returns:
            List of all event dictionaries, newest first
        """
        return list(self.events)
    
    def get_stats(self) -> Dict:
        """
        Compute statistics from stored events.
        
        Returns:
            Dictionary with stats:
                - total_flows: Total number of events
                - total_attacks: Number of attack events
                - attack_ratio: Percentage of attacks
                - attack_type_distribution: Count by attack type
        """
        events = list(self.events)
        total_flows = len(events)
        attacks = [e for e in events if e.get("is_attack", False)]
        total_attacks = len(attacks)
        attack_ratio = (total_attacks / total_flows * 100) if total_flows > 0 else 0.0
        
        # Attack type distribution
        attack_type_dist = {}
        for event in attacks:
            attack_type = event.get("attack_type", "Unknown")
            attack_type_dist[attack_type] = attack_type_dist.get(attack_type, 0) + 1
        
        # Most frequent attack type
        most_frequent = max(attack_type_dist.items(), key=lambda x: x[1])[0] if attack_type_dist else "N/A"
        
        return {
            "total_flows": total_flows,
            "total_attacks": total_attacks,
            "attack_ratio": round(attack_ratio, 2),
            "most_frequent_attack": most_frequent,
            "attack_type_distribution": attack_type_dist,
        }


# Global instance
prediction_store = PredictionStore()

