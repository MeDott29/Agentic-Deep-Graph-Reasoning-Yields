/**
 * Engagement Analyzer - Analyzes user engagement patterns
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
  EngagementPattern, 
  UserInteraction 
} from './types';

/**
 * Engagement Analyzer class
 */
export class EngagementAnalyzer {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Analyze engagement patterns
   */
  public async analyzeEngagementPatterns(
    userNodes: GraphNode[],
    startTime: Date,
    endTime: Date,
    minPatternSupport: number = 0.2
  ): Promise<BehaviorPattern[]> {
    console.log(`Analyzing engagement patterns for ${userNodes.length} users`);
    
    // Get user interactions within the time range
    const userInteractions = this.getUserInteractions(userNodes, startTime, endTime);
    
    if (Object.keys(userInteractions).length === 0) {
      console.log('No user interactions found in the specified time range');
      return [];
    }
    
    // Analyze different engagement patterns
    const patterns: BehaviorPattern[] = [];
    
    // 1. High engagement pattern
    const highEngagementPattern = await this.detectHighEngagementPattern(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (highEngagementPattern) {
      patterns.push(highEngagementPattern);
    }
    
    // 2. Low engagement pattern
    const lowEngagementPattern = await this.detectLowEngagementPattern(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (lowEngagementPattern) {
      patterns.push(lowEngagementPattern);
    }
    
    // 3. Binge watching pattern
    const bingeWatchingPattern = await this.detectBingeWatchingPattern(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (bingeWatchingPattern) {
      patterns.push(bingeWatchingPattern);
    }
    
    // 4. Content completion pattern
    const contentCompletionPattern = await this.detectContentCompletionPattern(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (contentCompletionPattern) {
      patterns.push(contentCompletionPattern);
    }
    
    // 5. Interaction-heavy pattern
    const interactionHeavyPattern = await this.detectInteractionHeavyPattern(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (interactionHeavyPattern) {
      patterns.push(interactionHeavyPattern);
    }
    
    console.log(`Found ${patterns.length} engagement patterns`);
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
   * Detect high engagement pattern
   */
  private async detectHighEngagementPattern(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<EngagementPattern | null> {
    console.log('Detecting high engagement pattern');
    
    // Calculate engagement metrics for each user
    const userEngagementMetrics: Record<string, {
      viewDuration: number;
      completionRate: number;
      interactionRate: number;
      returnRate: number;
    }> = {};
    
    for (const userId in userInteractions) {
      const interactions = userInteractions[userId];
      
      if (interactions.length === 0) {
        continue;
      }
      
      // Calculate view duration
      const viewInteractions = interactions.filter(interaction => interaction.action === 'view');
      const totalViewDuration = viewInteractions.reduce((sum, interaction) => sum + (interaction.duration || 0), 0);
      const avgViewDuration = viewInteractions.length > 0 ? totalViewDuration / viewInteractions.length : 0;
      
      // Calculate completion rate
      const videoIds = new Set(viewInteractions.map(interaction => interaction.videoId));
      let completedVideos = 0;
      
      for (const videoId of videoIds) {
        const videoInteractions = viewInteractions.filter(interaction => interaction.videoId === videoId);
        const videoDuration = this.getVideoDuration(videoId);
        const maxViewDuration = Math.max(...videoInteractions.map(interaction => interaction.duration || 0));
        
        if (maxViewDuration >= videoDuration * 0.9) {
          completedVideos++;
        }
      }
      
      const completionRate = videoIds.size > 0 ? completedVideos / videoIds.size : 0;
      
      // Calculate interaction rate
      const interactionCount = interactions.filter(interaction => 
        interaction.action === 'like' || 
        interaction.action === 'comment' || 
        interaction.action === 'share'
      ).length;
      
      const interactionRate = viewInteractions.length > 0 ? interactionCount / viewInteractions.length : 0;
      
      // Calculate return rate
      const videoReturnCounts: Record<string, number> = {};
      
      viewInteractions.forEach(interaction => {
        const videoId = interaction.videoId;
        videoReturnCounts[videoId] = (videoReturnCounts[videoId] || 0) + 1;
      });
      
      const returnedVideos = Object.values(videoReturnCounts).filter(count => count > 1).length;
      const returnRate = videoIds.size > 0 ? returnedVideos / videoIds.size : 0;
      
      // Store metrics
      userEngagementMetrics[userId] = {
        viewDuration: avgViewDuration,
        completionRate,
        interactionRate,
        returnRate
      };
    }
    
    // Define thresholds for high engagement
    const viewDurationThreshold = 60; // 1 minute
    const completionRateThreshold = 0.7;
    const interactionRateThreshold = 0.2;
    const returnRateThreshold = 0.1;
    
    // Find users with high engagement
    const highEngagementUsers = userNodes.filter(user => {
      const metrics = userEngagementMetrics[user.id];
      
      if (!metrics) {
        return false;
      }
      
      return (
        metrics.viewDuration >= viewDurationThreshold &&
        metrics.completionRate >= completionRateThreshold &&
        metrics.interactionRate >= interactionRateThreshold &&
        metrics.returnRate >= returnRateThreshold
      );
    });
    
    // Calculate support
    const support = userNodes.length > 0 ? highEngagementUsers.length / userNodes.length : 0;
    
    // Skip if support is below threshold
    if (support < minPatternSupport) {
      console.log('High engagement pattern support below threshold');
      return null;
    }
    
    // Calculate average metrics
    const avgViewDuration = this.calculateAverage(
      highEngagementUsers.map(user => userEngagementMetrics[user.id]?.viewDuration || 0)
    );
    
    const avgCompletionRate = this.calculateAverage(
      highEngagementUsers.map(user => userEngagementMetrics[user.id]?.completionRate || 0)
    );
    
    const avgInteractionRate = this.calculateAverage(
      highEngagementUsers.map(user => userEngagementMetrics[user.id]?.interactionRate || 0)
    );
    
    const avgReturnRate = this.calculateAverage(
      highEngagementUsers.map(user => userEngagementMetrics[user.id]?.returnRate || 0)
    );
    
    // Get related nodes and edges
    const relatedNodes: GraphNode[] = [];
    const relatedEdges: GraphEdge[] = [];
    
    for (const user of highEngagementUsers) {
      const interactions = userInteractions[user.id] || [];
      
      for (const interaction of interactions) {
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
    const pattern: EngagementPattern = {
      id: `pattern-high-engagement-${Date.now()}`,
      type: BehaviorPatternType.ENGAGEMENT,
      users: highEngagementUsers,
      relatedNodes,
      relatedEdges,
      support,
      confidence: 0.8, // High confidence for this pattern
      description: `High engagement pattern with ${highEngagementUsers.length} users`,
      detectionTime: new Date(),
      engagementMetrics: {
        viewDuration: avgViewDuration,
        completionRate: avgCompletionRate,
        interactionRate: avgInteractionRate,
        returnRate: avgReturnRate
      }
    };
    
    return pattern;
  }

  /**
   * Detect low engagement pattern
   */
  private async detectLowEngagementPattern(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<EngagementPattern | null> {
    console.log('Detecting low engagement pattern');
    
    // Similar to high engagement pattern, but with opposite thresholds
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return null;
  }

  /**
   * Detect binge watching pattern
   */
  private async detectBingeWatchingPattern(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<EngagementPattern | null> {
    console.log('Detecting binge watching pattern');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return null;
  }

  /**
   * Detect content completion pattern
   */
  private async detectContentCompletionPattern(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<EngagementPattern | null> {
    console.log('Detecting content completion pattern');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return null;
  }

  /**
   * Detect interaction-heavy pattern
   */
  private async detectInteractionHeavyPattern(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<EngagementPattern | null> {
    console.log('Detecting interaction-heavy pattern');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return null;
  }

  /**
   * Get video duration in seconds
   */
  private getVideoDuration(videoId: string): number {
    const videoNode = this.graphStore.getNode(videoId);
    
    if (!videoNode) {
      return 0;
    }
    
    return videoNode.properties.duration || 0;
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