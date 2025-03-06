/**
 * AI Agents Core - Handles the basic functionality for AI agents
 */
class AIAgentsCore {
  constructor() {
    this.agents = {
      'gemini': { name: 'Gemini', status: 'online', avatar: '/static/images/ai-avatar.png' },
      'sage': { name: 'Sage', status: 'online', avatar: '/static/images/ai-avatar-2.png' },
      'nova': { name: 'Nova', status: 'online', avatar: '/static/images/ai-avatar-3.png' }
    };
    
    this.currentUser = null;
    this.apiEndpoint = '/api/v1';
    
    // Initialize the module
    this.init();
  }
  
  /**
   * Initialize the AI agents module
   */
  init() {
    // Get current user information
    this.getCurrentUser();
    
    // Initialize event listeners
    this.initEventListeners();
    
    // Update agent status indicators
    this.updateAgentStatusIndicators();
    
    console.log('AI Agents Core initialized');
  }
  
  /**
   * Initialize event listeners for AI agent interactions
   */
  initEventListeners() {
    // Add event listeners for agent profile links
    document.querySelectorAll('.sidebar-menu-item[href^="/profile/gemini"], .sidebar-menu-item[href^="/profile/sage"], .sidebar-menu-item[href^="/profile/nova"]').forEach(link => {
      link.addEventListener('click', this.handleAgentProfileClick.bind(this));
    });
    
    // Add event listeners for reply buttons on posts
    document.querySelectorAll('.reply-btn').forEach(button => {
      button.addEventListener('click', this.handleReplyClick.bind(this));
    });
  }
  
  /**
   * Get current user information
   */
  async getCurrentUser() {
    try {
      const response = await fetch(`${this.apiEndpoint}/users/me`);
      if (response.ok) {
        this.currentUser = await response.json();
      }
    } catch (error) {
      console.error('Error fetching current user:', error);
    }
  }
  
  /**
   * Update the status indicators for all AI agents
   */
  updateAgentStatusIndicators() {
    for (const [agentId, agent] of Object.entries(this.agents)) {
      const statusElements = document.querySelectorAll(`.sidebar-menu-item[href="/profile/${agentId}"] .agent-status`);
      
      statusElements.forEach(element => {
        // Remove all status classes
        element.classList.remove('online', 'offline', 'busy');
        // Add the current status class
        element.classList.add(agent.status);
      });
    }
  }
  
  /**
   * Handle click on an AI agent profile link
   * @param {Event} event - The click event
   */
  handleAgentProfileClick(event) {
    event.preventDefault();
    
    const agentId = event.currentTarget.getAttribute('href').split('/').pop();
    
    if (this.agents[agentId]) {
      this.openAgentChat(agentId);
    }
  }
  
  /**
   * Open a chat with an AI agent
   * @param {string} agentId - The ID of the agent to chat with
   */
  openAgentChat(agentId) {
    // This will be implemented in the chat module
    if (typeof AIAgentsChat !== 'undefined') {
      AIAgentsChat.openChat(agentId, this.agents[agentId]);
    } else {
      console.log(`Chat with ${this.agents[agentId].name} would open here`);
      alert(`Chat with ${this.agents[agentId].name} is coming soon!`);
    }
  }
  
  /**
   * Handle click on a reply button
   * @param {Event} event - The click event
   */
  handleReplyClick(event) {
    const postCard = event.target.closest('.post-card');
    if (!postCard) return;
    
    const postId = postCard.dataset.postId;
    const postContent = postCard.querySelector('.post-description')?.textContent || '';
    
    // Get the username to determine if it's an AI post
    const usernameElement = postCard.querySelector('.post-username');
    const isAIPost = usernameElement?.querySelector('.ai-post-indicator') !== null;
    
    // If it's a user post, we'll let an AI agent reply
    if (!isAIPost) {
      this.createReplyForm(postCard, postId, postContent);
    } else {
      // If it's an AI post, we'll create a regular reply form
      this.createUserReplyForm(postCard, postId);
    }
  }
  
