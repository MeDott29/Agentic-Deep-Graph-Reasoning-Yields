"""
Content feed for displaying content to users.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime

from src.content.storage import ContentStorage

class ContentFeed:
    """
    Class for managing the content feed shown to users.
    """
    def __init__(self, content_storage: ContentStorage):
        """
        Initialize the content feed.
        
        Args:
            content_storage: The content storage to use
        """
        self.content_storage = content_storage
        self.current_feed = []
        self.feed_position = 0
        self.feed_size = 10
        self.refresh_feed()
    
    def refresh_feed(self) -> None:
        """
        Refresh the content feed with the latest content.
        """
        self.current_feed = self.content_storage.get_latest_content(limit=self.feed_size)
        self.feed_position = 0
    
    def get_current_item(self) -> Optional[Dict[str, Any]]:
        """
        Get the current item in the feed.
        
        Returns:
            The current content item, or None if the feed is empty
        """
        if not self.current_feed or self.feed_position >= len(self.current_feed):
            return None
        
        return self.current_feed[self.feed_position]
    
    def next_item(self) -> Optional[Dict[str, Any]]:
        """
        Move to the next item in the feed.
        
        Returns:
            The next content item, or None if at the end of the feed
        """
        if self.feed_position < len(self.current_feed) - 1:
            self.feed_position += 1
            return self.current_feed[self.feed_position]
        
        # If we're at the end, try to refresh with new content
        self.refresh_feed()
        
        # If still empty after refresh, return None
        if not self.current_feed:
            return None
        
        return self.current_feed[self.feed_position]
    
    def previous_item(self) -> Optional[Dict[str, Any]]:
        """
        Move to the previous item in the feed.
        
        Returns:
            The previous content item, or None if at the beginning of the feed
        """
        if self.feed_position > 0:
            self.feed_position -= 1
            return self.current_feed[self.feed_position]
        
        return None
    
    def get_feed_preview(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Get a preview of upcoming items in the feed.
        
        Args:
            count: Number of items to preview
            
        Returns:
            List of upcoming content items
        """
        start = self.feed_position + 1
        end = min(start + count, len(self.current_feed))
        
        if start >= end:
            return []
        
        return self.current_feed[start:end]
    
    def filter_by_agent(self, agent_id: str) -> None:
        """
        Filter the feed to only show content from a specific agent.
        
        Args:
            agent_id: The ID of the agent
        """
        self.current_feed = self.content_storage.get_content_by_agent(agent_id)
        self.feed_position = 0
    
    def filter_by_topic(self, topic: str) -> None:
        """
        Filter the feed to only show content about a specific topic.
        
        Args:
            topic: The topic
        """
        self.current_feed = self.content_storage.get_content_by_topic(topic)
        self.feed_position = 0
    
    def clear_filters(self) -> None:
        """
        Clear all filters and show the latest content.
        """
        self.refresh_feed() 