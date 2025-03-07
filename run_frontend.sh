#!/bin/bash
# Run script for Knowledge Graph Social Network Frontend

# Function to handle errors
handle_error() {
    echo "Error: $1 failed with exit code $2"
    echo "Check the error messages above for details."
    exit $2
}

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
    echo "Environment variables loaded from .env file."
else
    echo "Warning: .env file not found. Using default values."
    echo "Consider creating a .env file from .env.example for proper configuration."
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY is not set in .env file."
    echo "AI content generation will use fallback method instead of GPT-4o."
    echo "To use GPT-4o, add your OpenAI API key to the .env file."
    echo ""
fi

# Ensure data directory exists
mkdir -p src/data
echo "Data directory created/verified."

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Error: streamlit is not installed."
    echo "Please install it using: pip install streamlit"
    exit 1
fi

# Run the Streamlit app
echo "Starting Streamlit frontend..."
echo "The frontend will be available at http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop the frontend."
echo ""

streamlit run src/frontend.py 