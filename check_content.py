#!/usr/bin/env python3
"""
Script to check content and images in the system
"""
from src.services.content import ContentService
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.ai_agent_service import AIAgentService

def main():
    # Initialize services
    kg_service = KnowledgeGraphService()
    content_service = ContentService(kg_service)
    agent_service = AIAgentService(kg_service)

    # Check online agents
    online_agents = agent_service.get_online_agents()
    print(f"Online agents: {len(online_agents)}")
    for agent in online_agents:
        print(f"- {agent.name} (ID: {agent.id})")
        print(f"  Specializations: {[spec.value for spec in agent.specializations]}")
        print(f"  Status: {agent.status.value}")
        print(f"  Post count: {agent.post_count}")
        print(f"  Comment count: {agent.comment_count}")
        print()

    # Check recent content
    recent_content = content_service.get_recent_content(limit=10)
    print(f"\nRecent content: {len(recent_content)}")
    
    # Print raw content to see its structure
    print("\nRaw content structure:")
    for i, content in enumerate(recent_content[:2]):
        print(f"\nContent {i+1}:")
        print(f"Type: {type(content)}")
        print(f"Dir: {dir(content)}")
        if hasattr(content, "__dict__"):
            print(f"Dict: {content.__dict__}")
        elif isinstance(content, dict):
            print(f"Dict: {content}")
        else:
            print("No __dict__ attribute and not a dictionary")
    
    # Try to access content attributes
    print("\nContent details:")
    for i, content in enumerate(recent_content):
        print(f"\n{i+1}. Content item:")
        
        # Try different ways to access attributes
        if isinstance(content, dict):
            content_id = content.get('id', 'Unknown')
            title = content.get('title', 'No title')
            user_id = content.get('user_id', 'Unknown')
            file_path = content.get('file_path', None) or content.get('video_url', None)
            is_ai_generated = content.get('is_ai_generated', 'Unknown')
            created_at = content.get('created_at', 'Unknown')
        else:
            content_id = getattr(content, 'id', 'Unknown')
            title = getattr(content, 'title', 'No title')
            user_id = getattr(content, 'user_id', 'Unknown')
            file_path = getattr(content, 'file_path', None) or getattr(content, 'video_url', None)
            is_ai_generated = getattr(content, 'is_ai_generated', 'Unknown')
            created_at = getattr(content, 'created_at', 'Unknown')
        
        print(f"   Content ID: {content_id}")
        print(f"   Title: {title}")
        print(f"   User ID: {user_id}")
        print(f"   Has image: {file_path is not None}")
        if file_path:
            print(f"   Image path: {file_path}")
        print(f"   Is AI generated: {is_ai_generated}")
        print(f"   Created at: {created_at}")

if __name__ == "__main__":
    main() 