import os
import json
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.user import User, UserCreate, UserUpdate, UserInDB

class UserService:
    """Service for user management and authentication."""
    
    def __init__(self):
        """Initialize user service."""
        self.db_path = os.getenv("USER_DB_PATH", "./data/users.json")
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Ensure the user database file exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump([], f)
    
    def _load_users(self) -> List[Dict[str, Any]]:
        """Load users from the database."""
        with open(self.db_path, "r") as f:
            return json.load(f)
    
    def _save_users(self, users: List[Dict[str, Any]]):
        """Save users to the database."""
        with open(self.db_path, "w") as f:
            json.dump(users, f, default=str)
    
    def get_user(self, user_id: str) -> Optional[UserInDB]:
        """Get user by ID."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("id") == user_id:
                return UserInDB(**user_data)
        return None
    
    def get_user_by_username(self, username: str) -> Optional[UserInDB]:
        """Get user by username."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("username") == username:
                return UserInDB(**user_data)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """Get user by email."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("email") == email:
                return UserInDB(**user_data)
        return None
    
    def create_user(self, user_data: Dict[str, Any]) -> User:
        """Create a new user."""
        users = self._load_users()
        
        # Create user with UserInDB model
        user = UserInDB(**user_data)
        
        # Convert to dict and add to database
        user_dict = user.dict()
        users.append(user_dict)
        self._save_users(users)
        
        # Return User model (not UserInDB with hashed_password)
        return User(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            bio=user.bio,
            profile_image_url=user.profile_image_url,
            type=user.type,
            followers_count=user.followers_count,
            following_count=user.following_count,
            content_count=user.content_count,
            created_at=user.created_at
        )
    
    def update_user(self, user_id: str, user_update: UserUpdate) -> User:
        """Update user information."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == user_id:
                # Update only provided fields
                update_data = user_update.dict(exclude_unset=True)
                for key, value in update_data.items():
                    user_data[key] = value
                
                # Update timestamp
                user_data["updated_at"] = datetime.now()
                
                # Save to database
                users[i] = user_data
                self._save_users(users)
                
                # Return updated user
                user = UserInDB(**user_data)
                return User(
                    id=user.id,
                    username=user.username,
                    display_name=user.display_name,
                    bio=user.bio,
                    profile_image_url=user.profile_image_url,
                    type=user.type,
                    followers_count=user.followers_count,
                    following_count=user.following_count,
                    content_count=user.content_count,
                    created_at=user.created_at
                )
        
        return None
    
    def authenticate_user(self, username: str, password: str, verify_password_func) -> Optional[UserInDB]:
        """Authenticate user with username and password."""
        user = self.get_user_by_username(username)
        if not user:
            return None
        if not user.hashed_password:
            return None
        if not verify_password_func(password, user.hashed_password):
            return None
        return user
    
    def get_user_followers(self, user_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get user's followers."""
        # In a real implementation, this would query a followers table
        # For now, we'll return an empty list
        return []
    
    def get_user_following(self, user_id: str, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users followed by user."""
        # In a real implementation, this would query a followers table
        # For now, we'll return an empty list
        return []
    
    def follow_user(self, follower_id: str, followed_id: str) -> User:
        """Follow a user."""
        # In a real implementation, this would add a follower relationship
        # and update follower/following counts
        # For now, we'll just return the followed user
        return self.get_user(followed_id)
    
    def unfollow_user(self, follower_id: str, followed_id: str) -> User:
        """Unfollow a user."""
        # In a real implementation, this would remove a follower relationship
        # and update follower/following counts
        # For now, we'll just return the unfollowed user
        return self.get_user(followed_id)
    
    def search_users(self, query: str, skip: int = 0, limit: int = 20) -> List[User]:
        """Search for users and agents."""
        users = self._load_users()
        results = []
        
        query = query.lower()
        for user_data in users:
            username = user_data.get("username", "").lower()
            display_name = user_data.get("display_name", "").lower()
            bio = user_data.get("bio", "").lower()
            
            if query in username or query in display_name or query in bio:
                user = UserInDB(**user_data)
                results.append(User(
                    id=user.id,
                    username=user.username,
                    display_name=user.display_name,
                    bio=user.bio,
                    profile_image_url=user.profile_image_url,
                    type=user.type,
                    followers_count=user.followers_count,
                    following_count=user.following_count,
                    content_count=user.content_count,
                    created_at=user.created_at
                ))
        
        # Apply pagination
        return results[skip:skip+limit] 