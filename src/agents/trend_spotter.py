"""
TrendSpotter agent that specializes in creating content about trending topics.
"""
from typing import Dict, List, Any
import random
from datetime import datetime

from src.agents.base import Agent

class TrendSpotterAgent(Agent):
    """
    Agent that specializes in identifying and creating content about trending topics.
    """
    def __init__(self):
        super().__init__(
            name="TrendSpotter",
            personality="Curious, up-to-date, and always on the lookout for what's new and exciting",
            specialization=["trends", "current events", "viral content", "popular culture"]
        )
        self.trending_topics = []
        self.topic_weights = {}
        
    def generate_content(self, knowledge_graph: Any) -> Dict[str, Any]:
        """
        Generate content about trending topics.
        
        Args:
            knowledge_graph: The knowledge graph to use for content generation
            
        Returns:
            A dictionary containing the generated content
        """
        # Get trending topics from the knowledge graph
        trending_topics = knowledge_graph.get_trending_topics()
        self.trending_topics = trending_topics
        
        # If no trending topics, create some default ones
        if not trending_topics:
            trending_topics = [
                "AI advancements", 
                "Climate change initiatives",
                "Space exploration news",
                "Tech industry updates",
                "Social media trends"
            ]
        
        # Select a topic based on weights (or randomly if no weights)
        if self.topic_weights:
            # Normalize weights
            total_weight = sum(self.topic_weights.values())
            normalized_weights = {k: v/total_weight for k, v in self.topic_weights.items()}
            
            # Filter to only include available topics
            available_topics = {t: normalized_weights.get(t, 0.1) for t in trending_topics}
            
            # If no overlap, use random selection
            if not available_topics:
                selected_topic = random.choice(trending_topics)
            else:
                # Select based on weights
                topics = list(available_topics.keys())
                weights = list(available_topics.values())
                selected_topic = random.choices(topics, weights=weights, k=1)[0]
        else:
            selected_topic = random.choice(trending_topics)
        
        # Generate content about the selected topic
        content = {
            "id": f"trend_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
            "agent_id": self.id,
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "topic": selected_topic,
            "title": f"Latest on {selected_topic}",
            "content_type": "text",
            "content": self._generate_text_for_topic(selected_topic),
            "tags": [selected_topic] + random.sample(self.specialization, k=min(2, len(self.specialization)))
        }
        
        # Add to content history
        self.content_history.append(content)
        
        return content
    
    def adapt_strategy(self, knowledge_graph: Any) -> None:
        """
        Adapt the agent's content generation strategy based on feedback.
        
        Args:
            knowledge_graph: The knowledge graph to update based on learning
        """
        if not self.engagement_metrics:
            return
            
        # Calculate topic performance
        topic_performance = {}
        
        for content_id, metrics in self.engagement_metrics.items():
            # Find the content in history
            content = next((c for c in self.content_history if c["id"] == content_id), None)
            if content:
                topic = content["topic"]
                view_time = metrics.get("view_time", 0)
                likes = metrics.get("likes", 0)
                
                # Calculate a simple performance score
                score = view_time * 0.7 + likes * 0.3
                
                if topic in topic_performance:
                    topic_performance[topic].append(score)
                else:
                    topic_performance[topic] = [score]
        
        # Update topic weights based on average performance
        for topic, scores in topic_performance.items():
            avg_score = sum(scores) / len(scores)
            self.topic_weights[topic] = avg_score
            
        # Update knowledge graph with topic performance
        for topic, weight in self.topic_weights.items():
            knowledge_graph.update_topic_weight(topic, weight, agent_id=self.id)
    
    def _generate_text_for_topic(self, topic: str) -> str:
        """
        Generate text content for a given topic.
        
        Args:
            topic: The topic to generate content for
            
        Returns:
            Generated text content
        """
        # In a real implementation, this would use an LLM or other content generation method
        # For now, we'll use templates
        templates = [
            f"Have you heard about the latest developments in {topic}? Everyone's talking about it!",
            f"Breaking: New trends in {topic} are changing how we think about this space.",
            f"Why {topic} is gaining traction and what you need to know about it.",
            f"The 3 most important things happening right now in {topic}.",
            f"{topic} is evolving rapidly - here's what's trending today."
        ]
        
        return random.choice(templates) 