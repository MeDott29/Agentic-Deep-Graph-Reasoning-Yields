/**
 * Utility functions to help with audio playback issues
 */

/**
 * Checks if a video has an audio track
 * @param videoElement The HTML video element to check
 * @returns Promise that resolves to true if the video has audio, false otherwise
 */
export const checkVideoHasAudio = async (videoElement: HTMLVideoElement): Promise<boolean> => {
  return new Promise((resolve) => {
    // If the video is already loaded, check immediately
    if (videoElement.readyState >= 2) {
      resolve(hasAudioTrack(videoElement));
    } else {
      // Otherwise, wait for the video to load enough data
      const handleLoadedData = () => {
        videoElement.removeEventListener('loadeddata', handleLoadedData);
        resolve(hasAudioTrack(videoElement));
      };
      
      videoElement.addEventListener('loadeddata', handleLoadedData);
    }
  });
};

/**
 * Checks if a video element has an audio track
 * @param videoElement The HTML video element to check
 * @returns true if the video has audio, false otherwise
 */
const hasAudioTrack = (videoElement: HTMLVideoElement): boolean => {
  // Try to get audio tracks from the video element
  if (videoElement.mozHasAudio !== undefined) {
    // Firefox
    return videoElement.mozHasAudio;
  } else if (videoElement.webkitAudioDecodedByteCount !== undefined) {
    // Chrome and Safari
    return videoElement.webkitAudioDecodedByteCount > 0;
  } else if (videoElement.audioTracks !== undefined) {
    // Standard
    return videoElement.audioTracks.length > 0;
  }
  
  // If we can't determine, assume it has audio
  return true;
};

/**
 * Attempts to fix audio playback issues by ensuring proper initialization
 * @param videoElement The HTML video element to fix
 */
export const fixAudioPlayback = (videoElement: HTMLVideoElement): void => {
  // Ensure volume is set to a non-zero value
  videoElement.volume = 1.0;
  
  // Ensure muted is false
  videoElement.muted = false;
  
  // Set playsinline attribute to prevent fullscreen on iOS
  videoElement.setAttribute('playsinline', 'true');
  
  // Set crossorigin attribute to allow CORS audio
  videoElement.setAttribute('crossorigin', 'anonymous');
  
  // Force a reload of the video to reinitialize audio
  const currentTime = videoElement.currentTime;
  const src = videoElement.src;
  
  videoElement.pause();
  videoElement.src = '';
  videoElement.load();
  videoElement.src = src;
  videoElement.load();
  
  // Restore playback position
  videoElement.currentTime = currentTime;
};

/**
 * Attempts to play a video with audio, falling back to muted if necessary
 * @param videoElement The HTML video element to play
 * @returns Promise that resolves when playback starts, or rejects if it fails
 */
export const playVideoWithAudio = async (videoElement: HTMLVideoElement): Promise<void> => {
  try {
    // First try to play with audio
    await videoElement.play();
    console.log('Video playing with audio');
  } catch (error) {
    console.warn('Failed to play with audio, trying muted:', error);
    
    // If that fails, try muted
    videoElement.muted = true;
    try {
      await videoElement.play();
      console.log('Video playing muted');
      
      // Add a click handler to unmute on user interaction
      const handleUserInteraction = () => {
        videoElement.muted = false;
        document.removeEventListener('click', handleUserInteraction);
      };
      
      document.addEventListener('click', handleUserInteraction);
    } catch (secondError) {
      console.error('Failed to play even with muted audio:', secondError);
      throw secondError;
    }
  }
};

/**
 * Adds an audio track to a video that doesn't have one
 * @param videoElement The HTML video element to add audio to
 * @param audioUrl URL of the audio file to add
 */
export const addAudioToVideo = (videoElement: HTMLVideoElement, audioUrl: string): void => {
  // Create an audio element
  const audioElement = document.createElement('audio');
  audioElement.src = audioUrl;
  audioElement.loop = true;
  
  // Sync audio with video
  videoElement.addEventListener('play', () => {
    audioElement.currentTime = videoElement.currentTime;
    audioElement.play().catch(error => {
      console.error('Error playing audio:', error);
    });
  });
  
  videoElement.addEventListener('pause', () => {
    audioElement.pause();
  });
  
  videoElement.addEventListener('seeked', () => {
    audioElement.currentTime = videoElement.currentTime;
  });
  
  videoElement.addEventListener('ended', () => {
    audioElement.pause();
  });
  
  // Clean up when video is removed
  videoElement.addEventListener('emptied', () => {
    audioElement.pause();
    audioElement.src = '';
  });
}; 