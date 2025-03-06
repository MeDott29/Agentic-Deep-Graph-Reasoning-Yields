"""
Recommendation Service for the Knowledge Graph Social Network System
"""
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime
import uuid
import random

from models.recommendation import (
    RecommendationScore, ContentRecommendation, 
    RecommendationRequest, RecommendationResponse
)
from services.knowledge_graph import KnowledgeGraphService
from services.ai_content import AIContentGenerationService

class RecommendationService:
    """Service for generating content recommendations"""
    
    def __init__(self, knowledge_graph_service: KnowledgeGraphService):
        """Initialize the recommendation service"""
        self.kg_service = knowledge_graph_service
        self.ai_content_service = AIContentGenerationService(knowledge_graph_service)
    
    def get_recommendations(self, request: RecommendationRequest) -> RecommendationResponse:
        """Get content recommendations for a user"""
        user_id = request.user_id
        count = request.count
        include_ai_content = request.include_ai_content
        ai_content_ratio = request.ai_content_ratio
        
        # Calculate how many AI-generated content items to include
        ai_content_count = 0
        if include_ai_content:
            ai_content_count = int(count * ai_content_ratio)
            regular_content_count = count - ai_content_count
        else:
            regular_content_count = count
        
        # Get user feed from knowledge graph for regular content
        feed_items = self.kg_service.get_user_feed(
            user_id=user_id,
            limit=regular_content_count
        )
        
        # Apply filters
        filtered_items = self._apply_filters(feed_items, request)
        
        # Format regular content recommendations
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
                'is_ai_generated': properties.get('is_ai_generated', False),
                'ai_agent_id': properties.get('ai_agent_id'),
            }
            
            # Extract recommendation details
            recommendation = ContentRecommendation(
                content_id=item.get('content_id'),
                score=item.get('score', 0.0),
                reasons=item.get('reasons', []),
                content=content_details
            )
            
            recommendations.append(recommendation)
        
        # Add AI-generated content if requested
        if include_ai_content and ai_content_count > 0:
            ai_content_models = self.ai_content_service.generate_ai_content(
                user_id=user_id,
                count=ai_content_count
            )
            
            # Convert AI content models to recommendations
            for content_model in ai_content_models:
                # Create a recommendation object
                ai_recommendation = ContentRecommendation(
                    content_id=str(uuid.uuid4()),  # Generate a temporary ID
                    score=random.uniform(0.7, 1.0),  # Give AI content a high score
                    reasons=["AI-generated content based on your preferences"],
                    content={
                        'id': str(uuid.uuid4()),
                        'title': content_model.title,
                        'description': content_model.description,
                        'user_id': content_model.user_id,
                        'duration': 30.0,  # Default duration
                        'hashtags': content_model.hashtags,
                        'view_count': 0,
                        'like_count': 0,
                        'comment_count': 0,
                        'share_count': 0,
                        'is_ai_generated': True,
                        'ai_agent_id': content_model.ai_agent_id,
                    }
                )
                
                recommendations.append(ai_recommendation)
            
            # Shuffle recommendations to mix AI and regular content
            random.shuffle(recommendations)
        
        # Create response
        response = RecommendationResponse(
            user_id=user_id,
            count=len(recommendations),
            recommendations=recommendations
        )
        
        return response
    
    def _apply_filters(self, feed_items: List[Dict[str, Any]], request: RecommendationRequest) -> List[Dict[str, Any]]:
        """Apply filters to feed items based on request parameters"""
        filtered_items = feed_items
        
        # Filter by content type
        if request.content_types:
            filtered_items = [
                item for item in filtered_items
                if item.get('node_data', {}).get('properties', {}).get('content_type') in request.content_types
            ]
        
        # Filter by hashtags
        if request.hashtags:
            filtered_items = [
                item for item in filtered_items
                if any(tag in item.get('node_data', {}).get('properties', {}).get('hashtags', []) for tag in request.hashtags)
            ]
        
        # Filter by minimum duration
        if request.min_duration is not None:
            filtered_items = [
                item for item in filtered_items
                if item.get('node_data', {}).get('properties', {}).get('duration', 0) >= request.min_duration
            ]
        
        # Filter by maximum duration
        if request.max_duration is not None:
            filtered_items = [
                item for item in filtered_items
                if item.get('node_data', {}).get('properties', {}).get('duration', 0) <= request.max_duration
            ]
        
        # Filter by exclude seen
        if request.exclude_seen:
            # This would require tracking user views in a real implementation
            pass
        
        # Filter by exclude user IDs
        if request.exclude_user_ids:
            filtered_items = [
                item for item in filtered_items
                if item.get('node_data', {}).get('properties', {}).get('user_id') not in request.exclude_user_ids
            ]
        
        # Filter by include AI content
        if not request.include_ai_content:
            filtered_items = [
                item for item in filtered_items
                if not item.get('node_data', {}).get('properties', {}).get('is_ai_generated', False)
            ]
        
        return filtered_items
    
    def record_interaction(self, user_id: str, content_id: str, interaction_type: str, data: Dict[str, Any] = None) -> bool:
        """Record user interaction with content"""
        try:
            # Get content details
            content_node = self.kg_service.get_node(content_id)
            
            if not content_node:
                return False
            
            # Check if content is AI-generated
            is_ai_generated = content_node.get('properties', {}).get('is_ai_generated', False)
            ai_agent_id = content_node.get('properties', {}).get('ai_agent_id')
            
            # Record interaction in knowledge graph
            if interaction_type == "view":
                # Increment view count
                self.kg_service.add_node_property(
                    node_id=content_id,
                    node_type="CONTENT",
                    property_name="view_count",
                    property_value=content_node.get('properties', {}).get('view_count', 0) + 1
                )
                
                # Add view edge
                from models.social import View
                view_edge = View(
                    source_id=user_id,
                    target_id=content_id,
                    timestamp=datetime.now(),
                    properties=data or {}
                )
                self.kg_service.add_edge(view_edge)
                
            elif interaction_type == "like":
                # Increment like count
                self.kg_service.add_node_property(
                    node_id=content_id,
                    node_type="CONTENT",
                    property_name="like_count",
                    property_value=content_node.get('properties', {}).get('like_count', 0) + 1
                )
                
                # Add like edge
                from models.social import Like
                like_edge = Like(
                    source_id=user_id,
                    target_id=content_id,
                    timestamp=datetime.now(),
                    properties=data or {}
                )
                self.kg_service.add_edge(like_edge)
                
            elif interaction_type == "share":
                # Increment share count
                self.kg_service.add_node_property(
                    node_id=content_id,
                    node_type="CONTENT",
                    property_name="share_count",
                    property_value=content_node.get('properties', {}).get('share_count', 0) + 1
                )
                
                # Add share edge
                from models.social import Share
                share_edge = Share(
                    source_id=user_id,
                    target_id=content_id,
                    timestamp=datetime.now(),
                    properties=data or {}
                )
                self.kg_service.add_edge(share_edge)
                
            elif interaction_type == "comment":
                # Increment comment count
                self.kg_service.add_node_property(
                    node_id=content_id,
                    node_type="CONTENT",
                    property_name="comment_count",
                    property_value=content_node.get('properties', {}).get('comment_count', 0) + 1
                )
                
                # Add comment edge
                from models.social import CommentEdge
                comment_edge = CommentEdge(
                    source_id=user_id,
                    target_id=content_id,
                    timestamp=datetime.now(),
                    properties=data or {}
                )
                self.kg_service.add_edge(comment_edge)
            
            # If content is AI-generated, record interaction in AI content service
            if is_ai_generated and ai_agent_id:
                self.ai_content_service.record_user_interaction(
                    user_id=user_id,
                    content_id=content_id,
                    agent_id=ai_agent_id,
                    interaction_type=interaction_type
                )
            
            # Update user interests based on interaction
            self.update_user_interests(user_id)
            
            return True
            
        except Exception as e:
            print(f"Error recording interaction: {e}")
            return False
    
    def update_user_interests(self, user_id: str) -> bool:
        """Update user interests based on interactions"""
        try:
            # Get user's recent interactions
            interactions = []
            
            # Get view interactions
            view_edges = self.kg_service.get_edges(
                source_id=user_id,
                edge_type="VIEW"
            )
            for edge in view_edges:
                interactions.append({
                    "content_id": edge.get("target_id"),
                    "type": "view",
                    "timestamp": edge.get("properties", {}).get("timestamp"),
                    "weight": 1.0
                })
            
            # Get like interactions
            like_edges = self.kg_service.get_edges(
                source_id=user_id,
                edge_type="LIKE"
            )
            for edge in like_edges:
                interactions.append({
                    "content_id": edge.get("target_id"),
                    "type": "like",
                    "timestamp": edge.get("properties", {}).get("timestamp"),
                    "weight": 2.0
                })
            
            # Get share interactions
            share_edges = self.kg_service.get_edges(
                source_id=user_id,
                edge_type="SHARE"
            )
            for edge in share_edges:
                interactions.append({
                    "content_id": edge.get("target_id"),
                    "type": "share",
                    "timestamp": edge.get("properties", {}).get("timestamp"),
                    "weight": 3.0
                })
            
            # Get comment interactions
            comment_edges = self.kg_service.get_edges(
                source_id=user_id,
                edge_type="COMMENT"
            )
            for edge in comment_edges:
                interactions.append({
                    "content_id": edge.get("target_id"),
                    "type": "comment",
                    "timestamp": edge.get("properties", {}).get("timestamp"),
                    "weight": 2.5
                })
            
            # Sort interactions by timestamp (most recent first)
            interactions.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Limit to most recent 100 interactions
            interactions = interactions[:100]
            
            # Extract content details for each interaction
            content_details = []
            for interaction in interactions:
                content_id = interaction.get("content_id")
                content_node = self.kg_service.get_node(content_id)
                
                if content_node:
                    content_details.append({
                        "content_id": content_id,
                        "properties": content_node.get("properties", {}),
                        "weight": interaction.get("weight", 1.0)
                    })
            
            # Extract hashtags and calculate weights
            hashtag_weights = {}
            for content in content_details:
                hashtags = content.get("properties", {}).get("hashtags", [])
                weight = content.get("weight", 1.0)
                
                for hashtag in hashtags:
                    if hashtag in hashtag_weights:
                        hashtag_weights[hashtag] += weight
                    else:
                        hashtag_weights[hashtag] = weight
            
            # Sort hashtags by weight
            sorted_hashtags = sorted(hashtag_weights.items(), key=lambda x: x[1], reverse=True)
            
            # Get top 10 hashtags
            top_hashtags = [hashtag for hashtag, _ in sorted_hashtags[:10]]
            
            # Update user interests in knowledge graph
            user_node = self.kg_service.get_node(user_id)
            if user_node:
                self.kg_service.add_node_property(
                    node_id=user_id,
                    node_type="USER",
                    property_name="interests",
                    property_value=top_hashtags
                )
            
            # Update AI content preferences
            ai_preferences = self.ai_content_service.get_user_preferences(user_id)
            ai_preferences["interests"] = top_hashtags
            self.ai_content_service.update_user_preferences(user_id, {"interests": top_hashtags})
            
            return True
            
        except Exception as e:
            print(f"Error updating user interests: {e}")
            return False
    
    def find_similar_content(self, content_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Find content similar to the given content"""
        # Get content details
        content_node = self.kg_service.get_node(content_id)
        
        if not content_node:
            return []
        
        # Extract content properties
        properties = content_node.get("properties", {})
        hashtags = properties.get("hashtags", [])
        user_id = properties.get("user_id")
        
        # Find content with similar hashtags
        similar_content = []
        
        # Query graph for content with similar hashtags
        for hashtag in hashtags:
            hashtag_node_id = f"hashtag:{hashtag}"
            
            # Get content connected to this hashtag
            content_edges = self.kg_service.get_edges(
                source_id=None,
                target_id=hashtag_node_id,
                edge_type="HAS_TAG"
            )
            
            for edge in content_edges:
                content_id = edge.get("source_id")
                
                # Skip the original content
                if content_id == content_node.get("id"):
                    continue
                
                # Get content details
                similar_content_node = self.kg_service.get_node(content_id)
                
                if similar_content_node:
                    # Calculate similarity score based on hashtag overlap
                    similar_hashtags = similar_content_node.get("properties", {}).get("hashtags", [])
                    common_hashtags = set(hashtags).intersection(set(similar_hashtags))
                    similarity_score = len(common_hashtags) / max(len(hashtags), len(similar_hashtags))
                    
                    # Add to results
                    similar_content.append({
                        "content_id": content_id,
                        "score": similarity_score,
                        "common_hashtags": list(common_hashtags),
                        "node_data": similar_content_node
                    })
        
        # Remove duplicates
        unique_content = {}
        for content in similar_content:
            content_id = content.get("content_id")
            if content_id not in unique_content or content.get("score") > unique_content[content_id].get("score"):
                unique_content[content_id] = content
        
        # Sort by similarity score
        sorted_content = sorted(unique_content.values(), key=lambda x: x.get("score"), reverse=True)
        
        # Limit results
        return sorted_content[:limit] 