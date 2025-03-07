from typing import Optional, List, Dict, Any, Union, Literal
from pydantic import BaseModel, Field, EmailStr, validator
from datetime import datetime

from .base import DBModel, TimestampModel

class UserBase(BaseModel):
    """Base model for user data."""
    username: str
    display_name: str
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    
class UserCreate(UserBase):
    """Model for creating a new user."""
    email: EmailStr
    password: str
    
    @validator('password')
    def password_strength(cls, v):
        """Validate password strength."""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserUpdate(BaseModel):
    """Model for updating user information."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    
class UserType(BaseModel):
    """Enum for user types."""
    type: Literal["human", "ai_agent"]

class UserInDB(UserBase, DBModel, UserType):
    """Model for user data stored in the database."""
    email: Optional[EmailStr] = None
    hashed_password: Optional[str] = None
    is_active: bool = True
    followers_count: int = 0
    following_count: int = 0
    content_count: int = 0
    
class User(UserBase, UserType):
    """Model for user data returned to clients."""
    id: str
    followers_count: int
    following_count: int
    content_count: int
    created_at: datetime
    
class UserWithStats(User):
    """User model with additional statistics."""
    total_views: int
    total_likes: int
    total_shares: int
    engagement_rate: float
    
class Token(BaseModel):
    """Model for authentication tokens."""
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    """Model for token payload data."""
    user_id: Optional[str] = None 