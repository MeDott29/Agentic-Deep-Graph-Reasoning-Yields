#!/usr/bin/env python
"""
Image Generation Script for Knowledge Graph Social Network

This script scans the project for placeholder images and replaces them with
DALL-E-2 generated images. It also updates the AI agent avatars and generates
sample posts with images.
"""
import os
import sys
import json
import uuid
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
import argparse
import random

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from src.services.openai_service import OpenAIService
from src.services.ai_agent_service import AIAgentService
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.content import ContentService
from src.models.ai_agent import AgentSpecialization
from src.models.content import ContentCreate

# Constants
PLACEHOLDER_IMAGES = [
    "ai-avatar.png",
    "ai-avatar-2.png",
    "ai-avatar-3.png",
    "default-avatar.png",
    "placeholder.jpg"
]

TOPICS = [
    "Knowledge Graphs and Data Visualization",
    "Artificial Intelligence and Machine Learning",
    "Graph Databases and Data Modeling",
    "Neural Networks and Deep Learning",
    "Programming and Software Development",
    "Data Science and Analytics",
    "Natural Language Processing",
    "Computer Vision and Image Recognition",
    "Quantum Computing",
    "Blockchain and Distributed Systems",
    "Internet of Things (IoT)",
    "Cybersecurity and Privacy",
    "Cloud Computing and Serverless Architecture",
    "Augmented Reality and Virtual Reality",
    "Robotics and Automation"
]

