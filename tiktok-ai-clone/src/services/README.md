# Services Directory

This directory contains service modules that handle external API integrations and data processing.

## Service Modules

### aiService.ts

The AI service handles interactions with AI models for content generation:
- Generating video descriptions using OpenAI's GPT-4o
- Creating AI agent personalities for interactions
- Processing video frames for AI analysis

### fineVideoService.ts

The FineVideo service manages interactions with the Hugging Face FineVideo dataset:
- Fetching video metadata from the FineVideo API
- Processing video data for use in the application
- Handling fallback to local videos when API access fails

### openaiService.ts

The OpenAI service provides a wrapper for OpenAI API interactions:
- Managing API key and authentication
- Handling API requests and responses
- Implementing rate limiting and error handling
- Processing image and text inputs for the API

### analyticsService.ts

The Analytics service collects and processes usage data:
- Tracking user interactions and video views
- Aggregating metrics for the dashboard
- Generating reports and visualizations

## Usage Guidelines

When working with these services:

1. **Error Handling**: Always implement proper error handling and fallback mechanisms
2. **Rate Limiting**: Be mindful of API rate limits and implement appropriate throttling
3. **Caching**: Cache API responses when appropriate to reduce API calls
4. **Environment Variables**: Use environment variables for API keys and configuration
5. **Typing**: Define TypeScript interfaces for all API responses and service functions
6. **Testing**: Write unit tests for service functions to ensure reliability

## Adding New Services

When adding a new service:

1. Create a new file with a descriptive name (e.g., `newFeatureService.ts`)
2. Define clear interfaces for the service's input and output types
3. Implement error handling and logging
4. Document the service's functions with JSDoc comments
5. Export only what's necessary for other modules to use 