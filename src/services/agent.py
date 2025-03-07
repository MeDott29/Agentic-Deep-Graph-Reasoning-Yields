import os
import json
import random
from typing import List, Dict, Any, Optional
from datetime import datetime

from models.agent import AgentCreate, AgentUpdate, AgentInDB, AgentMetrics, PersonalityTrait, ContentSpecialization, AgentPersonality
from models.user import User
from models.content import Content, ContentCreate, ContentInDB
from utils.openai_integration import generate_content_with_gpt

class AgentService:
    """Service for AI agent management and content generation."""
    
    def __init__(self):
        """Initialize agent service."""
        self.user_db_path = os.getenv("USER_DB_PATH", "./data/users.json")
        self.content_db_path = os.getenv("CONTENT_DB_PATH", "./data/content.json")
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Ensure the database files exist."""
        # User database
        os.makedirs(os.path.dirname(self.user_db_path), exist_ok=True)
        if not os.path.exists(self.user_db_path):
            with open(self.user_db_path, "w") as f:
                json.dump([], f)
        
        # Content database
        os.makedirs(os.path.dirname(self.content_db_path), exist_ok=True)
        if not os.path.exists(self.content_db_path):
            with open(self.content_db_path, "w") as f:
                json.dump({"content": [], "comments": []}, f)
    
    def _load_users(self) -> List[Dict[str, Any]]:
        """Load users from the database."""
        with open(self.user_db_path, "r") as f:
            return json.load(f)
    
    def _save_users(self, users: List[Dict[str, Any]]):
        """Save users to the database."""
        with open(self.user_db_path, "w") as f:
            json.dump(users, f, default=str)
    
    def _load_content(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load content from the database."""
        with open(self.content_db_path, "r") as f:
            return json.load(f)
    
    def _save_content(self, content: Dict[str, List[Dict[str, Any]]]):
        """Save content to the database."""
        with open(self.content_db_path, "w") as f:
            json.dump(content, f, default=str)
    
    def create_agent(self, agent_create: AgentCreate) -> User:
        """Create a new AI agent profile."""
        users = self._load_users()
        
        # Check if username already exists
        for user in users:
            if user.get("username") == agent_create.username:
                raise ValueError("Username already exists")
        
        # Create agent with AgentInDB model
        agent_data = agent_create.dict()
        agent_data["type"] = "ai_agent"
        agent = AgentInDB(**agent_data)
        
        # Convert to dict and add to database
        agent_dict = agent.dict()
        users.append(agent_dict)
        self._save_users(users)
        
        # Return User model
        return User(
            id=agent.id,
            username=agent.username,
            display_name=agent.display_name,
            bio=agent.bio,
            profile_image_url=agent.profile_image_url,
            type=agent.type,
            followers_count=agent.followers_count,
            following_count=agent.following_count,
            content_count=agent.content_count,
            created_at=agent.created_at
        )
    
    def get_agent(self, agent_id: str) -> Optional[AgentInDB]:
        """Get agent by ID."""
        users = self._load_users()
        for user_data in users:
            if user_data.get("id") == agent_id and user_data.get("type") == "ai_agent":
                return AgentInDB(**user_data)
        return None
    
    def update_agent(self, agent_id: str, agent_update: AgentUpdate) -> User:
        """Update agent personality parameters."""
        users = self._load_users()
        
        for i, user_data in enumerate(users):
            if user_data.get("id") == agent_id and user_data.get("type") == "ai_agent":
                # Update only provided fields
                update_data = agent_update.dict(exclude_unset=True)
                for key, value in update_data.items():
                    user_data[key] = value
                
                # Update timestamp
                user_data["updated_at"] = datetime.now()
                
                # Save to database
                users[i] = user_data
                self._save_users(users)
                
                # Return updated agent
                agent = AgentInDB(**user_data)
                return User(
                    id=agent.id,
                    username=agent.username,
                    display_name=agent.display_name,
                    bio=agent.bio,
                    profile_image_url=agent.profile_image_url,
                    type=agent.type,
                    followers_count=agent.followers_count,
                    following_count=agent.following_count,
                    content_count=agent.content_count,
                    created_at=agent.created_at
                )
        
        return None
    
    def list_agents(self, skip: int = 0, limit: int = 100) -> List[User]:
        """List all AI agents."""
        users = self._load_users()
        agents = []
        
        for user_data in users:
            if user_data.get("type") == "ai_agent":
                agent = AgentInDB(**user_data)
                agents.append(User(
                    id=agent.id,
                    username=agent.username,
                    display_name=agent.display_name,
                    bio=agent.bio,
                    profile_image_url=agent.profile_image_url,
                    type=agent.type,
                    followers_count=agent.followers_count,
                    following_count=agent.following_count,
                    content_count=agent.content_count,
                    created_at=agent.created_at
                ))
        
        # Apply pagination
        return agents[skip:skip+limit]
    
    def generate_content(self, agent_id: str) -> Content:
        """Generate content for an agent using GPT-4o."""
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        # Get agent's specializations
        specializations = agent.personality.content_specializations
        if specializations:
            # Pick a random specialization weighted by expertise level
            weights = [spec.expertise_level for spec in specializations]
            total_weight = sum(weights)
            normalized_weights = [w / total_weight for w in weights]
            chosen_spec = random.choices(specializations, weights=normalized_weights, k=1)[0]
            topic = chosen_spec.topic
        else:
            topic = "general"
        
        # Determine content type (text, image, video, mixed)
        content_type = random.choices(
            ["text", "image", "video", "mixed"],
            weights=[0.5, 0.3, 0.1, 0.1],  # Text is most common
            k=1
        )[0]
        
        # Use OpenAI to generate content
        try:
            # Convert agent personality to dict for the OpenAI function
            personality_dict = {
                "traits": [{"name": trait.name, "value": trait.value} for trait in agent.personality.traits],
                "content_specializations": [{"topic": spec.topic, "expertise_level": spec.expertise_level} 
                                          for spec in agent.personality.content_specializations],
                "creativity": agent.personality.creativity,
                "sociability": agent.personality.sociability,
                "controversy_tolerance": agent.personality.controversy_tolerance
            }
            
            # Check if OpenAI API key is set
            if not os.getenv("OPENAI_API_KEY"):
                print(f"OpenAI API key not set. Using fallback content generation for agent {agent.username}.")
                raise ValueError("OpenAI API key not set")
            
            # Generate content
            generated_content = generate_content_with_gpt(
                agent_personality=personality_dict,
                topic=topic,
                content_type=content_type,
                temperature=agent.personality.creativity  # Use creativity as temperature
            )
            
            # Create content
            content_create = ContentCreate(
                title=generated_content["title"],
                text_content=generated_content["text_content"],
                media_urls=generated_content["media_urls"],
                hashtags=generated_content["hashtags"],
                type=generated_content["type"]
            )
        except Exception as e:
            print(f"OpenAI content generation failed for agent {agent.username}: {e}. Using fallback method.")
            
            # Generate simple content
            content_create = self._generate_fallback_content(topic, content_type)
        
        # Save content to database
        content_data = self._load_content()
        content_obj = ContentInDB(**content_create.dict(), creator_id=agent_id)
        content_dict = content_obj.dict()
        content_data["content"].append(content_dict)
        self._save_content(content_data)
        
        # Update agent's content count and last generation time
        users = self._load_users()
        for i, user_data in enumerate(users):
            if user_data.get("id") == agent_id:
                user_data["content_count"] = user_data.get("content_count", 0) + 1
                if "metrics" not in user_data:
                    user_data["metrics"] = {}
                if "content_generated" not in user_data["metrics"]:
                    user_data["metrics"]["content_generated"] = 0
                user_data["metrics"]["content_generated"] += 1
                user_data["last_content_generation"] = datetime.now()
                users[i] = user_data
                break
        self._save_users(users)
        
        # Return Content model
        return Content(
            id=content_obj.id,
            title=content_obj.title,
            text_content=content_obj.text_content,
            media_urls=content_obj.media_urls,
            hashtags=content_obj.hashtags,
            references=content_obj.references,
            type=content_obj.type,
            creator_id=content_obj.creator_id,
            view_count=content_obj.view_count,
            like_count=content_obj.like_count,
            share_count=content_obj.share_count,
            comment_count=content_obj.comment_count,
            avg_view_duration=content_obj.avg_view_duration,
            created_at=content_obj.created_at
        )
    
    def _generate_fallback_content(self, topic: str, content_type: str) -> ContentCreate:
        """Generate fallback content when OpenAI API fails."""
        # Simple templates for different topics
        templates = {
            "artificial intelligence": "The future of AI looks promising with recent advancements.",
            "visual art": "Exploring the intersection of art and emotion in contemporary works.",
            "philosophy": "Examining the ethical implications in modern society.",
            "physics": "Recent breakthroughs that challenge our understanding of reality.",
            "world history": "Forgotten episodes in history that deserve more attention.",
            "futurism": "Predicting the next decade based on current trends.",
            "music": "How music transcends cultural boundaries and connects diverse audiences.",
            "psychology": "Understanding behavioral patterns and how they influence decision-making.",
            "ecology": "How ecological principles can guide sustainable development.",
            "cultural anthropology": "Comparing cultural practices across different societies."
        }
        
        # Get template or use generic one
        text_content = templates.get(topic, f"Exploring the fascinating world of {topic} and its implications.")
        
        # Generate title
        title = f"Thoughts on {topic}"
        
        # Generate hashtags
        topic_words = topic.split()
        hashtags = [f"#{word.lower()}" for word in topic_words if len(word) > 3]
        hashtags.append("#trending")
        
        # Create media URLs if needed
        media_urls = []
        if content_type != "text":
            media_count = 1 if content_type != "mixed" else random.randint(1, 3)
            for i in range(media_count):
                media_type = "image" if content_type == "image" else "video" if content_type == "video" else random.choice(["image", "video"])
                media_id = random.randint(1000, 9999)
                media_urls.append(f"https://example.com/{media_type}/{media_id}")
        
        # Create content
        return ContentCreate(
            title=title,
            text_content=text_content,
            media_urls=media_urls,
            hashtags=hashtags,
            type=content_type
        )
    
    def get_agent_metrics(self, agent_id: str) -> AgentMetrics:
        """Get agent performance metrics."""
        agent = self.get_agent(agent_id)
        if not agent:
            raise ValueError("Agent not found")
        
        return agent.metrics
    
    def get_agent_content(self, agent_id: str, skip: int = 0, limit: int = 20) -> List[Content]:
        """Get content created by an agent."""
        content_data = self._load_content()
        results = []
        
        for content_item in content_data["content"]:
            if content_item.get("creator_id") == agent_id:
                content = ContentInDB(**content_item)
                results.append(Content(
                    id=content.id,
                    title=content.title,
                    text_content=content.text_content,
                    media_urls=content.media_urls,
                    hashtags=content.hashtags,
                    references=content.references,
                    type=content.type,
                    creator_id=content.creator_id,
                    view_count=content.view_count,
                    like_count=content.like_count,
                    share_count=content.share_count,
                    comment_count=content.comment_count,
                    avg_view_duration=content.avg_view_duration,
                    created_at=content.created_at
                ))
        
        # Sort by creation time (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return results[skip:skip+limit]
    
    def get_leaderboard(self, metric: str = "followers_count", limit: int = 10) -> List[User]:
        """Get agent performance rankings."""
        users = self._load_users()
        agents = []
        
        for user_data in users:
            if user_data.get("type") == "ai_agent":
                # Get metric value
                if metric == "followers_count":
                    metric_value = user_data.get("followers_count", 0)
                elif metric == "content_count":
                    metric_value = user_data.get("content_count", 0)
                elif metric in ["avg_engagement_rate", "avg_view_duration"]:
                    metrics = user_data.get("metrics", {})
                    metric_value = metrics.get(metric, 0)
                else:
                    metric_value = 0
                
                # Add agent with metric value
                agent = AgentInDB(**user_data)
                agents.append((User(
                    id=agent.id,
                    username=agent.username,
                    display_name=agent.display_name,
                    bio=agent.bio,
                    profile_image_url=agent.profile_image_url,
                    type=agent.type,
                    followers_count=agent.followers_count,
                    following_count=agent.following_count,
                    content_count=agent.content_count,
                    created_at=agent.created_at
                ), metric_value))
        
        # Sort by metric value (highest first)
        agents.sort(key=lambda x: x[1], reverse=True)
        
        # Apply limit and return only the User objects
        return [agent for agent, _ in agents[:limit]]
    
    def generate_batch_content(self, count: int = 10) -> List[Content]:
        """Generate content from multiple agents."""
        # Get all agents
        agents = self.list_agents()
        if not agents:
            return []
        
        # Generate content for random agents
        results = []
        for _ in range(min(count, len(agents))):
            agent = random.choice(agents)
            try:
                content = self.generate_content(agent.id)
                results.append(content)
            except Exception as e:
                # Skip failed content generation
                print(f"Failed to generate content for agent {agent.username}: {e}")
                continue
        
        return results 