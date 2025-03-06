"""
Content API endpoints for the Knowledge Graph Social Network System
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Response
from fastapi.responses import FileResponse
from typing import List, Optional
import os
from datetime import datetime

from src.models.user import User
from src.models.content import ContentCreate, ContentUpdate, Content, Comment
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.content import ContentService
from src.services.recommendation import RecommendationService
from src.api.users import get_current_user

# Create router
router = APIRouter()

# Create services
kg_service = KnowledgeGraphService()
content_service = ContentService(kg_service)

@router.post("/", response_model=Content, status_code=status.HTTP_201_CREATED)
async def create_content(
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    hashtags: str = Form(""),
    is_private: bool = Form(False),
    allow_comments: bool = Form(True),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Create new content"""
    # Process hashtags
    hashtag_list = [tag.strip() for tag in hashtags.split(",") if tag.strip()]
    
    # Create content model
    content_create = ContentCreate(
        title=title,
        description=description,
        user_id=current_user.id,
        file_path=file.filename,
        hashtags=hashtag_list,
        is_private=is_private,
        allow_comments=allow_comments
    )
    
    # Read file data
    file_data = await file.read()
    
    # Create content
    content = content_service.create_content(content_create, file_data)
    
    return content

@router.get("/{content_id}", response_model=Content)
async def get_content(content_id: str):
    """Get content by ID"""
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return content

@router.get("/{content_id}/video")
async def get_content_video(content_id: str):
    """Get content video file"""
    content_in_db = content_service.content.get(content_id)
    if not content_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    file_path = content_in_db.file_path
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video file not found"
        )
    
    return FileResponse(file_path)

@router.get("/{content_id}/thumbnail")
async def get_content_thumbnail(content_id: str):
    """Get content thumbnail"""
    content_in_db = content_service.content.get(content_id)
    if not content_in_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    if not content_in_db.thumbnail_path or not os.path.exists(content_in_db.thumbnail_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Thumbnail not found"
        )
    
    return FileResponse(content_in_db.thumbnail_path)

@router.put("/{content_id}", response_model=Content)
async def update_content(
    content_id: str,
    content_update: ContentUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update content"""
    # Check if content exists
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if user is the owner
    if content.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this content"
        )
    
    # Update content
    updated_content = content_service.update_content(content_id, content_update)
    if not updated_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update content"
        )
    
    return updated_content

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(
    content_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete content"""
    # Check if content exists
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if user is the owner
    if content.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this content"
        )
    
    # Delete content
    success = content_service.delete_content(content_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete content"
        )
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/{content_id}/view")
async def record_view(
    content_id: str,
    duration: float,
    current_user: User = Depends(get_current_user)
):
    """Record a view of content"""
    # Check if content exists
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Record view in recommendation service
    recommendation_service = RecommendationService(kg_service)
    
    success = recommendation_service.record_interaction(
        user_id=current_user.id,
        content_id=content_id,
        interaction_type="view",
        data={"duration": duration}
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to record view"
        )
    
    return {"success": True}

@router.post("/{content_id}/like")
async def like_content(
    content_id: str,
    current_user: User = Depends(get_current_user)
):
    """Like content"""
    # Check if content exists
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Record like in recommendation service
    recommendation_service = RecommendationService(kg_service)
    
    success = recommendation_service.record_interaction(
        user_id=current_user.id,
        content_id=content_id,
        interaction_type="like"
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to like content"
        )
    
    # Update user interests
    recommendation_service.update_user_interests(current_user.id)
    
    return {"success": True}

@router.post("/{content_id}/share")
async def share_content(
    content_id: str,
    platform: str,
    current_user: User = Depends(get_current_user)
):
    """Share content"""
    # Check if content exists
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Record share in recommendation service
    recommendation_service = RecommendationService(kg_service)
    
    success = recommendation_service.record_interaction(
        user_id=current_user.id,
        content_id=content_id,
        interaction_type="share",
        data={"platform": platform}
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to share content"
        )
    
    return {"success": True}

@router.post("/{content_id}/comments", response_model=Comment)
async def add_comment(
    content_id: str,
    text: str,
    parent_comment_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Add a comment to content"""
    # Check if content exists
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Check if comments are allowed
    if not content.allow_comments:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Comments are not allowed for this content"
        )
    
    # Add comment
    comment = content_service.add_comment(
        content_id=content_id,
        user_id=current_user.id,
        text=text,
        parent_comment_id=parent_comment_id
    )
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to add comment"
        )
    
    # Record comment in recommendation service
    recommendation_service = RecommendationService(kg_service)
    
    recommendation_service.record_interaction(
        user_id=current_user.id,
        content_id=content_id,
        interaction_type="comment",
        data={"comment_id": comment.id}
    )
    
    return comment

@router.get("/{content_id}/comments", response_model=List[Comment])
async def get_comments(
    content_id: str,
    limit: int = 50,
    offset: int = 0
):
    """Get comments for content"""
    # Check if content exists
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    comments = content_service.get_comments(content_id, limit, offset)
    return comments

@router.get("/comments/{comment_id}/replies", response_model=List[Comment])
async def get_comment_replies(
    comment_id: str,
    limit: int = 20,
    offset: int = 0
):
    """Get replies to a comment"""
    replies = content_service.get_comment_replies(comment_id, limit, offset)
    return replies

@router.post("/comments/{comment_id}/like")
async def like_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Like a comment"""
    success = content_service.like_comment(comment_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to like comment"
        )
    
    return {"success": True}

@router.get("/user/{user_id}", response_model=List[Content])
async def get_user_content(
    user_id: str,
    limit: int = 20,
    offset: int = 0
):
    """Get content created by a user"""
    content_list = content_service.get_user_content(user_id, limit, offset)
    return content_list

@router.get("/search", response_model=List[Content])
async def search_content(query: str, limit: int = 20):
    """Search for content"""
    content_list = content_service.search_content(query, limit)
    return content_list

@router.get("/hashtag/{hashtag}", response_model=List[Content])
async def get_content_by_hashtag(
    hashtag: str,
    limit: int = 20,
    offset: int = 0
):
    """Get content with a specific hashtag"""
    content_list = content_service.get_content_by_hashtag(hashtag, limit, offset)
    return content_list

@router.get("/trending/hashtags")
async def get_trending_hashtags(limit: int = 10):
    """Get trending hashtags"""
    trending_hashtags = content_service.get_trending_hashtags(limit)
    return trending_hashtags 