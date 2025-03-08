// This service simulates AI-generated content for our TikTok clone
// In a real application, this would connect to an actual AI service
import { 
  AgentPersonality, 
  generateAgentPersonality, 
  generateContent, 
  simulateAgentInteraction, 
  generateAgentNetwork,
  agentRoles
} from './openaiService';

import {
  fetchFineVideos,
  processFineVideo,
  trimVideoToFifteenSeconds,
  extractVideoFrame,
  getDescriptionFromFrame
} from './fineVideoService';

import { ReasoningEngine } from './graphReasoning/reasoningEngine';
import { ContentGenerationPrompt } from './graphReasoning/types';

import OpenAI from 'openai';

// Types for our AI-generated content
export interface AIVideo {
  id: string;
  username: string;
  description: string;
  music: string;
  likes: number;
  comments: number;
  shares: number;
  videoUrl: string;
  userAvatar: string;
  agent?: AgentPersonality;
  interactions?: AIInteraction[];
  // New fields for FineVideo integration
  videoBlob?: Blob;
  category?: string;
  originalTitle?: string;
  priority?: 'high' | 'normal' | 'low';
  metadata?: {
    json?: any;
    scenes?: any[];
    duration?: number;
  };
  audioUrl?: string;
}

export interface AIInteraction {
  id: string;
  type: 'comment' | 'collaboration' | 'debate' | 'challenge' | 'reaction';
  content: string;
  agent: AgentPersonality;
  timestamp: Date;
}

// User behavior tracking interfaces
export interface UserBehavior {
  userId: string;
  sessionId: string;
  interactions: UserInteraction[];
  preferences: UserPreferences;
  lastUpdated: Date;
}

export interface UserInteraction {
  videoId: string;
  action: 'view' | 'like' | 'share' | 'comment' | 'follow' | 'skip';
  duration: number; // How long they watched in seconds
  timestamp: Date;
  metadata?: Record<string, any>;
}

export interface UserPreferences {
  categories: Record<string, number>; // Category name to weight mapping
  creators: Record<string, number>; // Creator username to weight mapping
  musicTypes: Record<string, number>; // Music type to weight mapping
  viewingTimes: Record<string, number>; // Time of day to weight mapping
  contentLength: 'short' | 'medium' | 'long';
  interactionLevel: 'passive' | 'moderate' | 'active';
}

