#!/usr/bin/env python3
# Initialize database files

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def ensure_dir(path):
    """Ensure directory exists."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

def init_user_db(path):
    """Initialize user database."""
    ensure_dir(path)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump([], f)
        print(f"Created user database at {path}")
    else:
        print(f"User database already exists at {path}")

def init_content_db(path):
    """Initialize content database."""
    ensure_dir(path)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"content": [], "comments": []}, f)
        print(f"Created content database at {path}")
    else:
        print(f"Content database already exists at {path}")

def init_graph_db(path):
    """Initialize graph database."""
    ensure_dir(path)
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump({"nodes": [], "edges": []}, f)
        print(f"Created graph database at {path}")
    else:
        print(f"Graph database already exists at {path}")

def main():
    """Initialize all database files."""
    # Get database paths from environment variables or use defaults
    user_db_path = os.getenv("USER_DB_PATH", "./data/users.json")
    content_db_path = os.getenv("CONTENT_DB_PATH", "./data/content.json")
    graph_db_path = os.getenv("GRAPH_DB_PATH", "./data/graph.json")
    
    # Initialize databases
    init_user_db(user_db_path)
    init_content_db(content_db_path)
    init_graph_db(graph_db_path)
    
    print("Database initialization complete")

if __name__ == "__main__":
    main() 