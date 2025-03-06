"""
Autonomous Agent Posting Script

This script makes AI agents post autonomously every two minutes.
It runs in the background and generates posts from AI agents using their specializations.
"""
import os
import time
import sys
import random
import logging
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import required services and models
from src.services.ai_agent_service import AIAgentService
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.content import ContentService
from src.models.content import ContentCreate
from src.models.ai_agent import AgentStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('autonomous_agent_posting.log')
    ]
)
logger = logging.getLogger('autonomous_agent_posting')

class AutonomousAgentPosting:
    """Class to manage autonomous posting by AI agents"""
    
    def __init__(self):
        """Initialize the autonomous agent posting service"""
        self.kg_service = KnowledgeGraphService()
        self.ai_agent_service = AIAgentService(self.kg_service)
        self.content_service = ContentService(self.kg_service)
        self.post_interval = 120  # 2 minutes in seconds
        self.running = False
        
        # Create directory for storing generated content if it doesn't exist
        self.content_dir = Path("src/frontend/static/images/generated")
        self.content_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("Autonomous Agent Posting service initialized")
    
    async def generate_and_post_content(self, agent_id):
        """Generate and post content for an AI agent"""
        try:
            # Generate post content
            logger.info(f"Generating post for agent {agent_id}")
            post_data = self.ai_agent_service.generate_agent_post(agent_id)
            
            # Create a ContentCreate object
            content_create = ContentCreate(
                title=post_data["title"],
                description=post_data["description"],
                user_id=agent_id,  # Using agent_id as user_id
                file_path=post_data["image_path"],
                hashtags=post_data["hashtags"],
                is_private=False,
                allow_comments=True,
                is_ai_generated=True
            )
            
            # Get the image data
            image_path = Path("src/frontend/static") / post_data["image_path"].lstrip('/')
            if not image_path.exists():
                logger.error(f"Image file not found: {image_path}")
                return
            
            with open(image_path, "rb") as f:
                file_data = f.read()
            
            # Create the content
            content = self.content_service.create_content(content_create, file_data)
            
            # Increment the agent's post count
            self.ai_agent_service.increment_post_count(agent_id)
            
            logger.info(f"Successfully posted content for agent {agent_id}: {content.id}")
            return content
            
        except Exception as e:
            logger.error(f"Error generating post for agent {agent_id}: {str(e)}")
            return None
    
    async def run_posting_cycle(self):
        """Run a single posting cycle for all online agents"""
        try:
            # Get all online agents
            online_agents = self.ai_agent_service.get_online_agents()
            
            if not online_agents:
                logger.warning("No online agents found")
                return
            
            logger.info(f"Found {len(online_agents)} online agents")
            
            # Randomly select an agent to post
            agent = random.choice(online_agents)
            
            # Generate and post content for the selected agent
            await self.generate_and_post_content(agent.id)
            
        except Exception as e:
            logger.error(f"Error in posting cycle: {str(e)}")
    
    async def start(self):
        """Start the autonomous posting service"""
        self.running = True
        logger.info("Starting autonomous agent posting service")
        
        try:
            while self.running:
                # Run a posting cycle
                await self.run_posting_cycle()
                
                # Wait for the next cycle
                logger.info(f"Waiting {self.post_interval} seconds until next post")
                await asyncio.sleep(self.post_interval)
                
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping service")
            self.running = False
        except Exception as e:
            logger.error(f"Error in autonomous posting service: {str(e)}")
            self.running = False
    
    def stop(self):
        """Stop the autonomous posting service"""
        self.running = False
        logger.info("Stopping autonomous agent posting service")

async def main():
    """Main function to run the autonomous agent posting service"""
    posting_service = AutonomousAgentPosting()
    await posting_service.start()

if __name__ == "__main__":
    # Run the main function
    asyncio.run(main()) 