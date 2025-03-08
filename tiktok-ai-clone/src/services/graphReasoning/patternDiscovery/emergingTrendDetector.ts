/**
 * Emerging Trend Detector - Detects emerging trends in the graph
 */

import { GraphStore } from '../graphStore';
import { 
  NodeType, 
  GraphNode, 
  GraphEdge 
} from '../types';

/**
 * Emerging Trend interface
 */
export interface EmergingTrend {
  id: string;
  name: string;
  type: 'topic' | 'category' | 'creator' | 'hashtag';
  nodes: GraphNode[];
  relatedNodes: GraphNode[];
  growth: number; // Growth rate (0-1)
  momentum: number; // Momentum score (0-1)
  description: string;
  detectionTime: Date;
}

/**
 * Emerging Trend Detector class
 */
export class EmergingTrendDetector {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Detect emerging trends in the graph
   */
  public async detectEmergingTrends(
    timeframe: string = 'week',
    growthThreshold: number = 0.5,
    minActivity: number = 5,
    maxTrends: number = 10
  ): Promise<EmergingTrend[]> {
    console.log(`Detecting emerging trends with growth threshold ${growthThreshold}`);
    
    // Calculate time ranges
    const now = new Date();
    let currentPeriodStart: Date;
    let previousPeriodStart: Date;
    
    switch (timeframe) {
      case 'day':
        currentPeriodStart = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        previousPeriodStart = new Date(now.getTime() - 2 * 24 * 60 * 60 * 1000);
        break;
      case 'week':
        currentPeriodStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        previousPeriodStart = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        currentPeriodStart = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        previousPeriodStart = new Date(now.getTime() - 60 * 24 * 60 * 60 * 1000);
        break;
      default:
        currentPeriodStart = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        previousPeriodStart = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
    }
    
    // Detect trends for different entity types
    const topicTrends = await this.detectTopicTrends(
      currentPeriodStart, 
      previousPeriodStart, 
      growthThreshold, 
      minActivity
    );
    
    const categoryTrends = await this.detectCategoryTrends(
      currentPeriodStart, 
      previousPeriodStart, 
      growthThreshold, 
      minActivity
    );
    
    const creatorTrends = await this.detectCreatorTrends(
      currentPeriodStart, 
      previousPeriodStart, 
      growthThreshold, 
      minActivity
    );
    
    const hashtagTrends = await this.detectHashtagTrends(
      currentPeriodStart, 
      previousPeriodStart, 
      growthThreshold, 
      minActivity
    );
    
    // Combine all trends
    const allTrends = [
      ...topicTrends,
      ...categoryTrends,
      ...creatorTrends,
      ...hashtagTrends
    ];
    
    // Sort by momentum (descending) and take the top 'maxTrends'
    const topTrends = allTrends
      .sort((a, b) => b.momentum - a.momentum)
      .slice(0, maxTrends);
    
    // Generate descriptions for trends
    const trendsWithDescriptions = this.generateTrendDescriptions(topTrends);
    
    console.log(`Found ${trendsWithDescriptions.length} emerging trends`);
    return trendsWithDescriptions;
  }

  /**
   * Detect emerging topic trends
   */
  private async detectTopicTrends(
    currentPeriodStart: Date,
    previousPeriodStart: Date,
    growthThreshold: number,
    minActivity: number
  ): Promise<EmergingTrend[]> {
    console.log('Detecting emerging topic trends');
    
    // Get all topic nodes
    const topicNodes = this.graphStore.getNodesByType(NodeType.TOPIC);
    const trends: EmergingTrend[] = [];
    
    for (const topicNode of topicNodes) {
      // Get all edges referencing this topic
      const incomingEdges = this.graphStore.getIncomingEdges(topicNode.id);
      
      // Count activity in current period
      const currentPeriodEdges = incomingEdges.filter(edge => 
        edge.createdAt.getTime() >= currentPeriodStart.getTime()
      );
      
      const currentActivity = currentPeriodEdges.length;
      
      // Skip if activity is below minimum threshold
      if (currentActivity < minActivity) {
        continue;
      }
      
      // Count activity in previous period
      const previousPeriodEdges = incomingEdges.filter(edge => 
        edge.createdAt.getTime() >= previousPeriodStart.getTime() &&
        edge.createdAt.getTime() < currentPeriodStart.getTime()
      );
      
      const previousActivity = previousPeriodEdges.length;
      
      // Calculate growth rate
      let growthRate = 0;
      
      if (previousActivity > 0) {
        growthRate = (currentActivity - previousActivity) / previousActivity;
      } else if (currentActivity > 0) {
        growthRate = 1; // New trend
      }
      
      // Skip if growth rate is below threshold
      if (growthRate < growthThreshold) {
        continue;
      }
      
      // Calculate momentum score
      const momentum = this.calculateMomentumScore(currentActivity, growthRate);
      
      // Get related nodes
      const relatedNodes = this.findRelatedNodes(topicNode, currentPeriodEdges);
      
      // Create trend object
      trends.push({
        id: `trend-topic-${topicNode.id}`,
        name: topicNode.properties.name || 'Unknown Topic',
        type: 'topic',
        nodes: [topicNode],
        relatedNodes,
        growth: growthRate,
        momentum,
        description: '', // Will be generated later
        detectionTime: new Date()
      });
    }
    
    return trends;
  }

