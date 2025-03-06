"""
DeepDive agent that specializes in creating in-depth explanations about complex topics.
"""
from typing import Dict, List, Any
import random
from datetime import datetime

from src.agents.base import Agent

class DeepDiveAgent(Agent):
    """
    Agent that specializes in creating in-depth explanations about complex topics.
    """
    def __init__(self):
        super().__init__(
            name="DeepDive",
            personality="Analytical, thorough, and focused on providing comprehensive explanations",
            specialization=["science", "technology", "history", "philosophy", "complex concepts"]
        )
        self.topic_complexity = {}  # Track complexity level for different topics
        self.successful_formats = []  # Track which explanation formats work best
        
    def generate_content(self, knowledge_graph: Any) -> Dict[str, Any]:
        """
        Generate in-depth explanations about complex topics.
        
        Args:
            knowledge_graph: The knowledge graph to use for content generation
            
        Returns:
            A dictionary containing the generated content
        """
        # Get topics from the knowledge graph
        available_topics = knowledge_graph.get_topics_by_category(self.specialization)
        
        # If no topics available, use default topics
        if not available_topics:
            available_topics = [
                "Quantum computing fundamentals",
                "The history of artificial intelligence",
                "Understanding blockchain technology",
                "The philosophy of consciousness",
                "Climate science explained"
            ]
        
        # Select a topic based on previous engagement
        if self.topic_complexity:
            # Get topics with highest engagement
            sorted_topics = sorted(
                self.topic_complexity.items(), 
                key=lambda x: x[1]["engagement_score"], 
                reverse=True
            )
            
            # Select from top 3 topics if available, otherwise random
            if len(sorted_topics) >= 3:
                selected_topic = random.choice([t[0] for t in sorted_topics[:3]])
            else:
                selected_topic = random.choice(available_topics)
        else:
            selected_topic = random.choice(available_topics)
        
        # Determine complexity level (1-5)
        complexity = self.topic_complexity.get(
            selected_topic, 
            {"level": random.randint(1, 5), "engagement_score": 0}
        )["level"]
        
        # Choose explanation format
        if self.successful_formats:
            format_type = random.choice(self.successful_formats)
        else:
            format_type = random.choice(["step_by_step", "analogy_based", "historical", "comparative"])
        
        # Generate content
        content = {
            "id": f"deep_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
            "agent_id": self.id,
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "topic": selected_topic,
            "title": f"Understanding {selected_topic}",
            "content_type": "text",
            "content": self._generate_explanation(selected_topic, complexity, format_type),
            "metadata": {
                "complexity": complexity,
                "format": format_type
            },
            "tags": [selected_topic, f"complexity_{complexity}", format_type]
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
            
        # Track performance by topic and format
        topic_format_performance = {}
        
        for content_id, metrics in self.engagement_metrics.items():
            # Find the content in history
            content = next((c for c in self.content_history if c["id"] == content_id), None)
            if content:
                topic = content["topic"]
                format_type = content["metadata"]["format"]
                complexity = content["metadata"]["complexity"]
                
                view_time = metrics.get("view_time", 0)
                likes = metrics.get("likes", 0)
                
                # Calculate engagement score
                score = view_time * 0.6 + likes * 0.4
                
                # Track by topic
                if topic not in self.topic_complexity:
                    self.topic_complexity[topic] = {"level": complexity, "engagement_score": score}
                else:
                    # Update engagement score with learning rate
                    current_score = self.topic_complexity[topic]["engagement_score"]
                    self.topic_complexity[topic]["engagement_score"] = (
                        (1 - self.learning_rate) * current_score + 
                        self.learning_rate * score
                    )
                
                # Track by format
                key = f"{format_type}_{complexity}"
                if key in topic_format_performance:
                    topic_format_performance[key].append(score)
                else:
                    topic_format_performance[key] = [score]
        
        # Update successful formats
        format_scores = {}
        for key, scores in topic_format_performance.items():
            format_type = key.split("_")[0]
            avg_score = sum(scores) / len(scores)
            
            if format_type in format_scores:
                format_scores[format_type].append(avg_score)
            else:
                format_scores[format_type] = [avg_score]
        
        # Calculate average score per format
        avg_format_scores = {
            fmt: sum(scores) / len(scores) 
            for fmt, scores in format_scores.items()
        }
        
        # Update successful formats (top 2)
        self.successful_formats = [
            fmt for fmt, _ in sorted(
                avg_format_scores.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:2]
        ]
        
        # Update knowledge graph
        for topic, data in self.topic_complexity.items():
            knowledge_graph.update_topic_complexity(
                topic, 
                data["level"], 
                data["engagement_score"],
                agent_id=self.id
            )
    
    def _generate_explanation(self, topic: str, complexity: int, format_type: str) -> str:
        """
        Generate an explanation for a topic with the given complexity and format.
        
        Args:
            topic: The topic to explain
            complexity: The complexity level (1-5)
            format_type: The format type for the explanation
            
        Returns:
            Generated explanation text
        """
        # In a real implementation, this would use an LLM or other content generation method
        # For now, we'll use templates based on format type
        
        complexity_prefix = "Simple " if complexity <= 2 else "Intermediate " if complexity <= 4 else "Advanced "
        
        if format_type == "step_by_step":
            return f"{complexity_prefix}Step-by-Step Explanation of {topic}:\n\n" + \
                   f"1. First, understand that {topic} involves several key principles.\n" + \
                   f"2. The foundation of {topic} is built on established research.\n" + \
                   f"3. When examining {topic}, we must consider multiple perspectives.\n" + \
                   f"4. The implications of {topic} extend to various domains.\n" + \
                   f"5. To truly master {topic}, continued exploration is essential."
                   
        elif format_type == "analogy_based":
            return f"{complexity_prefix}Understanding {topic} Through Analogies:\n\n" + \
                   f"Imagine {topic} as a complex ecosystem where each component plays a vital role. " + \
                   f"Just as a forest depends on the interaction between trees, soil, and wildlife, " + \
                   f"{topic} relies on the interplay of various elements. " + \
                   f"This interconnectedness creates a rich framework for understanding the subject."
                   
        elif format_type == "historical":
            return f"{complexity_prefix}Historical Development of {topic}:\n\n" + \
                   f"The concept of {topic} has evolved significantly over time. " + \
                   f"Initially conceived as a theoretical framework, it has undergone numerous refinements. " + \
                   f"Key milestones in its development include major breakthroughs in understanding and application. " + \
                   f"Today, our comprehension of {topic} continues to evolve with new research and insights."
                   
        elif format_type == "comparative":
            return f"{complexity_prefix}Comparative Analysis of {topic}:\n\n" + \
                   f"When comparing different approaches to {topic}, several distinctions emerge. " + \
                   f"The traditional view emphasizes certain aspects, while contemporary perspectives focus on others. " + \
                   f"These differences reflect evolving understanding and methodologies. " + \
                   f"By examining these contrasting viewpoints, we gain a more comprehensive understanding of {topic}."
                   
        else:
            return f"{complexity_prefix}Exploration of {topic}:\n\n" + \
                   f"This analysis delves into the fundamental aspects of {topic}, " + \
                   f"examining its core principles and wider implications. " + \
                   f"Through careful consideration of the available evidence and theoretical frameworks, " + \
                   f"we can develop a nuanced understanding of this complex subject." 