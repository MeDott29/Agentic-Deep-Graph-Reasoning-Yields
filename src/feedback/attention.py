"""
Attention tracker for measuring user engagement with content.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import time

class AttentionTracker:
    """
    Class for tracking user attention to content.
    """
    def __init__(self):
        """
        Initialize the attention tracker.
        """
        self.current_content_id = None
        self.view_start_time = None
        self.active = False
        self.paused = False
        self.pause_start_time = None
        self.total_pause_time = 0.0
        
    def start_viewing(self, content_id: str) -> None:
        """
        Start tracking attention for a piece of content.
        
        Args:
            content_id: The ID of the content being viewed
        """
        # If already tracking, stop tracking the previous content
        if self.active and self.current_content_id:
            self.stop_viewing()
        
        self.current_content_id = content_id
        self.view_start_time = time.time()
        self.active = True
        self.paused = False
        self.total_pause_time = 0.0
        
    def pause(self) -> None:
        """
        Pause attention tracking (e.g., when user switches tabs).
        """
        if self.active and not self.paused:
            self.paused = True
            self.pause_start_time = time.time()
    
    def resume(self) -> None:
        """
        Resume attention tracking after a pause.
        """
        if self.active and self.paused:
            pause_duration = time.time() - self.pause_start_time
            self.total_pause_time += pause_duration
            self.paused = False
    
    def stop_viewing(self) -> Dict[str, Any]:
        """
        Stop tracking attention and return the metrics.
        
        Returns:
            Dictionary with content_id and view_time
        """
        if not self.active or not self.current_content_id:
            return {"content_id": None, "view_time": 0.0}
        
        # If paused, resume first
        if self.paused:
            self.resume()
        
        # Calculate view time
        end_time = time.time()
        total_time = end_time - self.view_start_time
        view_time = max(0.0, total_time - self.total_pause_time)
        
        # Create result
        result = {
            "content_id": self.current_content_id,
            "view_time": view_time
        }
        
        # Reset tracker
        self.current_content_id = None
        self.view_start_time = None
        self.active = False
        self.paused = False
        self.total_pause_time = 0.0
        
        return result
    
    def get_current_view_time(self) -> float:
        """
        Get the current view time without stopping tracking.
        
        Returns:
            Current view time in seconds
        """
        if not self.active or not self.current_content_id:
            return 0.0
        
        current_time = time.time()
        
        if self.paused:
            # If paused, calculate up to pause time
            total_time = self.pause_start_time - self.view_start_time
        else:
            # If not paused, calculate up to current time
            total_time = current_time - self.view_start_time
        
        return max(0.0, total_time - self.total_pause_time) 