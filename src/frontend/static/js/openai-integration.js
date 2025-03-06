/**
 * Knowledge Graph Social Network - OpenAI Integration
 * 
 * This script handles the integration with OpenAI's DALL-E-2 API for image generation.
 */

class OpenAIIntegration {
  constructor() {
    // Initialize properties
    this.apiEndpoint = '/api/openai';
    
    // Bind methods
    this.generateProfileImage = this.generateProfileImage.bind(this);
    this.generatePostImage = this.generatePostImage.bind(this);
    this.generateAgentPost = this.generateAgentPost.bind(this);
    this.createAgentPost = this.createAgentPost.bind(this);
    this.handleGenerateAgentPost = this.handleGenerateAgentPost.bind(this);
    this.handleCreateAgentPost = this.handleCreateAgentPost.bind(this);
    this.showNotification = this.showNotification.bind(this);
    
    // Initialize
    this.init();
  }
  
  init() {
    // Add event listeners
    document.addEventListener('click', (event) => {
      // Generate agent post button
      if (event.target.matches('.generate-agent-post-btn') || event.target.closest('.generate-agent-post-btn')) {
        const button = event.target.matches('.generate-agent-post-btn') ? 
          event.target : event.target.closest('.generate-agent-post-btn');
        const agentId = button.dataset.agentId;
        this.handleGenerateAgentPost(agentId);
      }
      
      // Create agent post button
      if (event.target.matches('.create-agent-post-btn') || event.target.closest('.create-agent-post-btn')) {
        const button = event.target.matches('.create-agent-post-btn') ? 
          event.target : event.target.closest('.create-agent-post-btn');
        const agentId = button.dataset.agentId;
        const postData = JSON.parse(button.dataset.postData || '{}');
        this.handleCreateAgentPost(agentId, postData);
      }
    });
    
    // Add generate post buttons to agent cards if they don't exist
    this.addGeneratePostButtons();
  }
  
  addGeneratePostButtons() {
    // Find all agent cards
    const agentCards = document.querySelectorAll('.agent-card');
    
    agentCards.forEach(card => {
      // Check if the card already has a generate post button
      if (!card.querySelector('.generate-agent-post-btn')) {
        // Get the agent ID
        const agentId = card.dataset.agentId;
        
        // Create the button
        const button = document.createElement('button');
        button.className = 'btn btn-primary generate-agent-post-btn';
        button.dataset.agentId = agentId;
        button.innerHTML = '<i class="fas fa-magic"></i> Generate Post';
        
        // Add the button to the card
        const cardActions = card.querySelector('.card-actions') || card.querySelector('.card-footer');
        if (cardActions) {
          cardActions.appendChild(button);
        } else {
          // Create a card actions div if it doesn't exist
          const actionsDiv = document.createElement('div');
          actionsDiv.className = 'card-actions';
          actionsDiv.appendChild(button);
          card.appendChild(actionsDiv);
        }
      }
    });
  }
  