class ImageGenerator:
    """Class for generating and replacing images in the project"""
    
    def __init__(self, dry_run: bool = False, force: bool = False):
        """Initialize the image generator"""
        self.dry_run = dry_run
        self.force = force
        self.openai_service = OpenAIService()
        self.kg_service = KnowledgeGraphService()
        self.ai_agent_service = AIAgentService(self.kg_service)
        self.content_service = ContentService(self.kg_service)
        
        # Paths
        self.project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        self.static_dir = self.project_root / "src" / "frontend" / "static"
        self.images_dir = self.static_dir / "images"
        self.generated_dir = self.images_dir / "generated"
        
        # Create generated directory if it doesn't exist
        if not self.dry_run:
            self.generated_dir.mkdir(parents=True, exist_ok=True)
        
        # Backup directory for original images
        self.backup_dir = self.project_root / "src" / "frontend" / "static" / "images" / "backup"
        if not self.dry_run:
            self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_image(self, image_path: Path) -> None:
        """Backup an image before replacing it"""
        if self.dry_run:
            print(f"[DRY RUN] Would backup {image_path} to {self.backup_dir / image_path.name}")
            return
        
        # Create backup if it doesn't exist
        backup_path = self.backup_dir / image_path.name
        if not backup_path.exists():
            shutil.copy2(image_path, backup_path)
            print(f"Backed up {image_path.name} to {backup_path}")
    
    def find_placeholder_images(self) -> List[Path]:
        """Find all placeholder images in the project"""
        placeholder_paths = []
        
        for placeholder in PLACEHOLDER_IMAGES:
            path = self.images_dir / placeholder
            if path.exists():
                placeholder_paths.append(path)
        
        return placeholder_paths
    
    def generate_replacement_image(self, placeholder_path: Path) -> str:
        """Generate a replacement image for a placeholder"""
        placeholder_name = placeholder_path.name
        
        # Generate different types of images based on the placeholder name
        if placeholder_name == "ai-avatar.png":
            prompt = "A professional profile picture for an AI assistant specialized in knowledge graphs. Minimalist, modern design with abstract elements representing artificial intelligence."
            image_type = "ai_avatar"
        elif placeholder_name == "ai-avatar-2.png":
            prompt = "A professional profile picture for an AI assistant specialized in graph databases. Minimalist, modern design with abstract elements representing data connections."
            image_type = "ai_avatar"
        elif placeholder_name == "ai-avatar-3.png":
            prompt = "A professional profile picture for an AI assistant specialized in machine learning. Minimalist, modern design with abstract elements representing neural networks."
            image_type = "ai_avatar"
        elif placeholder_name == "default-avatar.png":
            prompt = "A default user profile picture. Minimalist, modern design with a simple silhouette of a person."
            image_type = "user_avatar"
        elif placeholder_name == "placeholder.jpg":
            # Random topic for placeholder images
            topic = random.choice(TOPICS)
            prompt = f"An illustrative image for a social media post about {topic}. Modern, digital style, suitable for a knowledge graph social network."
            image_type = "post_image"
        else:
            # Generic prompt for unknown placeholders
            prompt = "A modern, abstract digital image suitable for a social media platform focused on knowledge graphs and AI."
            image_type = "generic"
        
        if self.dry_run:
            print(f"[DRY RUN] Would generate image with prompt: {prompt}")
            return f"/images/generated/{image_type}_{uuid.uuid4().hex[:8]}.png"
        
        try:
            # Generate the image
            response = self.openai_service.client.images.generate(
                model="dall-e-2",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            # Get the image URL
            image_url = response.data[0].url
            
            # Download the image
            import requests
            image_response = requests.get(image_url)
            if image_response.status_code != 200:
                raise Exception(f"Failed to download image: {image_response.status_code}")
            
            # Save the image
            filename = f"{image_type}_{uuid.uuid4().hex[:8]}.png"
            image_path = self.generated_dir / filename
            
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            print(f"Generated image: {image_path}")
            
            # Return the path relative to the static directory
            return f"/images/generated/{filename}"
        
        except Exception as e:
            print(f"Error generating image: {e}")
            
            # Try again with a simpler prompt
            try:
                print(f"Retrying with a simpler prompt...")
                simple_prompt = "A simple abstract digital art piece with vibrant colors"
                
                # Generate the image
                response = self.openai_service.client.images.generate(
                    model="dall-e-2",
                    prompt=simple_prompt,
                    size="1024x1024",
                    quality="standard",
                    n=1,
                )
                
                # Get the image URL
                image_url = response.data[0].url
                
                # Download the image
                image_response = requests.get(image_url)
                if image_response.status_code != 200:
                    raise Exception(f"Failed to download image: {image_response.status_code}")
                
                # Save the image
                filename = f"{image_type}_fallback_{uuid.uuid4().hex[:8]}.png"
                image_path = self.generated_dir / filename
                
                with open(image_path, "wb") as f:
                    f.write(image_response.content)
                
                print(f"Generated fallback image: {image_path}")
                
                # Return the path relative to the static directory
                return f"/images/generated/{filename}"
            except Exception as fallback_error:
                print(f"Error generating fallback image: {fallback_error}")
                # Generate a completely random image as a last resort
                try:
                    print(f"Generating a random abstract image as last resort...")
                    random_prompt = "Abstract digital art with random shapes and colors"
                    
                    # Generate the image
                    response = self.openai_service.client.images.generate(
                        model="dall-e-2",
                        prompt=random_prompt,
                        size="1024x1024",
                        quality="standard",
                        n=1,
                    )
                    
                    # Get the image URL
                    image_url = response.data[0].url
                    
                    # Download the image
                    image_response = requests.get(image_url)
                    if image_response.status_code != 200:
                        raise Exception(f"Failed to download image: {image_response.status_code}")
                    
                    # Save the image
                    filename = f"random_{uuid.uuid4().hex[:8]}.png"
                    image_path = self.generated_dir / filename
                    
                    with open(image_path, "wb") as f:
                        f.write(image_response.content)
                    
                    print(f"Generated random image: {image_path}")
                    
                    # Return the path relative to the static directory
                    return f"/images/generated/{filename}"
                except Exception as random_error:
                    print(f"Error generating random image: {random_error}")
                    # If all else fails, return None and let the caller handle it
                    return None
    
    def replace_image(self, placeholder_path: Path) -> str:
        """Replace a placeholder image with a generated one"""
        # Backup the original image
        self.backup_image(placeholder_path)
        
        # Generate a replacement image
        new_image_path = self.generate_replacement_image(placeholder_path)
        
        # Return the new image path
        return new_image_path
    
    def update_ai_agents(self) -> None:
        """Update AI agents with generated avatars"""
        print("\nUpdating AI agents with generated avatars...")
        
        # Get all agents
        agents = self.ai_agent_service.get_all_agents()
        
        for agent in agents:
            # Check if the agent has a placeholder avatar
            avatar = agent.avatar
            if avatar and any(placeholder in avatar for placeholder in PLACEHOLDER_IMAGES):
                print(f"Agent {agent.name} has a placeholder avatar: {avatar}")
                
                # Generate a new avatar
                specializations = [spec.value.replace('_', ' ') for spec in agent.specializations]
                specializations_text = ", ".join(specializations)
                
                if self.dry_run:
                    print(f"[DRY RUN] Would generate avatar for {agent.name} with specializations: {specializations_text}")
                    continue
                
                # Generate the avatar
                new_avatar = self.openai_service.generate_profile_image(
                    agent_name=agent.name,
                    agent_description=f"{agent.description or ''} Specialized in {specializations_text}."
                )
                
                # Update the agent
                self.ai_agent_service.update_agent(
                    agent_id=agent.id,
                    agent_update={
                        "avatar": new_avatar
                    }
                )
                
                print(f"Updated agent {agent.name} with new avatar: {new_avatar}")
    
    def generate_sample_posts(self, count: int = 5) -> None:
        """Generate sample posts from AI agents"""
        # Get all AI agents
        agents = self.ai_agent_service.get_agents()
        
        # Shuffle the agents to get random ones
        random.shuffle(agents)
        
        # Generate posts for the first 'count' agents
        for agent in agents[:count]:
            try:
                # Generate a post
                post_data = self.ai_agent_service.generate_agent_post(agent.id)
                
                # Check if the image path is None or a placeholder
                if not post_data.get("image_path"):
                    # Generate a new image
                    print(f"No valid image path for post by {agent.name}, generating a new image...")
                    
                    # Create a prompt based on the post content
                    prompt = f"An illustrative image for a social media post about: {post_data['description'][:200]}..."
                    
                    # Generate the image
                    new_image_path = self.openai_service.generate_post_image(
                        post_content=post_data["description"],
                        agent_specializations=[spec.value.replace('_', ' ') for spec in agent.specializations]
                    )
                    
                    if new_image_path:
                        post_data["image_path"] = new_image_path
                    else:
                        # Try with a simpler prompt as a last resort
                        print("Trying with a simpler prompt...")
                        simple_prompt = "A creative digital art piece with vibrant colors"
                        new_image_path = self.openai_service.generate_post_image(simple_prompt)
                        
                        if new_image_path:
                            post_data["image_path"] = new_image_path
                        else:
                            print(f"Failed to generate an image for post by {agent.name}, skipping...")
                            continue
                
                # Create a ContentCreate object
                content_create = ContentCreate(
                    title=post_data["title"],
                    description=post_data["description"],
                    user_id=agent.id,
                    file_path=post_data["image_path"],
                    hashtags=post_data["hashtags"],
                    is_private=False,
                    allow_comments=True,
                    is_ai_generated=True
                )
                
                # Create the post
                content = self.content_service.create_content(content_create)
                
                print(f"Created post for {agent.name}: {post_data['title']}")
            except Exception as e:
                print(f"Error generating post for {agent.name}: {e}")
    
    def update_html_templates(self, image_replacements: Dict[str, str]) -> None:
        """Update HTML templates with new image paths"""
        print("\nUpdating HTML templates...")
        
        templates_dir = self.project_root / "src" / "frontend" / "templates"
        
        for template_file in templates_dir.glob("*.html"):
            print(f"Processing template: {template_file.name}")
            
            # Read the template
            with open(template_file, "r") as f:
                content = f.read()
            
            # Replace image paths
            modified = False
            for old_path, new_path in image_replacements.items():
                old_path_rel = f"/static/images/{old_path}"
                new_path_rel = f"/static{new_path}"
                
                if old_path_rel in content:
                    if self.dry_run:
                        print(f"[DRY RUN] Would replace {old_path_rel} with {new_path_rel} in {template_file.name}")
                    else:
                        content = content.replace(old_path_rel, new_path_rel)
                        modified = True
            
            # Write the updated template
            if modified and not self.dry_run:
                with open(template_file, "w") as f:
                    f.write(content)
                print(f"Updated template: {template_file.name}")
    
    def run(self) -> None:
        """Run the image generation and replacement process"""
        print("Starting image generation and replacement process...")
        print(f"Dry run: {self.dry_run}")
        print(f"Force: {self.force}")
        
        # Find placeholder images
        placeholder_images = self.find_placeholder_images()
        print(f"Found {len(placeholder_images)} placeholder images:")
        for img in placeholder_images:
            print(f"  - {img.name}")
        
        # Replace placeholder images
        image_replacements = {}
        for img in placeholder_images:
            print(f"\nProcessing {img.name}...")
            new_path = self.replace_image(img)
            
            # Handle the case where image generation failed
            if new_path is None:
                print(f"Failed to generate a replacement for {img.name}, skipping...")
                continue
                
            image_replacements[img.name] = new_path
            print(f"Replaced {img.name} with {new_path}")
        
        # Update AI agents
        self.update_ai_agents()
        
        # Update HTML templates
        self.update_html_templates(image_replacements)
        
        # Generate sample posts
        self.generate_sample_posts(count=5)
        
        print("\nImage generation and replacement process completed!")

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Generate and replace placeholder images with DALL-E-2 generated images")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making any changes")
    parser.add_argument("--force", action="store_true", help="Force replacement of images even if they already exist")
    args = parser.parse_args()
    
    generator = ImageGenerator(dry_run=args.dry_run, force=args.force)
    generator.run()

if __name__ == "__main__":
    main() 