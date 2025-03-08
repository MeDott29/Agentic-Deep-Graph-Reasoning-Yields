/**
 * Temporal Pattern Analyzer - Analyzes user temporal patterns
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
  TemporalPattern, 
  UserInteraction,
  UserSession
} from './types';

/**
 * Temporal Pattern Analyzer class
 */
export class TemporalPatternAnalyzer {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Analyze temporal patterns
   */
  public async analyzeTemporalPatterns(
    userNodes: GraphNode[],
    startTime: Date,
    endTime: Date,
    minPatternSupport: number = 0.2
  ): Promise<BehaviorPattern[]> {
    console.log(`Analyzing temporal patterns for ${userNodes.length} users`);
    
    // Get user interactions within the time range
    const userInteractions = this.getUserInteractions(userNodes, startTime, endTime);
    
    if (Object.keys(userInteractions).length === 0) {
      console.log('No user interactions found in the specified time range');
      return [];
    }
    
    // Group interactions into sessions
    const userSessions = this.groupInteractionsIntoSessions(userInteractions);
    
    // Analyze different temporal patterns
    const patterns: BehaviorPattern[] = [];
    
    // 1. Time of day pattern
    const timeOfDayPatterns = await this.detectTimeOfDayPatterns(
      userNodes, 
      userInteractions, 
      userSessions, 
      minPatternSupport
    );
    
    patterns.push(...timeOfDayPatterns);
    
    // 2. Day of week pattern
    const dayOfWeekPatterns = await this.detectDayOfWeekPatterns(
      userNodes, 
      userInteractions, 
      userSessions, 
      minPatternSupport
    );
    
    patterns.push(...dayOfWeekPatterns);
    
    // 3. Session duration pattern
    const sessionDurationPatterns = await this.detectSessionDurationPatterns(
      userNodes, 
      userSessions, 
      minPatternSupport
    );
    
    patterns.push(...sessionDurationPatterns);
    
    // 4. Session frequency pattern
    const sessionFrequencyPatterns = await this.detectSessionFrequencyPatterns(
      userNodes, 
      userSessions, 
      startTime,
      endTime,
      minPatternSupport
    );
    
    patterns.push(...sessionFrequencyPatterns);
    
    console.log(`Found ${patterns.length} temporal patterns`);
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
      
      // Sort by timestamp
      userInteractions[userId].sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
    }
    
