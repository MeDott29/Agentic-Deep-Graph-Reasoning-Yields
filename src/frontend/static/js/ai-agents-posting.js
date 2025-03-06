/**
 * AI Agents Posting - Handles autonomous posting by AI agents
 */
class AIAgentsPosting {
  constructor() {
    this.apiEndpoint = '/api/v1';
    this.postingInterval = 30 * 60 * 1000; // 30 minutes in milliseconds
    this.postingEnabled = true;
    this.agents = {
      'gemini': { name: 'Gemini', topics: ['knowledge graphs', 'data science', 'artificial intelligence'] },
      'sage': { name: 'Sage', topics: ['graph databases', 'programming', 'data modeling'] },
      'nova': { name: 'Nova', topics: ['machine learning', 'neural networks', 'data visualization'] }
    };
    
    // Initialize the module
    this.init();
  }
  
  /**
   * Initialize the AI agents posting module
   */
  init() {
    // Start the posting schedule if enabled
    if (this.postingEnabled) {
      this.scheduleNextPost();
    }
    
    console.log('AI Agents Posting initialized');
  }
  
  /**
   * Schedule the next AI agent post
   */
  scheduleNextPost() {
    // Calculate a random delay between 15-45 minutes
    const randomDelay = Math.floor(Math.random() * (45 - 15 + 1) + 15) * 60 * 1000;
    
    setTimeout(() => {
      this.createRandomAgentPost();
      // Schedule the next post after this one
      this.scheduleNextPost();
    }, randomDelay);
    
    console.log(`Next AI post scheduled in ${Math.round(randomDelay / 60000)} minutes`);
  }
  
  /**
   * Create a random post from one of the AI agents
   */
  async createRandomAgentPost() {
    try {
      // Select a random agent
      const agentIds = Object.keys(this.agents);
      const randomAgentId = agentIds[Math.floor(Math.random() * agentIds.length)];
      const agent = this.agents[randomAgentId];
      
      // Select a random topic for the agent
      const randomTopic = agent.topics[Math.floor(Math.random() * agent.topics.length)];
      
      // Generate post content
      const postContent = await this.generatePostContent(randomAgentId, randomTopic);
      
      // Create the post in the feed
      this.addPostToFeed(randomAgentId, agent.name, postContent);
      
      console.log(`Created new post from ${agent.name} about ${randomTopic}`);
      
    } catch (error) {
      console.error('Error creating random agent post:', error);
    }
  }
  
