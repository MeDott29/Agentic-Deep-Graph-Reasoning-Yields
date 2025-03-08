/**
 * Graph Store - Manages the knowledge graph
 */

import { 
  KnowledgeGraph, 
  GraphNode, 
  GraphEdge, 
  NodeType, 
  EdgeType 
} from './types';
import { AIVideo, UserBehavior, UserInteraction } from '../aiService';

/**
 * Graph Store class
 */
export class GraphStore {
  private graph: KnowledgeGraph;
  private static instance: GraphStore;

  /**
   * Private constructor for singleton pattern
   */
  private constructor() {
    this.graph = {
      nodes: new Map<string, GraphNode>(),
      edges: new Map<string, GraphEdge>(),
      adjacencyList: new Map<string, Map<string, string[]>>()
    };
    this.initializeGraph();
  }

  /**
   * Get singleton instance
   */
  public static getInstance(): GraphStore {
    if (!GraphStore.instance) {
      GraphStore.instance = new GraphStore();
    }
    return GraphStore.instance;
  }

  /**
   * Initialize the graph with some seed data
   */
  private initializeGraph(): void {
    // Add some seed categories
    const categories = [
      'Comedy', 'Dance', 'Education', 'Fashion', 'Fitness',
      'Food', 'Gaming', 'Music', 'Technology', 'Travel'
    ];

    categories.forEach(category => {
      this.addNode({
        id: `category-${category.toLowerCase()}`,
        type: NodeType.CATEGORY,
        properties: { name: category },
        createdAt: new Date(),
        updatedAt: new Date()
      });
    });

    // Add some seed topics
    const topics = [
      'AI', 'Climate Change', 'Cryptocurrency', 'DIY', 'Health',
      'Mindfulness', 'Pets', 'Science', 'Sports', 'Sustainability'
    ];

    topics.forEach(topic => {
      this.addNode({
        id: `topic-${topic.toLowerCase().replace(/\s+/g, '-')}`,
        type: NodeType.TOPIC,
        properties: { name: topic },
        createdAt: new Date(),
        updatedAt: new Date()
      });
    });

    // Connect related categories and topics
    this.addEdge({
      id: `edge-tech-ai`,
      type: EdgeType.RELATED_TO,
      source: 'category-technology',
      target: 'topic-ai',
      weight: 0.9,
      properties: {},
      createdAt: new Date(),
      updatedAt: new Date()
    });

    // Add more edges as needed
    console.log('Graph initialized with seed data');
  }

  /**
   * Add a node to the graph
   */
  public addNode(node: GraphNode): void {
    if (this.graph.nodes.has(node.id)) {
      console.warn(`Node with ID ${node.id} already exists. Updating instead.`);
      this.updateNode(node.id, node);
      return;
    }

    this.graph.nodes.set(node.id, node);
    
    // Initialize adjacency list entry for this node
    if (!this.graph.adjacencyList.has(node.id)) {
      this.graph.adjacencyList.set(node.id, new Map<string, string[]>());
    }

    console.log(`Added node: ${node.id} of type ${node.type}`);
  }

  /**
   * Update a node in the graph
   */
  public updateNode(nodeId: string, updates: Partial<GraphNode>): void {
    const existingNode = this.graph.nodes.get(nodeId);
    
    if (!existingNode) {
      console.error(`Node with ID ${nodeId} not found.`);
      return;
    }

    const updatedNode = {
      ...existingNode,
      ...updates,
      properties: {
        ...existingNode.properties,
        ...(updates.properties || {})
      },
      updatedAt: new Date()
    };

    this.graph.nodes.set(nodeId, updatedNode as GraphNode);
    console.log(`Updated node: ${nodeId}`);
  }

