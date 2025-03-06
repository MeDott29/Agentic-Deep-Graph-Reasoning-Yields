"""
Social API endpoints for the Knowledge Graph Social Network System
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional, Dict, Any

from src.models.user import User
from src.models.content import Content
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.user import UserService
from src.services.content import ContentService
from src.services.recommendation import RecommendationService
from src.api.users import get_current_user

# Create router
router = APIRouter()

# Create services
kg_service = KnowledgeGraphService()
user_service = UserService(kg_service)
content_service = ContentService(kg_service)

@router.get("/feed")
async def get_social_feed(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get a feed of content from users the current user follows"""
    # Get users the current user follows
    following = user_service.get_following(current_user.id)
    following_ids = [user.id for user in following]
    
    # Get recent content from followed users
    feed_items = []
    for user_id in following_ids:
        user_content = content_service.get_user_content(user_id, limit=5)
        feed_items.extend(user_content)
    
    # Sort by creation date (newest first)
    feed_items.sort(key=lambda x: x.created_at, reverse=True)
    
    # Apply limit
    feed_items = feed_items[:limit]
    
    return {"feed": feed_items}

@router.get("/explore")
async def explore_content(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get a mix of trending and recommended content for exploration"""
    # Get trending content
    trending_content = kg_service.get_trending_content(limit=limit // 2)
    
    # Get recommended content
    recommendation_service = RecommendationService(kg_service)
    
    recommended_content = recommendation_service.get_recommended_content(
        user_id=current_user.id,
        limit=limit // 2,
        exclude_seen=True
    )
    
    # Combine and format results
    explore_items = []
    
    # Add trending content
    for item in trending_content:
        node_data = item.get('node_data', {})
        properties = node_data.get('properties', {})
        
        content_details = {
            'id': item.get('content_id'),
            'title': properties.get('title'),
            'description': properties.get('description'),
            'user_id': properties.get('user_id'),
            'hashtags': properties.get('hashtags', []),
            'view_count': properties.get('view_count', 0),
            'like_count': properties.get('like_count', 0),
            'comment_count': properties.get('comment_count', 0),
            'share_count': properties.get('share_count', 0),
            'source': 'trending',
            'score': item.get('trending_score', 0)
        }
        
        explore_items.append(content_details)
    
    # Add recommended content
    for item in recommended_content:
        node_data = item.get('node_data', {})
        properties = node_data.get('properties', {})
        
        content_details = {
            'id': item.get('content_id'),
            'title': properties.get('title'),
            'description': properties.get('description'),
            'user_id': properties.get('user_id'),
            'hashtags': properties.get('hashtags', []),
            'view_count': properties.get('view_count', 0),
            'like_count': properties.get('like_count', 0),
            'comment_count': properties.get('comment_count', 0),
            'share_count': properties.get('share_count', 0),
            'source': 'recommended',
            'score': item.get('score', 0),
            'reasons': item.get('reasons', [])
        }
        
        explore_items.append(content_details)
    
    # Shuffle items to mix trending and recommended
    import random
    random.shuffle(explore_items)
    
    return {"explore_items": explore_items}

@router.get("/notifications")
async def get_notifications(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get notifications for the current user"""
    # In a real app, you'd have a notifications service
    # For now, we'll generate some mock notifications based on graph data
    
    notifications = []
    
    # Check for new followers
    followers = user_service.get_followers(current_user.id)
    for follower in followers[:5]:  # Limit to 5 recent followers
        notifications.append({
            'type': 'new_follower',
            'user_id': follower.id,
            'username': follower.username,
            'timestamp': follower.updated_at.isoformat()
        })
    
    # Check for likes on user's content
    user_content = content_service.get_user_content(current_user.id)
    for content in user_content:
        # Get likes for this content
        likes_edges = kg_service.get_edges(
            target_id=content.id,
            edge_type='LIKES'
        )
        
        for edge in likes_edges[:3]:  # Limit to 3 recent likes per content
            user_id = edge.get('source_id')
            if user_id != current_user.id:  # Skip self-likes
                user = user_service.get_user(user_id)
                if user:
                    notifications.append({
                        'type': 'like',
                        'user_id': user.id,
                        'username': user.username,
                        'content_id': content.id,
                        'content_title': content.title or 'Your video',
                        'timestamp': edge.get('properties', {}).get('created_at')
                    })
    
    # Sort by timestamp (newest first)
    notifications.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Apply limit
    notifications = notifications[:limit]
    
    return {"notifications": notifications}

@router.get("/activity")
async def get_user_activity(
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get the current user's recent activity"""
    activity = []
    
    # Get user's outgoing edges
    edges = []
    for _, target, edge_data in kg_service.graph.out_edges(current_user.id, data=True):
        edge_type = edge_data.get('edge_type')
        if edge_type in ['LIKES', 'VIEWS', 'COMMENTS', 'SHARES', 'FOLLOWS']:
            created_at = edge_data.get('properties', {}).get('created_at')
            edges.append({
                'target_id': target,
                'edge_type': edge_type,
                'created_at': created_at
            })
    
    # Sort by creation date (newest first)
    edges.sort(key=lambda x: x.get('created_at', ''), reverse=True)
    
    # Format activity items
    for edge in edges[:limit]:
        edge_type = edge.get('edge_type')
        target_id = edge.get('target_id')
        
        if edge_type == 'FOLLOWS':
            # Follow activity
            user = user_service.get_user(target_id)
            if user:
                activity.append({
                    'type': 'follow',
                    'user_id': user.id,
                    'username': user.username,
                    'timestamp': edge.get('created_at')
                })
        else:
            # Content-related activity
            content = content_service.get_content(target_id)
            if content:
                activity_item = {
                    'type': edge_type.lower(),
                    'content_id': content.id,
                    'content_title': content.title or 'A video',
                    'user_id': content.user_id,
                    'timestamp': edge.get('created_at')
                }
                
                # Add additional details for comments
                if edge_type == 'COMMENTS':
                    comment_id = edge_data.get('properties', {}).get('comment_id')
                    if comment_id and comment_id in content_service.comments:
                        comment = content_service.comments[comment_id]
                        activity_item['comment_text'] = comment.text
                
                activity.append(activity_item)
    
    return {"activity": activity}

@router.get("/graph-visualization")
async def get_graph_visualization(
    depth: int = 2,
    current_user: User = Depends(get_current_user)
):
    """Get a visualization of the user's social graph"""
    # Query the graph starting from the current user
    query = {
        'start_node_id': current_user.id,
        'max_depth': depth,
        'limit': 100
    }
    
    graph_data = kg_service.query_graph(query)
    
    # Format for visualization
    nodes = []
    for node in graph_data.get('nodes', []):
        node_type = node.get('node_type')
        properties = node.get('properties', {})
        
        formatted_node = {
            'id': node.get('id'),
            'type': node_type,
            'label': properties.get('username') if node_type == 'USER' else properties.get('title', 'Content')
        }
        
        nodes.append(formatted_node)
    
    edges = []
    for edge in graph_data.get('edges', []):
        formatted_edge = {
            'source': edge.get('source_id'),
            'target': edge.get('target_id'),
            'type': edge.get('edge_type'),
            'weight': edge.get('weight', 1.0)
        }
        
        edges.append(formatted_edge)
    
    return {
        'nodes': nodes,
        'edges': edges
    } 