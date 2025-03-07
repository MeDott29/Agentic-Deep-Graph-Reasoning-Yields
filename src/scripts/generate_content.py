#!/usr/bin/env python3
# Generate initial content for AI agents

import os
import sys
import random
from datetime import datetime, timedelta

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agent import AgentService
from services.content import ContentService
from services.knowledge_graph import KnowledgeGraphService
from models.content import ContentCreate

# Sample content templates for different agent specializations
CONTENT_TEMPLATES = {
    "artificial intelligence": [
        "The future of {topic} looks promising with recent advancements in neural networks.",
        "How {topic} is transforming industries through automation and intelligent decision-making.",
        "Ethical considerations in {topic} development: balancing progress with responsibility.",
        "The role of {topic} in solving complex problems that were previously intractable.",
        "Understanding the fundamentals of {topic} and how they apply to real-world scenarios."
    ],
    "visual art": [
        "Exploring the intersection of {topic} and emotion in contemporary works.",
        "How digital tools are revolutionizing {topic} creation and distribution.",
        "The historical evolution of {topic} techniques and their modern applications.",
        "Finding inspiration for {topic} in unexpected places and everyday experiences.",
        "The role of cultural context in interpreting and appreciating {topic}."
    ],
    "philosophy": [
        "Examining the ethical implications of {topic} in modern society.",
        "How ancient perspectives on {topic} remain relevant in contemporary discourse.",
        "The intersection of {topic} and science: complementary or contradictory?",
        "Exploring different cultural approaches to {topic} across civilizations.",
        "The evolution of thinking about {topic} throughout human history."
    ],
    "physics": [
        "Recent breakthroughs in {topic} that challenge our understanding of reality.",
        "How {topic} explains everyday phenomena that we often take for granted.",
        "The beautiful mathematics behind {topic} and its elegant descriptions of nature.",
        "Exploring the frontiers of {topic} research and its potential applications.",
        "How {topic} connects to other scientific disciplines in unexpected ways."
    ],
    "world history": [
        "Forgotten episodes in {topic} that deserve more attention and study.",
        "How {topic} shapes our present: tracing the origins of modern institutions.",
        "Comparing perspectives on {topic} from different cultural viewpoints.",
        "The role of individuals versus systems in shaping {topic}.",
        "Patterns and cycles in {topic} that help us understand current events."
    ],
    "futurism": [
        "Predicting the next decade in {topic} based on current trends and innovations.",
        "How {topic} might reshape human society and daily life in coming years.",
        "The challenges and opportunities presented by emerging {topic} developments.",
        "Balancing optimism and caution when considering {topic} scenarios.",
        "The most underrated {topic} trends that deserve more attention."
    ],
    "music": [
        "How {topic} transcends cultural boundaries and connects diverse audiences.",
        "The evolution of {topic} production techniques and their impact on creativity.",
        "Analyzing the emotional impact of {topic} through psychological frameworks.",
        "The mathematics of {topic}: patterns, structures, and harmonies.",
        "How {topic} reflects and influences social movements throughout history."
    ],
    "psychology": [
        "Understanding {topic} patterns and how they influence decision-making.",
        "Recent research in {topic} that challenges conventional wisdom.",
        "How {topic} insights can improve personal relationships and communication.",
        "The neurological basis of {topic} and its evolutionary advantages.",
        "Cultural variations in {topic} and their implications for global understanding."
    ],
    "ecology": [
        "How {topic} principles can guide sustainable development and conservation.",
        "The interconnected nature of {topic} systems and the butterfly effect.",
        "Innovative solutions to {topic} challenges inspired by natural processes.",
        "The role of human activity in {topic} disruption and potential remedies.",
        "Understanding {topic} feedback loops and tipping points in natural systems."
    ],
    "cultural anthropology": [
        "Comparing {topic} practices across different societies and time periods.",
        "How {topic} rituals and traditions evolve while maintaining core meanings.",
        "The role of technology in transforming {topic} expressions and connections.",
        "Preserving {topic} heritage in an increasingly homogenized global society.",
        "How {topic} studies help us understand human universals and differences."
    ]
}

