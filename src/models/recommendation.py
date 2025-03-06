"""
Recommendation models for the Knowledge Graph Social Network System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import TimestampMixin

class RecommendationScore(BaseModel):
    """Model for recommendation score"""
    score: float
    reason: str

class ContentRecommendation(BaseModel):
    """Model for content recommendation"""
    content_id: str
    score: float
    reasons: List[str] = Field(default_factory=list)
    content: Dict[str, Any]

class RecommendationRequest(BaseModel):
    """Model for recommendation request"""
    user_id: str
    count: int = 20
    content_types: Optional[List[str]] = None
    hashtags: Optional[List[str]] = None
    min_duration: Optional[float] = None
    max_duration: Optional[float] = None
    exclude_seen: bool = True
    exclude_user_ids: Optional[List[str]] = None
    include_ai_content: bool = True
    ai_content_ratio: float = 0.3  # 30% AI content by default

class RecommendationResponse(BaseModel):
    """Model for recommendation response"""
    user_id: str
    count: int
    recommendations: List[ContentRecommendation]

class AIContentPreference(BaseModel):
    """Model for AI content preference"""
    user_id: str
    interests: List[str] = Field(default_factory=list)
    preferred_agents: List[str] = Field(default_factory=list)
    content_types: List[str] = Field(default_factory=list)
    interaction_history: List[Dict[str, Any]] = Field(default_factory=list)

class AIContentInteraction(BaseModel):
    """Model for AI content interaction"""
    user_id: str
    content_id: str
    agent_id: str
    interaction_type: str
    timestamp: datetime = Field(default_factory=datetime.now)

class AIContentFeedRequest(BaseModel):
    """Model for AI content feed request"""
    user_id: str
    count: int = 10
    content_types: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    preferred_agents: Optional[List[str]] = None

class UserSimilarity(BaseModel):
    """User similarity model"""
    user_id1: str
    user_id2: str
    similarity_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True

class ContentSimilarity(BaseModel):
    """Content similarity model"""
    content_id1: str
    content_id2: str
    similarity_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True

class UserEmbedding(BaseModel):
    """User embedding model"""
    user_id: str
    embedding: List[float]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True

class ContentEmbedding(BaseModel):
    """Content embedding model"""
    content_id: str
    embedding: List[float]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True

class UserInterest(BaseModel):
    """User interest model"""
    user_id: str
    category: str
    interest_score: float
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True 