// Initialize user behavior storage
let currentUserBehavior: UserBehavior = {
  userId: `user-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
  sessionId: `session-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`,
  interactions: [],
  preferences: {
    categories: {},
    creators: {},
    musicTypes: {},
    viewingTimes: {},
    contentLength: 'short',
    interactionLevel: 'passive'
  },
  lastUpdated: new Date()
};

// Sample video URLs (in a real app, these would be generated or fetched)
const sampleVideos = [
  'https://assets.mixkit.co/videos/preview/mixkit-woman-dancing-in-a-club-with-colorful-lights-3052-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-young-woman-dancing-happily-in-a-field-4702-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-young-woman-dancing-in-the-street-with-a-friend-39765-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-young-woman-dancing-in-the-street-39769-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-young-woman-dancing-in-the-street-with-a-friend-39765-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-man-dancing-to-music-playing-on-his-smartphone-42615-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-woman-dancing-with-shopping-bags-in-her-hands-42526-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-woman-dancing-with-a-pillow-in-her-hands-42520-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-urban-woman-dancing-in-the-street-42519-large.mp4',
  'https://assets.mixkit.co/videos/preview/mixkit-woman-dancing-with-a-pillow-in-her-hands-42520-large.mp4',
];

// Sample avatar URLs
const sampleAvatars = [
  '/assets/avatars/women1.jpg',
  '/assets/avatars/men1.jpg',
  '/assets/avatars/women2.jpg',
  '/assets/avatars/men2.jpg',
  '/assets/avatars/women3.jpg',
  '/assets/avatars/men3.jpg',
];

// Sample usernames
const sampleUsernames = [
  'ai_creator',
  'digital_artist',
  'virtual_influencer',
  'tech_trendsetter',
  'future_visionary',
  'creative_ai',
  'digital_dreamer',
  'ai_fashionista',
  'virtual_dancer',
  'tech_explorer',
];

// Sample music tracks
const sampleMusic = [
  'AI Beat - Virtual Producer',
  'Digital Dreams - AI Composer',
  'Neural Network Noise - AI DJ',
  'Synthetic Symphony - AI Orchestra',
  'Machine Learning Melody - AI Band',
  'Algorithm Anthem - Virtual Artist',
  'Data-Driven Beats - AI Producer',
  'Quantum Quirks - AI Musician',
  'Binary Bops - Digital Composer',
  'Artificial Acoustics - AI Sound',
];

// Sample video descriptions
const sampleDescriptions = [
  'Check out this AI-generated dance move! #AIcreator #digitalart',
  'This is what happens when AI learns to dance 💃 #virtualinfluencer',
  'AI-generated content is the future! What do you think? #techinnovation',
  'Would you believe this was created by AI? 🤖 #futureisnow',
  'AI creativity at its finest! 🎨 #digitalcreation',
  'When AI decides to join TikTok 😂 #AItrends',
  'The future of content creation is here! #AIrevolution',
  'AI-generated dance moves that will blow your mind! 🤯 #nextlevel',
  'This is what AI thinks is trending right now 😄 #virtualcontent',
  'AI trying to understand human dance moves be like... #AIlearning',
];

// Generate a random number between min and max
const getRandomNumber = (min: number, max: number): number => {
  return Math.floor(Math.random() * (max - min + 1)) + min;
};

// Get a random item from an array
const getRandomItem = <T>(array: T[]): T => {
  return array[Math.floor(Math.random() * array.length)];
};

// Cache for agent network to avoid regenerating for each request
let agentNetworkCache: AgentPersonality[] | null = null;

// Get or create agent network
const getAgentNetwork = async (count: number = 10): Promise<AgentPersonality[]> => {
  if (agentNetworkCache && agentNetworkCache.length >= count) {
    return agentNetworkCache.slice(0, count);
  }
  
  try {
    const network = await generateAgentNetwork(count);
    agentNetworkCache = network;
    return network;
  } catch (error) {
    console.error('Error generating agent network:', error);
    // Fallback to basic agents if API fails
    return Array(count).fill(null).map((_, i) => ({
      role: Object.values(agentRoles)[i % Object.values(agentRoles).length],
      name: `AI_Agent_${i}`,
      bio: `I'm an AI content creator`,
      interests: ['AI', 'content creation'],
      tone: 'friendly',
      quirks: ['loves emojis'],
    }));
  }
};

// Preload video paths for faster access
const localVideoPaths = [
  '/assets/videos/video1.mp4',
  '/assets/videos/video2.mp4',
  '/assets/videos/video3.mp4',
  '/assets/videos/video4.mp4',
  '/assets/videos/video5.mp4',
];

// Fast video generation without waiting for API calls
const generateQuickVideo = (index: number): AIVideo => {
  const videoPath = localVideoPaths[index % localVideoPaths.length];
  const username = getRandomItem(sampleUsernames);
  
  return {
    id: `video-${Date.now()}-${index}-${Math.random().toString(36).substring(2, 9)}`,
    username,
    description: `Check out this awesome video! #trending #viral`,
    music: getRandomItem(sampleMusic),
    likes: getRandomNumber(100, 10000),
    comments: getRandomNumber(10, 500),
    shares: getRandomNumber(5, 200),
    videoUrl: videoPath,
    userAvatar: getRandomItem(sampleAvatars),
    priority: index < 2 ? 'high' : 'normal',
  };
};

