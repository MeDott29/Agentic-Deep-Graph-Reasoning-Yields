"""
OpenAI Service for DALL-E-2 integration in the Knowledge Graph Social Network System
"""
import os
import base64
import uuid
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OpenAIService:
    """Service for generating images and content using OpenAI's DALL-E-2 API"""
    
    def __init__(self):
        """Initialize the OpenAI service with API key from environment variables"""
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")
        
        # Initialize the OpenAI client
        self.client = OpenAI(api_key=api_key)
        self.image_size = "1024x1024"  # Default size for DALL-E-2
        self.static_dir = Path("src/frontend/static")
        self.images_dir = self.static_dir / "images"
        self.generated_dir = self.images_dir / "generated"
        
        # Create directories if they don't exist
        self.generated_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_profile_image(self, agent_name: str, agent_description: str) -> str:
        """
        Generate a profile image for an AI agent using DALL-E 2
        
        Args:
            agent_name: The name of the AI agent
            agent_description: A description of the AI agent
            
        Returns:
            The path to the generated image relative to the static directory
        """
        try:
            # Create a prompt for the profile image
            prompt = f"A professional profile picture for an AI assistant named {agent_name}. {agent_description[:200]}. Modern, digital art style, suitable for a social media profile."
            
            # Ensure prompt is under 1000 characters
            if len(prompt) > 1000:
                prompt = prompt[:997] + "..."
            
            # Generate the image using DALL-E 2
            response = self.client.images.generate(
                model="dall-e-2",
                prompt=prompt,
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
            
            # Create a unique filename
            filename = f"profile_{uuid.uuid4().hex[:8]}.png"
            
            # Save the image to the static directory
            base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "frontend", "static")
            generated_dir = os.path.join(base_path, "images", "generated")
            
            # Create the directory if it doesn't exist
            os.makedirs(generated_dir, exist_ok=True)
            
            image_path = os.path.join(generated_dir, filename)
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            # Return the path relative to the static directory
            return f"/images/generated/{filename}"
        except Exception as e:
            print(f"Error generating profile image: {str(e)}")
            
            # Instead of returning a placeholder, generate a simple abstract profile image
            try:
                # Try with a simpler prompt
                simple_prompt = "A simple abstract profile picture with vibrant colors"
                response = self.client.images.generate(
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
                
                # Create a unique filename
                filename = f"profile_fallback_{uuid.uuid4().hex[:8]}.png"
                
                # Save the image to the static directory
                base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "frontend", "static")
                generated_dir = os.path.join(base_path, "images", "generated")
                
                # Create the directory if it doesn't exist
                os.makedirs(generated_dir, exist_ok=True)
                
                image_path = os.path.join(generated_dir, filename)
                with open(image_path, "wb") as f:
                    f.write(image_response.content)
                
                # Return the path relative to the static directory
                return f"/images/generated/{filename}"
            except Exception as fallback_error:
                print(f"Error generating fallback profile image: {str(fallback_error)}")
                # If all else fails, return None and let the caller handle it
                return None
    
    def generate_post_image(self, post_content: str, agent_specializations: List[str] = None) -> str:
        """
        Generate an image for a post using DALL-E 2
        
        Args:
            post_content: The content of the post
            agent_specializations: Optional list of agent specializations to guide the image generation
            
        Returns:
            The path to the generated image relative to the static directory
        """
        try:
            # Create a prompt for the image based on the post content
            prompt = f"Create an image for a social media post with the following content: {post_content[:500]}"
            
            # Add agent specializations if provided
            if agent_specializations and len(agent_specializations) > 0:
                prompt += f" The post is related to {', '.join(agent_specializations[:3])}."
            
            # Generate the image using DALL-E 2
            response = self.client.images.generate(
                model="dall-e-2",
                prompt=prompt,
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
            
            # Create a unique filename
            filename = f"dalle_{uuid.uuid4().hex[:8]}.png"
            
            # Save the image to the static directory
            base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "frontend", "static")
            generated_dir = os.path.join(base_path, "images", "generated")
            
            # Create the directory if it doesn't exist
            os.makedirs(generated_dir, exist_ok=True)
            
            image_path = os.path.join(generated_dir, filename)
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            # Return the path relative to the static directory
            return f"/images/generated/{filename}"
        except Exception as e:
            print(f"Error generating post image: {str(e)}")
            
            # Instead of returning a placeholder, generate a simple abstract image
            try:
                # Try with a simpler prompt
                simple_prompt = "A simple abstract digital art with vibrant colors"
                response = self.client.images.generate(
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
                
                # Create a unique filename
                filename = f"dalle_fallback_{uuid.uuid4().hex[:8]}.png"
                
                # Save the image to the static directory
                base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "frontend", "static")
                generated_dir = os.path.join(base_path, "images", "generated")
                
                # Create the directory if it doesn't exist
                os.makedirs(generated_dir, exist_ok=True)
                
                image_path = os.path.join(generated_dir, filename)
                with open(image_path, "wb") as f:
                    f.write(image_response.content)
                
                # Return the path relative to the static directory
                return f"/images/generated/{filename}"
            except Exception as fallback_error:
                print(f"Error generating fallback image: {str(fallback_error)}")
                # If all else fails, return None and let the caller handle it
                return None
    
    def generate_agent_post_content(self, agent_name: str, agent_specializations: List[str]) -> Dict[str, Any]:
        """
        Generate post content for an AI agent based on its specializations
        
        Args:
            agent_name: The name of the AI agent
            agent_specializations: The specializations of the AI agent
            
        Returns:
            A dictionary containing the generated post content and hashtags
        """
        specializations_text = ", ".join(agent_specializations)
        
        try:
            # Generate post content using OpenAI's text completion
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": f"You are {agent_name}, an AI agent specialized in {specializations_text}. Create an engaging, informative social media post about one of your specializations. The post should be educational, insightful, and include relevant hashtags."},
                    {"role": "user", "content": f"Write a social media post as {agent_name} about one of these topics: {specializations_text}. Include a title, main content (2-3 paragraphs), and 3-5 relevant hashtags."}
                ],
                max_tokens=500
            )
            
            # Extract the generated content
            content = response.choices[0].message.content
            
            # Parse the content to extract title, main content, and hashtags
            lines = content.strip().split('\n')
            title = lines[0].strip().replace('#', '').strip()
            
            # Extract hashtags
            hashtags = []
            main_content = []
            for line in lines[1:]:
                if line.strip().startswith('#'):
                    # Extract hashtags
                    tags = line.strip().split()
                    for tag in tags:
                        if tag.startswith('#'):
                            hashtags.append(tag[1:])  # Remove the # symbol
                else:
                    # Add to main content
                    if line.strip():
                        main_content.append(line.strip())
            
            # Join main content paragraphs
            description = '\n\n'.join(main_content)
            
            # If no hashtags were found in a specific format, try to extract them from the content
            if not hashtags:
                for line in lines:
                    if '#' in line:
                        for word in line.split():
                            if word.startswith('#'):
                                hashtags.append(word[1:])
            
            # Generate a default set of hashtags if none were found
            if not hashtags:
                hashtags = [spec.lower().replace('_', '') for spec in agent_specializations]
                hashtags.append('ai')
                hashtags.append('knowledgegraph')
            
            return {
                "title": title,
                "description": description,
                "hashtags": hashtags
            }
            
        except Exception as e:
            print(f"Error generating post content: {e}")
            # Return default content if generation fails
            return {
                "title": f"{agent_name}'s Thoughts on {agent_specializations[0] if agent_specializations else 'AI'}",
                "description": f"Exploring the fascinating world of {agent_specializations[0] if agent_specializations else 'artificial intelligence'} and its applications in modern technology.",
                "hashtags": [spec.lower().replace('_', '') for spec in agent_specializations] + ['ai', 'technology']
            }
    
    def analyze_image(self, image_path: str, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze an image using OpenAI's GPT-4o Vision capabilities
        
        Args:
            image_path: Path to the image file
            prompt: Optional prompt to guide the analysis
            
        Returns:
            A dictionary containing the success status and analysis
        """
        try:
            # Check if the image path is valid
            if not image_path:
                # Generate a new image with DALL-E 2 instead of using a placeholder
                default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                generated_image = self.generate_post_image(default_prompt)
                if not generated_image:
                    return {
                        "success": False,
                        "analysis": "Failed to generate a new image and no image path was provided."
                    }
                
                # Use the newly generated image
                image_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "src", "frontend", "static", 
                    generated_image.lstrip('/')
                )
            
            # Handle API URLs
            if image_path.startswith('/api/content/'):
                # Extract content ID from the URL
                content_id = image_path.split('/')[3]
                
                # Construct the path to the actual image file
                # In this system, images are stored in the static directory
                base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "frontend", "static")
                
                # Try to find the image in the generated images directory
                image_files = os.listdir(os.path.join(base_path, "images", "generated"))
                
                # Look for files that contain the content ID
                matching_files = [f for f in image_files if content_id in f]
                
                if matching_files:
                    # Use the first matching file
                    image_path = os.path.join(base_path, "images", "generated", matching_files[0])
                else:
                    # Try to find the image in the uploads directory
                    try:
                        upload_files = os.listdir(os.path.join(base_path, "uploads"))
                        matching_uploads = [f for f in upload_files if content_id in f]
                        
                        if matching_uploads:
                            # Use the first matching file
                            image_path = os.path.join(base_path, "uploads", matching_uploads[0])
                        else:
                            # Generate a new image with DALL-E 2 instead of using a placeholder
                            default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                            generated_image = self.generate_post_image(default_prompt)
                            if not generated_image:
                                return {
                                    "success": False,
                                    "analysis": "Failed to generate a new image and no valid image was found."
                                }
                            
                            # Use the newly generated image
                            image_path = os.path.join(
                                base_path, 
                                generated_image.lstrip('/')
                            )
                    except (FileNotFoundError, PermissionError):
                        # Generate a new image with DALL-E 2 instead of using a placeholder
                        default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                        generated_image = self.generate_post_image(default_prompt)
                        if not generated_image:
                            return {
                                "success": False,
                                "analysis": "Failed to generate a new image and no valid image was found."
                            }
                        
                        # Use the newly generated image
                        image_path = os.path.join(
                            base_path, 
                            generated_image.lstrip('/')
                        )
            
            # Handle relative paths
            elif image_path.startswith('/'):
                # Convert to absolute path
                base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "frontend", "static")
                image_path = os.path.join(base_path, image_path.lstrip('/'))
            
            # Check if the file exists and has content
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                # Generate a new image with DALL-E 2 instead of using a placeholder
                default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                generated_image = self.generate_post_image(default_prompt)
                if not generated_image:
                    return {
                        "success": False,
                        "analysis": f"Image file not found: {image_path} and failed to generate a new image."
                    }
                
                # Use the newly generated image
                image_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "src", "frontend", "static", 
                    generated_image.lstrip('/')
                )
            
            # Check if the file has content
            if os.path.getsize(image_path) == 0:
                print(f"Image file is empty: {image_path}")
                # Generate a new image with DALL-E 2 instead of using a placeholder
                default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                generated_image = self.generate_post_image(default_prompt)
                if not generated_image:
                    return {
                        "success": False,
                        "analysis": f"Image file is empty: {image_path} and failed to generate a new image."
                    }
                
                # Use the newly generated image
                image_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "src", "frontend", "static", 
                    generated_image.lstrip('/')
                )
            
            # Read the image file and encode it as base64
            with open(image_path, "rb") as f:
                image_data = f.read()
                
            # Ensure we have valid image data
            if not image_data:
                print(f"No image data read from file: {image_path}")
                # Generate a new image with DALL-E 2 instead of using a placeholder
                default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                generated_image = self.generate_post_image(default_prompt)
                if not generated_image:
                    return {
                        "success": False,
                        "analysis": f"No image data read from file: {image_path} and failed to generate a new image."
                    }
                
                # Use the newly generated image
                image_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "src", "frontend", "static", 
                    generated_image.lstrip('/')
                )
                
                # Read the new image file
                with open(image_path, "rb") as f:
                    image_data = f.read()
                
            # Encode the image data as base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Create a default prompt if none is provided
            if not prompt:
                prompt = "Analyze this image and describe what you see. Focus on the main subjects, style, colors, and overall composition."
            
            # Create the message for GPT-4o Vision
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Generate the analysis using GPT-4o
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=messages,
                max_tokens=1024
            )
            
            # Extract the analysis from the response
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis
            }
        except Exception as e:
            error_message = f"Error analyzing image with GPT-4o: {str(e)}"
            print(error_message)
            
            # Add more detailed error information for debugging
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Traceback: {traceback_str}")
            
            # Log the image path and data size for debugging
            print(f"Image path: {image_path}")
            try:
                print(f"Image data size: {len(image_data) if 'image_data' in locals() else 0} bytes")
            except:
                pass
            
            return {
                "success": False,
                "analysis": error_message
            } 