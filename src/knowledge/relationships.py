"""
Relationship class for the knowledge graph.
"""
from typing import Dict, Any, Optional
import uuid
from datetime import datetime

class Relationship:
    """
    Class representing a relationship between two nodes in the knowledge graph.
    """
    def __init__(self, source_id: str, target_id: str, relationship_type: str):
        """
        Initialize a new relationship.
        
        Args:
            source_id: The ID of the source node
            target_id: The ID of the target node
            relationship_type: The type of relationship
        """
        self.id = str(uuid.uuid4())
        self.source_id = source_id
        self.target_id = target_id
        self.relationship_type = relationship_type
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.properties = {}
        
    def update_property(self, key: str, value: Any) -> None:
        """
        Update a property of the relationship.
        
        Args:
            key: The property key
            value: The property value
        """
        self.properties[key] = value
        self.updated_at = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the relationship to a dictionary.
        
        Returns:
            Dictionary representation of the relationship
        """
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.relationship_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "properties": self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """
        Create a relationship from a dictionary.
        
        Args:
            data: Dictionary representation of the relationship
            
        Returns:
            A new relationship instance
        """
        relationship = cls(data["source_id"], data["target_id"], data["type"])
        relationship.id = data["id"]
        relationship.created_at = data["created_at"]
        relationship.updated_at = data["updated_at"]
        relationship.properties = data["properties"]
        return relationship
    
    def update_weight(self, weight: float) -> None:
        """
        Update the weight of the relationship.
        
        Args:
            weight: The new weight
        """
        # Use exponential moving average
        alpha = 0.3
        current = self.properties.get("weight", 0.0)
        self.properties["weight"] = (1 - alpha) * current + alpha * weight
        self.updated_at = datetime.now().isoformat()
        
    def increment_count(self, amount: int = 1) -> None:
        """
        Increment the count property of the relationship.
        
        Args:
            amount: The amount to increment by
        """
        count = self.properties.get("count", 0)
        self.properties["count"] = count + amount
        self.updated_at = datetime.now().isoformat() 