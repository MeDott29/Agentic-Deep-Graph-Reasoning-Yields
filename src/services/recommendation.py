"""
Recommendation Service for the Knowledge Graph Social Network System
"""
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import uuid

from models.recommendation import (
    RecommendationScore, ContentRecommendation, 
    RecommendationRequest, RecommendationResponse
)
from services.knowledge_graph import KnowledgeGraphService

class RecommendationService:
    """Service for generating content recommendations"""
    
    def __init__(self, knowledge_graph_service: KnowledgeGraphService):
        """Initialize the recommendation service"""
        self.kg_service = knowledge_graph_service
    
    def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """Get content recommendations for a user"""
        user_id = request.user_id
        count = request.count
        
        # Get user feed from knowledge graph
        feed_items = self.kg_service.get_user_feed(
            user_id=user_id,
            limit=count
        )
        
        # Apply filters
        filtered_items = self._apply_filters(feed_items, request)
        
        # Format response
        recommendations = []
        for item in filtered_items:
            node_data = item.get('node_data', {})
            properties = node_data.get('properties', {})
            
            # Extract content details
            content_details = {
                'id': item.get('content_id'),
                'title': properties.get('title'),
                'description': properties.get('description'),
                'user_id': properties.get('user_id'),
                'duration': properties.get('duration'),
                'hashtags': properties.get('hashtags', []),
                'view_count': properties.get('view_count', 0),
                'like_count': properties.get('like_count', 0),
                'comment_count': properties.get('comment_count', 0),
                'share_count': properties.get('share_count', 0),
                'score': item.get('normalized_score', 0),
                'reasons': item.get('reasons', ["Recommended for you"])
            }
            
            recommendations.append(content_details)
        
        # Create response
        response = RecommendationResponse(
            recommendations=recommendations,
            request_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow()
        )
        
        return response
    
    def _apply_filters(self, feed_items: List[Dict[str, Any]], request: RecommendationRequest) -> List[Dict[str, Any]]:
        """Apply filters to feed items based on request parameters"""
        filtered_items = feed_items.copy()
        
        # Filter by categories if specified
        if request.categories:
            filtered_items = [
                item for item in filtered_items
                if any(
                    category in item.get('node_data', {}).get('properties', {}).get('hashtags', [])
                    for category in request.categories
                )
            ]
        
        # Filter by duration if specified
        if request.max_duration:
            filtered_items = [
                item for item in filtered_items
                if item.get('node_data', {}).get('properties', {}).get('duration', 0) <= request.max_duration
            ]
        
        # Include/exclude content from followed users
        if not request.include_following:
            # Get list of users the current user follows
            followed_users = set()
            for _, target, edge_data in self.kg_service.graph.out_edges(request.user_id, data=True):
                if edge_data.get('edge_type') == 'FOLLOWS':
                    followed_users.add(target)
            
            # Filter out content created by followed users
            filtered_items = [
                item for item in filtered_items
                if item.get('node_data', {}).get('properties', {}).get('user_id') not in followed_users
            ]
        
        # Include/exclude trending content
        if not request.include_trending:
            # Filter out items that are primarily trending (not personalized)
            filtered_items = [
                item for item in filtered_items
                if 'score' in item  # Items with 'score' are from personalized recommendations
            ]
        
        return filtered_items
    
    def record_interaction(self, user_id: str, content_id: str, interaction_type: str, data: Dict[str, Any] = None) -> bool:
        """Record a user interaction with content to improve future recommendations"""
        data = data or {}
        
        try:
            if interaction_type == 'view':
                # Create a view edge
                duration = data.get('duration', 0)
                view_edge = self.kg_service.graph.add_edge(
                    user_id,
                    content_id,
                    edge_type='VIEWS',
                    properties={
                        'duration': duration,
                        'created_at': datetime.utcnow().isoformat()
                    }
                )
                
                # Update content view count
                if content_id in self.kg_service.graph.nodes:
                    properties = self.kg_service.graph.nodes[content_id].get('properties', {})
                    view_count = properties.get('view_count', 0)
                    properties['view_count'] = view_count + 1
                    self.kg_service.graph.nodes[content_id]['properties'] = properties
            
            elif interaction_type == 'like':
                # Create a like edge
                like_edge = self.kg_service.graph.add_edge(
                    user_id,
                    content_id,
                    edge_type='LIKES',
                    properties={
                        'created_at': datetime.utcnow().isoformat()
                    }
                )
                
                # Update content like count
                if content_id in self.kg_service.graph.nodes:
                    properties = self.kg_service.graph.nodes[content_id].get('properties', {})
                    like_count = properties.get('like_count', 0)
                    properties['like_count'] = like_count + 1
                    self.kg_service.graph.nodes[content_id]['properties'] = properties
            
            elif interaction_type == 'comment':
                # Create a comment edge
                comment_id = data.get('comment_id')
                if comment_id:
                    comment_edge = self.kg_service.graph.add_edge(
                        user_id,
                        content_id,
                        edge_type='COMMENTS',
                        properties={
                            'comment_id': comment_id,
                            'created_at': datetime.utcnow().isoformat()
                        }
                    )
                    
                    # Update content comment count
                    if content_id in self.kg_service.graph.nodes:
                        properties = self.kg_service.graph.nodes[content_id].get('properties', {})
                        comment_count = properties.get('comment_count', 0)
                        properties['comment_count'] = comment_count + 1
                        self.kg_service.graph.nodes[content_id]['properties'] = properties
            
            elif interaction_type == 'share':
                # Create a share edge
                platform = data.get('platform', 'unknown')
                share_edge = self.kg_service.graph.add_edge(
                    user_id,
                    content_id,
                    edge_type='SHARES',
                    properties={
                        'platform': platform,
                        'created_at': datetime.utcnow().isoformat()
                    }
                )
                
                # Update content share count
                if content_id in self.kg_service.graph.nodes:
                    properties = self.kg_service.graph.nodes[content_id].get('properties', {})
                    share_count = properties.get('share_count', 0)
                    properties['share_count'] = share_count + 1
                    self.kg_service.graph.nodes[content_id]['properties'] = properties
            
            # Save the updated graph
            self.kg_service._save_graph()
            return True
        
        except Exception as e:
            print(f"Error recording interaction: {e}")
            return False
    
    def update_user_interests(self, user_id: str) -> bool:
        """Update user interests based on their interactions"""
        try:
            # Get user's content interactions
            liked_content = []
            viewed_content = []
            
            for _, target, edge_data in self.kg_service.graph.out_edges(user_id, data=True):
                edge_type = edge_data.get('edge_type')
                if edge_type == 'LIKES':
                    liked_content.append(target)
                elif edge_type == 'VIEWS':
                    viewed_content.append(target)
            
            # Get hashtags from liked and viewed content
            hashtag_scores = {}
            
            # Hashtags from liked content (higher weight)
            for content_id in liked_content:
                for _, target, edge_data in self.kg_service.graph.out_edges(content_id, data=True):
                    if edge_data.get('edge_type') == 'HAS_TAG':
                        hashtag_id = target
                        hashtag_scores[hashtag_id] = hashtag_scores.get(hashtag_id, 0) + 2
            
            # Hashtags from viewed content (lower weight)
            for content_id in viewed_content:
                for _, target, edge_data in self.kg_service.graph.out_edges(content_id, data=True):
                    if edge_data.get('edge_type') == 'HAS_TAG':
                        hashtag_id = target
                        hashtag_scores[hashtag_id] = hashtag_scores.get(hashtag_id, 0) + 0.5
            
            # Update user's interest edges
            # First, remove existing interest edges
            edges_to_remove = []
            for _, target, edge_data in self.kg_service.graph.out_edges(user_id, data=True):
                if edge_data.get('edge_type') == 'INTEREST_IN':
                    edges_to_remove.append((user_id, target))
            
            for source, target in edges_to_remove:
                self.kg_service.graph.remove_edge(source, target)
            
            # Add new interest edges
            for hashtag_id, score in hashtag_scores.items():
                # Normalize score to be between 0 and 1
                normalized_score = min(1.0, score / 10.0)
                
                self.kg_service.graph.add_edge(
                    user_id,
                    hashtag_id,
                    edge_type='INTEREST_IN',
                    weight=normalized_score,
                    properties={
                        'score': normalized_score,
                        'created_at': datetime.utcnow().isoformat(),
                        'updated_at': datetime.utcnow().isoformat()
                    }
                )
            
            # Save the updated graph
            self.kg_service._save_graph()
            return True
        
        except Exception as e:
            print(f"Error updating user interests: {e}")
            return False
    
    def find_similar_content(self, content_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find content similar to the given content"""
        if content_id not in self.kg_service.graph.nodes:
            return []
        
        # Get content hashtags
        content_hashtags = set()
        for _, target, edge_data in self.kg_service.graph.out_edges(content_id, data=True):
            if edge_data.get('edge_type') == 'HAS_TAG':
                content_hashtags.add(target)
        
        # Get content creator
        content_creator = None
        for _, target, edge_data in self.kg_service.graph.out_edges(content_id, data=True):
            if edge_data.get('edge_type') == 'CREATED_BY':
                content_creator = target
                break
        
        # Score other content based on similarity
        content_scores = {}
        
        for node_id, node_data in self.kg_service.graph.nodes(data=True):
            # Skip if not content or if it's the same content
            if node_data.get('node_type') != 'CONTENT' or node_id == content_id:
                continue
            
            score = 0
            
            # Check for common hashtags
            node_hashtags = set()
            for _, target, edge_data in self.kg_service.graph.out_edges(node_id, data=True):
                if edge_data.get('edge_type') == 'HAS_TAG':
                    node_hashtags.add(target)
            
            # Score based on common hashtags
            common_hashtags = content_hashtags.intersection(node_hashtags)
            score += len(common_hashtags) * 2
            
            # Bonus if from same creator
            if content_creator:
                for _, target, edge_data in self.kg_service.graph.out_edges(node_id, data=True):
                    if edge_data.get('edge_type') == 'CREATED_BY' and target == content_creator:
                        score += 3
                        break
            
            # Only include if there's some similarity
            if score > 0:
                content_scores[node_id] = score
        
        # Sort by score and return top results
        similar_content = [
            {
                'content_id': c_id,
                'similarity_score': score,
                'node_data': self.kg_service.graph.nodes[c_id]
            }
            for c_id, score in sorted(content_scores.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]
        
        return similar_content 