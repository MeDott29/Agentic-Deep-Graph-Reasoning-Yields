"""
User models for the Knowledge Graph Social Network System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
from .base import GraphNode, TimestampMixin

class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: EmailStr
    full_name: Optional[str] = None
    bio: Optional[str] = None
    
    @validator('username')
    def username_alphanumeric(cls, v):
        assert v.isalnum(), 'Username must be alphanumeric'
        return v

class UserCreate(UserBase):
    """User creation model"""
    password: str
    
    @validator('password')
    def password_min_length(cls, v):
        assert len(v) >= 8, 'Password must be at least 8 characters'
        return v

class UserUpdate(BaseModel):
    """User update model"""
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture_url: Optional[str] = None
    
class UserInDB(UserBase, TimestampMixin):
    """User model as stored in the database"""
    id: str
    hashed_password: str
    is_active: bool = True
    is_verified: bool = False
    profile_picture_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    
class User(UserBase, TimestampMixin):
    """User model returned to clients"""
    id: str
    profile_picture_url: Optional[str] = None
    follower_count: int = 0
    following_count: int = 0
    
    class Config:
        orm_mode = True

class UserNode(GraphNode):
    """User node in the knowledge graph"""
    def __init__(self, user: User):
        super().__init__(
            id=user.id,
            node_type="USER",
            properties={
                "username": user.username,
                "full_name": user.full_name,
                "bio": user.bio,
                "follower_count": user.follower_count,
                "following_count": user.following_count,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
        )

class UserPreferences(BaseModel):
    """User preferences for content recommendations"""
    user_id: str
    content_categories: List[str] = Field(default_factory=list)
    preferred_content_duration: Optional[int] = None  # in seconds
    preferred_languages: List[str] = Field(default_factory=lambda: ["en"])
    explicit_content_allowed: bool = False
    autoplay_enabled: bool = True
    
    class Config:
        orm_mode = True 