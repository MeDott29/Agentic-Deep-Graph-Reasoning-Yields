from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from models.user import User
from models.content import Content, ContentCreate, ContentUpdate, ContentView, ContentInteraction, Comment, CommentCreate
from services.content import ContentService
from api.users import get_current_user

# Create router
router = APIRouter()

# Initialize content service
content_service = ContentService()

@router.post("/", response_model=Content, status_code=status.HTTP_201_CREATED)
async def create_content(content_create: ContentCreate, current_user: User = Depends(get_current_user)):
    """Create new content (available to both humans and agents)."""
    return content_service.create_content(current_user.id, content_create)

@router.get("/{content_id}", response_model=Content)
async def read_content(content_id: str):
    """Get content by ID."""
    content = content_service.get_content(content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.put("/{content_id}", response_model=Content)
async def update_content(content_id: str, content_update: ContentUpdate, current_user: User = Depends(get_current_user)):
    """Update content."""
    # Check if user is the creator
    content = content_service.get_content(content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this content")
    
    return content_service.update_content(content_id, content_update)

@router.delete("/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_content(content_id: str, current_user: User = Depends(get_current_user)):
    """Delete content."""
    # Check if user is the creator
    content = content_service.get_content(content_id)
    if content is None:
        raise HTTPException(status_code=404, detail="Content not found")
    if content.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this content")
    
    content_service.delete_content(content_id)
    return {"detail": "Content deleted"}

@router.post("/{content_id}/view")
async def record_content_view(content_id: str, view_data: ContentView, current_user: Optional[User] = Depends(get_current_user)):
    """Record content view and view duration."""
    user_id = current_user.id if current_user else None
    if view_data.user_id and current_user and view_data.user_id != current_user.id:
        raise HTTPException(status_code=400, detail="User ID mismatch")
    
    content_service.record_view(content_id, user_id or view_data.user_id, view_data.view_duration)
    return {"detail": "View recorded"}

@router.post("/{content_id}/like", response_model=Content)
async def like_content(content_id: str, current_user: User = Depends(get_current_user)):
    """Like content."""
    return content_service.like_content(content_id, current_user.id)

@router.post("/{content_id}/unlike", response_model=Content)
async def unlike_content(content_id: str, current_user: User = Depends(get_current_user)):
    """Unlike content."""
    return content_service.unlike_content(content_id, current_user.id)

@router.post("/{content_id}/share", response_model=Content)
async def share_content(content_id: str, current_user: User = Depends(get_current_user)):
    """Share content."""
    return content_service.share_content(content_id, current_user.id)

@router.post("/{content_id}/comments", response_model=Comment)
async def create_comment(content_id: str, comment_create: CommentCreate, current_user: User = Depends(get_current_user)):
    """Add comment to content."""
    return content_service.create_comment(content_id, current_user.id, comment_create)

@router.get("/{content_id}/comments", response_model=List[Comment])
async def read_content_comments(content_id: str, skip: int = 0, limit: int = 100):
    """Get content comments."""
    return content_service.get_content_comments(content_id, skip, limit)

@router.get("/search", response_model=List[Content])
async def search_content(query: str, skip: int = 0, limit: int = 20):
    """Search for content."""
    return content_service.search_content(query, skip, limit)

@router.get("/hashtag/{hashtag}", response_model=List[Content])
async def get_content_by_hashtag(hashtag: str, skip: int = 0, limit: int = 20):
    """Get content by hashtag."""
    return content_service.get_content_by_hashtag(hashtag, skip, limit)

@router.get("/feed", response_model=List[Content])
async def get_personalized_feed(skip: int = 0, limit: int = 20, current_user: Optional[User] = Depends(get_current_user)):
    """Get personalized content feed."""
    user_id = current_user.id if current_user else None
    return content_service.get_personalized_feed(user_id, skip, limit)

@router.get("/trending", response_model=List[Content])
async def get_trending_content(skip: int = 0, limit: int = 20):
    """Get trending content."""
    return content_service.get_trending_content(skip, limit) 