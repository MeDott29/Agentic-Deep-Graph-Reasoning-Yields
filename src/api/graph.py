from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

from models.user import User
from models.graph import GraphTopology, GraphMetrics, TopicCluster, BridgeNode, EmergingTopic, ContentRecommendation
from services.knowledge_graph import KnowledgeGraphService
from api.users import get_current_user

# Create router
router = APIRouter()

# Initialize knowledge graph service
graph_service = KnowledgeGraphService()

@router.get("/topology", response_model=GraphTopology)
async def get_graph_topology(limit: int = 1000):
    """Get current graph structure."""
    return graph_service.get_topology(limit)

@router.get("/metrics", response_model=GraphMetrics)
async def get_graph_metrics():
    """Get graph analytics and statistics."""
    return graph_service.get_metrics()

@router.get("/hubs", response_model=List[TopicCluster])
async def get_content_hubs(limit: int = 10):
    """Get major content and topic hubs."""
    return graph_service.get_topic_clusters(limit)

@router.get("/bridges", response_model=List[BridgeNode])
async def get_bridge_nodes(limit: int = 10):
    """Get bridge nodes connecting content domains."""
    return graph_service.get_bridge_nodes(limit)

@router.get("/emerging", response_model=List[EmergingTopic])
async def get_emerging_topics(limit: int = 10):
    """Get emerging topics based on attention patterns."""
    return graph_service.get_emerging_topics(limit)

@router.get("/visualization")
async def get_graph_visualization(node_limit: int = 100, include_users: bool = True, include_content: bool = True, include_topics: bool = True):
    """Get graph visualization data."""
    return graph_service.get_visualization_data(node_limit, include_users, include_content, include_topics)

@router.get("/recommendations", response_model=List[ContentRecommendation])
async def get_content_recommendations(limit: int = 10, current_user: Optional[User] = Depends(get_current_user)):
    """Get personalized content recommendations."""
    user_id = current_user.id if current_user else None
    return graph_service.get_recommendations(user_id, limit)

@router.get("/related/{content_id}", response_model=List[ContentRecommendation])
async def get_related_content(content_id: str, limit: int = 10):
    """Get content related to a specific piece of content."""
    return graph_service.get_related_content(content_id, limit)

@router.get("/user-similarity/{user_id}", response_model=List[User])
async def get_similar_users(user_id: str, limit: int = 10):
    """Get users similar to a specific user based on graph analysis."""
    return graph_service.get_similar_users(user_id, limit)

@router.get("/topic-map")
async def get_topic_map(depth: int = 2):
    """Get hierarchical topic map from the knowledge graph."""
    return graph_service.get_topic_map(depth)

@router.get("/content-path")
async def find_content_path(source_id: str, target_id: str):
    """Find the shortest path between two content nodes."""
    return graph_service.find_content_path(source_id, target_id) 