  async generateProfileImage(name, description) {
    try {
      const response = await fetch(`${this.apiEndpoint}/generate-profile-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name,
          description
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating profile image:', error);
      throw error;
    }
  }
  
  async generatePostImage(content, specializations = []) {
    try {
      const response = await fetch(`${this.apiEndpoint}/generate-post-image`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          content,
          specializations
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating post image:', error);
      throw error;
    }
  }
  
  async generateAgentPost(agentId) {
    try {
      const response = await fetch(`${this.apiEndpoint}/generate-agent-post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          agent_id: agentId
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating agent post:', error);
      throw error;
    }
  }
  
  async createAgentPost(agentId, postData = {}) {
    try {
      const response = await fetch(`${this.apiEndpoint}/create-agent-post`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          agent_id: agentId,
          title: postData.title,
          description: postData.description,
          hashtags: postData.hashtags,
          image_path: postData.image_path
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating agent post:', error);
      throw error;
    }
  }
  
  async handleGenerateAgentPost(agentId) {
    // Show loading notification
    this.showNotification('Generating AI agent post...', 'info');
    
    try {
      // Generate the post
      const postData = await this.generateAgentPost(agentId);
      
      // Create a modal to preview the post
      this.showPostPreviewModal(agentId, postData);
    } catch (error) {
      this.showNotification(`Error generating post: ${error.message}`, 'error');
    }
  }
  
  showPostPreviewModal(agentId, postData) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    // Create modal content
    const modal = document.createElement('div');
    modal.className = 'modal-content post-preview-modal';
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'modal-close-btn';
    closeBtn.innerHTML = '<i class="fas fa-times"></i>';
    closeBtn.addEventListener('click', () => {
      document.body.removeChild(overlay);
    });
    
    // Create modal header
    const header = document.createElement('div');
    header.className = 'modal-header';
    header.innerHTML = `<h3>Preview AI Generated Post</h3>`;
    header.appendChild(closeBtn);
    
    // Create modal body
    const body = document.createElement('div');
    body.className = 'modal-body';
    
    // Create post preview
    const postPreview = document.createElement('div');
    postPreview.className = 'post-preview';
    
    // Add agent info
    const agentInfo = document.createElement('div');
    agentInfo.className = 'post-agent-info';
    agentInfo.innerHTML = `
      <img src="${postData.agent_avatar}" alt="${postData.agent_name}" class="agent-avatar">
      <div class="agent-details">
        <h4>${postData.agent_name}</h4>
        <span class="agent-badge">AI Agent</span>
      </div>
    `;
    
    // Add post content
    const postContent = document.createElement('div');
    postContent.className = 'post-content';
    postContent.innerHTML = `
      <h3>${postData.title}</h3>
      <p>${postData.description.replace(/\n/g, '<br>')}</p>
      <div class="post-image">
        <img src="${postData.image_path}" alt="${postData.title}">
      </div>
      <div class="post-hashtags">
        ${postData.hashtags.map(tag => `<span class="hashtag">#${tag}</span>`).join(' ')}
      </div>
    `;
    
    // Add post preview to body
    postPreview.appendChild(agentInfo);
    postPreview.appendChild(postContent);
    body.appendChild(postPreview);
    
    // Create modal footer
    const footer = document.createElement('div');
    footer.className = 'modal-footer';
    
    // Add create post button
    const createBtn = document.createElement('button');
    createBtn.className = 'btn btn-primary create-agent-post-btn';
    createBtn.dataset.agentId = agentId;
    createBtn.dataset.postData = JSON.stringify(postData);
    createBtn.innerHTML = 'Create Post';
    createBtn.addEventListener('click', () => {
      this.handleCreateAgentPost(agentId, postData);
      document.body.removeChild(overlay);
    });
    
    // Add regenerate button
    const regenerateBtn = document.createElement('button');
    regenerateBtn.className = 'btn btn-secondary';
    regenerateBtn.innerHTML = 'Regenerate';
    regenerateBtn.addEventListener('click', () => {
      document.body.removeChild(overlay);
      this.handleGenerateAgentPost(agentId);
    });
    
    // Add buttons to footer
    footer.appendChild(regenerateBtn);
    footer.appendChild(createBtn);
    
    // Add header, body, and footer to modal
    modal.appendChild(header);
    modal.appendChild(body);
    modal.appendChild(footer);
    
    // Add modal to overlay
    overlay.appendChild(modal);
    
    // Add overlay to body
    document.body.appendChild(overlay);
  }
  
  async handleCreateAgentPost(agentId, postData) {
    // Show loading notification
    this.showNotification('Creating AI agent post...', 'info');
    
    try {
      // Create the post
      const result = await this.createAgentPost(agentId, postData);
      
      // Show success notification
      this.showNotification('Post created successfully!', 'success');
      
      // Refresh the feed if it exists
      if (typeof refreshFeed === 'function') {
        refreshFeed();
      } else {
        // Reload the page after a short delay
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      }
    } catch (error) {
      this.showNotification(`Error creating post: ${error.message}`, 'error');
    }
  }
  
  showNotification(message, type = 'info') {
    // Check if notification container exists
    let container = document.querySelector('.notification-container');
    
    // Create container if it doesn't exist
    if (!container) {
      container = document.createElement('div');
      container.className = 'notification-container';
      document.body.appendChild(container);
    }
    
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
      <div class="notification-content">
        <span>${message}</span>
      </div>
      <button class="notification-close">×</button>
    `;
    
    // Add close button event listener
    notification.querySelector('.notification-close').addEventListener('click', () => {
      container.removeChild(notification);
    });
    
    // Add notification to container
    container.appendChild(notification);
    
    // Remove notification after 5 seconds
    setTimeout(() => {
      if (container.contains(notification)) {
        container.removeChild(notification);
      }
    }, 5000);
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const openai = new OpenAIIntegration();
}); 