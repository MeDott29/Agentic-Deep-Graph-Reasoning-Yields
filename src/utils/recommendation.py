"""Recommendation algorithms for the Knowledge Graph Social Network."""

import random
import networkx as nx
from typing import List, Dict, Any, Optional, Tuple, Set

def calculate_content_similarity(content1: Dict[str, Any], content2: Dict[str, Any]) -> float:
    """Calculate similarity between two content items based on hashtags and text."""
    # Calculate hashtag similarity
    hashtags1 = set(content1.get("hashtags", []))
    hashtags2 = set(content2.get("hashtags", []))
    
    if not hashtags1 or not hashtags2:
        hashtag_similarity = 0.0
    else:
        intersection = hashtags1.intersection(hashtags2)
        union = hashtags1.union(hashtags2)
        hashtag_similarity = len(intersection) / len(union) if union else 0.0
    
    # Calculate text similarity (simple word overlap for now)
    text1 = content1.get("text_content", "").lower().split()
    text2 = content2.get("text_content", "").lower().split()
    
    if not text1 or not text2:
        text_similarity = 0.0
    else:
        words1 = set(text1)
        words2 = set(text2)
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        text_similarity = len(intersection) / len(union) if union else 0.0
    
    # Combine similarities (weighted)
    return 0.7 * hashtag_similarity + 0.3 * text_similarity

def find_similar_content(target_content: Dict[str, Any], all_content: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    """Find content similar to the target content."""
    # Calculate similarity scores
    scored_content = [
        (content, calculate_content_similarity(target_content, content))
        for content in all_content
        if content.get("id") != target_content.get("id")  # Exclude the target content itself
    ]
    
    # Sort by similarity score (highest first)
    scored_content.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N similar content
    return [content for content, score in scored_content[:limit]]

def recommend_by_graph_proximity(graph: nx.DiGraph, user_id: str, content_pool: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    """Recommend content based on graph proximity to user's interests."""
    # Find user node
    user_nodes = [
        node for node, attrs in graph.nodes(data=True)
        if attrs.get("type") == "user" and attrs.get("entity_id") == user_id
    ]
    
    if not user_nodes:
        # User not in graph, return random recommendations
        return random.sample(content_pool, min(limit, len(content_pool)))
    
    user_node = user_nodes[0]
    
    # Find content the user has interacted with
    interacted_content = set()
    for _, target, edge_data in graph.out_edges(user_node, data=True):
        if edge_data.get("type") in ["viewed", "liked", "shared", "commented"]:
            target_attrs = graph.nodes[target]
            if target_attrs.get("type") == "content":
                interacted_content.add(target_attrs.get("entity_id"))
    
    # Find topics the user is interested in
    interested_topics = set()
    for content_id in interacted_content:
        content_nodes = [
            node for node, attrs in graph.nodes(data=True)
            if attrs.get("type") == "content" and attrs.get("entity_id") == content_id
        ]
        
        for content_node in content_nodes:
            for _, topic_node, edge_data in graph.out_edges(content_node, data=True):
                if edge_data.get("type") == "related":
                    topic_attrs = graph.nodes[topic_node]
                    if topic_attrs.get("type") in ["topic", "hashtag"]:
                        interested_topics.add(topic_node)
    
    # Score content based on relation to interested topics
    scored_content = []
    for content in content_pool:
        # Skip content the user has already interacted with
        if content.get("id") in interacted_content:
            continue
        
        # Find content node
        content_nodes = [
            node for node, attrs in graph.nodes(data=True)
            if attrs.get("type") == "content" and attrs.get("entity_id") == content.get("id")
        ]
        
        if not content_nodes:
            continue
        
        content_node = content_nodes[0]
        
        # Calculate topic overlap
        content_topics = set()
        for _, topic_node, edge_data in graph.out_edges(content_node, data=True):
            if edge_data.get("type") == "related":
                topic_attrs = graph.nodes[topic_node]
                if topic_attrs.get("type") in ["topic", "hashtag"]:
                    content_topics.add(topic_node)
        
        topic_overlap = len(content_topics.intersection(interested_topics))
        
        # Score based on topic overlap and engagement metrics
        engagement_score = (
            content.get("like_count", 0) + 
            content.get("share_count", 0) * 2 + 
            content.get("comment_count", 0) * 1.5
        ) / max(1, content.get("view_count", 1))
        
        score = topic_overlap * 0.7 + engagement_score * 0.3
        
        scored_content.append((content, score))
    
    # Sort by score (highest first)
    scored_content.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N recommendations
    return [content for content, score in scored_content[:limit]]

def find_bridge_content(graph: nx.DiGraph, content_pool: List[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    """Find content that bridges different topics or communities."""
    # Calculate betweenness centrality for content nodes
    content_nodes = [
        node for node, attrs in graph.nodes(data=True)
        if attrs.get("type") == "content"
    ]
    
    if not content_nodes:
        return random.sample(content_pool, min(limit, len(content_pool)))
    
    # Create subgraph of content nodes and their neighbors
    subgraph_nodes = set(content_nodes)
    for node in content_nodes:
        subgraph_nodes.update(graph.neighbors(node))
    
    subgraph = graph.subgraph(subgraph_nodes)
    
    # Calculate betweenness centrality
    betweenness = nx.betweenness_centrality(subgraph)
    
    # Score content based on betweenness centrality
    scored_content = []
    for content in content_pool:
        content_nodes = [
            node for node, attrs in graph.nodes(data=True)
            if attrs.get("type") == "content" and attrs.get("entity_id") == content.get("id")
        ]
        
        if not content_nodes:
            continue
        
        content_node = content_nodes[0]
        
        if content_node in betweenness:
            score = betweenness[content_node]
            scored_content.append((content, score))
    
    # Sort by score (highest first)
    scored_content.sort(key=lambda x: x[1], reverse=True)
    
    # Return top N bridge content
    return [content for content, score in scored_content[:limit]]

def discover_emerging_topics(graph: nx.DiGraph, time_window_days: int = 7) -> List[Tuple[str, float]]:
    """Discover emerging topics based on recent engagement patterns."""
    # This is a simplified implementation
    # In a real system, this would analyze temporal patterns in the graph
    
    # Count topic occurrences in content
    topic_counts = {}
    for node, attrs in graph.nodes(data=True):
        if attrs.get("type") in ["topic", "hashtag"]:
            entity_id = attrs.get("entity_id")
            if entity_id:
                topic_counts[entity_id] = topic_counts.get(entity_id, 0) + 1
    
    # Sort by count (highest first)
    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Add a random growth rate for demonstration purposes
    # In a real implementation, this would be calculated from temporal data
    emerging_topics = [
        (topic, random.uniform(1.1, 2.0))
        for topic, count in sorted_topics[:20]
    ]
    
    # Sort by growth rate
    emerging_topics.sort(key=lambda x: x[1], reverse=True)
    
    return emerging_topics 