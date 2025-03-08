/**
 * Community Detector - Detects communities in the graph
 */

import { GraphStore } from '../graphStore';
import { 
  NodeType, 
  GraphNode, 
  GraphEdge 
} from '../types';

/**
 * Community interface
 */
export interface Community {
  id: string;
  nodes: GraphNode[];
  centralNodes: GraphNode[];
  size: number;
  density: number; // Connectivity density within community (0-1)
  cohesion: number; // Measure of community cohesion (0-1)
  description: string;
}

/**
 * Community Detector class
 */
export class CommunityDetector {
  private graphStore: GraphStore;

  /**
   * Constructor
   */
  constructor(graphStore: GraphStore) {
    this.graphStore = graphStore;
  }

  /**
   * Detect communities in the graph
   */
  public async detectCommunities(
    algorithm: string = 'louvain',
    nodeType: string = 'all',
    minCommunitySize: number = 3,
    maxCommunities: number = 10
  ): Promise<Community[]> {
    console.log(`Detecting communities using ${algorithm} algorithm`);
    
    // Convert string type to enum type if not 'all'
    let nodeTypeEnum: NodeType | null = null;
    if (nodeType !== 'all') {
      nodeTypeEnum = NodeType[nodeType as keyof typeof NodeType];
      if (!nodeTypeEnum) {
        console.warn(`Unknown node type: ${nodeType}. Using all node types.`);
        nodeTypeEnum = null;
      }
    }
    
    // Get nodes of the specified type
    const nodes = nodeTypeEnum 
      ? this.graphStore.getNodesByType(nodeTypeEnum)
      : Array.from(this.graphStore.getGraph().nodes.values());
    
    // Detect communities based on algorithm
    let communities: Community[] = [];
    
    switch (algorithm) {
      case 'louvain':
        communities = await this.detectCommunitiesLouvain(nodes, minCommunitySize);
        break;
      case 'label-propagation':
        communities = await this.detectCommunitiesLabelPropagation(nodes, minCommunitySize);
        break;
      case 'k-clique':
        communities = await this.detectCommunitiesKClique(nodes, minCommunitySize);
        break;
      default:
        console.warn(`Unknown algorithm: ${algorithm}. Falling back to louvain.`);
        communities = await this.detectCommunitiesLouvain(nodes, minCommunitySize);
    }
    
    // Sort communities by size (descending) and take the top 'maxCommunities'
    const topCommunities = communities
      .sort((a, b) => b.size - a.size)
      .slice(0, maxCommunities);
    
    // Generate descriptions for communities
    const communitiesWithDescriptions = this.generateCommunityDescriptions(topCommunities);
    
    console.log(`Found ${communitiesWithDescriptions.length} communities`);
    return communitiesWithDescriptions;
  }

  /**
   * Detect communities using Louvain algorithm
   * 
   * Louvain is a hierarchical community detection algorithm that
   * optimizes modularity in a greedy manner.
   */
  private async detectCommunitiesLouvain(
    nodes: GraphNode[],
    minCommunitySize: number
  ): Promise<Community[]> {
    console.log(`Detecting communities using Louvain algorithm with ${nodes.length} nodes`);
    
    // This is a simplified implementation of the Louvain algorithm
    // In a real system, you would use a more sophisticated implementation
    
    // Step 1: Initialize each node as its own community
    const nodeIds = nodes.map(node => node.id);
    const nodeCommunities = new Map<string, number>();
    
    nodeIds.forEach((nodeId, index) => {
      nodeCommunities.set(nodeId, index);
    });
    
    // Step 2: Calculate initial modularity
    const adjacencyMatrix = this.buildAdjacencyMatrix(nodeIds);
    let currentModularity = this.calculateModularity(nodeCommunities, adjacencyMatrix);
    
    // Step 3: Iteratively optimize modularity
    let improved = true;
    let iterations = 0;
    const maxIterations = 10;
    
    while (improved && iterations < maxIterations) {
      improved = false;
      iterations++;
      
      // For each node, try moving it to neighboring communities
      for (const nodeId of nodeIds) {
        const currentCommunity = nodeCommunities.get(nodeId)!;
        const neighborCommunities = this.getNeighborCommunities(nodeId, nodeCommunities);
        
        let bestCommunity = currentCommunity;
        let bestModularity = currentModularity;
        
        // Try moving to each neighboring community
        for (const neighborCommunity of neighborCommunities) {
          // Temporarily move node to neighbor community
          nodeCommunities.set(nodeId, neighborCommunity);
          
          // Calculate new modularity
          const newModularity = this.calculateModularity(nodeCommunities, adjacencyMatrix);
          
          // If modularity improved, keep the change
          if (newModularity > bestModularity) {
            bestModularity = newModularity;
            bestCommunity = neighborCommunity;
            improved = true;
          }
        }
        
        // Move node to best community
        nodeCommunities.set(nodeId, bestCommunity);
        currentModularity = bestModularity;
      }
      
      console.log(`Louvain iteration ${iterations}: modularity = ${currentModularity}`);
    }
    
    // Step 4: Group nodes by community
    const communities = new Map<number, string[]>();
    
    nodeCommunities.forEach((communityId, nodeId) => {
      if (!communities.has(communityId)) {
        communities.set(communityId, []);
      }
      communities.get(communityId)!.push(nodeId);
    });
    
    // Step 5: Create community objects
    const communityObjects: Community[] = [];
    
    communities.forEach((nodeIds, communityId) => {
      // Skip communities smaller than minCommunitySize
      if (nodeIds.length < minCommunitySize) {
        return;
      }
      
      // Get node objects
      const communityNodes = nodeIds
        .map(id => this.graphStore.getNode(id))
        .filter((node): node is GraphNode => node !== undefined);
      
      // Calculate community properties
      const density = this.calculateCommunityDensity(communityNodes);
      const cohesion = this.calculateCommunityCohesion(communityNodes);
      const centralNodes = this.findCentralNodes(communityNodes);
      
      // Create community object
      communityObjects.push({
        id: `community-${communityId}`,
        nodes: communityNodes,
        centralNodes,
        size: communityNodes.length,
        density,
        cohesion,
        description: '' // Will be generated later
      });
    });
    
    return communityObjects;
  }

