"""
AI Agent Interaction Service for autonomous agent interactions in the Knowledge Graph Social Network System
"""
import os
import random
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from src.services.ai_agent_service import AIAgentService
from src.services.content import ContentService, ContentCreate
from src.services.gemini_service import GeminiService
from src.services.openai_service import OpenAIService
from src.models.ai_agent import AIAgent, AgentStatus

class AIAgentInteractionService:
    """Service for managing autonomous interactions between AI agents"""
    
    def __init__(
        self,
        ai_agent_service: AIAgentService,
        content_service: ContentService,
        gemini_service: GeminiService,
        openai_service: OpenAIService
    ):
        """Initialize the AI agent interaction service"""
        self.ai_agent_service = ai_agent_service
        self.content_service = content_service
        self.gemini_service = gemini_service
        self.openai_service = openai_service
        self.interaction_interval = 120  # 2 minutes between interactions
        self.last_interaction_time: Dict[str, datetime] = {}
    
    def get_agents_ready_for_interaction(self) -> List[AIAgent]:
        """Get a list of agents that are ready to interact"""
        online_agents = self.ai_agent_service.get_online_agents()
        ready_agents = []
        
        current_time = datetime.now()
        
        for agent in online_agents:
            last_time = self.last_interaction_time.get(agent.id)
            
            # If the agent has never interacted or it's been more than the interval
            if not last_time or (current_time - last_time).total_seconds() >= self.interaction_interval:
                ready_agents.append(agent)
        
        return ready_agents
    
    def get_recent_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent content from the platform"""
        return self.content_service.get_recent_content(limit=limit)
    
    def get_content_by_agent(self, agent_id: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Get recent content from a specific agent"""
        return self.content_service.get_user_content(user_id=agent_id, limit=limit)
    
    def analyze_image_content(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image content using OpenAI's GPT-4o Vision"""
        # Check if content has video_url (which is used for all media)
        if not content.get("video_url"):
            # Try file_path as a fallback
            if hasattr(content, "file_path") and content.file_path:
                image_path = content.file_path
            else:
                return {
                    "success": False,
                    "analysis": "No image found in the content."
                }
        else:
            image_path = content["video_url"]
        
        # Create a prompt based on the content
        prompt = "Please analyze this image and describe what you see."
        
        # Add title if available
        if content.get("title"):
            prompt += f" The post title is: '{content['title']}'."
        elif hasattr(content, "title") and content.title:
            prompt += f" The post title is: '{content.title}'."
        
        # Add description if available
        if content.get("description"):
            prompt += f" The post description is: '{content['description']}'."
        elif hasattr(content, "description") and content.description:
            prompt += f" The post description is: '{content.description}'."
        
        # Add hashtags if available
        hashtags = []
        if content.get("hashtags") and len(content["hashtags"]) > 0:
            hashtags = content["hashtags"]
        elif hasattr(content, "hashtags") and content.hashtags:
            hashtags = content.hashtags
        
        if hashtags:
            prompt += f" Hashtags: {', '.join(['#' + tag for tag in hashtags])}."
        
        # Add user info if available
        user_name = ""
        if content.get("user_name"):
            user_name = content["user_name"]
        elif hasattr(content, "user_name") and content.user_name:
            user_name = content.user_name
        
        if user_name:
            prompt += f" This image was posted by {user_name}."
        
        prompt += " Focus on the main subjects, style, colors, and overall composition."
        
        # Analyze the image using OpenAI's GPT-4o instead of Gemini
        return self.openai_service.analyze_image(image_path=image_path, prompt=prompt)
    
    def generate_comment_on_image(self, content: Dict[str, Any], image_analysis: Dict[str, Any], agent: AIAgent) -> Dict[str, Any]:
        """Generate a comment on an image based on the analysis"""
        # Create a prompt for the comment
        prompt = f"You are {agent.name}, an AI agent specialized in {', '.join([spec.value.replace('_', ' ') for spec in agent.specializations])}."
        prompt += f"\n\nYou are looking at a post"
        
        # Add user info if available
        user_name = ""
        if content.get("user_name"):
            user_name = content["user_name"]
        elif hasattr(content, "user_name") and content.user_name:
            user_name = content.user_name
        
        if user_name:
            prompt += f" by {user_name}."
        else:
            prompt += " by another AI agent."
        
        # Add title if available
        if content.get("title"):
            prompt += f"\nPost title: '{content['title']}'."
        elif hasattr(content, "title") and content.title:
            prompt += f"\nPost title: '{content.title}'."
        
        # Add description if available
        if content.get("description"):
            prompt += f"\nPost description: '{content['description']}'."
        elif hasattr(content, "description") and content.description:
            prompt += f"\nPost description: '{content.description}'."
        
        # Add hashtags if available
        hashtags = []
        if content.get("hashtags") and len(content["hashtags"]) > 0:
            hashtags = content["hashtags"]
        elif hasattr(content, "hashtags") and content.hashtags:
            hashtags = content.hashtags
        
        if hashtags:
            prompt += f"\nHashtags: {', '.join(['#' + tag for tag in hashtags])}."
        
        # Add image analysis
        prompt += f"\n\nAnalysis of the image: {image_analysis.get('analysis', 'No analysis available.')}"
        
        prompt += "\n\nGenerate a thoughtful, engaging comment on this post that reflects your expertise and personality. Keep it under 280 characters."
        
        # Get content ID
        content_id = ""
        if content.get("id"):
            content_id = content["id"]
        elif hasattr(content, "id") and content.id:
            content_id = content.id
        
        # Generate the comment using Gemini
        response = self.gemini_service.generate_response_to_post(prompt, content_id)
        
        return {
            "content_id": content_id,
            "agent_id": agent.id,
            "agent_name": agent.name,
            "comment": response.get("reply_content", "Interesting post!")
        }
    
    def post_comment(self, comment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post a comment on content"""
        # Create the comment
        comment = self.content_service.create_comment(
            user_id=comment_data["agent_id"],
            content_id=comment_data["content_id"],
            comment=comment_data["comment"]
        )
        
        # Update the last interaction time for this agent
        self.last_interaction_time[comment_data["agent_id"]] = datetime.now()
        
        # Increment the agent's comment count
        self.ai_agent_service.increment_comment_count(comment_data["agent_id"])
        
        return comment
    
    def create_agent_post_with_image(self, agent: AIAgent) -> Dict[str, Any]:
        """Create a post with an image for an AI agent"""
        # Generate post content
        post_data = self.ai_agent_service.generate_agent_post(agent.id)
        
        # Check if the image generation failed or returned None
        if not post_data.get("image_path"):
            # Try using Gemini as a fallback for image generation
            print(f"DALL-E image generation failed, trying Gemini as fallback...")
            
            # Create a prompt for Gemini
            prompt = f"Generate an image for a post about: {post_data['description'][:200]}..."
            
            # Generate the image using Gemini
            static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "static")
            generated_dir = os.path.join(static_dir, "images", "generated")
            os.makedirs(generated_dir, exist_ok=True)
            
            # Generate the image
            gemini_image_result = self.gemini_service.generate_image(prompt)
            
            if gemini_image_result.get("success"):
                # Update the image path
                post_data["image_path"] = gemini_image_result.get("image_path")
            else:
                # If Gemini also fails, try one more time with a simpler prompt
                simple_prompt = "A creative digital art piece with vibrant colors"
                final_attempt = self.openai_service.generate_post_image(simple_prompt)
                
                if final_attempt:
                    post_data["image_path"] = final_attempt
        
        # Create the post in the database
        post_id = self.content_service.create_content({
            "user_id": agent.id,
            "user_name": agent.name,
            "title": post_data.get("title", ""),
            "description": post_data.get("description", ""),
            "hashtags": post_data.get("hashtags", []),
            "video_url": post_data.get("image_path"),  # In this system, video_url is used for all media
            "created_at": datetime.now().isoformat(),
            "likes": 0,
            "comments": []
        })
        
        return {
            "post_id": post_id,
            "post_data": post_data
        }
    
    def run_autonomous_interaction_cycle(self):
        """Run a cycle of autonomous interactions between agents"""
        try:
            # Get agents ready for interaction
            ready_agents = self.get_agents_ready_for_interaction()
            
            if not ready_agents:
                print("No agents ready for interaction at this time.")
                return
            
            # For each ready agent, decide on an action
            for agent in ready_agents:
                # Randomly decide what action to take
                action = random.choice(["post", "comment", "analyze"])
                
                if action == "post":
                    # Create a new post with a DALL-E-2 generated image
                    post = self.create_agent_post_with_image(agent)
                    if isinstance(post, dict) and post.get("error"):
                        print(f"Error creating post for agent {agent.name}: {post.get('error')}")
                    else:
                        print(f"Agent {agent.name} created a new post: {getattr(post, 'title', 'Untitled')}")
                    
                elif action == "comment":
                    # Get recent content to comment on
                    recent_content = self.get_recent_content(limit=10)
                    
                    if recent_content:
                        # Select a random content to comment on
                        content = random.choice(recent_content)
                        
                        # Convert content to dictionary if it's not already
                        if not isinstance(content, dict):
                            content_dict = {
                                "id": getattr(content, "id", ""),
                                "title": getattr(content, "title", ""),
                                "description": getattr(content, "description", ""),
                                "user_id": getattr(content, "user_id", ""),
                                "user_name": getattr(content, "user_name", ""),
                                "video_url": getattr(content, "file_path", ""),
                                "hashtags": getattr(content, "hashtags", [])
                            }
                        else:
                            content_dict = content
                        
                        # Analyze the image if present
                        if content_dict.get("video_url"):
                            image_analysis = self.analyze_image_content(content_dict)
                            
                            # Generate and post a comment based on the analysis
                            comment_data = self.generate_comment_on_image(content_dict, image_analysis, agent)
                            comment = self.post_comment(comment_data)
                            
                            print(f"Agent {agent.name} commented on a post by {content_dict.get('user_name', 'another agent')}")
                    
                elif action == "analyze":
                    # Get recent content with images to analyze
                    recent_content = self.get_recent_content(limit=20)
                    
                    # Convert content objects to dictionaries if needed
                    content_list = []
                    for content in recent_content:
                        if not isinstance(content, dict):
                            content_dict = {
                                "id": getattr(content, "id", ""),
                                "title": getattr(content, "title", ""),
                                "description": getattr(content, "description", ""),
                                "user_id": getattr(content, "user_id", ""),
                                "user_name": getattr(content, "user_name", ""),
                                "video_url": getattr(content, "file_path", ""),
                                "hashtags": getattr(content, "hashtags", [])
                            }
                            content_list.append(content_dict)
                        else:
                            content_list.append(content)
                    
                    # Filter for content with images
                    image_content = [c for c in content_list if c.get("video_url")]
                    
                    if image_content:
                        # Select a random content to analyze
                        content = random.choice(image_content)
                        
                        # Analyze the image
                        image_analysis = self.analyze_image_content(content)
                        
                        # Generate and post a comment based on the analysis
                        comment_data = self.generate_comment_on_image(content, image_analysis, agent)
                        comment = self.post_comment(comment_data)
                        
                        print(f"Agent {agent.name} analyzed and commented on an image by {content.get('user_name', 'another agent')}")
        except Exception as e:
            print(f"Error in autonomous agent interactions: {str(e)}")
    
    def start_autonomous_interactions(self, interval_seconds: int = 30):
        """Start autonomous interactions between agents at regular intervals"""
        print(f"Starting autonomous agent interactions every {interval_seconds} seconds")
        
        try:
            while True:
                self.run_autonomous_interaction_cycle()
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("Autonomous agent interactions stopped by user")
        except Exception as e:
            print(f"Error in autonomous agent interactions: {str(e)}")

    def generate_post_for_agent(self, agent: AIAgent) -> Dict[str, Any]:
        """Generate a post for an AI agent"""
        # Get the agent's specializations
        specializations = [spec.value.replace('_', ' ') for spec in agent.specializations]
        
        # Get recent posts by this agent to avoid repetition
        recent_posts = self.get_content_by_agent(agent.id)
        recent_post_texts = [post.get("description", "") for post in recent_posts]
        
        # Get trending topics
        trending_topics = self.get_trending_topics()
        
        # Create context for the post generation
        context = {
            "agent_name": agent.name,
            "specializations": specializations,
            "recent_posts": recent_post_texts,
            "trending_topics": trending_topics
        }
        
        # Generate the post content
        post_data = self.openai_service.generate_agent_post_content(agent.name, specializations)
        
        if not post_data.get("success", False):
            # Try with Gemini as a fallback
            post_data = self.gemini_service.generate_new_post(context)
        
        # Generate an image for the post if needed
        image_path = None
        if post_data.get("image_prompt"):
            image_path = self.openai_service.generate_post_image(
                post_data.get("image_prompt"),
                specializations
            )
        
        # If no image was generated or the generation failed, try again with the post content
        if not image_path:
            image_path = self.openai_service.generate_post_image(
                post_data.get("post_content", "An interesting social media post"),
                specializations
            )
            
        # If image generation still failed, generate a generic image
        if not image_path:
            # Try one more time with a simple prompt
            image_path = self.openai_service.generate_post_image(
                "A creative digital art piece",
                []
            )
        
        # Create the post
        post = {
            "user_id": agent.id,
            "user_name": agent.name,
            "title": post_data.get("title", ""),
            "description": post_data.get("post_content", ""),
            "hashtags": post_data.get("hashtags", []),
            "video_url": image_path,  # In this system, video_url is used for all media
            "created_at": datetime.now().isoformat(),
            "likes": 0,
            "comments": []
        }
        
        # Save the post to the database
        post_id = self.content_service.create_content(post)
        
        # Return the post data
        return {
            "post_id": post_id,
            "post_data": post
        } 