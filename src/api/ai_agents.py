"""
API endpoints for AI agents
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any
from pydantic import BaseModel

from src.models.ai_agent import AIAgent, AIAgentCreate, AIAgentUpdate, AgentStatus, AgentSpecialization
from src.models.user import User
from src.services.ai_agent_service import AIAgentService
from src.services.openai_service import OpenAIService
from src.api.dependencies import get_current_user, get_ai_agent_service, get_openai_service

router = APIRouter(
    prefix="/ai-agents",
    tags=["ai-agents"],
    responses={404: {"description": "Not found"}},
)

# Chat message models
class ChatMessage(BaseModel):
    """Chat message model"""
    content: str
    sender_id: str
    sender_type: str  # "user" or "agent"
    timestamp: Optional[str] = None

class ChatRequest(BaseModel):
    """Chat request model"""
    agent_id: str
    message: str
    chat_history: Optional[List[ChatMessage]] = []

class ChatResponse(BaseModel):
    """Chat response model"""
    agent_id: str
    message: str
    agent_name: str
    agent_avatar: str

@router.get("/", response_model=List[AIAgent])
async def get_all_agents(
    limit: int = 100,
    offset: int = 0,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all AI agents
    """
    return ai_agent_service.get_all_agents(limit=limit, offset=offset)

@router.get("/online", response_model=List[AIAgent])
async def get_online_agents(
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get all online AI agents
    """
    return ai_agent_service.get_online_agents()

@router.get("/specialization/{specialization}", response_model=List[AIAgent])
async def get_agents_by_specialization(
    specialization: AgentSpecialization,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI agents by specialization
    """
    return ai_agent_service.get_agents_by_specialization(specialization)

@router.get("/{agent_id}", response_model=AIAgent)
async def get_agent(
    agent_id: str,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get an AI agent by ID
    """
    agent = ai_agent_service.get_agent(agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI agent with ID {agent_id} not found"
        )
    return agent

@router.get("/name/{name}", response_model=AIAgent)
async def get_agent_by_name(
    name: str,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Get an AI agent by name
    """
    agent = ai_agent_service.get_agent_by_name(name)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI agent with name {name} not found"
        )
    return agent

@router.post("/", response_model=AIAgent, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_create: AIAgentCreate,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new AI agent
    """
    # Only admin users can create AI agents
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can create AI agents"
        )
    
    try:
        return ai_agent_service.create_agent(agent_create)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.put("/{agent_id}", response_model=AIAgent)
async def update_agent(
    agent_id: str,
    agent_update: AIAgentUpdate,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update an AI agent
    """
    # Only admin users can update AI agents
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update AI agents"
        )
    
    try:
        agent = ai_agent_service.update_agent(agent_id, agent_update)
        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"AI agent with ID {agent_id} not found"
            )
        return agent
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Delete an AI agent
    """
    # Only admin users can delete AI agents
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can delete AI agents"
        )
    
    success = ai_agent_service.delete_agent(agent_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI agent with ID {agent_id} not found"
        )

@router.put("/{agent_id}/status", response_model=AIAgent)
async def update_agent_status(
    agent_id: str,
    status: AgentStatus,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    current_user: User = Depends(get_current_user)
):
    """
    Update an AI agent's status
    """
    # Only admin users can update AI agent status
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can update AI agent status"
        )
    
    agent = ai_agent_service.update_agent_status(agent_id, status)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI agent with ID {agent_id} not found"
        )
    return agent

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    chat_request: ChatRequest,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    openai_service: OpenAIService = Depends(get_openai_service),
    current_user: User = Depends(get_current_user)
):
    """
    Chat with an AI agent
    """
    agent = ai_agent_service.get_agent(chat_request.agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI agent with ID {chat_request.agent_id} not found"
        )
    
    # Only allow chatting with online agents
    if agent.status != AgentStatus.ONLINE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AI agent {agent.name} is not online"
        )
    
    try:
        # Generate a response using OpenAI
        agent_context = {
            "name": agent.name,
            "bio": agent.bio,
            "specializations": [spec.value for spec in agent.specializations],
            "personality": agent.personality
        }
        
        response = openai_service.generate_chat_response(
            user_message=chat_request.message,
            chat_history=chat_request.chat_history,
            agent_context=agent_context
        )
        
        return {
            "agent_id": agent.id,
            "message": response,
            "agent_name": agent.name,
            "agent_avatar": agent.avatar_url
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate chat response: {str(e)}"
        ) 