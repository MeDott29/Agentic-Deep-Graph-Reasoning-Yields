from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Optional
from datetime import datetime, timedelta
import os
from jose import JWTError, jwt
from passlib.context import CryptContext

from models.user import User, UserCreate, UserUpdate, UserInDB, Token, TokenData
from services.user import UserService

# Create router
router = APIRouter()

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "development_secret_key")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Initialize user service
user_service = UserService()

def verify_password(plain_password, hashed_password):
    """Verify password against hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Hash password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get current user from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    user = user_service.get_user(token_data.user_id)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate):
    """Register a new human user."""
    # Check if username already exists
    if user_service.get_user_by_username(user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user_service.get_user_by_email(user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user with hashed password
    hashed_password = get_password_hash(user_create.password)
    user_data = user_create.dict()
    user_data.pop("password")
    user_data["hashed_password"] = hashed_password
    user_data["type"] = "human"
    
    return user_service.create_user(user_data)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """Authenticate user and provide access token."""
    user = user_service.authenticate_user(form_data.username, form_data.password, verify_password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """Get current user information."""
    return current_user

@router.put("/me", response_model=User)
async def update_user_me(user_update: UserUpdate, current_user: User = Depends(get_current_user)):
    """Update current user information."""
    return user_service.update_user(current_user.id, user_update)

@router.get("/{user_id}", response_model=User)
async def read_user(user_id: str):
    """Get user by ID."""
    user = user_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/followers", response_model=List[User])
async def read_user_followers(user_id: str, skip: int = 0, limit: int = 100):
    """Get user's followers."""
    return user_service.get_user_followers(user_id, skip, limit)

@router.get("/{user_id}/following", response_model=List[User])
async def read_user_following(user_id: str, skip: int = 0, limit: int = 100):
    """Get users followed by user."""
    return user_service.get_user_following(user_id, skip, limit)

@router.post("/{user_id}/follow", response_model=User)
async def follow_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Follow a user."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot follow yourself")
    return user_service.follow_user(current_user.id, user_id)

@router.post("/{user_id}/unfollow", response_model=User)
async def unfollow_user(user_id: str, current_user: User = Depends(get_current_user)):
    """Unfollow a user."""
    return user_service.unfollow_user(current_user.id, user_id)

@router.get("/search", response_model=List[User])
async def search_users(query: str, skip: int = 0, limit: int = 20):
    """Search for users and agents."""
    return user_service.search_users(query, skip, limit) 