/**
 * Pattern Detector - Detects frequent patterns in the graph
 */

import { GraphStore } from '../graphStore';
import { 
  NodeType, 
  EdgeType, 
  GraphNode, 
  GraphEdge 
} from '../types';

/**
 * Pattern interface
 */
export interface Pattern {
  id: string;
  nodes: GraphNode[];
  edges: GraphEdge[];
  support: number; // Frequency of occurrence (0-1)
  confidence: number; // Confidence score (0-1)
  description: string;
}

/**
 * Pattern Detector class
 */
export class PatternDetector {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Detect patterns in the graph
   */
  public async detectPatterns(
    patternType: string = 'frequent',
    nodeTypes: string[] = [],
    edgeTypes: string[] = [],
    minSupport: number = 0.1,
    maxPatternSize: number = 5,
    timeframe: string = 'all'
  ): Promise<Pattern[]> {
    console.log(`Detecting ${patternType} patterns with minSupport ${minSupport}`);
    
    // Convert string types to enum types
    const nodeTypeEnums = nodeTypes.length > 0 
      ? nodeTypes.map(type => NodeType[type as keyof typeof NodeType]).filter(Boolean)
      : Object.values(NodeType);
    
    const edgeTypeEnums = edgeTypes.length > 0
      ? edgeTypes.map(type => EdgeType[type as keyof typeof EdgeType]).filter(Boolean)
      : Object.values(EdgeType);
    
    // Filter nodes and edges by type and timeframe
    const filteredNodes = this.filterNodesByTypeAndTime(nodeTypeEnums, timeframe);
    const filteredEdges = this.filterEdgesByTypeAndTime(edgeTypeEnums, timeframe);
    
    // Detect patterns based on pattern type
    switch (patternType) {
      case 'frequent':
        return this.detectFrequentPatterns(filteredNodes, filteredEdges, minSupport, maxPatternSize);
      case 'sequential':
        return this.detectSequentialPatterns(filteredNodes, filteredEdges, minSupport, maxPatternSize);
      case 'causal':
        return this.detectCausalPatterns(filteredNodes, filteredEdges, minSupport, maxPatternSize);
      default:
        console.warn(`Unknown pattern type: ${patternType}. Falling back to frequent patterns.`);
        return this.detectFrequentPatterns(filteredNodes, filteredEdges, minSupport, maxPatternSize);
    }
  }

