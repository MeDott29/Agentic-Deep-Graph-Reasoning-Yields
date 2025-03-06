"""
Node classes for the knowledge graph.
"""
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime

class Node:
    """
    Base class for all nodes in the knowledge graph.
    """
    def __init__(self, name: str, node_type: str):
        """
        Initialize a new node.
        
        Args:
            name: The name of the node
            node_type: The type of the node
        """
        self.id = str(uuid.uuid4())
        self.name = name
        self.node_type = node_type
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at
        self.properties = {}
        
    def update_property(self, key: str, value: Any) -> None:
        """
        Update a property of the node.
        
        Args:
            key: The property key
            value: The property value
        """
        self.properties[key] = value
        self.updated_at = datetime.now().isoformat()
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the node to a dictionary.
        
        Returns:
            Dictionary representation of the node
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.node_type,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "properties": self.properties
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """
        Create a node from a dictionary.
        
        Args:
            data: Dictionary representation of the node
            
        Returns:
            A new node instance
        """
        node = cls(data["name"], data["type"])
        node.id = data["id"]
        node.created_at = data["created_at"]
        node.updated_at = data["updated_at"]
        node.properties = data["properties"]
        return node


class TopicNode(Node):
    """
    Node representing a topic in the knowledge graph.
    """
    def __init__(self, name: str, categories: List[str] = None):
        """
        Initialize a new topic node.
        
        Args:
            name: The name of the topic
            categories: List of categories the topic belongs to
        """
        super().__init__(name, "topic")
        self.properties["categories"] = categories or []
        self.properties["engagement_score"] = 0.0
        self.properties["trending_score"] = 0.0
        self.properties["complexity"] = 3  # 1-5 scale
        self.properties["entertainment_value"] = 0.0
        
    def update_engagement(self, score: float, agent_id: Optional[str] = None) -> None:
        """
        Update the engagement score for this topic.
        
        Args:
            score: The new engagement score
            agent_id: Optional ID of the agent providing the score
        """
        # Simple exponential moving average
        alpha = 0.3  # Learning rate
        current = self.properties["engagement_score"]
        self.properties["engagement_score"] = (1 - alpha) * current + alpha * score
        self.updated_at = datetime.now().isoformat()
        
        # Track agent-specific scores if provided
        if agent_id:
            agent_scores = self.properties.get("agent_scores", {})
            agent_scores[agent_id] = score
            self.properties["agent_scores"] = agent_scores
            
    def update_trending(self, score: float) -> None:
        """
        Update the trending score for this topic.
        
        Args:
            score: The new trending score
        """
        # Trending score decays faster
        alpha = 0.5  # Higher learning rate for trending
        current = self.properties["trending_score"]
        self.properties["trending_score"] = (1 - alpha) * current + alpha * score
        self.updated_at = datetime.now().isoformat()
        
    def update_complexity(self, level: int, engagement_score: float) -> None:
        """
        Update the complexity level for this topic.
        
        Args:
            level: The complexity level (1-5)
            engagement_score: The engagement score for this complexity level
        """
        # If engagement is higher than current, adjust complexity
        if engagement_score > self.properties["engagement_score"]:
            self.properties["complexity"] = level
            
        self.updated_at = datetime.now().isoformat()
        
    def update_entertainment_value(self, value: float) -> None:
        """
        Update the entertainment value for this topic.
        
        Args:
            value: The entertainment value
        """
        alpha = 0.3
        current = self.properties["entertainment_value"]
        self.properties["entertainment_value"] = (1 - alpha) * current + alpha * value
        self.updated_at = datetime.now().isoformat()


class ContentNode(Node):
    """
    Node representing a piece of content in the knowledge graph.
    """
    def __init__(self, title: str, content_type: str, agent_id: str, agent_name: str):
        """
        Initialize a new content node.
        
        Args:
            title: The title of the content
            content_type: The type of content (text, image, etc.)
            agent_id: The ID of the agent that created the content
            agent_name: The name of the agent that created the content
        """
        super().__init__(title, "content")
        self.properties["content_type"] = content_type
        self.properties["agent_id"] = agent_id
        self.properties["agent_name"] = agent_name
        self.properties["view_count"] = 0
        self.properties["total_view_time"] = 0.0
        self.properties["likes"] = 0
        self.properties["tags"] = []
        
    def record_view(self, view_time: float) -> None:
        """
        Record a view of this content.
        
        Args:
            view_time: The time spent viewing the content (in seconds)
        """
        self.properties["view_count"] += 1
        self.properties["total_view_time"] += view_time
        self.updated_at = datetime.now().isoformat()
        
    def add_like(self) -> None:
        """
        Add a like to this content.
        """
        self.properties["likes"] += 1
        self.updated_at = datetime.now().isoformat()
        
    def add_tag(self, tag: str) -> None:
        """
        Add a tag to this content.
        
        Args:
            tag: The tag to add
        """
        if tag not in self.properties["tags"]:
            self.properties["tags"].append(tag)
            self.updated_at = datetime.now().isoformat()
            
    def get_engagement_metrics(self) -> Dict[str, float]:
        """
        Get engagement metrics for this content.
        
        Returns:
            Dictionary of engagement metrics
        """
        view_count = self.properties["view_count"]
        if view_count == 0:
            return {"avg_view_time": 0, "likes_per_view": 0}
            
        return {
            "avg_view_time": self.properties["total_view_time"] / view_count,
            "likes_per_view": self.properties["likes"] / view_count
        }


class AgentNode(Node):
    """
    Node representing an agent in the knowledge graph.
    """
    def __init__(self, agent_id: str, name: str, personality: str, specialization: List[str]):
        """
        Initialize a new agent node.
        
        Args:
            agent_id: The ID of the agent
            name: The name of the agent
            personality: The personality of the agent
            specialization: List of topics the agent specializes in
        """
        super().__init__(name, "agent")
        self.id = agent_id  # Use the agent's ID
        self.properties["personality"] = personality
        self.properties["specialization"] = specialization
        self.properties["content_count"] = 0
        self.properties["total_engagement"] = 0.0
        self.properties["performance_by_topic"] = {}
        
    def record_content(self, topic: str, engagement_score: float) -> None:
        """
        Record a piece of content created by this agent.
        
        Args:
            topic: The topic of the content
            engagement_score: The engagement score for the content
        """
        self.properties["content_count"] += 1
        self.properties["total_engagement"] += engagement_score
        
        # Track performance by topic
        topic_performance = self.properties["performance_by_topic"]
        if topic in topic_performance:
            # Update with exponential moving average
            alpha = 0.3
            current = topic_performance[topic]
            topic_performance[topic] = (1 - alpha) * current + alpha * engagement_score
        else:
            topic_performance[topic] = engagement_score
            
        self.properties["performance_by_topic"] = topic_performance
        self.updated_at = datetime.now().isoformat()
        
    def get_top_topics(self, limit: int = 3) -> List[str]:
        """
        Get the top performing topics for this agent.
        
        Args:
            limit: Maximum number of topics to return
            
        Returns:
            List of top performing topics
        """
        topic_performance = self.properties["performance_by_topic"]
        if not topic_performance:
            return []
            
        sorted_topics = sorted(
            topic_performance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return [t[0] for t in sorted_topics[:limit]] 