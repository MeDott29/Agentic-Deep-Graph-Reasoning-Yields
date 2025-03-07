from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime

from .base import DBModel

class ContentType(BaseModel):
    """Enum for content types."""
    type: Literal["text", "image", "video", "mixed"]

class ContentBase(BaseModel):
    """Base model for content data."""
    title: Optional[str] = None
    text_content: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)  # IDs of referenced content
    
    @validator('media_urls')
    def validate_media_urls(cls, v, values):
        """Ensure content has either text or media."""
        if not v and not values.get('text_content'):
            raise ValueError('Content must have either text or media')
        return v

class ContentCreate(ContentBase, ContentType):
    """Model for creating new content."""
    pass

class ContentInDB(ContentBase, ContentType, DBModel):
    """Model for content data stored in the database."""
    creator_id: str
    view_count: int = 0
    like_count: int = 0
    share_count: int = 0
    comment_count: int = 0
    total_view_duration: float = 0.0  # In seconds
    avg_view_duration: float = 0.0    # In seconds
    
    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate based on interactions."""
        if self.view_count == 0:
            return 0.0
        return (self.like_count + self.share_count + self.comment_count) / self.view_count

class Content(ContentBase, ContentType):
    """Model for content data returned to clients."""
    id: str
    creator_id: str
    view_count: int
    like_count: int
    share_count: int
    comment_count: int
    avg_view_duration: float
    created_at: datetime
    
class ContentUpdate(BaseModel):
    """Model for updating content."""
    title: Optional[str] = None
    text_content: Optional[str] = None
    media_urls: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    
class ContentView(BaseModel):
    """Model for recording content views."""
    user_id: Optional[str] = None  # Optional for anonymous views
    view_duration: float  # In seconds
    
class ContentInteraction(BaseModel):
    """Model for content interactions (likes, shares)."""
    user_id: str
    
class CommentBase(BaseModel):
    """Base model for comments."""
    text: str
    
class CommentCreate(CommentBase):
    """Model for creating new comments."""
    pass
    
class CommentInDB(CommentBase, DBModel):
    """Model for comment data stored in the database."""
    content_id: str
    user_id: str
    like_count: int = 0
    
class Comment(CommentBase):
    """Model for comment data returned to clients."""
    id: str
    content_id: str
    user_id: str
    like_count: int
    created_at: datetime 