  /**
   * Filter nodes by type and timeframe
   */
  private filterNodesByTypeAndTime(
    nodeTypes: NodeType[],
    timeframe: string
  ): GraphNode[] {
    // Get all nodes of the specified types
    let nodes = this.graphStore.getNodesByType(nodeTypes[0]);
    
    for (let i = 1; i < nodeTypes.length; i++) {
      nodes = nodes.concat(this.graphStore.getNodesByType(nodeTypes[i]));
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
   * Filter edges by type and timeframe
   */
  private filterEdgesByTypeAndTime(
    edgeTypes: EdgeType[],
    timeframe: string
  ): GraphEdge[] {
    // Get all edges of the specified types
    let edges = this.graphStore.getEdgesByType(edgeTypes[0]);
    
    for (let i = 1; i < edgeTypes.length; i++) {
      edges = edges.concat(this.graphStore.getEdgesByType(edgeTypes[i]));
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
      
      edges = edges.filter(edge => edge.createdAt.getTime() >= startTime.getTime());
    }
    
    return edges;
  }

  /**
   * Detect frequent patterns using a simplified Apriori algorithm
   */
  private async detectFrequentPatterns(
    nodes: GraphNode[],
    edges: GraphEdge[],
    minSupport: number,
    maxPatternSize: number
  ): Promise<Pattern[]> {
    console.log(`Detecting frequent patterns with ${nodes.length} nodes and ${edges.length} edges`);
    
    // Start with single-node patterns
    const singleNodePatterns = this.generateSingleNodePatterns(nodes);
    
    // Filter by minimum support
    const frequentSingleNodePatterns = this.filterPatternsBySupport(singleNodePatterns, minSupport);
    
    if (frequentSingleNodePatterns.length === 0) {
      console.log('No frequent single-node patterns found');
      return [];
    }
    
    // Start with frequent single-node patterns
    let currentPatterns = frequentSingleNodePatterns;
    let allFrequentPatterns = [...frequentSingleNodePatterns];
    
    // Grow patterns iteratively
    for (let size = 2; size <= maxPatternSize; size++) {
      // Generate candidate patterns by extending current patterns
      const candidatePatterns = this.generateCandidatePatterns(currentPatterns, edges);
      
      if (candidatePatterns.length === 0) {
        console.log(`No candidate patterns of size ${size} found`);
        break;
      }
      
      // Filter by minimum support
      const frequentPatterns = this.filterPatternsBySupport(candidatePatterns, minSupport);
      
      if (frequentPatterns.length === 0) {
        console.log(`No frequent patterns of size ${size} found`);
        break;
      }
      
      // Add to all frequent patterns
      allFrequentPatterns = allFrequentPatterns.concat(frequentPatterns);
      
      // Update current patterns for next iteration
      currentPatterns = frequentPatterns;
    }
    
    // Calculate confidence for each pattern
    const patternsWithConfidence = this.calculatePatternConfidence(allFrequentPatterns);
    
    // Generate descriptions for each pattern
    const patternsWithDescriptions = this.generatePatternDescriptions(patternsWithConfidence);
    
    console.log(`Found ${patternsWithDescriptions.length} frequent patterns`);
    return patternsWithDescriptions;
  }

  /**
   * Generate single-node patterns
   */
  private generateSingleNodePatterns(nodes: GraphNode[]): Pattern[] {
    return nodes.map(node => ({
      id: `pattern-${node.id}`,
      nodes: [node],
      edges: [],
      support: 0, // Will be calculated later
      confidence: 0, // Will be calculated later
      description: '' // Will be generated later
    }));
  }

  /**
   * Filter patterns by minimum support
   */
  private filterPatternsBySupport(patterns: Pattern[], minSupport: number): Pattern[] {
    // Calculate support for each pattern
    const patternsWithSupport = patterns.map(pattern => {
      const support = this.calculatePatternSupport(pattern);
      return { ...pattern, support };
    });
    
    // Filter by minimum support
    return patternsWithSupport.filter(pattern => pattern.support >= minSupport);
  }

  /**
   * Calculate support for a pattern (frequency of occurrence)
   */
  private calculatePatternSupport(pattern: Pattern): number {
    // For single-node patterns
    if (pattern.nodes.length === 1 && pattern.edges.length === 0) {
      const node = pattern.nodes[0];
      const nodeType = node.type;
      
      // Count nodes of this type
      const nodesOfType = this.graphStore.getNodesByType(nodeType);
      
      // Support is the fraction of nodes of this type
      return nodesOfType.length > 0 ? 1 / nodesOfType.length : 0;
    }
    
    // For multi-node patterns
    // This is a simplified implementation
    // In a real system, you would need to count actual occurrences of the pattern
    
    // For now, we'll use a heuristic based on edge weights
    let totalWeight = 0;
    
    for (const edge of pattern.edges) {
      totalWeight += edge.weight;
    }
    
    // Normalize by the number of edges
    const avgWeight = pattern.edges.length > 0 ? totalWeight / pattern.edges.length : 0;
    
    // Support is proportional to average edge weight
    return avgWeight;
  }

  /**
   * Generate candidate patterns by extending current patterns
   */
  private generateCandidatePatterns(currentPatterns: Pattern[], allEdges: GraphEdge[]): Pattern[] {
    const candidatePatterns: Pattern[] = [];
    
    for (const pattern of currentPatterns) {
      // Get nodes in the pattern
      const patternNodeIds = new Set(pattern.nodes.map(node => node.id));
      
      // Find edges that connect to nodes in the pattern
      const connectingEdges = allEdges.filter(edge => 
        patternNodeIds.has(edge.source) || patternNodeIds.has(edge.target)
      );
      
      // Extend pattern with each connecting edge
      for (const edge of connectingEdges) {
        // Skip if edge is already in the pattern
        if (pattern.edges.some(e => e.id === edge.id)) {
          continue;
        }
        
        // Get the node on the other end of the edge
        const otherNodeId = patternNodeIds.has(edge.source) ? edge.target : edge.source;
        const otherNode = this.graphStore.getNode(otherNodeId);
        
        if (!otherNode) {
          continue;
        }
        
        // Skip if node is already in the pattern
        if (patternNodeIds.has(otherNodeId)) {
          continue;
        }
        
        // Create new pattern
        const newPattern: Pattern = {
          id: `pattern-${pattern.id}-${edge.id}`,
          nodes: [...pattern.nodes, otherNode],
          edges: [...pattern.edges, edge],
          support: 0, // Will be calculated later
          confidence: 0, // Will be calculated later
          description: '' // Will be generated later
        };
        
        candidatePatterns.push(newPattern);
      }
    }
    
    return candidatePatterns;
  }

  /**
   * Calculate confidence for patterns
   */
  private calculatePatternConfidence(patterns: Pattern[]): Pattern[] {
    return patterns.map(pattern => {
      // For single-node patterns, confidence is the same as support
      if (pattern.nodes.length === 1 && pattern.edges.length === 0) {
        return { ...pattern, confidence: pattern.support };
      }
      
      // For multi-node patterns
      // This is a simplified implementation
      // In a real system, you would calculate confidence based on conditional probabilities
      
      // For now, we'll use a heuristic based on node types and edge types
      const nodeTypeCount = new Set(pattern.nodes.map(node => node.type)).size;
      const edgeTypeCount = new Set(pattern.edges.map(edge => edge.type)).size;
      
      // More diverse node and edge types indicate higher confidence
      const diversity = (nodeTypeCount + edgeTypeCount) / (pattern.nodes.length + pattern.edges.length);
      
      // Confidence is a combination of support and diversity
      const confidence = (pattern.support * 0.7) + (diversity * 0.3);
      
      return { ...pattern, confidence };
    });
  }

  /**
   * Generate descriptions for patterns
   */
  private generatePatternDescriptions(patterns: Pattern[]): Pattern[] {
    return patterns.map(pattern => {
      let description = '';
      
      // For single-node patterns
      if (pattern.nodes.length === 1 && pattern.edges.length === 0) {
        const node = pattern.nodes[0];
        description = `Single ${node.type} node`;
        
        // Add node properties if available
        if (node.properties.name) {
          description += ` named "${node.properties.name}"`;
        }
      }
      // For multi-node patterns
      else {
        // Count node types
        const nodeTypeCounts: Record<string, number> = {};
        pattern.nodes.forEach(node => {
          nodeTypeCounts[node.type] = (nodeTypeCounts[node.type] || 0) + 1;
        });
        
        // Count edge types
        const edgeTypeCounts: Record<string, number> = {};
        pattern.edges.forEach(edge => {
          edgeTypeCounts[edge.type] = (edgeTypeCounts[edge.type] || 0) + 1;
        });
        
        // Generate description based on node and edge types
        const nodeTypeDesc = Object.entries(nodeTypeCounts)
          .map(([type, count]) => `${count} ${type}${count > 1 ? 's' : ''}`)
          .join(', ');
        
        const edgeTypeDesc = Object.entries(edgeTypeCounts)
          .map(([type, count]) => `${count} ${type}${count > 1 ? 's' : ''}`)
          .join(', ');
        
        description = `Pattern with ${nodeTypeDesc} connected by ${edgeTypeDesc}`;
      }
      
      return { ...pattern, description };
    });
  }

  /**
   * Detect sequential patterns
   */
  private async detectSequentialPatterns(
    nodes: GraphNode[],
    edges: GraphEdge[],
    minSupport: number,
    maxPatternSize: number
  ): Promise<Pattern[]> {
    // This is a placeholder for sequential pattern mining
    // In a real implementation, you would use algorithms like PrefixSpan or SPADE
    
    console.log('Sequential pattern detection is not fully implemented');
    
    // For now, return a subset of frequent patterns
    const frequentPatterns = await this.detectFrequentPatterns(nodes, edges, minSupport, maxPatternSize);
    
    // Filter to include only patterns with a temporal component
    const sequentialPatterns = frequentPatterns.filter(pattern => {
      // Check if edges have a temporal ordering
      if (pattern.edges.length < 2) {
        return false;
      }
      
      // Sort edges by creation time
      const sortedEdges = [...pattern.edges].sort((a, b) => 
        a.createdAt.getTime() - b.createdAt.getTime()
      );
      
      // Check if there's a significant time difference between edges
      for (let i = 1; i < sortedEdges.length; i++) {
        const timeDiff = sortedEdges[i].createdAt.getTime() - sortedEdges[i-1].createdAt.getTime();
        if (timeDiff > 60 * 60 * 1000) { // More than 1 hour
          return true;
        }
      }
      
      return false;
    });
    
    return sequentialPatterns;
  }

  /**
   * Detect causal patterns
   */
  private async detectCausalPatterns(
    nodes: GraphNode[],
    edges: GraphEdge[],
    minSupport: number,
    maxPatternSize: number
  ): Promise<Pattern[]> {
    // This is a placeholder for causal pattern mining
    // In a real implementation, you would use causal inference algorithms
    
    console.log('Causal pattern detection is not fully implemented');
    
    // For now, return a subset of sequential patterns
    const sequentialPatterns = await this.detectSequentialPatterns(nodes, edges, minSupport, maxPatternSize);
    
    // Filter to include only patterns with potential causal relationships
    const causalPatterns = sequentialPatterns.filter(pattern => {
      // Check if there are directed edges that could indicate causality
      return pattern.edges.some(edge => 
        edge.type === EdgeType.CREATED || 
        edge.type === EdgeType.INSPIRED_BY
      );
    });
    
    return causalPatterns;
  }
} 