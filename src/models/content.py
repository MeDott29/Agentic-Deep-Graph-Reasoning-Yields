"""
Content models for the Knowledge Graph Social Network System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from .base import GraphNode, TimestampMixin

class ContentBase(BaseModel):
    """Base content model"""
    title: Optional[str] = None
    description: Optional[str] = None
    user_id: str
    
class ContentCreate(ContentBase):
    """Content creation model"""
    file_path: str
    hashtags: List[str] = Field(default_factory=list)
    is_private: bool = False
    allow_comments: bool = True
    
    @validator('hashtags')
    def hashtags_format(cls, v):
        return [tag.lower().strip() for tag in v]

class ContentUpdate(BaseModel):
    """Content update model"""
    title: Optional[str] = None
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None
    is_private: Optional[bool] = None
    allow_comments: Optional[bool] = None
    
    @validator('hashtags')
    def hashtags_format(cls, v):
        if v is not None:
            return [tag.lower().strip() for tag in v]
        return v

class ContentInDB(ContentBase, TimestampMixin):
    """Content model as stored in the database"""
    id: str
    file_path: str
    thumbnail_path: Optional[str] = None
    duration: float  # in seconds
    width: int
    height: int
    hashtags: List[str] = Field(default_factory=list)
    is_private: bool = False
    allow_comments: bool = True
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    
class Content(ContentBase, TimestampMixin):
    """Content model returned to clients"""
    id: str
    thumbnail_url: Optional[str] = None
    video_url: str
    duration: float  # in seconds
    width: int
    height: int
    hashtags: List[str] = Field(default_factory=list)
    is_private: bool = False
    allow_comments: bool = True
    view_count: int = 0
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    
    class Config:
        orm_mode = True

class ContentNode(GraphNode):
    """Content node in the knowledge graph"""
    def __init__(self, content: Content):
        super().__init__(
            id=content.id,
            node_type="CONTENT",
            properties={
                "title": content.title,
                "description": content.description,
                "user_id": content.user_id,
                "duration": content.duration,
                "hashtags": content.hashtags,
                "view_count": content.view_count,
                "like_count": content.like_count,
                "comment_count": content.comment_count,
                "share_count": content.share_count,
                "created_at": content.created_at.isoformat(),
                "updated_at": content.updated_at.isoformat(),
            }
        )

class HashtagNode(GraphNode):
    """Hashtag node in the knowledge graph"""
    def __init__(self, hashtag: str):
        super().__init__(
            id=f"hashtag:{hashtag}",
            node_type="HASHTAG",
            properties={
                "name": hashtag,
                "content_count": 0,
            }
        )

class Comment(TimestampMixin):
    """Comment model"""
    id: str
    content_id: str
    user_id: str
    text: str
    parent_comment_id: Optional[str] = None
    like_count: int = 0
    
    class Config:
        orm_mode = True 