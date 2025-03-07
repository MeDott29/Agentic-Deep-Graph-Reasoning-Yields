"""Common utility functions for the Knowledge Graph Social Network."""

import random
import string
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

def generate_random_string(length: int = 10) -> str:
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def calculate_engagement_rate(views: int, interactions: int) -> float:
    """Calculate engagement rate based on views and interactions."""
    if views == 0:
        return 0.0
    return interactions / views

def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def time_since(dt: datetime) -> str:
    """Return a string representing time since the given datetime."""
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"

def filter_dict(data: Dict[str, Any], keys: List[str]) -> Dict[str, Any]:
    """Filter dictionary to only include specified keys."""
    return {k: v for k, v in data.items() if k in keys}

def paginate(items: List[Any], page: int, page_size: int) -> List[Any]:
    """Paginate a list of items."""
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]

def extract_hashtags(text: str) -> List[str]:
    """Extract hashtags from text."""
    words = text.split()
    return [word[1:] for word in words if word.startswith('#')]

def generate_content_summary(content: Dict[str, Any], max_length: int = 100) -> str:
    """Generate a summary of content for display."""
    text = content.get('text_content', '')
    if not text:
        return "No text content"
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length] + '...' 