  /**
   * Detect communities using Label Propagation algorithm
   * 
   * Label Propagation is a simple and efficient algorithm that
   * works by propagating labels through the network.
   */
  private async detectCommunitiesLabelPropagation(
    nodes: GraphNode[],
    minCommunitySize: number
  ): Promise<Community[]> {
    console.log(`Detecting communities using Label Propagation algorithm with ${nodes.length} nodes`);
    
    // This is a simplified implementation of the Label Propagation algorithm
    // In a real system, you would use a more sophisticated implementation
    
    // Step 1: Initialize each node with a unique label
    const nodeIds = nodes.map(node => node.id);
    const nodeLabels = new Map<string, number>();
    
    nodeIds.forEach((nodeId, index) => {
      nodeLabels.set(nodeId, index);
    });
    
    // Step 2: Iteratively update labels
    let changed = true;
    let iterations = 0;
    const maxIterations = 10;
    
    while (changed && iterations < maxIterations) {
      changed = false;
      iterations++;
      
      // Shuffle node order for randomness
      const shuffledNodeIds = [...nodeIds].sort(() => Math.random() - 0.5);
      
      // For each node, update its label to the most frequent label among neighbors
      for (const nodeId of shuffledNodeIds) {
        const neighbors = this.getNeighborNodes(nodeId);
        
        if (neighbors.length === 0) {
          continue;
        }
        
        // Count neighbor labels
        const labelCounts: Record<number, number> = {};
        
        neighbors.forEach(neighbor => {
          const neighborLabel = nodeLabels.get(neighbor.id);
          if (neighborLabel !== undefined) {
            labelCounts[neighborLabel] = (labelCounts[neighborLabel] || 0) + 1;
          }
        });
        
        // Find most frequent label
        let maxCount = 0;
        let maxLabel = nodeLabels.get(nodeId)!;
        
        Object.entries(labelCounts).forEach(([label, count]) => {
          if (count > maxCount) {
            maxCount = count;
            maxLabel = parseInt(label);
          }
        });
        
        // Update label if changed
        if (maxLabel !== nodeLabels.get(nodeId)) {
          nodeLabels.set(nodeId, maxLabel);
          changed = true;
        }
      }
      
      console.log(`Label Propagation iteration ${iterations}: changed = ${changed}`);
    }
    
    // Step 3: Group nodes by label
    const communities = new Map<number, string[]>();
    
    nodeLabels.forEach((label, nodeId) => {
      if (!communities.has(label)) {
        communities.set(label, []);
      }
      communities.get(label)!.push(nodeId);
    });
    
    // Step 4: Create community objects
    const communityObjects: Community[] = [];
    
    communities.forEach((nodeIds, label) => {
      // Skip communities smaller than minCommunitySize
      if (nodeIds.length < minCommunitySize) {
        return;
      }
      
      // Get node objects
      const communityNodes = nodeIds
        .map(id => this.graphStore.getNode(id))
        .filter((node): node is GraphNode => node !== undefined);
      
      // Calculate community properties
      const density = this.calculateCommunityDensity(communityNodes);
      const cohesion = this.calculateCommunityCohesion(communityNodes);
      const centralNodes = this.findCentralNodes(communityNodes);
      
      // Create community object
      communityObjects.push({
        id: `community-${label}`,
        nodes: communityNodes,
        centralNodes,
        size: communityNodes.length,
        density,
        cohesion,
        description: '' // Will be generated later
      });
    });
    
    return communityObjects;
  }

