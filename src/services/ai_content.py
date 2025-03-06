"""
AI Content Generation Service for the Knowledge Graph Social Network System
"""
from typing import Dict, List, Any, Optional
import uuid
from datetime import datetime
import random
import json
import os

from models.content import ContentCreate, ContentInDB, Content
from services.knowledge_graph import KnowledgeGraphService

class AIContentGenerationService:
    """Service for generating AI content based on user preferences"""
    
    def __init__(self, knowledge_graph_service: KnowledgeGraphService):
        """Initialize the AI content generation service"""
        self.kg_service = knowledge_graph_service
        self.ai_agents_file = "src/data/ai_agents.json"
        self.ai_content_preferences_file = "src/data/ai_content_preferences.json"
        self.ai_agents = self._load_ai_agents()
        self.user_preferences = self._load_user_preferences()
        
    def _load_ai_agents(self) -> Dict[str, Dict[str, Any]]:
        """Load AI agents from file"""
        if os.path.exists(self.ai_agents_file):
            try:
                with open(self.ai_agents_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading AI agents: {e}")
        
        # Initialize with default agents if file doesn't exist
        default_agents = {
            str(uuid.uuid4()): {
                "name": "TravelAgent",
                "description": "Creates travel and adventure content",
                "specialties": ["travel", "adventure", "nature", "tourism"],
                "content_types": ["video", "image"]
            },
            str(uuid.uuid4()): {
                "name": "FoodieBot",
                "description": "Creates food and cooking content",
                "specialties": ["food", "cooking", "recipes", "restaurants"],
                "content_types": ["video", "image"]
            },
            str(uuid.uuid4()): {
                "name": "TechGuru",
                "description": "Creates technology and gadget content",
                "specialties": ["technology", "gadgets", "reviews", "tutorials"],
                "content_types": ["video", "tutorial"]
            },
            str(uuid.uuid4()): {
                "name": "FitnessCoach",
                "description": "Creates fitness and wellness content",
                "specialties": ["fitness", "workout", "health", "wellness"],
                "content_types": ["video", "tutorial"]
            },
            str(uuid.uuid4()): {
                "name": "FashionDesigner",
                "description": "Creates fashion and style content",
                "specialties": ["fashion", "style", "trends", "outfits"],
                "content_types": ["video", "image"]
            }
        }
        
        # Save default agents
        with open(self.ai_agents_file, 'w') as f:
            json.dump(default_agents, f, indent=2)
            
        return default_agents
    
    def _save_ai_agents(self):
        """Save AI agents to file"""
        with open(self.ai_agents_file, 'w') as f:
            json.dump(self.ai_agents, f, indent=2)
    
    def _load_user_preferences(self) -> Dict[str, Dict[str, Any]]:
        """Load user preferences for AI content"""
        if os.path.exists(self.ai_content_preferences_file):
            try:
                with open(self.ai_content_preferences_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading user preferences: {e}")
        
        return {}
    
    def _save_user_preferences(self):
        """Save user preferences to file"""
        with open(self.ai_content_preferences_file, 'w') as f:
            json.dump(self.user_preferences, f, indent=2)
    
    def get_ai_agents(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get list of AI agents"""
        agents = []
        for agent_id, agent_data in self.ai_agents.items():
            agents.append({
                "id": agent_id,
                **agent_data
            })
        
        return agents[:limit]
    
    def get_ai_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get AI agent by ID"""
        if agent_id in self.ai_agents:
            return {
                "id": agent_id,
                **self.ai_agents[agent_id]
            }
        return None
    
    def create_ai_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new AI agent"""
        agent_id = str(uuid.uuid4())
        self.ai_agents[agent_id] = {
            "name": agent_data.get("name", f"Agent-{agent_id[:8]}"),
            "description": agent_data.get("description", "AI content creator"),
            "specialties": agent_data.get("specialties", []),
            "content_types": agent_data.get("content_types", ["video"])
        }
        
        self._save_ai_agents()
        
        return {
            "id": agent_id,
            **self.ai_agents[agent_id]
        }
    
    def update_ai_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an AI agent"""
        if agent_id not in self.ai_agents:
            return None
        
        agent = self.ai_agents[agent_id]
        
        if "name" in agent_data:
            agent["name"] = agent_data["name"]
        if "description" in agent_data:
            agent["description"] = agent_data["description"]
        if "specialties" in agent_data:
            agent["specialties"] = agent_data["specialties"]
        if "content_types" in agent_data:
            agent["content_types"] = agent_data["content_types"]
        
        self._save_ai_agents()
        
        return {
            "id": agent_id,
            **agent
        }
    
    def delete_ai_agent(self, agent_id: str) -> bool:
        """Delete an AI agent"""
        if agent_id in self.ai_agents:
            del self.ai_agents[agent_id]
            self._save_ai_agents()
            return True
        return False
    
    def update_user_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences for AI content"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "interests": [],
                "preferred_agents": [],
                "content_types": [],
                "interaction_history": []
            }
        
        user_prefs = self.user_preferences[user_id]
        
        if "interests" in preferences:
            user_prefs["interests"] = preferences["interests"]
        if "preferred_agents" in preferences:
            user_prefs["preferred_agents"] = preferences["preferred_agents"]
        if "content_types" in preferences:
            user_prefs["content_types"] = preferences["content_types"]
        
        self._save_user_preferences()
        
        return self.user_preferences[user_id]
    
    def get_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Get user preferences for AI content"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "interests": [],
                "preferred_agents": [],
                "content_types": [],
                "interaction_history": []
            }
            self._save_user_preferences()
        
        return self.user_preferences[user_id]
    
    def record_user_interaction(self, user_id: str, content_id: str, agent_id: str, interaction_type: str) -> bool:
        """Record user interaction with AI-generated content"""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "interests": [],
                "preferred_agents": [],
                "content_types": [],
                "interaction_history": []
            }
        
        # Add interaction to history
        self.user_preferences[user_id]["interaction_history"].append({
            "content_id": content_id,
            "agent_id": agent_id,
            "interaction_type": interaction_type,
            "timestamp": datetime.now().isoformat()
        })
        
        # Limit history size
        if len(self.user_preferences[user_id]["interaction_history"]) > 100:
            self.user_preferences[user_id]["interaction_history"] = self.user_preferences[user_id]["interaction_history"][-100:]
        
        self._save_user_preferences()
        return True
    
    def analyze_user_preferences(self, user_id: str) -> Dict[str, Any]:
        """Analyze user preferences based on interaction history"""
        if user_id not in self.user_preferences:
            return {
                "interests": [],
                "preferred_agents": [],
                "content_types": []
            }
        
        user_prefs = self.user_preferences[user_id]
        history = user_prefs.get("interaction_history", [])
        
        # Count agent interactions
        agent_counts = {}
        for interaction in history:
            agent_id = interaction.get("agent_id")
            if agent_id:
                agent_counts[agent_id] = agent_counts.get(agent_id, 0) + 1
        
        # Get top agents
        preferred_agents = sorted(agent_counts.items(), key=lambda x: x[1], reverse=True)
        preferred_agent_ids = [agent_id for agent_id, _ in preferred_agents[:5]]
        
        # Extract interests from preferred agents
        interests = []
        for agent_id in preferred_agent_ids:
            if agent_id in self.ai_agents:
                interests.extend(self.ai_agents[agent_id].get("specialties", []))
        
        # Remove duplicates
        interests = list(set(interests))
        
        return {
            "interests": interests,
            "preferred_agents": preferred_agent_ids,
            "content_types": user_prefs.get("content_types", ["video"])
        }
    
    def generate_ai_content(self, user_id: Optional[str] = None, count: int = 5) -> List[ContentCreate]:
        """Generate AI content based on user preferences or randomly if no user_id is provided"""
        generated_content = []
        
        # If user_id is provided, use their preferences
        if user_id:
            preferences = self.analyze_user_preferences(user_id)
            preferred_agents = preferences.get("preferred_agents", [])
            interests = preferences.get("interests", [])
            
            # If user has preferences, use them
            if preferred_agents and interests:
                for _ in range(count):
                    # Select an agent from preferred agents
                    agent_id = random.choice(preferred_agents)
                    agent = self.ai_agents.get(agent_id)
                    
                    if agent:
                        # Generate content based on agent specialties and user interests
                        content = self._create_content_for_agent(agent, interests, user_id)
                        generated_content.append(content)
                
                return generated_content
        
        # If no user_id or no preferences, generate random content
        agent_ids = list(self.ai_agents.keys())
        for _ in range(count):
            agent_id = random.choice(agent_ids)
            agent = self.ai_agents.get(agent_id)
            
            if agent:
                content = self._create_content_for_agent(agent, agent.get("specialties", []), user_id)
                generated_content.append(content)
        
        return generated_content
    
    def _create_content_for_agent(self, agent: Dict[str, Any], interests: List[str], user_id: Optional[str] = None) -> ContentCreate:
        """Create content for a specific agent based on interests"""
        # Select a random interest or specialty
        topic = random.choice(interests) if interests else random.choice(agent.get("specialties", ["general"]))
        
        # Generate a title based on agent and topic
        titles = [
            f"{agent['name']} explores {topic}",
            f"Discover {topic} with {agent['name']}",
            f"The ultimate guide to {topic}",
            f"{topic.capitalize()} trends you need to know",
            f"How to master {topic} - by {agent['name']}"
        ]
        
        # Generate a description
        descriptions = [
            f"Learn all about {topic} in this AI-generated content by {agent['name']}.",
            f"Explore the world of {topic} with expert insights from {agent['name']}.",
            f"Dive deep into {topic} with this specially curated content.",
            f"Everything you need to know about {topic}, presented by {agent['name']}.",
            f"Discover the secrets of {topic} in this exclusive content."
        ]
        
        # Generate hashtags
        hashtags = [topic]
        if agent.get("specialties"):
            # Add 2-3 random specialties as hashtags
            specialties = agent.get("specialties", [])
            if specialties:
                hashtags.extend(random.sample(specialties, min(3, len(specialties))))
        
        # Add trending hashtags
        trending_hashtags = ["trending", "viral", "recommended", "aiContent"]
        hashtags.extend(random.sample(trending_hashtags, 2))
        
        # Create content
        return ContentCreate(
            title=random.choice(titles),
            description=random.choice(descriptions),
            user_id="ai_" + agent.get("name", "Agent").lower().replace(" ", "_"),
            content_type=random.choice(agent.get("content_types", ["video"])),
            hashtags=hashtags,
            is_ai_generated=True,
            ai_agent_id=agent.get("id"),
            target_user_id=user_id
        ) 