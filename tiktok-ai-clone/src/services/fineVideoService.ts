import OpenAI from 'openai';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true, // Note: In production, API calls should be made from a backend
});

// Interface for FineVideo data
interface FineVideoData {
  mp4: Blob;
  json: {
    content_fine_category: string;
    content_parent_category: string;
    duration_seconds: number;
    youtube_title: string;
    content_metadata: {
      title: string;
      description: string;
      scenes: Array<{
        title: string;
        timestamps: {
          start_timestamp: string;
          end_timestamp: string;
        };
      }>;
    };
    video_path: string;
  };
}

// Function to fetch videos from the FineVideo dataset
export const fetchFineVideos = async (count: number = 5): Promise<FineVideoData[]> => {
  try {
    console.log(`Fetching ${count} videos from FineVideo dataset`);
    
    // Use local videos instead of trying to fetch from external sources
    try {
      console.log('Loading local video metadata...');
      const metadataResponse = await fetch('/assets/data/video_metadata.json');
      
      if (!metadataResponse.ok) {
        throw new Error(`Failed to fetch video metadata: ${metadataResponse.statusText}`);
      }
      
      const videoMetadata = await metadataResponse.json();
      console.log('Successfully loaded local video metadata:', videoMetadata);
      
      // Limit to requested count
      const selectedMetadata = videoMetadata.slice(0, count);
      
      // Create video objects directly without fetching
      const fineVideos: FineVideoData[] = [];
      
      for (let i = 0; i < selectedMetadata.length; i++) {
        const metadata = selectedMetadata[i];
        console.log(`Processing local video ${i + 1}/${selectedMetadata.length}: ${metadata.video_path}`);
        
        try {
          // Ensure the video path is correct
          const videoPath = `/assets/videos/video${i+1}.mp4`;
          
          // Create a FineVideoData object with the metadata
          fineVideos.push({
            mp4: new Blob(), // We'll use the URL directly instead of the blob
            json: {
              content_fine_category: metadata.content_fine_category,
              content_parent_category: metadata.content_parent_category,
              duration_seconds: metadata.duration_seconds,
              youtube_title: metadata.youtube_title,
              content_metadata: metadata.content_metadata,
              video_path: videoPath // Add the video path to the metadata
            }
          });
          
          console.log(`Successfully processed video ${i + 1}`);
        } catch (error) {
          console.error(`Error processing video ${i + 1}:`, error);
        }
      }
      
      if (fineVideos.length > 0) {
        return fineVideos;
      } else {
        throw new Error('Failed to load any local videos');
      }
    } catch (error) {
      console.error('Error loading local videos:', error);
      throw error;
    }
  } catch (error) {
    console.error('Error in fetchFineVideos:', error);
    return [];
  }
};

// Function to extract a frame from the middle of a video
export const extractVideoFrame = async (videoBlob: Blob): Promise<string> => {
  return new Promise((resolve, reject) => {
    try {
      // Create a video element to load the video
      const video = document.createElement('video');
      video.preload = 'metadata';
      video.muted = true; // Mute the video to avoid audio playing
      video.playsInline = true; // Better mobile support
      video.crossOrigin = 'anonymous'; // Handle CORS issues
      
      // Create object URL from blob
      const videoUrl = URL.createObjectURL(videoBlob);
      
      // Add event listeners before setting the src
      video.onloadedmetadata = () => {
        try {
          // Seek to the middle of the video (or 7.5 seconds for 15-second clips)
          const seekTime = Math.min(7.5, video.duration / 2);
          console.log(`Seeking to ${seekTime}s in video with duration ${video.duration}s`);
          video.currentTime = seekTime;
          
          video.onseeked = () => {
            try {
              // Create a canvas to draw the video frame
              const canvas = document.createElement('canvas');
              canvas.width = video.videoWidth || 640;  // Default to 640 if videoWidth is 0
              canvas.height = video.videoHeight || 360; // Default to 360 if videoHeight is 0
              
              console.log(`Drawing frame at time ${video.currentTime}s with dimensions ${canvas.width}x${canvas.height}`);
              
              // Draw the current frame to the canvas
              const ctx = canvas.getContext('2d');
              if (!ctx) {
                URL.revokeObjectURL(videoUrl);
                reject(new Error('Could not get canvas context'));
                return;
              }
              
              // Play the video briefly to ensure the frame is loaded
              video.play().then(() => {
                // Draw the frame after a short delay
                setTimeout(() => {
                  try {
                    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
                    video.pause();
                    
                    // Convert canvas to data URL (base64 image)
                    const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
                    
                    // Clean up
                    URL.revokeObjectURL(videoUrl);
                    
                    resolve(dataUrl);
                  } catch (drawError) {
                    console.error('Error drawing to canvas:', drawError);
                    URL.revokeObjectURL(videoUrl);
                    
                    // Return a placeholder image instead of failing
                    resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
                  }
                }, 100);
              }).catch(playError => {
                console.error('Error playing video:', playError);
                URL.revokeObjectURL(videoUrl);
                
                // Return a placeholder image instead of failing
                resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
              });
            } catch (error) {
              console.error('Error in onseeked:', error);
              URL.revokeObjectURL(videoUrl);
              
              // Return a placeholder image instead of failing
              resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
            }
          };
          
          video.onerror = (e) => {
            console.error('Error seeking video:', e);
            URL.revokeObjectURL(videoUrl);
            
            // Return a placeholder image instead of failing
            resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
          };
        } catch (error) {
          console.error('Error in onloadedmetadata:', error);
          URL.revokeObjectURL(videoUrl);
          
          // Return a placeholder image instead of failing
          resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
        }
      };
      
      video.onerror = (e) => {
        console.error('Error loading video:', e);
        URL.revokeObjectURL(videoUrl);
        
        // Return a placeholder image instead of failing
        resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
      };
      
      // Set the src after adding event listeners
      video.src = videoUrl;
      
      // Add a timeout to prevent hanging
      const timeout = setTimeout(() => {
        console.error('Timeout while loading video');
        URL.revokeObjectURL(videoUrl);
        
        // Return a placeholder image instead of failing
        resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
      }, 5000); // 5 second timeout (reduced from 10s)
      
      // Clear the timeout when the video is loaded
      video.onloadeddata = () => {
        clearTimeout(timeout);
      };
    } catch (error) {
      console.error('Error setting up video element:', error);
      
      // Return a placeholder image instead of failing
      resolve('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');
    }
  });
};