    return userInteractions;
  }

  /**
   * Group interactions into sessions
   */
  private groupInteractionsIntoSessions(
    userInteractions: Record<string, UserInteraction[]>
  ): Record<string, UserSession[]> {
    const userSessions: Record<string, UserSession[]> = {};
    const sessionTimeoutMs = 30 * 60 * 1000; // 30 minutes
    
    for (const userId in userInteractions) {
      const interactions = userInteractions[userId];
      userSessions[userId] = [];
      
      if (interactions.length === 0) {
        continue;
      }
      
      // Sort interactions by timestamp
      interactions.sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());
      
      // Initialize first session
      let currentSession: UserSession = {
        userId,
        startTime: interactions[0].timestamp,
        endTime: interactions[0].timestamp,
        interactions: [interactions[0]],
        duration: 0
      };
      
      // Group interactions into sessions
      for (let i = 1; i < interactions.length; i++) {
        const interaction = interactions[i];
        const timeSinceLastInteraction = interaction.timestamp.getTime() - currentSession.endTime.getTime();
        
        if (timeSinceLastInteraction <= sessionTimeoutMs) {
          // Add to current session
          currentSession.interactions.push(interaction);
          currentSession.endTime = interaction.timestamp;
        } else {
          // Calculate duration of current session
          currentSession.duration = (currentSession.endTime.getTime() - currentSession.startTime.getTime()) / 1000;
          
          // Save current session
          userSessions[userId].push(currentSession);
          
          // Start new session
          currentSession = {
            userId,
            startTime: interaction.timestamp,
            endTime: interaction.timestamp,
            interactions: [interaction],
            duration: 0
          };
        }
      }
      
      // Calculate duration of last session
      currentSession.duration = (currentSession.endTime.getTime() - currentSession.startTime.getTime()) / 1000;
      
      // Save last session
      userSessions[userId].push(currentSession);
    }
    
    return userSessions;
  }

  /**
   * Detect time of day patterns
   */
  private async detectTimeOfDayPatterns(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    userSessions: Record<string, UserSession[]>,
    minPatternSupport: number
  ): Promise<TemporalPattern[]> {
    console.log('Detecting time of day patterns');
    
    // Define time of day segments
    const timeSegments = {
      'morning': { start: 5, end: 11 }, // 5:00 - 11:59
      'afternoon': { start: 12, end: 17 }, // 12:00 - 17:59
      'evening': { start: 18, end: 21 }, // 18:00 - 21:59
      'night': { start: 22, end: 4 } // 22:00 - 4:59
    };
    
    // Calculate time of day activity for each user
    const userTimeOfDayActivity: Record<string, Record<string, number>> = {};
    
    for (const userId in userSessions) {
      const sessions = userSessions[userId];
      userTimeOfDayActivity[userId] = {
        'morning': 0,
        'afternoon': 0,
        'evening': 0,
        'night': 0
      };
      
      // Count sessions by time of day
      for (const session of sessions) {
        const hour = session.startTime.getHours();
        
        if (hour >= timeSegments.morning.start && hour <= timeSegments.morning.end) {
          userTimeOfDayActivity[userId].morning++;
        } else if (hour >= timeSegments.afternoon.start && hour <= timeSegments.afternoon.end) {
          userTimeOfDayActivity[userId].afternoon++;
        } else if (hour >= timeSegments.evening.start && hour <= timeSegments.evening.end) {
          userTimeOfDayActivity[userId].evening++;
        } else {
          userTimeOfDayActivity[userId].night++;
        }
      }
      
      // Normalize activity
      const totalSessions = Object.values(userTimeOfDayActivity[userId]).reduce((sum, count) => sum + count, 0);
      
      if (totalSessions > 0) {
        for (const segment in userTimeOfDayActivity[userId]) {
          userTimeOfDayActivity[userId][segment] /= totalSessions;
        }
      }
    }
    
    // Find dominant time of day for each user
    const userDominantTimeOfDay: Record<string, string> = {};
    
    for (const userId in userTimeOfDayActivity) {
      const activity = userTimeOfDayActivity[userId];
      let maxActivity = 0;
      let dominantTimeOfDay = '';
      
      for (const segment in activity) {
        if (activity[segment] > maxActivity) {
          maxActivity = activity[segment];
          dominantTimeOfDay = segment;
        }
      }
      
      if (maxActivity > 0.4) { // Threshold for dominant time of day
        userDominantTimeOfDay[userId] = dominantTimeOfDay;
      }
    }
    
    // Group users by dominant time of day
    const timeOfDayUsers: Record<string, GraphNode[]> = {};
    
    for (const userId in userDominantTimeOfDay) {
      const timeOfDay = userDominantTimeOfDay[userId];
      
      if (!timeOfDayUsers[timeOfDay]) {
        timeOfDayUsers[timeOfDay] = [];
      }
      
      const userNode = userNodes.find(node => node.id === userId);
      
      if (userNode) {
        timeOfDayUsers[timeOfDay].push(userNode);
      }
    }
    
    // Create patterns for each time of day with sufficient support
    const patterns: TemporalPattern[] = [];
    
    for (const timeOfDay in timeOfDayUsers) {
      const users = timeOfDayUsers[timeOfDay];
      const support = userNodes.length > 0 ? users.length / userNodes.length : 0;
      
      if (support < minPatternSupport) {
        continue;
      }
      
      // Calculate average metrics
      const avgTimeOfDay: Record<string, number> = {
        'morning': 0,
        'afternoon': 0,
        'evening': 0,
        'night': 0
      };
      
      for (const segment in avgTimeOfDay) {
        avgTimeOfDay[segment] = this.calculateAverage(
          users.map(user => userTimeOfDayActivity[user.id]?.[segment] || 0)
        );
      }
      
      // Calculate average day of week activity (placeholder)
      const avgDayOfWeek: Record<string, number> = {
        'monday': 0,
        'tuesday': 0,
        'wednesday': 0,
        'thursday': 0,
        'friday': 0,
        'saturday': 0,
        'sunday': 0
      };
      
      // Calculate average session metrics
      const avgSessionDuration = this.calculateAverage(
        users.flatMap(user => userSessions[user.id]?.map(session => session.duration) || [])
      );
      
      const avgSessionFrequency = this.calculateAverage(
        users.map(user => userSessions[user.id]?.length || 0)
      );
      
      // Get related nodes and edges
      const relatedNodes: GraphNode[] = [];
      const relatedEdges: GraphEdge[] = [];
      
      // Add video nodes and edges
      for (const user of users) {
        const interactions = userInteractions[user.id] || [];
        
        for (const interaction of interactions) {
          const interactionHour = interaction.timestamp.getHours();
          let isInTimeSegment = false;
          
          if (timeOfDay === 'morning' && interactionHour >= timeSegments.morning.start && interactionHour <= timeSegments.morning.end) {
            isInTimeSegment = true;
          } else if (timeOfDay === 'afternoon' && interactionHour >= timeSegments.afternoon.start && interactionHour <= timeSegments.afternoon.end) {
            isInTimeSegment = true;
          } else if (timeOfDay === 'evening' && interactionHour >= timeSegments.evening.start && interactionHour <= timeSegments.evening.end) {
            isInTimeSegment = true;
          } else if (timeOfDay === 'night' && (interactionHour >= timeSegments.night.start || interactionHour <= timeSegments.night.end)) {
            isInTimeSegment = true;
          }
          
          if (isInTimeSegment) {
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
      }
      
      // Create pattern
      const pattern: TemporalPattern = {
        id: `pattern-time-of-day-${timeOfDay}-${Date.now()}`,
        type: BehaviorPatternType.TEMPORAL,
        users,
        relatedNodes,
        relatedEdges,
        support,
        confidence: 0.7, // Good confidence for time of day patterns
        description: `${timeOfDay} activity pattern with ${users.length} users`,
        detectionTime: new Date(),
        temporalMetrics: {
          timeOfDay: avgTimeOfDay,
          dayOfWeek: avgDayOfWeek,
          sessionDuration: avgSessionDuration,
          sessionFrequency: avgSessionFrequency
        }
      };
      
      patterns.push(pattern);
    }
    
    return patterns;
  }

  /**
   * Detect day of week patterns
   */
  private async detectDayOfWeekPatterns(
    userNodes: GraphNode[],
    userInteractions: Record<string, UserInteraction[]>,
    userSessions: Record<string, UserSession[]>,
    minPatternSupport: number
  ): Promise<TemporalPattern[]> {
    console.log('Detecting day of week patterns');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
  }

  /**
   * Detect session duration patterns
   */
  private async detectSessionDurationPatterns(
    userNodes: GraphNode[],
    userSessions: Record<string, UserSession[]>,
    minPatternSupport: number
  ): Promise<TemporalPattern[]> {
    console.log('Detecting session duration patterns');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
  }

  /**
   * Detect session frequency patterns
   */
  private async detectSessionFrequencyPatterns(
    userNodes: GraphNode[],
    userSessions: Record<string, UserSession[]>,
    startTime: Date,
    endTime: Date,
    minPatternSupport: number
  ): Promise<TemporalPattern[]> {
    console.log('Detecting session frequency patterns');
    
    // Implementation details omitted for brevity
    
    // This is a placeholder implementation
    return [];
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