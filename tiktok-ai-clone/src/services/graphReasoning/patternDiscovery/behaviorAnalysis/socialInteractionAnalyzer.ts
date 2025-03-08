/**
 * Social Interaction Analyzer - Analyzes user social interaction patterns
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
  SocialInteractionPattern, 
  UserInteraction 
} from './types';

/**
 * Social Interaction Analyzer class
 */
export class SocialInteractionAnalyzer {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Analyze social interactions
   */
  public async analyzeSocialInteractions(
    userNodes: GraphNode[],
    startTime: Date,
    endTime: Date,
    minPatternSupport: number = 0.2
  ): Promise<BehaviorPattern[]> {
    console.log(`Analyzing social interactions for ${userNodes.length} users`);
    
    // Get user interactions within the time range
    const userInteractions = this.getUserInteractions(userNodes, startTime, endTime);
    
    if (Object.keys(userInteractions).length === 0) {
      console.log('No user interactions found in the specified time range');
      return [];
    }
    
    // Analyze different social interaction patterns
    const patterns: BehaviorPattern[] = [];
    
    // 1. High social engagement pattern
    const highSocialEngagementPattern = await this.detectHighSocialEngagementPattern(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (highSocialEngagementPattern) {
      patterns.push(highSocialEngagementPattern);
    }
    
    // 2. Creator follower pattern
    const creatorFollowerPatterns = await this.detectCreatorFollowerPatterns(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    patterns.push(...creatorFollowerPatterns);
    
    // 3. Community interaction pattern
    const communityInteractionPatterns = await this.detectCommunityInteractionPatterns(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    patterns.push(...communityInteractionPatterns);
    
    // 4. Influencer interaction pattern
    const influencerInteractionPattern = await this.detectInfluencerInteractionPattern(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (influencerInteractionPattern) {
      patterns.push(influencerInteractionPattern);
    }
    
    console.log(`Found ${patterns.length} social interaction patterns`);
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
   * Detect high social engagement pattern
   */
  private async detectHighSocialEngagementPattern(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<SocialInteractionPattern | null> {
    console.log('Detecting high social engagement pattern');
    
    // Calculate social metrics for each user
    const userSocialMetrics: Record<string, {
      followRate: number;
      commentRate: number;
      shareRate: number;
      responseRate: number;
      influencerInteractionRate: number;
    }> = {};
    
    for (const userId in userInteractions) {
      const interactions = userInteractions[userId];
      
      if (interactions.length === 0) {
        continue;
      }
      
      // Count interactions by type
      const viewCount = interactions.filter(interaction => interaction.action === 'view').length;
      const followCount = interactions.filter(interaction => interaction.action === 'follow').length;
      const commentCount = interactions.filter(interaction => interaction.action === 'comment').length;
      const shareCount = interactions.filter(interaction => interaction.action === 'share').length;
      
      // Calculate rates
      const followRate = viewCount > 0 ? followCount / viewCount : 0;
      const commentRate = viewCount > 0 ? commentCount / viewCount : 0;
      const shareRate = viewCount > 0 ? shareCount / viewCount : 0;
      
      // Calculate response rate (placeholder)
      const responseRate = 0;
      
      // Calculate influencer interaction rate
      const influencerInteractionRate = this.calculateInfluencerInteractionRate(userId, interactions);
      
      // Store metrics
      userSocialMetrics[userId] = {
        followRate,
        commentRate,
        shareRate,
        responseRate,
        influencerInteractionRate
      };
    }
    
    // Define thresholds for high social engagement
    const followRateThreshold = 0.05;
    const commentRateThreshold = 0.1;
    const shareRateThreshold = 0.03;
    const responseRateThreshold = 0.2;
    const influencerInteractionRateThreshold = 0.1;
    
    // Find users with high social engagement
    const highSocialEngagementUsers = userNodes.filter(user => {
      const metrics = userSocialMetrics[user.id];
      
      if (!metrics) {
        return false;
      }
      
      // User must meet at least 3 of the 5 criteria
      let criteriaCount = 0;
      
      if (metrics.followRate >= followRateThreshold) criteriaCount++;
      if (metrics.commentRate >= commentRateThreshold) criteriaCount++;
      if (metrics.shareRate >= shareRateThreshold) criteriaCount++;
      if (metrics.responseRate >= responseRateThreshold) criteriaCount++;
      if (metrics.influencerInteractionRate >= influencerInteractionRateThreshold) criteriaCount++;
      
      return criteriaCount >= 3;
    });
    
    // Calculate support
    const support = userNodes.length > 0 ? highSocialEngagementUsers.length / userNodes.length : 0;
    
    // Skip if support is below threshold
    if (support < minPatternSupport) {
      console.log('High social engagement pattern support below threshold');
      return null;
    }
    
    // Calculate average metrics
    const avgFollowRate = this.calculateAverage(
      highSocialEngagementUsers.map(user => userSocialMetrics[user.id]?.followRate || 0)
    );
    
    const avgCommentRate = this.calculateAverage(
      highSocialEngagementUsers.map(user => userSocialMetrics[user.id]?.commentRate || 0)
    );
    
    const avgShareRate = this.calculateAverage(
      highSocialEngagementUsers.map(user => userSocialMetrics[user.id]?.shareRate || 0)
    );
    
    const avgResponseRate = this.calculateAverage(
      highSocialEngagementUsers.map(user => userSocialMetrics[user.id]?.responseRate || 0)
    );
    
    const avgInfluencerInteractionRate = this.calculateAverage(
      highSocialEngagementUsers.map(user => userSocialMetrics[user.id]?.influencerInteractionRate || 0)
    );
    
    // Get related nodes and edges
    const relatedNodes: GraphNode[] = [];
    const relatedEdges: GraphEdge[] = [];
    
    for (const user of highSocialEngagementUsers) {
      const interactions = userInteractions[user.id] || [];
      
      for (const interaction of interactions) {
        if (interaction.action === 'view') {
          continue; // Skip view interactions
        }
        
        const videoNode = this.graphStore.getNode(interaction.videoId);
        
        if (videoNode && !relatedNodes.some(node => node.id === videoNode.id)) {
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
    
    // Create pattern
    const pattern: SocialInteractionPattern = {
      id: `pattern-high-social-engagement-${Date.now()}`,
      type: BehaviorPatternType.SOCIAL_INTERACTION,
      users: highSocialEngagementUsers,
      relatedNodes,
      relatedEdges,
      support,
      confidence: 0.8, // High confidence for this pattern
      description: `High social engagement pattern with ${highSocialEngagementUsers.length} users`,
      detectionTime: new Date(),
      socialMetrics: {
        followRate: avgFollowRate,
        commentRate: avgCommentRate,
        shareRate: avgShareRate,
        responseRate: avgResponseRate,
        influencerInteractionRate: avgInfluencerInteractionRate
      }
    };
    
    return pattern;
  }

  /**
   * Calculate influencer interaction rate
   */
  private calculateInfluencerInteractionRate(
    userId: string,
    interactions: UserInteraction[]
  ): number {
    // Get all creators
    const creatorNodes = this.graphStore.getNodesByType(NodeType.CREATOR);
    
    if (creatorNodes.length === 0) {
      return 0;
    }
    
    // Identify influencers (creators with high popularity)
    const influencers = creatorNodes.filter(creator => 
      creator.properties.popularity && creator.properties.popularity > 0.7
    );
    
    if (influencers.length === 0) {
      return 0;
    }
    
    // Count interactions with influencers
    let influencerInteractionCount = 0;
    
    for (const interaction of interactions) {
      if (interaction.action === 'view') {
        continue; // Skip view interactions
      }
      
      const videoNode = this.graphStore.getNode(interaction.videoId);
      
      if (!videoNode) {
        continue;
      }
      
      const videoCreator = videoNode.properties.creator;
      
      if (!videoCreator) {
        continue;
      }
      
      // Check if creator is an influencer
      const isInfluencer = influencers.some(influencer => 
        influencer.properties.name === videoCreator
      );
      
      if (isInfluencer) {
        influencerInteractionCount++;
      }
    }
    
    // Calculate rate
    const totalInteractions = interactions.filter(interaction => 
      interaction.action !== 'view'
    ).length;
    
    return totalInteractions > 0 ? influencerInteractionCount / totalInteractions : 0;
  }

  /**
   * Detect creator follower patterns
   */
  private async detectCreatorFollowerPatterns(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<SocialInteractionPattern[]> {
    console.log('Detecting creator follower patterns');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
  }

  /**
   * Detect community interaction patterns
   */
  private async detectCommunityInteractionPatterns(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<SocialInteractionPattern[]> {
    console.log('Detecting community interaction patterns');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
  }

  /**
   * Detect influencer interaction pattern
   */
  private async detectInfluencerInteractionPattern(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<SocialInteractionPattern | null> {
    console.log('Detecting influencer interaction pattern');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return null;
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