  /**
   * Detect emerging category trends
   */
  private async detectCategoryTrends(
    currentPeriodStart: Date,
    previousPeriodStart: Date,
    growthThreshold: number,
    minActivity: number
  ): Promise<EmergingTrend[]> {
    console.log('Detecting emerging category trends');
    
    // Get all category nodes
    const categoryNodes = this.graphStore.getNodesByType(NodeType.CATEGORY);
    const trends: EmergingTrend[] = [];
    
    for (const categoryNode of categoryNodes) {
      // Get all edges referencing this category
      const incomingEdges = this.graphStore.getIncomingEdges(categoryNode.id);
      
      // Count activity in current period
      const currentPeriodEdges = incomingEdges.filter(edge => 
        edge.createdAt.getTime() >= currentPeriodStart.getTime()
      );
      
      const currentActivity = currentPeriodEdges.length;
      
      // Skip if activity is below minimum threshold
      if (currentActivity < minActivity) {
        continue;
      }
      
      // Count activity in previous period
      const previousPeriodEdges = incomingEdges.filter(edge => 
        edge.createdAt.getTime() >= previousPeriodStart.getTime() &&
        edge.createdAt.getTime() < currentPeriodStart.getTime()
      );
      
      const previousActivity = previousPeriodEdges.length;
      
      // Calculate growth rate
      let growthRate = 0;
      
      if (previousActivity > 0) {
        growthRate = (currentActivity - previousActivity) / previousActivity;
      } else if (currentActivity > 0) {
        growthRate = 1; // New trend
      }
      
      // Skip if growth rate is below threshold
      if (growthRate < growthThreshold) {
        continue;
      }
      
      // Calculate momentum score
      const momentum = this.calculateMomentumScore(currentActivity, growthRate);
      
      // Get related nodes
      const relatedNodes = this.findRelatedNodes(categoryNode, currentPeriodEdges);
      
      // Create trend object
      trends.push({
        id: `trend-category-${categoryNode.id}`,
        name: categoryNode.properties.name || 'Unknown Category',
        type: 'category',
        nodes: [categoryNode],
        relatedNodes,
        growth: growthRate,
        momentum,
        description: '', // Will be generated later
        detectionTime: new Date()
      });
    }
    
    return trends;
  }

