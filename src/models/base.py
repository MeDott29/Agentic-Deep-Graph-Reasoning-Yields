"""
Base models for the Knowledge Graph Social Network System
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr, validator
import uuid

def generate_id() -> str:
    """Generate a unique ID"""
    return str(uuid.uuid4())

class TimestampMixin(BaseModel):
    """Mixin for created_at and updated_at fields"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class GraphNode(TimestampMixin):
    """Base class for all graph nodes"""
    id: str = Field(default_factory=generate_id)
    node_type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class GraphEdge(BaseModel):
    """Base class for all graph edges"""
    source_id: str
    target_id: str
    edge_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        arbitrary_types_allowed = True

class GraphQuery(BaseModel):
    """Base class for graph queries"""
    start_node_id: Optional[str] = None
    node_types: Optional[List[str]] = None
    edge_types: Optional[List[str]] = None
    max_depth: int = 2
    limit: int = 100
    
    class Config:
        arbitrary_types_allowed = True 