"""
Test script to verify that the system components are working correctly.
"""
import os
import sys
import json
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.trend_spotter import TrendSpotterAgent
from src.agents.deep_dive import DeepDiveAgent
from src.agents.entertainer import EntertainerAgent
from src.knowledge.graph import KnowledgeGraph
from src.content.generator import ContentGenerator
from src.content.storage import ContentStorage
from src.feedback.metrics import EngagementMetrics
from src.feedback.attention import AttentionTracker
from src.interface.feed import ContentFeed
from src.interface.engagement import EngagementHandler

def test_knowledge_graph():
    """Test the knowledge graph component."""
    print("\n=== Testing Knowledge Graph ===")
    
    # Initialize knowledge graph
    kg = KnowledgeGraph()
    
    # Get trending topics
    trending_topics = kg.get_trending_topics()
    print(f"Trending topics: {trending_topics}")
    
    # Get popular topics
    popular_topics = kg.get_popular_topics()
    print(f"Popular topics: {popular_topics}")
    
    # Update a topic weight
    test_topic = trending_topics[0] if trending_topics else "Test Topic"
    kg.update_topic_weight(test_topic, 0.8)
    print(f"Updated weight for topic: {test_topic}")
    
    # Save knowledge graph
    kg.save()
    print("Knowledge graph saved.")
    
    return kg

def test_agents(knowledge_graph):
    """Test the agent components."""
    print("\n=== Testing Agents ===")
    
    # Create agents
    trend_spotter = TrendSpotterAgent()
    deep_dive = DeepDiveAgent()
    entertainer = EntertainerAgent()
    
    print(f"Created TrendSpotter agent with ID: {trend_spotter.id}")
    print(f"Created DeepDive agent with ID: {deep_dive.id}")
    print(f"Created Entertainer agent with ID: {entertainer.id}")
    
    # Generate content
    trend_content = trend_spotter.generate_content(knowledge_graph)
    deep_content = deep_dive.generate_content(knowledge_graph)
    fun_content = entertainer.generate_content(knowledge_graph)
    
    print(f"\nTrendSpotter generated: {trend_content['title']}")
    print(f"DeepDive generated: {deep_content['title']}")
    print(f"Entertainer generated: {fun_content['title']}")
    
    return [trend_spotter, deep_dive, entertainer], [trend_content, deep_content, fun_content]

def test_content_storage(content_items):
    """Test the content storage component."""
    print("\n=== Testing Content Storage ===")
    
    # Initialize content storage
    storage = ContentStorage()
    
    # Store content
    for content in content_items:
        content_id = storage.store_content(content)
        print(f"Stored content with ID: {content_id}")
    
    # Get latest content
    latest = storage.get_latest_content(3)
    print(f"Retrieved {len(latest)} latest content items")
    
    return storage

def test_content_generator(knowledge_graph, agents):
    """Test the content generator component."""
    print("\n=== Testing Content Generator ===")
    
    # Initialize content generator
    generator = ContentGenerator(knowledge_graph)
    
    # Add agents
    for agent in agents:
        generator.add_agent(agent)
    
    # Generate content batch
    batch = generator.generate_content_batch(3)
    print(f"Generated batch of {len(batch)} content items")
    
    for i, content in enumerate(batch):
        print(f"{i+1}. {content['title']} by {content['agent_name']}")
    
    return generator, batch

def test_engagement(content_generator, content_items):
    """Test the engagement components."""
    print("\n=== Testing Engagement ===")
    
    # Initialize engagement metrics
    metrics = EngagementMetrics()
    
    # Initialize engagement handler
    handler = EngagementHandler(metrics, content_generator)
    
    # Test attention tracking
    tracker = AttentionTracker()
    
    # Start viewing
    content_id = content_items[0]["id"]
    agent_id = content_items[0]["agent_id"]
    
    print(f"Starting to view content: {content_id}")
    tracker.start_viewing(content_id)
    
    # Simulate viewing for 5 seconds
    import time
    time.sleep(5)
    
    # Stop viewing
    result = tracker.stop_viewing()
    print(f"Viewed for {result['view_time']:.2f} seconds")
    
    # Record like
    handler.record_like(content_id, agent_id)
    print(f"Recorded like for content: {content_id}")
    
    # Adapt agents
    handler.adapt_agents()
    print("Adapted agents based on feedback")
    
    return handler

def test_content_feed(content_storage):
    """Test the content feed component."""
    print("\n=== Testing Content Feed ===")
    
    # Initialize content feed
    feed = ContentFeed(content_storage)
    
    # Get current item
    current = feed.get_current_item()
    if current:
        print(f"Current item: {current['title']} by {current['agent_name']}")
    else:
        print("No current item")
    
    # Get next item
    next_item = feed.next_item()
    if next_item:
        print(f"Next item: {next_item['title']} by {next_item['agent_name']}")
    else:
        print("No next item")
    
    # Get feed preview
    preview = feed.get_feed_preview(2)
    print(f"Feed preview has {len(preview)} items")
    
    return feed

def main():
    """Run the system tests."""
    print("=== AI Agent Social Network System Test ===")
    print(f"Started at: {datetime.now().isoformat()}")
    
    try:
        # Test knowledge graph
        kg = test_knowledge_graph()
        
        # Test agents
        agents, content_items = test_agents(kg)
        
        # Test content storage
        storage = test_content_storage(content_items)
        
        # Test content generator
        generator, batch = test_content_generator(kg, agents)
        
        # Test engagement
        handler = test_engagement(generator, content_items)
        
        # Test content feed
        feed = test_content_feed(storage)
        
        print("\n=== All Tests Completed Successfully ===")
        print(f"Finished at: {datetime.now().isoformat()}")
        return 0
        
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 