import { useRef, useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { AIVideo, AIInteraction } from '../services/aiService';
import { motion, AnimatePresence } from 'framer-motion';
import React from 'react';

interface VideoCardProps {
  video: AIVideo;
  isActive: boolean;
}

const CardContainer = styled.div`
  height: 100vh;
  width: 100%;
  position: relative;
  scroll-snap-align: start;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: black;
`;

const VideoElement = styled.video`
  height: 100%;
  width: 100%;
  object-fit: cover;
`;

const VideoOverlay = styled.div`
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 20px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.7));
  color: white;
`;

const UserInfo = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 12px;
`;

const Avatar = styled.img`
  width: 48px;
  height: 48px;
  border-radius: 50%;
  margin-right: 12px;
  border: 2px solid white;
`;

const Username = styled.h3`
  font-size: 16px;
  font-weight: 600;
  margin: 0;
`;

const Description = styled.p`
  font-size: 14px;
  margin: 8px 0;
`;

const MusicInfo = styled.div`
  display: flex;
  align-items: center;
  font-size: 14px;
  margin-top: 8px;
`;

const MusicIcon = styled.span`
  margin-right: 8px;
`;

const ActionsContainer = styled.div`
  position: absolute;
  right: 16px;
  bottom: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
`;

const ActionButton = styled.button`
  display: flex;
  flex-direction: column;
  align-items: center;
  color: white;
  background: none;
  border: none;
  cursor: pointer;
`;

const ActionIcon = styled.div`
  font-size: 28px;
  margin-bottom: 4px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(255, 255, 255, 0.1);
  border-radius: 50%;
`;

const ActionCount = styled.span`
  font-size: 12px;
`;

// New components for agent interactions
const InteractionsButton = styled(ActionButton)`
  position: relative;
`;

const InteractionsBadge = styled.div`
  position: absolute;
  top: -5px;
  right: -5px;
  background-color: var(--primary);
  color: white;
  font-size: 10px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const InteractionsPanel = styled(motion.div)`
  position: absolute;
  right: 70px;
  bottom: 100px;
  width: 300px;
  max-height: 400px;
  background-color: rgba(0, 0, 0, 0.8);
  border-radius: 12px;
  padding: 16px;
  overflow-y: auto;
  color: white;
  backdrop-filter: blur(10px);
  z-index: 10;
`;

const InteractionItem = styled.div`
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  
  &:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }
`;

const InteractionHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 8px;
`;

const InteractionAvatar = styled.img`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  margin-right: 8px;
`;

const InteractionUsername = styled.span`
  font-weight: 600;
  font-size: 14px;
`;

const InteractionType = styled.span`
  font-size: 12px;
  color: var(--secondary);
  margin-left: 8px;
  text-transform: capitalize;
`;

const InteractionContent = styled.p`
  font-size: 14px;
  line-height: 1.4;
  margin: 0;
`;

const AgentBio = styled.div`
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
  margin-top: 4px;
  font-style: italic;
`;

// Add new styled components for FineVideo metadata
const VideoMetadata = styled.div`
  display: flex;
  align-items: center;
  margin-top: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
`;

const CategoryTag = styled.span`
  background-color: rgba(255, 255, 255, 0.2);
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 8px;
`;

const OriginalTitle = styled.span`
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 200px;
`;

// Helper function to format numbers (e.g., 1.2K, 1.5M)
const formatCount = (count: number): string => {
  if (count >= 1000000) {
    return `${(count / 1000000).toFixed(1)}M`;
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}K`;
  }
  return count.toString();
};

