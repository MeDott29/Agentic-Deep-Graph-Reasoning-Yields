/**
 * Anomaly Detector - Detects anomalies in the graph
 */

import { GraphStore } from '../graphStore';
import { 
  NodeType, 
  GraphNode, 
  GraphEdge 
} from '../types';

/**
 * Anomaly interface
 */
export interface Anomaly {
  id: string;
  type: 'structural' | 'temporal' | 'behavioral' | 'content';
  nodes: GraphNode[];
  edges: GraphEdge[];
  score: number; // Anomaly score (0-1)
  confidence: number; // Confidence in the anomaly (0-1)
  description: string;
  detectionTime: Date;
}

/**
 * Anomaly Detector class
 */
export class AnomalyDetector {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Detect anomalies in the graph
   */
  public async detectAnomalies(
    anomalyType: string = 'structural',
    nodeTypes: string[] = [],
    sensitivityThreshold: number = 0.8,
    timeframe: string = 'week'
  ): Promise<Anomaly[]> {
    console.log(`Detecting ${anomalyType} anomalies with sensitivity ${sensitivityThreshold}`);
    
    // Convert string types to enum types
    const nodeTypeEnums = nodeTypes.length > 0 
      ? nodeTypes.map(type => NodeType[type as keyof typeof NodeType]).filter(Boolean)
      : Object.values(NodeType);
    
    // Filter nodes by type and timeframe
    const filteredNodes = this.filterNodesByTypeAndTime(nodeTypeEnums, timeframe);
    
    // Detect anomalies based on type
    let anomalies: Anomaly[] = [];
    
    switch (anomalyType) {
      case 'structural':
        anomalies = await this.detectStructuralAnomalies(filteredNodes, sensitivityThreshold);
        break;
      case 'temporal':
        anomalies = await this.detectTemporalAnomalies(filteredNodes, sensitivityThreshold);
        break;
      case 'behavioral':
        anomalies = await this.detectBehavioralAnomalies(filteredNodes, sensitivityThreshold);
        break;
      case 'content':
        anomalies = await this.detectContentAnomalies(filteredNodes, sensitivityThreshold);
        break;
      default:
        console.warn(`Unknown anomaly type: ${anomalyType}. Falling back to structural.`);
        anomalies = await this.detectStructuralAnomalies(filteredNodes, sensitivityThreshold);
    }
    
    // Generate descriptions for anomalies
    const anomaliesWithDescriptions = this.generateAnomalyDescriptions(anomalies);
    
    console.log(`Found ${anomaliesWithDescriptions.length} anomalies`);
    return anomaliesWithDescriptions;
  }

  /**
   * Filter nodes by type and timeframe
   */
  private filterNodesByTypeAndTime(
    nodeTypes: NodeType[],
    timeframe: string
  ): GraphNode[] {
    // Get all nodes of the specified types
    let nodes: GraphNode[] = [];
    
    for (const nodeType of nodeTypes) {
      nodes = nodes.concat(this.graphStore.getNodesByType(nodeType));
    }
    
    // Filter by timeframe if not 'all'
    if (timeframe !== 'all') {
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
          startTime = new Date(0); // Beginning of time
      }
      
      nodes = nodes.filter(node => node.createdAt.getTime() >= startTime.getTime());
    }
    
