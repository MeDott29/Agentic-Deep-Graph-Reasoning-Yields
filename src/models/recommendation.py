"""
Recommendation models for the Knowledge Graph Social Network System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from .base import TimestampMixin

class RecommendationScore(BaseModel):
    """Score for a recommendation"""
    content_id: str
    score: float
    reason: str
    features: Dict[str, float] = Field(default_factory=dict)

class ContentRecommendation(BaseModel):
    """Content recommendation model"""
    user_id: str
    recommendations: List[RecommendationScore]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        orm_mode = True

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

class RecommendationRequest(BaseModel):
    """Recommendation request model"""
    user_id: str
    count: int = 10
    exclude_seen: bool = True
    include_following: bool = True
    include_trending: bool = True
    categories: Optional[List[str]] = None
    max_duration: Optional[int] = None  # in seconds
    
class RecommendationResponse(BaseModel):
    """Recommendation response model"""
    recommendations: List[Dict[str, Any]]
    request_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow) 