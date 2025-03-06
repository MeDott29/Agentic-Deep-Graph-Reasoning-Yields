"""
Analytics API endpoints for the Knowledge Graph Social Network System
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models.user import User
from services.knowledge_graph import KnowledgeGraphService
from services.user import UserService
from services.content import ContentService
from api.users import get_current_user

# Create router
router = APIRouter()

# Create services
kg_service = KnowledgeGraphService()
user_service = UserService(kg_service)
content_service = ContentService(kg_service)

@router.get("/content/{content_id}/metrics")
async def get_content_metrics(
    content_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get detailed metrics for a specific content item"""
    # Verify content exists
    content = content_service.get_content(content_id)
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Verify user has permission (content owner or admin)
    if content.user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view these metrics"
        )
    
    # Get basic metrics
    metrics = {
        "views": content.view_count,
        "likes": content.like_count,
        "comments": content.comment_count,
        "shares": content.share_count,
        "engagement_rate": calculate_engagement_rate(content),
        "average_view_duration": get_average_view_duration(content_id),
        "completion_rate": get_completion_rate(content_id),
    }
    
    # Get demographic data
    demographics = get_content_demographics(content_id)
    
    # Get time-based metrics
    time_metrics = get_time_based_metrics(content_id)
    
    # Get referral sources
    referrals = get_referral_sources(content_id)
    
    return {
        "content_id": content_id,
        "title": content.title,
        "created_at": content.created_at.isoformat(),
        "metrics": metrics,
        "demographics": demographics,
        "time_metrics": time_metrics,
        "referrals": referrals
    }

@router.get("/user/{user_id}/metrics")
async def get_user_metrics(
    user_id: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get detailed metrics for a user's content and profile"""
    # If no user_id provided, use current user
    if not user_id:
        user_id = current_user.id
    
    # Verify user exists
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Verify permission (own profile or admin)
    if user_id != current_user.id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view these metrics"
        )
    
    # Get user's content
    user_content = content_service.get_user_content(user_id)
    
    # Calculate aggregate metrics
    total_views = sum(content.view_count for content in user_content)
    total_likes = sum(content.like_count for content in user_content)
    total_comments = sum(content.comment_count for content in user_content)
    total_shares = sum(content.share_count for content in user_content)
    
    # Get follower metrics
    followers = user_service.get_followers(user_id)
    following = user_service.get_following(user_id)
    
    # Calculate follower growth
    follower_growth = calculate_follower_growth(user_id)
    
    # Get content performance over time
    content_performance = get_content_performance_over_time(user_id)
    
    # Get audience demographics
    audience_demographics = get_audience_demographics(user_id)
    
    return {
        "user_id": user_id,
        "username": user.username,
        "created_at": user.created_at.isoformat(),
        "content_count": len(user_content),
        "aggregate_metrics": {
            "total_views": total_views,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "average_engagement_rate": calculate_average_engagement_rate(user_content)
        },
        "follower_metrics": {
            "follower_count": len(followers),
            "following_count": len(following),
            "follower_growth": follower_growth
        },
        "content_performance": content_performance,
        "audience_demographics": audience_demographics
    }

@router.get("/trending/topics")
async def get_trending_topics(
    time_period: str = Query("day", enum=["day", "week", "month"]),
    limit: int = 10,
    current_user: User = Depends(get_current_user)
):
    """Get trending topics based on hashtag usage and engagement"""
    # Calculate time range
    now = datetime.now()
    if time_period == "day":
        start_time = now - timedelta(days=1)
    elif time_period == "week":
        start_time = now - timedelta(weeks=1)
    else:  # month
        start_time = now - timedelta(days=30)
    
    # Get trending hashtags with engagement metrics
    trending_hashtags = content_service.get_trending_hashtags(
        limit=limit,
        start_time=start_time
    )
    
    # Format response
    topics = []
    for hashtag in trending_hashtags:
        topics.append({
            "hashtag": hashtag["hashtag"],
            "content_count": hashtag["content_count"],
            "total_views": hashtag["total_views"],
            "total_likes": hashtag["total_likes"],
            "engagement_rate": hashtag["engagement_rate"],
            "growth_rate": hashtag.get("growth_rate", 0)
        })
    
    return {"trending_topics": topics, "time_period": time_period}

