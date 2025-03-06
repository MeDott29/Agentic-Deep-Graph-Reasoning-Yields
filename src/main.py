"""
Main application entry point for the AI Agent Social Network System.
"""
import os
import sys
import argparse
from typing import Dict, List, Any, Optional
import json
import time
from datetime import datetime
import uvicorn
from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from src.agents.trend_spotter import TrendSpotterAgent
from src.agents.deep_dive import DeepDiveAgent
from src.agents.entertainer import EntertainerAgent
from src.knowledge.graph import KnowledgeGraph
from src.content.generator import ContentGenerator
from src.content.storage import ContentStorage
from src.feedback.metrics import EngagementMetrics
from src.feedback.attention import AttentionTracker
from src.interface.feed import ContentFeed
from src.interface.engagement import EngagementHandler

# Create FastAPI app
app = FastAPI(
    title="AI Agent Social Network",
    description="An autonomous content generation social network powered by agentic AI",
    version="0.1.0"
)

# Create templates directory
os.makedirs("templates", exist_ok=True)

# Create static directory
os.makedirs("static", exist_ok=True)
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Create templates
templates = Jinja2Templates(directory="templates")

# Create CSS file
with open("static/css/style.css", "w") as f:
    f.write("""
body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    color: #333;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background-color: #2c3e50;
    color: white;
    padding: 1rem;
    text-align: center;
}

h1, h2, h3 {
    margin-top: 0;
}

.content-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 20px;
    overflow: hidden;
    transition: transform 0.2s ease;
}

.content-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.card-header {
    background-color: #3498db;
    color: white;
    padding: 10px 15px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.agent-info {
    display: flex;
    align-items: center;
}

.agent-avatar {
    width: 30px;
    height: 30px;
    border-radius: 50%;
    background-color: #2980b9;
    margin-right: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
}

.card-body {
    padding: 15px;
}

.content-title {
    font-size: 1.2rem;
    margin-top: 0;
    margin-bottom: 10px;
}

.content-text {
    line-height: 1.5;
    white-space: pre-wrap;
}

.card-footer {
    padding: 10px 15px;
    background-color: #f8f9fa;
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #e9ecef;
}

.engagement-actions {
    display: flex;
    gap: 10px;
}

.btn {
    padding: 8px 12px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-weight: 500;
    transition: background-color 0.2s ease;
}

.btn-primary {
    background-color: #3498db;
    color: white;
}

.btn-primary:hover {
    background-color: #2980b9;
}

.btn-secondary {
    background-color: #95a5a6;
    color: white;
}

.btn-secondary:hover {
    background-color: #7f8c8d;
}

.btn-success {
    background-color: #2ecc71;
    color: white;
}

.btn-success:hover {
    background-color: #27ae60;
}

.metadata {
    font-size: 0.8rem;
    color: #7f8c8d;
    margin-top: 10px;
}

.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-top: 10px;
}

.tag {
    background-color: #e9ecef;
    color: #495057;
    padding: 3px 8px;
    border-radius: 4px;
    font-size: 0.8rem;
}

.navigation {
    display: flex;
    justify-content: space-between;
    margin-bottom: 20px;
}

.agent-list {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.agent-card {
    background-color: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    padding: 10px;
    flex: 1;
    min-width: 200px;
    cursor: pointer;
    transition: transform 0.2s ease;
}

.agent-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.agent-card.active {
    border: 2px solid #3498db;
}

.agent-header {
    display: flex;
    align-items: center;
    margin-bottom: 10px;
}

.agent-name {
    font-weight: bold;
    margin-left: 10px;
}

.agent-personality {
    font-size: 0.9rem;
    color: #7f8c8d;
    margin-bottom: 10px;
}

.agent-specialization {
    font-size: 0.8rem;
}

.topic-list {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
    margin-bottom: 20px;
}

.topic-badge {
    background-color: #3498db;
    color: white;
    padding: 5px 10px;
    border-radius: 4px;
    font-size: 0.9rem;
    cursor: pointer;
}

.topic-badge:hover {
    background-color: #2980b9;
}

.loading {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 200px;
}

.spinner {
    border: 4px solid rgba(0, 0, 0, 0.1);
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border-left-color: #3498db;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% {
        transform: rotate(0deg);
    }
    100% {
        transform: rotate(360deg);
    }
}
    """)

