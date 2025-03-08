/**
 * Content Generator - Generates AI content based on graph insights
 */

import { GraphStore } from './graphStore';
import { 
  ContentGenerationPrompt, 
  ContentGenerationResult,
  NodeType,
  EdgeType,
  GraphNode
} from './types';
import OpenAI from 'openai';

/**
 * Content Generator class
 */
export class ContentGenerator {
  private graphStore: GraphStore;
  private openai: OpenAI;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
    
    // Initialize OpenAI client
    this.openai = new OpenAI({
      apiKey: import.meta.env.VITE_OPENAI_API_KEY,
      dangerouslyAllowBrowser: true, // Note: In production, API calls should be made from a backend
    });
  }

  /**
   * Generate content based on a prompt
   */
  public async generateContent(
    prompt: ContentGenerationPrompt, 
    count: number = 1
  ): Promise<ContentGenerationResult[]> {
    console.log(`Generating ${count} content items with prompt:`, prompt);
    
    // Enrich prompt with graph insights
    const enrichedPrompt = await this.enrichPromptWithGraphInsights(prompt);
    
    // Generate content using OpenAI
    const results: ContentGenerationResult[] = [];
    
    for (let i = 0; i < count; i++) {
      try {
        const result = await this.generateSingleContent(enrichedPrompt);
        results.push(result);
      } catch (error) {
        console.error('Error generating content:', error);
        // Continue with next item
      }
    }
    
    console.log(`Generated ${results.length} content items`);
    return results;
  }

  /**
   * Enrich a prompt with insights from the graph
   */
  private async enrichPromptWithGraphInsights(prompt: ContentGenerationPrompt): Promise<ContentGenerationPrompt> {
    const enrichedPrompt = { ...prompt };
    
    // 1. Find related topics
    if (prompt.topic) {
      const relatedTopics = await this.findRelatedTopics(prompt.topic);
      enrichedPrompt.relatedContent = [
        ...(enrichedPrompt.relatedContent || []),
        ...relatedTopics
      ];
    }
    
    // 2. Find trending topics if no specific topic is provided
    if (!prompt.topic) {
      const trendingTopics = await this.findTrendingTopics();
      if (trendingTopics.length > 0) {
        enrichedPrompt.topic = trendingTopics[0];
        enrichedPrompt.relatedContent = [
          ...(enrichedPrompt.relatedContent || []),
          ...trendingTopics.slice(1)
        ];
      }
    }
    
    // 3. Find popular content for inspiration
    const popularContent = await this.findPopularContent(prompt.topic);
    enrichedPrompt.inspirations = [
      ...(enrichedPrompt.inspirations || []),
      ...popularContent
    ];
    
    return enrichedPrompt;
  }

  /**
   * Generate a single content item
   */
  private async generateSingleContent(prompt: ContentGenerationPrompt): Promise<ContentGenerationResult> {
    // Construct a prompt for the OpenAI API
    const promptText = this.constructPromptText(prompt);
    
    try {
      // Call OpenAI API
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: 'You are a creative content generator for a TikTok-like platform. Generate engaging, authentic content that feels natural and appealing to the target audience.'
          },
          {
            role: 'user',
            content: promptText
          }
        ],
        temperature: 0.8,
        max_tokens: 500
      });
      
      // Extract content from response
      const content = response.choices[0]?.message?.content || '';
      
      // Extract metadata using a second API call
      const metadata = await this.extractMetadata(content, prompt);
      
      // Calculate predicted engagement
      const predictedEngagement = await this.calculatePredictedEngagement(content, metadata, prompt);
      
      return {
        content,
        metadata,
        relatedTopics: metadata.relatedTopics || [],
        targetAudience: metadata.targetAudience || [],
        predictedEngagement
      };
    } catch (error) {
      console.error('Error calling OpenAI API:', error);
      
      // Return fallback content
      return this.generateFallbackContent(prompt);
    }
  }

  /**
   * Construct a text prompt for the OpenAI API
   */
  private constructPromptText(prompt: ContentGenerationPrompt): string {
    let promptText = 'Generate ';
    
    // Add format
    if (prompt.format) {
      promptText += `a ${prompt.format} `;
    } else {
      promptText += 'content ';
    }
    
    // Add topic
    if (prompt.topic) {
      promptText += `about ${prompt.topic} `;
    }
    
    // Add style
    if (prompt.style) {
      promptText += `in a ${prompt.style} style `;
    }
    
    // Add target audience
    if (prompt.targetAudience) {
      promptText += `for ${prompt.targetAudience} `;
    }
    
    // Add related content
    if (prompt.relatedContent && prompt.relatedContent.length > 0) {
      promptText += `\nRelated topics: ${prompt.relatedContent.join(', ')} `;
    }
    
    // Add inspirations
    if (prompt.inspirations && prompt.inspirations.length > 0) {
      promptText += `\nInspired by: ${prompt.inspirations.join(', ')} `;
    }
    
    // Add constraints
    if (prompt.constraints && prompt.constraints.length > 0) {
      promptText += `\nConstraints: ${prompt.constraints.join(', ')} `;
    }
    
    // Add length
    if (prompt.length) {
      promptText += `\nLength: ${prompt.length} `;
    }
    
    // Add final instructions based on format
    if (prompt.format === 'video') {
      promptText += '\n\nGenerate a script for a short video that includes a hook, main content, and call to action.';
    } else if (prompt.format === 'comment') {
      promptText += '\n\nGenerate an engaging comment that adds value to the conversation.';
    } else if (prompt.format === 'interaction') {
      promptText += '\n\nGenerate an interaction between two users that feels authentic and engaging.';
    }
    
    return promptText;
  }

  /**
   * Extract metadata from generated content
   */
  private async extractMetadata(content: string, prompt: ContentGenerationPrompt): Promise<Record<string, any>> {
    try {
      // Call OpenAI API to extract metadata
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4o',
        messages: [
          {
            role: 'system',
            content: 'Extract metadata from the content. Return a JSON object with the following fields: keywords, emotions, relatedTopics, targetAudience, contentType, and contentLength.'
          },
          {
            role: 'user',
            content: `Content: ${content}\n\nExtract metadata as JSON.`
          }
        ],
        temperature: 0.2,
        max_tokens: 500,
        response_format: { type: 'json_object' }
      });
      
      // Parse JSON response
      const metadataText = response.choices[0]?.message?.content || '{}';
      const metadata = JSON.parse(metadataText);
      
      return metadata;
    } catch (error) {
      console.error('Error extracting metadata:', error);
      
      // Return basic metadata
      return {
        keywords: prompt.topic ? [prompt.topic] : [],
        emotions: [],
        relatedTopics: prompt.relatedContent || [],
        targetAudience: prompt.targetAudience ? [prompt.targetAudience] : [],
        contentType: prompt.format || 'general',
        contentLength: prompt.length || 'medium'
      };
    }
  }

  /**
   * Calculate predicted engagement for content
   */
  private async calculatePredictedEngagement(
    content: string, 
    metadata: Record<string, any>, 
    prompt: ContentGenerationPrompt
  ): Promise<number> {
    // Start with a base engagement score
    let engagement = 0.5;
    
    // Adjust based on content length
    const contentLength = content.length;
    if (contentLength < 50) {
      engagement -= 0.1; // Too short
    } else if (contentLength > 500) {
      engagement -= 0.1; // Too long
    } else if (contentLength > 100 && contentLength < 300) {
      engagement += 0.1; // Optimal length
    }
    
    // Adjust based on keywords count
    const keywords = metadata.keywords || [];
    if (keywords.length > 5) {
      engagement += 0.1; // Good keyword diversity
    }
    
    // Adjust based on emotions
    const emotions = metadata.emotions || [];
    if (emotions.includes('joy') || emotions.includes('surprise') || emotions.includes('awe')) {
      engagement += 0.1; // Positive emotions tend to engage more
    }
    
    // Adjust based on topic popularity
    if (prompt.topic) {
      const topicPopularity = await this.getTopicPopularity(prompt.topic);
      engagement += topicPopularity * 0.2;
    }
    
    // Ensure engagement is between 0 and 1
    return Math.max(0, Math.min(1, engagement));
  }

  /**
   * Generate fallback content when API calls fail
   */
  private generateFallbackContent(prompt: ContentGenerationPrompt): ContentGenerationResult {
    const topic = prompt.topic || 'general content';
    const format = prompt.format || 'content';
    
    let content = '';
    
    switch (format) {
      case 'video':
        content = `Here's a quick video about ${topic}! Check out these amazing facts and let me know what you think in the comments. Don't forget to like and follow for more content like this!`;
        break;
      case 'comment':
        content = `This is such interesting content about ${topic}! I've been following this for a while and it's amazing to see how things evolve. Thanks for sharing!`;
        break;
      case 'interaction':
        content = `User1: Have you seen the latest trends in ${topic}?\nUser2: Yes! I'm really excited about how it's developing. What do you think about it?\nUser1: I think it has a lot of potential, especially with the recent developments.`;
        break;
      default:
        content = `Here's some interesting content about ${topic}. Hope you find it useful and engaging!`;
    }
    
    return {
      content,
      metadata: {
        keywords: [topic],
        contentType: format
      },
      relatedTopics: [],
      targetAudience: [],
      predictedEngagement: 0.3 // Low engagement for fallback content
    };
  }

  /**
   * Find related topics in the graph
   */
  private async findRelatedTopics(topic: string): Promise<string[]> {
    // Find topic node
    const topicNodes = this.graphStore.getNodesByType(NodeType.TOPIC)
      .filter(node => 
        node.properties.name.toLowerCase().includes(topic.toLowerCase())
      );
    
    if (topicNodes.length === 0) {
      return [];
    }
    
    const topicNode = topicNodes[0];
    
    // Find related topics
    const relatedTopics: string[] = [];
    
    // Get neighbors connected by RELATED_TO edges
    const neighbors = this.graphStore.getNeighbors(topicNode.id, EdgeType.RELATED_TO);
    
    neighbors.forEach(neighbor => {
      if (neighbor.type === NodeType.TOPIC && neighbor.properties.name) {
        relatedTopics.push(neighbor.properties.name);
      }
    });
    
    return relatedTopics;
  }

  /**
   * Find trending topics in the graph
   */
  private async findTrendingTopics(): Promise<string[]> {
    // Get all topic nodes
    const topicNodes = this.graphStore.getNodesByType(NodeType.TOPIC);
    
    // Count references to each topic
    const topicCounts: Record<string, number> = {};
    
    topicNodes.forEach(topic => {
      const topicName = topic.properties.name;
      if (!topicName) return;
      
      // Count incoming edges
      const incomingEdges = this.graphStore.getIncomingEdges(topic.id);
      topicCounts[topicName] = incomingEdges.length;
    });
    
    // Sort topics by count
    const sortedTopics = Object.entries(topicCounts)
      .sort(([, countA], [, countB]) => countB - countA)
      .map(([name]) => name);
    
    return sortedTopics.slice(0, 5); // Return top 5 trending topics
  }

  /**
   * Find popular content related to a topic
   */
  private async findPopularContent(topic?: string): Promise<string[]> {
    // Get all video nodes
    let videoNodes = this.graphStore.getNodesByType(NodeType.VIDEO);
    
    // Filter by topic if provided
    if (topic) {
      videoNodes = videoNodes.filter(video => {
        const videoTitle = video.properties.title || '';
        return videoTitle.toLowerCase().includes(topic.toLowerCase());
      });
    }
    
    // Count views for each video
    const videoCounts = videoNodes.map(video => {
      const incomingEdges = this.graphStore.getIncomingEdges(video.id)
        .filter(edge => edge.type === EdgeType.VIEWED);
      
      return {
        videoId: video.id,
        title: video.properties.title || '',
        viewCount: incomingEdges.length
      };
    });
    
    // Sort by view count
    const popularVideos = videoCounts
      .sort((a, b) => b.viewCount - a.viewCount)
      .slice(0, 5); // Top 5 popular videos
    
    return popularVideos.map(video => video.title);
  }

  /**
   * Get popularity score for a topic
   */
  private async getTopicPopularity(topic: string): Promise<number> {
    // Find topic node
    const topicNodes = this.graphStore.getNodesByType(NodeType.TOPIC)
      .filter(node => 
        node.properties.name.toLowerCase().includes(topic.toLowerCase())
      );
    
    if (topicNodes.length === 0) {
      return 0.5; // Default popularity
    }
    
    const topicNode = topicNodes[0];
    
    // Count incoming edges
    const incomingEdges = this.graphStore.getIncomingEdges(topicNode.id);
    
    // Normalize to a score between 0 and 1
    // Assuming more than 10 references is very popular
    const popularity = Math.min(incomingEdges.length / 10, 1);
    
    return popularity;
  }
} 