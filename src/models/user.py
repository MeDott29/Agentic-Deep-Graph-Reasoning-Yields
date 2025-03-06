"""
User model for the Knowledge Graph Social Network System
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.models.base import GraphNode

class UserNode(GraphNode):
    """User node in the knowledge graph"""
    def __init__(self, user_id: str, properties: Dict[str, Any]):
        super().__init__(node_id=user_id, node_type="USER", properties=properties)

class UserBase(BaseModel):
    """Base user model"""
    username: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None

class User(BaseModel):
    """User model"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    is_verified: bool = False
    is_admin: bool = False
    
    class Config:
        """Pydantic config"""
        from_attributes = True 

class UserCreate(BaseModel):
    """User creation model"""
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    bio: Optional[str] = None
    
class UserUpdate(BaseModel):
    """User update model"""
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    full_name: Optional[str] = None
    bio: Optional[str] = None
    profile_picture: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None 

class UserInDB(User):
    """User model as stored in the database"""
    hashed_password: str

class UserPreferences(BaseModel):
    """User preferences model"""
    user_id: str
    content_categories: List[str] = []
    preferred_languages: List[str] = ["en"]
    explicit_content_allowed: bool = False
    autoplay_enabled: bool = True 