// Function to get a description from GPT-4o based on a video frame
export const getDescriptionFromFrame = async (
  frameDataUrl: string, 
  videoMetadata?: any
): Promise<string> => {
  try {
    // For development, we'll generate a description without calling the API
    // This is to avoid using up API credits during development
    console.log('Generating description for video frame...');
    
    // Extract base64 data from data URL
    const base64Image = frameDataUrl.split(',')[1];
    
    // In a production environment, you would call the OpenAI API here
    // For now, we'll generate a simple description based on the metadata
    
    const category = videoMetadata?.content_fine_category || 'Video';
    const descriptions = [
      `Vibing to the rhythm! This ${category.toLowerCase()} moment is everything 💯 #trending #${category.replace(/\s+/g, '')}`,
      `When the ${category.toLowerCase()} hits just right ✨ #viral #${category.replace(/\s+/g, '')}`,
      `POV: You're watching the best ${category.toLowerCase()} of 2024 🔥 #fyp #${category.replace(/\s+/g, '')}`,
      `This ${category.toLowerCase()} changed my life! No cap 🙌 #trending #viral`,
      `Main character energy in this ${category.toLowerCase()} 💫 #aesthetic #${category.replace(/\s+/g, '')}`
    ];
    
    const randomDescription = descriptions[Math.floor(Math.random() * descriptions.length)];
    
    // In production, you would use the OpenAI API like this:
    /*
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: 'You are a creative social media content writer. Your task is to write engaging, catchy descriptions for short video clips that will perform well on platforms like TikTok. Keep descriptions concise (max 150 characters), trendy, and include 2-3 relevant hashtags.'
        },
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: `Write a catchy, engaging description for this video clip that would perform well on TikTok. Keep it under 150 characters and include 2-3 relevant hashtags. ${contextPrompt}`
            },
            {
              type: 'image_url',
              image_url: {
                url: `data:image/jpeg;base64,${base64Image}`
              }
            }
          ]
        }
      ],
      temperature: 0.7,
    });

    return response.choices[0].message.content || 'Check out this amazing video! #trending #viral';
    */
    
    return randomDescription;
  } catch (error) {
    console.error('Error getting description from GPT-4o:', error);
    return 'Check out this amazing video! #trending #viral';
  }
};

// Function to trim a video blob to 15 seconds
export const trimVideoToFifteenSeconds = async (videoBlob: Blob): Promise<Blob> => {
  // In a real implementation, this would use a video processing library
  // For now, we'll just return the original blob
  // In production, you would use something like FFmpeg.wasm to trim the video
  console.log('Trimming video to 15 seconds (simulated)');
  return videoBlob;
};

// Function to process a FineVideo for use in the app
export const processFineVideo = async (videoData: FineVideoData): Promise<{
  videoBlob: Blob;
  description: string;
  metadata: any;
}> => {
  try {
    // Trim the video to 15 seconds
    const trimmedVideo = await trimVideoToFifteenSeconds(videoData.mp4);
    
    try {
      // Extract a frame from the middle of the video
      const frameDataUrl = await extractVideoFrame(trimmedVideo);
      
      // Get a description from GPT-4o
      const description = await getDescriptionFromFrame(frameDataUrl, videoData.json);
      
      return {
        videoBlob: trimmedVideo,
        description,
        metadata: videoData.json
      };
    } catch (frameError) {
      console.error('Error extracting frame or generating description:', frameError);
      
      // Fall back to a generic description if frame extraction fails
      return {
        videoBlob: trimmedVideo,
        description: `Check out this ${videoData.json.content_fine_category || 'amazing'} video! #trending #viral`,
        metadata: videoData.json
      };
    }
  } catch (error) {
    console.error('Error processing FineVideo:', error);
    
    // Return the original data with a generic description as a last resort
    return {
      videoBlob: videoData.mp4,
      description: `Amazing ${videoData.json.content_fine_category || ''} content! #mustwatch`,
      metadata: videoData.json
    };
  }
}; 