/**
 * Recommendation Engine - Provides personalized content recommendations
 */

import { 
  GraphStore 
} from './graphStore';
import { 
  ContentRecommendation, 
  GraphNode, 
  GraphEdge, 
  NodeType, 
  EdgeType,
  GraphPath
} from './types';
import { AIVideo } from '../aiService';

/**
 * Recommendation Engine class
 */
export class RecommendationEngine {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Get content recommendations for a user
   */
  public async getRecommendations(
    userId: string, 
    count: number = 5, 
    includeReasons: boolean = true
  ): Promise<ContentRecommendation[]> {
    console.log(`Getting ${count} recommendations for user ${userId}`);
    
    // Get user node
    const userNode = this.graphStore.getNode(userId);
    if (!userNode) {
      console.error(`User node ${userId} not found`);
      return [];
    }
    
    // Get all video nodes
    const allVideos = this.graphStore.getNodesByType(NodeType.VIDEO);
    
    // Get videos the user has already viewed
    const viewedEdges = this.graphStore.getOutgoingEdges(userId)
      .filter(edge => edge.type === EdgeType.VIEWED);
    
    const viewedVideoIds = new Set(viewedEdges.map(edge => edge.target));
    
    // Filter out videos the user has already viewed
    const unwatchedVideos = allVideos.filter(video => !viewedVideoIds.has(video.id));
    
    if (unwatchedVideos.length === 0) {
      console.log('No unwatched videos found');
      return [];
    }
    
    // Score each video
    const scoredVideos = await Promise.all(
      unwatchedVideos.map(async video => {
        const score = await this.calculateRecommendationScore(userId, video.id);
        const reasons = includeReasons 
          ? await this.generateRecommendationReasons(userId, video.id) 
          : [];
        
        return {
          videoId: video.id,
          score,
          reasons
        };
      })
    );
    
    // Sort by score (descending) and take the top 'count'
    const recommendations = scoredVideos
      .sort((a, b) => b.score - a.score)
      .slice(0, count);
    
    console.log(`Generated ${recommendations.length} recommendations for user ${userId}`);
    return recommendations;
  }

  /**
   * Calculate recommendation score for a video
   */
  private async calculateRecommendationScore(userId: string, videoId: string): Promise<number> {
    let score = 0;
    
    // Get video node
    const videoNode = this.graphStore.getNode(videoId);
    if (!videoNode) return 0;
    
    // 1. Content-based scoring
    score += await this.calculateContentBasedScore(userId, videoId);
    
    // 2. Collaborative filtering score
    score += await this.calculateCollaborativeScore(userId, videoId);
    
    // 3. Graph-based scoring
    score += await this.calculateGraphBasedScore(userId, videoId);
    
    // 4. Recency boost
    score += this.calculateRecencyBoost(videoNode);
    
    // 5. Diversity factor
    score += await this.calculateDiversityFactor(userId, videoId);
    
    return score;
  }

