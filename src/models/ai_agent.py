"""
AI Agent model for the Knowledge Graph Social Network System
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

from src.models.base import GraphNode

class AgentStatus(str, Enum):
    """Status of an AI agent"""
    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"

class AgentSpecialization(str, Enum):
    """Specialization of an AI agent"""
    KNOWLEDGE_GRAPHS = "knowledge_graphs"
    DATA_SCIENCE = "data_science"
    ARTIFICIAL_INTELLIGENCE = "artificial_intelligence"
    GRAPH_DATABASES = "graph_databases"
    PROGRAMMING = "programming"
    DATA_MODELING = "data_modeling"
    MACHINE_LEARNING = "machine_learning"
    NEURAL_NETWORKS = "neural_networks"
    DATA_VISUALIZATION = "data_visualization"

class AIAgentNode(GraphNode):
    """AI Agent node in the knowledge graph"""
    def __init__(self, agent_id: str, properties: Dict[str, Any]):
        super().__init__(node_id=agent_id, node_type="AI_AGENT", properties=properties)

class AIAgentBase(BaseModel):
    """Base AI agent model"""
    name: str
    description: Optional[str] = None
    status: AgentStatus = AgentStatus.ONLINE
    specializations: List[AgentSpecialization] = []
    avatar: Optional[str] = None

class AIAgent(AIAgentBase):
    """AI agent model"""
    id: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    is_active: bool = True
    post_count: int = 0
    comment_count: int = 0
    follower_count: int = 0
    following_count: int = 0
    
    class Config:
        """Pydantic config"""
        from_attributes = True

class AIAgentCreate(AIAgentBase):
    """AI agent creation model"""
    pass

class AIAgentUpdate(BaseModel):
    """AI agent update model"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AgentStatus] = None
    specializations: Optional[List[AgentSpecialization]] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None

class AIAgentInDB(AIAgent):
    """AI agent model as stored in the database"""
    api_key: str
    model_config: Dict[str, Any] = {} 