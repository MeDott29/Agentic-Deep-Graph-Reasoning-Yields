#!/usr/bin/env python3
"""
Run Autonomous Agent Posting Service

This script runs the autonomous agent posting service as a background process.
It can be started and stopped using command-line arguments.
"""
import os
import sys
import argparse
import subprocess
import signal
import time
from pathlib import Path

# Add the parent directory to the path so we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Define the PID file path
PID_FILE = "autonomous_agents.pid"

def start_service():
    """Start the autonomous agent posting service"""
    # Check if the service is already running
    if os.path.exists(PID_FILE):
        with open(PID_FILE, 'r') as f:
            pid = int(f.read().strip())
        
        # Check if the process is still running
        try:
            os.kill(pid, 0)
            print(f"Autonomous agent posting service is already running (PID: {pid})")
            return
        except OSError:
            # Process is not running, remove the PID file
            os.remove(PID_FILE)
    
    # Start the service
    print("Starting autonomous agent posting service...")
    
    # Get the path to the autonomous_agent_posting.py script
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "autonomous_agent_posting.py")
    
    # Start the process
    process = subprocess.Popen(
        [sys.executable, script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True  # Start in a new session so it's not killed when the parent process exits
    )
    
    # Save the PID to a file
    with open(PID_FILE, 'w') as f:
        f.write(str(process.pid))
    
    print(f"Autonomous agent posting service started (PID: {process.pid})")

def stop_service():
    """Stop the autonomous agent posting service"""
    if not os.path.exists(PID_FILE):
        print("Autonomous agent posting service is not running")
        return
    
    # Read the PID from the file
    with open(PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    # Try to stop the process
    try:
        # Send SIGTERM to the process group
        os.killpg(os.getpgid(pid), signal.SIGTERM)
        
        # Wait for the process to terminate
        for _ in range(10):
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except OSError:
                # Process has terminated
                break
        else:
            # Process didn't terminate, send SIGKILL
            os.killpg(os.getpgid(pid), signal.SIGKILL)
        
        print(f"Autonomous agent posting service stopped (PID: {pid})")
    except OSError as e:
        print(f"Error stopping autonomous agent posting service: {e}")
    
    # Remove the PID file
    os.remove(PID_FILE)

def status_service():
    """Check the status of the autonomous agent posting service"""
    if not os.path.exists(PID_FILE):
        print("Autonomous agent posting service is not running")
        return
    
    # Read the PID from the file
    with open(PID_FILE, 'r') as f:
        pid = int(f.read().strip())
    
    # Check if the process is still running
    try:
        os.kill(pid, 0)
        print(f"Autonomous agent posting service is running (PID: {pid})")
    except OSError:
        print("Autonomous agent posting service is not running (stale PID file)")
        os.remove(PID_FILE)

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run autonomous agent posting service")
    parser.add_argument("action", choices=["start", "stop", "restart", "status"], help="Action to perform")
    
    args = parser.parse_args()
    
    if args.action == "start":
        start_service()
    elif args.action == "stop":
        stop_service()
    elif args.action == "restart":
        stop_service()
        time.sleep(1)
        start_service()
    elif args.action == "status":
        status_service()

if __name__ == "__main__":
    main() 