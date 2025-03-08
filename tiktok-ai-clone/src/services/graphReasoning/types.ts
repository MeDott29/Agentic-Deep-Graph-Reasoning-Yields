/**
 * Types for the Graph Reasoning System
 */

import { AIVideo, UserBehavior, UserInteraction } from '../aiService';

/**
 * Node types in our knowledge graph
 */
export enum NodeType {
  USER = 'USER',
  VIDEO = 'VIDEO',
  CATEGORY = 'CATEGORY',
  CREATOR = 'CREATOR',
  TOPIC = 'TOPIC',
  TREND = 'TREND',
  MUSIC = 'MUSIC',
  AGENT = 'AGENT',
  INTERACTION = 'INTERACTION'
}

/**
 * Edge types in our knowledge graph
 */
export enum EdgeType {
  VIEWED = 'VIEWED',
  LIKED = 'LIKED',
  CREATED = 'CREATED',
  BELONGS_TO = 'BELONGS_TO',
  RELATED_TO = 'RELATED_TO',
  INTERACTED_WITH = 'INTERACTED_WITH',
  FOLLOWS = 'FOLLOWS',
  COMMENTED_ON = 'COMMENTED_ON',
  SHARED = 'SHARED',
  USES = 'USES',
  SIMILAR_TO = 'SIMILAR_TO',
  INSPIRED_BY = 'INSPIRED_BY'
}

/**
 * Node in our knowledge graph
 */
export interface GraphNode {
  id: string;
  type: NodeType;
  properties: Record<string, any>;
  embeddings?: number[]; // Vector embeddings for semantic similarity
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Edge in our knowledge graph
 */
export interface GraphEdge {
  id: string;
  type: EdgeType;
  source: string; // Source node ID
  target: string; // Target node ID
  weight: number; // Edge weight (strength of connection)
  properties: Record<string, any>;
  createdAt: Date;
  updatedAt: Date;
}

/**
 * Knowledge Graph
 */
export interface KnowledgeGraph {
  nodes: Map<string, GraphNode>;
  edges: Map<string, GraphEdge>;
  // Adjacency list for quick traversal
  adjacencyList: Map<string, Map<string, string[]>>;
}

/**
 * Content generation prompt
 */
export interface ContentGenerationPrompt {
  topic?: string;
  style?: string;
  trend?: string;
  targetAudience?: string;
  relatedContent?: string[];
  inspirations?: string[];
  constraints?: string[];
  format?: 'video' | 'comment' | 'interaction';
  length?: 'short' | 'medium' | 'long';
}

/**
 * Agent interaction context
 */
export interface AgentInteractionContext {
  agent1Id: string;
  agent2Id: string;
  topic: string;
  interactionType: string;
  previousInteractions?: string[];
  userPreferences?: Record<string, any>;
}

/**
 * Graph traversal path
 */
export interface GraphPath {
  nodes: GraphNode[];
  edges: GraphEdge[];
  totalWeight: number;
}

/**
 * Content recommendation
 */
export interface ContentRecommendation {
  videoId: string;
  score: number;
  reasons: string[];
  path?: GraphPath;
}

/**
 * Trend analysis result
 */
export interface TrendAnalysis {
  trendId: string;
  name: string;
  strength: number; // 0-1 scale
  growth: number; // Rate of change
  relatedTopics: string[];
  relatedVideos: string[];
  predictedLifespan: number; // In days
}

/**
 * User segment
 */
export interface UserSegment {
  id: string;
  name: string;
  description: string;
  userIds: string[];
  commonInterests: string[];
  commonBehaviors: Record<string, any>;
  size: number;
}

/**
 * Content generation result
 */
export interface ContentGenerationResult {
  content: string;
  metadata: Record<string, any>;
  relatedTopics: string[];
  targetAudience: string[];
  predictedEngagement: number; // 0-1 scale
}

/**
 * Graph reasoning query
 */
export interface GraphQuery {
  type: 'recommendation' | 'generation' | 'analysis' | 'discovery';
  parameters: Record<string, any>;
  context?: Record<string, any>;
}

/**
 * Graph reasoning result
 */
export interface GraphResult {
  query: GraphQuery;
  results: any[];
  metadata: Record<string, any>;
  executionTime: number; // In milliseconds
} 