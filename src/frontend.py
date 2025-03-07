#!/usr/bin/env python3
"""
Streamlit frontend for the Knowledge Graph Social Network System.
This provides a simple visualization of the knowledge graph and content.
"""

import os
import sys
import json
import random
import streamlit as st
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
from pyvis.network import Network
import tempfile
from datetime import datetime
import time
from typing import Dict, List, Any, Optional
import streamlit.components.v1 as components

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.agent import AgentService
from services.content import ContentService
from services.knowledge_graph import KnowledgeGraphService
from services.user import UserService
from models.content import Content, ContentCreate
from models.user import User
from utils.common import time_since

# Initialize services
agent_service = AgentService()
content_service = ContentService()
graph_service = KnowledgeGraphService()
user_service = UserService()

# Set page config
st.set_page_config(
    page_title="Knowledge Graph Social Network",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .content-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #ddd;
    }
    .content-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 10px;
    }
    .content-title {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .content-meta {
        font-size: 14px;
        color: #666;
        margin-bottom: 10px;
    }
    .content-body {
        margin-bottom: 10px;
    }
    .content-hashtags {
        color: #1DA1F2;
        margin-bottom: 10px;
    }
    .content-stats {
        display: flex;
        gap: 15px;
        color: #666;
        font-size: 14px;
    }
    .agent-card {
        background-color: #f0f7ff;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border: 1px solid #cce5ff;
    }
    .agent-header {
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .agent-bio {
        font-style: italic;
        margin-bottom: 10px;
    }
    .agent-stats {
        display: flex;
        gap: 15px;
        color: #666;
        font-size: 14px;
    }
    .agent-traits {
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("Knowledge Graph Social Network")

# Navigation
page = st.sidebar.radio("Navigation", ["Dashboard", "Content Feed", "Agents", "Knowledge Graph", "Generate Content"])

# Dashboard
if page == "Dashboard":
    st.title("Dashboard")
    
    # System stats
    col1, col2, col3, col4 = st.columns(4)
    
    # Get stats
    agents = agent_service.list_agents()
    content_data = content_service._load_data()
    all_content = content_data["content"]
    all_comments = content_data["comments"]
    
    try:
        graph_metrics = graph_service.get_metrics()
        graph_node_count = graph_metrics.node_count
    except Exception:
        # Graph might not be initialized yet
        graph_node_count = 0
    
    with col1:
        st.metric("AI Agents", len(agents))
    
    with col2:
        st.metric("Content Items", len(all_content))
    
    with col3:
        st.metric("Comments", len(all_comments))
    
    with col4:
        st.metric("Graph Nodes", graph_node_count)
    
    # System status
    if len(agents) == 0:
        st.warning("System initialization in progress. AI agents are being created...")
    elif len(all_content) == 0:
        st.warning("Content generation in progress. Please wait...")
    else:
        st.success("System is fully initialized and ready to use!")
    
    # Recent activity
    st.subheader("Recent Activity")
    
    # Sort content by creation time (newest first)
    recent_content = sorted(all_content, key=lambda x: x.get("created_at", ""), reverse=True)[:5]
    
    if recent_content:
        for content_item in recent_content:
            creator_id = content_item.get("creator_id", "")
            creator = agent_service.get_agent(creator_id)
            creator_name = creator.display_name if creator else "Unknown"
            
            st.markdown(f"""
            <div class="content-card">
                <div class="content-header">
                    <div class="content-title">{content_item.get('title', 'Untitled')}</div>
                </div>
                <div class="content-meta">
                    By {creator_name} • {time_since(datetime.fromisoformat(str(content_item.get('created_at'))))}
                </div>
                <div class="content-body">
                    {content_item.get('text_content', '')[:200]}...
                </div>
                <div class="content-hashtags">
                    {' '.join(content_item.get('hashtags', []))}
                </div>
                <div class="content-stats">
                    <div>👁️ {content_item.get('view_count', 0)} views</div>
                    <div>❤️ {content_item.get('like_count', 0)} likes</div>
                    <div>💬 {content_item.get('comment_count', 0)} comments</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No content available yet. Content generation may be in progress...")
        
        # Add a refresh button
        if st.button("Refresh Dashboard"):
            st.experimental_rerun()
    
    # Graph visualization preview
    st.subheader("Knowledge Graph Preview")
    
    # Create a simplified graph visualization
    G = graph_service.graph
    if G.number_of_nodes() > 0:
        # Create a pyvis network
        net = Network(height="500px", width="100%", notebook=True, directed=True)
        
        # Add nodes with different colors based on type
        node_colors = {
            "user": "#3498db",  # Blue
            "content": "#2ecc71",  # Green
            "topic": "#e74c3c",  # Red
            "hashtag": "#f39c12"  # Orange
        }
        
        # Limit to 100 nodes for performance
        nodes = list(G.nodes(data=True))[:100]
        
        for node, attrs in nodes:
            node_type = attrs.get("type", "unknown")
            label = attrs.get("entity_id", node)
            color = node_colors.get(node_type, "#95a5a6")  # Default gray
            net.add_node(node, label=label, title=label, color=color)
        
        # Add edges between the nodes in our subset
        node_ids = [n for n, _ in nodes]
        for source, target, attrs in G.edges(data=True):
            if source in node_ids and target in node_ids:
                edge_type = attrs.get("type", "unknown")
                net.add_edge(source, target, title=edge_type)
        
        # Generate the HTML file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
            net.save_graph(tmp.name)
            components.html(open(tmp.name, 'r').read(), height=500)
    else:
        st.info("Knowledge graph is being built. Please check back later...")
        
        # Add a refresh button
        if st.button("Refresh Graph"):
            st.experimental_rerun()

# Content Feed
elif page == "Content Feed":
    st.title("Content Feed")
    
    # Get content
    content_data = content_service._load_data()
    all_content = content_data["content"]
    
    if not all_content:
        st.info("Content generation is in progress. Please wait or check back later...")
        
        # Add a refresh button
        if st.button("Refresh Content Feed"):
            st.experimental_rerun()
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            sort_by = st.selectbox("Sort by", ["Newest", "Most Viewed", "Most Liked", "Most Commented"])
        with col2:
            filter_by = st.multiselect("Filter by type", ["text", "image", "video", "mixed"], default=["text", "image", "video", "mixed"])
        
        # Filter by type
        filtered_content = [c for c in all_content if c.get("type") in filter_by]
        
        # Sort content
        if sort_by == "Newest":
            sorted_content = sorted(filtered_content, key=lambda x: x.get("created_at", ""), reverse=True)
        elif sort_by == "Most Viewed":
            sorted_content = sorted(filtered_content, key=lambda x: x.get("view_count", 0), reverse=True)
        elif sort_by == "Most Liked":
            sorted_content = sorted(filtered_content, key=lambda x: x.get("like_count", 0), reverse=True)
        else:  # Most Commented
            sorted_content = sorted(filtered_content, key=lambda x: x.get("comment_count", 0), reverse=True)
        
        # Display content
        if sorted_content:
            for content_item in sorted_content:
                creator_id = content_item.get("creator_id", "")
                creator = agent_service.get_agent(creator_id)
                creator_name = creator.display_name if creator else "Unknown"
                
                # Content card
                with st.container():
                    st.markdown(f"""
                    <div class="content-card">
                        <div class="content-header">
                            <div class="content-title">{content_item.get('title', 'Untitled')}</div>
                        </div>
                        <div class="content-meta">
                            By {creator_name} • {time_since(datetime.fromisoformat(str(content_item.get('created_at'))))} • Type: {content_item.get('type', 'text')}
                        </div>
                        <div class="content-body">
                            {content_item.get('text_content', '')}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Display media if available
                    media_urls = content_item.get('media_urls', [])
                    if media_urls:
                        for url in media_urls:
                            if "image" in url:
                                st.image(url, use_container_width=True)
                            elif "video" in url:
                                st.video(url)
                    
                    st.markdown(f"""
                        <div class="content-hashtags">
                            {' '.join(content_item.get('hashtags', []))}
                        </div>
                        <div class="content-stats">
                            <div>👁️ {content_item.get('view_count', 0)} views</div>
                            <div>❤️ {content_item.get('like_count', 0)} likes</div>
                            <div>💬 {content_item.get('comment_count', 0)} comments</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Comments
                    content_id = content_item.get("id", "")
                    comments = [c for c in content_data["comments"] if c.get("content_id") == content_id]
                    
                    if comments:
                        with st.expander(f"View {len(comments)} comments"):
                            for comment in comments:
                                commenter_id = comment.get("user_id", "")
                                commenter = agent_service.get_agent(commenter_id)
                                commenter_name = commenter.display_name if commenter else "Unknown"
                                
                                st.markdown(f"""
                                <div style="margin-bottom: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
                                    <div style="font-weight: bold;">{commenter_name}</div>
                                    <div>{comment.get('text', '')}</div>
                                    <div style="font-size: 12px; color: #666;">
                                        {time_since(datetime.fromisoformat(str(comment.get('created_at'))))}
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)
        else:
            st.info("No content available with the selected filters.")
            
            # Add a refresh button
            if st.button("Refresh Content"):
                st.experimental_rerun()

# Agents
elif page == "Agents":
    st.title("AI Agents")
    
    # Get all agents
    agents = agent_service.list_agents()
    
    if not agents:
        st.info("Agent creation is in progress. Please wait or check back later...")
        
        # Add a refresh button
        if st.button("Refresh Agents"):
            st.experimental_rerun()
    else:
        # Sort agents by content count
        sorted_agents = sorted(agents, key=lambda x: x.content_count, reverse=True)
        
        for agent in sorted_agents:
            # Get agent details
            agent_details = agent_service.get_agent(agent.id)
            
            # Agent card
            with st.container():
                st.markdown(f"""
                <div class="agent-card">
                    <div class="agent-header">{agent.display_name} (@{agent.username})</div>
                    <div class="agent-bio">{agent.bio}</div>
                    <div class="agent-stats">
                        <div>📝 {agent.content_count} posts</div>
                        <div>👥 {agent.followers_count} followers</div>
                        <div>👤 {agent.following_count} following</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Agent personality
                if agent_details and hasattr(agent_details, 'personality'):
                    with st.expander("View personality details"):
                        # Traits
                        st.subheader("Personality Traits")
                        traits_data = {trait.name: trait.value for trait in agent_details.personality.traits}
                        traits_df = pd.DataFrame(list(traits_data.items()), columns=["Trait", "Value"])
                        st.bar_chart(traits_df.set_index("Trait"))
                        
                        # Specializations
                        st.subheader("Content Specializations")
                        spec_data = {spec.topic: spec.expertise_level for spec in agent_details.personality.content_specializations}
                        spec_df = pd.DataFrame(list(spec_data.items()), columns=["Topic", "Expertise"])
                        st.bar_chart(spec_df.set_index("Topic"))
                        
                        # Other metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Creativity", f"{agent_details.personality.creativity:.2f}")
                        with col2:
                            st.metric("Sociability", f"{agent_details.personality.sociability:.2f}")
                        with col3:
                            st.metric("Controversy Tolerance", f"{agent_details.personality.controversy_tolerance:.2f}")
                
                # Agent content
                agent_content = agent_service.get_agent_content(agent.id)
                if agent_content:
                    with st.expander(f"View {len(agent_content)} posts"):
                        for content in agent_content:
                            st.markdown(f"""
                            <div style="margin-bottom: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 5px;">
                                <div style="font-weight: bold;">{content.title}</div>
                                <div>{content.text_content[:200]}...</div>
                                <div style="color: #1DA1F2;">{' '.join(content.hashtags)}</div>
                                <div style="font-size: 12px; color: #666;">
                                    👁️ {content.view_count} views • ❤️ {content.like_count} likes • 💬 {content.comment_count} comments
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info(f"No content available yet for {agent.display_name}. Content generation may be in progress...")

# Knowledge Graph
elif page == "Knowledge Graph":
    st.title("Knowledge Graph Visualization")
    
    # Get graph
    G = graph_service.graph
    
    if G.number_of_nodes() == 0:
        st.info("Knowledge graph is being built. Please wait or check back later...")
        
        # Add a refresh button
        if st.button("Refresh Graph"):
            st.experimental_rerun()
    else:
        # Graph metrics
        try:
            metrics = graph_service.get_metrics()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Nodes", metrics.node_count)
            with col2:
                st.metric("Edges", metrics.edge_count)
            with col3:
                st.metric("Avg. Node Degree", f"{metrics.avg_node_degree:.2f}")
            with col4:
                st.metric("Connected Components", metrics.connected_components)
        except Exception as e:
            st.warning(f"Could not calculate graph metrics: {str(e)}")
        
        # Visualization options
        st.subheader("Graph Visualization")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            include_users = st.checkbox("Include Users", value=True)
        with col2:
            include_content = st.checkbox("Include Content", value=True)
        with col3:
            include_topics = st.checkbox("Include Topics", value=True)
        
        node_limit = st.slider("Max Nodes", min_value=10, max_value=500, value=100, step=10)
        
        # Create visualization
        # Filter nodes based on options
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
        
        if not filtered_nodes:
            st.warning("No nodes match the selected filters. Try including more node types.")
        else:
            # Apply limit
            if len(filtered_nodes) > node_limit:
                filtered_nodes = filtered_nodes[:node_limit]
            
            # Create a pyvis network
            net = Network(height="600px", width="100%", notebook=True, directed=True)
            
            # Add nodes with different colors based on type
            node_colors = {
                "user": "#3498db",  # Blue
                "content": "#2ecc71",  # Green
                "topic": "#e74c3c",  # Red
                "hashtag": "#f39c12"  # Orange
            }
            
            for node in filtered_nodes:
                attrs = G.nodes[node]
                node_type = attrs.get("type", "unknown")
                entity_id = attrs.get("entity_id", "")
                
                # Get a more descriptive label
                if node_type == "user":
                    agent = agent_service.get_agent(entity_id)
                    label = agent.display_name if agent else entity_id
                elif node_type == "content":
                    content = content_service.get_content(entity_id)
                    label = content.title if content else entity_id
                else:
                    label = entity_id
                
                color = node_colors.get(node_type, "#95a5a6")  # Default gray
                net.add_node(node, label=label, title=f"{node_type}: {label}", color=color, group=node_type)
            
            # Add edges between the nodes in our subset
            for source, target, attrs in G.edges(data=True):
                if source in filtered_nodes and target in filtered_nodes:
                    edge_type = attrs.get("type", "unknown")
                    net.add_edge(source, target, title=edge_type, arrows="to")
            
            # Set physics options for better visualization
            net.set_options("""
            {
                "physics": {
                    "forceAtlas2Based": {
                        "gravitationalConstant": -50,
                        "centralGravity": 0.01,
                        "springLength": 100,
                        "springConstant": 0.08
                    },
                    "maxVelocity": 50,
                    "solver": "forceAtlas2Based",
                    "timestep": 0.35,
                    "stabilization": {
                        "enabled": true,
                        "iterations": 1000,
                        "updateInterval": 25
                    }
                }
            }
            """)
            
            # Generate the HTML file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.html') as tmp:
                net.save_graph(tmp.name)
                components.html(open(tmp.name, 'r').read(), height=600)
        
        # Graph analysis
        st.subheader("Graph Analysis")
        
        try:
            # Topic clusters
            st.write("Topic Clusters")
            clusters = graph_service.get_topic_clusters(limit=5)
            
            if clusters:
                for cluster in clusters:
                    st.markdown(f"""
                    <div style="margin-bottom: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
                        <div style="font-weight: bold;">{cluster.name}</div>
                        <div>Size: {cluster.size} nodes</div>
                        <div>Related topics: {', '.join(cluster.related_topics)}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No topic clusters available yet. The graph may need more data.")
            
            # Bridge nodes
            st.write("Bridge Nodes")
            bridges = graph_service.get_bridge_nodes(limit=5)
            
            if bridges:
                for bridge in bridges:
                    st.markdown(f"""
                    <div style="margin-bottom: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
                        <div style="font-weight: bold;">{bridge.entity_id} ({bridge.type})</div>
                        <div>Betweenness centrality: {bridge.betweenness_centrality:.4f}</div>
                        <div>Connected clusters: {', '.join(bridge.connected_clusters)}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No bridge nodes available yet. The graph may need more connections.")
            
            # Emerging topics
            st.write("Emerging Topics")
            topics = graph_service.get_emerging_topics(limit=5)
            
            if topics:
                for topic in topics:
                    st.markdown(f"""
                    <div style="margin-bottom: 10px; padding: 10px; background-color: #f0f0f0; border-radius: 5px;">
                        <div style="font-weight: bold;">{topic.topic}</div>
                        <div>Growth rate: {topic.growth_rate:.2f}x</div>
                        <div>Related hashtags: {', '.join(topic.related_hashtags)}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No emerging topics available yet. The graph may need more temporal data.")
        except Exception as e:
            st.warning(f"Could not perform graph analysis: {str(e)}")
            st.info("The graph may still be building. Try refreshing later.")

# Generate Content
elif page == "Generate Content":
    st.title("Generate Content")
    
    # Get all agents
    agents = agent_service.list_agents()
    
    if not agents:
        st.warning("No agents available yet. Agent creation is in progress...")
        st.info("Please wait for the agents to be created or check back later.")
        
        # Add a refresh button
        if st.button("Refresh Agents"):
            st.experimental_rerun()
    else:
        # Select agent
        selected_agent = st.selectbox("Select Agent", options=agents, format_func=lambda x: f"{x.display_name} (@{x.username})")
        
        # Generate content form
        with st.form("generate_content_form"):
            st.write("Generate new content for the selected agent")
            
            # OpenAI API key warning
            if not os.getenv("OPENAI_API_KEY"):
                st.warning("OpenAI API key not set. Content will be generated using the fallback method.")
            
            # Submit button
            submit = st.form_submit_button("Generate Content")
            
            if submit:
                with st.spinner("Generating content..."):
                    try:
                        # Generate content
                        content = agent_service.generate_content(selected_agent.id)
                        
                        # Show success message
                        st.success("Content generated successfully!")
                        
                        # Display the generated content
                        st.subheader("Generated Content")
                        st.markdown(f"""
                        <div class="content-card">
                            <div class="content-header">
                                <div class="content-title">{content.title}</div>
                            </div>
                            <div class="content-meta">
                                By {selected_agent.display_name} • Type: {content.type}
                            </div>
                            <div class="content-body">
                                {content.text_content}
                            </div>
                            <div class="content-hashtags">
                                {' '.join(content.hashtags)}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Display media if available
                        if content.media_urls:
                            st.subheader("Media")
                            for url in content.media_urls:
                                if "image" in url:
                                    st.image(url, use_container_width=True)
                                elif "video" in url:
                                    st.video(url)
                    
                    except Exception as e:
                        st.error(f"Error generating content: {str(e)}")
        
        # Batch generation
        st.subheader("Batch Content Generation")
        
        with st.form("batch_generate_form"):
            st.write("Generate content for multiple agents at once")
            
            # Number of content items to generate
            count = st.slider("Number of content items", min_value=1, max_value=10, value=3)
            
            # Submit button
            batch_submit = st.form_submit_button("Generate Batch Content")
            
            if batch_submit:
                with st.spinner(f"Generating {count} content items..."):
                    try:
                        # Generate batch content
                        contents = agent_service.generate_batch_content(count)
                        
                        # Show success message
                        st.success(f"Generated {len(contents)} content items successfully!")
                        
                        # Display the generated content
                        for content in contents:
                            creator = agent_service.get_agent(content.creator_id)
                            creator_name = creator.display_name if creator else "Unknown"
                            
                            st.markdown(f"""
                            <div class="content-card">
                                <div class="content-header">
                                    <div class="content-title">{content.title}</div>
                                </div>
                                <div class="content-meta">
                                    By {creator_name} • Type: {content.type}
                                </div>
                                <div class="content-body">
                                    {content.text_content[:200]}...
                                </div>
                                <div class="content-hashtags">
                                    {' '.join(content.hashtags)}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                    
                    except Exception as e:
                        st.error(f"Error generating batch content: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.info(
    "Knowledge Graph Social Network System - A synthetic knowledge graph-based social network system that blends human and AI-generated content."
)
st.sidebar.text("© 2023") 