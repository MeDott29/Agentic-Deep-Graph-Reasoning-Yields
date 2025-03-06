"""
Knowledge Graph Service for the Social Network System
"""
import networkx as nx
from typing import Dict, List, Any, Optional, Tuple
import json
import os
from datetime import datetime

from models.base import GraphNode, GraphEdge, GraphQuery
from models.user import UserNode
from models.content import ContentNode, HashtagNode
from models.social import (
    Follow, Like, View, Share, CommentEdge, 
    HasTag, CreatedBy, InterestIn, SimilarTo
)

class KnowledgeGraphService:
    """Service for managing the knowledge graph"""
    
    def __init__(self, graph_path: Optional[str] = None):
        """Initialize the knowledge graph service"""
        self.graph = nx.DiGraph()
        self.graph_path = graph_path or "src/data/knowledge_graph.json"
        self._load_graph()
    
    def _load_graph(self):
        """Load the graph from disk if it exists"""
        if os.path.exists(self.graph_path):
            try:
                with open(self.graph_path, 'r') as f:
                    graph_data = json.load(f)
                
                # Add nodes
                for node_data in graph_data.get('nodes', []):
                    self.graph.add_node(
                        node_data['id'],
                        node_type=node_data['node_type'],
                        properties=node_data['properties']
                    )
                
                # Add edges
                for edge_data in graph_data.get('edges', []):
                    self.graph.add_edge(
                        edge_data['source_id'],
                        edge_data['target_id'],
                        edge_type=edge_data['edge_type'],
                        weight=edge_data['weight'],
                        properties=edge_data['properties']
                    )
                
                print(f"Loaded graph with {len(self.graph.nodes)} nodes and {len(self.graph.edges)} edges")
            except Exception as e:
                print(f"Error loading graph: {e}")
                self.graph = nx.DiGraph()
    
    def _save_graph(self):
        """Save the graph to disk"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.graph_path), exist_ok=True)
        
        # Prepare data for serialization
        nodes = []
        for node_id, node_data in self.graph.nodes(data=True):
            nodes.append({
                'id': node_id,
                'node_type': node_data.get('node_type'),
                'properties': node_data.get('properties', {})
            })
        
        edges = []
        for source, target, edge_data in self.graph.edges(data=True):
            edges.append({
                'source_id': source,
                'target_id': target,
                'edge_type': edge_data.get('edge_type'),
                'weight': edge_data.get('weight', 1.0),
                'properties': edge_data.get('properties', {})
            })
        
        graph_data = {
            'nodes': nodes,
            'edges': edges,
            'last_updated': datetime.utcnow().isoformat()
        }
        
        with open(self.graph_path, 'w') as f:
            json.dump(graph_data, f, indent=2)
    
    def add_node(self, node: GraphNode) -> str:
        """Add a node to the graph"""
        self.graph.add_node(
            node.id,
            node_type=node.node_type,
            properties=node.properties
        )
        self._save_graph()
        return node.id
    
    def add_edge(self, edge: GraphEdge) -> Tuple[str, str]:
        """Add an edge to the graph"""
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            edge_type=edge.edge_type,
            weight=edge.weight,
            properties=edge.properties
        )
        self._save_graph()
        return (edge.source_id, edge.target_id)
    
    def get_node(self, node_id: str) -> Optional[Dict[str, Any]]:
        """Get a node by ID"""
        if node_id in self.graph.nodes:
            node_data = self.graph.nodes[node_id]
            return {
                'id': node_id,
                'node_type': node_data.get('node_type'),
                'properties': node_data.get('properties', {})
            }
        return None
    
    def get_edges(self, source_id: str, target_id: Optional[str] = None, edge_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get edges from a source node, optionally filtered by target and type"""
        edges = []
        
        if target_id:
            # Get specific edge between source and target
            if self.graph.has_edge(source_id, target_id):
                edge_data = self.graph.get_edge_data(source_id, target_id)
                if not edge_type or edge_data.get('edge_type') == edge_type:
                    edges.append({
                        'source_id': source_id,
                        'target_id': target_id,
                        'edge_type': edge_data.get('edge_type'),
                        'weight': edge_data.get('weight', 1.0),
                        'properties': edge_data.get('properties', {})
                    })
        else:
            # Get all outgoing edges from source
            for _, target, edge_data in self.graph.out_edges(source_id, data=True):
                if not edge_type or edge_data.get('edge_type') == edge_type:
                    edges.append({
                        'source_id': source_id,
                        'target_id': target,
                        'edge_type': edge_data.get('edge_type'),
                        'weight': edge_data.get('weight', 1.0),
                        'properties': edge_data.get('properties', {})
                    })
        
        return edges
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the graph"""
        if node_id in self.graph.nodes:
            self.graph.remove_node(node_id)
            self._save_graph()
            return True
        return False
    
    def remove_edge(self, source_id: str, target_id: str, edge_type: Optional[str] = None) -> bool:
        """Remove an edge from the graph"""
        if self.graph.has_edge(source_id, target_id):
            if edge_type:
                edge_data = self.graph.get_edge_data(source_id, target_id)
                if edge_data.get('edge_type') == edge_type:
                    self.graph.remove_edge(source_id, target_id)
                    self._save_graph()
                    return True
            else:
                self.graph.remove_edge(source_id, target_id)
                self._save_graph()
                return True
        return False
    
    def query_graph(self, query: GraphQuery) -> Dict[str, Any]:
        """Query the graph based on the provided parameters"""
        results = {
            'nodes': [],
            'edges': []
        }
        
        # Start with a specific node if provided
        if query.start_node_id:
            start_nodes = [query.start_node_id]
        else:
            # Otherwise, filter nodes by type
            start_nodes = [
                node_id for node_id, node_data in self.graph.nodes(data=True)
                if not query.node_types or node_data.get('node_type') in query.node_types
            ]
        
        # Limit the number of start nodes
        start_nodes = start_nodes[:query.limit]
        
        # For each start node, traverse the graph up to max_depth
        for start_node in start_nodes:
            # BFS traversal
            visited = {start_node}
            queue = [(start_node, 0)]  # (node_id, depth)
            
            while queue and len(results['nodes']) < query.limit:
                current_node, depth = queue.pop(0)
                
                # Add current node to results
                node_data = self.graph.nodes[current_node]
                results['nodes'].append({
                    'id': current_node,
                    'node_type': node_data.get('node_type'),
                    'properties': node_data.get('properties', {})
                })
                
                # If we've reached max depth, don't explore further
                if depth >= query.max_depth:
                    continue
                
                # Explore neighbors
                for _, neighbor, edge_data in self.graph.out_edges(current_node, data=True):
                    edge_type = edge_data.get('edge_type')
                    
                    # Filter by edge type if specified
                    if query.edge_types and edge_type not in query.edge_types:
                        continue
                    
                    # Add edge to results
                    results['edges'].append({
                        'source_id': current_node,
                        'target_id': neighbor,
                        'edge_type': edge_type,
                        'weight': edge_data.get('weight', 1.0),
                        'properties': edge_data.get('properties', {})
                    })
                    
                    # Add neighbor to queue if not visited
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, depth + 1))
        
        return results
    
    def get_similar_users(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find users similar to the given user based on graph structure"""
        if user_id not in self.graph.nodes:
            return []
        
        # Get user's interests, liked content, and followed users
        interests = set()
        liked_content = set()
        followed_users = set()
        
        for _, target, edge_data in self.graph.out_edges(user_id, data=True):
            edge_type = edge_data.get('edge_type')
            if edge_type == 'INTEREST_IN':
                interests.add(target)
            elif edge_type == 'LIKES':
                liked_content.add(target)
            elif edge_type == 'FOLLOWS':
                followed_users.add(target)
        
        # Find users with similar interests, likes, or follows
        user_scores = {}
        
        # Users who like similar content
        for content_id in liked_content:
            for source, _, edge_data in self.graph.in_edges(content_id, data=True):
                if source != user_id and edge_data.get('edge_type') == 'LIKES':
                    user_scores[source] = user_scores.get(source, 0) + 1
        
        # Users with similar interests
        for interest_id in interests:
            for source, _, edge_data in self.graph.in_edges(interest_id, data=True):
                if source != user_id and edge_data.get('edge_type') == 'INTEREST_IN':
                    user_scores[source] = user_scores.get(source, 0) + 2
        
        # Users followed by users the current user follows
        for followed_id in followed_users:
            for _, target, edge_data in self.graph.out_edges(followed_id, data=True):
                if target != user_id and edge_data.get('edge_type') == 'FOLLOWS':
                    user_scores[target] = user_scores.get(target, 0) + 0.5
        
        # Sort users by score and return top results
        similar_users = [
            {
                'user_id': u_id,
                'score': score,
                'node_data': self.graph.nodes[u_id]
            }
            for u_id, score in sorted(user_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]
        
        return similar_users
    
    def get_recommended_content(self, user_id: str, limit: int = 10, exclude_seen: bool = True) -> List[Dict[str, Any]]:
        """Get recommended content for a user based on their interests and social connections"""
        if user_id not in self.graph.nodes:
            return []
        
        # Get content the user has already seen
        seen_content = set()
        if exclude_seen:
            for _, target, edge_data in self.graph.out_edges(user_id, data=True):
                if edge_data.get('edge_type') in ['VIEWS', 'LIKES']:
                    seen_content.add(target)
        
        # Get user's interests and followed users
        interests = set()
        followed_users = set()
        
        for _, target, edge_data in self.graph.out_edges(user_id, data=True):
            edge_type = edge_data.get('edge_type')
            if edge_type == 'INTEREST_IN':
                interests.add(target)
            elif edge_type == 'FOLLOWS':
                followed_users.add(target)
        
        # Score content based on various factors
        content_scores = {}
        
        # Content from followed users
        for followed_id in followed_users:
            for _, target, edge_data in self.graph.out_edges(followed_id, data=True):
                if edge_data.get('edge_type') == 'CREATED_BY':
                    content_id = target
                    if content_id not in seen_content:
                        content_scores[content_id] = content_scores.get(content_id, 0) + 3
        
        # Content with user's interests
        for interest_id in interests:
            for source, _, edge_data in self.graph.in_edges(interest_id, data=True):
                if edge_data.get('edge_type') == 'HAS_TAG' and source not in seen_content:
                    content_scores[source] = content_scores.get(source, 0) + 2
        
        # Content liked by similar users
        similar_users = self.get_similar_users(user_id, limit=20)
        for similar_user in similar_users:
            similar_user_id = similar_user['user_id']
            similarity_score = similar_user['score']
            
            for _, target, edge_data in self.graph.out_edges(similar_user_id, data=True):
                if edge_data.get('edge_type') == 'LIKES' and target not in seen_content:
                    content_scores[target] = content_scores.get(target, 0) + (similarity_score * 0.5)
        
        # Add popularity factor (based on like count)
        for node_id, node_data in self.graph.nodes(data=True):
            if node_data.get('node_type') == 'CONTENT' and node_id not in seen_content:
                properties = node_data.get('properties', {})
                like_count = properties.get('like_count', 0)
                view_count = properties.get('view_count', 0)
                
                # Calculate popularity score (logarithmic to prevent domination by very popular content)
                popularity_score = 0.1 * (1 + (like_count / (view_count + 1)))
                content_scores[node_id] = content_scores.get(node_id, 0) + popularity_score
        
        # Sort content by score and return top results
        recommended_content = [
            {
                'content_id': c_id,
                'score': score,
                'node_data': self.graph.nodes[c_id],
                'reasons': self._get_recommendation_reasons(user_id, c_id)
            }
            for c_id, score in sorted(content_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]
        
        return recommended_content
    
    def _get_recommendation_reasons(self, user_id: str, content_id: str) -> List[str]:
        """Get reasons for recommending this content to the user"""
        reasons = []
        
        # Check if content is from a followed user
        for _, target, edge_data in self.graph.out_edges(content_id, data=True):
            if edge_data.get('edge_type') == 'CREATED_BY':
                creator_id = target
                if self.graph.has_edge(user_id, creator_id) and self.graph.get_edge_data(user_id, creator_id).get('edge_type') == 'FOLLOWS':
                    creator_name = self.graph.nodes[creator_id].get('properties', {}).get('username', 'Someone you follow')
                    reasons.append(f"Created by {creator_name} who you follow")
        
        # Check if content has hashtags the user is interested in
        content_hashtags = set()
        for _, target, edge_data in self.graph.out_edges(content_id, data=True):
            if edge_data.get('edge_type') == 'HAS_TAG':
                content_hashtags.add(target)
        
        user_interests = set()
        for _, target, edge_data in self.graph.out_edges(user_id, data=True):
            if edge_data.get('edge_type') == 'INTEREST_IN':
                user_interests.add(target)
        
        common_interests = content_hashtags.intersection(user_interests)
        if common_interests:
            interest_names = [self.graph.nodes[i].get('properties', {}).get('name', 'a topic') for i in common_interests]
            reasons.append(f"Related to your interests: {', '.join(interest_names[:3])}")
        
        # Check if content is popular
        properties = self.graph.nodes[content_id].get('properties', {})
        like_count = properties.get('like_count', 0)
        if like_count > 100:
            reasons.append(f"Popular with {like_count} likes")
        
        # Default reason if none found
        if not reasons:
            reasons.append("Based on your activity")
        
        return reasons
    
    def get_trending_content(self, limit: int = 10, time_window: int = 24) -> List[Dict[str, Any]]:
        """Get trending content based on recent engagement"""
        # Find content nodes
        content_nodes = [
            node_id for node_id, node_data in self.graph.nodes(data=True)
            if node_data.get('node_type') == 'CONTENT'
        ]
        
        # Calculate trending score based on recent likes, views, comments, shares
        now = datetime.utcnow()
        trending_scores = {}
        
        for content_id in content_nodes:
            # Get engagement edges
            engagement_count = 0
            recency_sum = 0
            
            for source, _, edge_data in self.graph.in_edges(content_id, data=True):
                edge_type = edge_data.get('edge_type')
                if edge_type in ['LIKES', 'VIEWS', 'COMMENTS', 'SHARES']:
                    # Check if the engagement is recent
                    created_at_str = edge_data.get('properties', {}).get('created_at')
                    if created_at_str:
                        try:
                            created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                            hours_ago = (now - created_at).total_seconds() / 3600
                            
                            if hours_ago <= time_window:
                                # Weight different engagement types
                                weight = {
                                    'LIKES': 2.0,
                                    'COMMENTS': 3.0,
                                    'SHARES': 4.0,
                                    'VIEWS': 0.5
                                }.get(edge_type, 1.0)
                                
                                # More recent engagements have higher weight
                                recency_weight = 1.0 - (hours_ago / time_window)
                                
                                engagement_count += 1
                                recency_sum += recency_weight * weight
                        except (ValueError, TypeError):
                            pass
            
            # Calculate trending score
            if engagement_count > 0:
                # Get content creation time
                created_at_str = self.graph.nodes[content_id].get('properties', {}).get('created_at')
                age_penalty = 0
                
                if created_at_str:
                    try:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        days_old = (now - created_at).total_seconds() / 86400
                        # Slight penalty for older content
                        age_penalty = min(0.5, days_old / 30)
                    except (ValueError, TypeError):
                        pass
                
                trending_scores[content_id] = (recency_sum / (1 + age_penalty)) * (1 + (engagement_count / 10))
        
        # Sort content by trending score and return top results
        trending_content = [
            {
                'content_id': c_id,
                'trending_score': score,
                'node_data': self.graph.nodes[c_id]
            }
            for c_id, score in sorted(trending_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]
        
        return trending_content
    
    def get_user_feed(self, user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get a personalized feed for a user, combining recommendations and trending content"""
        # Get recommended content (70% of feed)
        recommended = self.get_recommended_content(user_id, limit=int(limit * 0.7))
        
        # Get trending content (30% of feed)
        trending = self.get_trending_content(limit=limit)
        
        # Remove duplicates (prefer recommended content)
        recommended_ids = {item['content_id'] for item in recommended}
        unique_trending = [item for item in trending if item['content_id'] not in recommended_ids]
        
        # Combine and limit results
        feed = recommended + unique_trending[:limit - len(recommended)]
        
        # Sort by score (normalized)
        for item in feed:
            if 'score' in item:
                item['normalized_score'] = item['score']
            elif 'trending_score' in item:
                item['normalized_score'] = item['trending_score'] * 0.8  # Slight penalty for trending-only content
        
        feed.sort(key=lambda x: x.get('normalized_score', 0), reverse=True)
        
        return feed[:limit] 