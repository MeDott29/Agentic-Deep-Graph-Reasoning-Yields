/**
 * Content Preference Analyzer - Analyzes user content preferences
 */

import { GraphStore } from '../../graphStore';
import { 
  NodeType, 
  EdgeType, 
  GraphNode, 
  GraphEdge 
} from '../../types';
import { 
  BehaviorPattern, 
  BehaviorPatternType, 
  ContentPreferencePattern, 
  UserInteraction 
} from './types';

/**
 * Content Preference Analyzer class
 */
export class ContentPreferenceAnalyzer {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Analyze content preferences
   */
  public async analyzeContentPreferences(
    userNodes: GraphNode[],
    startTime: Date,
    endTime: Date,
    minPatternSupport: number = 0.2
  ): Promise<BehaviorPattern[]> {
    console.log(`Analyzing content preferences for ${userNodes.length} users`);
    
    // Get user interactions within the time range
    const userInteractions = this.getUserInteractions(userNodes, startTime, endTime);
    
    if (Object.keys(userInteractions).length === 0) {
      console.log('No user interactions found in the specified time range');
      return [];
    }
    
    // Analyze different content preference patterns
    const patterns: BehaviorPattern[] = [];
    
    // 1. Category preference pattern
    const categoryPreferencePatterns = await this.detectCategoryPreferencePatterns(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    patterns.push(...categoryPreferencePatterns);
    
    // 2. Creator preference pattern
    const creatorPreferencePatterns = await this.detectCreatorPreferencePatterns(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    patterns.push(...creatorPreferencePatterns);
    
    // 3. Topic preference pattern
    const topicPreferencePatterns = await this.detectTopicPreferencePatterns(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    patterns.push(...topicPreferencePatterns);
    
    // 4. Format preference pattern
    const formatPreferencePatterns = await this.detectFormatPreferencePatterns(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    patterns.push(...formatPreferencePatterns);
    
    console.log(`Found ${patterns.length} content preference patterns`);
    return patterns;
  }

  /**
   * Get user interactions within a time range
   */
  private getUserInteractions(
    userNodes: GraphNode[],
    startTime: Date,
    endTime: Date
  ): Record<string, UserInteraction[]> {
    const userInteractions: Record<string, UserInteraction[]> = {};
    
    for (const userNode of userNodes) {
      const userId = userNode.id;
      userInteractions[userId] = [];
      
      // Get interactions from user properties
      const interactions = userNode.properties.interactions || [];
      
      // Filter interactions by time range
      const filteredInteractions = interactions.filter((interaction: any) => {
        const timestamp = new Date(interaction.timestamp);
        return timestamp >= startTime && timestamp <= endTime;
      });
      
      // Convert to UserInteraction objects
      userInteractions[userId] = filteredInteractions.map((interaction: any) => ({
        userId,
        videoId: interaction.videoId,
        action: interaction.action,
        timestamp: new Date(interaction.timestamp),
        duration: interaction.duration,
        metadata: interaction.metadata
      }));
    }
    
    return userInteractions;
  }

  /**
   * Detect category preference patterns
   */
  private async detectCategoryPreferencePatterns(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<ContentPreferencePattern[]> {
    console.log('Detecting category preference patterns');
    
    // Get all categories
    const categoryNodes = this.graphStore.getNodesByType(NodeType.CATEGORY);
    const categories = categoryNodes.map(node => node.properties.name);
    
    // Calculate category preferences for each user
    const userCategoryPreferences: Record<string, Record<string, number>> = {};
    
    for (const userId in userInteractions) {
      const interactions = userInteractions[userId];
      
      if (interactions.length === 0) {
        continue;
      }
      
      // Initialize category preferences
      userCategoryPreferences[userId] = {};
      categories.forEach(category => {
        userCategoryPreferences[userId][category] = 0;
      });
      
      // Count interactions by category
      for (const interaction of interactions) {
        const videoNode = this.graphStore.getNode(interaction.videoId);
        
        if (!videoNode) {
          continue;
        }
        
        const videoCategory = videoNode.properties.category;
        
        if (!videoCategory || !categories.includes(videoCategory)) {
          continue;
        }
        
        // Weight by interaction type
        let weight = 1;
        
        if (interaction.action === 'like') {
          weight = 2;
        } else if (interaction.action === 'comment') {
          weight = 3;
        } else if (interaction.action === 'share') {
          weight = 4;
        }
        
        userCategoryPreferences[userId][videoCategory] += weight;
      }
      
      // Normalize preferences
      const totalWeight = Object.values(userCategoryPreferences[userId]).reduce((sum, weight) => sum + weight, 0);
      
      if (totalWeight > 0) {
        for (const category in userCategoryPreferences[userId]) {
          userCategoryPreferences[userId][category] /= totalWeight;
        }
      }
    }
    
    // Find dominant category for each user
    const userDominantCategories: Record<string, string> = {};
    
    for (const userId in userCategoryPreferences) {
      const preferences = userCategoryPreferences[userId];
      let maxPreference = 0;
      let dominantCategory = '';
      
      for (const category in preferences) {
        if (preferences[category] > maxPreference) {
          maxPreference = preferences[category];
          dominantCategory = category;
        }
      }
      
      if (maxPreference > 0.3) { // Threshold for dominant category
        userDominantCategories[userId] = dominantCategory;
      }
    }
    
    // Group users by dominant category
    const categoryUsers: Record<string, GraphNode[]> = {};
    
    for (const userId in userDominantCategories) {
      const category = userDominantCategories[userId];
      
      if (!categoryUsers[category]) {
        categoryUsers[category] = [];
      }
      
      const userNode = userNodes.find(node => node.id === userId);
      
      if (userNode) {
        categoryUsers[category].push(userNode);
      }
    }
    
    // Create patterns for each category with sufficient support
    const patterns: ContentPreferencePattern[] = [];
    
    for (const category in categoryUsers) {
      const users = categoryUsers[category];
      const support = userNodes.length > 0 ? users.length / userNodes.length : 0;
      
      if (support < minPatternSupport) {
        continue;
      }
      
      // Calculate average preferences
      const avgPreferences = {
        categories: {},
        creators: {},
        topics: {},
        formats: {}
      };
      
      // Calculate category preferences
      for (const category in categories) {
        avgPreferences.categories[category] = this.calculateAverage(
          users.map(user => userCategoryPreferences[user.id]?.[category] || 0)
        );
      }
      
      // Get related nodes and edges
      const relatedNodes: GraphNode[] = [];
      const relatedEdges: GraphEdge[] = [];
      
      // Add category node
      const categoryNode = categoryNodes.find(node => node.properties.name === category);
      
      if (categoryNode) {
        relatedNodes.push(categoryNode);
      }
      
      // Add video nodes and edges
      for (const user of users) {
        const interactions = userInteractions[user.id] || [];
        
        for (const interaction of interactions) {
          const videoNode = this.graphStore.getNode(interaction.videoId);
          
          if (videoNode && videoNode.properties.category === category) {
            if (!relatedNodes.some(node => node.id === videoNode.id)) {
              relatedNodes.push(videoNode);
            }
            
            // Find edge for this interaction
            const edges = this.graphStore.getOutgoingEdges(user.id)
              .filter(edge => edge.target === interaction.videoId);
            
            for (const edge of edges) {
              if (!relatedEdges.some(e => e.id === edge.id)) {
                relatedEdges.push(edge);
              }
            }
          }
        }
      }
      
      // Create pattern
      const pattern: ContentPreferencePattern = {
        id: `pattern-category-preference-${category}-${Date.now()}`,
        type: BehaviorPatternType.CONTENT_PREFERENCE,
        users,
        relatedNodes,
        relatedEdges,
        support,
        confidence: 0.7, // Good confidence for category preferences
        description: `${category} preference pattern with ${users.length} users`,
        detectionTime: new Date(),
        preferenceMetrics: avgPreferences as any
      };
      
      patterns.push(pattern);
    }
    
    return patterns;
  }

  /**
   * Detect creator preference patterns
   */
  private async detectCreatorPreferencePatterns(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<ContentPreferencePattern[]> {
    console.log('Detecting creator preference patterns');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
  }

  /**
   * Detect topic preference patterns
   */
  private async detectTopicPreferencePatterns(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<ContentPreferencePattern[]> {
    console.log('Detecting topic preference patterns');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
  }

  /**
   * Detect format preference patterns
   */
  private async detectFormatPreferencePatterns(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<ContentPreferencePattern[]> {
    console.log('Detecting format preference patterns');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
  }

  /**
   * Calculate average of an array of numbers
   */
  private calculateAverage(values: number[]): number {
    if (values.length === 0) {
      return 0;
    }
    
    const sum = values.reduce((acc, val) => acc + val, 0);
    return sum / values.length;
  }
} 