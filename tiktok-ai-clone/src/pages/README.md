# Pages Directory

This directory contains top-level page components that correspond to different routes in the application.

## Page Structure

Each page is typically organized as a directory containing:
- A main component file (e.g., `Home/index.tsx`)
- Page-specific components (e.g., `Home/VideoFeed.tsx`)
- Page-specific styles (e.g., `Home/Home.styles.ts`)

## Available Pages

### Home

The Home page is the main landing page of the application, featuring:
- The infinite scrolling video feed
- Video player with autoplay functionality
- AI-generated video descriptions
- Interaction buttons (like, comment, share)

### Dashboard

The Dashboard page provides analytics and insights about the platform:
- User engagement metrics
- Video performance statistics
- Content trends and patterns
- Interactive charts and visualizations
- Filtering and date range selection

## Routing

Pages are connected to routes in the `App.tsx` file using React Router. Each page component is loaded when the user navigates to its corresponding route.

## State Management

Pages can manage their own state using React hooks, but should delegate complex state management to custom hooks or context providers when appropriate.

## Best Practices

When creating or modifying pages:

1. **Keep page components focused**: Pages should primarily compose other components rather than implementing complex logic
2. **Implement proper loading states**: Show loading indicators while data is being fetched
3. **Handle errors gracefully**: Display user-friendly error messages when things go wrong
4. **Optimize for performance**: Implement code splitting and lazy loading for better performance
5. **Maintain responsive design**: Ensure pages work well on all screen sizes
6. **Follow accessibility guidelines**: Make sure pages are accessible to all users 