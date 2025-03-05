"""
Content Service for the Knowledge Graph Social Network System
"""
from typing import Dict, List, Any, Optional
from datetime import datetime
import os
import json
import uuid
import shutil
from pathlib import Path

from models.content import (
    ContentBase, ContentCreate, ContentUpdate, ContentInDB, 
    Content, ContentNode, HashtagNode, Comment
)
from models.social import HasTag, CreatedBy
from services.knowledge_graph import KnowledgeGraphService

class ContentService:
    """Service for managing content"""
    
    def __init__(self, knowledge_graph_service: KnowledgeGraphService):
        """Initialize the content service"""
        self.kg_service = knowledge_graph_service
        self.content_file = "src/data/content.json"
        self.comments_file = "src/data/comments.json"
        self.content_dir = "src/data/content"
        self.content = self._load_content()
        self.comments = self._load_comments()
        
        # Create content directory if it doesn't exist
        os.makedirs(self.content_dir, exist_ok=True)
    
    def _load_content(self) -> Dict[str, ContentInDB]:
        """Load content from file"""
        if os.path.exists(self.content_file):
            try:
                with open(self.content_file, 'r') as f:
                    content_data = json.load(f)
                
                content = {}
                for item_data in content_data:
                    item = ContentInDB(**item_data)
                    content[item.id] = item
                
                return content
            except Exception as e:
                print(f"Error loading content: {e}")
        
        return {}
    
    def _save_content(self):
        """Save content to file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.content_file), exist_ok=True)
        
        # Convert content objects to dictionaries with datetime handling
        content_data = []
        for item in self.content.values():
            item_dict = item.dict()
            # Convert datetime objects to ISO format strings
            for key, value in item_dict.items():
                if isinstance(value, datetime):
                    item_dict[key] = value.isoformat()
            content_data.append(item_dict)
        
        with open(self.content_file, 'w') as f:
            json.dump(content_data, f, indent=2)
    
    def _load_comments(self) -> Dict[str, Comment]:
        """Load comments from file"""
        if os.path.exists(self.comments_file):
            try:
                with open(self.comments_file, 'r') as f:
                    comments_data = json.load(f)
                
                comments = {}
                for comment_data in comments_data:
                    comment = Comment(**comment_data)
                    comments[comment.id] = comment
                
                return comments
            except Exception as e:
                print(f"Error loading comments: {e}")
        
        return {}
    
    def _save_comments(self):
        """Save comments to file"""
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(self.comments_file), exist_ok=True)
        
        # Convert comment objects to dictionaries with datetime handling
        comments_data = []
        for comment in self.comments.values():
            comment_dict = comment.dict()
            # Convert datetime objects to ISO format strings
            for key, value in comment_dict.items():
                if isinstance(value, datetime):
                    comment_dict[key] = value.isoformat()
            comments_data.append(comment_dict)
        
        with open(self.comments_file, 'w') as f:
            json.dump(comments_data, f, indent=2)
    
    def get_content(self, content_id: str) -> Optional[Content]:
        """Get content by ID"""
        if content_id in self.content:
            content_in_db = self.content[content_id]
            
            # Convert file paths to URLs
            video_url = f"/api/content/{content_id}/video"
            thumbnail_url = f"/api/content/{content_id}/thumbnail" if content_in_db.thumbnail_path else None
            
            return Content(
                id=content_in_db.id,
                title=content_in_db.title,
                description=content_in_db.description,
                user_id=content_in_db.user_id,
                video_url=video_url,
                thumbnail_url=thumbnail_url,
                duration=content_in_db.duration,
                width=content_in_db.width,
                height=content_in_db.height,
                hashtags=content_in_db.hashtags,
                is_private=content_in_db.is_private,
                allow_comments=content_in_db.allow_comments,
                view_count=content_in_db.view_count,
                like_count=content_in_db.like_count,
                comment_count=content_in_db.comment_count,
                share_count=content_in_db.share_count,
                created_at=content_in_db.created_at,
                updated_at=content_in_db.updated_at
            )
        
        return None
    
    def create_content(self, content_create: ContentCreate, file_data: Optional[bytes] = None) -> Content:
        """Create new content"""
        content_id = str(uuid.uuid4())
        
        # Save file
        file_ext = Path(content_create.file_path).suffix
        file_path = os.path.join(self.content_dir, f"{content_id}{file_ext}")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        if file_data:
            with open(file_path, 'wb') as f:
                f.write(file_data)
        else:
            # Create an empty file for sample data
            with open(file_path, 'wb') as f:
                f.write(b'')
        
        # TODO: Generate thumbnail and get video metadata
        # For now, we'll use placeholder values
        thumbnail_path = None
        duration = 15.0  # seconds
        width = 1080
        height = 1920
        
        content_in_db = ContentInDB(
            id=content_id,
            title=content_create.title,
            description=content_create.description,
            user_id=content_create.user_id,
            file_path=file_path,
            thumbnail_path=thumbnail_path,
            duration=duration,
            width=width,
            height=height,
            hashtags=content_create.hashtags,
            is_private=content_create.is_private,
            allow_comments=content_create.allow_comments,
            view_count=0,
            like_count=0,
            comment_count=0,
            share_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save content to database
        self.content[content_id] = content_in_db
        self._save_content()
        
        # Add content to knowledge graph
        content = self.get_content(content_id)
        content_node = ContentNode(content)
        self.kg_service.add_node(content_node)
        
        # Add creator relationship
        created_by_edge = CreatedBy(content_id, content_create.user_id)
        self.kg_service.add_edge(created_by_edge)
        
        # Add hashtag nodes and relationships
        for hashtag in content_create.hashtags:
            hashtag_id = f"hashtag:{hashtag}"
            
            # Check if hashtag node exists
            if not self.kg_service.get_node(hashtag_id):
                hashtag_node = HashtagNode(hashtag)
                self.kg_service.add_node(hashtag_node)
            
            # Add relationship
            has_tag_edge = HasTag(content_id, hashtag_id)
            self.kg_service.add_edge(has_tag_edge)
        
        return content
    
    def update_content(self, content_id: str, content_update: ContentUpdate) -> Optional[Content]:
        """Update content"""
        if content_id not in self.content:
            return None
        
        content_in_db = self.content[content_id]
        
        # Update fields
        if content_update.title is not None:
            content_in_db.title = content_update.title
        
        if content_update.description is not None:
            content_in_db.description = content_update.description
        
        if content_update.is_private is not None:
            content_in_db.is_private = content_update.is_private
        
        if content_update.allow_comments is not None:
            content_in_db.allow_comments = content_update.allow_comments
        
        # Update hashtags if provided
        if content_update.hashtags is not None:
            old_hashtags = set(content_in_db.hashtags)
            new_hashtags = set(content_update.hashtags)
            
            # Remove old hashtag relationships
            for hashtag in old_hashtags - new_hashtags:
                hashtag_id = f"hashtag:{hashtag}"
                self.kg_service.remove_edge(content_id, hashtag_id, edge_type='HAS_TAG')
            
            # Add new hashtag relationships
            for hashtag in new_hashtags - old_hashtags:
                hashtag_id = f"hashtag:{hashtag}"
                
                # Check if hashtag node exists
                if not self.kg_service.get_node(hashtag_id):
                    hashtag_node = HashtagNode(hashtag)
                    self.kg_service.add_node(hashtag_node)
                
                # Add relationship
                has_tag_edge = HasTag(content_id, hashtag_id)
                self.kg_service.add_edge(has_tag_edge)
            
            content_in_db.hashtags = list(new_hashtags)
        
        content_in_db.updated_at = datetime.utcnow()
        
        # Save content to database
        self.content[content_id] = content_in_db
        self._save_content()
        
        # Update content in knowledge graph
        content = self.get_content(content_id)
        content_node = ContentNode(content)
        
        # Get existing node
        existing_node = self.kg_service.get_node(content_id)
        if existing_node:
            # Update properties
            self.kg_service.graph.nodes[content_id]['properties'] = content_node.properties
            self.kg_service._save_graph()
        
        return content
    
    def delete_content(self, content_id: str) -> bool:
        """Delete content"""
        if content_id not in self.content:
            return False
        
        content_in_db = self.content[content_id]
        
        # Delete file
        try:
            if os.path.exists(content_in_db.file_path):
                os.remove(content_in_db.file_path)
            
            if content_in_db.thumbnail_path and os.path.exists(content_in_db.thumbnail_path):
                os.remove(content_in_db.thumbnail_path)
        except Exception as e:
            print(f"Error deleting content files: {e}")
        
        # Remove content from database
        del self.content[content_id]
        self._save_content()
        
        # Remove content from knowledge graph
        self.kg_service.remove_node(content_id)
        
        # Remove associated comments
        comments_to_delete = [
            comment_id for comment_id, comment in self.comments.items()
            if comment.content_id == content_id
        ]
        
        for comment_id in comments_to_delete:
            del self.comments[comment_id]
        
        self._save_comments()
        
        return True
    
    def get_user_content(self, user_id: str, limit: int = 20, offset: int = 0) -> List[Content]:
        """Get content created by a user"""
        user_content = [
            self.get_content(content_id)
            for content_id, content_in_db in self.content.items()
            if content_in_db.user_id == user_id
        ]
        
        # Sort by creation date (newest first)
        user_content.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return user_content[offset:offset+limit]
    
    def search_content(self, query: str, limit: int = 20) -> List[Content]:
        """Search for content by title, description, or hashtags"""
        query = query.lower()
        results = []
        
        for content_id, content_in_db in self.content.items():
            # Skip private content
            if content_in_db.is_private:
                continue
            
            # Check title, description, and hashtags
            if ((content_in_db.title and query in content_in_db.title.lower()) or
                (content_in_db.description and query in content_in_db.description.lower()) or
                any(query in hashtag.lower() for hashtag in content_in_db.hashtags)):
                
                results.append(self.get_content(content_id))
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_content_by_hashtag(self, hashtag: str, limit: int = 20, offset: int = 0) -> List[Content]:
        """Get content with a specific hashtag"""
        hashtag = hashtag.lower()
        
        # Find content with the hashtag
        content_with_hashtag = [
            self.get_content(content_id)
            for content_id, content_in_db in self.content.items()
            if not content_in_db.is_private and hashtag in [h.lower() for h in content_in_db.hashtags]
        ]
        
        # Sort by creation date (newest first)
        content_with_hashtag.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return content_with_hashtag[offset:offset+limit]
    
    def add_comment(self, content_id: str, user_id: str, text: str, parent_comment_id: Optional[str] = None) -> Optional[Comment]:
        """Add a comment to content"""
        if content_id not in self.content:
            return None
        
        content_in_db = self.content[content_id]
        
        # Check if comments are allowed
        if not content_in_db.allow_comments:
            return None
        
        # Check if parent comment exists if provided
        if parent_comment_id and parent_comment_id not in self.comments:
            return None
        
        # Create comment
        comment_id = str(uuid.uuid4())
        
        comment = Comment(
            id=comment_id,
            content_id=content_id,
            user_id=user_id,
            text=text,
            parent_comment_id=parent_comment_id,
            like_count=0,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Save comment to database
        self.comments[comment_id] = comment
        self._save_comments()
        
        # Update content comment count
        content_in_db.comment_count += 1
        self._save_content()
        
        # Update content in knowledge graph
        self.kg_service.graph.nodes[content_id]['properties']['comment_count'] = content_in_db.comment_count
        self.kg_service._save_graph()
        
        # Add comment edge to knowledge graph
        from models.social import CommentEdge
        comment_edge = CommentEdge(user_id, content_id, comment_id)
        self.kg_service.add_edge(comment_edge)
        
        return comment
    
    def get_comments(self, content_id: str, limit: int = 50, offset: int = 0) -> List[Comment]:
        """Get comments for content"""
        if content_id not in self.content:
            return []
        
        # Get top-level comments
        top_level_comments = [
            comment for comment in self.comments.values()
            if comment.content_id == content_id and comment.parent_comment_id is None
        ]
        
        # Sort by creation date (newest first)
        top_level_comments.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply pagination
        return top_level_comments[offset:offset+limit]
    
    def get_comment_replies(self, comment_id: str, limit: int = 20, offset: int = 0) -> List[Comment]:
        """Get replies to a comment"""
        if comment_id not in self.comments:
            return []
        
        # Get replies
        replies = [
            comment for comment in self.comments.values()
            if comment.parent_comment_id == comment_id
        ]
        
        # Sort by creation date (oldest first)
        replies.sort(key=lambda x: x.created_at)
        
        # Apply pagination
        return replies[offset:offset+limit]
    
    def like_comment(self, comment_id: str, user_id: str) -> bool:
        """Like a comment"""
        if comment_id not in self.comments:
            return False
        
        comment = self.comments[comment_id]
        
        # Update comment like count
        comment.like_count += 1
        self._save_comments()
        
        return True
    
    def get_trending_hashtags(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending hashtags"""
        # Count hashtag occurrences in recent content
        hashtag_counts = {}
        
        for content_id, content_in_db in self.content.items():
            # Skip private content
            if content_in_db.is_private:
                continue
            
            # Only consider content from the last 7 days
            days_old = (datetime.utcnow() - content_in_db.created_at).days
            if days_old > 7:
                continue
            
            for hashtag in content_in_db.hashtags:
                hashtag = hashtag.lower()
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        # Sort hashtags by count
        trending_hashtags = [
            {
                'name': hashtag,
                'count': count
            }
            for hashtag, count in sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
        ]
        
        return trending_hashtags 