"""
Base Agent class that defines the structure for all agents in the system.
"""
from abc import ABC, abstractmethod
import uuid
from typing import Dict, List, Any, Optional
import random

class Agent(ABC):
    """
    Base class for all autonomous agents in the system.
    """
    def __init__(self, name: str, personality: str, specialization: List[str]):
        """
        Initialize a new agent.
        
        Args:
            name: The name of the agent
            personality: A description of the agent's personality
            specialization: List of topics the agent specializes in
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.personality = personality
        self.specialization = specialization
        self.content_history = []
        self.engagement_metrics = {}
        self.learning_rate = 0.1
        
    @abstractmethod
    def generate_content(self, knowledge_graph: Any) -> Dict[str, Any]:
        """
        Generate content based on the agent's personality and specialization.
        
        Args:
            knowledge_graph: The knowledge graph to use for content generation
            
        Returns:
            A dictionary containing the generated content
        """
        pass
    
    def receive_feedback(self, content_id: str, metrics: Dict[str, float]) -> None:
        """
        Process feedback for a piece of content.
        
        Args:
            content_id: The ID of the content
            metrics: Dictionary of engagement metrics (view_time, likes, etc.)
        """
        if content_id not in self.engagement_metrics:
            self.engagement_metrics[content_id] = {}
            
        # Update metrics
        for key, value in metrics.items():
            if key in self.engagement_metrics[content_id]:
                # Apply learning rate to update the metric
                self.engagement_metrics[content_id][key] = (
                    (1 - self.learning_rate) * self.engagement_metrics[content_id][key] +
                    self.learning_rate * value
                )
            else:
                self.engagement_metrics[content_id][key] = value
    
    def adapt_strategy(self, knowledge_graph: Any) -> None:
        """
        Adapt the agent's content generation strategy based on feedback.
        
        Args:
            knowledge_graph: The knowledge graph to update based on learning
        """
        # This will be implemented by specific agent types
        pass
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Calculate overall performance metrics for this agent.
        
        Returns:
            Dictionary of aggregated metrics
        """
        if not self.engagement_metrics:
            return {"avg_view_time": 0, "avg_likes": 0, "total_content": 0}
        
        total_view_time = 0
        total_likes = 0
        content_count = len(self.engagement_metrics)
        
        for content_metrics in self.engagement_metrics.values():
            total_view_time += content_metrics.get("view_time", 0)
            total_likes += content_metrics.get("likes", 0)
            
        return {
            "avg_view_time": total_view_time / content_count,
            "avg_likes": total_likes / content_count,
            "total_content": content_count
        } 