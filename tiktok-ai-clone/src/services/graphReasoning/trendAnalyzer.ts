/**
 * Trend Analyzer - Analyzes trends and user segments in the graph
 */

import { GraphStore } from './graphStore';
import { 
  TrendAnalysis, 
  UserSegment,
  NodeType,
  EdgeType,
  GraphNode
} from './types';

/**
 * Trend Analyzer class
 */
export class TrendAnalyzer {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Analyze trends in the graph
   */
  public async analyzeTrends(timeframe: string = 'week', count: number = 5): Promise<TrendAnalysis[]> {
    console.log(`Analyzing trends for timeframe: ${timeframe}`);
    
    // Get all topic nodes
    const topicNodes = this.graphStore.getNodesByType(NodeType.TOPIC);
    
    // Calculate time range based on timeframe
    const now = new Date();
    let startTime: Date;
    
    switch (timeframe) {
      case 'day':
        startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000);
        break;
      case 'week':
        startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        break;
      case 'month':
        startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
        break;
      default:
        startTime = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000); // Default to week
    }
    
    // Analyze each topic
    const trendAnalyses = await Promise.all(
      topicNodes.map(async topic => {
        return this.analyzeTopic(topic, startTime, now);
      })
    );
    
    // Sort by strength (descending) and take the top 'count'
    const topTrends = trendAnalyses
      .sort((a, b) => b.strength - a.strength)
      .slice(0, count);
    
    console.log(`Found ${topTrends.length} top trends`);
    return topTrends;
  }

  /**
   * Analyze a specific topic
   */
  private async analyzeTopic(
    topicNode: GraphNode, 
    startTime: Date, 
    endTime: Date
  ): Promise<TrendAnalysis> {
    const topicId = topicNode.id;
    const topicName = topicNode.properties.name || 'Unknown Topic';
    
    // Get all edges referencing this topic
    const incomingEdges = this.graphStore.getIncomingEdges(topicId);
    
    // Filter edges by time range
    const recentEdges = incomingEdges.filter(edge => 
      edge.createdAt.getTime() >= startTime.getTime() &&
      edge.createdAt.getTime() <= endTime.getTime()
    );
    
    // Calculate trend strength based on recent activity
    const strength = Math.min(recentEdges.length / 10, 1); // Normalize to 0-1
    
    // Calculate growth rate
    // Compare recent activity to previous period
    const previousStartTime = new Date(startTime.getTime() - (endTime.getTime() - startTime.getTime()));
    
    const previousEdges = incomingEdges.filter(edge => 
      edge.createdAt.getTime() >= previousStartTime.getTime() &&
      edge.createdAt.getTime() < startTime.getTime()
    );
    
    // Calculate growth rate
    let growth = 0;
    if (previousEdges.length > 0) {
      growth = (recentEdges.length - previousEdges.length) / previousEdges.length;
    } else if (recentEdges.length > 0) {
      growth = 1; // New trend
    }
    
    // Find related topics
    const relatedTopics = await this.findRelatedTopics(topicId);
    
    // Find related videos
    const relatedVideos = await this.findRelatedVideos(topicId);
    
    // Predict lifespan based on growth and strength
    const predictedLifespan = this.predictTrendLifespan(strength, growth);
    
    return {
      trendId: topicId,
      name: topicName,
      strength,
      growth,
      relatedTopics,
      relatedVideos,
      predictedLifespan
    };
  }

  /**
   * Find topics related to a given topic
   */
  private async findRelatedTopics(topicId: string): Promise<string[]> {
    // Get neighbors connected by RELATED_TO edges
    const neighbors = this.graphStore.getNeighbors(topicId, EdgeType.RELATED_TO);
    
    // Filter for topic nodes and extract names
    const relatedTopics = neighbors
      .filter(node => node.type === NodeType.TOPIC)
      .map(node => node.properties.name || 'Unknown Topic');
    
    return relatedTopics;
  }

  /**
   * Find videos related to a topic
   */
  private async findRelatedVideos(topicId: string): Promise<string[]> {
    // Get all video nodes
    const videoNodes = this.graphStore.getNodesByType(NodeType.VIDEO);
    
    // Find videos that reference this topic
    const relatedVideos: string[] = [];
    
    for (const video of videoNodes) {
      // Check if video has a path to the topic
      const paths = this.graphStore.findPaths(video.id, topicId, 2);
      
      if (paths.length > 0) {
        relatedVideos.push(video.id);
      }
    }
    
    return relatedVideos;
  }

  /**
   * Predict the lifespan of a trend in days
   */
  private predictTrendLifespan(strength: number, growth: number): number {
    // Base lifespan
    let lifespan = 7; // Default to one week
    
    // Adjust based on strength
    if (strength > 0.8) {
      lifespan += 14; // Strong trends last longer
    } else if (strength > 0.5) {
      lifespan += 7;
    }
    
    // Adjust based on growth
    if (growth > 1) {
      lifespan += 7; // Fast-growing trends have potential to last longer
    } else if (growth < 0) {
      lifespan = Math.max(1, lifespan - 7); // Declining trends won't last as long
    }
    
    return lifespan;
  }

  /**
   * Analyze user segments in the graph
   */
  public async analyzeUserSegments(count: number = 5): Promise<UserSegment[]> {
    console.log(`Analyzing user segments`);
    
    // Get all user nodes
    const userNodes = this.graphStore.getNodesByType(NodeType.USER);
    
    if (userNodes.length === 0) {
      console.log('No users found in the graph');
      return [];
    }
    
    // Analyze user interests
    const userInterests = await this.analyzeUserInterests(userNodes);
    
    // Cluster users based on interests
    const segments = await this.clusterUsersByInterests(userNodes, userInterests);
    
    // Take top segments by size
    const topSegments = segments
      .sort((a, b) => b.size - a.size)
      .slice(0, count);
    
    console.log(`Found ${topSegments.length} user segments`);
    return topSegments;
  }

  /**
   * Analyze interests for each user
   */
  private async analyzeUserInterests(
    userNodes: GraphNode[]
  ): Promise<Map<string, string[]>> {
    const userInterests = new Map<string, string[]>();
    
    for (const user of userNodes) {
      const userId = user.id;
      
      // Get videos the user has viewed
      const viewedEdges = this.graphStore.getOutgoingEdges(userId)
        .filter(edge => edge.type === EdgeType.VIEWED);
      
      // Get categories of viewed videos
      const categories = new Set<string>();
      
      for (const edge of viewedEdges) {
        const videoNode = this.graphStore.getNode(edge.target);
        if (videoNode && videoNode.properties.category) {
          categories.add(videoNode.properties.category);
        }
      }
      
      // Store user interests
      userInterests.set(userId, Array.from(categories));
    }
    
    return userInterests;
  }

  /**
   * Cluster users based on their interests
   */
  private async clusterUsersByInterests(
    userNodes: GraphNode[],
    userInterests: Map<string, string[]>
  ): Promise<UserSegment[]> {
    // Count interest occurrences
    const interestCounts: Record<string, number> = {};
    
    userInterests.forEach((interests) => {
      interests.forEach(interest => {
        interestCounts[interest] = (interestCounts[interest] || 0) + 1;
      });
    });
    
    // Sort interests by popularity
    const sortedInterests = Object.entries(interestCounts)
      .sort(([, countA], [, countB]) => countB - countA)
      .map(([interest]) => interest);
    
    // Create segments based on top interests
    const segments: UserSegment[] = [];
    
    for (const interest of sortedInterests.slice(0, 10)) { // Consider top 10 interests
      // Find users with this interest
      const userIds: string[] = [];
      
      userInterests.forEach((interests, userId) => {
        if (interests.includes(interest)) {
          userIds.push(userId);
        }
      });
      
      // Find common interests among these users
      const commonInterests = this.findCommonInterests(userIds, userInterests);
      
      // Create segment
      segments.push({
        id: `segment-${interest.toLowerCase().replace(/\s+/g, '-')}`,
        name: `${interest} Enthusiasts`,
        description: `Users interested in ${interest} and related topics`,
        userIds,
        commonInterests,
        commonBehaviors: {
          primaryInterest: interest
        },
        size: userIds.length
      });
    }
    
    return segments;
  }

  /**
   * Find common interests among a group of users
   */
  private findCommonInterests(
    userIds: string[],
    userInterests: Map<string, string[]>
  ): string[] {
    if (userIds.length === 0) return [];
    
    // Count interest occurrences
    const interestCounts: Record<string, number> = {};
    
    userIds.forEach(userId => {
      const interests = userInterests.get(userId) || [];
      interests.forEach(interest => {
        interestCounts[interest] = (interestCounts[interest] || 0) + 1;
      });
    });
    
    // Find interests shared by at least 50% of users
    const threshold = Math.max(1, Math.floor(userIds.length * 0.5));
    
    const commonInterests = Object.entries(interestCounts)
      .filter(([, count]) => count >= threshold)
      .map(([interest]) => interest);
    
    return commonInterests;
  }
} 