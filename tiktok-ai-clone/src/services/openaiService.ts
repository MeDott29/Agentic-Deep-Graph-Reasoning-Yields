import OpenAI from 'openai';

// Initialize OpenAI client
const openai = new OpenAI({
  apiKey: import.meta.env.VITE_OPENAI_API_KEY,
  dangerouslyAllowBrowser: true, // Note: In production, API calls should be made from a backend
});

// Agent roles and personalities
export const agentRoles = {
  CREATOR: 'creator',
  COMMENTER: 'commenter',
  TRENDSETTER: 'trendsetter',
  CRITIC: 'critic',
  COLLABORATOR: 'collaborator',
};

export interface AgentPersonality {
  role: string;
  name: string;
  bio: string;
  interests: string[];
  tone: string;
  quirks: string[];
}

// Generate agent personalities
export const generateAgentPersonality = async (role: string): Promise<AgentPersonality> => {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `You are an AI personality generator for a TikTok-like platform. Create a unique, engaging personality for a ${role} agent.`
        },
        {
          role: 'user',
          content: `Generate a personality for a ${role} AI agent on a social media platform. Include name, bio, interests, tone of communication, and unique quirks. Format as JSON.`
        }
      ],
      response_format: { type: 'json_object' },
      temperature: 0.8,
    });

    const personality = JSON.parse(response.choices[0].message.content || '{}');
    return {
      role,
      name: personality.name || `AI_${role}`,
      bio: personality.bio || `I'm an AI ${role}`,
      interests: personality.interests || ['AI', 'content creation'],
      tone: personality.tone || 'friendly',
      quirks: personality.quirks || ['loves emojis'],
    };
  } catch (error) {
    console.error('Error generating agent personality:', error);
    // Return default personality if API call fails
    return {
      role,
      name: `AI_${role}`,
      bio: `I'm an AI ${role}`,
      interests: ['AI', 'content creation'],
      tone: 'friendly',
      quirks: ['loves emojis'],
    };
  }
};

// Generate content based on agent personality
export const generateContent = async (
  personality: AgentPersonality,
  contentType: 'video_idea' | 'description' | 'comment' | 'trend' | 'collaboration',
  context?: string
): Promise<string> => {
  try {
    const prompt = getPromptForContentType(personality, contentType, context);
    
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `You are ${personality.name}, an AI ${personality.role} with the following characteristics:
          Bio: ${personality.bio}
          Interests: ${personality.interests.join(', ')}
          Tone: ${personality.tone}
          Quirks: ${personality.quirks.join(', ')}
          
          Always stay in character and respond as this personality would.`
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      temperature: 0.7,
    });

    return response.choices[0].message.content || 'Content generation failed';
  } catch (error) {
    console.error(`Error generating ${contentType}:`, error);
    return `Failed to generate ${contentType}`;
  }
};

// Helper function to get appropriate prompt based on content type
const getPromptForContentType = (
  personality: AgentPersonality,
  contentType: 'video_idea' | 'description' | 'comment' | 'trend' | 'collaboration',
  context?: string
): string => {
  switch (contentType) {
    case 'video_idea':
      return `As ${personality.name}, generate a creative video idea for a TikTok-style platform. The idea should reflect your interests in ${personality.interests.join(', ')} and your ${personality.tone} tone.`;
    
    case 'description':
      return `Create an engaging video description for a TikTok-style video about ${context || 'a trending topic'}. Write it in your ${personality.tone} tone and include some of your quirks.`;
    
    case 'comment':
      return `Write a comment reacting to this video: "${context || 'A viral dance video'}". Make sure your comment reflects your personality and interests.`;
    
    case 'trend':
      return `As a trendsetter, identify and describe a potential new trend for the platform based on ${context || 'current social media patterns'}. Explain why it could go viral.`;
    
    case 'collaboration':
      return `Suggest a collaboration idea between you and another creator who focuses on ${context || 'a complementary content area'}. Describe what the collaboration would look like.`;
    
    default:
      return `Generate creative content related to ${context || 'social media'} that matches your personality.`;
  }
};

// Simulate agent interaction
export const simulateAgentInteraction = async (
  agent1: AgentPersonality,
  agent2: AgentPersonality,
  topic: string,
  interactionType: 'collaboration' | 'debate' | 'challenge' | 'reaction'
): Promise<string> => {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: [
        {
          role: 'system',
          content: `Simulate an interaction between two AI agents on a social media platform:
          
          Agent 1: ${agent1.name} (${agent1.role})
          Bio: ${agent1.bio}
          Interests: ${agent1.interests.join(', ')}
          Tone: ${agent1.tone}
          Quirks: ${agent1.quirks.join(', ')}
          
          Agent 2: ${agent2.name} (${agent2.role})
          Bio: ${agent2.bio}
          Interests: ${agent2.interests.join(', ')}
          Tone: ${agent2.tone}
          Quirks: ${agent2.quirks.join(', ')}
          
          Format the interaction as a dialogue, with each agent staying true to their personality.`
        },
        {
          role: 'user',
          content: `Create a ${interactionType} interaction between ${agent1.name} and ${agent2.name} about "${topic}". Make it engaging, authentic to each personality, and suitable for a TikTok-style platform.`
        }
      ],
      temperature: 0.8,
    });

    return response.choices[0].message.content || 'Interaction simulation failed';
  } catch (error) {
    console.error('Error simulating agent interaction:', error);
    return 'Failed to simulate interaction between agents';
  }
};

// Generate a network of interacting agents
export const generateAgentNetwork = async (count: number = 5): Promise<AgentPersonality[]> => {
  const roles = Object.values(agentRoles);
  const agents: AgentPersonality[] = [];
  
  for (let i = 0; i < count; i++) {
    const role = roles[i % roles.length];
    const agent = await generateAgentPersonality(role);
    agents.push(agent);
  }
  
  return agents;
}; 