"""
Knowledge Graph Social Network System - Main Application
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from api.users import router as users_router
from api.content import router as content_router
from api.social import router as social_router
from api.recommendations import router as recommendations_router
from api.analytics import router as analytics_router
from api.ai_content import router as ai_content_router

# Create FastAPI application
app = FastAPI(
    title="Knowledge Graph Social Network",
    description="A TikTok-inspired social network system using knowledge graphs",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(content_router, prefix="/api/content", tags=["content"])
app.include_router(social_router, prefix="/api/social", tags=["social"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(ai_content_router, prefix="/api/ai-content", tags=["ai-content"])

@app.get("/")
async def root():
    """Root endpoint that returns basic API information"""
    return {
        "message": "Welcome to the Knowledge Graph Social Network API",
        "version": "0.1.0",
        "documentation": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 