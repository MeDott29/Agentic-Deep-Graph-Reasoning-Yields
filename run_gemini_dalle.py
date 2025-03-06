#!/usr/bin/env python3
"""
Run script for Gemini-DALL-E interactions in the Knowledge Graph Social Network System
"""
import os
import argparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.scripts.gemini_dalle_interaction import GeminiDalleInteraction

def main():
    """Main function to run Gemini-DALL-E interactions"""
    parser = argparse.ArgumentParser(description="Run Gemini-DALL-E interactions")
    parser.add_argument(
        "--interval", 
        type=int, 
        default=15, 
        help="Interval between interactions in seconds (default: 15)"
    )
    parser.add_argument(
        "--single-cycle", 
        action="store_true", 
        help="Run a single cycle of interactions and exit"
    )
    args = parser.parse_args()
    
    # Create the interaction service
    interaction_service = GeminiDalleInteraction()
    
    # Run interactions
    if args.single_cycle:
        print("Running a single cycle of Gemini-DALL-E interactions...")
        interaction_service.run_interaction_cycle()
        print("Completed.")
    else:
        print(f"Starting Gemini-DALL-E interactions with interval of {args.interval} seconds...")
        print("Press Ctrl+C to stop.")
        interaction_service.start(interval_seconds=args.interval)

if __name__ == "__main__":
    main() 