// Generate interactions for a video
const generateInteractions = async (video: AIVideo, agentNetwork: AgentPersonality[], count: number = 3): Promise<AIInteraction[]> => {
  if (!video.agent) return [];
  
  const interactions: AIInteraction[] = [];
  const interactionTypes = ['comment', 'collaboration', 'debate', 'challenge', 'reaction'] as const;
  
  for (let i = 0; i < count; i++) {
    // Select a random agent from the network that isn't the video creator
    const interactingAgents = agentNetwork.filter(agent => agent.name !== video.agent?.name);
    if (interactingAgents.length === 0) continue;
    
    const interactingAgent = getRandomItem(interactingAgents);
    const interactionType = getRandomItem(interactionTypes);
    
    try {
      let content;
      
      if (interactionType === 'comment') {
        // Generate a comment on the video
        content = await generateContent(interactingAgent, 'comment', video.description);
      } else {
        // Generate an interaction between the video creator and the interacting agent
        const topic = video.description.split(' ').slice(0, 5).join(' '); // Use part of the description as topic
        content = await simulateAgentInteraction(
          video.agent,
          interactingAgent,
          topic,
          interactionType
        );
      }
      
      interactions.push({
        id: `interaction-${Date.now()}-${i}`,
        type: interactionType,
        content,
        agent: interactingAgent,
        timestamp: new Date(),
      });
    } catch (error) {
      console.error(`Error generating ${interactionType}:`, error);
    }
  }
  
  return interactions;
};

// Track user interaction with a video
export const trackUserInteraction = (
  videoId: string, 
  action: UserInteraction['action'], 
  duration: number = 0,
  metadata?: Record<string, any>
): void => {
  const interaction: UserInteraction = {
    videoId,
    action,
    duration,
    timestamp: new Date(),
    metadata
  };
  
  currentUserBehavior.interactions.push(interaction);
  currentUserBehavior.lastUpdated = new Date();
  
  // Update user preferences based on this interaction
  updateUserPreferences(videoId, action, duration);
  
  // Save to localStorage for persistence
  saveUserBehavior();
  
  console.log(`Tracked user interaction: ${action} on video ${videoId} for ${duration}s`);
};

// Update user preferences based on interactions
const updateUserPreferences = (videoId: string, action: UserInteraction['action'], duration: number): void => {
  // Find the video in our cache
  const video = recentVideos.find(v => v.id === videoId);
  if (!video) return;
  
  const { preferences } = currentUserBehavior;
  
  // Update category preference
  if (video.category) {
    preferences.categories[video.category] = (preferences.categories[video.category] || 0) + getActionWeight(action);
  }
  
  // Update creator preference
  preferences.creators[video.username] = (preferences.creators[video.username] || 0) + getActionWeight(action);
  
  // Update music preference
  const musicType = video.music.split(' - ')[0];
  preferences.musicTypes[musicType] = (preferences.musicTypes[musicType] || 0) + getActionWeight(action);
  
  // Update viewing time preference
  const hour = new Date().getHours();
  const timeBlock = `${Math.floor(hour / 6) * 6}-${Math.floor(hour / 6) * 6 + 5}`;
  preferences.viewingTimes[timeBlock] = (preferences.viewingTimes[timeBlock] || 0) + 1;
  
  // Update content length preference
  if (duration > 0) {
    if (duration < 15) {
      preferences.contentLength = 'short';
    } else if (duration < 45) {
      preferences.contentLength = 'medium';
    } else {
      preferences.contentLength = 'long';
    }
  }
  
  // Update interaction level
  const recentInteractions = currentUserBehavior.interactions.slice(-20);
  const actionCount = recentInteractions.filter(i => i.action !== 'view').length;
  
  if (actionCount < 5) {
    preferences.interactionLevel = 'passive';
  } else if (actionCount < 10) {
    preferences.interactionLevel = 'moderate';
  } else {
    preferences.interactionLevel = 'active';
  }
};

// Get weight for different actions
const getActionWeight = (action: UserInteraction['action']): number => {
  switch (action) {
    case 'view': return 1;
    case 'like': return 3;
    case 'comment': return 5;
    case 'share': return 7;
    case 'follow': return 10;
    case 'skip': return -2;
    default: return 0;
  }
};

// Save user behavior to localStorage
const saveUserBehavior = (): void => {
  try {
    localStorage.setItem('userBehavior', JSON.stringify(currentUserBehavior));
  } catch (error) {
    console.error('Error saving user behavior:', error);
  }
};

