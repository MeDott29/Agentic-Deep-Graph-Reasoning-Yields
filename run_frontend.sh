#!/bin/bash
# Run script for Knowledge Graph Social Network Frontend

# Function to handle errors
handle_error() {
    echo "Error: $1 failed with exit code $2"
    echo "Check the error messages above for details."
    exit $2
}

# Function to initialize the system in the background
initialize_system_background() {
    # Initialize database
    echo "Initializing database in the background..."
    python src/scripts/init_db.py
    
    # Create AI agents if they don't exist
    echo "Creating AI agents in the background..."
    python src/scripts/init_agents.py
    
    # Generate initial content
    echo "Generating initial content in the background..."
    python src/scripts/generate_content.py
    
    echo "Background initialization complete!"
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

# Start initialization in the background
initialize_system_background &
INIT_PID=$!
echo "System initialization started in the background (PID $INIT_PID)"

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Error: streamlit is not installed."
    echo "Please install it using: pip install streamlit"
    
    # Kill background process
    if [ -n "$INIT_PID" ]; then
        kill $INIT_PID
    fi
    
    exit 1
fi

# Run the Streamlit app
echo "Starting Streamlit frontend..."
echo "The frontend will be available at http://localhost:8501"
echo "System initialization is running in the background."
echo "Content will appear as it's generated."
echo ""
echo "Press Ctrl+C to stop the frontend."
echo ""

# Run the frontend
streamlit run src/frontend.py

# Kill background process when frontend exits
if [ -n "$INIT_PID" ]; then
    echo "Stopping background initialization (PID $INIT_PID)..."
    kill $INIT_PID
fi 