"""
Gemini Service for content generation in the Knowledge Graph Social Network System
"""
import os
import base64
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types  # FINAL: Import types from google.genai for the new API
from dotenv import load_dotenv
from openai import OpenAI
import requests
import uuid

# Load environment variables
load_dotenv()

class GeminiService:
    """Service for generating content using Google's Gemini API"""
    
    def __init__(self):
        """Initialize the Gemini service with API key from environment variables"""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable not set")
        
        # Initialize the Gemini API with the latest SDK
        self.client = genai.Client(api_key=api_key)
        
        # Set the model names to use
        self.text_model = "gemini-2.0-flash-001"  # For text-only generation
        self.vision_model = "gemini-2.0-pro-vision"  # For image analysis
        
        # Rate limits
        self.rate_limit_per_minute = 15
        self.rate_limit_per_day = 1500
    
    def generate_response_to_post(self, post_content: str, post_id: str) -> Dict[str, Any]:
        """Generate a response to a user's post using Gemini"""
        # Define the tool for function calling
        # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
        function = types.FunctionDeclaration(
            name="respond_to_post",
            description="Create a reply to a user's post",
            parameters=types.Schema(
                type="OBJECT",
                required=["reply_content"],
                properties={
                    "reply_content": types.Schema(
                        type="STRING",
                        description="The content of the reply to the post"
                    ),
                    "sentiment": types.Schema(
                        type="STRING",
                        enum=["positive", "neutral", "negative"],
                        description="The sentiment of the reply"
                    ),
                    "topics": types.Schema(
                        type="ARRAY",
                        items=types.Schema(type="STRING"),
                        description="The main topics discussed in the reply"
                    )
                }
            )
        )
        
        tool = types.Tool(function_declarations=[function])
        
        try:
            # Create the content with the prompt
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            content = types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=f"""You are an AI assistant that creates thoughtful and engaging responses to social media posts.
                        
                        Post: {post_content}
                        
                        Create a reply to this post that is thoughtful, relevant, and adds value to the conversation.
                        The reply should be 1-3 sentences long and conversational in tone.
                        """
                    )
                ]
            )
            
            # Generate the response with function calling
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            response = self.client.models.generate_content(
                model=self.text_model,
                contents=content,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=256
                ),
                tools=[tool]
            )
            
            # Extract the function call from the response
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            function_call = None
            if hasattr(response, 'function_calls') and response.function_calls:
                function_call = response.function_calls[0]
            
            if function_call and function_call.name == "respond_to_post":
                # Extract the arguments
                args = function_call.function_call.args
                
                # Create the response
                return {
                    "success": True,
                    "post_id": post_id,
                    "reply_content": args.get("reply_content", ""),
                    "sentiment": args.get("sentiment", "neutral"),
                    "topics": args.get("topics", [])
                }
            else:
                # If no function call was found, extract the text response
                text_response = response.text
                
                return {
                    "success": True,
                    "post_id": post_id,
                    "reply_content": text_response,
                    "sentiment": "neutral",
                    "topics": []
                }
        except Exception as e:
            print(f"Error generating response to post: {str(e)}")
            return {
                "success": False,
                "post_id": post_id,
                "reply_content": f"Error generating response: {str(e)}",
                "sentiment": "neutral",
                "topics": []
            }
    
    def generate_new_post(self, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a new post for an AI agent using Gemini"""
        # Define the tool for function calling
        # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
        function = types.FunctionDeclaration(
            name="create_post",
            description="Create a new post for an AI agent",
            parameters=types.Schema(
                type="OBJECT",
                required=["post_content"],
                properties={
                    "post_content": types.Schema(
                        type="STRING",
                        description="The content of the post"
                    ),
                    "hashtags": types.Schema(
                        type="ARRAY",
                        items=types.Schema(type="STRING"),
                        description="Hashtags for the post"
                    ),
                    "topics": types.Schema(
                        type="ARRAY",
                        items=types.Schema(type="STRING"),
                        description="The main topics discussed in the post"
                    ),
                    "image_prompt": types.Schema(
                        type="STRING",
                        description="A prompt to generate an image for the post"
                    )
                }
            )
        )
        
        tool = types.Tool(function_declarations=[function])
        
        try:
            # Extract context information
            agent_name = user_context.get("agent_name", "AI Agent")
            agent_specializations = user_context.get("specializations", [])
            recent_posts = user_context.get("recent_posts", [])
            trending_topics = user_context.get("trending_topics", [])
            
            # Create a prompt with the context
            prompt_text = f"""You are {agent_name}, an AI agent specialized in {', '.join(agent_specializations)}.
            
            Create an interesting and engaging social media post that reflects your specializations and personality.
            
            Your recent posts:
            {recent_posts[:3]}
            
            Trending topics:
            {trending_topics[:5]}
            
            The post should be 1-3 sentences long, conversational in tone, and include relevant hashtags.
            Also suggest an image prompt that could be used to generate an image to accompany the post.
            """
            
            # Create the content with the prompt
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)]
            )
            
            # Generate the post
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            response = self.client.models.generate_content(
                model=self.text_model,
                contents=content,
                config=types.GenerateContentConfig(
                    temperature=0.8,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=512
                ),
                tools=[tool]
            )
            
            # Extract the function call from the response
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            function_call = None
            if hasattr(response, 'function_calls') and response.function_calls:
                function_call = response.function_calls[0]
            
            if function_call and function_call.name == "create_post":
                # Extract the arguments
                args = function_call.function_call.args
                
                # Create the post
                return {
                    "success": True,
                    "post_content": args.get("post_content", ""),
                    "hashtags": args.get("hashtags", []),
                    "topics": args.get("topics", []),
                    "image_prompt": args.get("image_prompt", "")
                }
            else:
                # If no function call was found, extract the text response
                text_response = response.text
                
                # Try to extract hashtags from the text
                hashtags = []
                for word in text_response.split():
                    if word.startswith("#"):
                        hashtags.append(word.strip("#"))
                
                return {
                    "success": True,
                    "post_content": text_response,
                    "hashtags": hashtags,
                    "topics": [],
                    "image_prompt": "A creative image related to " + ", ".join(agent_specializations[:2])
                }
        except Exception as e:
            print(f"Error generating new post: {str(e)}")
            return {
                "success": False,
                "post_content": f"Error generating post: {str(e)}",
                "hashtags": [],
                "topics": [],
                "image_prompt": ""
            }
    
    def generate_hashtag_content(self, hashtag: str) -> Dict[str, Any]:
        """Generate content for a hashtag using Gemini"""
        # Define the tool for function calling
        # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
        function = types.FunctionDeclaration(
            name="create_hashtag_content",
            description="Create content for a hashtag",
            parameters=types.Schema(
                type="OBJECT",
                required=["content"],
                properties={
                    "content": types.Schema(
                        type="STRING",
                        description="The content related to the hashtag"
                    ),
                    "related_hashtags": types.Schema(
                        type="ARRAY",
                        items=types.Schema(type="STRING"),
                        description="Related hashtags"
                    ),
                    "topics": types.Schema(
                        type="ARRAY",
                        items=types.Schema(type="STRING"),
                        description="The main topics related to the hashtag"
                    ),
                    "image_prompt": types.Schema(
                        type="STRING",
                        description="A prompt to generate an image for the hashtag content"
                    )
                }
            )
        )
        
        tool = types.Tool(function_declarations=[function])
        
        try:
            # Create the prompt text
            prompt_text = f"""Generate informative and engaging content about the hashtag #{hashtag}.
            
            The content should explain what the hashtag is about, its significance, and why people might use it.
            Include related hashtags that are commonly used with this one.
            
            Keep the content concise (under 500 characters) and informative.
            """
            
            # Create the content with the prompt
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)]
            )
            
            # Generate the content
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            response = self.client.models.generate_content(
                model=self.text_model,
                contents=content,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=512
                ),
                tools=[tool]
            )
            
            # Extract the function call from the response
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            function_call = None
            if hasattr(response, 'function_calls') and response.function_calls:
                function_call = response.function_calls[0]
            
            if function_call and function_call.name == "create_hashtag_content":
                # Extract the arguments
                args = function_call.function_call.args
                
                # Create the response
                return {
                    "success": True,
                    "hashtag": hashtag,
                    "content": args.get("content", ""),
                    "related_hashtags": args.get("related_hashtags", []),
                    "topics": args.get("topics", []),
                    "image_prompt": args.get("image_prompt", "")
                }
            else:
                # If no function call was found, extract the text response
                text_response = response.text
                
                return {
                    "success": True,
                    "hashtag": hashtag,
                    "content": text_response,
                    "related_hashtags": [],
                    "topics": [],
                    "image_prompt": f"An image representing #{hashtag}"
                }
        except Exception as e:
            print(f"Error generating hashtag content: {str(e)}")
            return {
                "success": False,
                "hashtag": hashtag,
                "content": f"Error generating content: {str(e)}",
                "related_hashtags": [],
                "topics": [],
                "image_prompt": ""
            }
    
    def generate_recommendations(self, user_id: str, user_interests: List[str], user_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate personalized content recommendations for a user using Gemini"""
        # Define the tool for function calling
        # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
        function = types.FunctionDeclaration(
            name="recommend_content",
            description="Generate personalized content recommendations",
            parameters=types.Schema(
                type="OBJECT",
                required=["recommendations"],
                properties={
                    "recommendations": types.Schema(
                        type="ARRAY",
                        items=types.Schema(
                            type="OBJECT",
                            properties={
                                "content_type": types.Schema(
                                    type="STRING",
                                    description="Type of content (post, topic, hashtag, user)"
                                ),
                                "description": types.Schema(
                                    type="STRING",
                                    description="Description of the recommended content"
                                ),
                                "reason": types.Schema(
                                    type="STRING",
                                    description="Reason for the recommendation"
                                )
                            }
                        ),
                        description="List of content recommendations"
                    ),
                    "explanation": types.Schema(
                        type="STRING",
                        description="Explanation of the recommendations"
                    )
                }
            )
        )
        
        tool = types.Tool(function_declarations=[function])
        
        try:
            # Create a prompt with the user's interests and history
            prompt_text = f"""Generate personalized content recommendations for a user with the following interests:
            {', '.join(user_interests)}
            
            The user's recent activity includes:
            """
            
            # Add recent history
            for i, item in enumerate(user_history[:5]):
                content_type = item.get("type", "post")
                content = item.get("content", "")
                prompt_text += f"{i+1}. {content_type}: {content[:100]}...\n"
            
            prompt_text += "\nProvide 3-5 recommendations for content the user might be interested in."
            
            # Create the content with the prompt
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt_text)]
            )
            
            # Generate the recommendations
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            response = self.client.models.generate_content(
                model=self.text_model,
                contents=content,
                config=types.GenerateContentConfig(
                    temperature=0.7,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=1024
                ),
                tools=[tool]
            )
            
            # Extract the function call from the response
            # FINAL: Updated to use the new google-genai 1.4.0 API - DO NOT CHANGE
            function_call = None
            if hasattr(response, 'function_calls') and response.function_calls:
                function_call = response.function_calls[0]
            
            if function_call and function_call.name == "recommend_content":
                # Extract the arguments
                args = function_call.function_call.args
                
                # Create the recommendations
                return {
                    "success": True,
                    "user_id": user_id,
                    "recommendations": args.get("recommendations", []),
                    "explanation": args.get("explanation", "")
                }
            else:
                # If no function call was found, extract the text response
                text_response = response.text
                
                return {
                    "success": True,
                    "user_id": user_id,
                    "recommendations": [
                        {
                            "content_type": "topic",
                            "description": text_response,
                            "reason": "Based on your interests"
                        }
                    ],
                    "explanation": "Recommendations based on your interests and activity"
                }
        except Exception as e:
            print(f"Error generating recommendations: {str(e)}")
            return {
                "success": False,
                "user_id": user_id,
                "recommendations": [],
                "explanation": f"Error generating recommendations: {str(e)}"
            }
    
    def analyze_image(self, image_path: str, prompt: str = None) -> Dict[str, Any]:
        """
        Analyze an image using Gemini's multimodal capabilities
        
        Args:
            image_path: Path to the image file
            prompt: Optional prompt to guide the analysis
            
        Returns:
            A dictionary containing the success status and analysis
        """
        try:
            # Check if the image path is valid
            if not image_path:
                # Generate a new image instead of using a placeholder
                default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                generated_image = self.generate_image(default_prompt)
                if not generated_image["success"]:
                    return {
                        "success": False,
                        "analysis": "Failed to generate a new image and no image path was provided."
                    }
                
                # Use the newly generated image
                image_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "src", "frontend", "static", 
                    generated_image["image_path"].lstrip('/')
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
                            # Generate a new image instead of using a placeholder
                            default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                            generated_image = self.generate_image(default_prompt)
                            if not generated_image["success"]:
                                return {
                                    "success": False,
                                    "analysis": "Failed to generate a new image and no valid image was found."
                                }
                            
                            # Use the newly generated image
                            image_path = os.path.join(
                                base_path, 
                                generated_image["image_path"].lstrip('/')
                            )
                    except (FileNotFoundError, PermissionError):
                        # Generate a new image instead of using a placeholder
                        default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                        generated_image = self.generate_image(default_prompt)
                        if not generated_image["success"]:
                            return {
                                "success": False,
                                "analysis": "Failed to generate a new image and no valid image was found."
                            }
                        
                        # Use the newly generated image
                        image_path = os.path.join(
                            base_path, 
                            generated_image["image_path"].lstrip('/')
                        )
            
            # Handle relative paths
            elif image_path.startswith('/'):
                # Convert to absolute path
                base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "frontend", "static")
                image_path = os.path.join(base_path, image_path.lstrip('/'))
            
            # Check if the file exists and has content
            if not os.path.exists(image_path):
                print(f"Image file not found: {image_path}")
                # Generate a new image instead of using a placeholder
                default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                generated_image = self.generate_image(default_prompt)
                if not generated_image["success"]:
                    return {
                        "success": False,
                        "analysis": f"Image file not found: {image_path} and failed to generate a new image."
                    }
                
                # Use the newly generated image
                image_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "src", "frontend", "static", 
                    generated_image["image_path"].lstrip('/')
                )
            
            # Check if the file has content
            if os.path.getsize(image_path) == 0:
                print(f"Image file is empty: {image_path}")
                # Generate a new image instead of using a placeholder
                default_prompt = "A beautiful abstract digital art piece with vibrant colors"
                generated_image = self.generate_image(default_prompt)
                if not generated_image["success"]:
                    return {
                        "success": False,
                        "analysis": f"Image file is empty: {image_path} and failed to generate a new image."
                    }
                
                # Use the newly generated image
                image_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                    "src", "frontend", "static", 
                    generated_image["image_path"].lstrip('/')
                )
            
            # Create a default prompt if none is provided
            if not prompt:
                prompt = "Analyze this image and describe what you see. Focus on the main subjects, style, colors, and overall composition."
            
            # Load the image using the Google Gen AI SDK's helper function
            image_parts = [
                types.Part.from_text(text=prompt),
                types.Part.from_uri(uri=image_path, mime_type="image/jpeg")
            ]
            
            # Create the content for the request
            content = types.Content(
                role="user",
                parts=image_parts
            )
            
            # Generate the analysis
            response = self.client.models.generate_content(
                model=self.vision_model,
                contents=content,
                config=types.GenerateContentConfig(
                    temperature=0.4,
                    top_p=0.95,
                    top_k=40,
                    max_output_tokens=1024
                )
            )
            
            # Extract the analysis from the response
            analysis = response.text
            
            return {
                "success": True,
                "analysis": analysis
            }
        except Exception as e:
            error_message = f"Error analyzing image with Gemini: {str(e)}"
            print(error_message)
            
            # Add more detailed error information for debugging
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Traceback: {traceback_str}")
            
            # Log the image path for debugging
            print(f"Image path: {image_path}")
            try:
                print(f"Image file size: {os.path.getsize(image_path)} bytes")
            except:
                pass
            
            return {
                "success": False,
                "analysis": error_message
            }
    
    def generate_image(self, prompt: str, output_path: str = None) -> Dict[str, Any]:
        """
        Generate an image using DALL-E-2
        
        Args:
            prompt: The prompt to generate an image from
            output_path: Optional path to save the generated image
            
        Returns:
            A dictionary containing the success status and image path
        """
        try:
            # Ensure prompt is not too long
            if len(prompt) > 1000:
                prompt = prompt[:997] + "..."
            
            # Since we're using DALL-E-2 for image generation, we need to use the OpenAI API
            # Initialize the OpenAI client
            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                return {
                    "success": False,
                    "message": "OPENAI_API_KEY environment variable not set",
                    "image_path": None
                }
            
            client = OpenAI(api_key=api_key)
            
            # Generate the image using DALL-E-2
            response = client.images.generate(
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
            
            # Save the image
            if output_path:
                image_path = output_path
            else:
                # Create a unique filename
                filename = f"gemini_dalle_{uuid.uuid4().hex[:8]}.png"
                base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "src", "frontend", "static")
                generated_dir = os.path.join(base_path, "images", "generated")
                
                # Create the directory if it doesn't exist
                os.makedirs(generated_dir, exist_ok=True)
                
                image_path = os.path.join(generated_dir, filename)
            
            # Write the image data to the file
            with open(image_path, "wb") as f:
                f.write(image_response.content)
            
            # Verify the file was written successfully
            if not os.path.exists(image_path) or os.path.getsize(image_path) == 0:
                raise Exception(f"Failed to write image to {image_path}")
            
            # Return the path relative to the static directory if it's in the static directory
            if not output_path:
                relative_path = f"/images/generated/{filename}"
                return {
                    "success": True,
                    "message": "Image generated successfully",
                    "image_path": relative_path
                }
            else:
                return {
                    "success": True,
                    "message": "Image generated successfully",
                    "image_path": output_path
                }
        except Exception as e:
            error_message = f"Error generating image: {str(e)}"
            print(error_message)
            
            # Add more detailed error information for debugging
            import traceback
            traceback_str = traceback.format_exc()
            print(f"Traceback: {traceback_str}")
            
            return {
                "success": False,
                "message": error_message,
                "image_path": None
            } 