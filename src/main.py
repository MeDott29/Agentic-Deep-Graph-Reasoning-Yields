#!/usr/bin/env python3
# Knowledge Graph Social Network System
# Main application entry point

import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API routers
from api.users import router as users_router
from api.content import router as content_router
from api.graph import router as graph_router
from api.agents import router as agents_router

# Create FastAPI application
app = FastAPI(
    title="Knowledge Graph Social Network",
    description="A synthetic knowledge graph-based social network system that blends human and AI-generated content",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(content_router, prefix="/api/content", tags=["content"])
app.include_router(graph_router, prefix="/api/graph", tags=["graph"])
app.include_router(agents_router, prefix="/api/agents", tags=["agents"])

# Root endpoint
@app.get("/", tags=["root"])
async def root():
    return {
        "message": "Welcome to the Knowledge Graph Social Network API",
        "documentation": "/docs",
    }

# Run the application
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=debug) 