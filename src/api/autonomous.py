"""
Autonomous agent interaction API endpoints for the Knowledge Graph Social Network System
"""
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from typing import Dict, Any, List
from pydantic import BaseModel

from src.models.user import User
from src.services.ai_agent_interaction_service import AIAgentInteractionService
from src.api.users import get_current_user
from src.api.dependencies import get_ai_agent_interaction_service

# Create router
router = APIRouter()

# Models
class AgentInteractionResponse(BaseModel):
    """Response model for agent interactions"""
    message: str
    status: str

class AgentInteractionStatusResponse(BaseModel):
    """Response model for agent interaction status"""
    is_running: bool
    interval_seconds: int
    active_agents: int

# Background task for running autonomous interactions
autonomous_task_running = False
autonomous_interval_seconds = 120  # Default to 2 minutes

@router.post("/start", response_model=AgentInteractionResponse)
async def start_autonomous_interactions(
    background_tasks: BackgroundTasks,
    interval_seconds: int = 120,
    current_user: User = Depends(get_current_user),
    ai_agent_interaction_service: AIAgentInteractionService = Depends(get_ai_agent_interaction_service)
):
    """Start autonomous agent interactions"""
    global autonomous_task_running, autonomous_interval_seconds
    
    # Only allow admins to start autonomous interactions
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can start autonomous agent interactions"
        )
    
    if autonomous_task_running:
        return {
            "message": "Autonomous agent interactions are already running",
            "status": "already_running"
        }
    
    # Set the interval
    autonomous_interval_seconds = max(30, interval_seconds)  # Minimum 30 seconds
    
    # Start the autonomous interactions in the background
    def run_autonomous_interactions():
        global autonomous_task_running
        autonomous_task_running = True
        try:
            ai_agent_interaction_service.start_autonomous_interactions(interval_seconds=autonomous_interval_seconds)
        finally:
            autonomous_task_running = False
    
    background_tasks.add_task(run_autonomous_interactions)
    
    return {
        "message": f"Started autonomous agent interactions with interval of {autonomous_interval_seconds} seconds",
        "status": "started"
    }

@router.post("/stop", response_model=AgentInteractionResponse)
async def stop_autonomous_interactions(
    current_user: User = Depends(get_current_user)
):
    """Stop autonomous agent interactions"""
    global autonomous_task_running
    
    # Only allow admins to stop autonomous interactions
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can stop autonomous agent interactions"
        )
    
    if not autonomous_task_running:
        return {
            "message": "Autonomous agent interactions are not running",
            "status": "not_running"
        }
    
    # Set the flag to stop the autonomous interactions
    autonomous_task_running = False
    
    return {
        "message": "Stopping autonomous agent interactions",
        "status": "stopping"
    }

@router.get("/status", response_model=AgentInteractionStatusResponse)
async def get_autonomous_interaction_status(
    current_user: User = Depends(get_current_user),
    ai_agent_interaction_service: AIAgentInteractionService = Depends(get_ai_agent_interaction_service)
):
    """Get the status of autonomous agent interactions"""
    global autonomous_task_running, autonomous_interval_seconds
    
    # Get the number of active agents
    active_agents = len(ai_agent_interaction_service.get_agents_ready_for_interaction())
    
    return {
        "is_running": autonomous_task_running,
        "interval_seconds": autonomous_interval_seconds,
        "active_agents": active_agents
    }

@router.post("/run-cycle", response_model=AgentInteractionResponse)
async def run_interaction_cycle(
    current_user: User = Depends(get_current_user),
    ai_agent_interaction_service: AIAgentInteractionService = Depends(get_ai_agent_interaction_service)
):
    """Run a single cycle of autonomous agent interactions"""
    # Only allow admins to manually run interaction cycles
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can manually run interaction cycles"
        )
    
    # Run a single cycle
    ai_agent_interaction_service.run_autonomous_interaction_cycle()
    
    return {
        "message": "Ran a single cycle of autonomous agent interactions",
        "status": "completed"
    } 