@router.get("/dashboard")
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user)
):
    """Get a comprehensive analytics dashboard for the current user"""
    # Get user metrics
    user_metrics = await get_user_metrics(current_user.id, current_user)
    
    # Get top performing content
    user_content = content_service.get_user_content(current_user.id)
    top_content = sorted(
        user_content,
        key=lambda x: (x.view_count + x.like_count * 2 + x.comment_count * 3 + x.share_count * 4),
        reverse=True
    )[:5]
    
    top_content_metrics = []
    for content in top_content:
        metrics = {
            "content_id": content.id,
            "title": content.title,
            "views": content.view_count,
            "likes": content.like_count,
            "comments": content.comment_count,
            "shares": content.share_count,
            "engagement_rate": calculate_engagement_rate(content)
        }
        top_content_metrics.append(metrics)
    
    # Get audience growth
    audience_growth = get_audience_growth(current_user.id)
    
    # Get content performance by type
    performance_by_type = get_performance_by_content_type(current_user.id)
    
    # Get optimal posting times
    optimal_posting_times = get_optimal_posting_times(current_user.id)
    
    return {
        "user_metrics": user_metrics,
        "top_content": top_content_metrics,
        "audience_growth": audience_growth,
        "performance_by_type": performance_by_type,
        "optimal_posting_times": optimal_posting_times
    }

# Helper functions for analytics calculations

def calculate_engagement_rate(content):
    """Calculate engagement rate for a content item"""
    if content.view_count == 0:
        return 0
    
    engagement_actions = content.like_count + content.comment_count + content.share_count
    return round((engagement_actions / content.view_count) * 100, 2)

def calculate_average_engagement_rate(content_list):
    """Calculate average engagement rate across multiple content items"""
    if not content_list:
        return 0
    
    total_engagement_rate = sum(calculate_engagement_rate(content) for content in content_list)
    return round(total_engagement_rate / len(content_list), 2)

def get_average_view_duration(content_id):
    """Get average view duration for a content item"""
    # In a real implementation, this would query a database of view events
    # For this prototype, return a mock value
    return {
        "seconds": 15.7,
        "percentage": 78.5  # Percentage of total content length
    }

def get_completion_rate(content_id):
    """Get completion rate for a content item"""
    # In a real implementation, this would query a database of view events
    # For this prototype, return a mock value
    return 68.3  # Percentage of viewers who watched to the end

def get_content_demographics(content_id):
    """Get demographic data for content viewers"""
    # In a real implementation, this would query user demographics from a database
    # For this prototype, return mock data
    return {
        "age_groups": {
            "13-17": 12,
            "18-24": 45,
            "25-34": 28,
            "35-44": 10,
            "45+": 5
        },
        "genders": {
            "male": 48,
            "female": 51,
            "other": 1
        },
        "locations": {
            "United States": 35,
            "India": 15,
            "Brazil": 12,
            "United Kingdom": 8,
            "Other": 30
        }
    }

def get_time_based_metrics(content_id):
    """Get time-based metrics for a content item"""
    # In a real implementation, this would query a time-series database
    # For this prototype, return mock data
    return {
        "views_by_hour": [
            {"hour": 0, "views": 120},
            {"hour": 1, "views": 85},
            # ... more hours
            {"hour": 23, "views": 150}
        ],
        "engagement_by_day": [
            {"day": "2023-06-01", "views": 1200, "likes": 350, "comments": 45},
            {"day": "2023-06-02", "views": 1500, "likes": 420, "comments": 60},
            # ... more days
        ]
    }

def get_referral_sources(content_id):
    """Get referral sources for content views"""
    # In a real implementation, this would query referral data
    # For this prototype, return mock data
    return {
        "for_you_page": 65,
        "profile": 15,
        "search": 10,
        "hashtags": 8,
        "shares": 2
    }

