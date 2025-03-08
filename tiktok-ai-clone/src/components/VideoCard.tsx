import { useRef, useState, useEffect } from 'react';
import styled from '@emotion/styled';
import { AIVideo, AIInteraction, trackUserInteraction, processUserInteraction } from '../services/aiService';
import { motion, AnimatePresence } from 'framer-motion';
import React from 'react';
import { checkVideoHasAudio, fixAudioPlayback, playVideoWithAudio, addAudioToVideo } from '../utils/audioFix';

interface VideoCardProps {
  video: AIVideo;
  isActive: boolean;
  id?: string;
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

const VideoCard: React.FC<VideoCardProps> = ({ video, isActive, id }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [showInteractions, setShowInteractions] = useState(false);
  const [videoError, setVideoError] = useState(false);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const [watchDuration, setWatchDuration] = useState(0);
  const [watchStartTime, setWatchStartTime] = useState<number | null>(null);
  const [audioEnabled, setAudioEnabled] = useState(true);
  const [hasAudio, setHasAudio] = useState<boolean | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Preload video when component mounts
  useEffect(() => {
    if (videoRef.current) {
      // Set preload attribute to auto
      videoRef.current.preload = 'auto';
      
      // Try to load the video immediately
      videoRef.current.load();
    }
  }, []);

  // Check if video has audio after it loads
  useEffect(() => {
    if (videoLoaded && videoRef.current) {
      checkVideoHasAudio(videoRef.current)
        .then(hasAudioTrack => {
          setHasAudio(hasAudioTrack);
          console.log(`Video ${video.id} has audio: ${hasAudioTrack}`);
          
          // If video doesn't have audio and we have timecoded_text_to_speech in metadata, try to extract audio
          if (!hasAudioTrack && video.metadata && video.metadata.json) {
            try {
              const jsonData = typeof video.metadata.json === 'string' 
                ? JSON.parse(video.metadata.json) 
                : video.metadata.json;
              
              // Check if this is a FineVideo dataset video with audio
              if (jsonData.text_to_speech || jsonData.timecoded_text_to_speech) {
                console.log(`FineVideo dataset detected for video ${video.id}, attempting to extract audio`);
                
                // If there's an audio URL in the metadata, use it
                if (video.audioUrl) {
                  addAudioToVideo(videoRef.current, video.audioUrl);
                  console.log(`Added audio track from metadata to video ${video.id}`);
                } else {
                  // Use a default audio track from assets as fallback
                  const audioTrack = `/assets/audio/background${Math.floor(Math.random() * 5) + 1}.mp3`;
                  addAudioToVideo(videoRef.current, audioTrack);
                  console.log(`Added background audio track to video ${video.id}`);
                }
              }
            } catch (error) {
              console.error('Error parsing video metadata:', error);
            }
          } else if (!hasAudioTrack) {
            // Use a default audio track from assets
            const audioTrack = `/assets/audio/background${Math.floor(Math.random() * 5) + 1}.mp3`;
            addAudioToVideo(videoRef.current, audioTrack);
            console.log(`Added background audio track to video ${video.id}`);
          }
        })
        .catch(error => {
          console.error('Error checking for audio:', error);
          setHasAudio(false);
        });
    }
  }, [videoLoaded, video]);

  // Handle video playback when active
  useEffect(() => {
    let playAttemptTimeout: number | null = null;
    
    if (isActive && videoRef.current) {
      // Reset watch duration when video becomes active
      setWatchDuration(0);
      setWatchStartTime(Date.now());
      
      // Track that user is viewing this video
      trackUserInteraction(video.id, 'view');
      
      // Also update the graph with this interaction
      processUserInteraction(
        {
          videoId: video.id,
          action: 'view',
          timestamp: new Date(),
          duration: 0, // Will be updated when video becomes inactive
          metadata: { started: true }
        },
        video
      );
      
      // Attempt to play the video
      const attemptPlay = async () => {
        if (videoRef.current) {
          try {
            // Fix any audio playback issues
            fixAudioPlayback(videoRef.current);
            
            // Ensure volume is set (fix for audio issues)
            videoRef.current.volume = audioEnabled ? 1.0 : 0.0;
            videoRef.current.muted = !audioEnabled;
            
            // Play the video with audio, falling back to muted if necessary
            console.log(`Attempting to play video ${video.id}`);
            await playVideoWithAudio(videoRef.current);
            setIsPlaying(true);
            console.log(`Successfully playing video ${video.id}`);
          } catch (error) {
            console.error('Error playing video:', error);
            
            // Try again with muted
            try {
              console.log(`Retrying with muted video ${video.id}`);
              videoRef.current.muted = true;
              await videoRef.current.play();
              setIsPlaying(true);
              console.log(`Successfully playing muted video ${video.id}`);
            } catch (mutedError) {
              console.error('Error playing even with muted:', mutedError);
              setVideoError(true);
            }
          }
        }
      };
      
      // Try to play immediately if video is loaded
      if (videoLoaded) {
        attemptPlay();
      } else {
        // Set a timeout to try playing after a short delay
        playAttemptTimeout = window.setTimeout(() => {
          attemptPlay();
        }, 300);
        
        // Add a longer timeout as a fallback
        const fallbackTimeout = window.setTimeout(() => {
          if (!isPlaying && videoRef.current) {
            console.log(`Fallback timeout: attempting to play video ${video.id} again`);
            attemptPlay();
          }
        }, 1000);
        
        return () => {
          if (fallbackTimeout) clearTimeout(fallbackTimeout);
        };
      }
    } else if (!isActive && videoRef.current) {
      // Pause the video when not active
      videoRef.current.pause();
      setIsPlaying(false);
      
      // Calculate and track watch duration when video becomes inactive
      if (watchStartTime !== null) {
        const duration = Math.floor((Date.now() - watchStartTime) / 1000);
        setWatchDuration(duration);
        
        // Track view with duration
        trackUserInteraction(video.id, 'view', duration);
        
        // Also update the graph with this interaction
        processUserInteraction(
          {
            videoId: video.id,
            action: 'view',
            timestamp: new Date(),
            duration,
            metadata: { completed: duration > 0 }
          },
          video
        );
        
        // Reset watch start time
        setWatchStartTime(null);
      }
    }
    
    return () => {
      if (playAttemptTimeout) {
        clearTimeout(playAttemptTimeout);
      }
    };
  }, [isActive, videoLoaded, video, audioEnabled, isPlaying]);

  // Handle video errors
  const handleVideoError = (e: React.SyntheticEvent<HTMLVideoElement, Event>) => {
    console.error('Video error:', e);
    setVideoError(true);
    trackUserInteraction(video.id, 'skip', 0, { reason: 'error' });
  };

  // Handle video loaded
  const handleVideoLoaded = () => {
    console.log('Video loaded successfully');
    setVideoLoaded(true);
    setVideoError(false);
  };

  // Handle video ended
  const handleVideoEnded = () => {
    console.log('Video playback ended');
    if (videoRef.current) {
      // Loop the video
      videoRef.current.currentTime = 0;
      videoRef.current.play().catch(error => {
        console.error('Error replaying video:', error);
      });
    }
  };

  // Toggle play/pause
  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
        setIsPlaying(false);
        
        // Track pause action
        if (watchStartTime !== null) {
          const duration = Math.floor((Date.now() - watchStartTime) / 1000);
          trackUserInteraction(video.id, 'view', duration, { paused: true });
          setWatchStartTime(null);
        }
      } else {
        videoRef.current.play()
          .then(() => {
            setIsPlaying(true);
            setWatchStartTime(Date.now());
          })
          .catch(error => {
            console.error('Error playing video:', error);
          });
      }
    }
  };

  // Toggle audio
  const toggleAudio = () => {
    if (videoRef.current) {
      const newAudioEnabled = !audioEnabled;
      setAudioEnabled(newAudioEnabled);
      
      // Update video element
      videoRef.current.muted = !newAudioEnabled;
      videoRef.current.volume = newAudioEnabled ? 1.0 : 0.0;
      
      // Track user preference
      trackUserInteraction(video.id, newAudioEnabled ? 'unmute' : 'mute');
      
      // Show feedback
      console.log(`Audio ${newAudioEnabled ? 'enabled' : 'disabled'} for video ${video.id}`);
    }
  };

  // Toggle interactions panel
  const toggleInteractions = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowInteractions(!showInteractions);
    
    // Track interaction panel toggle
    trackUserInteraction(
      video.id, 
      'view', 
      0, 
      { showInteractions: !showInteractions }
    );
  };

  // Handle like action
  const handleLike = (e: React.MouseEvent) => {
    e.stopPropagation();
    // In a real app, this would call an API to like the video
    console.log('Liked video:', video.id);
    
    // Track like action
    trackUserInteraction(video.id, 'like');
    
    // Also update the graph with this interaction
    processUserInteraction(
      {
        videoId: video.id,
        action: 'like',
        timestamp: new Date(),
        metadata: { liked: true }
      },
      video
    );
  };

  // Handle comment action
  const handleComment = (e: React.MouseEvent) => {
    e.stopPropagation();
    // In a real app, this would open a comment modal
    console.log('Comment on video:', video.id);
    
    // Track comment action
    trackUserInteraction(video.id, 'comment');
    
    // Also update the graph with this interaction
    processUserInteraction(
      {
        videoId: video.id,
        action: 'comment',
        timestamp: new Date(),
        metadata: { commented: true }
      },
      video
    );
  };

  // Handle share action
  const handleShare = (e: React.MouseEvent) => {
    e.stopPropagation();
    // In a real app, this would open a share modal
    console.log('Share video:', video.id);
    
    // Track share action
    trackUserInteraction(video.id, 'share');
    
    // Also update the graph with this interaction
    processUserInteraction(
      {
        videoId: video.id,
        action: 'share',
        timestamp: new Date(),
        metadata: { shared: true }
      },
      video
    );
  };

  // Handle follow action
  const handleFollow = (e: React.MouseEvent) => {
    e.stopPropagation();
    // In a real app, this would call an API to follow the creator
    console.log('Follow creator:', video.username);
    
    // Track follow action
    trackUserInteraction(video.id, 'follow', 0, { creator: video.username });
    
    // Also update the graph with this interaction
    processUserInteraction(
      {
        videoId: video.id,
        action: 'follow',
        timestamp: new Date(),
        metadata: { creator: video.username }
      },
      video
    );
  };

  return (
    <CardContainer id={id}>
      {videoError ? (
        <div style={{ color: 'white', textAlign: 'center', padding: '20px' }}>
          <p>Error loading video</p>
          <button onClick={(e) => {
            e.stopPropagation();
            if (videoRef.current) {
              videoRef.current.load();
              setVideoError(false);
            }
          }}>
            Retry
          </button>
        </div>
      ) : (
        <VideoElement
          ref={videoRef}
          src={video.videoUrl}
          loop
          playsInline
          preload="auto"
          onError={handleVideoError}
          onLoadedData={handleVideoLoaded}
          onEnded={handleVideoEnded}
          onClick={togglePlayPause}
        />
      )}
      
      <VideoOverlay>
        <UserInfo>
          <Avatar src={video.userAvatar} alt={video.username} />
          <div>
            <Username>@{video.username}</Username>
            {video.agent && <AgentBio>{video.agent.bio}</AgentBio>}
          </div>
          <button 
            style={{ 
              marginLeft: 'auto', 
              background: 'var(--primary)', 
              color: 'white',
              border: 'none',
              padding: '8px 16px',
              borderRadius: '4px',
              cursor: 'pointer'
            }}
            onClick={handleFollow}
          >
            Follow
          </button>
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
            {video.originalTitle && <OriginalTitle>Original: {video.originalTitle}</OriginalTitle>}
          </VideoMetadata>
        )}
      </VideoOverlay>
      
      <ActionsContainer>
        <ActionButton onClick={handleLike}>
          <ActionIcon>❤️</ActionIcon>
          <ActionCount>{formatCount(video.likes)}</ActionCount>
        </ActionButton>
        <ActionButton onClick={handleComment}>
          <ActionIcon>💬</ActionIcon>
          <ActionCount>{formatCount(video.comments)}</ActionCount>
        </ActionButton>
        <ActionButton onClick={handleShare}>
          <ActionIcon>↗️</ActionIcon>
          <ActionCount>{formatCount(video.shares)}</ActionCount>
        </ActionButton>
        
        {video.interactions && video.interactions.length > 0 && (
          <InteractionsButton onClick={toggleInteractions}>
            <ActionIcon>🤖</ActionIcon>
            <ActionCount>{video.interactions.length}</ActionCount>
            <InteractionsBadge>{video.interactions.length}</InteractionsBadge>
          </InteractionsButton>
        )}
        <ActionButton onClick={toggleAudio}>
          <ActionIcon>{audioEnabled ? '🔊' : '🔇'}</ActionIcon>
          <ActionCount>{audioEnabled ? 'Mute' : 'Unmute'}</ActionCount>
        </ActionButton>
        
        {hasAudio === false && (
          <div style={{
            position: 'absolute',
            bottom: '-30px',
            right: '0',
            color: 'white',
            fontSize: '10px',
            backgroundColor: 'rgba(0,0,0,0.5)',
            padding: '2px 5px',
            borderRadius: '3px'
          }}>
            Using background audio
          </div>
        )}
      </ActionsContainer>
      
      <AnimatePresence>
        {showInteractions && video.interactions && (
          <InteractionsPanel
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 20 }}
            transition={{ duration: 0.2 }}
          >
            {video.interactions.map((interaction) => (
              <InteractionItem key={interaction.id}>
                <InteractionHeader>
                  <InteractionAvatar src={getRandomAvatar(interaction.agent.name)} alt={interaction.agent.name} />
                  <InteractionUsername>@{interaction.agent.name.toLowerCase().replace(/\s+/g, '_')}</InteractionUsername>
                  <InteractionType>{interaction.type}</InteractionType>
                </InteractionHeader>
                <InteractionContent>{interaction.content}</InteractionContent>
              </InteractionItem>
            ))}
          </InteractionsPanel>
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