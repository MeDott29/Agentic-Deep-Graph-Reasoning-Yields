import { useState, useEffect, useRef, useCallback } from 'react';
import styled from '@emotion/styled';
import VideoCard from './VideoCard';
import { fetchAIVideos, AIVideo } from '../services/aiService';
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

  // Load initial videos - optimized for speed
  const loadInitialVideos = useCallback(async () => {
    try {
      setInitialLoading(true);
      setError(null);
      
      console.log('Loading initial videos...');
      
      // Preload a smaller batch of videos first for immediate display
      const initialVideos = await fetchAIVideos(2);
      
      if (initialVideos.length === 0) {
        console.warn('No videos were loaded. Showing error message to user.');
        throw new Error('No videos could be loaded. Please check that the local video files are available in the public/assets/videos directory.');
      }
      
      // Set videos immediately with the first batch
      setVideos(initialVideos);
      setActiveIndex(0);
      
      // Once the first batch is displayed, load more videos in the background
      setTimeout(async () => {
        try {
          const moreVideos = await fetchAIVideos(3);
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
      const newVideos = await fetchAIVideos(2);
      
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
      const index = Math.floor(scrollTop / videoHeight);
      
      if (index !== activeIndex && index >= 0 && index < videos.length) {
        setActiveIndex(index);
      }
    };

    const feedElement = feedRef.current;
    if (feedElement) {
      feedElement.addEventListener('scroll', handleScroll);
    }

    return () => {
      if (feedElement) {
        feedElement.removeEventListener('scroll', handleScroll);
      }
    };
  }, [activeIndex, videos.length]);

  // Handle retry when there's an error
  const handleRetry = () => {
    loadInitialVideos();
  };

  if (initialLoading) {
    return (
      <LoadingContainer>
        <div className="loading-spinner" />
        <LoadingText>{loadingMessage}</LoadingText>
      </LoadingContainer>
    );
  }

  if (error) {
    return (
      <ErrorContainer>
        <ErrorTitle>Something went wrong</ErrorTitle>
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
    <FeedContainer ref={feedRef}>
      {videos.map((video, index) => (
        <VideoCard 
          key={video.id} 
          video={video} 
          isActive={index === activeIndex}
        />
      ))}
      {hasMore && (
        <div ref={loaderRef} style={{ height: '20px', opacity: 0 }}>
          Loading more...
        </div>
      )}
    </FeedContainer>
  );
};

export default VideoFeed; 