  /**
   * Detect communities using K-Clique Percolation algorithm
   * 
   * K-Clique Percolation finds communities by identifying
   * connected k-cliques (complete subgraphs of k nodes).
   */
  private async detectCommunitiesKClique(
    nodes: GraphNode[],
    minCommunitySize: number,
    k: number = 3
  ): Promise<Community[]> {
    console.log(`Detecting communities using K-Clique Percolation algorithm with k=${k}`);
    
    // This is a placeholder for K-Clique Percolation
    // In a real implementation, you would use a more sophisticated algorithm
    
    console.log('K-Clique Percolation is not fully implemented');
    
    // For now, return a subset of Louvain communities
    const louvainCommunities = await this.detectCommunitiesLouvain(nodes, minCommunitySize);
    
    // Filter to include only dense communities
    const denseCommunities = louvainCommunities.filter(community => 
      community.density > 0.5
    );
    
    return denseCommunities;
  }

  /**
   * Build adjacency matrix for a set of nodes
   */
  private buildAdjacencyMatrix(nodeIds: string[]): number[][] {
    const n = nodeIds.length;
    const nodeIndexMap = new Map<string, number>();
    
    // Map node IDs to indices
    nodeIds.forEach((id, index) => {
      nodeIndexMap.set(id, index);
    });
    
    // Initialize adjacency matrix with zeros
    const adjacencyMatrix: number[][] = Array(n).fill(0).map(() => Array(n).fill(0));
    
    // Fill adjacency matrix
    for (let i = 0; i < n; i++) {
      const nodeId = nodeIds[i];
      const outgoingEdges = this.graphStore.getOutgoingEdges(nodeId);
      
      for (const edge of outgoingEdges) {
        const targetIndex = nodeIndexMap.get(edge.target);
        
        if (targetIndex !== undefined) {
          adjacencyMatrix[i][targetIndex] = edge.weight;
        }
      }
    }
    
    return adjacencyMatrix;
  }

