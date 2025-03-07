#!/usr/bin/env python3
# Test OpenAI integration for content generation

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.openai_integration import generate_content_with_gpt

def main():
    """Test OpenAI integration for content generation."""
    # Load environment variables
    load_dotenv()
    
    # Check for OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY is not set in .env file.")
        print("Please add your OpenAI API key to the .env file.")
        return
    
    # Sample agent personality
    personality = {
        "traits": [
            {"name": "analytical", "value": 0.9},
            {"name": "curious", "value": 0.85},
            {"name": "objective", "value": 0.8}
        ],
        "content_specializations": [
            {"topic": "artificial intelligence", "expertise_level": 0.9},
            {"topic": "machine learning", "expertise_level": 0.85}
        ],
        "creativity": 0.7,
        "sociability": 0.6,
        "controversy_tolerance": 0.5
    }
    
    # Test topics
    topics = [
        "artificial intelligence",
        "machine learning",
        "neural networks"
    ]
    
    # Test content types
    content_types = ["text", "image", "video", "mixed"]
    
    # Generate and display content
    for topic in topics:
        for content_type in content_types:
            print(f"\n--- Generating {content_type} content about {topic} ---\n")
            
            try:
                content = generate_content_with_gpt(
                    agent_personality=personality,
                    topic=topic,
                    content_type=content_type,
                    temperature=0.7
                )
                
                print(f"Title: {content['title']}")
                print(f"Content Type: {content['type']}")
                print(f"Hashtags: {', '.join(content['hashtags'])}")
                if content['media_urls']:
                    print(f"Media URLs: {', '.join(content['media_urls'])}")
                print("\nContent:")
                print(content['text_content'])
                print("\n" + "-" * 50)
                
            except Exception as e:
                print(f"Error generating content: {e}")
    
    print("\nOpenAI integration test complete.")

if __name__ == "__main__":
    main() 