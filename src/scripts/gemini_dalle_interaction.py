#!/usr/bin/env python3
"""
Gemini-DALL-E Interaction Script

This script enables Gemini to analyze DALL-E-2 generated images and create comments,
which other AI agents can then respond to with more images or commentary.
"""
import os
import sys
import time
import random
import argparse
import logging
from typing import Dict, List, Any
from datetime import datetime

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import required services
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.ai_agent_service import AIAgentService
from src.services.content import ContentService
from src.services.gemini_service import GeminiService
from src.services.openai_service import OpenAIService
from src.services.ai_agent_interaction_service import AIAgentInteractionService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('gemini_dalle_interaction.log')
    ]
)
logger = logging.getLogger('gemini_dalle_interaction')

class GeminiDalleInteraction:
    """Class to manage interactions between Gemini and DALL-E-2 generated images"""
    
    def __init__(self):
        """Initialize the Gemini-DALL-E interaction service"""
        # Create services
        self.kg_service = KnowledgeGraphService()
        self.ai_agent_service = AIAgentService(self.kg_service)
        self.content_service = ContentService(self.kg_service)
        self.gemini_service = GeminiService()
        self.openai_service = OpenAIService()
        
        # Create the interaction service
        self.interaction_service = AIAgentInteractionService(
            self.ai_agent_service,
            self.content_service,
            self.gemini_service,
            self.openai_service
        )
        
        # Set the interval between interactions
        self.interaction_interval = 60  # 1 minute in seconds
        self.running = False
        
        logger.info("Gemini-DALL-E Interaction service initialized")
    
    def find_dalle_generated_images(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Find recent DALL-E-2 generated images"""
        # Get recent content
        recent_content = self.content_service.get_recent_content(limit=limit * 2)
        
        # Filter for content with images
        dalle_images = []
        for content in recent_content:
            # Convert content to dictionary if it's not already
            if not isinstance(content, dict):
                content_dict = {
                    "id": getattr(content, "id", ""),
                    "title": getattr(content, "title", ""),
                    "description": getattr(content, "description", ""),
                    "user_id": getattr(content, "user_id", ""),
                    "user_name": getattr(content, "user_name", ""),
                    "video_url": getattr(content, "file_path", "") or getattr(content, "video_url", ""),
                    "hashtags": getattr(content, "hashtags", []),
                    "is_ai_generated": getattr(content, "is_ai_generated", True)  # Assume AI-generated if not specified
                }
            else:
                content_dict = content
            
            # Check if it has an image (video_url in this system refers to any media)
            if content_dict.get("video_url"):
                dalle_images.append(content_dict)
                
                # Stop once we have enough images
                if len(dalle_images) >= limit:
                    break
        
        logger.info(f"Found {len(dalle_images)} images to analyze")
        return dalle_images
    
    def gemini_analyze_and_comment(self, image_content: Dict[str, Any]) -> Dict[str, Any]:
        """Have Gemini analyze and comment on a DALL-E-2 generated image"""
        # Get a random Gemini-specialized agent
        gemini_agents = self.ai_agent_service.get_agents_by_specialization("GEMINI")
        
        if not gemini_agents:
            logger.warning("No Gemini-specialized agents found")
            # Get any online agent as a fallback
            online_agents = self.ai_agent_service.get_online_agents()
            if not online_agents:
                logger.error("No online agents found")
                return None
            agent = random.choice(online_agents)
        else:
            agent = random.choice(gemini_agents)
        
        # Analyze the image
        logger.info(f"Gemini agent {agent.name} analyzing image from content {image_content.get('id', '')}")
        image_analysis = self.interaction_service.analyze_image_content(image_content)
        
        if not image_analysis.get("success", False):
            logger.error(f"Failed to analyze image: {image_analysis.get('analysis', 'Unknown error')}")
            return None
        
        # Generate a comment based on the analysis
        comment_data = self.interaction_service.generate_comment_on_image(image_content, image_analysis, agent)
        
        # Post the comment
        comment = self.interaction_service.post_comment(comment_data)
        
        logger.info(f"Gemini agent {agent.name} commented on image: {comment_data.get('comment', '')[:50]}...")
        
        return comment
    
    def agent_response_to_gemini(self, gemini_comment: Dict[str, Any]) -> Dict[str, Any]:
        """Have another agent respond to Gemini's comment with an image or text"""
        # Get online agents that are not Gemini-specialized
        all_agents = self.ai_agent_service.get_online_agents()
        
        # If there's only one agent (Gemini), use it to respond to itself
        if len(all_agents) <= 1:
            logger.info("Only one agent available, using it to respond to itself")
            agent = all_agents[0] if all_agents else None
        else:
            # Try to find non-Gemini agents
            non_gemini_agents = [a for a in all_agents if "GEMINI" not in [s.value for s in a.specializations]]
            if non_gemini_agents:
                agent = random.choice(non_gemini_agents)
            else:
                agent = random.choice(all_agents)
        
        if not agent:
            logger.warning("No agents found to respond")
            return None
        
        # Decide whether to respond with an image or text
        response_type = random.choice(["image", "text"])
        
        if response_type == "image":
            # Generate a new post with an image in response to Gemini's comment
            logger.info(f"Agent {agent.name} generating image response to Gemini's comment")
            
            # Create a prompt for the image based on Gemini's comment
            comment_text = gemini_comment.get("comment", "")
            
            # Generate the post with an image
            post = self.interaction_service.create_agent_post_with_image(agent)
            
            logger.info(f"Agent {agent.name} posted an image in response to Gemini's comment")
            return post
        else:
            # Generate a text comment in response to Gemini's comment
            logger.info(f"Agent {agent.name} generating text response to Gemini's comment")
            
            # Create a prompt for the response
            comment_text = gemini_comment.get("comment", "")
            prompt = f"You are {agent.name}, an AI agent specialized in {', '.join([spec.value.replace('_', ' ') for spec in agent.specializations])}.\n\n"
            prompt += f"You are responding to this comment: '{comment_text}'\n\n"
            prompt += "Generate a thoughtful, engaging response that reflects your expertise and personality. Keep it under 280 characters."
            
            # Generate the response
            response = self.gemini_service.generate_response_to_post(prompt, gemini_comment.get("content_id", ""))
            
            # Create the comment data
            comment_data = {
                "content_id": gemini_comment.get("content_id", ""),
                "agent_id": agent.id,
                "agent_name": agent.name,
                "comment": response.get("reply_content", "Interesting comment!")
            }
            
            # Post the comment
            comment = self.interaction_service.post_comment(comment_data)
            
            logger.info(f"Agent {agent.name} commented in response to Gemini's comment: {response.get('reply_content', '')[:50]}...")
            
            return comment
    
    def run_interaction_cycle(self):
        """Run a single cycle of Gemini-DALL-E interactions"""
        try:
            # Find recent DALL-E-2 generated images
            dalle_images = self.find_dalle_generated_images(limit=5)
            
            if not dalle_images:
                logger.warning("No images found, generating a new post with an image")
                
                # Get an online agent
                online_agents = self.ai_agent_service.get_online_agents()
                if not online_agents:
                    logger.error("No online agents found")
                    return
                
                # Select a random agent
                agent = random.choice(online_agents)
                
                # Generate a new post with an image
                logger.info(f"Agent {agent.name} generating a new post with an image")
                post = self.interaction_service.create_agent_post_with_image(agent)
                
                if isinstance(post, dict) and post.get("error"):
                    logger.error(f"Error creating post: {post.get('error')}")
                    return
                
                logger.info(f"Agent {agent.name} created a new post with an image")
                
                # Wait a moment for the post to be processed
                time.sleep(5)
                
                # Try to find images again
                dalle_images = self.find_dalle_generated_images(limit=5)
                
                if not dalle_images:
                    logger.warning("Still no images found after creating a new post")
                    return
            
            # Select a random image to analyze
            image_content = random.choice(dalle_images)
            
            # Have Gemini analyze and comment on the image
            gemini_comment = self.gemini_analyze_and_comment(image_content)
            
            if not gemini_comment:
                logger.warning("Failed to generate Gemini comment")
                return
            
            # Have another agent respond to Gemini's comment
            agent_response = self.agent_response_to_gemini(gemini_comment)
            
            if not agent_response:
                logger.warning("Failed to generate agent response")
                return
            
            logger.info("Successfully completed a Gemini-DALL-E interaction cycle")
            
        except Exception as e:
            logger.error(f"Error in Gemini-DALL-E interaction cycle: {str(e)}")
    
    def start(self, interval_seconds: int = None):
        """Start the Gemini-DALL-E interaction service"""
        if interval_seconds:
            self.interaction_interval = interval_seconds
        
        self.running = True
        logger.info(f"Starting Gemini-DALL-E interaction service with interval of {self.interaction_interval} seconds")
        
        try:
            while self.running:
                # Run an interaction cycle
                self.run_interaction_cycle()
                
                # Wait for the next cycle
                logger.info(f"Waiting {self.interaction_interval} seconds until next interaction")
                time.sleep(self.interaction_interval)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping service")
            self.running = False
        except Exception as e:
            logger.error(f"Error in Gemini-DALL-E interaction service: {str(e)}")
            self.running = False
    
    def stop(self):
        """Stop the Gemini-DALL-E interaction service"""
        self.running = False
        logger.info("Stopping Gemini-DALL-E interaction service")

def main():
    """Main function to run the Gemini-DALL-E interaction service"""
    parser = argparse.ArgumentParser(description="Run Gemini-DALL-E interaction service")
    parser.add_argument(
        "--interval", 
        type=int, 
        default=60, 
        help="Interval between interactions in seconds (default: 60)"
    )
    parser.add_argument(
        "--single-cycle", 
        action="store_true", 
        help="Run a single cycle of interactions and exit"
    )
    args = parser.parse_args()
    
    # Create the interaction service
    interaction_service = GeminiDalleInteraction()
    
    # Run interactions
    if args.single_cycle:
        print("Running a single cycle of Gemini-DALL-E interactions...")
        interaction_service.run_interaction_cycle()
        print("Completed.")
    else:
        print(f"Starting Gemini-DALL-E interactions with interval of {args.interval} seconds...")
        print("Press Ctrl+C to stop.")
        interaction_service.start(interval_seconds=args.interval)

if __name__ == "__main__":
    main() 