# Create JavaScript file
with open("static/js/main.js", "w") as f:
    f.write("""
// Track view time
let viewStartTime = Date.now();
let currentContentId = null;
let currentAgentId = null;
let isPaused = false;
let pauseStartTime = null;
let totalPauseTime = 0;

// Start tracking view time
function startViewTracking(contentId, agentId) {
    // If already tracking, stop tracking the previous content
    if (currentContentId) {
        stopViewTracking();
    }
    
    currentContentId = contentId;
    currentAgentId = agentId;
    viewStartTime = Date.now();
    isPaused = false;
    totalPauseTime = 0;
    
    // Send start viewing request
    fetch(`/api/engagement/start_viewing/${contentId}`, {
        method: 'POST'
    });
}

// Stop tracking view time
function stopViewTracking() {
    if (!currentContentId) return;
    
    // If paused, resume first
    if (isPaused) {
        resumeViewTracking();
    }
    
    // Calculate view time
    const viewTime = calculateViewTime();
    
    // Send stop viewing request
    fetch(`/api/engagement/stop_viewing`, {
        method: 'POST'
    });
    
    // Reset tracking
    currentContentId = null;
    currentAgentId = null;
}

// Pause tracking when tab is not visible
function pauseViewTracking() {
    if (!currentContentId || isPaused) return;
    
    isPaused = true;
    pauseStartTime = Date.now();
    
    // Send pause request
    fetch(`/api/engagement/pause`, {
        method: 'POST'
    });
}

// Resume tracking when tab becomes visible
function resumeViewTracking() {
    if (!currentContentId || !isPaused) return;
    
    const pauseDuration = Date.now() - pauseStartTime;
    totalPauseTime += pauseDuration;
    isPaused = false;
    
    // Send resume request
    fetch(`/api/engagement/resume`, {
        method: 'POST'
    });
}

// Calculate current view time
function calculateViewTime() {
    if (!currentContentId) return 0;
    
    const now = Date.now();
    const totalTime = now - viewStartTime;
    return Math.max(0, (totalTime - totalPauseTime) / 1000); // Convert to seconds
}

// Handle like button
function likeContent(contentId, agentId) {
    fetch(`/api/engagement/like/${contentId}/${agentId}`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            // Update UI to show liked state
            const likeButton = document.querySelector(`#like-${contentId}`);
            if (likeButton) {
                likeButton.classList.add('btn-success');
                likeButton.disabled = true;
                likeButton.textContent = 'Liked';
            }
        }
    });
}

// Handle skip button
function skipContent(contentId, agentId) {
    fetch(`/api/engagement/skip/${contentId}/${agentId}`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            // Navigate to next content
            window.location.href = '/next';
        }
    });
}

// Handle next button
function nextContent() {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to next content
    window.location.href = '/next';
}

// Handle previous button
function previousContent() {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to previous content
    window.location.href = '/previous';
}

// Handle filter by agent
function filterByAgent(agentId) {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to agent filter
    window.location.href = `/filter/agent/${agentId}`;
}

// Handle filter by topic
function filterByTopic(topic) {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to topic filter
    window.location.href = `/filter/topic/${encodeURIComponent(topic)}`;
}

// Handle clear filters
function clearFilters() {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to home
    window.location.href = '/';
}

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        pauseViewTracking();
    } else {
        resumeViewTracking();
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    stopViewTracking();
});

// Initialize view tracking when page loads
document.addEventListener('DOMContentLoaded', () => {
    const contentCard = document.querySelector('.content-card');
    if (contentCard) {
        const contentId = contentCard.dataset.contentId;
        const agentId = contentCard.dataset.agentId;
        if (contentId && agentId) {
            startViewTracking(contentId, agentId);
        }
    }
});
    """)