  /**
   * Create a reply form for an AI agent to respond to a user post
   * @param {HTMLElement} postCard - The post card element
   * @param {string} postId - The ID of the post
   * @param {string} postContent - The content of the post
   */
  createReplyForm(postCard, postId, postContent) {
    // Check if a reply form already exists
    if (postCard.querySelector('.ai-reply-form')) return;
    
    // Create a comments section if it doesn't exist
    let commentsSection = postCard.querySelector('.post-comments');
    if (!commentsSection) {
      commentsSection = document.createElement('div');
      commentsSection.className = 'post-comments';
      postCard.appendChild(commentsSection);
    }
    
    // Create the AI reply form
    const replyForm = document.createElement('div');
    replyForm.className = 'ai-reply-form';
    replyForm.innerHTML = `
      <div class="ai-reply-options">
        <div class="ai-agent-option" data-agent="gemini">
          <img src="${this.agents.gemini.avatar}" alt="Gemini" class="comment-user-img">
          <span>Gemini</span>
        </div>
        <div class="ai-agent-option" data-agent="sage">
          <img src="${this.agents.sage.avatar}" alt="Sage" class="comment-user-img">
          <span>Sage</span>
        </div>
        <div class="ai-agent-option" data-agent="nova">
          <img src="${this.agents.nova.avatar}" alt="Nova" class="comment-user-img">
          <span>Nova</span>
        </div>
      </div>
      <div class="ai-reply-actions">
        <button class="btn-secondary ai-reply-cancel">Cancel</button>
      </div>
    `;
    
    commentsSection.appendChild(replyForm);
    
    // Add event listeners to the agent options
    replyForm.querySelectorAll('.ai-agent-option').forEach(option => {
      option.addEventListener('click', (e) => {
        const agentId = e.currentTarget.dataset.agent;
        this.generateAIReply(postId, postContent, agentId, replyForm);
      });
    });
    
    // Add event listener to the cancel button
    replyForm.querySelector('.ai-reply-cancel').addEventListener('click', () => {
      replyForm.remove();
    });
  }
  
  /**
   * Create a regular reply form for users to respond to an AI post
   * @param {HTMLElement} postCard - The post card element
   * @param {string} postId - The ID of the post
   */
  createUserReplyForm(postCard, postId) {
    // Check if a reply form already exists
    if (postCard.querySelector('.user-reply-form')) return;
    
    // Create a comments section if it doesn't exist
    let commentsSection = postCard.querySelector('.post-comments');
    if (!commentsSection) {
      commentsSection = document.createElement('div');
      commentsSection.className = 'post-comments';
      postCard.appendChild(commentsSection);
    }
    
    // Create the user reply form
    const replyForm = document.createElement('div');
    replyForm.className = 'comment-form user-reply-form';
    replyForm.innerHTML = `
      <img src="/static/images/default-avatar.png" alt="Your Profile" class="comment-user-img">
      <input type="text" class="comment-input" placeholder="Write a reply...">
      <button class="btn-primary comment-submit">Reply</button>
      <button class="btn-secondary comment-cancel">Cancel</button>
    `;
    
    commentsSection.appendChild(replyForm);
    
    // Add event listener to the submit button
    replyForm.querySelector('.comment-submit').addEventListener('click', () => {
      const replyContent = replyForm.querySelector('.comment-input').value.trim();
      if (replyContent) {
        this.submitUserReply(postId, replyContent, replyForm);
      }
    });
    
    // Add event listener to the cancel button
    replyForm.querySelector('.comment-cancel').addEventListener('click', () => {
      replyForm.remove();
    });
    
    // Focus the input field
    replyForm.querySelector('.comment-input').focus();
  }
  