// Load user behavior from localStorage
export const loadUserBehavior = (): UserBehavior => {
  try {
    const saved = localStorage.getItem('userBehavior');
    if (saved) {
      currentUserBehavior = JSON.parse(saved);
      // Ensure dates are properly parsed
      currentUserBehavior.lastUpdated = new Date(currentUserBehavior.lastUpdated);
      currentUserBehavior.interactions.forEach(interaction => {
        interaction.timestamp = new Date(interaction.timestamp);
      });
    }
  } catch (error) {
    console.error('Error loading user behavior:', error);
  }
  return currentUserBehavior;
};

// Get recommended videos based on user preferences
export const filterRecommendedVideos = (videos: AIVideo[], count: number = 5): AIVideo[] => {
  if (videos.length <= count) return videos;
  
  const { preferences } = currentUserBehavior;
  
  // Score each video based on user preferences
  const scoredVideos = videos.map(video => {
    let score = 0;
    
    // Category score
    if (video.category && preferences.categories[video.category]) {
      score += preferences.categories[video.category];
    }
    
    // Creator score
    if (preferences.creators[video.username]) {
      score += preferences.creators[video.username];
    }
    
    // Music score
    const musicType = video.music.split(' - ')[0];
    if (preferences.musicTypes[musicType]) {
      score += preferences.musicTypes[musicType];
    }
    
    return { video, score };
  });
  
  // Sort by score and return top videos
  return scoredVideos
    .sort((a, b) => b.score - a.score)
    .slice(0, count)
    .map(item => item.video);
};

// Cache for recent videos to use in preference calculations
let recentVideos: AIVideo[] = [];