  /**
   * Detect emerging creator trends
   */
  private async detectCreatorTrends(
    currentPeriodStart: Date,
    previousPeriodStart: Date,
    growthThreshold: number,
    minActivity: number
  ): Promise<EmergingTrend[]> {
    console.log('Detecting emerging creator trends');
    
    // Get all creator nodes
    const creatorNodes = this.graphStore.getNodesByType(NodeType.CREATOR);
    const trends: EmergingTrend[] = [];
    
    for (const creatorNode of creatorNodes) {
      // Get all edges referencing this creator
      const incomingEdges = this.graphStore.getIncomingEdges(creatorNode.id);
      
      // Count activity in current period
      const currentPeriodEdges = incomingEdges.filter(edge => 
        edge.createdAt.getTime() >= currentPeriodStart.getTime()
      );
      
      const currentActivity = currentPeriodEdges.length;
      
      // Skip if activity is below minimum threshold
      if (currentActivity < minActivity) {
        continue;
      }
      
      // Count activity in previous period
      const previousPeriodEdges = incomingEdges.filter(edge => 
        edge.createdAt.getTime() >= previousPeriodStart.getTime() &&
        edge.createdAt.getTime() < currentPeriodStart.getTime()
      );
      
      const previousActivity = previousPeriodEdges.length;
      
      // Calculate growth rate
      let growthRate = 0;
      
      if (previousActivity > 0) {
        growthRate = (currentActivity - previousActivity) / previousActivity;
      } else if (currentActivity > 0) {
        growthRate = 1; // New trend
      }
      
      // Skip if growth rate is below threshold
      if (growthRate < growthThreshold) {
        continue;
      }
      
      // Calculate momentum score
      const momentum = this.calculateMomentumScore(currentActivity, growthRate);
      
      // Get related nodes
      const relatedNodes = this.findRelatedNodes(creatorNode, currentPeriodEdges);
      
      // Create trend object
      trends.push({
        id: `trend-creator-${creatorNode.id}`,
        name: creatorNode.properties.name || 'Unknown Creator',
        type: 'creator',
        nodes: [creatorNode],
        relatedNodes,
        growth: growthRate,
        momentum,
        description: '', // Will be generated later
        detectionTime: new Date()
      });
    }
    
    return trends;
  }

  /**
   * Detect emerging hashtag trends
   */
  private async detectHashtagTrends(
    currentPeriodStart: Date,
    previousPeriodStart: Date,
    growthThreshold: number,
    minActivity: number
  ): Promise<EmergingTrend[]> {
    console.log('Detecting emerging hashtag trends');
    
    // This is a placeholder for hashtag trend detection
    // In a real implementation, you would extract hashtags from content
    
    console.log('Hashtag trend detection is not fully implemented');
    
    // For now, return an empty array
    return [];
  }

  /**
   * Calculate momentum score
   */
  private calculateMomentumScore(activity: number, growthRate: number): number {
    // Normalize activity (assuming max activity is 100)
    const normalizedActivity = Math.min(1, activity / 100);
    
    // Normalize growth rate (cap at 5x growth)
    const normalizedGrowth = Math.min(1, growthRate / 5);
    
    // Momentum is a combination of activity and growth
    return (normalizedActivity * 0.4) + (normalizedGrowth * 0.6);
  }

  /**
   * Find nodes related to a trend
   */
  private findRelatedNodes(
    trendNode: GraphNode,
    recentEdges: GraphEdge[]
  ): GraphNode[] {
    // Get nodes connected by recent edges
    const connectedNodeIds = new Set<string>();
    
    recentEdges.forEach(edge => {
      if (edge.source !== trendNode.id) {
        connectedNodeIds.add(edge.source);
      }
      if (edge.target !== trendNode.id) {
        connectedNodeIds.add(edge.target);
      }
    });
    
    // Get node objects
    return Array.from(connectedNodeIds)
      .map(id => this.graphStore.getNode(id))
      .filter((node): node is GraphNode => node !== undefined);
  }

  /**
   * Generate descriptions for trends
   */
  private generateTrendDescriptions(trends: EmergingTrend[]): EmergingTrend[] {
    return trends.map(trend => {
      let description = '';
      
      switch (trend.type) {
        case 'topic':
          description = `Emerging topic trend: "${trend.name}"`;
          break;
        case 'category':
          description = `Emerging category trend: "${trend.name}"`;
          break;
        case 'creator':
          description = `Emerging creator trend: "${trend.name}"`;
          break;
        case 'hashtag':
          description = `Emerging hashtag trend: #${trend.name}`;
          break;
        default:
          description = `Emerging trend: "${trend.name}"`;
      }
      
      // Add growth and momentum information
      description += ` with ${(trend.growth * 100).toFixed(0)}% growth`;
      
      // Add related nodes information
      const videoCount = trend.relatedNodes.filter(node => node.type === NodeType.VIDEO).length;
      const userCount = trend.relatedNodes.filter(node => node.type === NodeType.USER).length;
      
      if (videoCount > 0 || userCount > 0) {
        description += ` (${videoCount} videos, ${userCount} users)`;
      }
      
      return { ...trend, description };
    });
  }
} 