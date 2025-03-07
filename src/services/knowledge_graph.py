import os
import json
import networkx as nx
from typing import List, Dict, Any, Optional
import random
from datetime import datetime, timedelta

from models.graph import (
    Node, Edge, GraphTopology, GraphMetrics, 
    TopicCluster, BridgeNode, EmergingTopic, ContentRecommendation
)
from models.content import Content, ContentInDB
from models.user import User, UserInDB

class KnowledgeGraphService:
    """Service for knowledge graph management and analysis."""
    
    def __init__(self):
        """Initialize knowledge graph service."""
        self.db_path = os.getenv("GRAPH_DB_PATH", "./data/graph.json")
        self._ensure_db_exists()
        self.graph = self._load_graph()
        
    def _ensure_db_exists(self):
        """Ensure the graph database file exists."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        if not os.path.exists(self.db_path):
            with open(self.db_path, "w") as f:
                json.dump({"nodes": [], "edges": []}, f)
    
    def _load_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load graph data from the database."""
        with open(self.db_path, "r") as f:
            return json.load(f)
    
    def _save_data(self, data: Dict[str, List[Dict[str, Any]]]):
        """Save graph data to the database."""
        with open(self.db_path, "w") as f:
            json.dump(data, f, default=str)
    
    def _load_graph(self) -> nx.DiGraph:
        """Load graph from database into NetworkX."""
        data = self._load_data()
        G = nx.DiGraph()
        
        # Add nodes
        for node_data in data["nodes"]:
            G.add_node(
                node_data["id"],
                type=node_data["type"],
                entity_id=node_data["entity_id"],
                properties=node_data.get("properties", {})
            )
        
        # Add edges
        for edge_data in data["edges"]:
            G.add_edge(
                edge_data["source_id"],
                edge_data["target_id"],
                id=edge_data["id"],
                type=edge_data["type"],
                weight=edge_data.get("weight", 1.0),
                properties=edge_data.get("properties", {})
            )
        
        return G
    
    def _save_graph(self):
        """Save NetworkX graph to database."""
        nodes = []
        edges = []
        
        # Convert nodes
        for node_id in self.graph.nodes:
            node_data = self.graph.nodes[node_id]
            nodes.append({
                "id": node_id,
                "type": node_data["type"],
                "entity_id": node_data["entity_id"],
                "properties": node_data.get("properties", {}),
                "created_at": node_data.get("created_at", datetime.now()),
                "updated_at": datetime.now()
            })
        
        # Convert edges
        for source_id, target_id, edge_data in self.graph.edges(data=True):
            edges.append({
                "id": edge_data["id"],
                "type": edge_data["type"],
                "source_id": source_id,
                "target_id": target_id,
                "weight": edge_data.get("weight", 1.0),
                "properties": edge_data.get("properties", {}),
                "created_at": edge_data.get("created_at", datetime.now()),
                "updated_at": datetime.now()
            })
        
        self._save_data({"nodes": nodes, "edges": edges})
    
    def get_node_id(self, node_or_id):
        """Get node ID from a node object or ID string."""
        if isinstance(node_or_id, str):
            return node_or_id
        elif hasattr(node_or_id, 'id'):
            return node_or_id.id
        else:
            raise ValueError(f"Cannot extract ID from {node_or_id}")

    def node_exists(self, node_type: str, entity_id: str) -> Optional[str]:
        """Check if a node with the given type and entity_id exists and return its ID if found."""
        for node_id, attrs in self.graph.nodes(data=True):
            if attrs.get("type") == node_type and attrs.get("entity_id") == entity_id:
                return node_id
        return None

    def add_node(self, node_type: str, entity_id: str, properties: Dict[str, Any] = None) -> Node:
        """Add a node to the graph if it doesn't exist, or return existing node."""
        # Check if node already exists
        existing_node_id = self.node_exists(node_type, entity_id)
        if existing_node_id:
            # Return existing node data
            node_data = self.graph.nodes[existing_node_id]
            return Node(
                id=existing_node_id,
                type=node_data["type"],
                entity_id=node_data["entity_id"],
                properties=node_data.get("properties", {}),
                created_at=node_data.get("created_at", datetime.now()),
                updated_at=datetime.now()
            )
        
        # Create new node
        node = Node(
            type=node_type,
            entity_id=entity_id,
            properties=properties or {}
        )
        
        # Add to NetworkX graph
        self.graph.add_node(
            node.id,
            type=node.type,
            entity_id=node.entity_id,
            properties=node.properties,
            created_at=node.created_at
        )
        
        # Save graph
        self._save_graph()
        
        return node
    
    def add_edge(self, edge_type: str, source_id: str, target_id: str, 
                weight: float = 1.0, properties: Dict[str, Any] = None) -> Edge:
        """Add an edge to the graph."""
        # Ensure source_id and target_id are strings
        source_id = self.get_node_id(source_id)
        target_id = self.get_node_id(target_id)
        
        # Check if nodes exist
        if source_id not in self.graph.nodes:
            raise ValueError(f"Source node {source_id} does not exist")
        if target_id not in self.graph.nodes:
            raise ValueError(f"Target node {target_id} does not exist")
        
        # Create edge
        edge = Edge(
            type=edge_type,
            source_id=source_id,
            target_id=target_id,
            weight=weight,
            properties=properties or {}
        )
        
        # Add to NetworkX graph
        self.graph.add_edge(
            source_id,
            target_id,
            id=edge.id,
            type=edge.type,
            weight=edge.weight,
            properties=edge.properties,
            created_at=edge.created_at
        )
        
        # Save graph
        self._save_graph()
        
        return edge
    
    def get_topology(self, limit: int = 1000) -> GraphTopology:
        """Get current graph structure."""
        data = self._load_data()
        
        # Apply limit
        nodes = data["nodes"][:limit]
        
        # Only include edges between nodes in the limited set
        node_ids = {node["id"] for node in nodes}
        edges = [
            edge for edge in data["edges"]
            if edge["source_id"] in node_ids and edge["target_id"] in node_ids
        ]
        
        # Convert to models
        node_models = [Node(**node) for node in nodes]
        edge_models = [Edge(**edge) for edge in edges]
        
        return GraphTopology(nodes=node_models, edges=edge_models)
    
    def get_metrics(self) -> GraphMetrics:
        """Get graph analytics and statistics."""
        G = self.graph
        
        # Calculate metrics
        node_count = G.number_of_nodes()
        edge_count = G.number_of_edges()
        
        # Average node degree
        avg_node_degree = 0
        if node_count > 0:
            avg_node_degree = edge_count / node_count
        
        # Clustering coefficient (convert to undirected for this calculation)
        undirected_G = G.to_undirected()
        clustering_coefficient = nx.average_clustering(undirected_G)
        
        # Connected components
        connected_components = nx.number_weakly_connected_components(G)
        
        return GraphMetrics(
            node_count=node_count,
            edge_count=edge_count,
            avg_node_degree=avg_node_degree,
            clustering_coefficient=clustering_coefficient,
            connected_components=connected_components
        )
    
    def get_topic_clusters(self, limit: int = 10) -> List[TopicCluster]:
        """Get major content and topic hubs."""
        G = self.graph
        
        # Filter nodes to only include topic and hashtag nodes
        topic_nodes = [
            node for node, attrs in G.nodes(data=True)
            if attrs.get("type") in ["topic", "hashtag"]
        ]
        
        # Calculate degree centrality for topic nodes
        topic_subgraph = G.subgraph(topic_nodes)
        centrality = nx.degree_centrality(topic_subgraph)
        
        # Sort by centrality
        sorted_topics = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        
        # Create clusters
        clusters = []
        for i, (node_id, centrality_score) in enumerate(sorted_topics[:limit]):
            # Get node attributes
            node_attrs = G.nodes[node_id]
            
            # Get connected nodes
            neighbors = list(G.neighbors(node_id))
            
            # Get related topics
            related_topics = [
                G.nodes[n]["entity_id"] for n in neighbors
                if G.nodes[n]["type"] in ["topic", "hashtag"]
            ]
            
            # Create cluster
            cluster = TopicCluster(
                id=f"cluster_{i}",
                name=node_attrs.get("properties", {}).get("name", node_attrs["entity_id"]),
                size=len(neighbors),
                central_nodes=[node_id],
                related_topics=related_topics[:5]  # Limit to 5 related topics
            )
            
            clusters.append(cluster)
        
        return clusters
    
    def get_bridge_nodes(self, limit: int = 10) -> List[BridgeNode]:
        """Get bridge nodes connecting content domains."""
        G = self.graph
        
        # Calculate betweenness centrality
        betweenness = nx.betweenness_centrality(G)
        
        # Sort by betweenness
        sorted_nodes = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
        
        # Create bridge nodes
        bridges = []
        for i, (node_id, betweenness_score) in enumerate(sorted_nodes[:limit]):
            # Get node attributes
            node_attrs = G.nodes[node_id]
            
            # Get connected clusters
            # In a real implementation, this would identify which clusters the node connects
            # For now, we'll just use a placeholder
            connected_clusters = [f"cluster_{j}" for j in range(min(3, i+1))]
            
            # Create bridge node
            bridge = BridgeNode(
                id=node_id,
                type=node_attrs["type"],
                entity_id=node_attrs["entity_id"],
                connected_clusters=connected_clusters,
                betweenness_centrality=betweenness_score
            )
            
            bridges.append(bridge)
        
        return bridges
    
    def get_emerging_topics(self, limit: int = 10) -> List[EmergingTopic]:
        """Get emerging topics based on attention patterns."""
        G = self.graph
        
        # In a real implementation, this would analyze temporal patterns
        # For now, we'll create some placeholder data
        topics = []
        for i in range(limit):
            topic = EmergingTopic(
                topic=f"Emerging Topic {i+1}",
                growth_rate=random.uniform(1.1, 2.0),
                related_hashtags=[f"hashtag{j}" for j in range(3)],
                key_content=[f"content_{random.randint(1, 100)}" for _ in range(3)]
            )
            topics.append(topic)
        
        return topics
    
    def get_visualization_data(self, node_limit: int = 100, include_users: bool = True, 
                              include_content: bool = True, include_topics: bool = True) -> Dict:
        """Get graph visualization data."""
        G = self.graph
        
        # Filter nodes based on parameters
        node_types_to_include = []
        if include_users:
            node_types_to_include.append("user")
        if include_content:
            node_types_to_include.append("content")
        if include_topics:
            node_types_to_include.extend(["topic", "hashtag"])
        
        filtered_nodes = [
            node for node, attrs in G.nodes(data=True)
            if attrs.get("type") in node_types_to_include
        ]
        
        # Apply limit
        if len(filtered_nodes) > node_limit:
            filtered_nodes = filtered_nodes[:node_limit]
        
        # Create subgraph
        subgraph = G.subgraph(filtered_nodes)
        
        # Convert to visualization format
        vis_nodes = []
        for node_id in subgraph.nodes():
            attrs = subgraph.nodes[node_id]
            vis_nodes.append({
                "id": node_id,
                "label": attrs.get("properties", {}).get("name", attrs["entity_id"]),
                "type": attrs["type"],
                "size": 5 + len(list(G.neighbors(node_id))) * 0.5  # Size based on degree
            })
        
        vis_edges = []
        for source, target, attrs in subgraph.edges(data=True):
            vis_edges.append({
                "id": attrs["id"],
                "source": source,
                "target": target,
                "type": attrs["type"],
                "weight": attrs.get("weight", 1.0)
            })
        
        return {
            "nodes": vis_nodes,
            "edges": vis_edges
        }
    
    def get_recommendations(self, user_id: Optional[str], limit: int = 10) -> List[ContentRecommendation]:
        """Get personalized content recommendations."""
        # In a real implementation, this would use graph algorithms
        # For now, we'll create some placeholder recommendations
        recommendations = []
        for i in range(limit):
            recommendation = ContentRecommendation(
                content_id=f"content_{random.randint(1, 100)}",
                score=random.uniform(0.5, 1.0),
                reason=f"Based on your interest in {random.choice(['technology', 'science', 'art', 'music'])}"
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_related_content(self, content_id: str, limit: int = 10) -> List[ContentRecommendation]:
        """Get content related to a specific piece of content."""
        G = self.graph
        
        # Find content node
        content_nodes = [
            node for node, attrs in G.nodes(data=True)
            if attrs.get("type") == "content" and attrs.get("entity_id") == content_id
        ]
        
        if not content_nodes:
            return []
        
        content_node = content_nodes[0]
        
        # In a real implementation, this would use graph traversal
        # For now, we'll create some placeholder recommendations
        recommendations = []
        for i in range(limit):
            recommendation = ContentRecommendation(
                content_id=f"content_{random.randint(1, 100)}",
                score=random.uniform(0.5, 1.0),
                reason=f"Related to content through {random.choice(['topic', 'creator', 'hashtag'])}"
            )
            recommendations.append(recommendation)
        
        return recommendations
    
    def get_similar_users(self, user_id: str, limit: int = 10) -> List[User]:
        """Get users similar to a specific user based on graph analysis."""
        # In a real implementation, this would use graph algorithms
        # For now, we'll return an empty list
        return []
    
    def get_topic_map(self, depth: int = 2) -> Dict:
        """Get hierarchical topic map from the knowledge graph."""
        # In a real implementation, this would create a hierarchical structure
        # For now, we'll create a simple placeholder
        return {
            "name": "Root",
            "children": [
                {
                    "name": f"Topic {i}",
                    "children": [
                        {"name": f"Subtopic {i}.{j}", "value": random.randint(1, 100)}
                        for j in range(3)
                    ]
                }
                for i in range(5)
            ]
        }
    
    def find_content_path(self, source_id: str, target_id: str) -> List[Dict]:
        """Find the shortest path between two content nodes."""
        G = self.graph
        
        # Find content nodes
        source_nodes = [
            node for node, attrs in G.nodes(data=True)
            if attrs.get("type") == "content" and attrs.get("entity_id") == source_id
        ]
        
        target_nodes = [
            node for node, attrs in G.nodes(data=True)
            if attrs.get("type") == "content" and attrs.get("entity_id") == target_id
        ]
        
        if not source_nodes or not target_nodes:
            return []
        
        source_node = source_nodes[0]
        target_node = target_nodes[0]
        
        # Try to find path
        try:
            path = nx.shortest_path(G, source=source_node, target=target_node)
            
            # Convert path to response format
            result = []
            for node_id in path:
                attrs = G.nodes[node_id]
                result.append({
                    "id": node_id,
                    "type": attrs["type"],
                    "entity_id": attrs["entity_id"]
                })
            
            return result
        except nx.NetworkXNoPath:
            return [] 