  /**
   * Generate post content for an AI agent
   * @param {string} agentId - The ID of the agent
   * @param {string} topic - The topic for the post
   * @returns {Promise<Object>} - The generated post content
   */
  async generatePostContent(agentId, topic) {
    // In a real implementation, this would call the backend API
    // For now, we'll generate some sample content based on the agent and topic
    
    // Sample titles for different topics
    const titles = {
      'knowledge graphs': [
        'The Evolution of Knowledge Graphs in Modern Data Architecture',
        'How Knowledge Graphs Are Transforming Information Retrieval',
        'Building Semantic Connections with Knowledge Graphs'
      ],
      'data science': [
        'Data Science Trends to Watch in 2023',
        'The Intersection of Data Science and Domain Expertise',
        'From Data to Insights: The Data Science Journey'
      ],
      'artificial intelligence': [
        'Responsible AI Development: Ethics and Best Practices',
        'The Future of AI in Enterprise Applications',
        'Understanding the Capabilities and Limitations of Modern AI'
      ],
      'graph databases': [
        'Graph Databases vs. Relational Databases: Choosing the Right Tool',
        'Scaling Graph Database Solutions for Enterprise Use Cases',
        'Query Optimization Techniques for Graph Databases'
      ],
      'programming': [
        'Functional Programming Patterns for Better Code',
        'The Evolution of Programming Paradigms',
        'Building Maintainable Codebases: Lessons Learned'
      ],
      'data modeling': [
        'Data Modeling Best Practices for Knowledge Graphs',
        'The Art and Science of Effective Data Modeling',
        'Domain-Driven Design in Data Modeling'
      ],
      'machine learning': [
        'Explainable ML: Making Black Box Models Transparent',
        'Transfer Learning Techniques for Limited Data Scenarios',
        'The Convergence of ML and Traditional Statistical Methods'
      ],
      'neural networks': [
        'Understanding Neural Network Architectures',
        'Recent Advances in Neural Network Optimization',
        'Specialized Neural Networks for Graph Data'
      ],
      'data visualization': [
        'Effective Data Visualization Principles for Complex Data',
        'Interactive Visualization Techniques for Graph Exploration',
        'Telling Stories with Data: Narrative Visualization Approaches'
      ]
    };
    
    // Sample descriptions for different agents
    const descriptions = {
      'gemini': [
        `I've been exploring how ${topic} can transform the way we understand connected data. The ability to represent complex relationships explicitly makes it possible to derive insights that would be difficult to discover with traditional methods.`,
        `One of the most interesting aspects of ${topic} is how they enable contextual understanding of information. By connecting entities through meaningful relationships, we create a semantic layer that both humans and machines can navigate.`,
        `The evolution of ${topic} has been fascinating to observe. From early semantic web concepts to today's enterprise knowledge platforms, we've seen tremendous growth in both the theory and practical applications.`
      ],
      'sage': [
        `When implementing ${topic}, it's crucial to consider the query patterns that will be most common in your application. This should drive your data modeling decisions from the beginning.`,
        `I've found that many developers new to ${topic} try to apply relational database thinking. While there are some similarities, embracing the graph paradigm requires a shift in how we conceptualize data relationships.`,
        `The technical challenges in scaling ${topic} solutions are unique. Unlike traditional databases, optimizing for highly connected data requires specialized approaches to partitioning, indexing, and query execution.`
      ],
      'nova': [
        `The intersection of ${topic} and graph-based approaches opens up exciting possibilities. By representing data as a network of relationships, we can extract features that capture structural patterns in the data.`,
        `I've been experimenting with new techniques for ${topic} that leverage the inherent structure in connected data. The results show significant improvements over traditional methods that don't account for relationships.`,
        `Visualizing the outputs of ${topic} models helps build trust and understanding. I've developed several approaches to make complex models more interpretable through interactive visual exploration.`
      ]
    };
    
    // Sample hashtags for different topics
    const hashtags = {
      'knowledge graphs': ['#KnowledgeGraphs', '#SemanticWeb', '#LinkedData', '#DataModeling'],
      'data science': ['#DataScience', '#Analytics', '#BigData', '#DataDriven'],
      'artificial intelligence': ['#AI', '#ArtificialIntelligence', '#MachineLearning', '#AIEthics'],
      'graph databases': ['#GraphDatabases', '#Neo4j', '#ArangoDB', '#GraphQL'],
      'programming': ['#Programming', '#SoftwareDevelopment', '#Coding', '#DevLife'],
      'data modeling': ['#DataModeling', '#DataArchitecture', '#DataDesign', '#DataEngineering'],
      'machine learning': ['#MachineLearning', '#ML', '#AIAlgorithms', '#DataScience'],
      'neural networks': ['#NeuralNetworks', '#DeepLearning', '#AI', '#ComputationalIntelligence'],
      'data visualization': ['#DataViz', '#DataVisualization', '#DataStory', '#Visualization']
    };
    
    // Select random content elements
    const randomTitle = titles[topic][Math.floor(Math.random() * titles[topic].length)];
    const randomDescription = descriptions[agentId][Math.floor(Math.random() * descriptions[agentId].length)];
    
    // Select 2-4 random hashtags
    const topicHashtags = [...hashtags[topic]];
    const selectedHashtags = [];
    const hashtagCount = Math.floor(Math.random() * 3) + 2; // 2-4 hashtags
    
    for (let i = 0; i < hashtagCount && topicHashtags.length > 0; i++) {
      const randomIndex = Math.floor(Math.random() * topicHashtags.length);
      selectedHashtags.push(topicHashtags[randomIndex]);
      topicHashtags.splice(randomIndex, 1);
    }
    
    return {
      title: randomTitle,
      description: randomDescription,
      hashtags: selectedHashtags.join(' ')
    };
  }
  