    return nodes;
  }

  /**
   * Detect structural anomalies in the graph
   * 
   * Structural anomalies are unusual patterns in the graph structure,
   * such as isolated nodes, hub nodes, or bridge edges.
   */
  private async detectStructuralAnomalies(
    nodes: GraphNode[],
    sensitivityThreshold: number
  ): Promise<Anomaly[]> {
    console.log(`Detecting structural anomalies with ${nodes.length} nodes`);
    
    const anomalies: Anomaly[] = [];
    
    // 1. Detect isolated nodes
    const isolatedNodes = this.detectIsolatedNodes(nodes);
    
    // 2. Detect hub nodes
    const hubNodes = this.detectHubNodes(nodes);
    
    // 3. Detect bridge edges
    const bridgeEdges = this.detectBridgeEdges(nodes);
    
    // Create anomalies for isolated nodes
    isolatedNodes.forEach(node => {
      const score = 0.7; // Base score for isolated nodes
      
      // Only include if score exceeds threshold
      if (score >= sensitivityThreshold) {
        anomalies.push({
          id: `anomaly-isolated-${node.id}`,
          type: 'structural',
          nodes: [node],
          edges: [],
          score,
          confidence: 0.9, // High confidence for isolated nodes
          description: '', // Will be generated later
          detectionTime: new Date()
        });
      }
    });
    
    // Create anomalies for hub nodes
    hubNodes.forEach(({ node, hubScore }) => {
      // Only include if score exceeds threshold
      if (hubScore >= sensitivityThreshold) {
        // Get connected edges
        const outgoingEdges = this.graphStore.getOutgoingEdges(node.id);
        const incomingEdges = this.graphStore.getIncomingEdges(node.id);
        const connectedEdges = [...outgoingEdges, ...incomingEdges];
        
        anomalies.push({
          id: `anomaly-hub-${node.id}`,
          type: 'structural',
          nodes: [node],
          edges: connectedEdges,
          score: hubScore,
          confidence: 0.8, // Good confidence for hub nodes
          description: '', // Will be generated later
          detectionTime: new Date()
        });
      }
    });
    
    // Create anomalies for bridge edges
    bridgeEdges.forEach(({ edge, bridgeScore }) => {
      // Only include if score exceeds threshold
      if (bridgeScore >= sensitivityThreshold) {
        // Get connected nodes
        const sourceNode = this.graphStore.getNode(edge.source);
        const targetNode = this.graphStore.getNode(edge.target);
        const connectedNodes: GraphNode[] = [];
        
        if (sourceNode) connectedNodes.push(sourceNode);
        if (targetNode) connectedNodes.push(targetNode);
        
        anomalies.push({
          id: `anomaly-bridge-${edge.id}`,
          type: 'structural',
          nodes: connectedNodes,
          edges: [edge],
          score: bridgeScore,
          confidence: 0.7, // Moderate confidence for bridge edges
          description: '', // Will be generated later
          detectionTime: new Date()
        });
      }
    });
    
    return anomalies;
  }

  /**
   * Detect isolated nodes
   */
  private detectIsolatedNodes(nodes: GraphNode[]): GraphNode[] {
    return nodes.filter(node => {
      const outgoingEdges = this.graphStore.getOutgoingEdges(node.id);
      const incomingEdges = this.graphStore.getIncomingEdges(node.id);
      
      return outgoingEdges.length === 0 && incomingEdges.length === 0;
    });
  }

  /**
   * Detect hub nodes
   */
  private detectHubNodes(nodes: GraphNode[]): { node: GraphNode; hubScore: number }[] {
    // Calculate degree for each node
    const nodeDegrees = nodes.map(node => {
      const outgoingEdges = this.graphStore.getOutgoingEdges(node.id);
      const incomingEdges = this.graphStore.getIncomingEdges(node.id);
      const degree = outgoingEdges.length + incomingEdges.length;
      
      return { node, degree };
    });
    
    // Calculate mean and standard deviation of degrees
    const degrees = nodeDegrees.map(item => item.degree);
    const meanDegree = degrees.reduce((sum, degree) => sum + degree, 0) / degrees.length;
    
    const squaredDiffs = degrees.map(degree => Math.pow(degree - meanDegree, 2));
    const variance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / degrees.length;
    const stdDev = Math.sqrt(variance);
    
    // Identify hub nodes (nodes with degree > mean + 2*stdDev)
    return nodeDegrees
      .filter(item => item.degree > meanDegree + 2 * stdDev)
      .map(item => {
        // Calculate hub score (0-1)
        const zScore = (item.degree - meanDegree) / stdDev;
        const hubScore = Math.min(1, zScore / 5); // Normalize to 0-1
        
        return { node: item.node, hubScore };
      });
  }

  /**
   * Detect bridge edges
   */
  private detectBridgeEdges(nodes: GraphNode[]): { edge: GraphEdge; bridgeScore: number }[] {
    // Get all edges between the nodes
    const nodeIds = new Set(nodes.map(node => node.id));
    const edges: GraphEdge[] = [];
    
    for (const node of nodes) {
      const outgoingEdges = this.graphStore.getOutgoingEdges(node.id);
      
      for (const edge of outgoingEdges) {
        if (nodeIds.has(edge.target)) {
          edges.push(edge);
        }
      }
    }
    
    // This is a simplified bridge detection
    // In a real implementation, you would use a more sophisticated algorithm
    
    // For now, we'll identify edges that connect different node types
    return edges
      .filter(edge => {
        const sourceNode = this.graphStore.getNode(edge.source);
        const targetNode = this.graphStore.getNode(edge.target);
        
        return sourceNode && targetNode && sourceNode.type !== targetNode.type;
      })
      .map(edge => {
        // Calculate bridge score (0-1)
        // For now, use a fixed score
        const bridgeScore = 0.8;
        
        return { edge, bridgeScore };
      });
  }

  /**
   * Detect temporal anomalies in the graph
   * 
   * Temporal anomalies are unusual patterns in the timing of events,
   * such as sudden spikes in activity or unusual time gaps.
   */
  private async detectTemporalAnomalies(
    nodes: GraphNode[],
    sensitivityThreshold: number
  ): Promise<Anomaly[]> {
    console.log(`Detecting temporal anomalies with ${nodes.length} nodes`);
    
    // This is a placeholder for temporal anomaly detection
    // In a real implementation, you would use time series analysis
    
    console.log('Temporal anomaly detection is not fully implemented');
    
    // For now, detect nodes with unusual creation times
    const anomalies: Anomaly[] = [];
    
    // Group nodes by hour of day
    const nodesByHour: Record<number, GraphNode[]> = {};
    
    for (let i = 0; i < 24; i++) {
      nodesByHour[i] = [];
    }
    
    nodes.forEach(node => {
      const hour = node.createdAt.getHours();
      nodesByHour[hour].push(node);
    });
    
    // Calculate mean and standard deviation of node counts by hour
    const hourCounts = Object.values(nodesByHour).map(hourNodes => hourNodes.length);
    const meanCount = hourCounts.reduce((sum, count) => sum + count, 0) / 24;
    
    const squaredDiffs = hourCounts.map(count => Math.pow(count - meanCount, 2));
    const variance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / 24;
    const stdDev = Math.sqrt(variance);
    
    // Identify hours with unusual activity
    for (let hour = 0; hour < 24; hour++) {
      const count = nodesByHour[hour].length;
      const zScore = Math.abs(count - meanCount) / stdDev;
      
      // If count is significantly different from mean
      if (zScore > 2) {
        const anomalyScore = Math.min(1, zScore / 5); // Normalize to 0-1
        
        // Only include if score exceeds threshold
        if (anomalyScore >= sensitivityThreshold) {
          // Create an anomaly for each node in the unusual hour
          nodesByHour[hour].forEach(node => {
            anomalies.push({
              id: `anomaly-temporal-${node.id}`,
              type: 'temporal',
              nodes: [node],
              edges: [],
              score: anomalyScore,
              confidence: 0.6, // Moderate confidence for temporal anomalies
              description: '', // Will be generated later
              detectionTime: new Date()
            });
          });
        }
      }
    }
    
    return anomalies;
  }

  /**
   * Detect behavioral anomalies in the graph
   * 
   * Behavioral anomalies are unusual patterns in user behavior,
   * such as sudden changes in activity or unusual interaction patterns.
   */
  private async detectBehavioralAnomalies(
    nodes: GraphNode[],
    sensitivityThreshold: number
  ): Promise<Anomaly[]> {
    console.log(`Detecting behavioral anomalies with ${nodes.length} nodes`);
    
    // This is a placeholder for behavioral anomaly detection
    // In a real implementation, you would use more sophisticated algorithms
    
    console.log('Behavioral anomaly detection is not fully implemented');
    
    // For now, focus on user nodes with unusual activity patterns
    const userNodes = nodes.filter(node => node.type === NodeType.USER);
    const anomalies: Anomaly[] = [];
    
    for (const userNode of userNodes) {
      // Get user's interactions
      const interactions = userNode.properties.interactions || [];
      
      if (interactions.length === 0) {
        continue;
      }
      
      // Check for unusual interaction patterns
      const unusualPatterns = this.detectUnusualInteractionPatterns(userNode, interactions);
      
      for (const { pattern, score } of unusualPatterns) {
        // Only include if score exceeds threshold
        if (score >= sensitivityThreshold) {
          // Get related edges
          const relatedEdges = this.graphStore.getOutgoingEdges(userNode.id)
            .filter(edge => pattern.videoIds.includes(edge.target));
          
          anomalies.push({
            id: `anomaly-behavioral-${userNode.id}-${pattern.type}`,
            type: 'behavioral',
            nodes: [userNode],
            edges: relatedEdges,
            score,
            confidence: 0.5, // Lower confidence for behavioral anomalies
            description: '', // Will be generated later
            detectionTime: new Date()
          });
        }
      }
    }
    
    return anomalies;
  }

  /**
   * Detect unusual interaction patterns
   */
  private detectUnusualInteractionPatterns(
    userNode: GraphNode,
    interactions: any[]
  ): { pattern: { type: string; videoIds: string[] }; score: number }[] {
    const patterns: { pattern: { type: string; videoIds: string[] }; score: number }[] = [];
    
    // Check for rapid-fire interactions
    const interactionTimes = interactions.map(interaction => 
      new Date(interaction.timestamp).getTime()
    );
    
    if (interactionTimes.length < 2) {
      return patterns;
    }
    
    // Sort times in ascending order
    interactionTimes.sort((a, b) => a - b);
    
    // Calculate time differences between consecutive interactions
    const timeDiffs = [];
    for (let i = 1; i < interactionTimes.length; i++) {
      timeDiffs.push(interactionTimes[i] - interactionTimes[i - 1]);
    }
    
    // Calculate mean and standard deviation of time differences
    const meanDiff = timeDiffs.reduce((sum, diff) => sum + diff, 0) / timeDiffs.length;
    
    const squaredDiffs = timeDiffs.map(diff => Math.pow(diff - meanDiff, 2));
    const variance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / timeDiffs.length;
    const stdDev = Math.sqrt(variance);
    
    // Check for unusually small time differences (rapid-fire interactions)
    const rapidFireThreshold = Math.max(1000, meanDiff - 2 * stdDev); // At least 1 second
    
    const rapidFireIndices = [];
    for (let i = 0; i < timeDiffs.length; i++) {
      if (timeDiffs[i] < rapidFireThreshold) {
        rapidFireIndices.push(i);
      }
    }
    
    // If there are rapid-fire interactions, create a pattern
    if (rapidFireIndices.length > 0) {
      const videoIds = rapidFireIndices.map(i => interactions[i + 1].videoId);
      
      // Calculate score based on number of rapid-fire interactions
      const score = Math.min(1, rapidFireIndices.length / 10);
      
      patterns.push({
        pattern: {
          type: 'rapid-fire',
          videoIds
        },
        score
      });
    }
    
    // Check for unusual interaction types
    const interactionTypes = interactions.map(interaction => interaction.action);
    const typeCounts: Record<string, number> = {};
    
    interactionTypes.forEach(type => {
      typeCounts[type] = (typeCounts[type] || 0) + 1;
    });
    
    // Calculate expected distribution
    const expectedDistribution: Record<string, number> = {
      view: 0.7,
      like: 0.2,
      comment: 0.05,
      share: 0.03,
      follow: 0.02
    };
    
    // Check for significant deviations from expected distribution
    for (const [type, count] of Object.entries(typeCounts)) {
      const expected = expectedDistribution[type] || 0.01;
      const actual = count / interactions.length;
      
      // If actual is significantly higher than expected
      if (actual > expected * 3) {
        const videoIds = interactions
          .filter(interaction => interaction.action === type)
          .map(interaction => interaction.videoId);
        
        // Calculate score based on deviation from expected
        const score = Math.min(1, (actual - expected) / expected);
        
        patterns.push({
          pattern: {
            type: `unusual-${type}-rate`,
            videoIds
          },
          score
        });
      }
    }
    
    return patterns;
  }

  /**
   * Detect content anomalies in the graph
   * 
   * Content anomalies are unusual patterns in the content itself,
   * such as videos with unusual properties or descriptions.
   */
  private async detectContentAnomalies(
    nodes: GraphNode[],
    sensitivityThreshold: number
  ): Promise<Anomaly[]> {
    console.log(`Detecting content anomalies with ${nodes.length} nodes`);
    
    // This is a placeholder for content anomaly detection
    // In a real implementation, you would use content analysis
    
    console.log('Content anomaly detection is not fully implemented');
    
    // For now, focus on video nodes with unusual properties
    const videoNodes = nodes.filter(node => node.type === NodeType.VIDEO);
    const anomalies: Anomaly[] = [];
    
    // Calculate statistics for video properties
    const viewCounts = videoNodes
      .map(node => node.properties.viewCount || 0)
      .filter(count => count > 0);
    
    if (viewCounts.length === 0) {
      return anomalies;
    }
    
    const meanViewCount = viewCounts.reduce((sum, count) => sum + count, 0) / viewCounts.length;
    
    const squaredDiffs = viewCounts.map(count => Math.pow(count - meanViewCount, 2));
    const variance = squaredDiffs.reduce((sum, diff) => sum + diff, 0) / viewCounts.length;
    const stdDev = Math.sqrt(variance);
    
    // Identify videos with unusual view counts
    for (const videoNode of videoNodes) {
      const viewCount = videoNode.properties.viewCount || 0;
      
      if (viewCount === 0) {
        continue;
      }
      
      const zScore = Math.abs(viewCount - meanViewCount) / stdDev;
      
      // If view count is significantly different from mean
      if (zScore > 3) {
        const anomalyScore = Math.min(1, zScore / 10); // Normalize to 0-1
        
        // Only include if score exceeds threshold
        if (anomalyScore >= sensitivityThreshold) {
          anomalies.push({
            id: `anomaly-content-${videoNode.id}`,
            type: 'content',
            nodes: [videoNode],
            edges: [],
            score: anomalyScore,
            confidence: 0.7, // Moderate confidence for content anomalies
            description: '', // Will be generated later
            detectionTime: new Date()
          });
        }
      }
    }
    
    return anomalies;
  }

  /**
   * Generate descriptions for anomalies
   */
  private generateAnomalyDescriptions(anomalies: Anomaly[]): Anomaly[] {
    return anomalies.map(anomaly => {
      let description = '';
      
      switch (anomaly.type) {
        case 'structural':
          if (anomaly.nodes.length === 1 && anomaly.edges.length === 0) {
            // Isolated node
            const node = anomaly.nodes[0];
            description = `Isolated ${node.type} node with no connections`;
          } else if (anomaly.nodes.length === 1 && anomaly.edges.length > 0) {
            // Hub node
            const node = anomaly.nodes[0];
            description = `Hub ${node.type} node with unusually high connectivity (${anomaly.edges.length} connections)`;
          } else if (anomaly.nodes.length === 2 && anomaly.edges.length === 1) {
            // Bridge edge
            const sourceType = anomaly.nodes[0].type;
            const targetType = anomaly.nodes[1].type;
            description = `Bridge edge connecting ${sourceType} and ${targetType} nodes`;
          } else {
            description = `Structural anomaly with ${anomaly.nodes.length} nodes and ${anomaly.edges.length} edges`;
          }
          break;
          
        case 'temporal':
          if (anomaly.nodes.length === 1) {
            const node = anomaly.nodes[0];
            const hour = node.createdAt.getHours();
            description = `${node.type} node created at unusual hour (${hour}:00)`;
          } else {
            description = `Temporal anomaly with ${anomaly.nodes.length} nodes`;
          }
          break;
          
        case 'behavioral':
          if (anomaly.nodes.length === 1 && anomaly.nodes[0].type === NodeType.USER) {
            const user = anomaly.nodes[0];
            if (anomaly.id.includes('rapid-fire')) {
              description = `User ${user.id} showing rapid-fire interaction pattern`;
            } else if (anomaly.id.includes('unusual-like-rate')) {
              description = `User ${user.id} showing unusually high like rate`;
            } else if (anomaly.id.includes('unusual-comment-rate')) {
              description = `User ${user.id} showing unusually high comment rate`;
            } else if (anomaly.id.includes('unusual-share-rate')) {
              description = `User ${user.id} showing unusually high share rate`;
            } else {
              description = `User ${user.id} showing unusual behavior pattern`;
            }
          } else {
            description = `Behavioral anomaly with ${anomaly.nodes.length} nodes`;
          }
          break;
          
        case 'content':
          if (anomaly.nodes.length === 1 && anomaly.nodes[0].type === NodeType.VIDEO) {
            const video = anomaly.nodes[0];
            const viewCount = video.properties.viewCount || 0;
            description = `Video ${video.id} with unusually ${viewCount > 0 ? 'high' : 'low'} view count (${viewCount})`;
          } else {
            description = `Content anomaly with ${anomaly.nodes.length} nodes`;
          }
          break;
          
        default:
          description = `Unknown anomaly type: ${anomaly.type}`;
      }
      
      // Add score and confidence information
      description += ` (score: ${anomaly.score.toFixed(2)}, confidence: ${anomaly.confidence.toFixed(2)})`;
      
      return { ...anomaly, description };
    });
  }
} 