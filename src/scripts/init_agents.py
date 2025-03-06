"""
Script for initializing the agents in the system.
"""
import os
import sys
import argparse
from typing import List

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.agents.trend_spotter import TrendSpotterAgent
from src.agents.deep_dive import DeepDiveAgent
from src.agents.entertainer import EntertainerAgent
from src.knowledge.graph import KnowledgeGraph
from src.content.generator import ContentGenerator
from src.content.storage import ContentStorage

def initialize_agents(count: int = 3) -> List[str]:
    """
    Initialize the agents in the system.
    
    Args:
        count: Number of agents to initialize (max 3)
        
    Returns:
        List of agent IDs
    """
    # Ensure count is valid
    count = min(count, 3)
    
    # Initialize knowledge graph
    knowledge_graph = KnowledgeGraph()
    
    # Initialize content storage
    content_storage = ContentStorage()
    
    # Initialize content generator
    content_generator = ContentGenerator(knowledge_graph)
    
    # Create agents
    agents = []
    agent_ids = []
    
    if count >= 1:
        trend_spotter = TrendSpotterAgent()
        agents.append(trend_spotter)
        agent_ids.append(trend_spotter.id)
        content_generator.add_agent(trend_spotter)
        print(f"Created TrendSpotter agent with ID: {trend_spotter.id}")
    
    if count >= 2:
        deep_dive = DeepDiveAgent()
        agents.append(deep_dive)
        agent_ids.append(deep_dive.id)
        content_generator.add_agent(deep_dive)
        print(f"Created DeepDive agent with ID: {deep_dive.id}")
    
    if count >= 3:
        entertainer = EntertainerAgent()
        agents.append(entertainer)
        agent_ids.append(entertainer.id)
        content_generator.add_agent(entertainer)
        print(f"Created Entertainer agent with ID: {entertainer.id}")
    
    # Generate initial content
    print("\nGenerating initial content...")
    for agent in agents:
        content = agent.generate_content(knowledge_graph)
        content_storage.store_content(content)
        print(f"Generated content: {content['title']} by {agent.name}")
    
    # Save knowledge graph
    knowledge_graph.save()
    print("\nKnowledge graph saved.")
    
    return agent_ids

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize agents in the system")
    parser.add_argument("--count", type=int, default=3, help="Number of agents to initialize (max 3)")
    args = parser.parse_args()
    
    initialize_agents(args.count) 