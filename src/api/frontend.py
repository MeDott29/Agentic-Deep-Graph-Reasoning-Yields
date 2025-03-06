"""
Frontend routes for the Knowledge Graph Social Network System
"""
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

from src.models.user import User
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.user import UserService
from src.services.content import ContentService
from src.api.users import get_current_user_optional

# Create router
router = APIRouter()

# Create services
kg_service = KnowledgeGraphService()
user_service = UserService(kg_service)
content_service = ContentService(kg_service)

# Set up templates
templates_path = Path(__file__).parent.parent / "frontend" / "templates"
templates = Jinja2Templates(directory=str(templates_path))

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Render the home page"""
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "user": current_user}
    )

@router.get("/explore", response_class=HTMLResponse)
async def explore(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Render the explore page"""
    return templates.TemplateResponse(
        "index.html",  # Reuse the index template with different data
        {"request": request, "user": current_user, "page": "explore"}
    )

@router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Render the current user's profile page"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": current_user, "profile_user": current_user}
    )

@router.get("/profile/{username}", response_class=HTMLResponse)
async def user_profile(
    username: str,
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Render a user's profile page"""
    # Get user by username
    profile_user = user_service.get_user_by_username(username)
    
    if not profile_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return templates.TemplateResponse(
        "profile.html",
        {
            "request": request,
            "user": current_user,
            "profile_user": profile_user,
            "is_following": current_user and user_service.is_following(current_user.id, profile_user.id)
        }
    )

@router.get("/post/{post_id}", response_class=HTMLResponse)
async def post_detail(
    post_id: str,
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Render a post detail page"""
    # Get post by ID
    post = content_service.get_content(post_id)
    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    # Get post author
    post_author = user_service.get_user(post.user_id)
    
    # Get comments
    comments = content_service.get_comments(post_id)
    
    return templates.TemplateResponse(
        "post.html",
        {
            "request": request,
            "user": current_user,
            "post": post,
            "post_author": post_author,
            "comments": comments
        }
    )

@router.get("/hashtag/{hashtag}", response_class=HTMLResponse)
async def hashtag_page(
    hashtag: str,
    request: Request,
    current_user: User = Depends(get_current_user_optional)
):
    """Render a hashtag page"""
    return templates.TemplateResponse(
        "hashtag.html",
        {
            "request": request,
            "user": current_user,
            "hashtag": hashtag
        }
    )

@router.get("/notifications", response_class=HTMLResponse)
async def notifications(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Render the notifications page"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return templates.TemplateResponse(
        "notifications.html",
        {"request": request, "user": current_user}
    )

@router.get("/settings", response_class=HTMLResponse)
async def settings(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Render the settings page"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return templates.TemplateResponse(
        "settings.html",
        {"request": request, "user": current_user}
    )

@router.get("/analytics", response_class=HTMLResponse)
async def analytics(request: Request, current_user: User = Depends(get_current_user_optional)):
    """Render the analytics page"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    return templates.TemplateResponse(
        "analytics.html",
        {"request": request, "user": current_user}
    ) 