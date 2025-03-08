# Components Directory

This directory contains reusable UI components used throughout the application.

## Component Structure

Each component typically follows this structure:
- A main component file (e.g., `VideoPlayer.tsx`)
- A styles file for component-specific styling (e.g., `VideoPlayer.styles.ts`)
- Optional subcomponents in a subdirectory (e.g., `VideoPlayer/Controls.tsx`)

## Key Components

### VideoPlayer

The VideoPlayer component is responsible for playing videos in the feed. It handles:
- Autoplay when scrolled into view
- Pausing when scrolled out of view
- Audio playback control
- Video progress tracking
- User interactions (play/pause, volume, etc.)

### VideoFeed

The VideoFeed component renders the infinite scrolling feed of videos. It:
- Loads videos from the API
- Implements infinite scroll using Intersection Observer
- Manages the active video state
- Handles loading states and errors

### VideoDescription

The VideoDescription component displays AI-generated descriptions for videos. It:
- Renders the description text with proper formatting
- Shows user information (AI-generated profiles)
- Displays video metadata (views, likes, etc.)
- Provides interaction buttons (like, comment, share)

### Dashboard Components

The Dashboard directory contains components used in the analytics dashboard:
- Charts and graphs for visualizing data
- Stat cards for displaying key metrics
- Filter controls for customizing the dashboard view

## Best Practices

When creating new components:

1. **Keep components focused**: Each component should have a single responsibility
2. **Use TypeScript**: Define proper types for props and state
3. **Implement error handling**: Handle edge cases and loading states
4. **Make components responsive**: Ensure they work on all screen sizes
5. **Follow accessibility guidelines**: Use semantic HTML and ARIA attributes
6. **Optimize performance**: Memoize expensive calculations and prevent unnecessary re-renders
7. **Document props**: Add JSDoc comments to describe component props 