const VideoCard: React.FC<VideoCardProps> = ({ video, isActive }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showInteractions, setShowInteractions] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const [videoLoaded, setVideoLoaded] = useState(false);

  // Preload video when component mounts
  useEffect(() => {
    if (videoRef.current) {
      // Set preload attribute to auto
      videoRef.current.preload = 'auto';
      
      // Try to load the video immediately
      videoRef.current.load();
    }
  }, []);

  // Handle video playback when active
  useEffect(() => {
    let playAttemptTimeout: number | null = null;
    
    const attemptPlay = () => {
      if (!videoRef.current || !isActive) return;
      
      // Cancel any previous play attempts
      if (playAttemptTimeout) {
        window.clearTimeout(playAttemptTimeout);
        playAttemptTimeout = null;
      }
      
      const playPromise = videoRef.current.play();
      
      if (playPromise !== undefined) {
        playPromise
          .then(() => {
            setIsPlaying(true);
          })
          .catch(error => {
            console.error(`Error playing video: ${error.message}`);
            setIsPlaying(false);
            
            // Try again after a short delay, but only if still active
            if (isActive) {
              playAttemptTimeout = window.setTimeout(() => {
                if (videoRef.current && isActive) {
                  attemptPlay();
                }
              }, 500);
            }
          });
      }
    };
    
    if (isActive && videoLoaded) {
      attemptPlay();
    } else if (videoRef.current) {
      // Pause when not active
      videoRef.current.pause();
      setIsPlaying(false);
    }
    
    // Cleanup function
    return () => {
      if (playAttemptTimeout) {
        window.clearTimeout(playAttemptTimeout);
      }
    };
  }, [isActive, videoLoaded]);

  // Handle video loading errors
  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    console.error(`Error loading video: ${video.videoUrl}`);
    setVideoError(true);
  };

  // Handle video loaded successfully
  const handleVideoLoaded = () => {
    setVideoLoaded(true);
    setVideoError(false);
    
    // Try to play immediately if this is the active video
    if (isActive && videoRef.current) {
      videoRef.current.play().catch(error => {
        console.error('Error playing after load:', error.message);
      });
    }
  };

  // Toggle play/pause
  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setIsPlaying(false);
      } else {
        const playPromise = videoRef.current.play();
        
        if (playPromise !== undefined) {
          playPromise
            .then(() => {
              setIsPlaying(true);
            })
            .catch(error => {
              console.error(`Error playing video: ${error.message}`);
              setIsPlaying(false);
            });
        }
      }
    }
  };

  // Toggle interactions panel
  const toggleInteractions = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowInteractions(!showInteractions);
  };

  return (
    <CardContainer onClick={togglePlayPause}>
      {videoError ? (
        <div style={{ 
          color: 'white', 
          display: 'flex', 
          flexDirection: 'column', 
          alignItems: 'center', 
          justifyContent: 'center',
          height: '100%',
          padding: '20px',
          textAlign: 'center',
          backgroundColor: '#111'
        }}>
          <h3>Video could not be loaded</h3>
          <p>There was an error loading this video.</p>
        </div>
      ) : (
        <VideoElement
          ref={videoRef}
          src={video.videoUrl}
          loop
          playsInline
          muted
          preload="auto"
          autoPlay={isActive}
          onError={handleVideoError}
          onLoadedData={handleVideoLoaded}
        />
      )}
      
      <VideoOverlay>
        <UserInfo>
          <Avatar src={video.userAvatar} alt={video.username} />
          <div>
            <Username>@{video.username}</Username>
            {video.agent && <div style={{ fontSize: '12px' }}>{video.agent.role}</div>}
          </div>
        </UserInfo>
        <Description>{video.description}</Description>
        <MusicInfo>
          <MusicIcon>♪</MusicIcon>
          {video.music}
        </MusicInfo>
        
        {/* Display FineVideo metadata if available */}
        {(video.category || video.originalTitle) && (
          <VideoMetadata>
            {video.category && <CategoryTag>{video.category}</CategoryTag>}
            {video.originalTitle && <OriginalTitle>Source: {video.originalTitle}</OriginalTitle>}
          </VideoMetadata>
        )}
      </VideoOverlay>
      
      <ActionsContainer>
        <ActionButton>
          <ActionIcon>❤️</ActionIcon>
          {formatCount(video.likes)}
        </ActionButton>
        <ActionButton onClick={toggleInteractions}>
          <ActionIcon>💬</ActionIcon>
          {formatCount(video.comments)}
        </ActionButton>
        <ActionButton>
          <ActionIcon>↪️</ActionIcon>
          {formatCount(video.shares)}
        </ActionButton>
        
        {video.interactions && video.interactions.length > 0 && (
          <InteractionsButton onClick={toggleInteractions}>
            <ActionIcon>🤖</ActionIcon>
            <ActionCount>AI</ActionCount>
            <InteractionsBadge>{video.interactions.length}</InteractionsBadge>
          </InteractionsButton>
        )}
      </ActionsContainer>
      
      <AnimatePresence>
        {showInteractions && (
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 20 }}
            style={{
              position: 'absolute',
              top: 0,
              right: 0,
              bottom: 0,
              width: '80%',
              backgroundColor: 'rgba(0, 0, 0, 0.9)',
              padding: '20px',
              overflowY: 'auto',
              zIndex: 10,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h3>AI Interactions</h3>
            {video.interactions.map((interaction) => (
              <InteractionItem key={interaction.id}>
                <InteractionHeader>
                  <InteractionAvatar 
                    src={getRandomAvatar(interaction.agent.name)} 
                    alt={interaction.agent.name} 
                  />
                  <InteractionUsername>@{interaction.agent.name}</InteractionUsername>
                  <InteractionType>{interaction.type}</InteractionType>
                </InteractionHeader>
                <InteractionContent>{interaction.content}</InteractionContent>
              </InteractionItem>
            ))}
          </motion.div>
        )}
      </AnimatePresence>
    </CardContainer>
  );
};

// Helper function to generate consistent avatars based on agent name
const getRandomAvatar = (name: string): string => {
  // Use the first character of the name to determine gender
  const firstChar = name.charCodeAt(0) % 2;
  // Use the sum of character codes to determine avatar number (1-8)
  const sum = name.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % 8 + 1;
  return `/assets/avatars/${firstChar === 0 ? 'women' : 'men'}${sum}.jpg`;
};

// Memoize the VideoCard component to prevent unnecessary re-renders
export default React.memo(VideoCard, (prevProps, nextProps) => {
  // Only re-render if isActive changes or if the video ID changes
  return prevProps.isActive === nextProps.isActive && 
         prevProps.video.id === nextProps.video.id;
}); 