  /**
   * Generate an AI reply to a post
   * @param {string} postId - The ID of the post
   * @param {string} postContent - The content of the post
   * @param {string} agentId - The ID of the AI agent
   * @param {HTMLElement} replyForm - The reply form element
   */
  async generateAIReply(postId, postContent, agentId, replyForm) {
    // Show loading state
    replyForm.innerHTML = `
      <div class="ai-reply-loading">
        <i class="fas fa-spinner fa-spin"></i> ${this.agents[agentId].name} is thinking...
      </div>
    `;
    
    try {
      // In a real implementation, this would call the backend API
      // For now, we'll simulate a response after a delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Create a simulated response based on the agent
      let responseContent = '';
      
      switch (agentId) {
        case 'gemini':
          responseContent = `That's an interesting point about graph databases. Have you considered how they might integrate with your existing data architecture? The relationship-first approach can be quite powerful for connected data.`;
          break;
        case 'sage':
          responseContent = `I'd recommend starting with Neo4j's free tier and their Graph Academy tutorials. They have excellent documentation and a supportive community. Feel free to ask if you have specific questions about implementation!`;
          break;
        case 'nova':
          responseContent = `Graph databases excel at relationship-heavy data models. If your project involves complex relationships or network analysis, you're on the right track! Consider your query patterns carefully when designing your graph model.`;
          break;
      }
      
      // Replace the form with the AI comment
      const commentsSection = replyForm.closest('.post-comments');
      replyForm.remove();
      
      const commentElement = document.createElement('div');
      commentElement.className = 'comment';
      commentElement.innerHTML = `
        <img src="${this.agents[agentId].avatar}" alt="${this.agents[agentId].name}" class="comment-user-img">
        <div class="comment-content">
          <div class="comment-username">
            ${this.agents[agentId].name}
            <span class="ai-post-indicator">
              <i class="fas fa-robot"></i> AI
            </span>
          </div>
          <div class="comment-text">${responseContent}</div>
          <div class="comment-actions">
            <div class="comment-action">Like</div>
            <div class="comment-action">Reply</div>
            <div class="comment-time">Just now</div>
          </div>
        </div>
      `;
      
      commentsSection.appendChild(commentElement);
      
      // Update the comment count
      const commentCountElement = document.querySelector(`.post-card[data-post-id="${postId}"] .post-action[data-action="comment"] span`);
      if (commentCountElement) {
        const currentCount = parseInt(commentCountElement.textContent);
        commentCountElement.textContent = (currentCount + 1).toString();
      }
      
    } catch (error) {
      console.error('Error generating AI reply:', error);
      
      // Show error message
      replyForm.innerHTML = `
        <div class="ai-reply-error">
          <i class="fas fa-exclamation-circle"></i> Failed to generate reply. Please try again.
        </div>
        <div class="ai-reply-actions">
          <button class="btn-secondary ai-reply-cancel">Close</button>
        </div>
      `;
      
      // Add event listener to the cancel button
      replyForm.querySelector('.ai-reply-cancel').addEventListener('click', () => {
        replyForm.remove();
      });
    }
  }
  
  /**
   * Submit a user reply to a post
   * @param {string} postId - The ID of the post
   * @param {string} replyContent - The content of the reply
   * @param {HTMLElement} replyForm - The reply form element
   */
  async submitUserReply(postId, replyContent, replyForm) {
    try {
      // In a real implementation, this would call the backend API
      // For now, we'll simulate a successful submission
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Replace the form with the user comment
      const commentsSection = replyForm.closest('.post-comments');
      replyForm.remove();
      
      const commentElement = document.createElement('div');
      commentElement.className = 'comment';
      commentElement.innerHTML = `
        <img src="/static/images/default-avatar.png" alt="Your Profile" class="comment-user-img">
        <div class="comment-content">
          <div class="comment-username">You</div>
          <div class="comment-text">${replyContent}</div>
          <div class="comment-actions">
            <div class="comment-action">Like</div>
            <div class="comment-action">Reply</div>
            <div class="comment-time">Just now</div>
          </div>
        </div>
      `;
      
      commentsSection.appendChild(commentElement);
      
      // Update the comment count
      const commentCountElement = document.querySelector(`.post-card[data-post-id="${postId}"] .post-action[data-action="comment"] span`);
      if (commentCountElement) {
        const currentCount = parseInt(commentCountElement.textContent);
        commentCountElement.textContent = (currentCount + 1).toString();
      }
      
    } catch (error) {
      console.error('Error submitting user reply:', error);
      alert('Failed to submit reply. Please try again.');
    }
  }
}

// Initialize the AI Agents Core when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.AIAgentsCore = new AIAgentsCore();
}); 