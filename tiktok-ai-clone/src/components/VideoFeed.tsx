import { useState, useEffect, useRef, useCallback } from 'react';
import styled from '@emotion/styled';
import VideoCard from './VideoCard';
import { fetchAIVideos, AIVideo, getRecommendedVideos, loadUserBehavior } from '../services/aiService';
import useInfiniteScroll from '../hooks/useInfiniteScroll';

const FeedContainer = styled.div`
  height: 100vh;
  overflow-y: scroll;
  scroll-snap-type: y mandatory;
  background-color: black;
`;

const LoadingContainer = styled.div`
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  flex-direction: column;
`;

const LoadingText = styled.p`
  margin-top: 16px;
  font-size: 16px;
`;

const ErrorContainer = styled.div`
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  color: white;
  flex-direction: column;
  padding: 20px;
  text-align: center;
`;

const ErrorTitle = styled.h2`
  margin-bottom: 16px;
  color: #ff4d4f;
`;

const ErrorMessage = styled.p`
  margin-bottom: 24px;
  max-width: 600px;
`;

const RetryButton = styled.button`
  background-color: var(--primary);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover {
    opacity: 0.9;
  }
`;

const VideoFeed = () => {
  const [videos, setVideos] = useState<AIVideo[]>([]);
  const [loading, setLoading] = useState(true);
  const [initialLoading, setInitialLoading] = useState(true);
  const [hasMore, setHasMore] = useState(true);
  const [activeIndex, setActiveIndex] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('Loading videos...');
  const [error, setError] = useState<string | null>(null);
  const [userProfile, setUserProfile] = useState<any>(null);
  const loaderRef = useRef<HTMLDivElement>(null);
  const feedRef = useRef<HTMLDivElement>(null);

  // Simplified loading messages
  const loadingMessages = [
    'Loading videos...',
    'Preparing your feed...',
    'Almost ready...',
  ];

  // Cycle through loading messages faster
  useEffect(() => {
    if (!initialLoading) return;

    const interval = setInterval(() => {
      setLoadingMessage(prev => {
        const currentIndex = loadingMessages.indexOf(prev);
        const nextIndex = (currentIndex + 1) % loadingMessages.length;
        return loadingMessages[nextIndex];
      });
    }, 800); // Faster message cycling

    return () => clearInterval(interval);
  }, [initialLoading]);

  // Load user profile on mount
  useEffect(() => {
    const userBehavior = loadUserBehavior();
    setUserProfile(userBehavior);
    
    console.log('Loaded user profile:', userBehavior);
  }, []);

  // Load initial videos - optimized for speed
  const loadInitialVideos = useCallback(async () => {
    try {
      setInitialLoading(true);
      setError(null);
      
      console.log('Loading initial videos...');
      
      // Load user behavior if not already loaded
      const userBehavior = loadUserBehavior();
      
      // Preload a smaller batch of videos first for immediate display
      let initialVideos: AIVideo[] = [];
      
      // If user has interactions, use recommendations
      if (userBehavior.interactions.length > 0) {
        console.log('Using recommendations based on user behavior');
        initialVideos = await getRecommendedVideos(userBehavior.userId, 5);
      } else {
        // Otherwise, fetch random videos
        console.log('Using random videos (no user behavior yet)');
        initialVideos = await fetchAIVideos(5);
      }
      
      if (initialVideos.length === 0) {
        console.warn('No videos were loaded. Showing error message to user.');
        throw new Error('No videos could be loaded. Please check that the local video files are available in the public/assets/videos directory.');
      }
      
      // Set videos immediately
      setVideos(initialVideos);
      setActiveIndex(0);
      
      // Once the first batch is displayed, load more videos in the background
      setTimeout(async () => {
        try {
          // If user has interactions, use recommendations
          let moreVideos: AIVideo[] = [];
          
          if (userBehavior.interactions.length > 0) {
            moreVideos = await getRecommendedVideos(userBehavior.userId, 5);
          } else {
            moreVideos = await fetchAIVideos(5);
          }
          
          setVideos(prevVideos => [...prevVideos, ...moreVideos]);
          console.log(`Loaded ${moreVideos.length} additional videos in the background`);
        } catch (error) {
          console.error('Error loading additional videos:', error);
          // Continue with the videos we already have
        }
      }, 100);
      
      console.log(`Successfully loaded initial videos`);
      
      // Set loading to false immediately after the first batch is ready
      setInitialLoading(false);
      setLoading(false);
      
    } catch (error) {
      console.error('Error fetching initial videos:', error);
      setError(error instanceof Error ? error.message : 'Failed to load videos. Please check that the local video files are available.');
      setInitialLoading(false);
      setLoading(false);
    }
  }, []);

  // Initial load - start immediately
  useEffect(() => {
    // Start loading videos immediately
    loadInitialVideos();
  }, [loadInitialVideos]);

  // Load more videos when scrolling
  const loadMoreVideos = useCallback(async () => {
    if (loading) return;
    
    setLoading(true);
    try {
      console.log('Loading more videos...');
      
      // Load user behavior
      const userBehavior = loadUserBehavior();
      
      // Get videos based on user behavior or random
      let newVideos: AIVideo[] = [];
      
      if (userBehavior.interactions.length > 0) {
        console.log('Loading more recommended videos');
        newVideos = await getRecommendedVideos(userBehavior.userId, 5);
      } else {
        console.log('Loading more random videos');
        newVideos = await fetchAIVideos(5);
      }
      
      if (newVideos.length > 0) {
        setVideos(prev => [...prev, ...newVideos]);
        setHasMore(true);
        console.log(`Successfully loaded ${newVideos.length} more videos`);
      } else {
        console.log('No more videos available');
        setHasMore(false);
      }
    } catch (error) {
      console.error('Error fetching more videos:', error);
      setHasMore(false);
    } finally {
      setLoading(false);
    }
  }, [loading]);

  // Set up infinite scroll
  useInfiniteScroll({
    loading,
    hasMore,
    onLoadMore: loadMoreVideos,
    targetRef: loaderRef,
  });

  // Track which video is currently visible
  useEffect(() => {
    const handleScroll = () => {
      if (!feedRef.current) return;
      
      const scrollTop = feedRef.current.scrollTop;
      const videoHeight = window.innerHeight;
      const index = Math.round(scrollTop / videoHeight); // Use Math.round instead of Math.floor for better accuracy
      
      if (index !== activeIndex && index >= 0 && index < videos.length) {
        console.log(`Changing active video from ${activeIndex} to ${index}`);
        setActiveIndex(index);
        
        // Force a small delay to ensure the DOM has updated
        setTimeout(() => {
          // Try to play the video directly
          const videoElement = document.querySelector(`#video-${index} video`) as HTMLVideoElement;
          if (videoElement) {
            console.log(`Found video element for index ${index}, attempting to play`);
            videoElement.play().catch(err => {
              console.warn(`Error auto-playing video ${index}:`, err);
              // Try playing muted if normal playback fails
              videoElement.muted = true;
              videoElement.play().catch(err2 => {
                console.error(`Failed to play video ${index} even when muted:`, err2);
              });
            });
          } else {
            console.warn(`Could not find video element for index ${index}`);
          }
        }, 50);
      }
    };

    // Add a more robust scroll detection
    const handleScrollEnd = () => {
      // This will be called when scrolling stops
      handleScroll();
    };

    // Add intersection observer for more reliable detection
    const observerOptions = {
      root: feedRef.current,
      rootMargin: '0px',
      threshold: 0.7, // 70% of the video must be visible
    };

    const videoObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const videoId = entry.target.id;
          const index = parseInt(videoId.replace('video-', ''));
          if (!isNaN(index) && index !== activeIndex) {
            console.log(`Intersection observer detected video ${index} is visible`);
            setActiveIndex(index);
          }
        }
      });
    }, observerOptions);

    // Observe all video elements
    videos.forEach((_, index) => {
      const element = document.getElementById(`video-${index}`);
      if (element) {
        videoObserver.observe(element);
      }
    });

    const feedElement = feedRef.current;
    if (feedElement) {
      feedElement.addEventListener('scroll', handleScroll);
      feedElement.addEventListener('scrollend', handleScrollEnd);
      // For browsers that don't support scrollend
      let scrollTimeout: number | null = null;
      feedElement.addEventListener('scroll', () => {
        if (scrollTimeout) {
          clearTimeout(scrollTimeout);
        }
        scrollTimeout = window.setTimeout(handleScrollEnd, 150);
      });
    }

    return () => {
      if (feedElement) {
        feedElement.removeEventListener('scroll', handleScroll);
        feedElement.removeEventListener('scrollend', handleScrollEnd);
      }
      // Disconnect observer
      videoObserver.disconnect();
    };
  }, [activeIndex, videos.length]);

  // Handle retry when there's an error
  const handleRetry = () => {
    loadInitialVideos();
  };

  // Render user profile summary if available
  const renderUserProfile = () => {
    if (!userProfile || userProfile.interactions.length === 0) return null;
    
    const { preferences } = userProfile;
    
    // Get top categories
    const topCategories = Object.entries(preferences.categories)
      .sort(([, a], [, b]) => (b as number) - (a as number))
      .slice(0, 3)
      .map(([category]) => category);
      
    // Get top creators
    const topCreators = Object.entries(preferences.creators)
      .sort(([, a], [, b]) => (b as number) - (a as number))
      .slice(0, 3)
      .map(([creator]) => creator);
    
    return (
      <div style={{
        position: 'absolute',
        top: '70px',
        right: '10px',
        background: 'rgba(0, 0, 0, 0.7)',
        color: 'white',
        padding: '10px',
        borderRadius: '8px',
        zIndex: 100,
        maxWidth: '250px',
        fontSize: '12px'
      }}>
        <h4 style={{ margin: '0 0 8px 0' }}>Your Profile</h4>
        <p style={{ margin: '4px 0' }}>Interactions: {userProfile.interactions.length}</p>
        {topCategories.length > 0 && (
          <p style={{ margin: '4px 0' }}>Top categories: {topCategories.join(', ')}</p>
        )}
        {topCreators.length > 0 && (
          <p style={{ margin: '4px 0' }}>Favorite creators: {topCreators.join(', ')}</p>
        )}
        <p style={{ margin: '4px 0' }}>Content length: {preferences.contentLength}</p>
        <p style={{ margin: '4px 0' }}>Interaction level: {preferences.interactionLevel}</p>
      </div>
    );
  };

  if (initialLoading) {
    return (
      <LoadingContainer>
        <div className="loader"></div>
        <LoadingText>{loadingMessage}</LoadingText>
      </LoadingContainer>
    );
  }

  if (error) {
    return (
      <ErrorContainer>
        <ErrorTitle>Oops! Something went wrong</ErrorTitle>
        <ErrorMessage>{error}</ErrorMessage>
        <RetryButton onClick={handleRetry}>Try Again</RetryButton>
      </ErrorContainer>
    );
  }

  if (videos.length === 0) {
    return (
      <ErrorContainer>
        <ErrorTitle>No videos available</ErrorTitle>
        <ErrorMessage>We couldn't load any videos at this time. This could be due to network issues or API limitations.</ErrorMessage>
        <RetryButton onClick={handleRetry}>Try Again</RetryButton>
      </ErrorContainer>
    );
  }

  return (
    <>
      {initialLoading ? (
        <LoadingContainer>
          <div className="loader"></div>
          <LoadingText>{loadingMessage}</LoadingText>
        </LoadingContainer>
      ) : error ? (
        <ErrorContainer>
          <ErrorTitle>Oops! Something went wrong</ErrorTitle>
          <ErrorMessage>{error}</ErrorMessage>
          <RetryButton onClick={handleRetry}>Try Again</RetryButton>
        </ErrorContainer>
      ) : (
        <FeedContainer ref={feedRef}>
          {videos.map((video, index) => (
            <VideoCard 
              key={video.id} 
              video={video} 
              isActive={index === activeIndex}
              id={`video-${index}`}
            />
          ))}
          {hasMore && !loading && (
            <div ref={loaderRef} style={{ height: '20px' }}></div>
          )}
          {loading && !initialLoading && (
            <div style={{ 
              height: '100px', 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              color: 'white'
            }}>
              Loading more videos...
            </div>
          )}
          {renderUserProfile()}
        </FeedContainer>
      )}
    </>
  );
};

export default VideoFeed; 