def calculate_follower_growth(user_id):
    """Calculate follower growth over time"""
    # In a real implementation, this would query historical follower data
    # For this prototype, return mock data
    return {
        "daily": [
            {"date": "2023-06-01", "followers": 1200},
            {"date": "2023-06-02", "followers": 1250},
            # ... more days
        ],
        "growth_rate": 4.2  # Percentage growth in the last 30 days
    }

def get_content_performance_over_time(user_id):
    """Get content performance metrics over time"""
    # In a real implementation, this would query historical content data
    # For this prototype, return mock data
    return {
        "views_by_day": [
            {"date": "2023-06-01", "views": 5200},
            {"date": "2023-06-02", "views": 6100},
            # ... more days
        ],
        "engagement_by_day": [
            {"date": "2023-06-01", "engagement_rate": 8.5},
            {"date": "2023-06-02", "engagement_rate": 9.2},
            # ... more days
        ]
    }

def get_audience_demographics(user_id):
    """Get demographic data for a user's audience"""
    # In a real implementation, this would query follower demographics
    # For this prototype, return mock data
    return {
        "age_groups": {
            "13-17": 15,
            "18-24": 40,
            "25-34": 30,
            "35-44": 10,
            "45+": 5
        },
        "genders": {
            "male": 45,
            "female": 53,
            "other": 2
        },
        "locations": {
            "United States": 30,
            "India": 18,
            "Brazil": 15,
            "United Kingdom": 7,
            "Other": 30
        },
        "interests": [
            {"category": "Technology", "percentage": 45},
            {"category": "Entertainment", "percentage": 35},
            {"category": "Fashion", "percentage": 25},
            {"category": "Sports", "percentage": 20},
            {"category": "Food", "percentage": 15}
        ]
    }

def get_audience_growth(user_id):
    """Get audience growth metrics"""
    # In a real implementation, this would query historical audience data
    # For this prototype, return mock data
    return {
        "followers_growth": [
            {"date": "2023-05-01", "followers": 1000},
            {"date": "2023-05-15", "followers": 1200},
            {"date": "2023-06-01", "followers": 1500},
            {"date": "2023-06-15", "followers": 1800}
        ],
        "engagement_growth": [
            {"date": "2023-05-01", "engagement_rate": 7.5},
            {"date": "2023-05-15", "engagement_rate": 8.0},
            {"date": "2023-06-01", "engagement_rate": 8.5},
            {"date": "2023-06-15", "engagement_rate": 9.0}
        ]
    }

def get_performance_by_content_type(user_id):
    """Get performance metrics by content type/category"""
    # In a real implementation, this would analyze content and performance data
    # For this prototype, return mock data
    return [
        {
            "category": "Tutorials",
            "content_count": 15,
            "avg_views": 2500,
            "avg_engagement": 9.5
        },
        {
            "category": "Entertainment",
            "content_count": 10,
            "avg_views": 3200,
            "avg_engagement": 10.2
        },
        {
            "category": "Educational",
            "content_count": 8,
            "avg_views": 1800,
            "avg_engagement": 7.8
        }
    ]

def get_optimal_posting_times(user_id):
    """Get optimal posting times based on audience activity"""
    # In a real implementation, this would analyze audience activity patterns
    # For this prototype, return mock data
    return {
        "days_of_week": [
            {"day": "Monday", "score": 75},
            {"day": "Tuesday", "score": 80},
            {"day": "Wednesday", "score": 85},
            {"day": "Thursday", "score": 90},
            {"day": "Friday", "score": 95},
            {"day": "Saturday", "score": 100},
            {"day": "Sunday", "score": 85}
        ],
        "hours_of_day": [
            {"hour": 8, "score": 60},
            {"hour": 12, "score": 75},
            {"hour": 16, "score": 85},
            {"hour": 20, "score": 100}
        ],
        "best_times": [
            {"day": "Saturday", "hour": 20, "score": 100},
            {"day": "Friday", "hour": 20, "score": 95},
            {"day": "Thursday", "hour": 20, "score": 90}
        ]
    } 