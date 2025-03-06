"""
Knowledge Graph Social Network System - Main Application
"""
import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import routers
from src.api.users import router as users_router
from src.api.content import router as content_router
from src.api.social import router as social_router
from src.api.recommendations import router as recommendations_router
from src.api.analytics import router as analytics_router
from src.api.gemini import router as gemini_router
from src.api.openai import router as openai_router
from src.api.frontend import router as frontend_router
from src.api.autonomous import router as autonomous_router

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

# Mount static files directory for frontend
app.mount("/static", StaticFiles(directory="src/frontend/static"), name="static")

# Include API routers
app.include_router(users_router, prefix="/api/users", tags=["users"])
app.include_router(content_router, prefix="/api/content", tags=["content"])
app.include_router(social_router, prefix="/api/social", tags=["social"])
app.include_router(recommendations_router, prefix="/api/recommendations", tags=["recommendations"])
app.include_router(analytics_router, prefix="/api/analytics", tags=["analytics"])
app.include_router(gemini_router, prefix="/api/gemini", tags=["gemini"])
app.include_router(openai_router, prefix="/api/openai", tags=["openai"])
app.include_router(autonomous_router, prefix="/api/autonomous", tags=["autonomous"])

# Include frontend router (no prefix, handles root routes)
app.include_router(frontend_router, tags=["frontend"])

# API root endpoint
@app.get("/api")
async def api_root():
    """Root endpoint that returns basic API information"""
    return {
        "message": "Welcome to the Knowledge Graph Social Network API",
        "version": "0.1.0",
        "documentation": "/docs"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.getenv("PORT", 8000))
    
    # Run the application
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    ) 