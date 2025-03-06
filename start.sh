#!/bin/bash

# Start the AI Agent Social Network System

# Set up environment
echo "Setting up environment..."
if [ ! -d "data" ]; then
    mkdir -p data
fi

if [ ! -d "templates" ]; then
    mkdir -p templates
fi

if [ ! -d "static/css" ]; then
    mkdir -p static/css
fi

if [ ! -d "static/js" ]; then
    mkdir -p static/js
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    cp .env.example .env
fi

# Check if Python virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Run tests
echo "Running system tests..."
python src/scripts/test_system.py

# Check if tests passed
if [ $? -ne 0 ]; then
    echo "Tests failed. Please check the error messages above."
    exit 1
fi

# Start the application
echo "Starting the application..."
python src/main.py 