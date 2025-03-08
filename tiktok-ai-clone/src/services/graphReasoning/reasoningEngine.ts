/**
 * Reasoning Engine - Main coordinator for graph reasoning operations
 */

import { GraphStore } from './graphStore';
import { RecommendationEngine } from './recommendationEngine';
import { ContentGenerator } from './contentGenerator';
import { TrendAnalyzer } from './trendAnalyzer';
import { PatternDiscovery } from './patternDiscovery';
import { 
  GraphQuery, 
  GraphResult, 
  ContentGenerationPrompt, 
  ContentRecommendation,
  TrendAnalysis,
  UserSegment,
  ContentGenerationResult
} from './types';

/**
 * Reasoning Engine class
 */
export class ReasoningEngine {
  private graphStore: GraphStore;
  private recommendationEngine: RecommendationEngine;
  private contentGenerator: ContentGenerator;
  private trendAnalyzer: TrendAnalyzer;
  private patternDiscovery: PatternDiscovery;
  private static instance: ReasoningEngine;

  /**
   * Private constructor for singleton pattern
   */
  private constructor() {
    this.graphStore = GraphStore.getInstance();
    this.recommendationEngine = new RecommendationEngine(this.graphStore);
    this.contentGenerator = new ContentGenerator(this.graphStore);
    this.trendAnalyzer = new TrendAnalyzer(this.graphStore);
    this.patternDiscovery = new PatternDiscovery(this.graphStore);
  }

  /**
   * Get singleton instance
   */
  public static getInstance(): ReasoningEngine {
    if (!ReasoningEngine.instance) {
      ReasoningEngine.instance = new ReasoningEngine();
    }
    return ReasoningEngine.instance;
  }

  /**
   * Execute a graph query
   */
  public async executeQuery(query: GraphQuery): Promise<GraphResult> {
    console.log(`Executing query of type: ${query.type}`);
    const startTime = Date.now();
    
    let results: any[] = [];
    let metadata: Record<string, any> = {};
    
    try {
      switch (query.type) {
        case 'recommendation':
          results = await this.executeRecommendationQuery(query);
          break;
        case 'generation':
          results = await this.executeGenerationQuery(query);
          break;
        case 'analysis':
          results = await this.executeAnalysisQuery(query);
          break;
        case 'discovery':
          results = await this.executeDiscoveryQuery(query);
          break;
        default:
          throw new Error(`Unknown query type: ${query.type}`);
      }
      
      metadata.success = true;
    } catch (error) {
      console.error('Error executing query:', error);
      metadata.success = false;
      metadata.error = error instanceof Error ? error.message : 'Unknown error';
    }
    
    const executionTime = Date.now() - startTime;
    
    return {
      query,
      results,
      metadata,
      executionTime
    };
  }

  /**
   * Execute a recommendation query
   */
  private async executeRecommendationQuery(query: GraphQuery): Promise<ContentRecommendation[]> {
    const { userId, count = 5, includeReasons = true } = query.parameters;
    
    if (!userId) {
      throw new Error('userId is required for recommendation queries');
    }
    
    return this.recommendationEngine.getRecommendations(userId, count, includeReasons);
  }

  /**
   * Execute a content generation query
   */
  private async executeGenerationQuery(query: GraphQuery): Promise<ContentGenerationResult[]> {
    const { prompt, count = 1 } = query.parameters;
    
    if (!prompt) {
      throw new Error('prompt is required for generation queries');
    }
    
    return this.contentGenerator.generateContent(prompt as ContentGenerationPrompt, count);
  }

  /**
   * Execute an analysis query
   */
  private async executeAnalysisQuery(query: GraphQuery): Promise<TrendAnalysis[]> {
    const { type, timeframe = 'week', count = 5 } = query.parameters;
    
    if (!type) {
      throw new Error('type is required for analysis queries');
    }
    
    switch (type) {
      case 'trends':
        return this.trendAnalyzer.analyzeTrends(timeframe, count);
      case 'userSegments':
        return this.trendAnalyzer.analyzeUserSegments(count) as unknown as TrendAnalysis[];
      default:
        throw new Error(`Unknown analysis type: ${type}`);
    }
  }

  /**
   * Execute a discovery query
   */
  private async executeDiscoveryQuery(query: GraphQuery): Promise<any[]> {
    const { type, parameters = {} } = query.parameters;
    
    if (!type) {
      throw new Error('type is required for discovery queries');
    }
    
    switch (type) {
      case 'patterns':
        return this.patternDiscovery.discoverPatterns(parameters);
      case 'communities':
        return this.patternDiscovery.discoverCommunities(parameters);
      case 'anomalies':
        return this.patternDiscovery.discoverAnomalies(parameters);
      default:
        throw new Error(`Unknown discovery type: ${type}`);
    }
  }

  /**
   * Get recommendations for a user
   */
  public async getRecommendationsForUser(userId: string, count: number = 5): Promise<ContentRecommendation[]> {
    return this.recommendationEngine.getRecommendations(userId, count);
  }

  /**
   * Generate content based on a prompt
   */
  public async generateContent(prompt: ContentGenerationPrompt): Promise<ContentGenerationResult> {
    const results = await this.contentGenerator.generateContent(prompt, 1);
    return results[0];
  }

  /**
   * Analyze current trends
   */
  public async analyzeTrends(timeframe: string = 'week', count: number = 5): Promise<TrendAnalysis[]> {
    return this.trendAnalyzer.analyzeTrends(timeframe, count);
  }

  /**
   * Analyze user segments
   */
  public async analyzeUserSegments(count: number = 5): Promise<UserSegment[]> {
    return this.trendAnalyzer.analyzeUserSegments(count);
  }

  /**
   * Discover patterns in the graph
   */
  public async discoverPatterns(parameters: Record<string, any> = {}): Promise<any[]> {
    return this.patternDiscovery.discoverPatterns(parameters);
  }

  /**
   * Get the graph store instance
   */
  public getGraphStore(): GraphStore {
    return this.graphStore;
  }
} 