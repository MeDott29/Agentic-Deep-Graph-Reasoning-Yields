/**
 * Pattern Discovery - Main coordinator for pattern discovery operations
 */

import { GraphStore } from './graphStore';
import { PatternDetector } from './patternDiscovery/patternDetector';
import { CommunityDetector } from './patternDiscovery/communityDetector';
import { AnomalyDetector } from './patternDiscovery/anomalyDetector';
import { EmergingTrendDetector } from './patternDiscovery/emergingTrendDetector';
import { BehaviorAnalyzer } from './patternDiscovery/behaviorAnalyzer';

/**
 * Pattern Discovery class
 */
export class PatternDiscovery {
  private graphStore: GraphStore;
  private patternDetector: PatternDetector;
  private communityDetector: CommunityDetector;
  private anomalyDetector: AnomalyDetector;
  private emergingTrendDetector: EmergingTrendDetector;
  private behaviorAnalyzer: BehaviorAnalyzer;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
    this.patternDetector = new PatternDetector(graphStore);
    this.communityDetector = new CommunityDetector(graphStore);
    this.anomalyDetector = new AnomalyDetector(graphStore);
    this.emergingTrendDetector = new EmergingTrendDetector(graphStore);
    this.behaviorAnalyzer = new BehaviorAnalyzer(graphStore);
  }

  /**
   * Discover patterns in the graph
   */
  public async discoverPatterns(parameters: Record<string, any> = {}): Promise<any[]> {
    console.log('Discovering patterns with parameters:', parameters);
    
    const { 
      patternType = 'frequent', 
      nodeTypes = [], 
      edgeTypes = [], 
      minSupport = 0.1,
      maxPatternSize = 5,
      timeframe = 'all'
    } = parameters;
    
    return this.patternDetector.detectPatterns(
      patternType,
      nodeTypes,
      edgeTypes,
      minSupport,
      maxPatternSize,
      timeframe
    );
  }

  /**
   * Discover communities in the graph
   */
  public async discoverCommunities(parameters: Record<string, any> = {}): Promise<any[]> {
    console.log('Discovering communities with parameters:', parameters);
    
    const { 
      algorithm = 'louvain', 
      nodeType = 'all',
      minCommunitySize = 3,
      maxCommunities = 10
    } = parameters;
    
    return this.communityDetector.detectCommunities(
      algorithm,
      nodeType,
      minCommunitySize,
      maxCommunities
    );
  }

  /**
   * Discover anomalies in the graph
   */
  public async discoverAnomalies(parameters: Record<string, any> = {}): Promise<any[]> {
    console.log('Discovering anomalies with parameters:', parameters);
    
    const { 
      anomalyType = 'structural', 
      nodeTypes = [],
      sensitivityThreshold = 0.8,
      timeframe = 'week'
    } = parameters;
    
    return this.anomalyDetector.detectAnomalies(
      anomalyType,
      nodeTypes,
      sensitivityThreshold,
      timeframe
    );
  }

  /**
   * Discover emerging trends
   */
  public async discoverEmergingTrends(parameters: Record<string, any> = {}): Promise<any[]> {
    console.log('Discovering emerging trends with parameters:', parameters);
    
    const { 
      timeframe = 'week',
      growthThreshold = 0.5,
      minActivity = 5,
      maxTrends = 10
    } = parameters;
    
    return this.emergingTrendDetector.detectEmergingTrends(
      timeframe,
      growthThreshold,
      minActivity,
      maxTrends
    );
  }

  /**
   * Analyze user behavior patterns
   */
  public async analyzeBehaviorPatterns(parameters: Record<string, any> = {}): Promise<any[]> {
    console.log('Analyzing behavior patterns with parameters:', parameters);
    
    const { 
      behaviorType = 'engagement',
      userSegment = 'all',
      timeframe = 'month',
      minPatternSupport = 0.2
    } = parameters;
    
    return this.behaviorAnalyzer.analyzeBehaviorPatterns(
      behaviorType,
      userSegment,
      timeframe,
      minPatternSupport
    );
  }
} 