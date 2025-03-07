#!/usr/bin/env python3
# Test script to verify fixes

import os
import sys
import json
from dotenv import load_dotenv

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agent import AgentService
from services.content import ContentService
from services.knowledge_graph import KnowledgeGraphService

def test_knowledge_graph():
    """Test knowledge graph node and edge creation."""
    print("\n=== Testing Knowledge Graph ===")
    
    # Initialize services
    graph_service = KnowledgeGraphService()
    
    # Create test nodes
    print("Creating test nodes...")
    user_node = graph_service.add_node("user", "test_user", {"name": "Test User"})
    print(f"Created user node: {user_node.id}")
    
    content_node = graph_service.add_node("content", "test_content", {"title": "Test Content"})
    print(f"Created content node: {content_node.id}")
    
    topic_node = graph_service.add_node("topic", "test_topic", {"name": "Test Topic"})
    print(f"Created topic node: {topic_node.id}")
    
    hashtag_node = graph_service.add_node("hashtag", "test_hashtag", {"name": "TestHashtag"})
    print(f"Created hashtag node: {hashtag_node.id}")
    
    # Create test edges
    print("\nCreating test edges...")
    try:
        created_edge = graph_service.add_edge("created", user_node.id, content_node.id)
        print(f"Created 'created' edge: {created_edge.id}")
        
        related_edge = graph_service.add_edge("related", content_node.id, topic_node.id)
        print(f"Created 'related' edge: {related_edge.id}")
        
        tagged_edge = graph_service.add_edge("tagged", content_node.id, hashtag_node.id)
        print(f"Created 'tagged' edge: {tagged_edge.id}")
        
        print("\nKnowledge graph tests passed!")
    except Exception as e:
        print(f"Error creating edges: {e}")
        return False
    
    return True

def test_agent_content_generation():
    """Test agent content generation."""
    print("\n=== Testing Agent Content Generation ===")
    
    # Initialize services
    agent_service = AgentService()
    
    # Get all agents
    agents = agent_service.list_agents()
    if not agents:
        print("No agents found. Please run init_agents.py first.")
        return False
    
    # Test content generation for the first agent
    agent = agents[0]
    print(f"Testing content generation for agent: {agent.username}")
    
    try:
        content = agent_service.generate_content(agent.id)
        print(f"Successfully generated content: {content.title}")
        print(f"Content type: {content.type}")
        print(f"Hashtags: {', '.join(content.hashtags)}")
        print(f"Content: {content.text_content[:100]}...")
        
        print("\nAgent content generation test passed!")
        return True
    except Exception as e:
        print(f"Error generating content: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run tests to verify fixes."""
    # Load environment variables
    load_dotenv()
    
    print("Running tests to verify fixes...")
    
    # Test knowledge graph
    kg_test_passed = test_knowledge_graph()
    
    # Test agent content generation
    agent_test_passed = test_agent_content_generation()
    
    # Print summary
    print("\n=== Test Summary ===")
    print(f"Knowledge Graph Test: {'PASSED' if kg_test_passed else 'FAILED'}")
    print(f"Agent Content Generation Test: {'PASSED' if agent_test_passed else 'FAILED'}")
    
    if kg_test_passed and agent_test_passed:
        print("\nAll tests passed! The fixes have been successfully applied.")
        return 0
    else:
        print("\nSome tests failed. Please check the error messages above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 