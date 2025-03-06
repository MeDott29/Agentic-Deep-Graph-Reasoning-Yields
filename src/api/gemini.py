"""
Gemini API endpoints for the Knowledge Graph Social Network System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any, List, Optional
from pydantic import BaseModel

from src.models.user import User
from src.services.gemini_service import GeminiService
from src.services.content import ContentService
from src.services.knowledge_graph import KnowledgeGraphService
from src.api.users import get_current_user
from src.models.content import ContentCreate

# Create router
router = APIRouter()

# Create services
gemini_service = GeminiService()
kg_service = KnowledgeGraphService()
content_service = ContentService(kg_service)

class PostResponse(BaseModel):
    """Model for post response generation"""
    post_id: str
    response_content: str

class PostGeneration(BaseModel):
    """Model for post generation"""
    user_id: str
    post_content: str
    hashtags: List[str] = []
    title: Optional[str] = None

class HashtagGeneration(BaseModel):
    """Model for hashtag content generation"""
    hashtag: str
    post_content: str
    hashtags: List[str] = []
    title: Optional[str] = None

class ContentRecommendation(BaseModel):
    """Model for personalized content recommendations"""
    user_id: str
    recommendations: List[Dict[str, Any]]
    explanation: str

class ImageAnalysisRequest(BaseModel):
    """Model for image analysis request"""
    image_path: str
    prompt: Optional[str] = None

class ImageAnalysisResponse(BaseModel):
    """Model for image analysis response"""
    success: bool
    analysis: str
    error: Optional[str] = None

@router.post("/respond", response_model=PostResponse)
async def generate_response(
    post_id: str,
    post_content: str,
    current_user: User = Depends(get_current_user)
):
    """Generate a response to a post using Gemini"""
    try:
        response = gemini_service.generate_response_to_post(post_content, post_id)
        
        return {
            "post_id": post_id,
            "response_content": response["reply_content"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
        )

@router.post("/generate", response_model=PostGeneration)
async def generate_post(
    user_context: Dict[str, Any],
    current_user: User = Depends(get_current_user)
):
    """Generate a new post for a synthetic user"""
    try:
        # Only allow admins to generate posts for other users
        if user_context.get("user_id") != current_user.id:
            # Check if current user is admin (this would need to be implemented)
            pass
            
        response = gemini_service.generate_new_post(user_context)
        
        return {
            "user_id": user_context.get("user_id", current_user.id),
            "post_content": response["post_content"],
            "hashtags": response["hashtags"],
            "title": response["title"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate post: {str(e)}"
        )

@router.post("/hashtag-content", response_model=HashtagGeneration)
async def generate_hashtag_content(
    hashtag: str,
    current_user: User = Depends(get_current_user)
):
    """Generate content related to a specific hashtag"""
    try:
        response = gemini_service.generate_hashtag_content(hashtag)
        
        return {
            "hashtag": hashtag,
            "post_content": response["post_content"],
            "hashtags": response["hashtags"],
            "title": response["title"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate hashtag content: {str(e)}"
        )

@router.post("/create-content", status_code=status.HTTP_201_CREATED)
async def create_ai_content(
    post_generation: PostGeneration,
    current_user: User = Depends(get_current_user)
):
    """Create content using AI generation"""
    try:
        # Only allow admins to create content for other users
        if post_generation.user_id != current_user.id:
            # Check if current user is admin (this would need to be implemented)
            pass
            
        # Create a ContentCreate object
        content_create = ContentCreate(
            title=post_generation.title,
            description=post_generation.post_content,
            user_id=post_generation.user_id,
            file_path="",  # This would need to be updated with a real file path
            hashtags=post_generation.hashtags,
            is_private=False,
            allow_comments=True,
            is_ai_generated=True
        )
        
        # Create the content
        content = content_service.create_content(content_create)
        
        return content
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create content: {str(e)}"
        )

@router.post("/recommend", response_model=ContentRecommendation)
async def recommend_content(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Generate personalized content recommendations for a user"""
    try:
        # Only allow users to get recommendations for themselves or admins for any user
        if user_id != current_user.id:
            # Check if current user is admin (this would need to be implemented)
            pass
            
        # Get user interests and history from knowledge graph
        user_interests = kg_service.get_user_interests(user_id)
        user_history = content_service.get_user_content_history(user_id, limit=10)
        
        # Generate recommendations
        recommendations = gemini_service.generate_recommendations(user_id, user_interests, user_history)
        
        return {
            "user_id": user_id,
            "recommendations": recommendations["recommendations"],
            "explanation": recommendations["explanation"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate recommendations: {str(e)}"
        )

@router.post("/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_image(
    request: ImageAnalysisRequest,
    current_user: User = Depends(get_current_user)
):
    """Analyze an image using Gemini's multimodal capabilities"""
    try:
        # Analyze the image
        result = gemini_service.analyze_image(
            image_path=request.image_path,
            prompt=request.prompt
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze image: {str(e)}"
        ) 