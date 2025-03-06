#!/usr/bin/env python3
"""
Script to check comments in the system
"""
from src.services.content import ContentService
from src.services.knowledge_graph import KnowledgeGraphService

def main():
    # Initialize services
    kg_service = KnowledgeGraphService()
    content_service = ContentService(kg_service)
    
    # Get recent content
    recent_content = content_service.get_recent_content(limit=10)
    
    # Check comments for each content
    total_comments = 0
    for i, content in enumerate(recent_content):
        content_id = content.id if hasattr(content, 'id') else content.get('id', 'Unknown')
        title = content.title if hasattr(content, 'title') else content.get('title', 'No title')
        
        # Get comments for this content
        comments = content_service.get_comments(content_id)
        
        print(f"\n{i+1}. Content: {title}")
        print(f"   Comments: {len(comments)}")
        
        total_comments += len(comments)
        
        # Print each comment
        for j, comment in enumerate(comments):
            comment_text = comment.comment if hasattr(comment, 'comment') else comment.get('comment', 'No comment')
            user_id = comment.user_id if hasattr(comment, 'user_id') else comment.get('user_id', 'Unknown')
            created_at = comment.created_at if hasattr(comment, 'created_at') else comment.get('created_at', 'Unknown')
            
            print(f"   {j+1}. Comment: {comment_text[:100]}...")
            print(f"      User ID: {user_id}")
            print(f"      Created at: {created_at}")
    
    print(f"\nTotal comments: {total_comments}")

if __name__ == "__main__":
    main() 