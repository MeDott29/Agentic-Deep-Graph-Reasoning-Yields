from typing import Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime

from .base import DBModel
from .user import UserInDB

class PersonalityTrait(BaseModel):
    """Model for personality traits of AI agents."""
    name: str
    value: float = Field(..., ge=0.0, le=1.0)
    
    @validator('value')
    def validate_value(cls, v):
        """Ensure value is between 0 and 1."""
        if v < 0.0 or v > 1.0:
            raise ValueError('Trait value must be between 0.0 and 1.0')
        return v

class ContentSpecialization(BaseModel):
    """Model for content specializations of AI agents."""
    topic: str
    expertise_level: float = Field(..., ge=0.0, le=1.0)
    
    @validator('expertise_level')
    def validate_expertise(cls, v):
        """Ensure expertise level is between 0 and 1."""
        if v < 0.0 or v > 1.0:
            raise ValueError('Expertise level must be between 0.0 and 1.0')
        return v

class AgentPersonality(BaseModel):
    """Model for AI agent personality configuration."""
    traits: List[PersonalityTrait]
    content_specializations: List[ContentSpecialization]
    creativity: float = Field(..., ge=0.0, le=1.0)
    sociability: float = Field(..., ge=0.0, le=1.0)
    controversy_tolerance: float = Field(..., ge=0.0, le=1.0)
    
class AgentMetrics(BaseModel):
    """Model for AI agent performance metrics."""
    content_generated: int = 0
    avg_engagement_rate: float = 0.0
    avg_view_duration: float = 0.0
    follower_growth_rate: float = 0.0
    content_diversity_score: float = 0.0
    
class AgentCreate(BaseModel):
    """Model for creating a new AI agent."""
    username: str
    display_name: str
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    personality: AgentPersonality
    
class AgentInDB(UserInDB):
    """Model for AI agent data stored in the database."""
    personality: AgentPersonality
    metrics: AgentMetrics = Field(default_factory=AgentMetrics)
    last_content_generation: Optional[datetime] = None
    
    def __init__(self, **data):
        """Initialize AI agent with type set to 'ai_agent'."""
        super().__init__(**data)
        self.type = "ai_agent"
        
class AgentUpdate(BaseModel):
    """Model for updating AI agent configuration."""
    display_name: Optional[str] = None
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None
    personality: Optional[AgentPersonality] = None 