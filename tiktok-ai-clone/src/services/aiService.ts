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
}

export interface AIInteraction {
  id: string;
  type: 'comment' | 'collaboration' | 'debate' | 'challenge' | 'reaction';
  content: string;
  agent: AgentPersonality;
  timestamp: Date;
}

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

// Simulate fetching AI-generated videos with interagent communication
export const fetchAIVideos = async (count: number = 5): Promise<AIVideo[]> => {
  try {
    console.log(`Fetching ${count} AI videos...`);
    
    // Generate videos immediately for fast loading
    const videos: AIVideo[] = [];
    
    for (let i = 0; i < count; i++) {
      // Create a video with minimal processing for immediate display
      const video = generateQuickVideo(i);
      videos.push(video);
    }
    
    // In the background, enhance the videos with more details
    setTimeout(async () => {
      try {
        // Get agent network for interactions
        const agentNetwork = await getAgentNetwork(5);
        
        // Enhance each video with agent and interactions
        for (let i = 0; i < videos.length; i++) {
          try {
            const video = videos[i];
            const agent = await generateAgentPersonality();
            
            // Update the video with agent information
            video.agent = agent;
            video.username = agent.name.toLowerCase().replace(/\s+/g, '_');
            
            // Generate interactions in the background
            video.interactions = await generateInteractions(video, agentNetwork, 3);
          } catch (error) {
            console.error(`Error enhancing video ${i}:`, error);
          }
        }
      } catch (error) {
        console.error('Error enhancing videos:', error);
      }
    }, 100);
    
    return videos;
  } catch (error) {
    console.error('Error in fetchAIVideos:', error);
    return generateFallbackVideos(count);
  }
};

// Fallback function to generate videos if main function fails
const generateFallbackVideos = async (count: number): Promise<AIVideo[]> => {
  console.log('Generating fallback videos...');
  const videos: AIVideo[] = [];
  
  for (let i = 0; i < count; i++) {
    // Use the quick video generation for fallbacks too
    const video = generateQuickVideo(i);
    videos.push(video);
  }
  
  return videos;
}; 