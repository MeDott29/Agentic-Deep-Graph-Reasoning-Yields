/**
 * Types for Behavior Analysis
 */

import { GraphNode, GraphEdge } from '../../types';

/**
 * Behavior Pattern interface
 */
export interface BehaviorPattern {
  id: string;
  type: BehaviorPatternType;
  users: GraphNode[];
  relatedNodes: GraphNode[];
  relatedEdges: GraphEdge[];
  support: number; // Frequency of occurrence (0-1)
  confidence: number; // Confidence score (0-1)
  description: string;
  detectionTime: Date;
}

/**
 * Behavior Pattern Type enum
 */
export enum BehaviorPatternType {
  ENGAGEMENT = 'engagement',
  CONTENT_PREFERENCE = 'content-preference',
  TEMPORAL = 'temporal',
  SOCIAL_INTERACTION = 'social-interaction',
  SEGMENT = 'segment'
}

/**
 * Engagement Pattern interface
 */
export interface EngagementPattern extends BehaviorPattern {
  type: BehaviorPatternType.ENGAGEMENT;
  engagementMetrics: {
    viewDuration: number; // Average view duration in seconds
    completionRate: number; // Average completion rate (0-1)
    interactionRate: number; // Average interaction rate (0-1)
    returnRate: number; // Average return rate (0-1)
  };
}

/**
 * Content Preference Pattern interface
 */
export interface ContentPreferencePattern extends BehaviorPattern {
  type: BehaviorPatternType.CONTENT_PREFERENCE;
  preferenceMetrics: {
    categories: Record<string, number>; // Category to preference score mapping
    creators: Record<string, number>; // Creator to preference score mapping
    topics: Record<string, number>; // Topic to preference score mapping
    formats: Record<string, number>; // Format to preference score mapping
  };
}

/**
 * Temporal Pattern interface
 */
export interface TemporalPattern extends BehaviorPattern {
  type: BehaviorPatternType.TEMPORAL;
  temporalMetrics: {
    timeOfDay: Record<string, number>; // Hour to activity score mapping
    dayOfWeek: Record<string, number>; // Day to activity score mapping
    sessionDuration: number; // Average session duration in minutes
    sessionFrequency: number; // Average sessions per day
  };
}

/**
 * Social Interaction Pattern interface
 */
export interface SocialInteractionPattern extends BehaviorPattern {
  type: BehaviorPatternType.SOCIAL_INTERACTION;
  socialMetrics: {
    followRate: number; // Average follow rate (0-1)
    commentRate: number; // Average comment rate (0-1)
    shareRate: number; // Average share rate (0-1)
    responseRate: number; // Average response rate (0-1)
    influencerInteractionRate: number; // Average interaction rate with influencers (0-1)
  };
}

/**
 * User Segment Pattern interface
 */
export interface UserSegmentPattern extends BehaviorPattern {
  type: BehaviorPatternType.SEGMENT;
  segmentMetrics: {
    size: number; // Segment size
    cohesion: number; // Segment cohesion (0-1)
    stability: number; // Segment stability over time (0-1)
    distinctiveness: number; // Segment distinctiveness (0-1)
    growthRate: number; // Segment growth rate
  };
}

/**
 * User Interaction interface
 */
export interface UserInteraction {
  userId: string;
  videoId: string;
  action: 'view' | 'like' | 'comment' | 'share' | 'follow';
  timestamp: Date;
  duration?: number; // For view actions
  metadata?: Record<string, any>;
}

/**
 * User Session interface
 */
export interface UserSession {
  userId: string;
  startTime: Date;
  endTime: Date;
  interactions: UserInteraction[];
  duration: number; // In seconds
}

/**
 * Content Category interface
 */
export interface ContentCategory {
  id: string;
  name: string;
  parentCategory?: string;
  description?: string;
}

/**
 * Content Creator interface
 */
export interface ContentCreator {
  id: string;
  name: string;
  categories: string[];
  popularity: number; // 0-1 scale
}

/**
 * Content Topic interface
 */
export interface ContentTopic {
  id: string;
  name: string;
  categories: string[];
  popularity: number; // 0-1 scale
} 