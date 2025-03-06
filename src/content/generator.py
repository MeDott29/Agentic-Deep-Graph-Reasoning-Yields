"""
Content generator for creating content from agents.
"""
from typing import Dict, List, Any, Optional
import random
from datetime import datetime

from src.agents.base import Agent
from src.knowledge.graph import KnowledgeGraph

class ContentGenerator:
    """
    Class for generating content from agents.
    """
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the content generator.
        
        Args:
            knowledge_graph: The knowledge graph to use for content generation
        """
        self.knowledge_graph = knowledge_graph
        self.agents = []
        
    def add_agent(self, agent: Agent) -> None:
        """
        Add an agent to the content generator.
        
        Args:
            agent: The agent to add
        """
        self.agents.append(agent)
        
        # Add agent to knowledge graph if not already there
        agent_node = self.knowledge_graph._get_agent_node(agent.id)
        if not agent_node:
            from src.knowledge.nodes import AgentNode
            agent_node = AgentNode(agent.id, agent.name, agent.personality, agent.specialization)
            self.knowledge_graph.add_node(agent_node)
    
    def generate_content(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate content from an agent.
        
        Args:
            agent_id: Optional ID of the agent to generate content from
            
        Returns:
            Generated content
        """
        if not self.agents:
            raise ValueError("No agents available for content generation")
        
        # Select agent
        if agent_id:
            agent = next((a for a in self.agents if a.id == agent_id), None)
            if not agent:
                raise ValueError(f"Agent with ID {agent_id} not found")
        else:
            agent = random.choice(self.agents)
        
        # Generate content
        content = agent.generate_content(self.knowledge_graph)
        
        return content
    
    def generate_content_batch(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate a batch of content from different agents.
        
        Args:
            count: Number of content items to generate
            
        Returns:
            List of generated content
        """
        if not self.agents:
            raise ValueError("No agents available for content generation")
        
        # Ensure we don't try to generate more content than we have agents
        count = min(count, len(self.agents))
        
        # Select random agents without replacement
        selected_agents = random.sample(self.agents, count)
        
        # Generate content
        content_batch = []
        for agent in selected_agents:
            content = agent.generate_content(self.knowledge_graph)
            content_batch.append(content)
        
        return content_batch
    
    def process_feedback(self, content_id: str, agent_id: str, metrics: Dict[str, float]) -> None:
        """
        Process feedback for a piece of content.
        
        Args:
            content_id: The ID of the content
            agent_id: The ID of the agent that created the content
            metrics: Dictionary of engagement metrics
        """
        # Find agent
        agent = next((a for a in self.agents if a.id == agent_id), None)
        if not agent:
            return
        
        # Send feedback to agent
        agent.receive_feedback(content_id, metrics)
        
        # Update knowledge graph
        if "topic" in agent.content_history[-1]:
            topic = agent.content_history[-1]["topic"]
            view_time = metrics.get("view_time", 0)
            likes = metrics.get("likes", 0)
            
            self.knowledge_graph.record_content_engagement(
                content_id, 
                agent_id, 
                topic, 
                view_time, 
                likes
            )
    
    def adapt_agents(self) -> None:
        """
        Adapt all agents based on feedback.
        """
        for agent in self.agents:
            agent.adapt_strategy(self.knowledge_graph)
        
        # Save knowledge graph after adaptation
        self.knowledge_graph.save() 