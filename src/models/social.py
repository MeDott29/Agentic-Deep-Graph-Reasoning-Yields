"""
Social interaction models for the Knowledge Graph Social Network System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import GraphEdge, TimestampMixin

class Follow(GraphEdge):
    """Follow relationship between users"""
    def __init__(self, follower_id: str, followed_id: str):
        super().__init__(
            source_id=follower_id,
            target_id=followed_id,
            edge_type="FOLLOWS",
            properties={
                "created_at": datetime.utcnow().isoformat()
            }
        )

class Like(GraphEdge):
    """Like relationship between a user and content"""
    def __init__(self, user_id: str, content_id: str):
        super().__init__(
            source_id=user_id,
            target_id=content_id,
            edge_type="LIKES",
            properties={
                "created_at": datetime.utcnow().isoformat()
            }
        )

class View(GraphEdge):
    """View relationship between a user and content"""
    def __init__(self, user_id: str, content_id: str, duration: float):
        super().__init__(
            source_id=user_id,
            target_id=content_id,
            edge_type="VIEWS",
            properties={
                "duration": duration,  # How long the user viewed the content
                "percentage_watched": 0.0,  # Will be calculated based on content duration
                "created_at": datetime.utcnow().isoformat()
            }
        )

class Share(GraphEdge):
    """Share relationship between a user and content"""
    def __init__(self, user_id: str, content_id: str, platform: str):
        super().__init__(
            source_id=user_id,
            target_id=content_id,
            edge_type="SHARES",
            properties={
                "platform": platform,  # e.g., "facebook", "twitter", "whatsapp"
                "created_at": datetime.utcnow().isoformat()
            }
        )

class CommentEdge(GraphEdge):
    """Comment relationship between a user and content"""
    def __init__(self, user_id: str, content_id: str, comment_id: str):
        super().__init__(
            source_id=user_id,
            target_id=content_id,
            edge_type="COMMENTS",
            properties={
                "comment_id": comment_id,
                "created_at": datetime.utcnow().isoformat()
            }
        )

class HasTag(GraphEdge):
    """Relationship between content and a hashtag"""
    def __init__(self, content_id: str, hashtag_id: str):
        super().__init__(
            source_id=content_id,
            target_id=hashtag_id,
            edge_type="HAS_TAG",
            properties={
                "created_at": datetime.utcnow().isoformat()
            }
        )

class CreatedBy(GraphEdge):
    """Relationship between content and its creator"""
    def __init__(self, content_id: str, user_id: str):
        super().__init__(
            source_id=content_id,
            target_id=user_id,
            edge_type="CREATED_BY",
            properties={
                "created_at": datetime.utcnow().isoformat()
            }
        )

class InterestIn(GraphEdge):
    """Relationship between a user and a topic/category they're interested in"""
    def __init__(self, user_id: str, topic_id: str, weight: float = 1.0):
        super().__init__(
            source_id=user_id,
            target_id=topic_id,
            edge_type="INTEREST_IN",
            weight=weight,
            properties={
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
        )

class SimilarTo(GraphEdge):
    """Relationship between similar content items"""
    def __init__(self, content_id1: str, content_id2: str, similarity_score: float):
        super().__init__(
            source_id=content_id1,
            target_id=content_id2,
            edge_type="SIMILAR_TO",
            weight=similarity_score,
            properties={
                "similarity_score": similarity_score,
                "created_at": datetime.utcnow().isoformat()
            }
        ) 