"""
Engagement handler for processing user engagement with content.
"""
from typing import Dict, Any, Optional

from src.feedback.metrics import EngagementMetrics
from src.feedback.attention import AttentionTracker
from src.content.generator import ContentGenerator

class EngagementHandler:
    """
    Class for handling user engagement with content.
    """
    def __init__(self, metrics: EngagementMetrics, content_generator: ContentGenerator):
        """
        Initialize the engagement handler.
        
        Args:
            metrics: The engagement metrics to use
            content_generator: The content generator to use for feedback
        """
        self.metrics = metrics
        self.content_generator = content_generator
        self.attention_tracker = AttentionTracker()
    
    def start_viewing(self, content_id: str) -> None:
        """
        Start tracking attention for a piece of content.
        
        Args:
            content_id: The ID of the content being viewed
        """
        self.attention_tracker.start_viewing(content_id)
    
    def stop_viewing(self) -> Dict[str, Any]:
        """
        Stop tracking attention and record the view.
        
        Returns:
            Dictionary with content_id and view_time
        """
        result = self.attention_tracker.stop_viewing()
        
        if result["content_id"]:
            # Record the view
            self.metrics.record_view(result["content_id"], result["view_time"])
        
        return result
    
    def pause_attention(self) -> None:
        """
        Pause attention tracking.
        """
        self.attention_tracker.pause()
    
    def resume_attention(self) -> None:
        """
        Resume attention tracking.
        """
        self.attention_tracker.resume()
    
    def record_like(self, content_id: str, agent_id: str) -> None:
        """
        Record a like for a piece of content.
        
        Args:
            content_id: The ID of the content
            agent_id: The ID of the agent that created the content
        """
        # Record the like
        self.metrics.record_like(content_id)
        
        # Get current view time
        view_time = 0.0
        if self.attention_tracker.current_content_id == content_id:
            view_time = self.attention_tracker.get_current_view_time()
        
        # Process feedback
        self._process_feedback(content_id, agent_id, view_time, 1)
    
    def record_skip(self, content_id: str, agent_id: str) -> None:
        """
        Record a skip for a piece of content.
        
        Args:
            content_id: The ID of the content
            agent_id: The ID of the agent that created the content
        """
        # Get current view time
        view_time = 0.0
        if self.attention_tracker.current_content_id == content_id:
            view_time = self.attention_tracker.get_current_view_time()
            
            # Stop viewing
            self.attention_tracker.stop_viewing()
        
        # Process feedback (skip is neutral, so 0 likes)
        self._process_feedback(content_id, agent_id, view_time, 0)
    
    def _process_feedback(self, content_id: str, agent_id: str, view_time: float, likes: int) -> None:
        """
        Process feedback for a piece of content.
        
        Args:
            content_id: The ID of the content
            agent_id: The ID of the agent that created the content
            view_time: The time spent viewing the content
            likes: The number of likes
        """
        # Create metrics
        metrics = {
            "view_time": view_time,
            "likes": likes
        }
        
        # Send feedback to content generator
        self.content_generator.process_feedback(content_id, agent_id, metrics)
    
    def adapt_agents(self) -> None:
        """
        Adapt all agents based on feedback.
        """
        self.content_generator.adapt_agents() 