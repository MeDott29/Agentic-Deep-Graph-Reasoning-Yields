"""
User Service for the Knowledge Graph Social Network System
"""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import os
import json
import uuid
from passlib.context import CryptContext
from jose import jwt

from src.models.user import UserBase, UserCreate, UserUpdate, UserInDB, User, UserNode
from src.models.social import Follow
from src.services.knowledge_graph import KnowledgeGraphService

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")  # In production, use a secure key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserService:
    """Service for managing users"""
    
    def __init__(self, knowledge_graph_service: KnowledgeGraphService):
        """Initialize the user service"""
        self.kg_service = knowledge_graph_service
        self.users_file = "src/data/users.json"
        self.users = self._load_users()
    
    def _load_users(self) -> Dict[str, UserInDB]:
        """Load users from file"""
        if os.path.exists(self.users_file):
            try:
                with open(self.users_file, 'r') as f:
                    users_data = json.load(f)
                
                users = {}
                for user_data in users_data:
                    user = UserInDB(**user_data)
                    users[user.id] = user
                
                return users
            except Exception as e:
                print(f"Error loading users: {e}")
        
        return {}
    
    def _save_users(self):
        """Save users to file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.users_file), exist_ok=True)
        
        # Convert user objects to dictionaries with datetime handling
        users_data = []
        for user in self.users.values():
            user_dict = user.dict()
            # Convert datetime objects to ISO format strings
            for key, value in user_dict.items():
                if isinstance(value, datetime):
                    user_dict[key] = value.isoformat()
            users_data.append(user_dict)
        
        with open(self.users_file, 'w') as f:
            json.dump(users_data, f, indent=2)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        if user_id in self.users:
            user_in_db = self.users[user_id]
            return User(
                id=user_in_db.id,
                username=user_in_db.username,
                email=user_in_db.email,
                full_name=user_in_db.full_name,
                bio=user_in_db.bio,
                profile_picture=user_in_db.profile_picture,
                follower_count=user_in_db.follower_count,
                following_count=user_in_db.following_count,
                created_at=user_in_db.created_at,
                updated_at=user_in_db.updated_at
            )
        return None
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        for user_id, user in self.users.items():
            if user.username.lower() == username.lower():
                return self.get_user(user_id)
        return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        for user_id, user in self.users.items():
            if user.email.lower() == email.lower():
                return self.get_user(user_id)
        return None
    
    def create_user(self, user_create: UserCreate) -> User:
        """Create a new user"""
        # Check if username or email already exists
        if self.get_user_by_username(user_create.username):
            raise ValueError("Username already exists")
        
        if self.get_user_by_email(user_create.email):
            raise ValueError("Email already exists")
        
        # Create user
        user_id = str(uuid.uuid4())
        hashed_password = self._get_password_hash(user_create.password)
        
        user_in_db = UserInDB(
            id=user_id,
            username=user_create.username,
            email=user_create.email,
            full_name=user_create.full_name,
            bio=user_create.bio,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
            profile_picture=None,
            follower_count=0,
            following_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save user to database
        self.users[user_id] = user_in_db
        self._save_users()
        
        # Add user to knowledge graph
        user = self.get_user(user_id)
        user_node = UserNode(user)
        self.kg_service.add_node(user_node)
        
        return user
    
    def update_user(self, user_id: str, user_update: UserUpdate) -> Optional[User]:
        """Update a user"""
        if user_id not in self.users:
            return None
        
        user_in_db = self.users[user_id]
        
        # Update fields
        if user_update.full_name is not None:
            user_in_db.full_name = user_update.full_name
        
        if user_update.bio is not None:
            user_in_db.bio = user_update.bio
        
        if user_update.profile_picture is not None:
            user_in_db.profile_picture = user_update.profile_picture
        
        user_in_db.updated_at = datetime.utcnow()
        
        # Save user to database
        self.users[user_id] = user_in_db
        self._save_users()
        
        # Update user in knowledge graph
        user = self.get_user(user_id)
        user_node = UserNode(user)
        
        # Get existing node
        existing_node = self.kg_service.get_node(user_id)
        if existing_node:
            # Update properties
            self.kg_service.graph.nodes[user_id]['properties'] = user_node.properties
            self.kg_service._save_graph()
        
        return user
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        if user_id not in self.users:
            return False
        
        # Remove user from database
        del self.users[user_id]
        self._save_users()
        
        # Remove user from knowledge graph
        self.kg_service.remove_node(user_id)
        
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user"""
        user = self.get_user_by_username(username)
        if not user:
            return None
        
        user_in_db = self.users[user.id]
        if not self._verify_password(password, user_in_db.hashed_password):
            return None
        
        return user
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        
        return encoded_jwt
    
    def _get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    def _verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return pwd_context.verify(plain_password, hashed_password)
    
    def follow_user(self, follower_id: str, followed_id: str) -> bool:
        """Follow a user"""
        # Check if users exist
        if follower_id not in self.users or followed_id not in self.users:
            return False
        
        # Check if already following
        for _, target, edge_data in self.kg_service.graph.out_edges(follower_id, data=True):
            if target == followed_id and edge_data.get('edge_type') == 'FOLLOWS':
                return True  # Already following
        
        # Create follow relationship
        follow_edge = Follow(follower_id, followed_id)
        self.kg_service.add_edge(follow_edge)
        
        # Update follower counts
        follower = self.users[follower_id]
        followed = self.users[followed_id]
        
        follower.following_count += 1
        followed.follower_count += 1
        
        self._save_users()
        
        return True
    
    def unfollow_user(self, follower_id: str, followed_id: str) -> bool:
        """Unfollow a user"""
        # Check if users exist
        if follower_id not in self.users or followed_id not in self.users:
            return False
        
        # Check if following
        is_following = False
        for _, target, edge_data in self.kg_service.graph.out_edges(follower_id, data=True):
            if target == followed_id and edge_data.get('edge_type') == 'FOLLOWS':
                is_following = True
                break
        
        if not is_following:
            return False  # Not following
        
        # Remove follow relationship
        self.kg_service.remove_edge(follower_id, followed_id, edge_type='FOLLOWS')
        
        # Update follower counts
        follower = self.users[follower_id]
        followed = self.users[followed_id]
        
        follower.following_count = max(0, follower.following_count - 1)
        followed.follower_count = max(0, followed.follower_count - 1)
        
        self._save_users()
        
        return True
    
    def get_followers(self, user_id: str, limit: int = 100, offset: int = 0) -> List[User]:
        """Get a user's followers"""
        if user_id not in self.users:
            return []
        
        followers = []
        
        # Find all users who follow this user
        for source, _, edge_data in self.kg_service.graph.in_edges(user_id, data=True):
            if edge_data.get('edge_type') == 'FOLLOWS':
                follower = self.get_user(source)
                if follower:
                    followers.append(follower)
        
        # Apply pagination
        return followers[offset:offset+limit]
    
    def get_following(self, user_id: str, limit: int = 100, offset: int = 0) -> List[User]:
        """Get users that a user is following"""
        if user_id not in self.users:
            return []
        
        following = []
        
        # Find all users this user follows
        for _, target, edge_data in self.kg_service.graph.out_edges(user_id, data=True):
            if edge_data.get('edge_type') == 'FOLLOWS':
                followed = self.get_user(target)
                if followed:
                    following.append(followed)
        
        # Apply pagination
        return following[offset:offset+limit]
    
    def search_users(self, query: str, limit: int = 10) -> List[User]:
        """Search for users by username or full name"""
        results = []
        query = query.lower()
        
        for user_id, user in self.users.items():
            if (query in user.username.lower() or 
                (user.full_name and query in user.full_name.lower())):
                results.append(self.get_user(user_id))
                
                if len(results) >= limit:
                    break
        
        return results 