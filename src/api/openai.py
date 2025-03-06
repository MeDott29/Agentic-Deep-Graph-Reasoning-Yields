"""
OpenAI API endpoints for the Knowledge Graph Social Network System
"""
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.services.ai_agent_service import AIAgentService
from src.services.content import ContentService, ContentCreate
from src.services.openai_service import OpenAIService
from src.api.dependencies import get_ai_agent_service, get_content_service

# Create router
router = APIRouter()

# Create OpenAI service
openai_service = OpenAIService()

# Models
class GenerateProfileImageRequest(BaseModel):
    """Request model for generating a profile image"""
    name: str
    description: str

class GenerateProfileImageResponse(BaseModel):
    """Response model for generating a profile image"""
    image_path: str

class GeneratePostImageRequest(BaseModel):
    """Request model for generating a post image"""
    content: str
    specializations: Optional[List[str]] = None

class GeneratePostImageResponse(BaseModel):
    """Response model for generating a post image"""
    image_path: str

class GenerateAgentPostRequest(BaseModel):
    """Request model for generating an agent post"""
    agent_id: str

class GenerateAgentPostResponse(BaseModel):
    """Response model for generating an agent post"""
    agent_id: str
    agent_name: str
    agent_avatar: str
    title: str
    description: str
    hashtags: List[str]
    image_path: str

class CreateAgentPostRequest(BaseModel):
    """Request model for creating an agent post"""
    agent_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    hashtags: Optional[List[str]] = None
    image_path: Optional[str] = None

class CreateAgentPostResponse(BaseModel):
    """Response model for creating an agent post"""
    content_id: str
    title: str
    description: str
    hashtags: List[str]
    image_url: str
    agent_id: str
    agent_name: str

# Endpoints
@router.post("/generate-profile-image", response_model=GenerateProfileImageResponse)
async def generate_profile_image(
    request: GenerateProfileImageRequest
) -> Dict[str, Any]:
    """
    Generate a profile image using DALL-E-2
    """
    try:
        image_path = openai_service.generate_profile_image(
            agent_name=request.name,
            agent_description=request.description
        )
        
        return {"image_path": image_path}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate profile image: {str(e)}"
        )

@router.post("/generate-post-image", response_model=GeneratePostImageResponse)
async def generate_post_image(
    request: GeneratePostImageRequest
) -> Dict[str, Any]:
    """
    Generate a post image using DALL-E-2
    """
    try:
        image_path = openai_service.generate_post_image(
            post_content=request.content,
            agent_specializations=request.specializations
        )
        
        return {"image_path": image_path}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate post image: {str(e)}"
        )

@router.post("/generate-agent-post", response_model=GenerateAgentPostResponse)
async def generate_agent_post(
    request: GenerateAgentPostRequest,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service)
) -> Dict[str, Any]:
    """
    Generate a post for an AI agent using DALL-E-2 and GPT
    """
    try:
        post_data = ai_agent_service.generate_agent_post(request.agent_id)
        return post_data
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate agent post: {str(e)}"
        )

@router.post("/create-agent-post", response_model=CreateAgentPostResponse)
async def create_agent_post(
    request: CreateAgentPostRequest,
    ai_agent_service: AIAgentService = Depends(get_ai_agent_service),
    content_service: ContentService = Depends(get_content_service)
) -> Dict[str, Any]:
    """Create a post for an AI agent"""
    # Check if the agent exists
    agent = ai_agent_service.get_agent(request.agent_id)
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI agent with ID '{request.agent_id}' not found"
        )
    
    try:
        # Generate post content if not provided
        if not request.title or not request.description or not request.hashtags or not request.image_path:
            post_data = ai_agent_service.generate_agent_post(request.agent_id)
            
            title = request.title or post_data["title"]
            description = request.description or post_data["description"]
            hashtags = request.hashtags or post_data["hashtags"]
            image_path = request.image_path or post_data["image_path"]
        else:
            title = request.title
            description = request.description
            hashtags = request.hashtags
            image_path = request.image_path
        
        # Create a ContentCreate object
        content_create = ContentCreate(
            title=title,
            description=description,
            user_id=request.agent_id,
            file_path=image_path,
            hashtags=hashtags,
            is_private=False,
            allow_comments=True,
            is_ai_generated=True
        )
        
        # Create the content
        content = content_service.create_content(content_create)
        
        # Increment the agent's post count
        ai_agent_service.increment_post_count(request.agent_id)
        
        # Return the response
        return {
            "content_id": content.id,
            "title": content.title,
            "description": content.description,
            "hashtags": content.hashtags,
            "image_url": content.video_url,  # Using video_url field for image URL
            "agent_id": request.agent_id,
            "agent_name": agent.name
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent post: {str(e)}"
        ) 