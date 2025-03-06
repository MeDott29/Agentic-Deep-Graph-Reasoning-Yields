from src.services.user import UserService
from src.services.knowledge_graph import KnowledgeGraphService
from src.services.gemini_service import GeminiService
from src.services.ai_agent_service import AIAgentService
from src.services.openai_service import OpenAIService
from src.services.content import ContentService
from src.services.recommendation import RecommendationService
from src.services.ai_agent_interaction_service import AIAgentInteractionService

# Knowledge Graph Service
_knowledge_graph_service = None

def get_knowledge_graph_service():
    global _knowledge_graph_service
    if _knowledge_graph_service is None:
        _knowledge_graph_service = KnowledgeGraphService()
    return _knowledge_graph_service

# AI Agent Service
_ai_agent_service = None

def get_ai_agent_service():
    global _ai_agent_service
    if _ai_agent_service is None:
        _ai_agent_service = AIAgentService(get_knowledge_graph_service())
    return _ai_agent_service

# OpenAI Service
_openai_service = None

def get_openai_service():
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service

# Content Service
_content_service = None

def get_content_service():
    global _content_service
    if _content_service is None:
        _content_service = ContentService(get_knowledge_graph_service())
    return _content_service

# Recommendation Service
_recommendation_service = None

def get_recommendation_service():
    global _recommendation_service
    if _recommendation_service is None:
        _recommendation_service = RecommendationService(get_knowledge_graph_service())
    return _recommendation_service

# User Service
_user_service = None

def get_user_service():
    global _user_service
    if _user_service is None:
        _user_service = UserService(get_knowledge_graph_service())
    return _user_service

# Gemini Service
_gemini_service = None

def get_gemini_service():
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service

# AI Agent Interaction Service
_ai_agent_interaction_service = None

def get_ai_agent_interaction_service():
    global _ai_agent_interaction_service
    if _ai_agent_interaction_service is None:
        _ai_agent_interaction_service = AIAgentInteractionService(
            get_ai_agent_service(),
            get_content_service(),
            get_gemini_service(),
            get_openai_service()
        )
    return _ai_agent_interaction_service 