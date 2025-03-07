from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, Field
from datetime import datetime

from .base import DBModel

class NodeType(BaseModel):
    """Enum for node types in the knowledge graph."""
    type: Literal["user", "content", "topic", "hashtag"]

class EdgeType(BaseModel):
    """Enum for edge types in the knowledge graph."""
    type: Literal[
        "created", "viewed", "liked", "shared", "commented", 
        "follows", "references", "tagged", "related"
    ]

class Node(NodeType, DBModel):
    """Model for nodes in the knowledge graph."""
    entity_id: str  # ID of the entity (user, content, etc.)
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "node_123",
                "type": "content",
                "entity_id": "content_456",
                "properties": {
                    "title": "Example Content",
                    "engagement_score": 0.85
                },
                "created_at": "2023-09-01T12:00:00",
                "updated_at": "2023-09-01T12:00:00"
            }
        }

class Edge(EdgeType, DBModel):
    """Model for edges in the knowledge graph."""
    source_id: str  # ID of the source node
    target_id: str  # ID of the target node
    weight: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        json_schema_extra = {
            "example": {
                "id": "edge_123",
                "type": "viewed",
                "source_id": "user_123",
                "target_id": "content_456",
                "weight": 0.75,
                "properties": {
                    "view_duration": 120,
                    "view_completion": 0.9
                },
                "created_at": "2023-09-01T12:00:00",
                "updated_at": "2023-09-01T12:00:00"
            }
        }

class GraphTopology(BaseModel):
    """Model for graph topology data."""
    nodes: List[Node]
    edges: List[Edge]
    
class GraphMetrics(BaseModel):
    """Model for graph analytics metrics."""
    node_count: int
    edge_count: int
    avg_node_degree: float
    clustering_coefficient: float
    connected_components: int
    
class TopicCluster(BaseModel):
    """Model for topic clusters in the graph."""
    id: str
    name: str
    size: int
    central_nodes: List[str]
    related_topics: List[str]
    
class BridgeNode(BaseModel):
    """Model for bridge nodes connecting different clusters."""
    id: str
    type: str
    entity_id: str
    connected_clusters: List[str]
    betweenness_centrality: float
    
class EmergingTopic(BaseModel):
    """Model for emerging topics based on attention patterns."""
    topic: str
    growth_rate: float
    related_hashtags: List[str]
    key_content: List[str]
    
class ContentRecommendation(BaseModel):
    """Model for content recommendations."""
    content_id: str
    score: float
    reason: str 