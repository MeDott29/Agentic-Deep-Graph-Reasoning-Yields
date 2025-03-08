# Source Code Directory

This directory contains all the source code for the TikTok AI Clone application.

## Directory Structure

- **assets/**: Static assets used in the application (icons, images, etc.)
- **components/**: Reusable UI components used throughout the application
- **hooks/**: Custom React hooks for shared functionality
- **pages/**: Page components for different routes in the application
- **services/**: API and service functions for external integrations
- **styles/**: Global styles and theme definitions
- **utils/**: Utility functions and helper methods
- **App.tsx**: Main application component that sets up routing
- **main.tsx**: Entry point of the application

## Key Components

### Video Feed

The video feed is the core of the application, providing an infinite scroll experience similar to TikTok. It uses the Intersection Observer API to detect when a user has scrolled to the bottom of the feed and automatically loads more content.

### Video Player

The video player component handles video playback, including autoplay when a video is scrolled into view and pausing when it's scrolled out of view. It also manages audio playback and provides controls for users to interact with the video.

### AI Integration

The application integrates with OpenAI's GPT-4o to generate engaging descriptions for videos. It extracts frames from videos and sends them to the API along with metadata to generate contextually relevant descriptions.

## Development Guidelines

When working with this codebase, follow these guidelines:

1. **Component Structure**: Keep components small and focused on a single responsibility
2. **State Management**: Use React hooks for local state and context for global state
3. **Styling**: Use Emotion for styling components with the CSS-in-JS approach
4. **TypeScript**: Use TypeScript types for all components and functions
5. **Error Handling**: Implement proper error handling for all API calls and async operations
6. **Performance**: Optimize for performance, especially for video playback and scrolling
7. **Accessibility**: Ensure all components are accessible and follow WCAG guidelines 