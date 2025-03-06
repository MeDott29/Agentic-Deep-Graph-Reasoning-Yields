"""
Engagement metrics for tracking user engagement with content.
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import os

class EngagementMetrics:
    """
    Class for tracking user engagement with content.
    """
    def __init__(self, metrics_path: str = None):
        """
        Initialize engagement metrics.
        
        Args:
            metrics_path: Path to the metrics data file
        """
        self.metrics_path = metrics_path or os.getenv("METRICS_PATH", "./data/metrics.json")
        self.metrics = {}
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.metrics_path), exist_ok=True)
        
        # Load metrics if they exist
        if os.path.exists(self.metrics_path):
            self.load()
    
    def record_view(self, content_id: str, view_time: float) -> None:
        """
        Record a view of content.
        
        Args:
            content_id: The ID of the content
            view_time: The time spent viewing the content (in seconds)
        """
        if content_id not in self.metrics:
            self.metrics[content_id] = {
                "views": 0,
                "total_view_time": 0.0,
                "likes": 0,
                "last_viewed": None,
                "history": []
            }
        
        self.metrics[content_id]["views"] += 1
        self.metrics[content_id]["total_view_time"] += view_time
        self.metrics[content_id]["last_viewed"] = datetime.now().isoformat()
        
        # Add to history
        self.metrics[content_id]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "view",
            "view_time": view_time
        })
        
        # Save metrics
        self.save()
    
    def record_like(self, content_id: str) -> None:
        """
        Record a like for content.
        
        Args:
            content_id: The ID of the content
        """
        if content_id not in self.metrics:
            self.metrics[content_id] = {
                "views": 0,
                "total_view_time": 0.0,
                "likes": 0,
                "last_viewed": None,
                "history": []
            }
        
        self.metrics[content_id]["likes"] += 1
        
        # Add to history
        self.metrics[content_id]["history"].append({
            "timestamp": datetime.now().isoformat(),
            "action": "like"
        })
        
        # Save metrics
        self.save()
    
    def get_content_metrics(self, content_id: str) -> Dict[str, Any]:
        """
        Get metrics for a specific piece of content.
        
        Args:
            content_id: The ID of the content
            
        Returns:
            Dictionary of metrics for the content
        """
        if content_id not in self.metrics:
            return {
                "views": 0,
                "total_view_time": 0.0,
                "avg_view_time": 0.0,
                "likes": 0,
                "likes_per_view": 0.0
            }
        
        metrics = self.metrics[content_id]
        views = metrics["views"]
        
        if views == 0:
            return {
                "views": 0,
                "total_view_time": 0.0,
                "avg_view_time": 0.0,
                "likes": metrics["likes"],
                "likes_per_view": 0.0
            }
        
        return {
            "views": views,
            "total_view_time": metrics["total_view_time"],
            "avg_view_time": metrics["total_view_time"] / views,
            "likes": metrics["likes"],
            "likes_per_view": metrics["likes"] / views
        }
    
    def get_top_content(self, limit: int = 5, metric: str = "avg_view_time") -> List[str]:
        """
        Get the top performing content based on a metric.
        
        Args:
            limit: Maximum number of content IDs to return
            metric: The metric to sort by (avg_view_time, likes, likes_per_view)
            
        Returns:
            List of content IDs
        """
        if not self.metrics:
            return []
        
        # Calculate metrics for all content
        content_metrics = {}
        for content_id, metrics in self.metrics.items():
            views = metrics["views"]
            if views == 0:
                continue
                
            if metric == "avg_view_time":
                content_metrics[content_id] = metrics["total_view_time"] / views
            elif metric == "likes":
                content_metrics[content_id] = metrics["likes"]
            elif metric == "likes_per_view":
                content_metrics[content_id] = metrics["likes"] / views
        
        # Sort by metric
        sorted_content = sorted(
            content_metrics.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [c[0] for c in sorted_content[:limit]]
    
    def save(self) -> None:
        """
        Save metrics to a file.
        """
        with open(self.metrics_path, 'w') as f:
            json.dump(self.metrics, f, indent=2)
    
    def load(self) -> None:
        """
        Load metrics from a file.
        """
        if not os.path.exists(self.metrics_path):
            return
            
        with open(self.metrics_path, 'r') as f:
            self.metrics = json.load(f) 