"""
AI Content API for the Knowledge Graph Social Network System
"""
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from pydantic import BaseModel

from services.ai_content import AIContentGenerationService
from services.content import ContentService
from services.knowledge_graph import KnowledgeGraphService

# Create router
router = APIRouter()

# Service instances
knowledge_graph_service = KnowledgeGraphService()
content_service = ContentService(knowledge_graph_service)
ai_content_service = AIContentGenerationService(knowledge_graph_service)

# Models
class AIAgentCreate(BaseModel):
    """Model for creating an AI agent"""
    name: str
    description: str
    specialties: List[str]
    content_types: List[str] = ["video"]

class AIAgentUpdate(BaseModel):
    """Model for updating an AI agent"""
    name: Optional[str] = None
    description: Optional[str] = None
    specialties: Optional[List[str]] = None
    content_types: Optional[List[str]] = None

class UserPreferencesUpdate(BaseModel):
    """Model for updating user preferences"""
    interests: Optional[List[str]] = None
    preferred_agents: Optional[List[str]] = None
    content_types: Optional[List[str]] = None

# Endpoints
@router.get("/agents")
async def get_ai_agents(limit: int = Query(10, ge=1, le=100)):
    """Get list of AI agents"""
    return ai_content_service.get_ai_agents(limit=limit)

@router.get("/agents/{agent_id}")
async def get_ai_agent(agent_id: str = Path(...)):
    """Get AI agent by ID"""
    agent = ai_content_service.get_ai_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")
    return agent

@router.post("/agents")
async def create_ai_agent(agent_data: AIAgentCreate):
    """Create a new AI agent"""
    return ai_content_service.create_ai_agent(agent_data.dict())

@router.put("/agents/{agent_id}")
async def update_ai_agent(agent_data: AIAgentUpdate, agent_id: str = Path(...)):
    """Update an AI agent"""
    agent = ai_content_service.update_ai_agent(agent_id, agent_data.dict(exclude_unset=True))
    if not agent:
        raise HTTPException(status_code=404, detail="AI agent not found")
    return agent

@router.delete("/agents/{agent_id}")
async def delete_ai_agent(agent_id: str = Path(...)):
    """Delete an AI agent"""
    success = ai_content_service.delete_ai_agent(agent_id)
    if not success:
        raise HTTPException(status_code=404, detail="AI agent not found")
    return {"message": "AI agent deleted successfully"}

@router.get("/preferences/{user_id}")
async def get_user_preferences(user_id: str = Path(...)):
    """Get user preferences for AI content"""
    return ai_content_service.get_user_preferences(user_id)

@router.put("/preferences/{user_id}")
async def update_user_preferences(preferences: UserPreferencesUpdate, user_id: str = Path(...)):
    """Update user preferences for AI content"""
    return ai_content_service.update_user_preferences(user_id, preferences.dict(exclude_unset=True))

@router.post("/generate")
async def generate_ai_content(
    user_id: Optional[str] = Query(None),
    count: int = Query(5, ge=1, le=20)
):
    """Generate AI content based on user preferences or randomly"""
    # Generate content models
    content_models = ai_content_service.generate_ai_content(user_id=user_id, count=count)
    
    # Create content in the system
    created_content = []
    for content_model in content_models:
        # Create placeholder content
        content = content_service.create_content(content_model)
        created_content.append(content)
    
    return created_content

@router.post("/feed")
async def get_ai_content_feed(
    user_id: str = Query(...),
    count: int = Query(10, ge=1, le=50)
):
    """Get personalized AI content feed for a user"""
    # Generate content models
    content_models = ai_content_service.generate_ai_content(user_id=user_id, count=count)
    
    # Create content in the system
    created_content = []
    for content_model in content_models:
        # Create placeholder content
        content = content_service.create_content(content_model)
        created_content.append(content)
    
    return created_content

@router.post("/interaction/{user_id}/{content_id}")
async def record_ai_content_interaction(
    user_id: str = Path(...),
    content_id: str = Path(...),
    agent_id: str = Query(...),
    interaction_type: str = Query(...)
):
    """Record user interaction with AI-generated content"""
    success = ai_content_service.record_user_interaction(
        user_id=user_id,
        content_id=content_id,
        agent_id=agent_id,
        interaction_type=interaction_type
    )
    
    if not success:
        raise HTTPException(status_code=400, detail="Failed to record interaction")
    
    return {"message": "Interaction recorded successfully"}

@router.get("/analysis/{user_id}")
async def analyze_user_preferences(user_id: str = Path(...)):
    """Analyze user preferences based on interaction history"""
    return ai_content_service.analyze_user_preferences(user_id) 