"""
Recommendations API endpoints for the Knowledge Graph Social Network System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any

from src.models.user import User
from src.models.recommendation import RecommendationRequest, RecommendationResponse
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.recommendation import RecommendationService
from src.api.users import get_current_user

# Create router
router = APIRouter()

# Create services
kg_service = KnowledgeGraphService()
recommendation_service = RecommendationService(kg_service)

@router.post("/feed", response_model=RecommendationResponse)
async def get_personalized_feed(
    count: int = 10,
    exclude_seen: bool = True,
    include_following: bool = True,
    include_trending: bool = True,
    categories: Optional[List[str]] = None,
    max_duration: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """Get a personalized feed for the current user"""
    # Create recommendation request
    request = RecommendationRequest(
        user_id=current_user.id,
        count=count,
        exclude_seen=exclude_seen,
        include_following=include_following,
        include_trending=include_trending,
        categories=categories,
        max_duration=max_duration
    )
    
    # Get recommendations
    recommendations = recommendation_service.get_recommendations(request)
    
    return recommendations

@router.get("/trending")
async def get_trending_content(limit: int = 10):
    """Get trending content"""
    trending_content = kg_service.get_trending_content(limit=limit)
    
    # Format response
    formatted_content = []
    for item in trending_content:
        node_data = item.get('node_data', {})
        properties = node_data.get('properties', {})
        
        content_details = {
            'id': item.get('content_id'),
            'title': properties.get('title'),
            'description': properties.get('description'),
            'user_id': properties.get('user_id'),
            'hashtags': properties.get('hashtags', []),
            'view_count': properties.get('view_count', 0),
            'like_count': properties.get('like_count', 0),
            'comment_count': properties.get('comment_count', 0),
            'share_count': properties.get('share_count', 0),
            'trending_score': item.get('trending_score', 0)
        }
        
        formatted_content.append(content_details)
    
    return {"trending_content": formatted_content}

@router.get("/similar-content/{content_id}")
async def get_similar_content(content_id: str, limit: int = 10):
    """Get content similar to the specified content"""
    similar_content = recommendation_service.find_similar_content(content_id, limit)
    
    # Format response
    formatted_content = []
    for item in similar_content:
        node_data = item.get('node_data', {})
        properties = node_data.get('properties', {})
        
        content_details = {
            'id': item.get('content_id'),
            'title': properties.get('title'),
            'description': properties.get('description'),
            'user_id': properties.get('user_id'),
            'hashtags': properties.get('hashtags', []),
            'view_count': properties.get('view_count', 0),
            'like_count': properties.get('like_count', 0),
            'comment_count': properties.get('comment_count', 0),
            'share_count': properties.get('share_count', 0),
            'similarity_score': item.get('similarity_score', 0)
        }
        
        formatted_content.append(content_details)
    
    return {"similar_content": formatted_content}

@router.get("/similar-users/{user_id}")
async def get_similar_users(
    user_id: str, 
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get users similar to the specified user"""
    # Only allow users to see similar users to themselves or if they're checking a public profile
    if user_id != current_user.id:
        # In a real app, you'd check if the target user's profile is public
        pass
    
    similar_users = kg_service.get_similar_users(user_id, limit)
    
    # Format response
    formatted_users = []
    for item in similar_users:
        node_data = item.get('node_data', {})
        properties = node_data.get('properties', {})
        
        user_details = {
            'id': item.get('user_id'),
            'username': properties.get('username'),
            'full_name': properties.get('full_name'),
            'bio': properties.get('bio'),
            'follower_count': properties.get('follower_count', 0),
            'following_count': properties.get('following_count', 0),
            'similarity_score': item.get('score', 0)
        }
        
        formatted_users.append(user_details)
    
    return {"similar_users": formatted_users}

@router.post("/update-interests")
async def update_user_interests(current_user: User = Depends(get_current_user)):
    """Update the current user's interests based on their interactions"""
    success = recommendation_service.update_user_interests(current_user.id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update user interests"
        )
    
    return {"success": True, "message": "User interests updated successfully"} 