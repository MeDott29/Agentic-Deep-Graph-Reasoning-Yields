#!/usr/bin/env python3
"""
Simple script to run the AI Agent Social Network System.
"""
import os
import sys
import subprocess

def main():
    """
    Run the AI Agent Social Network System.
    """
    # Ensure we're in the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)
    
    # Check if the data directory exists
    if not os.path.exists("data"):
        os.makedirs("data")
    
    # Check if the templates directory exists
    if not os.path.exists("templates"):
        os.makedirs("templates")
    
    # Check if the static directory exists
    if not os.path.exists("static"):
        os.makedirs("static")
        os.makedirs("static/css", exist_ok=True)
        os.makedirs("static/js", exist_ok=True)
    
    # Run the application
    try:
        subprocess.run([sys.executable, "src/main.py"], check=True)
    except KeyboardInterrupt:
        print("\nShutting down the application...")
    except Exception as e:
        print(f"Error running the application: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 