# Generic templates for any topic
GENERIC_TEMPLATES = [
    "Exploring the fascinating world of {topic} and its implications.",
    "10 things you might not know about {topic} that could change your perspective.",
    "The evolution of {topic} over time and what it means for the future.",
    "How {topic} connects to other fields in surprising and meaningful ways.",
    "Understanding {topic} through different lenses and frameworks."
]

def generate_hashtags(topic, specialization, count=3):
    """Generate relevant hashtags for content."""
    topic_words = topic.split()
    specialization_words = specialization.split()
    
    # Create hashtag pool
    hashtag_pool = [
        f"#{word.lower()}" for word in topic_words + specialization_words
        if len(word) > 3  # Only use words longer than 3 characters
    ]
    
    # Add some generic popular hashtags
    generic_hashtags = ["#trending", "#discover", "#knowledge", "#learning", 
                        "#interesting", "#thoughtprovoking", "#perspective"]
    
    hashtag_pool.extend(generic_hashtags)
    
    # Ensure uniqueness
    hashtag_pool = list(set(hashtag_pool))
    
    # Select random hashtags
    selected = random.sample(hashtag_pool, min(count, len(hashtag_pool)))
    
    return selected

def generate_content_for_agent(agent_id, agent_service, content_service, graph_service, count=5):
    """Generate content for a specific agent."""
    agent = agent_service.get_agent(agent_id)
    if not agent:
        print(f"Agent {agent_id} not found")
        return []
    
    print(f"Generating content for agent: {agent.username}")
    
    # Get agent specializations
    specializations = agent.personality.content_specializations
    if not specializations:
        print(f"No specializations found for agent {agent.username}")
        return []
    
    generated_content = []
    
    for _ in range(count):
        try:
            # Generate content using the agent service (which now uses OpenAI)
            content = agent_service.generate_content(agent.id)
            generated_content.append(content)
            
            print(f"  Created content: {content.title}")
            
            # Add to knowledge graph
            # Create content node
            content_node = graph_service.add_node("content", content.id)
            
            # Extract topic from content
            # For simplicity, use the first hashtag without the # symbol as the topic
            topic = None
            if content.hashtags:
                for hashtag in content.hashtags:
                    if hashtag.startswith('#'):
                        topic = hashtag[1:]
                        break
            
            # If no topic found, use a default one
            if not topic:
                # Try to find a topic from the agent's specializations
                if specializations:
                    topic = specializations[0].topic
                else:
                    topic = "general"
            
            # Create topic node if it doesn't exist
            topic_nodes = [
                node for node, attrs in graph_service.graph.nodes(data=True)
                if attrs.get("type") == "topic" and attrs.get("entity_id") == topic
            ]
            
            if not topic_nodes:
                topic_node = graph_service.add_node("topic", topic, {"name": topic})
                topic_node_id = topic_node.id
            else:
                topic_node_id = topic_nodes[0]
            
            # Create hashtag nodes and connect to content
            for hashtag in content.hashtags:
                hashtag_text = hashtag[1:] if hashtag.startswith('#') else hashtag  # Remove # symbol if present
                
                # Check if hashtag node already exists
                hashtag_nodes = [
                    node for node, attrs in graph_service.graph.nodes(data=True)
                    if attrs.get("type") == "hashtag" and attrs.get("entity_id") == hashtag_text
                ]
                
                if not hashtag_nodes:
                    # Create new hashtag node
                    hashtag_node = graph_service.add_node("hashtag", hashtag_text, {"name": hashtag_text})
                    hashtag_node_id = hashtag_node.id
                else:
                    # Use existing hashtag node
                    hashtag_node_id = hashtag_nodes[0]
                
                # Connect content to hashtag
                graph_service.add_edge("tagged", content_node.id, hashtag_node_id)
            
            # Connect content to topic
            graph_service.add_edge("related", content_node.id, topic_node_id)
            
            # Check if agent node exists
            agent_nodes = [
                node for node, attrs in graph_service.graph.nodes(data=True)
                if attrs.get("type") == "user" and attrs.get("entity_id") == agent.id
            ]
            
            if not agent_nodes:
                # Create agent node
                agent_node = graph_service.add_node("user", agent.id, {"name": agent.username})
                agent_node_id = agent_node.id
            else:
                # Use existing agent node
                agent_node_id = agent_nodes[0]
            
            # Connect agent to content
            graph_service.add_edge("created", agent_node_id, content_node.id)
            
        except Exception as e:
            print(f"  Error generating content: {e}")
            import traceback
            traceback.print_exc()
    
    return generated_content

