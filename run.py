#!/usr/bin/env python3
"""
Run script for Knowledge Graph Social Network System
"""
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    print(f"Starting Knowledge Graph Social Network System on port {port}")
    print(f"Access the web interface at http://localhost:{port}")
    print(f"API documentation available at http://localhost:{port}/docs")
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 