  /**
   * Add an edge to the graph
   */
  public addEdge(edge: GraphEdge): void {
    if (this.graph.edges.has(edge.id)) {
      console.warn(`Edge with ID ${edge.id} already exists. Updating instead.`);
      this.updateEdge(edge.id, edge);
      return;
    }

    // Ensure source and target nodes exist
    if (!this.graph.nodes.has(edge.source)) {
      console.error(`Source node ${edge.source} does not exist.`);
      return;
    }

    if (!this.graph.nodes.has(edge.target)) {
      console.error(`Target node ${edge.target} does not exist.`);
      return;
    }

    this.graph.edges.set(edge.id, edge);

    // Update adjacency list
    let sourceAdjList = this.graph.adjacencyList.get(edge.source);
    if (!sourceAdjList) {
      sourceAdjList = new Map<string, string[]>();
      this.graph.adjacencyList.set(edge.source, sourceAdjList);
    }

    let edgeList = sourceAdjList.get(edge.type);
    if (!edgeList) {
      edgeList = [];
      sourceAdjList.set(edge.type, edgeList);
    }

    edgeList.push(edge.target);
    console.log(`Added edge: ${edge.id} from ${edge.source} to ${edge.target} of type ${edge.type}`);
  }

  /**
   * Update an edge in the graph
   */
  public updateEdge(edgeId: string, updates: Partial<GraphEdge>): void {
    const existingEdge = this.graph.edges.get(edgeId);
    
    if (!existingEdge) {
      console.error(`Edge with ID ${edgeId} not found.`);
      return;
    }

    const updatedEdge = {
      ...existingEdge,
      ...updates,
      properties: {
        ...existingEdge.properties,
        ...(updates.properties || {})
      },
      updatedAt: new Date()
    };

    this.graph.edges.set(edgeId, updatedEdge as GraphEdge);
    console.log(`Updated edge: ${edgeId}`);
  }

  /**
   * Get a node by ID
   */
  public getNode(nodeId: string): GraphNode | undefined {
    return this.graph.nodes.get(nodeId);
  }

  /**
   * Get an edge by ID
   */
  public getEdge(edgeId: string): GraphEdge | undefined {
    return this.graph.edges.get(edgeId);
  }

  /**
   * Get all nodes of a specific type
   */
  public getNodesByType(type: NodeType): GraphNode[] {
    return Array.from(this.graph.nodes.values())
      .filter(node => node.type === type);
  }

  /**
   * Get all edges of a specific type
   */
  public getEdgesByType(type: EdgeType): GraphEdge[] {
    return Array.from(this.graph.edges.values())
      .filter(edge => edge.type === type);
  }

  /**
   * Get all outgoing edges from a node
   */
  public getOutgoingEdges(nodeId: string): GraphEdge[] {
    return Array.from(this.graph.edges.values())
      .filter(edge => edge.source === nodeId);
  }

  /**
   * Get all incoming edges to a node
   */
  public getIncomingEdges(nodeId: string): GraphEdge[] {
    return Array.from(this.graph.edges.values())
      .filter(edge => edge.target === nodeId);
  }

  /**
   * Get neighbors of a node by edge type
   */
  public getNeighbors(nodeId: string, edgeType?: EdgeType): GraphNode[] {
    const adjacencyMap = this.graph.adjacencyList.get(nodeId);
    if (!adjacencyMap) return [];

    let neighborIds: string[] = [];
    
    if (edgeType) {
      // Get neighbors connected by a specific edge type
      const edgeTypeNeighbors = adjacencyMap.get(edgeType);
      if (edgeTypeNeighbors) {
        neighborIds = edgeTypeNeighbors;
      }
    } else {
      // Get all neighbors regardless of edge type
      neighborIds = Array.from(adjacencyMap.values())
        .flat();
    }

    // Remove duplicates
    neighborIds = [...new Set(neighborIds)];

    // Get the actual node objects
    return neighborIds
      .map(id => this.graph.nodes.get(id))
      .filter((node): node is GraphNode => node !== undefined);
  }