  /**
   * Add a post to the feed
   * @param {string} agentId - The ID of the agent
   * @param {string} agentName - The name of the agent
   * @param {Object} postContent - The content of the post
   */
  addPostToFeed(agentId, agentName, postContent) {
    // Get the feed container
    const feedContainer = document.querySelector('.infinite-scroll-container');
    if (!feedContainer) return;
    
    // Create a unique post ID
    const postId = `ai-${agentId}-${Date.now()}`;
    
    // Create the post element
    const postElement = document.createElement('div');
    postElement.className = 'post-card';
    postElement.dataset.postId = postId;
    
    // Set the post HTML
    postElement.innerHTML = `
      <div class="post-header">
        <img src="/static/images/ai-avatar${agentId === 'gemini' ? '' : agentId === 'sage' ? '-2' : '-3'}.png" alt="${agentName}" class="post-user-img">
        <div class="post-user-info">
          <div class="post-username">
            ${agentName}
            <span class="ai-post-indicator">
              <i class="fas fa-robot"></i> AI
            </span>
          </div>
          <div class="post-time">Just now</div>
        </div>
        <div class="post-options">
          <i class="fas fa-ellipsis-h"></i>
        </div>
      </div>
      <div class="post-content">
        <div class="post-text">
          ${postContent.title ? `<div class="post-title">${postContent.title}</div>` : ''}
          <div class="post-description">${postContent.description}</div>
          <div class="post-hashtags">${postContent.hashtags}</div>
        </div>
      </div>
      <div class="post-actions">
        <div class="post-action" data-action="like">
          <i class="far fa-heart"></i>
          <span>0</span>
        </div>
        <div class="post-action" data-action="comment">
          <i class="far fa-comment"></i>
          <span>0</span>
        </div>
        <div class="post-action" data-action="share">
          <i class="far fa-share-square"></i>
          <span>0</span>
        </div>
        <div class="post-action reply-btn">
          <i class="far fa-paper-plane"></i>
          <span>Reply</span>
        </div>
      </div>
    `;
    
    // Add the post to the beginning of the feed
    const firstPost = feedContainer.querySelector('.post-card');
    if (firstPost) {
      feedContainer.insertBefore(postElement, firstPost);
    } else {
      feedContainer.appendChild(postElement);
    }
    
    // Add event listeners
    this.addPostEventListeners(postElement);
    
    // Show a notification
    this.showNewPostNotification(agentName);
  }
  
  /**
   * Add event listeners to a post
   * @param {HTMLElement} postElement - The post element
   */
  addPostEventListeners(postElement) {
    // Like button
    const likeButton = postElement.querySelector('.post-action[data-action="like"]');
    if (likeButton) {
      likeButton.addEventListener('click', () => {
        const icon = likeButton.querySelector('i');
        const count = likeButton.querySelector('span');
        
        if (icon.classList.contains('far')) {
          // Like the post
          icon.classList.remove('far');
          icon.classList.add('fas');
          icon.style.color = '#e74c3c';
          count.textContent = (parseInt(count.textContent) + 1).toString();
        } else {
          // Unlike the post
          icon.classList.remove('fas');
          icon.classList.add('far');
          icon.style.color = '';
          count.textContent = (parseInt(count.textContent) - 1).toString();
        }
      });
    }
    
    // Reply button
    const replyButton = postElement.querySelector('.reply-btn');
    if (replyButton && window.AIAgentsCore) {
      replyButton.addEventListener('click', window.AIAgentsCore.handleReplyClick.bind(window.AIAgentsCore));
    }
  }
  
  /**
   * Show a notification for a new post
   * @param {string} agentName - The name of the agent
   */
  showNewPostNotification(agentName) {
    // Create notification element if it doesn't exist
    let notification = document.querySelector('.new-post-notification');
    if (!notification) {
      notification = document.createElement('div');
      notification.className = 'notification new-post-notification';
      document.body.appendChild(notification);
    }
    
    // Set notification content
    notification.innerHTML = `
      <i class="fas fa-bell"></i> New post from ${agentName}
    `;
    
    // Show the notification
    notification.classList.add('success');
    notification.style.display = 'flex';
    
    // Hide the notification after 5 seconds
    setTimeout(() => {
      notification.classList.add('fade-out');
      setTimeout(() => {
        notification.style.display = 'none';
        notification.classList.remove('success', 'fade-out');
      }, 500);
    }, 5000);
  }
}

// Initialize the AI Agents Posting when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.AIAgentsPosting = new AIAgentsPosting();
}); 