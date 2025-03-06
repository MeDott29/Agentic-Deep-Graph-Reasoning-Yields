"""
Content storage for storing and retrieving content.
"""
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

class ContentStorage:
    """
    Class for storing and retrieving content.
    """
    def __init__(self, content_path: str = None):
        """
        Initialize the content storage.
        
        Args:
            content_path: Path to the content data file
        """
        self.content_path = content_path or os.getenv("CONTENT_DB_PATH", "./data/content.json")
        self.content = {}
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.content_path), exist_ok=True)
        
        # Load content if it exists
        if os.path.exists(self.content_path):
            self.load()
    
    def store_content(self, content: Dict[str, Any]) -> str:
        """
        Store a piece of content.
        
        Args:
            content: The content to store
            
        Returns:
            The ID of the stored content
        """
        content_id = content["id"]
        self.content[content_id] = content
        
        # Add timestamp if not present
        if "timestamp" not in content:
            content["timestamp"] = datetime.now().isoformat()
        
        # Save content
        self.save()
        
        return content_id
    
    def get_content(self, content_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a piece of content by ID.
        
        Args:
            content_id: The ID of the content
            
        Returns:
            The content, or None if not found
        """
        return self.content.get(content_id)
    
    def get_all_content(self) -> List[Dict[str, Any]]:
        """
        Get all content.
        
        Returns:
            List of all content
        """
        return list(self.content.values())
    
    def get_content_by_agent(self, agent_id: str) -> List[Dict[str, Any]]:
        """
        Get all content created by a specific agent.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            List of content created by the agent
        """
        return [c for c in self.content.values() if c.get("agent_id") == agent_id]
    
    def get_content_by_topic(self, topic: str) -> List[Dict[str, Any]]:
        """
        Get all content about a specific topic.
        
        Args:
            topic: The topic
            
        Returns:
            List of content about the topic
        """
        return [c for c in self.content.values() if c.get("topic") == topic]
    
    def get_latest_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the latest content.
        
        Args:
            limit: Maximum number of content items to return
            
        Returns:
            List of latest content
        """
        sorted_content = sorted(
            self.content.values(),
            key=lambda x: x.get("timestamp", ""),
            reverse=True
        )
        
        return sorted_content[:limit]
    
    def delete_content(self, content_id: str) -> bool:
        """
        Delete a piece of content.
        
        Args:
            content_id: The ID of the content
            
        Returns:
            True if the content was deleted, False otherwise
        """
        if content_id in self.content:
            del self.content[content_id]
            self.save()
            return True
        return False
    
    def save(self) -> None:
        """
        Save content to a file.
        """
        with open(self.content_path, 'w') as f:
            json.dump(self.content, f, indent=2)
    
    def load(self) -> None:
        """
        Load content from a file.
        """
        if not os.path.exists(self.content_path):
            return
            
        with open(self.content_path, 'r') as f:
            self.content = json.load(f) 