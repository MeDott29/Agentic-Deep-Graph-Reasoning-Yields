from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from models.user import User
from models.agent import AgentCreate, AgentUpdate, AgentMetrics
from models.content import Content
from services.agent import AgentService
from api.users import get_current_user

# Create router
router = APIRouter()

# Initialize agent service
agent_service = AgentService()

@router.post("/create-agent", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_agent(agent_create: AgentCreate, current_user: User = Depends(get_current_user)):
    """Create a new AI agent profile."""
    # Only allow creation if user is authenticated
    return agent_service.create_agent(agent_create)

@router.get("/", response_model=List[User])
async def list_agents(skip: int = 0, limit: int = 100):
    """List all AI agents."""
    return agent_service.list_agents(skip, limit)

@router.get("/{agent_id}", response_model=User)
async def get_agent(agent_id: str):
    """Get agent by ID."""
    agent = agent_service.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.put("/{agent_id}", response_model=User)
async def update_agent(agent_id: str, agent_update: AgentUpdate, current_user: User = Depends(get_current_user)):
    """Update agent personality parameters."""
    # Only allow updates if user is authenticated
    agent = agent_service.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent_service.update_agent(agent_id, agent_update)

@router.post("/{agent_id}/generate", response_model=Content)
async def generate_content(agent_id: str, current_user: User = Depends(get_current_user)):
    """Trigger content generation for an agent."""
    agent = agent_service.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent_service.generate_content(agent_id)

@router.get("/{agent_id}/metrics", response_model=AgentMetrics)
async def get_agent_metrics(agent_id: str):
    """Get agent performance metrics."""
    agent = agent_service.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent_service.get_agent_metrics(agent_id)

@router.get("/{agent_id}/content", response_model=List[Content])
async def get_agent_content(agent_id: str, skip: int = 0, limit: int = 20):
    """Get content created by an agent."""
    agent = agent_service.get_agent(agent_id)
    if agent is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent_service.get_agent_content(agent_id, skip, limit)

@router.get("/leaderboard", response_model=List[User])
async def get_agent_leaderboard(metric: str = "followers_count", limit: int = 10):
    """Get agent performance rankings."""
    valid_metrics = ["followers_count", "content_count", "avg_engagement_rate", "avg_view_duration"]
    if metric not in valid_metrics:
        raise HTTPException(status_code=400, detail=f"Invalid metric. Must be one of: {', '.join(valid_metrics)}")
    
    return agent_service.get_leaderboard(metric, limit)

@router.post("/generate-batch", response_model=List[Content])
async def generate_batch_content(count: int = 10, current_user: User = Depends(get_current_user)):
    """Generate content from multiple agents."""
    if count < 1 or count > 50:
        raise HTTPException(status_code=400, detail="Count must be between 1 and 50")
    
    return agent_service.generate_batch_content(count) 