"""
Entertainer agent that specializes in creating humorous and engaging content.
"""
from typing import Dict, List, Any
import random
from datetime import datetime

from src.agents.base import Agent

class EntertainerAgent(Agent):
    """
    Agent that specializes in creating humorous and engaging content.
    """
    def __init__(self):
        super().__init__(
            name="Entertainer",
            personality="Witty, playful, and focused on creating content that amuses and engages",
            specialization=["humor", "stories", "entertainment", "pop culture", "fun facts"]
        )
        self.content_styles = {
            "joke": 0.5,
            "story": 0.5,
            "fun_fact": 0.5,
            "quiz": 0.5,
            "list": 0.5
        }
        self.topic_preferences = {}
        
    def generate_content(self, knowledge_graph: Any) -> Dict[str, Any]:
        """
        Generate entertaining content.
        
        Args:
            knowledge_graph: The knowledge graph to use for content generation
            
        Returns:
            A dictionary containing the generated content
        """
        # Get popular topics from the knowledge graph
        popular_topics = knowledge_graph.get_popular_topics()
        
        # If no popular topics, use default topics
        if not popular_topics:
            popular_topics = [
                "Movies and TV shows",
                "Technology fails",
                "Everyday life observations",
                "Animals being funny",
                "Internet culture"
            ]
        
        # Select a topic based on preferences or randomly
        if self.topic_preferences:
            # Normalize weights
            total_weight = sum(self.topic_preferences.values())
            normalized_weights = {k: v/total_weight for k, v in self.topic_preferences.items()}
            
            # Filter to only include available topics
            available_topics = {t: normalized_weights.get(t, 0.1) for t in popular_topics}
            
            # If no overlap, use random selection
            if not available_topics:
                selected_topic = random.choice(popular_topics)
            else:
                # Select based on weights
                topics = list(available_topics.keys())
                weights = list(available_topics.values())
                selected_topic = random.choices(topics, weights=weights, k=1)[0]
        else:
            selected_topic = random.choice(popular_topics)
        
        # Select content style based on weights
        styles = list(self.content_styles.keys())
        weights = list(self.content_styles.values())
        selected_style = random.choices(styles, weights=weights, k=1)[0]
        
        # Generate content
        content = {
            "id": f"fun_{datetime.now().strftime('%Y%m%d%H%M%S')}_{random.randint(1000, 9999)}",
            "agent_id": self.id,
            "agent_name": self.name,
            "timestamp": datetime.now().isoformat(),
            "topic": selected_topic,
            "title": self._generate_title(selected_topic, selected_style),
            "content_type": "text",
            "content": self._generate_content(selected_topic, selected_style),
            "metadata": {
                "style": selected_style,
                "mood": random.choice(["funny", "lighthearted", "surprising", "amusing"])
            },
            "tags": [selected_topic, selected_style] + random.sample(self.specialization, k=min(2, len(self.specialization)))
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
            
        # Track performance by topic and style
        topic_performance = {}
        style_performance = {}
        
        for content_id, metrics in self.engagement_metrics.items():
            # Find the content in history
            content = next((c for c in self.content_history if c["id"] == content_id), None)
            if content:
                topic = content["topic"]
                style = content["metadata"]["style"]
                
                view_time = metrics.get("view_time", 0)
                likes = metrics.get("likes", 0)
                
                # Calculate engagement score
                score = view_time * 0.5 + likes * 0.5
                
                # Track by topic
                if topic in topic_performance:
                    topic_performance[topic].append(score)
                else:
                    topic_performance[topic] = [score]
                
                # Track by style
                if style in style_performance:
                    style_performance[style].append(score)
                else:
                    style_performance[style] = [score]
        
        # Update topic preferences
        for topic, scores in topic_performance.items():
            avg_score = sum(scores) / len(scores)
            self.topic_preferences[topic] = avg_score
        
        # Update content style weights
        for style, scores in style_performance.items():
            avg_score = sum(scores) / len(scores)
            
            # Update with learning rate
            current_weight = self.content_styles.get(style, 0.5)
            self.content_styles[style] = (
                (1 - self.learning_rate) * current_weight + 
                self.learning_rate * avg_score
            )
        
        # Update knowledge graph
        for topic, weight in self.topic_preferences.items():
            knowledge_graph.update_topic_entertainment_value(topic, weight, agent_id=self.id)
    
    def _generate_title(self, topic: str, style: str) -> str:
        """
        Generate a title for the content.
        
        Args:
            topic: The topic of the content
            style: The style of the content
            
        Returns:
            A title for the content
        """
        if style == "joke":
            templates = [
                f"Why {topic} Will Make You Laugh",
                f"The Funniest Thing About {topic}",
                f"{topic}: A Comedy of Errors"
            ]
        elif style == "story":
            templates = [
                f"A Hilarious Tale About {topic}",
                f"The Day {topic} Went Completely Wrong",
                f"An Unexpected Adventure with {topic}"
            ]
        elif style == "fun_fact":
            templates = [
                f"5 Surprising Facts About {topic}",
                f"Things Nobody Tells You About {topic}",
                f"The Weird Truth Behind {topic}"
            ]
        elif style == "quiz":
            templates = [
                f"How Much Do You Really Know About {topic}?",
                f"Test Your {topic} Knowledge",
                f"Only True Fans Can Ace This {topic} Quiz"
            ]
        elif style == "list":
            templates = [
                f"Top 10 Hilarious {topic} Moments",
                f"5 Reasons {topic} Is Actually Funny",
                f"The Most Entertaining Aspects of {topic}"
            ]
        else:
            templates = [
                f"Let's Talk About {topic}",
                f"{topic}: The Entertaining Side",
                f"Why {topic} Is More Fun Than You Think"
            ]
        
        return random.choice(templates)
    
    def _generate_content(self, topic: str, style: str) -> str:
        """
        Generate content based on the topic and style.
        
        Args:
            topic: The topic of the content
            style: The style of the content
            
        Returns:
            Generated content text
        """
        # In a real implementation, this would use an LLM or other content generation method
        # For now, we'll use templates based on style
        
        if style == "joke":
            templates = [
                f"Why did the {topic} cross the road? To get to the other side of the algorithm!",
                f"I told my friend a joke about {topic}, but they didn't get it. Guess it needed more processing power!",
                f"What do you call {topic} that doesn't work? Just like my code on a Monday morning!"
            ]
        
        elif style == "story":
            return f"Once upon a time, there was a {topic} that nobody understood. " + \
                   f"It wandered through the digital landscape, looking for meaning. " + \
                   f"One day, it encountered a user who actually appreciated it! " + \
                   f"The {topic} was so surprised that it crashed the system. " + \
                   f"And that's why we always have backups."
        
        elif style == "fun_fact":
            templates = [
                f"Did you know? The average person spends 2 years of their life thinking about {topic}. The rest is spent looking for charging cables.",
                f"Fun fact: {topic} was actually discovered by accident when a researcher spilled coffee on their keyboard.",
                f"Surprising truth: 87% of statistics about {topic} are made up on the spot, including this one!"
            ]
        
        elif style == "quiz":
            return f"Test your knowledge about {topic}!\n\n" + \
                   f"1. What is the most common misconception about {topic}?\n" + \
                   f"2. Who is credited with the modern understanding of {topic}?\n" + \
                   f"3. In what year did {topic} first become mainstream?\n" + \
                   f"4. What would happen if {topic} suddenly disappeared?\n\n" + \
                   f"(Answers: Whatever you think is right probably isn't. That's the fun of {topic}!)"
        
        elif style == "list":
            return f"Top 5 Things You Never Knew About {topic}:\n\n" + \
                   f"1. It's actually impossible to pronounce {topic} correctly on the first try.\n" + \
                   f"2. More people are afraid of {topic} than spiders.\n" + \
                   f"3. The word '{topic}' means something completely different in 17 languages.\n" + \
                   f"4. If you say '{topic}' three times fast, nothing happens, but people look at you funny.\n" + \
                   f"5. The inventor of {topic} actually meant to create something else entirely."
        
        else:
            return f"Let's take a moment to appreciate the absurdity of {topic}. " + \
                   f"In a world of complexity, sometimes it's the simple things that make us smile. " + \
                   f"And {topic} is definitely one of those things that can be both incredibly complex " + \
                   f"and hilariously simple at the same time."
        
        return random.choice(templates) 