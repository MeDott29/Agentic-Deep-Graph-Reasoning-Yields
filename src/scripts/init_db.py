"""
Database Initialization Script for Knowledge Graph Social Network System

This script initializes the knowledge graph database with sample data for testing.
It creates users, content, hashtags, and relationships between them.
"""
import os
import sys
import json
import uuid
import random
from datetime import datetime, timedelta
import networkx as nx

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.knowledge_graph import KnowledgeGraphService
from services.user import UserService
from services.content import ContentService
from models.user import UserCreate, UserPreferences
from models.content import ContentCreate, Comment
from models.base import GraphNode, GraphEdge

# Create services
kg_service = KnowledgeGraphService()
user_service = UserService(kg_service)
content_service = ContentService(kg_service)

# Sample data
SAMPLE_USERS = [
    {
        "username": "techguru",
        "email": "techguru@example.com",
        "password": "Password123!",
        "full_name": "Tech Guru",
        "bio": "Technology enthusiast and content creator",
        "preferences": {
            "user_id": "user_1",
            "content_categories": ["technology", "programming", "gadgets"],
            "preferred_languages": ["en"],
            "explicit_content_allowed": False,
            "autoplay_enabled": True
        }
    },
    {
        "username": "travelbug",
        "email": "travelbug@example.com",
        "password": "Password123!",
        "full_name": "Travel Bug",
        "bio": "Exploring the world one video at a time",
        "preferences": {
            "user_id": "user_2",
            "content_categories": ["travel", "adventure", "food"],
            "preferred_languages": ["en"],
            "explicit_content_allowed": False,
            "autoplay_enabled": True
        }
    },
    {
        "username": "fitnessfanatic",
        "email": "fitness@example.com",
        "password": "Password123!",
        "full_name": "Fitness Fanatic",
        "bio": "Helping you achieve your fitness goals",
        "preferences": {
            "user_id": "user_3",
            "content_categories": ["fitness", "health", "nutrition"],
            "preferred_languages": ["en"],
            "explicit_content_allowed": False,
            "autoplay_enabled": True
        }
    },
    {
        "username": "foodie",
        "email": "foodie@example.com",
        "password": "Password123!",
        "full_name": "Food Lover",
        "bio": "Cooking and eating my way through life",
        "preferences": {
            "user_id": "user_4",
            "content_categories": ["food", "cooking", "recipes"],
            "preferred_languages": ["en"],
            "explicit_content_allowed": False,
            "autoplay_enabled": True
        }
    },
    {
        "username": "gamer",
        "email": "gamer@example.com",
        "password": "Password123!",
        "full_name": "Pro Gamer",
        "bio": "Gaming content creator and streamer",
        "preferences": {
            "user_id": "user_5",
            "content_categories": ["gaming", "esports", "technology"],
            "preferred_languages": ["en"],
            "explicit_content_allowed": True,
            "autoplay_enabled": True
        }
    }
]

