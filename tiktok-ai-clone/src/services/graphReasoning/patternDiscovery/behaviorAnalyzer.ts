/**
 * Behavior Analyzer - Analyzes user behavior patterns in the graph
 */

import { GraphStore } from '../graphStore';
import { 
  NodeType, 
  GraphNode 
} from '../types';
import { EngagementAnalyzer } from './behaviorAnalysis/engagementAnalyzer';
import { ContentPreferenceAnalyzer } from './behaviorAnalysis/contentPreferenceAnalyzer';
import { TemporalPatternAnalyzer } from './behaviorAnalysis/temporalPatternAnalyzer';
import { SocialInteractionAnalyzer } from './behaviorAnalysis/socialInteractionAnalyzer';
import { BehaviorSegmentAnalyzer } from './behaviorAnalysis/behaviorSegmentAnalyzer';
import { BehaviorPattern } from './behaviorAnalysis/types';

/**
 * Behavior Analyzer class
 */
export class BehaviorAnalyzer {
  private graphStore: GraphStore;
  private engagementAnalyzer: EngagementAnalyzer;
  private contentPreferenceAnalyzer: ContentPreferenceAnalyzer;
  private temporalPatternAnalyzer: TemporalPatternAnalyzer;
  private socialInteractionAnalyzer: SocialInteractionAnalyzer;
  private behaviorSegmentAnalyzer: BehaviorSegmentAnalyzer;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
    this.engagementAnalyzer = new EngagementAnalyzer(graphStore);
    this.contentPreferenceAnalyzer = new ContentPreferenceAnalyzer(graphStore);
    this.temporalPatternAnalyzer = new TemporalPatternAnalyzer(graphStore);
    this.socialInteractionAnalyzer = new SocialInteractionAnalyzer(graphStore);
    this.behaviorSegmentAnalyzer = new BehaviorSegmentAnalyzer(graphStore);
  }

  /**
   * Analyze behavior patterns
   */
  public async analyzeBehaviorPatterns(
    behaviorType: string = 'engagement',
    userSegment: string = 'all',
    timeframe: string = 'month',
    minPatternSupport: number = 0.2
  ): Promise<BehaviorPattern[]> {
    console.log(`Analyzing ${behaviorType} behavior patterns for ${userSegment} users`);
    
    // Get user nodes
    const userNodes = this.getUserNodes(userSegment);
    
    if (userNodes.length === 0) {
      console.log('No users found for the specified segment');
      return [];
    }
    
    // Calculate time range
    const timeRange = this.calculateTimeRange(timeframe);
    
    // Analyze patterns based on behavior type
    let patterns: BehaviorPattern[] = [];
    
    switch (behaviorType) {
      case 'engagement':
        patterns = await this.engagementAnalyzer.analyzeEngagementPatterns(
          userNodes, 
          timeRange.startTime, 
          timeRange.endTime, 
          minPatternSupport
        );
        break;
      case 'content-preference':
        patterns = await this.contentPreferenceAnalyzer.analyzeContentPreferences(
          userNodes, 
          timeRange.startTime, 
          timeRange.endTime, 
          minPatternSupport
        );
        break;
      case 'temporal':
        patterns = await this.temporalPatternAnalyzer.analyzeTemporalPatterns(
          userNodes, 
          timeRange.startTime, 
          timeRange.endTime, 
          minPatternSupport
        );
        break;
      case 'social-interaction':
        patterns = await this.socialInteractionAnalyzer.analyzeSocialInteractions(
          userNodes, 
          timeRange.startTime, 
          timeRange.endTime, 
          minPatternSupport
        );
        break;
      case 'segment':
        patterns = await this.behaviorSegmentAnalyzer.analyzeUserSegments(
          userNodes, 
          timeRange.startTime, 
          timeRange.endTime, 
          minPatternSupport
        );
        break;
      default:
        console.warn(`Unknown behavior type: ${behaviorType}. Falling back to engagement.`);
        patterns = await this.engagementAnalyzer.analyzeEngagementPatterns(
          userNodes, 
          timeRange.startTime, 
          timeRange.endTime, 
          minPatternSupport
        );
    }
    
    console.log(`Found ${patterns.length} behavior patterns`);
    return patterns;
  }

  /**
   * Get user nodes based on segment
   */
  private getUserNodes(userSegment: string): GraphNode[] {
    // Get all user nodes
    const allUserNodes = this.graphStore.getNodesByType(NodeType.USER);
    
    // If segment is 'all', return all users
    if (userSegment === 'all') {
      return allUserNodes;
    }
    
    // Otherwise, filter by segment
    return allUserNodes.filter(user => {
      // Check if user has segment property
      const segments = user.properties.segments || [];
      return segments.includes(userSegment);
    });
  }

  /**
   * Calculate time range based on timeframe
   */
  private calculateTimeRange(timeframe: string): { startTime: Date; endTime: Date } {
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
      case 'year':
        startTime = new Date(now.getTime() - 365 * 24 * 60 * 60 * 1000);
        break;
      case 'all':
        startTime = new Date(0); // Beginning of time
        break;
      default:
        startTime = new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000); // Default to month
    }
    
    return { startTime, endTime: now };
  }
} 