  /**
   * Calculate modularity for a community assignment
   */
  private calculateModularity(
    nodeCommunities: Map<string, number>,
    adjacencyMatrix: number[][]
  ): number {
    // This is a simplified modularity calculation
    // In a real implementation, you would use a more accurate formula
    
    const n = adjacencyMatrix.length;
    let modularity = 0;
    
    // Calculate total edge weight
    let totalWeight = 0;
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        totalWeight += adjacencyMatrix[i][j];
      }
    }
    
    if (totalWeight === 0) {
      return 0;
    }
    
    // Calculate node strengths (sum of edge weights)
    const nodeStrengths: number[] = Array(n).fill(0);
    
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        nodeStrengths[i] += adjacencyMatrix[i][j];
      }
    }
    
    // Calculate modularity
    for (let i = 0; i < n; i++) {
      for (let j = 0; j < n; j++) {
        const aij = adjacencyMatrix[i][j];
        const kikj = nodeStrengths[i] * nodeStrengths[j] / totalWeight;
        
        // Get node communities
        const communityI = nodeCommunities.get(i.toString());
        const communityJ = nodeCommunities.get(j.toString());
        
        // Add to modularity if nodes are in the same community
        if (communityI === communityJ) {
          modularity += (aij - kikj) / totalWeight;
        }
      }
    }
    
    return modularity;
  }

  /**
   * Get neighboring communities of a node
   */
  private getNeighborCommunities(
    nodeId: string,
    nodeCommunities: Map<string, number>
  ): Set<number> {
    const neighborCommunities = new Set<number>();
    
    // Get neighbors of the node
    const neighbors = this.getNeighborNodes(nodeId);
    
    // Add communities of neighbors
    neighbors.forEach(neighbor => {
      const community = nodeCommunities.get(neighbor.id);
      if (community !== undefined) {
        neighborCommunities.add(community);
      }
    });
    
    return neighborCommunities;
  }

  /**
   * Get neighboring nodes of a node
   */
  private getNeighborNodes(nodeId: string): GraphNode[] {
    // Get outgoing edges
    const outgoingEdges = this.graphStore.getOutgoingEdges(nodeId);
    const outNeighborIds = outgoingEdges.map(edge => edge.target);
    
    // Get incoming edges
    const incomingEdges = this.graphStore.getIncomingEdges(nodeId);
    const inNeighborIds = incomingEdges.map(edge => edge.source);
    
    // Combine and deduplicate neighbor IDs
    const neighborIds = [...new Set([...outNeighborIds, ...inNeighborIds])];
    
    // Get node objects
    return neighborIds
      .map(id => this.graphStore.getNode(id))
      .filter((node): node is GraphNode => node !== undefined);
  }

  /**
   * Calculate density of a community
   */
  private calculateCommunityDensity(nodes: GraphNode[]): number {
    if (nodes.length < 2) {
      return 0;
    }
    
    // Count edges within the community
    const nodeIds = new Set(nodes.map(node => node.id));
    let edgeCount = 0;
    
    for (const node of nodes) {
      const outgoingEdges = this.graphStore.getOutgoingEdges(node.id);
      
      for (const edge of outgoingEdges) {
        if (nodeIds.has(edge.target)) {
          edgeCount++;
        }
      }
    }
    
    // Calculate maximum possible edges
    const maxEdges = nodes.length * (nodes.length - 1);
    
    // Density is the ratio of actual edges to maximum possible edges
    return maxEdges > 0 ? edgeCount / maxEdges : 0;
  }

  /**
   * Calculate cohesion of a community
   */
  private calculateCommunityCohesion(nodes: GraphNode[]): number {
    if (nodes.length < 2) {
      return 0;
    }
    
    // Count internal and external edges
    const nodeIds = new Set(nodes.map(node => node.id));
    let internalEdges = 0;
    let externalEdges = 0;
    
    for (const node of nodes) {
      const outgoingEdges = this.graphStore.getOutgoingEdges(node.id);
      
      for (const edge of outgoingEdges) {
        if (nodeIds.has(edge.target)) {
          internalEdges++;
        } else {
          externalEdges++;
        }
      }
    }
    
    // Cohesion is the ratio of internal edges to total edges
    const totalEdges = internalEdges + externalEdges;
    return totalEdges > 0 ? internalEdges / totalEdges : 0;
  }

  /**
   * Find central nodes in a community
   */
  private findCentralNodes(nodes: GraphNode[]): GraphNode[] {
    if (nodes.length === 0) {
      return [];
    }
    
    // Calculate degree centrality for each node
    const nodeCentralities = nodes.map(node => {
      const outgoingEdges = this.graphStore.getOutgoingEdges(node.id);
      const incomingEdges = this.graphStore.getIncomingEdges(node.id);
      const degree = outgoingEdges.length + incomingEdges.length;
      
      return {
        node,
        centrality: degree
      };
    });
    
    // Sort by centrality (descending)
    nodeCentralities.sort((a, b) => b.centrality - a.centrality);
    
    // Take top 20% of nodes as central nodes
    const topCount = Math.max(1, Math.ceil(nodes.length * 0.2));
    return nodeCentralities.slice(0, topCount).map(item => item.node);
  }

  /**
   * Generate descriptions for communities
   */
  private generateCommunityDescriptions(communities: Community[]): Community[] {
    return communities.map(community => {
      // Count node types
      const nodeTypeCounts: Record<string, number> = {};
      
      community.nodes.forEach(node => {
        nodeTypeCounts[node.type] = (nodeTypeCounts[node.type] || 0) + 1;
      });
      
      // Find dominant node type
      let dominantType = '';
      let maxCount = 0;
      
      Object.entries(nodeTypeCounts).forEach(([type, count]) => {
        if (count > maxCount) {
          maxCount = count;
          dominantType = type;
        }
      });
      
      // Generate description based on dominant type
      let description = '';
      
      if (dominantType === NodeType.USER) {
        description = `User community with ${community.size} members`;
      } else if (dominantType === NodeType.VIDEO) {
        description = `Video community with ${community.size} videos`;
      } else if (dominantType === NodeType.CATEGORY) {
        description = `Category community with ${community.size} categories`;
      } else if (dominantType === NodeType.TOPIC) {
        description = `Topic community with ${community.size} topics`;
      } else {
        description = `Mixed community with ${community.size} nodes`;
      }
      
      // Add density and cohesion information
      description += ` (density: ${community.density.toFixed(2)}, cohesion: ${community.cohesion.toFixed(2)})`;
      
      return { ...community, description };
    });
  }
} 