SAMPLE_CONTENT = [
    {
        "user_index": 0,  # techguru
        "title": "Top 10 Tech Gadgets of 2023",
        "description": "Check out these amazing tech gadgets that will change your life!",
        "hashtags": ["tech", "gadgets", "innovation"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 0,  # techguru
        "title": "Python Programming Tutorial for Beginners",
        "description": "Learn the basics of Python programming in this beginner-friendly tutorial.",
        "hashtags": ["programming", "python", "tutorial"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 1,  # travelbug
        "title": "Exploring the Hidden Beaches of Bali",
        "description": "Discover these secret beaches in Bali that tourists don't know about!",
        "hashtags": ["travel", "bali", "beaches"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 1,  # travelbug
        "title": "Street Food Tour in Bangkok",
        "description": "Join me as I try the best street food in Bangkok, Thailand!",
        "hashtags": ["travel", "food", "bangkok"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 2,  # fitnessfanatic
        "title": "10-Minute HIIT Workout for Busy People",
        "description": "No time to exercise? Try this quick HIIT workout that you can do anywhere!",
        "hashtags": ["fitness", "workout", "hiit"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 2,  # fitnessfanatic
        "title": "Healthy Meal Prep for the Week",
        "description": "Learn how to meal prep for a healthy week ahead with these simple recipes.",
        "hashtags": ["fitness", "nutrition", "mealprep"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 3,  # foodie
        "title": "Easy Pasta Carbonara Recipe",
        "description": "Learn how to make authentic Italian carbonara in just 15 minutes!",
        "hashtags": ["food", "recipe", "italian"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 3,  # foodie
        "title": "Best Burger Joints in New York City",
        "description": "I tried the top-rated burger places in NYC. Here's my ranking!",
        "hashtags": ["food", "burgers", "nyc"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 4,  # gamer
        "title": "Minecraft Building Tips and Tricks",
        "description": "Improve your Minecraft building skills with these pro tips!",
        "hashtags": ["gaming", "minecraft", "tutorial"],
        "allow_comments": True,
        "privacy": "public"
    },
    {
        "user_index": 4,  # gamer
        "title": "Call of Duty: Warzone Gameplay Highlights",
        "description": "Check out these epic moments from my recent Warzone matches!",
        "hashtags": ["gaming", "callofduty", "warzone"],
        "allow_comments": True,
        "privacy": "public"
    }
]

SAMPLE_COMMENTS = [
    "Great video! Really enjoyed it.",
    "Thanks for sharing this!",
    "I learned so much from this.",
    "Can you make more content like this?",
    "This is exactly what I was looking for!",
    "Amazing content as always!",
    "I disagree with some points, but overall good video.",
    "First time watching your content, definitely subscribing!",
    "The quality of your videos keeps improving!",
    "Could you do a follow-up on this topic?"
]

def create_sample_users():
    """Create sample users in the database"""
    print("Creating sample users...")
    created_users = []
    
    for user_data in SAMPLE_USERS:
        # Create user without preferences first
        user_create = UserCreate(
            username=user_data["username"],
            email=user_data["email"],
            password=user_data["password"],
            full_name=user_data["full_name"],
            bio=user_data["bio"]
        )
        
        try:
            # Create the user
            user = user_service.create_user(user_create)
            
            # Now create preferences with the actual user_id
            preferences_data = user_data["preferences"].copy()
            preferences_data["user_id"] = user.id
            
            # Store preferences in the knowledge graph
            preferences = UserPreferences(**preferences_data)
            
            # Add preferences to the knowledge graph
            kg_service.add_node_property(
                node_id=user.id,
                node_type="USER",
                property_name="preferences",
                property_value=preferences.model_dump()
            )
            
            created_users.append(user)
            print(f"Created user: {user.username}")
        except Exception as e:
            print(f"Error creating user {user_data['username']}: {str(e)}")
    
    return created_users

def create_sample_content(users):
    """Create sample content in the database"""
    print("Creating sample content...")
    created_content = []
    
    # If no users were created, return empty list
    if not users:
        print("No users available to create content. Skipping content creation.")
        return created_content
    
    for content_data in SAMPLE_CONTENT:
        # Check if user_index is valid
        if content_data["user_index"] >= len(users):
            print(f"Invalid user index {content_data['user_index']}. Skipping content.")
            continue
            
        user = users[content_data["user_index"]]
        
        # Create a dummy file path for sample content
        dummy_file_path = f"src/data/sample_videos/{content_data['title'].lower().replace(' ', '_')}.mp4"
        
        content_create = ContentCreate(
            title=content_data["title"],
            description=content_data["description"],
            hashtags=content_data["hashtags"],
            allow_comments=content_data["allow_comments"],
            is_private=content_data["privacy"] == "private",
            user_id=user.id,
            file_path=dummy_file_path
        )
        
        try:
            # In a real implementation, we would upload a file
            # For this sample, we'll just create the content without a file
            content = content_service.create_content(
                content_create=content_create,
                file_data=None  # No actual file data for this sample
            )
            
            # Manually set some engagement metrics
            content.view_count = random.randint(100, 10000)
            content.like_count = random.randint(10, content.view_count // 10)
            content.comment_count = random.randint(5, content.like_count // 2)
            content.share_count = random.randint(1, content.like_count // 5)
            
            # Update the content in the database
            content_service.contents[content.id] = content
            content_service._save_content()
            
            # Update the node in the knowledge graph
            kg_service.add_node_property(
                node_id=content.id,
                node_type="CONTENT",
                property_name="metrics",
                property_value={
                    "view_count": content.view_count,
                    "like_count": content.like_count,
                    "comment_count": content.comment_count,
                    "share_count": content.share_count
                }
            )
            
            created_content.append(content)
            print(f"Created content: {content.title}")
        except Exception as e:
            print(f"Error creating content '{content_data['title']}': {str(e)}")
    
    return created_content

def create_sample_interactions(users, content_items):
    """Create sample interactions between users and content"""
    print("Creating sample interactions...")
    
    # Check if we have users and content
    if not users or not content_items:
        print("Not enough users or content to create interactions. Skipping.")
        return
    
    # Create follows between users
    for i, user in enumerate(users):
        # Each user follows some other users
        for j in range(len(users)):
            if i != j and random.random() < 0.7:  # 70% chance to follow
                try:
                    user_service.follow_user(user.id, users[j].id)
                    print(f"{user.username} followed {users[j].username}")
                except Exception as e:
                    print(f"Error creating follow: {str(e)}")
    
    # Create likes, views, and comments on content
    for content in content_items:
        content_owner_id = content.user_id
        
        # Users view, like, and comment on content
        for user in users:
            if user.id != content_owner_id:
                # View content (90% chance)
                if random.random() < 0.9:
                    try:
                        # Record a view
                        view_edge = GraphEdge(
                            source_id=user.id,
                            target_id=content.id,
                            edge_type="VIEWS",
                            properties={
                                "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                                "duration": random.randint(5, 60)  # View duration in seconds
                            }
                        )
                        kg_service.add_edge(view_edge)
                        
                        # Like content (60% chance if viewed)
                        if random.random() < 0.6:
                            like_edge = GraphEdge(
                                source_id=user.id,
                                target_id=content.id,
                                edge_type="LIKES",
                                properties={
                                    "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat()
                                }
                            )
                            kg_service.add_edge(like_edge)
                            
                            # Update content like count
                            content.like_count += 1
                        
                        # Comment on content (30% chance if viewed)
                        if random.random() < 0.3:
                            # Generate a random comment
                            comment_text = random.choice(SAMPLE_COMMENTS)
                            comment_id = str(uuid.uuid4())
                            
                            # Add comment to database
                            content_service.comments[comment_id] = Comment(
                                id=comment_id,
                                content_id=content.id,
                                user_id=user.id,
                                text=comment_text,
                                like_count=0,
                                created_at=datetime.now() - timedelta(days=random.randint(0, 30)),
                                updated_at=datetime.now() - timedelta(days=random.randint(0, 30))
                            )
                            
                            # Save comments to file
                            content_service._save_comments()
                            
                            # Add edge in knowledge graph
                            comment_edge = GraphEdge(
                                source_id=user.id,
                                target_id=content.id,
                                edge_type="COMMENTS",
                                properties={
                                    "created_at": (datetime.now() - timedelta(days=random.randint(0, 30))).isoformat(),
                                    "comment_id": comment_id
                                }
                            )
                            kg_service.add_edge(comment_edge)
                            print(f"{user.username} commented on '{content.title}'")
                    except Exception as e:
                        print(f"Error creating interaction: {str(e)}")

def create_sample_interests():
    """Create sample interest nodes and connect users to them"""
    print("Creating sample interest nodes...")
    
    # List of interests
    interests = [
        "technology", "programming", "gadgets", "travel", "adventure", 
        "food", "fitness", "health", "nutrition", "gaming", "esports",
        "cooking", "recipes", "fashion", "beauty", "music", "movies",
        "books", "photography", "art", "science", "history", "politics",
        "business", "finance", "sports", "outdoors", "pets", "animals",
        "diy", "crafts", "home", "garden", "parenting", "education"
    ]
    
    # Create interest nodes
    for interest in interests:
        try:
            # Create a GraphNode object
            interest_node = GraphNode(
                id=f"interest_{interest}",
                node_type="INTEREST",
                properties={
                    "name": interest,
                    "created_at": datetime.now().isoformat()
                }
            )
            
            # Add the node to the graph
            kg_service.add_node(interest_node)
            print(f"Created interest node: {interest}")
        except Exception as e:
            print(f"Error creating interest node '{interest}': {str(e)}")
    
    # Connect users to interests based on their preferences
    for user_id, user_data in user_service.users.items():
        if hasattr(user_data, "preferences") and hasattr(user_data.preferences, "content_categories"):
            for category in user_data.preferences.content_categories:
                if f"interest_{category}" in kg_service.graph.nodes:
                    try:
                        kg_service.add_edge(
                            source_id=user_id,
                            target_id=f"interest_{category}",
                            edge_type="INTERESTED_IN",
                            properties={
                                "created_at": datetime.now().isoformat(),
                                "weight": random.uniform(0.7, 1.0)  # Interest strength
                            }
                        )
                        print(f"Connected user {user_data.username} to interest {category}")
                    except Exception as e:
                        print(f"Error connecting user to interest: {str(e)}")

def main():
    """Main function to initialize the database"""
    print("Initializing database with sample data...")
    
    # Check if data already exists
    if kg_service.graph.number_of_nodes() > 0:
        response = input("Database already contains data. Do you want to reset it? (y/n): ")
        if response.lower() != 'y':
            print("Aborting initialization.")
            return
        
        # Reset the database
        kg_service.graph = nx.DiGraph()
        kg_service._save_graph()
        
        # Reset user and content data
        user_service.users = {}
        user_service._save_users()
        
        content_service.contents = {}
        content_service._save_content()
        content_service.comments = {}
        content_service._save_comments()
        
        print("Database reset complete.")
    
    # Create sample data
    users = create_sample_users()
    
    # Only proceed if users were created
    if users:
        content_items = create_sample_content(users)
        if content_items:
            create_sample_interactions(users, content_items)
        create_sample_interests()
        
        # Save all data
        kg_service._save_graph()
        
        print("Database initialization complete!")
        print(f"Created {len(users)} users")
        print(f"Created {len(content_items)} content items")
        print(f"Graph now has {kg_service.graph.number_of_nodes()} nodes and {kg_service.graph.number_of_edges()} edges")
    else:
        print("No users were created. Database initialization failed.")

if __name__ == "__main__":
    main() 