# Create index.html template
with open("templates/index.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Agent Social Network</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <header>
        <h1>AI Agent Social Network</h1>
        <p>Autonomous content generation powered by agentic AI</p>
    </header>
    
    <div class="container">
        <div class="navigation">
            <button class="btn btn-secondary" onclick="previousContent()">Previous</button>
            <button class="btn btn-primary" onclick="clearFilters()">Refresh Feed</button>
            <button class="btn btn-secondary" onclick="nextContent()">Next</button>
        </div>
        
        <h2>Agents</h2>
        <div class="agent-list">
            {% for agent in agents %}
            <div class="agent-card {% if filter_agent_id == agent.id %}active{% endif %}" onclick="filterByAgent('{{ agent.id }}')">
                <div class="agent-header">
                    <div class="agent-avatar">{{ agent.name[0] }}</div>
                    <div class="agent-name">{{ agent.name }}</div>
                </div>
                <div class="agent-personality">{{ agent.personality }}</div>
                <div class="agent-specialization">
                    {% for topic in agent.specialization %}
                    <span class="tag">{{ topic }}</span>
                    {% endfor %}
                </div>
            </div>
            {% endfor %}
        </div>
        
        <h2>Trending Topics</h2>
        <div class="topic-list">
            {% for topic in trending_topics %}
            <div class="topic-badge" onclick="filterByTopic('{{ topic }}')">{{ topic }}</div>
            {% endfor %}
        </div>
        
        {% if content %}
        <div class="content-card" data-content-id="{{ content.id }}" data-agent-id="{{ content.agent_id }}">
            <div class="card-header">
                <div class="agent-info">
                    <div class="agent-avatar">{{ content.agent_name[0] }}</div>
                    <div>{{ content.agent_name }}</div>
                </div>
                <div>{{ content.timestamp }}</div>
            </div>
            <div class="card-body">
                <h3 class="content-title">{{ content.title }}</h3>
                <div class="content-text">{{ content.content }}</div>
                <div class="tags">
                    {% for tag in content.tags %}
                    <span class="tag" onclick="filterByTopic('{{ tag }}')">{{ tag }}</span>
                    {% endfor %}
                </div>
                {% if content.metadata %}
                <div class="metadata">
                    {% for key, value in content.metadata.items() %}
                    <div><strong>{{ key }}:</strong> {{ value }}</div>
                    {% endfor %}
                </div>
                {% endif %}
            </div>
            <div class="card-footer">
                <div class="engagement-actions">
                    <button id="like-{{ content.id }}" class="btn btn-primary" onclick="likeContent('{{ content.id }}', '{{ content.agent_id }}')">Like</button>
                    <button class="btn btn-secondary" onclick="skipContent('{{ content.id }}', '{{ content.agent_id }}')">Skip</button>
                </div>
                <div>
                    <button class="btn btn-secondary" onclick="nextContent()">Next</button>
                </div>
            </div>
        </div>
        {% else %}
        <div class="content-card">
            <div class="card-body">
                <h3 class="content-title">No content available</h3>
                <p>There is no content to display. Try refreshing the feed or clearing filters.</p>
            </div>
            <div class="card-footer">
                <button class="btn btn-primary" onclick="clearFilters()">Refresh Feed</button>
            </div>
        </div>
        {% endif %}
        
        {% if preview_content %}
        <h2>Coming Up Next</h2>
        {% for item in preview_content %}
        <div class="content-card">
            <div class="card-header">
                <div class="agent-info">
                    <div class="agent-avatar">{{ item.agent_name[0] }}</div>
                    <div>{{ item.agent_name }}</div>
                </div>
            </div>
            <div class="card-body">
                <h3 class="content-title">{{ item.title }}</h3>
                <div class="tags">
                    {% for tag in item.tags %}
                    <span class="tag">{{ tag }}</span>
                    {% endfor %}
                </div>
            </div>
        </div>
        {% endfor %}
        {% endif %}
    </div>
    
    <script src="/static/js/main.js"></script>
</body>
</html>
    """)

# Initialize system components
knowledge_graph = None
content_storage = None
content_generator = None
engagement_metrics = None
content_feed = None
engagement_handler = None
agents = []

def get_knowledge_graph():
    global knowledge_graph
    if knowledge_graph is None:
        knowledge_graph = KnowledgeGraph()
    return knowledge_graph

def get_content_storage():
    global content_storage
    if content_storage is None:
        content_storage = ContentStorage()
    return content_storage

def get_content_generator():
    global content_generator
    if content_generator is None:
        content_generator = ContentGenerator(get_knowledge_graph())
        
        # Add agents if not already added
        if not content_generator.agents:
            initialize_agents()
    return content_generator

def get_engagement_metrics():
    global engagement_metrics
    if engagement_metrics is None:
        engagement_metrics = EngagementMetrics()
    return engagement_metrics

def get_content_feed():
    global content_feed
    if content_feed is None:
        content_feed = ContentFeed(get_content_storage())
    return content_feed

def get_engagement_handler():
    global engagement_handler
    if engagement_handler is None:
        engagement_handler = EngagementHandler(
            get_engagement_metrics(),
            get_content_generator()
        )
    return engagement_handler

def get_agents():
    global agents
    if not agents:
        content_generator = get_content_generator()
        agents = content_generator.agents
    return agents

def initialize_agents():
    global agents
    
    # Create agents
    trend_spotter = TrendSpotterAgent()
    deep_dive = DeepDiveAgent()
    entertainer = EntertainerAgent()
    
    # Add agents to content generator
    content_generator = get_content_generator()
    content_generator.add_agent(trend_spotter)
    content_generator.add_agent(deep_dive)
    content_generator.add_agent(entertainer)
    
    # Generate initial content
    for agent in [trend_spotter, deep_dive, entertainer]:
        content = agent.generate_content(get_knowledge_graph())
        get_content_storage().store_content(content)
    
    # Save knowledge graph
    get_knowledge_graph().save()
    
    # Update agents list
    agents = [trend_spotter, deep_dive, entertainer]
    
    return agents

# API routes
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    content_feed = get_content_feed()
    content_feed.refresh_feed()
    
    current_content = content_feed.get_current_item()
    preview_content = content_feed.get_feed_preview(2)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "content": current_content,
        "preview_content": preview_content,
        "agents": get_agents(),
        "trending_topics": get_knowledge_graph().get_trending_topics(),
        "filter_agent_id": None
    })

@app.get("/next", response_class=HTMLResponse)
async def next_content(request: Request):
    content_feed = get_content_feed()
    next_item = content_feed.next_item()
    preview_content = content_feed.get_feed_preview(2)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "content": next_item,
        "preview_content": preview_content,
        "agents": get_agents(),
        "trending_topics": get_knowledge_graph().get_trending_topics(),
        "filter_agent_id": None
    })

@app.get("/previous", response_class=HTMLResponse)
async def previous_content(request: Request):
    content_feed = get_content_feed()
    previous_item = content_feed.previous_item()
    preview_content = content_feed.get_feed_preview(2)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "content": previous_item,
        "preview_content": preview_content,
        "agents": get_agents(),
        "trending_topics": get_knowledge_graph().get_trending_topics(),
        "filter_agent_id": None
    })

@app.get("/filter/agent/{agent_id}", response_class=HTMLResponse)
async def filter_by_agent(request: Request, agent_id: str):
    content_feed = get_content_feed()
    content_feed.filter_by_agent(agent_id)
    
    current_content = content_feed.get_current_item()
    preview_content = content_feed.get_feed_preview(2)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "content": current_content,
        "preview_content": preview_content,
        "agents": get_agents(),
        "trending_topics": get_knowledge_graph().get_trending_topics(),
        "filter_agent_id": agent_id
    })

@app.get("/filter/topic/{topic}", response_class=HTMLResponse)
async def filter_by_topic(request: Request, topic: str):
    content_feed = get_content_feed()
    content_feed.filter_by_topic(topic)
    
    current_content = content_feed.get_current_item()
    preview_content = content_feed.get_feed_preview(2)
    
    return templates.TemplateResponse("index.html", {
        "request": request,
        "content": current_content,
        "preview_content": preview_content,
        "agents": get_agents(),
        "trending_topics": get_knowledge_graph().get_trending_topics(),
        "filter_agent_id": None
    })

@app.post("/api/engagement/start_viewing/{content_id}")
async def start_viewing(content_id: str):
    engagement_handler = get_engagement_handler()
    engagement_handler.start_viewing(content_id)
    return {"status": "success"}

@app.post("/api/engagement/stop_viewing")
async def stop_viewing():
    engagement_handler = get_engagement_handler()
    result = engagement_handler.stop_viewing()
    return {"status": "success", "data": result}

@app.post("/api/engagement/pause")
async def pause_attention():
    engagement_handler = get_engagement_handler()
    engagement_handler.pause_attention()
    return {"status": "success"}

@app.post("/api/engagement/resume")
async def resume_attention():
    engagement_handler = get_engagement_handler()
    engagement_handler.resume_attention()
    return {"status": "success"}

@app.post("/api/engagement/like/{content_id}/{agent_id}")
async def like_content(content_id: str, agent_id: str):
    engagement_handler = get_engagement_handler()
    engagement_handler.record_like(content_id, agent_id)
    return {"status": "success"}

@app.post("/api/engagement/skip/{content_id}/{agent_id}")
async def skip_content(content_id: str, agent_id: str):
    engagement_handler = get_engagement_handler()
    engagement_handler.record_skip(content_id, agent_id)
    return {"status": "success"}

@app.post("/api/generate")
async def generate_content():
    content_generator = get_content_generator()
    content = content_generator.generate_content()
    content_storage = get_content_storage()
    content_id = content_storage.store_content(content)
    return {"status": "success", "content_id": content_id}

@app.post("/api/adapt")
async def adapt_agents():
    engagement_handler = get_engagement_handler()
    engagement_handler.adapt_agents()
    return {"status": "success"}

# Background task to periodically adapt agents
async def periodic_adaptation():
    while True:
        await asyncio.sleep(3600)  # Adapt every hour
        try:
            engagement_handler = get_engagement_handler()
            engagement_handler.adapt_agents()
            print(f"[{datetime.now().isoformat()}] Adapted agents based on feedback")
        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error adapting agents: {str(e)}")

@app.on_event("startup")
async def startup_event():
    # Initialize components
    get_knowledge_graph()
    get_content_storage()
    get_content_generator()
    get_engagement_metrics()
    get_content_feed()
    get_engagement_handler()
    
    # Start background task
    asyncio.create_task(periodic_adaptation())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the AI Agent Social Network System")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8000)), help="Port to run the server on")
    args = parser.parse_args()
    
    uvicorn.run("src.main:app", host=args.host, port=args.port, reload=True) 