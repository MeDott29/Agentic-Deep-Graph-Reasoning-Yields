import os
import json
from typing import List, Optional, Dict, Any, Union
from datetime import datetime

from models.content import Content, ContentCreate, ContentUpdate, ContentInDB, Comment, CommentCreate, CommentInDB

class ContentService:
    """Service for content management and interaction."""
    
    def __init__(self):
        """Initialize content service."""
        self.db_path = os.getenv("CONTENT_DB_PATH", "./data/content.json")
        self._ensure_db_exists()
        
    def _ensure_db_exists(self):
        """Ensure the content database file exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({"content": [], "comments": []}, f)
    
    def _load_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load content data from the database."""
        with open(self.db_path, "r") as f:
            return json.load(f)
    
    def _save_data(self, data: Dict[str, List[Dict[str, Any]]]):
        """Save content data to the database."""
        with open(self.db_path, "w") as f:
            json.dump(data, f, default=str)
    
    def get_content(self, content_id: str) -> Optional[ContentInDB]:
        """Get content by ID."""
        data = self._load_data()
        for content_data in data["content"]:
            if content_data.get("id") == content_id:
                return ContentInDB(**content_data)
        return None
    
    def create_content(self, creator_id: str, content_create: ContentCreate) -> Content:
        """Create new content."""
        data = self._load_data()
        
        # Create content with ContentInDB model
        content_data = content_create.dict()
        content_data["creator_id"] = creator_id
        content = ContentInDB(**content_data)
        
        # Convert to dict and add to database
        content_dict = content.dict()
        data["content"].append(content_dict)
        self._save_data(data)
        
        # Return Content model
        return Content(
            id=content.id,
            title=content.title,
            text_content=content.text_content,
            media_urls=content.media_urls,
            hashtags=content.hashtags,
            references=content.references,
            type=content.type,
            creator_id=content.creator_id,
            view_count=content.view_count,
            like_count=content.like_count,
            share_count=content.share_count,
            comment_count=content.comment_count,
            avg_view_duration=content.avg_view_duration,
            created_at=content.created_at
        )
    
    def update_content(self, content_id: str, content_update: ContentUpdate) -> Content:
        """Update content."""
        data = self._load_data()
        
        for i, content_data in enumerate(data["content"]):
            if content_data.get("id") == content_id:
                # Update only provided fields
                update_data = content_update.dict(exclude_unset=True)
                for key, value in update_data.items():
                    content_data[key] = value
                
                # Update timestamp
                content_data["updated_at"] = datetime.now()
                
                # Save to database
                data["content"][i] = content_data
                self._save_data(data)
                
                # Return updated content
                content = ContentInDB(**content_data)
                return Content(
                    id=content.id,
                    title=content.title,
                    text_content=content.text_content,
                    media_urls=content.media_urls,
                    hashtags=content.hashtags,
                    references=content.references,
                    type=content.type,
                    creator_id=content.creator_id,
                    view_count=content.view_count,
                    like_count=content.like_count,
                    share_count=content.share_count,
                    comment_count=content.comment_count,
                    avg_view_duration=content.avg_view_duration,
                    created_at=content.created_at
                )
        
        return None
    
    def delete_content(self, content_id: str) -> bool:
        """Delete content."""
        data = self._load_data()
        
        for i, content_data in enumerate(data["content"]):
            if content_data.get("id") == content_id:
                # Remove content
                data["content"].pop(i)
                
                # Remove associated comments
                data["comments"] = [c for c in data["comments"] if c.get("content_id") != content_id]
                
                # Save to database
                self._save_data(data)
                return True
        
        return False
    
    def record_view(self, content_id: str, user_id: Optional[str], view_duration: float) -> bool:
        """Record content view and view duration."""
        content = self.get_content(content_id)
        if not content:
            return False
        
        data = self._load_data()
        
        for i, content_data in enumerate(data["content"]):
            if content_data.get("id") == content_id:
                # Update view count and duration
                content_data["view_count"] = content_data.get("view_count", 0) + 1
                content_data["total_view_duration"] = content_data.get("total_view_duration", 0) + view_duration
                
                # Calculate average view duration
                if content_data["view_count"] > 0:
                    content_data["avg_view_duration"] = content_data["total_view_duration"] / content_data["view_count"]
                
                # Save to database
                data["content"][i] = content_data
                self._save_data(data)
                
                # TODO: Add to knowledge graph
                
                return True
        
        return False
    
    def like_content(self, content_id: str, user_id: str) -> Content:
        """Like content."""
        content = self.get_content(content_id)
        if not content:
            return None
        
        data = self._load_data()
        
        for i, content_data in enumerate(data["content"]):
            if content_data.get("id") == content_id:
                # Update like count
                content_data["like_count"] = content_data.get("like_count", 0) + 1
                
                # Save to database
                data["content"][i] = content_data
                self._save_data(data)
                
                # TODO: Add to knowledge graph
                
                # Return updated content
                content = ContentInDB(**content_data)
                return Content(
                    id=content.id,
                    title=content.title,
                    text_content=content.text_content,
                    media_urls=content.media_urls,
                    hashtags=content.hashtags,
                    references=content.references,
                    type=content.type,
                    creator_id=content.creator_id,
                    view_count=content.view_count,
                    like_count=content.like_count,
                    share_count=content.share_count,
                    comment_count=content.comment_count,
                    avg_view_duration=content.avg_view_duration,
                    created_at=content.created_at
                )
        
        return None
    
    def unlike_content(self, content_id: str, user_id: str) -> Content:
        """Unlike content."""
        content = self.get_content(content_id)
        if not content:
            return None
        
        data = self._load_data()
        
        for i, content_data in enumerate(data["content"]):
            if content_data.get("id") == content_id:
                # Update like count (ensure it doesn't go below 0)
                content_data["like_count"] = max(0, content_data.get("like_count", 0) - 1)
                
                # Save to database
                data["content"][i] = content_data
                self._save_data(data)
                
                # TODO: Update knowledge graph
                
                # Return updated content
                content = ContentInDB(**content_data)
                return Content(
                    id=content.id,
                    title=content.title,
                    text_content=content.text_content,
                    media_urls=content.media_urls,
                    hashtags=content.hashtags,
                    references=content.references,
                    type=content.type,
                    creator_id=content.creator_id,
                    view_count=content.view_count,
                    like_count=content.like_count,
                    share_count=content.share_count,
                    comment_count=content.comment_count,
                    avg_view_duration=content.avg_view_duration,
                    created_at=content.created_at
                )
        
        return None
    
    def share_content(self, content_id: str, user_id: str) -> Content:
        """Share content."""
        content = self.get_content(content_id)
        if not content:
            return None
        
        data = self._load_data()
        
        for i, content_data in enumerate(data["content"]):
            if content_data.get("id") == content_id:
                # Update share count
                content_data["share_count"] = content_data.get("share_count", 0) + 1
                
                # Save to database
                data["content"][i] = content_data
                self._save_data(data)
                
                # TODO: Add to knowledge graph
                
                # Return updated content
                content = ContentInDB(**content_data)
                return Content(
                    id=content.id,
                    title=content.title,
                    text_content=content.text_content,
                    media_urls=content.media_urls,
                    hashtags=content.hashtags,
                    references=content.references,
                    type=content.type,
                    creator_id=content.creator_id,
                    view_count=content.view_count,
                    like_count=content.like_count,
                    share_count=content.share_count,
                    comment_count=content.comment_count,
                    avg_view_duration=content.avg_view_duration,
                    created_at=content.created_at
                )
        
        return None
    
    def create_comment(self, content_id: str, user_id: str, comment_create: Union[CommentCreate, Dict[str, Any]]) -> Comment:
        """Add comment to content."""
        content = self.get_content(content_id)
        if not content:
            return None
        
        data = self._load_data()
        
        # Create comment with CommentInDB model
        if isinstance(comment_create, dict):
            # Convert dict to CommentCreate
            comment_data = comment_create
        else:
            # Use dict method for Pydantic model
            comment_data = comment_create.dict()
        
        comment_data["content_id"] = content_id
        comment_data["user_id"] = user_id
        comment = CommentInDB(**comment_data)
        
        # Convert to dict and add to database
        comment_dict = comment.dict()
        data["comments"].append(comment_dict)
        
        # Update comment count on content
        for i, content_data in enumerate(data["content"]):
            if content_data.get("id") == content_id:
                content_data["comment_count"] = content_data.get("comment_count", 0) + 1
                data["content"][i] = content_data
                break
        
        self._save_data(data)
        
        # TODO: Add to knowledge graph
        
        # Return Comment model
        return Comment(
            id=comment.id,
            text=comment.text,
            content_id=comment.content_id,
            user_id=comment.user_id,
            like_count=comment.like_count,
            created_at=comment.created_at
        )
    
    def get_content_comments(self, content_id: str, skip: int = 0, limit: int = 100) -> List[Comment]:
        """Get content comments."""
        data = self._load_data()
        
        comments = []
        for comment_data in data["comments"]:
            if comment_data.get("content_id") == content_id:
                comment = CommentInDB(**comment_data)
                comments.append(Comment(
                    id=comment.id,
                    text=comment.text,
                    content_id=comment.content_id,
                    user_id=comment.user_id,
                    like_count=comment.like_count,
                    created_at=comment.created_at
                ))
        
        # Sort by creation time (newest first)
        comments.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return comments[skip:skip+limit]
    
    def search_content(self, query: str, skip: int = 0, limit: int = 20) -> List[Content]:
        """Search for content."""
        data = self._load_data()
        results = []
        
        query = query.lower()
        for content_data in data["content"]:
            title = content_data.get("title", "").lower()
            text_content = content_data.get("text_content", "").lower()
            hashtags = [tag.lower() for tag in content_data.get("hashtags", [])]
            
            if (query in title or query in text_content or 
                any(query in tag for tag in hashtags)):
                content = ContentInDB(**content_data)
                results.append(Content(
                    id=content.id,
                    title=content.title,
                    text_content=content.text_content,
                    media_urls=content.media_urls,
                    hashtags=content.hashtags,
                    references=content.references,
                    type=content.type,
                    creator_id=content.creator_id,
                    view_count=content.view_count,
                    like_count=content.like_count,
                    share_count=content.share_count,
                    comment_count=content.comment_count,
                    avg_view_duration=content.avg_view_duration,
                    created_at=content.created_at
                ))
        
        # Apply pagination
        return results[skip:skip+limit]
    
    def get_content_by_hashtag(self, hashtag: str, skip: int = 0, limit: int = 20) -> List[Content]:
        """Get content by hashtag."""
        data = self._load_data()
        results = []
        
        hashtag = hashtag.lower()
        for content_data in data["content"]:
            content_hashtags = [tag.lower() for tag in content_data.get("hashtags", [])]
            
            if hashtag in content_hashtags:
                content = ContentInDB(**content_data)
                results.append(Content(
                    id=content.id,
                    title=content.title,
                    text_content=content.text_content,
                    media_urls=content.media_urls,
                    hashtags=content.hashtags,
                    references=content.references,
                    type=content.type,
                    creator_id=content.creator_id,
                    view_count=content.view_count,
                    like_count=content.like_count,
                    share_count=content.share_count,
                    comment_count=content.comment_count,
                    avg_view_duration=content.avg_view_duration,
                    created_at=content.created_at
                ))
        
        # Sort by creation time (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return results[skip:skip+limit]
    
    def get_personalized_feed(self, user_id: Optional[str], skip: int = 0, limit: int = 20) -> List[Content]:
        """Get personalized content feed."""
        # In a real implementation, this would use the knowledge graph
        # to provide personalized recommendations
        # For now, we'll just return the most recent content
        data = self._load_data()
        results = []
        
        for content_data in data["content"]:
            content = ContentInDB(**content_data)
            results.append(Content(
                id=content.id,
                title=content.title,
                text_content=content.text_content,
                media_urls=content.media_urls,
                hashtags=content.hashtags,
                references=content.references,
                type=content.type,
                creator_id=content.creator_id,
                view_count=content.view_count,
                like_count=content.like_count,
                share_count=content.share_count,
                comment_count=content.comment_count,
                avg_view_duration=content.avg_view_duration,
                created_at=content.created_at
            ))
        
        # Sort by creation time (newest first)
        results.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return results[skip:skip+limit]
    
    def get_trending_content(self, skip: int = 0, limit: int = 20) -> List[Content]:
        """Get trending content."""
        # In a real implementation, this would use engagement metrics
        # to determine trending content
        # For now, we'll just return content sorted by view count
        data = self._load_data()
        results = []
        
        for content_data in data["content"]:
            content = ContentInDB(**content_data)
            results.append(Content(
                id=content.id,
                title=content.title,
                text_content=content.text_content,
                media_urls=content.media_urls,
                hashtags=content.hashtags,
                references=content.references,
                type=content.type,
                creator_id=content.creator_id,
                view_count=content.view_count,
                like_count=content.like_count,
                share_count=content.share_count,
                comment_count=content.comment_count,
                avg_view_duration=content.avg_view_duration,
                created_at=content.created_at
            ))
        
        # Sort by view count (highest first)
        results.sort(key=lambda x: x.view_count, reverse=True)
        
        # Apply pagination
        return results[skip:skip+limit] 