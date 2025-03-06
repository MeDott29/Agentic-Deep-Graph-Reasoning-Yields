#!/usr/bin/env python
"""
Wrapper script to run the image generation program.

This script runs the image generation program that replaces all placeholder
images in the project with DALL-E-2 generated images.
"""
import os
import sys
import subprocess
import argparse

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run the image generation program")
    parser.add_argument("--dry-run", action="store_true", help="Perform a dry run without making any changes")
    parser.add_argument("--force", action="store_true", help="Force replacement of images even if they already exist")
    args = parser.parse_args()
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.abspath(__file__))
    
    # Build the command
    cmd = [sys.executable, os.path.join(project_root, "src", "scripts", "generate_images.py")]
    
    # Add arguments
    if args.dry_run:
        cmd.append("--dry-run")
    if args.force:
        cmd.append("--force")
    
    # Print the command
    print(f"Running command: {' '.join(cmd)}")
    
    # Run the command
    try:
        subprocess.run(cmd, check=True)
        print("Image generation completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running image generation: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 