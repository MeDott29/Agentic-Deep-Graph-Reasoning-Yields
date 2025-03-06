"""
Knowledge graph implementation.
"""
from typing import Dict, List, Any, Optional, Set, Tuple
import json
import os
from datetime import datetime
import networkx as nx

from src.knowledge.nodes import Node, TopicNode, ContentNode, AgentNode
from src.knowledge.relationships import Relationship

class KnowledgeGraph:
    """
    Knowledge graph implementation using NetworkX.
    """
    def __init__(self, graph_path: str = None):
        """
        Initialize a new knowledge graph.
        
        Args:
            graph_path: Path to the graph data file
        """
        self.graph = nx.DiGraph()
        self.nodes = {}  # id -> Node
        self.relationships = {}  # id -> Relationship
        self.graph_path = graph_path or os.getenv("GRAPH_DB_PATH", "./data/graph.json")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        
        # Load graph if it exists
        if os.path.exists(self.graph_path):
            self.load()
        else:
            # Initialize with some default topics
            self._initialize_default_topics()
    
    def _initialize_default_topics(self) -> None:
        """
        Initialize the graph with some default topics.
        """
        default_topics = [
            ("Technology", ["science", "technology"]),
            ("Science", ["science"]),
            ("Entertainment", ["entertainment", "pop culture"]),
            ("Sports", ["entertainment"]),
            ("Politics", ["current events"]),
            ("Health", ["science", "health"]),
            ("Environment", ["science", "current events"]),
            ("Business", ["business", "current events"]),
            ("Education", ["education"]),
            ("Art", ["entertainment", "art"])
        ]
        
        for name, categories in default_topics:
            topic = TopicNode(name, categories)
            self.add_node(topic)
            
            # Add some initial trending scores
            topic.update_trending(0.5)
    
    def add_node(self, node: Node) -> str:
        """
        Add a node to the graph.
        
        Args:
            node: The node to add
            
        Returns:
            The ID of the added node
        """
        self.nodes[node.id] = node
        self.graph.add_node(node.id, **node.to_dict())
        return node.id
    
    def add_relationship(self, relationship: Relationship) -> str:
        """
        Add a relationship to the graph.
        
        Args:
            relationship: The relationship to add
            
        Returns:
            The ID of the added relationship
        """
        self.relationships[relationship.id] = relationship
        
        # Extract the relationship data without the id field to avoid duplication
        rel_data = relationship.to_dict()
        
        # Add the edge with the relationship data
        self.graph.add_edge(
            relationship.source_id, 
            relationship.target_id, 
            key=relationship.id,  # Use key instead of id to avoid conflict
            **rel_data
        )
        return relationship.id
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node by ID.
        
        Args:
            node_id: The ID of the node
            
        Returns:
            The node, or None if not found
        """
        return self.nodes.get(node_id)
    
    def get_relationship(self, relationship_id: str) -> Optional[Relationship]:
        """
        Get a relationship by ID.
        
        Args:
            relationship_id: The ID of the relationship
            
        Returns:
            The relationship, or None if not found
        """
        return self.relationships.get(relationship_id)
    
    def get_nodes_by_type(self, node_type: str) -> List[Node]:
        """
        Get all nodes of a specific type.
        
        Args:
            node_type: The type of nodes to get
            
        Returns:
            List of nodes
        """
        return [node for node in self.nodes.values() if node.node_type == node_type]
    
    def get_relationships_by_type(self, relationship_type: str) -> List[Relationship]:
        """
        Get all relationships of a specific type.
        
        Args:
            relationship_type: The type of relationships to get
            
        Returns:
            List of relationships
        """
        return [rel for rel in self.relationships.values() if rel.relationship_type == relationship_type]
    
    def get_relationships_between(self, source_id: str, target_id: str) -> List[Relationship]:
        """
        Get all relationships between two nodes.
        
        Args:
            source_id: The ID of the source node
            target_id: The ID of the target node
            
        Returns:
            List of relationships
        """
        return [
            rel for rel in self.relationships.values() 
            if rel.source_id == source_id and rel.target_id == target_id
        ]
    
    def get_trending_topics(self, limit: int = 5) -> List[str]:
        """
        Get the trending topics.
        
        Args:
            limit: Maximum number of topics to return
            
        Returns:
            List of trending topic names
        """
        topic_nodes = self.get_nodes_by_type("topic")
        
        # Sort by trending score
        sorted_topics = sorted(
            topic_nodes,
            key=lambda x: x.properties["trending_score"],
            reverse=True
        )
        
        return [topic.name for topic in sorted_topics[:limit]]
    
    def get_popular_topics(self, limit: int = 5) -> List[str]:
        """
        Get the most popular topics based on engagement.
        
        Args:
            limit: Maximum number of topics to return
            
        Returns:
            List of popular topic names
        """
        topic_nodes = self.get_nodes_by_type("topic")
        
        # Sort by engagement score
        sorted_topics = sorted(
            topic_nodes,
            key=lambda x: x.properties["engagement_score"],
            reverse=True
        )
        
        return [topic.name for topic in sorted_topics[:limit]]
    
    def get_topics_by_category(self, categories: List[str]) -> List[str]:
        """
        Get topics that belong to any of the specified categories.
        
        Args:
            categories: List of categories
            
        Returns:
            List of topic names
        """
        topic_nodes = self.get_nodes_by_type("topic")
        matching_topics = []
        
        for topic in topic_nodes:
            topic_categories = topic.properties.get("categories", [])
            if any(category in topic_categories for category in categories):
                matching_topics.append(topic.name)
                
        return matching_topics
    
    def update_topic_weight(self, topic_name: str, weight: float, agent_id: str = None) -> None:
        """
        Update the weight of a topic.
        
        Args:
            topic_name: The name of the topic
            weight: The new weight
            agent_id: Optional ID of the agent providing the weight
        """
        # Find the topic node
        topic_node = self._get_or_create_topic(topic_name)
        
        # Update engagement score
        topic_node.update_engagement(weight, agent_id)
        
        # Update trending score (with decay)
        current_time = datetime.now()
        last_updated = datetime.fromisoformat(topic_node.updated_at)
        time_diff = (current_time - last_updated).total_seconds() / 3600  # hours
        
        # Apply time decay (more recent updates have higher trending score)
        decay_factor = max(0.1, 1.0 / (1.0 + 0.1 * time_diff))
        trending_score = weight * decay_factor
        topic_node.update_trending(trending_score)
        
        # If agent_id is provided, update or create relationship
        if agent_id:
            agent_node = self._get_agent_node(agent_id)
            if agent_node:
                # Check if relationship exists
                relationships = self.get_relationships_between(agent_id, topic_node.id)
                if relationships:
                    # Update existing relationship
                    for rel in relationships:
                        if rel.relationship_type == "SPECIALIZES_IN":
                            rel.update_weight(weight)
                else:
                    # Create new relationship
                    rel = Relationship(agent_id, topic_node.id, "SPECIALIZES_IN")
                    rel.update_property("weight", weight)
                    self.add_relationship(rel)
    
    def update_topic_complexity(self, topic_name: str, complexity: int, 
                               engagement_score: float, agent_id: str = None) -> None:
        """
        Update the complexity of a topic.
        
        Args:
            topic_name: The name of the topic
            complexity: The complexity level (1-5)
            engagement_score: The engagement score for this complexity level
            agent_id: Optional ID of the agent providing the complexity
        """
        # Find the topic node
        topic_node = self._get_or_create_topic(topic_name)
        
        # Update complexity
        topic_node.update_complexity(complexity, engagement_score)
        
        # Update engagement score
        topic_node.update_engagement(engagement_score, agent_id)
        
        # If agent_id is provided, update or create relationship
        if agent_id:
            agent_node = self._get_agent_node(agent_id)
            if agent_node:
                # Check if relationship exists
                relationships = self.get_relationships_between(agent_id, topic_node.id)
                if relationships:
                    # Update existing relationship
                    for rel in relationships:
                        if rel.relationship_type == "EXPLAINS":
                            rel.update_property("complexity", complexity)
                            rel.update_weight(engagement_score)
                else:
                    # Create new relationship
                    rel = Relationship(agent_id, topic_node.id, "EXPLAINS")
                    rel.update_property("complexity", complexity)
                    rel.update_property("weight", engagement_score)
                    self.add_relationship(rel)
    
    def update_topic_entertainment_value(self, topic_name: str, value: float, agent_id: str = None) -> None:
        """
        Update the entertainment value of a topic.
        
        Args:
            topic_name: The name of the topic
            value: The entertainment value
            agent_id: Optional ID of the agent providing the value
        """
        # Find the topic node
        topic_node = self._get_or_create_topic(topic_name)
        
        # Update entertainment value
        topic_node.update_entertainment_value(value)
        
        # Update engagement score (entertainment contributes to engagement)
        topic_node.update_engagement(value * 0.7, agent_id)
        
        # If agent_id is provided, update or create relationship
        if agent_id:
            agent_node = self._get_agent_node(agent_id)
            if agent_node:
                # Check if relationship exists
                relationships = self.get_relationships_between(agent_id, topic_node.id)
                if relationships:
                    # Update existing relationship
                    for rel in relationships:
                        if rel.relationship_type == "ENTERTAINS_ABOUT":
                            rel.update_weight(value)
                else:
                    # Create new relationship
                    rel = Relationship(agent_id, topic_node.id, "ENTERTAINS_ABOUT")
                    rel.update_property("weight", value)
                    self.add_relationship(rel)
    
    def record_content_engagement(self, content_id: str, agent_id: str, topic: str, 
                                 view_time: float, likes: int) -> None:
        """
        Record engagement for a piece of content.
        
        Args:
            content_id: The ID of the content
            agent_id: The ID of the agent that created the content
            topic: The topic of the content
            view_time: The time spent viewing the content
            likes: The number of likes
        """
        # Find or create content node
        content_node = self.nodes.get(content_id)
        if not content_node:
            # Get agent info
            agent_node = self._get_agent_node(agent_id)
            if not agent_node:
                return
                
            # Create content node
            content_node = ContentNode(f"Content {content_id}", "text", agent_id, agent_node.name)
            content_node.id = content_id  # Use the provided ID
            self.add_node(content_node)
        
        # Record view and likes
        content_node.record_view(view_time)
        for _ in range(likes):
            content_node.add_like()
        
        # Add topic as tag if not already present
        content_node.add_tag(topic)
        
        # Find or create topic node
        topic_node = self._get_or_create_topic(topic)
        
        # Calculate engagement score
        engagement_score = view_time * 0.7 + likes * 0.3
        
        # Update topic engagement
        topic_node.update_engagement(engagement_score, agent_id)
        
        # Update agent performance
        agent_node = self._get_agent_node(agent_id)
        if agent_node:
            agent_node.record_content(topic, engagement_score)
        
        # Create or update relationships
        
        # Content ABOUT Topic
        content_topic_rels = self.get_relationships_between(content_id, topic_node.id)
        if content_topic_rels:
            for rel in content_topic_rels:
                if rel.relationship_type == "ABOUT":
                    rel.update_weight(engagement_score)
        else:
            rel = Relationship(content_id, topic_node.id, "ABOUT")
            rel.update_property("weight", engagement_score)
            self.add_relationship(rel)
        
        # Agent CREATED Content
        agent_content_rels = self.get_relationships_between(agent_id, content_id)
        if not agent_content_rels:
            rel = Relationship(agent_id, content_id, "CREATED")
            self.add_relationship(rel)
    
    def save(self) -> None:
        """
        Save the graph to a file.
        """
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "relationships": [rel.to_dict() for rel in self.relationships.values()]
        }
        
        with open(self.graph_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load(self) -> None:
        """
        Load the graph from a file.
        """
        if not os.path.exists(self.graph_path):
            return
            
        with open(self.graph_path, 'r') as f:
            data = json.load(f)
        
        # Clear existing data
        self.nodes = {}
        self.relationships = {}
        self.graph = nx.DiGraph()
        
        # Load nodes
        for node_data in data.get("nodes", []):
            node_type = node_data["type"]
            
            if node_type == "topic":
                node = TopicNode(node_data["name"])
            elif node_type == "content":
                node = ContentNode(
                    node_data["name"],
                    node_data["properties"].get("content_type", "text"),
                    node_data["properties"].get("agent_id", ""),
                    node_data["properties"].get("agent_name", "")
                )
            elif node_type == "agent":
                node = AgentNode(
                    node_data["id"],
                    node_data["name"],
                    node_data["properties"].get("personality", ""),
                    node_data["properties"].get("specialization", [])
                )
            else:
                node = Node(node_data["name"], node_type)
                
            node.id = node_data["id"]
            node.created_at = node_data["created_at"]
            node.updated_at = node_data["updated_at"]
            node.properties = node_data["properties"]
            
            self.add_node(node)
        
        # Load relationships
        for rel_data in data.get("relationships", []):
            rel = Relationship(
                rel_data["source_id"],
                rel_data["target_id"],
                rel_data["type"]
            )
            rel.id = rel_data["id"]
            rel.created_at = rel_data["created_at"]
            rel.updated_at = rel_data["updated_at"]
            rel.properties = rel_data["properties"]
            
            self.add_relationship(rel)
    
    def _get_or_create_topic(self, topic_name: str) -> TopicNode:
        """
        Get a topic node by name, or create it if it doesn't exist.
        
        Args:
            topic_name: The name of the topic
            
        Returns:
            The topic node
        """
        # Find the topic node
        topic_nodes = [node for node in self.nodes.values() 
                      if node.node_type == "topic" and node.name == topic_name]
        
        if topic_nodes:
            return topic_nodes[0]
        
        # Create new topic node
        topic_node = TopicNode(topic_name)
        self.add_node(topic_node)
        return topic_node
    
    def _get_agent_node(self, agent_id: str) -> Optional[AgentNode]:
        """
        Get an agent node by ID.
        
        Args:
            agent_id: The ID of the agent
            
        Returns:
            The agent node, or None if not found
        """
        node = self.nodes.get(agent_id)
        if node and node.node_type == "agent":
            return node
        return None 