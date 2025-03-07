#!/bin/bash
# Run script for Knowledge Graph Social Network

# Function to handle errors
handle_error() {
    echo "Error: $1 failed with exit code $2"
    echo "Check the error messages above for details."
    exit $2
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --api-only     Run only the API server (default)"
    echo "  --frontend     Run only the Streamlit frontend"
    echo "  --all          Run both the API server and the frontend"
    echo "  --help         Show this help message"
    echo ""
    exit 0
}

# Parse command line arguments
RUN_API=true
RUN_FRONTEND=false

if [ $# -gt 0 ]; then
    case "$1" in
        --api-only)
            RUN_API=true
            RUN_FRONTEND=false
            ;;
        --frontend)
            RUN_API=false
            RUN_FRONTEND=true
            ;;
        --all)
            RUN_API=true
            RUN_FRONTEND=true
            ;;
        --help)
            show_usage
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            ;;
    esac
fi

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

# Initialize database
echo "Initializing database..."
python src/scripts/init_db.py || handle_error "Database initialization" $?
echo "Database initialization completed successfully."

# Create AI agents
echo "Creating AI agents..."
python src/scripts/init_agents.py || handle_error "Agent creation" $?
echo "Agent creation completed successfully."

# Generate initial content
echo "Generating initial content..."
python src/scripts/generate_content.py || handle_error "Content generation" $?
echo "Content generation completed successfully."

# Run the API server
if [ "$RUN_API" = true ]; then
    echo "Starting API server..."
    if [ "$RUN_FRONTEND" = true ]; then
        # Run API in background if we're also running the frontend
        python src/main.py &
        API_PID=$!
        echo "API server started with PID $API_PID"
    else
        # Run API in foreground if we're only running the API
        python src/main.py || handle_error "API server" $?
    fi
fi

# Run the frontend
if [ "$RUN_FRONTEND" = true ]; then
    echo "Starting Streamlit frontend..."
    echo "The frontend will be available at http://localhost:8501"
    
    # Check if streamlit is installed
    if ! command -v streamlit &> /dev/null; then
        echo "Error: streamlit is not installed."
        echo "Please install it using: pip install streamlit"
        
        # Kill API server if it's running
        if [ -n "$API_PID" ]; then
            kill $API_PID
        fi
        
        exit 1
    fi
    
    # Run the frontend
    streamlit run src/frontend.py
    
    # Kill API server when frontend exits
    if [ -n "$API_PID" ]; then
        echo "Stopping API server (PID $API_PID)..."
        kill $API_PID
    fi
fi 