def main():
    """Generate initial content for AI agents."""
    try:
        agent_service = AgentService()
        content_service = ContentService()
        graph_service = KnowledgeGraphService()
        
        # Get all agents
        agents = agent_service.list_agents()
        if not agents:
            print("No agents found. Please run init_agents.py first.")
            return
        
        print(f"Found {len(agents)} agents. Generating content...")
        total_content = 0
        
        # Generate content for each agent
        for agent in agents:
            try:
                content_count = random.randint(3, 5)  # Reduced count to avoid too many API calls
                print(f"Generating {content_count} content items for agent: {agent.username}")
                generated = generate_content_for_agent(
                    agent.id, 
                    agent_service, 
                    content_service, 
                    graph_service, 
                    count=content_count
                )
                total_content += len(generated)
                print(f"Successfully generated {len(generated)} content items for {agent.username}")
            except Exception as e:
                print(f"Error generating content for agent {agent.username}: {e}")
                import traceback
                traceback.print_exc()
        
        print(f"Generated a total of {total_content} content items for {len(agents)} agents")
        
        # Generate some random views, likes, and comments
        print("Generating interactions...")
        
        try:
            # Load all content
            content_data = content_service._load_data()
            all_content = [content for content in content_data["content"]]
            
            if not all_content:
                print("No content found to generate interactions for.")
                return
            
            print(f"Found {len(all_content)} content items. Generating interactions...")
            
            # Generate random views
            view_count = 0
            for content_item in all_content:
                num_views = random.randint(5, 20)  # Reduced for faster execution
                for _ in range(num_views):
                    # Random view duration between 5 and 120 seconds
                    view_duration = random.uniform(5, 120)
                    content_service.record_view(content_item["id"], None, view_duration)
                    view_count += 1
            
            print(f"Generated {view_count} views")
            
            # Generate random likes
            like_count = 0
            for content_item in all_content:
                # Like about 10-30% of views
                num_likes = random.randint(1, max(1, int(content_item["view_count"] * 0.3)))
                for _ in range(num_likes):
                    # Use a random agent as liker
                    liker = random.choice(agents)
                    content_service.like_content(content_item["id"], liker.id)
                    like_count += 1
            
            print(f"Generated {like_count} likes")
            
            # Generate random comments
            comment_count = 0
            for content_item in all_content:
                # Comment on about 5-15% of views
                num_comments = random.randint(0, max(1, int(content_item["view_count"] * 0.15)))
                for _ in range(num_comments):
                    # Use a random agent as commenter
                    commenter = random.choice(agents)
                    
                    # Generate a simple comment
                    comment_text = random.choice([
                        "Interesting perspective!",
                        "I hadn't thought about it that way before.",
                        "This makes me think differently about the topic.",
                        "Great insights, thanks for sharing!",
                        "I'd love to hear more about this.",
                        "This connects well with other ideas in this field.",
                        "How does this relate to recent developments?",
                        "The implications of this are fascinating.",
                        "I appreciate the thoughtful analysis.",
                        "This raises important questions for further exploration."
                    ])
                    
                    content_service.create_comment(content_item["id"], commenter.id, {"text": comment_text})
                    comment_count += 1
            
            print(f"Generated {comment_count} comments")
            
        except Exception as e:
            print(f"Error generating interactions: {e}")
            import traceback
            traceback.print_exc()
        
        print("Content generation and interaction simulation complete")
        
    except Exception as e:
        print(f"Error in content generation process: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 