  /**
   * Calculate content-based recommendation score
   */
  private async calculateContentBasedScore(userId: string, videoId: string): Promise<number> {
    let score = 0;
    
    // Get user node
    const userNode = this.graphStore.getNode(userId);
    if (!userNode) return 0;
    
    // Get video node
    const videoNode = this.graphStore.getNode(videoId);
    if (!videoNode) return 0;
    
    // Get user's viewed videos
    const viewedEdges = this.graphStore.getOutgoingEdges(userId)
      .filter(edge => edge.type === EdgeType.VIEWED);
    
    // If user has no viewing history, return base score
    if (viewedEdges.length === 0) return 0.5;
    
    // Get categories of videos the user has viewed
    const viewedVideoIds = viewedEdges.map(edge => edge.target);
    const viewedVideos = viewedVideoIds
      .map(id => this.graphStore.getNode(id))
      .filter((node): node is GraphNode => node !== undefined);
    
    // Count category occurrences
    const categoryCount: Record<string, number> = {};
    viewedVideos.forEach(video => {
      const category = video.properties.category;
      if (category) {
        categoryCount[category] = (categoryCount[category] || 0) + 1;
      }
    });
    
    // Calculate category preference score
    const videoCategory = videoNode.properties.category;
    if (videoCategory && categoryCount[videoCategory]) {
      const categoryPreference = categoryCount[videoCategory] / viewedVideos.length;
      score += categoryPreference * 0.5; // Weight of 0.5 for category preference
    }
    
    // Similar calculation for creator preference
    const creatorCount: Record<string, number> = {};
    viewedVideos.forEach(video => {
      const creator = video.properties.creator;
      if (creator) {
        creatorCount[creator] = (creatorCount[creator] || 0) + 1;
      }
    });
    
    const videoCreator = videoNode.properties.creator;
    if (videoCreator && creatorCount[videoCreator]) {
      const creatorPreference = creatorCount[videoCreator] / viewedVideos.length;
      score += creatorPreference * 0.3; // Weight of 0.3 for creator preference
    }
    
    return score;
  }

  /**
   * Calculate collaborative filtering score
   */
  private async calculateCollaborativeScore(userId: string, videoId: string): Promise<number> {
    let score = 0;
    
    // Get all users who have viewed this video
    const viewerEdges = this.graphStore.getIncomingEdges(videoId)
      .filter(edge => edge.type === EdgeType.VIEWED);
    
    // If no one has viewed this video, return base score
    if (viewerEdges.length === 0) return 0.3;
    
    // Get users who have viewed this video
    const viewerIds = viewerEdges.map(edge => edge.source);
    
    // Get videos that the current user has viewed
    const userViewedEdges = this.graphStore.getOutgoingEdges(userId)
      .filter(edge => edge.type === EdgeType.VIEWED);
    
    const userViewedIds = userViewedEdges.map(edge => edge.target);
    
    // For each viewer, calculate similarity to current user
    let totalSimilarity = 0;
    let similarityCount = 0;
    
    for (const viewerId of viewerIds) {
      if (viewerId === userId) continue;
      
      // Get videos that this viewer has viewed
      const viewerViewedEdges = this.graphStore.getOutgoingEdges(viewerId)
        .filter(edge => edge.type === EdgeType.VIEWED);
      
      const viewerViewedIds = viewerViewedEdges.map(edge => edge.target);
      
      // Calculate Jaccard similarity
      const intersection = userViewedIds.filter(id => viewerViewedIds.includes(id));
      const union = new Set([...userViewedIds, ...viewerViewedIds]);
      
      const similarity = intersection.length / union.size;
      
      totalSimilarity += similarity;
      similarityCount++;
    }
    
    // Calculate average similarity
    const avgSimilarity = similarityCount > 0 ? totalSimilarity / similarityCount : 0;
    
    // Scale similarity to a score
    score = avgSimilarity * 0.4; // Weight of 0.4 for collaborative filtering
    
    return score;
  }

  /**
   * Calculate graph-based recommendation score
   */
  private async calculateGraphBasedScore(userId: string, videoId: string): Promise<number> {
    let score = 0;
    
    // Find paths between user and video
    const paths = this.graphStore.findPaths(userId, videoId, 3);
    
    if (paths.length === 0) return 0.1; // Base score if no paths
    
    // Calculate path-based score
    // Shorter paths and paths with higher weights are better
    let pathScore = 0;
    
    paths.forEach(path => {
      // Calculate total weight of the path
      let pathWeight = 0;
      path.forEach(edge => {
        pathWeight += edge.weight;
      });
      
      // Shorter paths are better
      const lengthFactor = 1 / (path.length + 1);
      
      // Combine length and weight factors
      pathScore += pathWeight * lengthFactor;
    });
    
    // Normalize path score
    score = Math.min(pathScore / paths.length, 1) * 0.3; // Weight of 0.3 for graph-based score
    
    return score;
  }

