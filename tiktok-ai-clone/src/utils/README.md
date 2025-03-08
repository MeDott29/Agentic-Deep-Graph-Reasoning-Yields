# Utils Directory

This directory contains utility functions and helper methods used throughout the application.

## Purpose

Utility functions are small, reusable pieces of code that perform common tasks. They are typically pure functions that don't have side effects and don't depend on the React component lifecycle.

## Available Utilities

### videoUtils.ts

Functions for working with video files:
- Extracting frames from videos
- Converting video formats
- Calculating video duration
- Generating video thumbnails

### formatUtils.ts

Functions for formatting data:
- Formatting numbers (e.g., 1000 → 1K)
- Formatting dates and times
- Formatting durations
- Truncating text with ellipsis

### apiUtils.ts

Utilities for working with APIs:
- Handling API errors
- Retrying failed requests
- Parsing API responses
- Managing API rate limits

### analyticsUtils.ts

Utilities for analytics and tracking:
- Generating unique identifiers
- Tracking user events
- Processing analytics data
- Formatting data for charts and graphs

## Best Practices

When working with utility functions:

1. **Keep functions pure**: Avoid side effects and make functions depend only on their inputs
2. **Use TypeScript**: Define proper types for inputs and outputs
3. **Write tests**: Unit test utility functions to ensure they work correctly
4. **Document usage**: Add JSDoc comments to describe how to use each function
5. **Export selectively**: Only export functions that are needed by other modules

## Usage Example

```tsx
import { formatNumber, formatDuration } from '../utils/formatUtils';

const VideoStats = ({ views, duration }) => {
  return (
    <div>
      <span>{formatNumber(views)} views</span>
      <span>{formatDuration(duration)}</span>
    </div>
  );
};
``` 