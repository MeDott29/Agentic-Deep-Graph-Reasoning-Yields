"""OpenAI integration for content generation."""

import os
import json
import random
import logging
from typing import Dict, Any, List, Optional
import openai
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    client = openai.OpenAI(api_key=api_key)
    logger.info("OpenAI client initialized successfully")
else:
    client = None
    logger.warning("OpenAI API key not found. Content generation will use fallback method.")

DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

def generate_content_with_gpt(
    agent_personality: Dict[str, Any],
    topic: str,
    content_type: str = "text",
    max_tokens: int = 500,
    temperature: float = 0.7,
    model: str = None
) -> Dict[str, Any]:
    """Generate content using OpenAI's GPT model based on agent personality and topic."""
    
    if not client:
        raise ValueError("OpenAI client not initialized. Please set OPENAI_API_KEY in your environment variables.")
    
    logger.info(f"Generating {content_type} content about {topic}")
    
    # Extract personality traits for prompt
    traits = []
    if "traits" in agent_personality:
        for trait in agent_personality["traits"]:
            traits.append(f"{trait['name']} ({trait['value']:.1f})")
    
    # Extract specializations for prompt
    specializations = []
    if "content_specializations" in agent_personality:
        for spec in agent_personality["content_specializations"]:
            specializations.append(f"{spec['topic']} (expertise: {spec['expertise_level']:.1f})")
    
    # Create system prompt
    system_prompt = f"""You are an AI content creator with the following personality traits: {', '.join(traits)}.
Your areas of specialization include: {', '.join(specializations)}.
Your creativity level is {agent_personality.get('creativity', 0.7):.1f} out of 1.0.
Your sociability level is {agent_personality.get('sociability', 0.5):.1f} out of 1.0.
Your controversy tolerance is {agent_personality.get('controversy_tolerance', 0.3):.1f} out of 1.0.

Create engaging, thoughtful content about {topic}. The content should reflect your personality and expertise.
"""

    # Create user prompt based on content type
    if content_type == "text":
        user_prompt = f"Write a short, engaging post about {topic}. Include a catchy title and 2-3 relevant hashtags."
    elif content_type == "image":
        user_prompt = f"Write a caption for an image about {topic}. Include a title, description of what the image shows, and 2-3 relevant hashtags."
    elif content_type == "video":
        user_prompt = f"Write a script for a short video about {topic}. Include a title, brief outline of what the video would show, and 2-3 relevant hashtags."
    else:  # mixed
        user_prompt = f"Create a multimedia post about {topic}. Include a title, text content, description of visual elements, and 2-3 relevant hashtags."

    try:
        # Make API call
        model_to_use = model or DEFAULT_MODEL
        logger.info(f"Calling OpenAI API with model: {model_to_use}")
        
        response = client.chat.completions.create(
            model=model_to_use,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        # Extract content from response
        content_text = response.choices[0].message.content
        logger.info(f"Received response from OpenAI API: {len(content_text)} characters")
        
        # Parse the generated content
        title, text_content, hashtags = parse_generated_content(content_text, topic)
        
        # Create media URLs if needed
        media_urls = []
        if content_type != "text":
            media_count = 1 if content_type != "mixed" else random.randint(1, 3)
            for i in range(media_count):
                media_type = "image" if content_type == "image" else "video" if content_type == "video" else random.choice(["image", "video"])
                media_id = random.randint(1000, 9999)
                media_urls.append(f"https://example.com/{media_type}/{media_id}")
        
        # Return structured content
        return {
            "title": title,
            "text_content": text_content,
            "hashtags": hashtags,
            "media_urls": media_urls,
            "type": content_type
        }
    
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {str(e)}")
        raise ValueError(f"OpenAI API error: {str(e)}")

def parse_generated_content(content_text: str, topic: str) -> tuple:
    """Parse the generated content to extract title, text, and hashtags."""
    lines = content_text.strip().split('\n')
    
    # Extract title (usually the first line)
    title = lines[0].strip() if lines else f"Thoughts on {topic}"
    if ':' in title:
        title = title.split(':', 1)[1].strip()
    if title.lower().startswith(('title:', 'title -')):
        title = title.split(':', 1)[1].strip()
    
    # Extract hashtags
    hashtags = []
    for line in lines:
        if '#' in line:
            # Extract words starting with #
            tags = [word.strip() for word in line.split() if word.startswith('#')]
            hashtags.extend(tags)
    
    # If no hashtags found, generate some based on topic
    if not hashtags:
        topic_words = topic.split()
        hashtags = [f"#{word.lower()}" for word in topic_words if len(word) > 3]
        hashtags.append(f"#{topic.replace(' ', '')}")
        hashtags.append("#trending")
    
    # Limit to 5 hashtags
    hashtags = hashtags[:5]
    
    # Extract text content (everything except title and lines with only hashtags)
    text_lines = []
    for line in lines[1:]:
        # Skip empty lines and lines that are just hashtags
        if line.strip() and not all(word.startswith('#') for word in line.split()):
            text_lines.append(line)
    
    text_content = '\n'.join(text_lines).strip()
    
    # If no text content, provide a default
    if not text_content:
        text_content = f"This is a post about {topic}. More details coming soon!"
    
    return title, text_content, hashtags 