// Simulate fetching AI-generated videos with interagent communication
export const fetchAIVideos = async (count: number = 5): Promise<AIVideo[]> => {
  try {
    console.log(`Fetching ${count} AI videos...`);
    
    // Try to fetch videos from FineVideo dataset first
    try {
      const fineVideos = await fetchFineVideos(count);
      
      if (fineVideos.length > 0) {
        console.log(`Successfully fetched ${fineVideos.length} videos from FineVideo dataset`);
        
        // Process each video
        const processedVideos = await Promise.all(
          fineVideos.map(async (videoData) => {
            try {
              const processed = await processFineVideo(videoData);
              
              // Create a unique ID for the video
              const id = `video-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
              
              // Create a URL for the video blob
              const videoUrl = videoData.json.video_path || URL.createObjectURL(processed.videoBlob);
              
              // Generate a random username
              const username = `creator_${Math.floor(Math.random() * 1000)}`;
              
              // Create an AI video object
              return {
                id,
                username,
                description: processed.description,
                music: `Original sound - ${username}`,
                likes: Math.floor(Math.random() * 10000),
                comments: Math.floor(Math.random() * 1000),
                shares: Math.floor(Math.random() * 500),
                videoUrl,
                userAvatar: getRandomItem(sampleAvatars),
                category: videoData.json.content_fine_category,
                originalTitle: videoData.json.youtube_title,
                metadata: processed.metadata,
                audioUrl: processed.audioUrl
              };
            } catch (error) {
              console.error('Error processing FineVideo:', error);
              return null;
            }
          })
        );
        
        // Filter out any null values
        const validVideos = processedVideos.filter(Boolean) as AIVideo[];
        
        if (validVideos.length > 0) {
          return validVideos;
        }
      }
    } catch (error) {
      console.error('Error fetching from FineVideo dataset:', error);
    }
    
    // Fall back to generating videos if FineVideo fetch fails
    console.log('Falling back to generated videos...');
    return generateFallbackVideos(count);
  } catch (error) {
    console.error('Error in fetchAIVideos:', error);
    return [];
  }
};

// Fallback function to generate videos if main function fails
const generateFallbackVideos = async (count: number): Promise<AIVideo[]> => {
  console.log(`Generating ${count} fallback videos...`);
  
  // Generate videos immediately for fast loading
  const videos: AIVideo[] = [];
  
  for (let i = 0; i < count; i++) {
    // Create a video with minimal processing for immediate display
    const video = generateQuickVideo(i);
    videos.push(video);
  }
  
  // Add videos to recent videos cache
  recentVideos = [...recentVideos, ...videos].slice(-50); // Keep last 50 videos
  
  // In the background, enhance the videos with more details
  setTimeout(async () => {
    try {
      // Get agent network for interactions
      const agentNetwork = await getAgentNetwork(5);
      
      // Enhance each video with agent and interactions
      for (let i = 0; i < videos.length; i++) {
        try {
          // Add an agent personality to the video
          videos[i].agent = getRandomItem(agentNetwork);
          
          // Generate interactions for the video
          videos[i].interactions = await generateInteractions(videos[i], agentNetwork);
        } catch (error) {
          console.error(`Error enhancing video ${i}:`, error);
        }
      }
    } catch (error) {
      console.error('Error in background video enhancement:', error);
    }
  }, 100);
  
  return videos;
};

// Initialize the reasoning engine
let reasoningEngine: ReasoningEngine | null = null;

// Get the reasoning engine instance
export const getReasoningEngine = (): ReasoningEngine => {
  if (!reasoningEngine) {
    reasoningEngine = ReasoningEngine.getInstance();
  }
  return reasoningEngine;
};

// Generate content using the reasoning engine
export const generateAIContent = async (
  topic?: string,
  style?: string,
  targetAudience?: string,
  format: 'video' | 'comment' | 'interaction' = 'video'
): Promise<string> => {
  const engine = getReasoningEngine();
  
  const prompt: ContentGenerationPrompt = {
    topic,
    style,
    targetAudience,
    format,
    length: 'short'
  };
  
  try {
    const result = await engine.generateContent(prompt);
    return result.content;
  } catch (error) {
    console.error('Error generating content:', error);
    return `Here's some content about ${topic || 'interesting topics'}!`;
  }
};

// Get recommended videos for a user
export const getRecommendedVideos = async (
  userId: string,
  count: number = 5
): Promise<AIVideo[]> => {
  try {
    const engine = getReasoningEngine();
    
    // Get recommendations from the reasoning engine
    const recommendations = await engine.getRecommendationsForUser(userId, count);
    
    // Get the actual video objects
    const videos: AIVideo[] = [];
    
    for (const recommendation of recommendations) {
      const videoNode = engine.getGraphStore().getNode(recommendation.videoId);
      
      if (videoNode) {
        // Convert graph node to AIVideo
        const video: AIVideo = {
          id: videoNode.id,
          username: videoNode.properties.creator || 'ai_creator',
          description: videoNode.properties.title || 'AI-generated content',
          music: videoNode.properties.music || 'AI Beat - Virtual Producer',
          likes: videoNode.properties.likes || getRandomNumber(100, 10000),
          comments: videoNode.properties.comments || getRandomNumber(10, 500),
          shares: videoNode.properties.shares || getRandomNumber(5, 200),
          videoUrl: videoNode.properties.videoUrl || getRandomItem(sampleVideos),
          userAvatar: videoNode.properties.userAvatar || getRandomItem(sampleAvatars),
          category: videoNode.properties.category,
          originalTitle: videoNode.properties.originalTitle,
          metadata: videoNode.properties.metadata,
          audioUrl: videoNode.properties.audioUrl
        };
        
        videos.push(video);
      }
    }
    
    // If we don't have enough videos, fetch more
    if (videos.length < count) {
      const additionalVideos = await fetchAIVideos(count - videos.length);
      videos.push(...additionalVideos);
    }
    
    return videos;
  } catch (error) {
    console.error('Error getting recommended videos:', error);
    return fetchAIVideos(count);
  }
};

// Process user interaction and update the graph
export const processUserInteraction = async (
  interaction: UserInteraction,
  video: AIVideo
): Promise<void> => {
  try {
    const engine = getReasoningEngine();
    
    // Update the graph with this interaction
    engine.getGraphStore().processUserInteraction(interaction, video);
    
    // Update user behavior
    trackUserInteraction(
      interaction.videoId,
      interaction.action,
      interaction.duration,
      interaction.metadata
    );
    
    console.log(`Processed user interaction in graph: ${interaction.action} on video ${interaction.videoId}`);
  } catch (error) {
    console.error('Error processing user interaction in graph:', error);
  }
};

// Dashboard analytics functions
export const getUserBehaviorStats = async (): Promise<any> => {
  try {
    // Load user behavior data
    const userBehavior = loadUserBehavior();
    
    // Calculate total users (in a real app, this would come from a database)
    const totalUsers = 1; // Just the current user in our demo
    
    // Calculate top categories
    const categoryCounts: Record<string, number> = {};
    
    // Count interactions by category
    userBehavior.interactions.forEach(interaction => {
      // Find the video
      const video = recentVideos.find(v => v.id === interaction.videoId);
      if (video && video.category) {
        categoryCounts[video.category] = (categoryCounts[video.category] || 0) + 1;
      }
    });
    
    // Convert to array and sort
    const topCategories = Object.entries(categoryCounts)
      .map(([category, count]) => ({ category, count }))
      .sort((a, b) => b.count - a.count)
      .slice(0, 5);
    
    // Get user preferences
    const preferences = userBehavior.preferences;
    
    return {
      totalUsers,
      topCategories,
      preferences,
      activeSessionCount: 1, // Just the current session in our demo
      lastUpdated: new Date()
    };
  } catch (error) {
    console.error('Error getting user behavior stats:', error);
    return {
      totalUsers: 0,
      topCategories: [],
      preferences: {},
      activeSessionCount: 0,
      lastUpdated: new Date()
    };
  }
};

export const getVideoStats = async (): Promise<any> => {
  try {
    // In a real app, this would query a database
    // For our demo, we'll use the recentVideos array
    
    // Add view counts to videos (simulated)
    const videosWithStats = recentVideos.map(video => {
      // Generate a random number of views between likes and likes*10
      const views = video.likes + Math.floor(Math.random() * video.likes * 9);
      
      return {
        ...video,
        views
      };
    });
    
    // Sort by views (descending)
    const topVideos = [...videosWithStats].sort((a, b) => (b.views || 0) - (a.views || 0)).slice(0, 10);
    
    // Calculate total videos
    const totalVideos = recentVideos.length;
    
    // Calculate videos by category
    const videosByCategory: Record<string, number> = {};
    recentVideos.forEach(video => {
      if (video.category) {
        videosByCategory[video.category] = (videosByCategory[video.category] || 0) + 1;
      }
    });
    
    return {
      totalVideos,
      topVideos,
      videosByCategory,
      lastUpdated: new Date()
    };
  } catch (error) {
    console.error('Error getting video stats:', error);
    return {
      totalVideos: 0,
      topVideos: [],
      videosByCategory: {},
      lastUpdated: new Date()
    };
  }
};

export const getInteractionStats = async (): Promise<any> => {
  try {
    // Load user behavior data
    const userBehavior = loadUserBehavior();
    
    // Calculate total interactions
    const totalInteractions = userBehavior.interactions.length;
    
    // Calculate interactions by type
    const interactionsByType: Record<string, number> = {};
    userBehavior.interactions.forEach(interaction => {
      interactionsByType[interaction.action] = (interactionsByType[interaction.action] || 0) + 1;
    });
    
    // Convert to array and sort
    const byType = Object.entries(interactionsByType)
      .map(([type, count]) => ({ type, count }))
      .sort((a, b) => b.count - a.count);
    
    // Calculate average watch time
    const viewInteractions = userBehavior.interactions.filter(i => i.action === 'view');
    const totalWatchTime = viewInteractions.reduce((sum, i) => sum + i.duration, 0);
    const averageWatchTime = viewInteractions.length > 0 ? totalWatchTime / viewInteractions.length : 0;
    
    // Get recent interactions (last 10)
    const recentInteractions = [...userBehavior.interactions]
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 10);
    
    return {
      totalInteractions,
      byType,
      averageWatchTime,
      recentInteractions,
      lastUpdated: new Date()
    };
  } catch (error) {
    console.error('Error getting interaction stats:', error);
    return {
      totalInteractions: 0,
      byType: [],
      averageWatchTime: 0,
      recentInteractions: [],
      lastUpdated: new Date()
    };
  }
}; 