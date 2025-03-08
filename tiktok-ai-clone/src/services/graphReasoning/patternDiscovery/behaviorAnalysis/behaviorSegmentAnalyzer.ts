/**
 * Behavior Segment Analyzer - Analyzes user behavior segments
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
  UserSegmentPattern, 
  UserInteraction 
} from './types';

/**
 * Behavior Segment Analyzer class
 */
export class BehaviorSegmentAnalyzer {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Analyze user segments
   */
  public async analyzeUserSegments(
    userNodes: GraphNode[],
    startTime: Date,
    endTime: Date,
    minPatternSupport: number = 0.2
  ): Promise<BehaviorPattern[]> {
    console.log(`Analyzing user segments for ${userNodes.length} users`);
    
    // Get user interactions within the time range
    const userInteractions = this.getUserInteractions(userNodes, startTime, endTime);
    
    if (Object.keys(userInteractions).length === 0) {
      console.log('No user interactions found in the specified time range');
      return [];
    }
    
    // Analyze different user segments
    const patterns: BehaviorPattern[] = [];
    
    // 1. Content explorer segment
    const contentExplorerSegment = await this.detectContentExplorerSegment(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (contentExplorerSegment) {
      patterns.push(contentExplorerSegment);
    }
    
    // 2. Content creator segment
    const contentCreatorSegment = await this.detectContentCreatorSegment(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (contentCreatorSegment) {
      patterns.push(contentCreatorSegment);
    }
    
    // 3. Social butterfly segment
    const socialButterflySegment = await this.detectSocialButterflySegment(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (socialButterflySegment) {
      patterns.push(socialButterflySegment);
    }
    
    // 4. Passive consumer segment
    const passiveConsumerSegment = await this.detectPassiveConsumerSegment(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    if (passiveConsumerSegment) {
      patterns.push(passiveConsumerSegment);
    }
    
    // 5. Niche enthusiast segment
    const nicheEnthusiastSegments = await this.detectNicheEnthusiastSegments(
      userNodes, 
      userInteractions, 
      minPatternSupport
    );
    
    patterns.push(...nicheEnthusiastSegments);
    
    console.log(`Found ${patterns.length} user segments`);
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
   * Detect content explorer segment
   */
  private async detectContentExplorerSegment(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<UserSegmentPattern | null> {
    console.log('Detecting content explorer segment');
    
    // Calculate metrics for each user
    const userMetrics: Record<string, {
      uniqueCategories: number;
      uniqueCreators: number;
      viewToInteractionRatio: number;
      averageViewDuration: number;
    }> = {};
    
    for (const userId in userInteractions) {
      const interactions = userInteractions[userId];
      
      if (interactions.length === 0) {
        continue;
      }
      
      // Get unique categories and creators
      const categories = new Set<string>();
      const creators = new Set<string>();
      
      for (const interaction of interactions) {
        const videoNode = this.graphStore.getNode(interaction.videoId);
        
        if (!videoNode) {
          continue;
        }
        
        if (videoNode.properties.category) {
          categories.add(videoNode.properties.category);
        }
        
        if (videoNode.properties.creator) {
          creators.add(videoNode.properties.creator);
        }
      }
      
      // Calculate view to interaction ratio
      const viewCount = interactions.filter(interaction => interaction.action === 'view').length;
      const interactionCount = interactions.filter(interaction => interaction.action !== 'view').length;
      const viewToInteractionRatio = viewCount > 0 ? interactionCount / viewCount : 0;
      
      // Calculate average view duration
      const viewInteractions = interactions.filter(interaction => interaction.action === 'view');
      const totalViewDuration = viewInteractions.reduce((sum, interaction) => sum + (interaction.duration || 0), 0);
      const averageViewDuration = viewInteractions.length > 0 ? totalViewDuration / viewInteractions.length : 0;
      
      // Store metrics
      userMetrics[userId] = {
        uniqueCategories: categories.size,
        uniqueCreators: creators.size,
        viewToInteractionRatio,
        averageViewDuration
      };
    }
    
    // Define thresholds for content explorer segment
    const uniqueCategoriesThreshold = 5;
    const uniqueCreatorsThreshold = 10;
    const viewToInteractionRatioThreshold = 0.1;
    const averageViewDurationThreshold = 30; // 30 seconds
    
    // Find users in the content explorer segment
    const contentExplorerUsers = userNodes.filter(user => {
      const metrics = userMetrics[user.id];
      
      if (!metrics) {
        return false;
      }
      
      return (
        metrics.uniqueCategories >= uniqueCategoriesThreshold &&
        metrics.uniqueCreators >= uniqueCreatorsThreshold &&
        metrics.viewToInteractionRatio >= viewToInteractionRatioThreshold &&
        metrics.averageViewDuration >= averageViewDurationThreshold
      );
    });
    
    // Calculate support
    const support = userNodes.length > 0 ? contentExplorerUsers.length / userNodes.length : 0;
    
    // Skip if support is below threshold
    if (support < minPatternSupport) {
      console.log('Content explorer segment support below threshold');
      return null;
    }
    
    // Get related nodes and edges
    const relatedNodes: GraphNode[] = [];
    const relatedEdges: GraphEdge[] = [];
    
    for (const user of contentExplorerUsers) {
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
    
    // Calculate segment metrics
    const size = contentExplorerUsers.length;
    const cohesion = this.calculateSegmentCohesion(contentExplorerUsers, userInteractions);
    const stability = this.calculateSegmentStability(contentExplorerUsers);
    const distinctiveness = this.calculateSegmentDistinctiveness(contentExplorerUsers, userNodes);
    const growthRate = this.calculateSegmentGrowthRate(contentExplorerUsers);
    
    // Create pattern
    const pattern: UserSegmentPattern = {
      id: `segment-content-explorer-${Date.now()}`,
      type: BehaviorPatternType.SEGMENT,
      users: contentExplorerUsers,
      relatedNodes,
      relatedEdges,
      support,
      confidence: 0.8, // High confidence for this segment
      description: `Content explorer segment with ${contentExplorerUsers.length} users`,
      detectionTime: new Date(),
      segmentMetrics: {
        size,
        cohesion,
        stability,
        distinctiveness,
        growthRate
      }
    };
    
    return pattern;
  }

  /**
   * Detect content creator segment
   */
  private async detectContentCreatorSegment(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<UserSegmentPattern | null> {
    console.log('Detecting content creator segment');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return null;
  }

  /**
   * Detect social butterfly segment
   */
  private async detectSocialButterflySegment(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<UserSegmentPattern | null> {
    console.log('Detecting social butterfly segment');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return null;
  }

  /**
   * Detect passive consumer segment
   */
  private async detectPassiveConsumerSegment(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<UserSegmentPattern | null> {
    console.log('Detecting passive consumer segment');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return null;
  }

  /**
   * Detect niche enthusiast segments
   */
  private async detectNicheEnthusiastSegments(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    minPatternSupport: number
  ): Promise<UserSegmentPattern[]> {
    console.log('Detecting niche enthusiast segments');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
  }

  /**
   * Calculate segment cohesion
   */
  private calculateSegmentCohesion(
    segmentUsers: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>
  ): number {
    // Calculate similarity between users in the segment
    let totalSimilarity = 0;
    let pairCount = 0;
    
    for (let i = 0; i < segmentUsers.length; i++) {
      for (let j = i + 1; j < segmentUsers.length; j++) {
        const user1 = segmentUsers[i];
        const user2 = segmentUsers[j];
        
        const similarity = this.calculateUserSimilarity(
          user1.id,
          user2.id,
          userInteractions
        );
        
        totalSimilarity += similarity;
        pairCount++;
      }
    }
    
    // Average similarity is the cohesion
    return pairCount > 0 ? totalSimilarity / pairCount : 0;
  }

  /**
   * Calculate user similarity
   */
  private calculateUserSimilarity(
    userId1: string,
    userId2: string,
    userInteractions: Record<string, UserInteraction[]>
  ): number {
    const interactions1 = userInteractions[userId1] || [];
    const interactions2 = userInteractions[userId2] || [];
    
    if (interactions1.length === 0 || interactions2.length === 0) {
      return 0;
    }
    
    // Get video IDs for each user
    const videoIds1 = new Set(interactions1.map(interaction => interaction.videoId));
    const videoIds2 = new Set(interactions2.map(interaction => interaction.videoId));
    
    // Calculate Jaccard similarity
    const intersection = new Set([...videoIds1].filter(id => videoIds2.has(id)));
    const union = new Set([...videoIds1, ...videoIds2]);
    
    return union.size > 0 ? intersection.size / union.size : 0;
  }

  /**
   * Calculate segment stability
   */
  private calculateSegmentStability(segmentUsers: GraphNode[]): number {
    // This is a placeholder implementation
    // In a real system, you would analyze historical data to measure stability
    return 0.7;
  }

  /**
   * Calculate segment distinctiveness
   */
  private calculateSegmentDistinctiveness(
    segmentUsers: GraphNode[],
    allUsers: GraphNode[]
  ): number {
    // This is a placeholder implementation
    // In a real system, you would compare this segment to other segments
    return 0.8;
  }

  /**
   * Calculate segment growth rate
   */
  private calculateSegmentGrowthRate(segmentUsers: GraphNode[]): number {
    // This is a placeholder implementation
    // In a real system, you would analyze historical data to measure growth
    return 0.1;
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