  /**
   * Calculate recency boost
   */
  private calculateRecencyBoost(videoNode: GraphNode): number {
    const now = new Date();
    const videoDate = videoNode.createdAt;
    
    // Calculate days since video was created
    const daysSinceCreation = (now.getTime() - videoDate.getTime()) / (1000 * 60 * 60 * 24);
    
    // Newer videos get a higher boost
    // Exponential decay function: boost = e^(-days/30)
    const recencyBoost = Math.exp(-daysSinceCreation / 30) * 0.2; // Weight of 0.2 for recency
    
    return recencyBoost;
  }

  /**
   * Calculate diversity factor
   */
  private async calculateDiversityFactor(userId: string, videoId: string): Promise<number> {
    // Get video node
    const videoNode = this.graphStore.getNode(videoId);
    if (!videoNode) return 0;
    
    // Get user's recently viewed videos
    const viewedEdges = this.graphStore.getOutgoingEdges(userId)
      .filter(edge => edge.type === EdgeType.VIEWED)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, 10); // Consider only the 10 most recent views
    
    if (viewedEdges.length === 0) return 0.1; // Base diversity score if no history
    
    // Get categories of recently viewed videos
    const recentCategories = new Set<string>();
    viewedEdges.forEach(edge => {
      const videoNode = this.graphStore.getNode(edge.target);
      if (videoNode && videoNode.properties.category) {
        recentCategories.add(videoNode.properties.category);
      }
    });
    
    // If the video's category is not in the recent categories, give it a diversity boost
    const videoCategory = videoNode.properties.category;
    if (videoCategory && !recentCategories.has(videoCategory)) {
      return 0.1; // Diversity boost
    }
    