  /**
   * Find paths between two nodes
   */
  public findPaths(sourceId: string, targetId: string, maxDepth: number = 3): GraphEdge[][] {
    const paths: GraphEdge[][] = [];
    const visited = new Set<string>();
    
    const dfs = (currentId: string, currentPath: GraphEdge[], depth: number) => {
      if (depth > maxDepth) return;
      if (currentId === targetId) {
        paths.push([...currentPath]);
        return;
      }
      
      visited.add(currentId);
      
      const outgoingEdges = this.getOutgoingEdges(currentId);
      for (const edge of outgoingEdges) {
        if (!visited.has(edge.target)) {
          currentPath.push(edge);
          dfs(edge.target, currentPath, depth + 1);
          currentPath.pop();
        }
      }
      
      visited.delete(currentId);
    };
    
    dfs(sourceId, [], 0);
    return paths;
  }

  /**
   * Process a user interaction and update the graph
   */
  public processUserInteraction(interaction: UserInteraction, video: AIVideo): void {
    const userId = interaction.videoId.split('-')[0]; // Assuming userId is part of videoId
    const videoId = interaction.videoId;
    const timestamp = interaction.timestamp;
    
    // Ensure user node exists
    if (!this.graph.nodes.has(userId)) {
      this.addNode({
        id: userId,
        type: NodeType.USER,
        properties: { interactions: [] },
        createdAt: timestamp,
        updatedAt: timestamp
      });
    }
    
    // Ensure video node exists
    if (!this.graph.nodes.has(videoId)) {
      this.addNode({
        id: videoId,
        type: NodeType.VIDEO,
        properties: {
          title: video.description,
          category: video.category,
          creator: video.username
        },
        createdAt: timestamp,
        updatedAt: timestamp
      });
    }
    
    // Create edge based on interaction type
    let edgeType: EdgeType;
    switch (interaction.action) {
      case 'view':
        edgeType = EdgeType.VIEWED;
        break;
      case 'like':
        edgeType = EdgeType.LIKED;
        break;
      case 'comment':
        edgeType = EdgeType.COMMENTED_ON;
        break;
      case 'share':
        edgeType = EdgeType.SHARED;
        break;
      case 'follow':
        edgeType = EdgeType.FOLLOWS;
        break;
      default:
        edgeType = EdgeType.INTERACTED_WITH;
    }
    
    const edgeId = `${edgeType.toLowerCase()}-${userId}-${videoId}-${timestamp.getTime()}`;
    
    this.addEdge({
      id: edgeId,
      type: edgeType,
      source: userId,
      target: videoId,
      weight: 1.0,
      properties: {
        duration: interaction.duration,
        metadata: interaction.metadata
      },
      createdAt: timestamp,
      updatedAt: timestamp
    });
    
    // Update user node with interaction
    const userNode = this.graph.nodes.get(userId);
    if (userNode) {
      const interactions = userNode.properties.interactions || [];
      interactions.push({
        videoId,
        action: interaction.action,
        timestamp
      });
      
      this.updateNode(userId, {
        properties: {
          ...userNode.properties,
          interactions
        }
      });
    }
    
    console.log(`Processed user interaction: ${interaction.action} on video ${videoId}`);
  }

  /**
   * Get the entire graph
   */
  public getGraph(): KnowledgeGraph {
    return this.graph;
  }

  /**
   * Clear the graph
   */
  public clearGraph(): void {
    this.graph.nodes.clear();
    this.graph.edges.clear();
    this.graph.adjacencyList.clear();
    this.initializeGraph();
    console.log('Graph cleared and reinitialized');
  }

  /**
   * Export graph to JSON
   */
  public exportGraph(): string {
    const exportData = {
      nodes: Array.from(this.graph.nodes.values()),
      edges: Array.from(this.graph.edges.values())
    };
    
    return JSON.stringify(exportData);
  }

  /**
   * Import graph from JSON
   */
  public importGraph(jsonData: string): void {
    try {
      const importData = JSON.parse(jsonData);
      
      this.clearGraph();
      
      if (importData.nodes) {
        importData.nodes.forEach((node: GraphNode) => {
          this.addNode(node);
        });
      }
      
      if (importData.edges) {
        importData.edges.forEach((edge: GraphEdge) => {
          this.addEdge(edge);
        });
      }
      
      console.log('Graph imported successfully');
    } catch (error) {
      console.error('Error importing graph:', error);
    }
  }
} 