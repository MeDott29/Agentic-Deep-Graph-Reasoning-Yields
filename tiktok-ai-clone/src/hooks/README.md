# Hooks Directory

This directory contains custom React hooks used throughout the application.

## What are React Hooks?

React hooks are functions that let you "hook into" React state and lifecycle features from function components. They allow you to use state and other React features without writing a class.

## Available Hooks

### useVideoPlayer

A hook for managing video player functionality:
- Play/pause control
- Volume control
- Progress tracking
- Autoplay when in view
- Audio management

### useInfiniteScroll

A hook that implements infinite scrolling functionality:
- Detects when the user has scrolled to the bottom of the content
- Triggers loading of more content
- Manages loading states
- Handles error cases

### useVideoVisibility

A hook that tracks whether a video is visible in the viewport:
- Uses Intersection Observer API
- Triggers autoplay when a video becomes visible
- Pauses videos when they're scrolled out of view

### useAnalytics

A hook for tracking user interactions and video engagement:
- Records video views and watch time
- Tracks user interactions (likes, comments, shares)
- Sends data to the analytics service

## Creating New Hooks

When creating new hooks:

1. **Keep hooks focused**: Each hook should have a single responsibility
2. **Use TypeScript**: Define proper types for inputs and outputs
3. **Handle cleanup**: Implement cleanup functions to prevent memory leaks
4. **Document usage**: Add JSDoc comments to describe how to use the hook
5. **Follow naming conventions**: Hook names should start with "use"

## Usage Example

```tsx
import { useVideoPlayer } from '../hooks/useVideoPlayer';

const VideoComponent = ({ src }) => {
  const { 
    playing, 
    progress, 
    volume, 
    togglePlay, 
    handleVolumeChange, 
    videoRef 
  } = useVideoPlayer();

  return (
    <div>
      <video ref={videoRef} src={src} />
      <button onClick={togglePlay}>
        {playing ? 'Pause' : 'Play'}
      </button>
      <input 
        type="range" 
        min="0" 
        max="1" 
        step="0.1" 
        value={volume} 
        onChange={handleVolumeChange} 
      />
      <progress value={progress} max="100" />
    </div>
  );
};
``` 