    return 0;
  }

  /**
   * Generate reasons for a recommendation
   */
  private async generateRecommendationReasons(userId: string, videoId: string): Promise<string[]> {
    const reasons: string[] = [];
    
    // Get user node
    const userNode = this.graphStore.getNode(userId);
    if (!userNode) return reasons;
    
    // Get video node
    const videoNode = this.graphStore.getNode(videoId);
    if (!videoNode) return reasons;
    
    // 1. Category-based reason
    const videoCategory = videoNode.properties.category;
    if (videoCategory) {
      // Check if user has viewed videos in this category
      const viewedEdges = this.graphStore.getOutgoingEdges(userId)
        .filter(edge => edge.type === EdgeType.VIEWED);
      
      const viewedVideoIds = viewedEdges.map(edge => edge.target);
      const viewedVideos = viewedVideoIds
        .map(id => this.graphStore.getNode(id))
        .filter((node): node is GraphNode => node !== undefined);
      
      const categoryViews = viewedVideos.filter(video => 
        video.properties.category === videoCategory
      ).length;
      
      if (categoryViews > 0) {
        reasons.push(`Based on your interest in ${videoCategory} videos`);
      }
    }
    
    // 2. Creator-based reason
    const videoCreator = videoNode.properties.creator;
    if (videoCreator) {
      // Check if user has viewed videos by this creator
      const viewedEdges = this.graphStore.getOutgoingEdges(userId)
        .filter(edge => edge.type === EdgeType.VIEWED);
      
      const viewedVideoIds = viewedEdges.map(edge => edge.target);
      const viewedVideos = viewedVideoIds
        .map(id => this.graphStore.getNode(id))
        .filter((node): node is GraphNode => node !== undefined);
      
      const creatorViews = viewedVideos.filter(video => 
        video.properties.creator === videoCreator
      ).length;
      
      if (creatorViews > 0) {
        reasons.push(`Because you've watched videos from ${videoCreator}`);
      }
    }
    
    // 3. Similar users reason
    const similarUsers = await this.findSimilarUsers(userId);
    const videoViewers = this.graphStore.getIncomingEdges(videoId)
      .filter(edge => edge.type === EdgeType.VIEWED)
      .map(edge => edge.source);
    
    const similarViewers = similarUsers.filter(user => videoViewers.includes(user));
    
    if (similarViewers.length > 0) {
      reasons.push(`Popular among users with similar interests`);
    }
    
    // 4. Trending reason
    const isVideoTrending = await this.isVideoTrending(videoId);
    if (isVideoTrending) {
      reasons.push('Currently trending');
    }
    
    // 5. Diversity reason
    const isDiverseRecommendation = await this.isDiverseRecommendation(userId, videoId);
    if (isDiverseRecommendation) {
      reasons.push('To help you discover new content');
    }
    
    return reasons;
  }

  /**
   * Find users similar to the given user
   */
  private async findSimilarUsers(userId: string): Promise<string[]> {
    // Get all users
    const allUsers = this.graphStore.getNodesByType(NodeType.USER)
      .filter(user => user.id !== userId);
    
    // Get videos that the current user has viewed
    const userViewedEdges = this.graphStore.getOutgoingEdges(userId)
      .filter(edge => edge.type === EdgeType.VIEWED);
    
    const userViewedIds = userViewedEdges.map(edge => edge.target);
    
    // Calculate similarity for each user
    const userSimilarities = allUsers.map(user => {
      // Get videos that this user has viewed
      const viewedEdges = this.graphStore.getOutgoingEdges(user.id)
        .filter(edge => edge.type === EdgeType.VIEWED);
      
      const viewedIds = viewedEdges.map(edge => edge.target);
      
      // Calculate Jaccard similarity
      const intersection = userViewedIds.filter(id => viewedIds.includes(id));
      const union = new Set([...userViewedIds, ...viewedIds]);
      
      const similarity = intersection.length / union.size;
      
      return {
        userId: user.id,
        similarity
      };
    });
    
    // Sort by similarity (descending) and take the top 10
    const similarUsers = userSimilarities
      .sort((a, b) => b.similarity - a.similarity)
      .slice(0, 10)
      .map(user => user.userId);
    
    return similarUsers;
  }

  /**
   * Check if a video is trending
   */
  private async isVideoTrending(videoId: string): Promise<boolean> {
    // Get all view edges for this video
    const viewEdges = this.graphStore.getIncomingEdges(videoId)
      .filter(edge => edge.type === EdgeType.VIEWED);
    
    // If less than 5 views, not trending
    if (viewEdges.length < 5) return false;
    
    // Get views in the last 24 hours
    const now = new Date();
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
    
    const recentViews = viewEdges.filter(edge => 
      edge.createdAt.getTime() > oneDayAgo.getTime()
    );
    
    // If more than 50% of views are recent, consider it trending
    return recentViews.length / viewEdges.length > 0.5;
  }

  /**
   * Check if a recommendation adds diversity
   */
  private async isDiverseRecommendation(userId: string, videoId: string): Promise<boolean> {
    // Get video node
    const videoNode = this.graphStore.getNode(videoId);
    if (!videoNode) return false;
    
    // Get user's recently viewed videos
    const viewedEdges = this.graphStore.getOutgoingEdges(userId)
      .filter(edge => edge.type === EdgeType.VIEWED)
      .sort((a, b) => b.createdAt.getTime() - a.createdAt.getTime())
      .slice(0, 10); // Consider only the 10 most recent views
    
    if (viewedEdges.length === 0) return true; // If no history, any recommendation adds diversity
    
    // Get categories of recently viewed videos
    const recentCategories = new Set<string>();
    viewedEdges.forEach(edge => {
      const videoNode = this.graphStore.getNode(edge.target);
      if (videoNode && videoNode.properties.category) {
        recentCategories.add(videoNode.properties.category);
      }
    });
    
    // If the video's category is not in the recent categories, it adds diversity
    const videoCategory = videoNode.properties.category;
    return videoCategory !== undefined && !recentCategories.has(videoCategory);
  }
} 