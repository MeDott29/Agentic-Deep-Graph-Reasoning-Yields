"""
Users API endpoints for the Knowledge Graph Social Network System
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from datetime import datetime, timedelta

from models.user import UserCreate, UserUpdate, User
from services.knowledge_graph import KnowledgeGraphService
from services.user import UserService

# Create router
router = APIRouter()

# Create services
kg_service = KnowledgeGraphService()
user_service = UserService(kg_service)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token")

# Dependency to get current user
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user"""
    from jose import jwt, JWTError
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        from services.user import SECRET_KEY, ALGORITHM
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_service.get_user(user_id)
    if user is None:
        raise credentials_exception
    
    return user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate):
    """Register a new user"""
    try:
        user = user_service.create_user(user_create)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Get an access token"""
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = user_service.create_access_token(
        data={"sub": user.id},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get the current user"""
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update the current user"""
    updated_user = user_service.update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.post("/me/profile-picture", response_model=User)
async def upload_profile_picture(
    profile_picture: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload a profile picture"""
    import os
    from pathlib import Path
    
    # Create directory if it doesn't exist
    profile_pictures_dir = "src/data/profile_pictures"
    os.makedirs(profile_pictures_dir, exist_ok=True)
    
    # Save file
    file_ext = Path(profile_picture.filename).suffix
    file_path = os.path.join(profile_pictures_dir, f"{current_user.id}{file_ext}")
    
    with open(file_path, "wb") as f:
        f.write(await profile_picture.read())
    
    # Update user
    profile_picture_url = f"/api/users/{current_user.id}/profile-picture"
    user_update = UserUpdate(profile_picture_url=profile_picture_url)
    
    updated_user = user_service.update_user(current_user.id, user_update)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user

@router.get("/{user_id}", response_model=User)
async def get_user(user_id: str):
    """Get a user by ID"""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user

@router.get("/{user_id}/followers", response_model=List[User])
async def get_user_followers(
    user_id: str,
    limit: int = 100,
    offset: int = 0
):
    """Get a user's followers"""
    # Check if user exists
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    followers = user_service.get_followers(user_id, limit, offset)
    return followers

@router.get("/{user_id}/following", response_model=List[User])
async def get_user_following(
    user_id: str,
    limit: int = 100,
    offset: int = 0
):
    """Get users that a user is following"""
    # Check if user exists
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    following = user_service.get_following(user_id, limit, offset)
    return following

@router.post("/{user_id}/follow", response_model=User)
async def follow_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Follow a user"""
    # Check if user exists
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Can't follow yourself
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself"
        )
    
    success = user_service.follow_user(current_user.id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to follow user"
        )
    
    # Return updated user
    return user_service.get_user(user_id)

@router.post("/{user_id}/unfollow", response_model=User)
async def unfollow_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unfollow a user"""
    # Check if user exists
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    success = user_service.unfollow_user(current_user.id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to unfollow user"
        )
    
    # Return updated user
    return user_service.get_user(user_id)

@router.get("/search", response_model=List[User])
async def search_users(query: str, limit: int = 10):
    """Search for users"""
    users = user_service.search_users(query, limit)
    return users 