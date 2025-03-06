#!/usr/bin/env python3
"""
Run script for autonomous AI agent interactions in the Knowledge Graph Social Network System
"""
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.services.knowledge_graph import KnowledgeGraphService
from src.services.ai_agent_service import AIAgentService
from src.services.content import ContentService
from src.services.gemini_service import GeminiService
from src.services.openai_service import OpenAIService
from src.services.ai_agent_interaction_service import AIAgentInteractionService

def main():
    """Main function to run autonomous agent interactions"""
    parser = argparse.ArgumentParser(description="Run autonomous AI agent interactions")
    parser.add_argument(
        "--interval", 
        type=int, 
        default=120, 
        help="Interval between agent interactions in seconds (default: 120)"
    )
    parser.add_argument(
        "--single-cycle", 
        action="store_true", 
        help="Run a single cycle of interactions and exit"
    )
    args = parser.parse_args()
    
    # Create services
    kg_service = KnowledgeGraphService()
    ai_agent_service = AIAgentService(kg_service)
    content_service = ContentService(kg_service)
    gemini_service = GeminiService()
    openai_service = OpenAIService()
    
    # Create the interaction service
    interaction_service = AIAgentInteractionService(
        ai_agent_service,
        content_service,
        gemini_service,
        openai_service
    )
    
    # Run interactions
    if args.single_cycle:
        print("Running a single cycle of autonomous agent interactions...")
        interaction_service.run_autonomous_interaction_cycle()
        print("Completed.")
    else:
        print(f"Starting autonomous agent interactions with interval of {args.interval} seconds...")
        print("Press Ctrl+C to stop.")
        interaction_service.start_autonomous_interactions(interval_seconds=args.interval)

if __name__ == "__main__":
    main() 