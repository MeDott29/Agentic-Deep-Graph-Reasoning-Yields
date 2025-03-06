/**
 * Knowledge Graph Social Network - Gemini Integration
 * 
 * This script handles the integration with Google's Gemini API for content generation.
 */

class GeminiIntegration {
  constructor() {
    // Initialize properties
    this.apiEndpoint = '/api/gemini';
    
    // Bind methods
    this.generateResponse = this.generateResponse.bind(this);
    this.generatePost = this.generatePost.bind(this);
    this.generateHashtagContent = this.generateHashtagContent.bind(this);
    this.createAIContent = this.createAIContent.bind(this);
    this.loadRecommendations = this.loadRecommendations.bind(this);
    this.handleRefreshRecommendations = this.handleRefreshRecommendations.bind(this);
    this.handleVoiceInput = this.handleVoiceInput.bind(this);
    this.handleAIAssist = this.handleAIAssist.bind(this);
    
    // Initialize
    this.init();
  }
  
  init() {
    // Add event listeners to response buttons
    const responseButtons = document.querySelectorAll('.ai-response-btn');
    responseButtons.forEach(button => {
      button.addEventListener('click', this.handleResponseClick.bind(this));
    });
    
    // Add event listeners to generate post buttons
    const generateButtons = document.querySelectorAll('.ai-generate-btn');
    generateButtons.forEach(button => {
      button.addEventListener('click', this.handleGenerateClick.bind(this));
    });
    
    // Add event listener to refresh recommendations button
    const refreshButton = document.querySelector('.refresh-recommendations-btn');
    if (refreshButton) {
      refreshButton.addEventListener('click', this.handleRefreshRecommendations);
    }
    
    // Add event listener to voice input button
    const voiceInputButton = document.querySelector('.voice-input-btn');
    if (voiceInputButton) {
      voiceInputButton.addEventListener('click', this.handleVoiceInput);
    }
    
    // Add event listener to AI assist button
    const aiAssistButton = document.querySelector('.ai-assist-btn');
    if (aiAssistButton) {
      aiAssistButton.addEventListener('click', this.handleAIAssist.bind(this));
    }
    
    // Initialize dark mode
    this.initDarkMode();
    
    // Load recommendations
    this.loadRecommendations();
  }
  
  initDarkMode() {
    // Check for saved theme preference or use preferred color scheme
    const savedTheme = localStorage.getItem('theme');
    const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Apply dark mode if saved or preferred
    if (savedTheme === 'dark' || (!savedTheme && prefersDark)) {
      document.body.classList.add('dark-mode');
      this.updateThemeToggleIcon(true);
    }
    
    // Add event listener to theme toggle
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', this.toggleDarkMode.bind(this));
    }
  }
  
  toggleDarkMode() {
    // Toggle dark mode class
    const isDarkMode = document.body.classList.toggle('dark-mode');
    
    // Save preference to localStorage
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
    
    // Update icon
    this.updateThemeToggleIcon(isDarkMode);
  }
  
  updateThemeToggleIcon(isDarkMode) {
    const themeToggle = document.querySelector('.theme-toggle');
    if (!themeToggle) return;
    
    // Clear existing icons
    themeToggle.innerHTML = '';
    
    // Add appropriate icon
    const icon = document.createElement('i');
    icon.className = isDarkMode ? 'fas fa-sun' : 'fas fa-moon';
    themeToggle.appendChild(icon);
  }
  
  async generateResponse(postId, postContent) {
    try {
      const response = await fetch(`${this.apiEndpoint}/respond`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          post_id: postId,
          post_content: postContent
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating response:', error);
      throw error;
    }
  }
  
  async generatePost(userContext) {
    try {
      const response = await fetch(`${this.apiEndpoint}/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userContext)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating post:', error);
      throw error;
    }
  }
  
  async generateHashtagContent(hashtag) {
    try {
      const response = await fetch(`${this.apiEndpoint}/hashtag-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          hashtag: hashtag
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error generating hashtag content:', error);
      throw error;
    }
  }
  
  async createAIContent(postGeneration) {
    try {
      const response = await fetch(`${this.apiEndpoint}/create-content`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(postGeneration)
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating AI content:', error);
      throw error;
    }
  }
  
  async handleResponseClick(event) {
    const button = event.currentTarget;
    const postCard = button.closest('.post-card');
    const postId = postCard.dataset.postId;
    const postContent = postCard.querySelector('.post-description').textContent;
    
    try {
      // Disable button and show loading state
      button.disabled = true;
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
      
      // Generate response
      const responseData = await this.generateResponse(postId, postContent);
      
      // Create comment element
      const commentSection = postCard.querySelector('.post-comments') || this.createCommentSection(postCard);
      const commentElement = document.createElement('div');
      commentElement.className = 'comment';
      commentElement.innerHTML = `
        <img src="/static/images/ai-avatar.png" alt="AI Assistant" class="comment-user-img">
        <div class="comment-content">
          <div class="comment-username">AI Assistant</div>
          <div class="comment-text">${responseData.response_content}</div>
          <div class="comment-actions">
            <div class="comment-action">Like</div>
            <div class="comment-action">Reply</div>
            <div class="comment-time">just now</div>
          </div>
        </div>
      `;
      
      // Add comment to the beginning of the comments section
      const commentForm = commentSection.querySelector('.comment-form');
      if (commentForm) {
        commentSection.insertBefore(commentElement, commentForm);
      } else {
        commentSection.appendChild(commentElement);
      }
      
      // Update comment count
      const commentCountElement = postCard.querySelector('.post-action[data-action="comment"] span');
      if (commentCountElement) {
        const currentCount = parseInt(commentCountElement.textContent, 10) || 0;
        commentCountElement.textContent = currentCount + 1;
      }
      
    } catch (error) {
      console.error('Error handling response click:', error);
      alert('Failed to generate response. Please try again.');
    } finally {
      // Reset button state
      button.disabled = false;
      button.innerHTML = '<i class="fas fa-robot"></i> AI Response';
    }
  }
  
  createCommentSection(postCard) {
    const commentSection = document.createElement('div');
    commentSection.className = 'post-comments';
    
    // Add comment form
    commentSection.innerHTML = `
      <div class="comment-form">
        <input type="text" class="comment-input" placeholder="Add a comment...">
        <button class="btn-primary">Post</button>
      </div>
    `;
    
    postCard.appendChild(commentSection);
    return commentSection;
  }
  
  async handleGenerateClick(event) {
    const button = event.currentTarget;
    const userId = button.dataset.userId || 'current';
    const hashtag = button.dataset.hashtag;
    
    try {
      // Disable button and show loading state
      button.disabled = true;
      button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
      
      let postGeneration;
      
      if (hashtag) {
        // Generate hashtag content
        postGeneration = await this.generateHashtagContent(hashtag);
      } else {
        // Get user context
        const userContext = await this.getUserContext(userId);
        
        // Generate post
        postGeneration = await this.generatePost(userContext);
      }
      
      // Create content
      const content = await this.createAIContent({
        user_id: userId,
        post_content: postGeneration.post_content,
        hashtags: postGeneration.hashtags,
        title: postGeneration.title
      });
      
      // Refresh feed
      window.location.reload();
      
    } catch (error) {
      console.error('Error handling generate click:', error);
      alert('Failed to generate post. Please try again.');
    } finally {
      // Reset button state
      button.disabled = false;
      const buttonText = hashtag ? 
        `<i class="fas fa-magic"></i> Generate AI Post with #${hashtag}` : 
        '<i class="fas fa-magic"></i> Generate AI Post';
      button.innerHTML = buttonText;
    }
  }
  
  async getUserContext(userId) {
    // If userId is 'current', get current user's context
    if (userId === 'current') {
      return {
        user_id: userId,
        username: document.querySelector('.header-profile .username')?.textContent || 'user',
        bio: document.querySelector('.profile-bio')?.textContent || '',
        interests: [] // This would need to be populated from user preferences
      };
    }
    
    // Otherwise, fetch user context from API
    try {
      const response = await fetch(`/api/users/${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const userData = await response.json();
      
      return {
        user_id: userData.id,
        username: userData.username,
        bio: userData.bio || '',
        interests: [] // This would need to be populated from user preferences
      };
    } catch (error) {
      console.error('Error getting user context:', error);
      throw error;
    }
  }
  
  async loadRecommendations() {
    const container = document.querySelector('.recommendations-container');
    if (!container) return;
    
    const loadingElement = container.querySelector('.recommendation-loading');
    if (loadingElement) {
      loadingElement.style.display = 'block';
    }
    
    try {
      // Get current user ID
      const userId = 'current'; // This would need to be replaced with actual user ID
      
      // Fetch recommendations
      const response = await fetch(`${this.apiEndpoint}/recommend?user_id=${userId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Clear loading indicator
      if (loadingElement) {
        loadingElement.style.display = 'none';
      }
      
      // Render recommendations
      this.renderRecommendations(container, data);
      
    } catch (error) {
      console.error('Error loading recommendations:', error);
      
      // Show error message
      if (loadingElement) {
        loadingElement.innerHTML = '<i class="fas fa-exclamation-circle"></i> Failed to load recommendations.';
      }
    }
  }
  
  renderRecommendations(container, data) {
    // Clear existing recommendations
    const loadingElement = container.querySelector('.recommendation-loading');
    
    // Create recommendations elements
    const fragment = document.createDocumentFragment();
    
    // Add explanation if available
    if (data.explanation) {
      const explanationElement = document.createElement('div');
      explanationElement.className = 'recommendation-explanation';
      explanationElement.textContent = data.explanation;
      fragment.appendChild(explanationElement);
    }
    
    // Add recommendations
    data.recommendations.forEach(recommendation => {
      const element = document.createElement('div');
      element.className = 'sidebar-menu-item recommendation-item';
      
      // Create icon based on content type
      let icon = 'fas fa-file-alt'; // Default
      if (recommendation.content_type === 'video') {
        icon = 'fas fa-video';
      } else if (recommendation.content_type === 'image') {
        icon = 'fas fa-image';
      } else if (recommendation.content_type === 'post') {
        icon = 'fas fa-comment-alt';
      }
      
      element.innerHTML = `
        <i class="${icon}"></i>
        <div class="recommendation-content">
          <div class="recommendation-title">${recommendation.title}</div>
          <div class="recommendation-hashtags">
            ${recommendation.hashtags.map(tag => `#${tag}`).join(' ')}
          </div>
        </div>
        <div class="recommendation-actions">
          <button class="recommendation-preview-btn" title="Preview">
            <i class="fas fa-eye"></i>
          </button>
          <button class="recommendation-post-btn" title="Post to feed">
            <i class="fas fa-paper-plane"></i>
          </button>
        </div>
      `;
      
      // Add click event to preview content
      const previewBtn = element.querySelector('.recommendation-preview-btn');
      previewBtn.addEventListener('click', () => {
        this.previewRecommendation(recommendation);
      });
      
      // Add click event to create content
      const postBtn = element.querySelector('.recommendation-post-btn');
      postBtn.addEventListener('click', async () => {
        try {
          // Create content
          await this.createAIContent({
            user_id: data.user_id,
            post_content: recommendation.description,
            hashtags: recommendation.hashtags,
            title: recommendation.title
          });
          
          // Show success message
          this.showNotification('Post created successfully!');
          
          // Refresh feed
          setTimeout(() => {
            window.location.reload();
          }, 1500);
        } catch (error) {
          console.error('Error creating content from recommendation:', error);
          this.showNotification('Failed to create post. Please try again.', 'error');
        }
      });
      
      fragment.appendChild(element);
    });
    
    // Clear container and append new elements
    while (container.firstChild) {
      container.removeChild(container.firstChild);
    }
    
    container.appendChild(fragment);
  }
  
  previewRecommendation(recommendation) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    // Create modal content
    const modal = document.createElement('div');
    modal.className = 'modal-content';
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'modal-close-btn';
    closeBtn.innerHTML = '<i class="fas fa-times"></i>';
    closeBtn.addEventListener('click', () => {
      document.body.removeChild(overlay);
    });
    
    // Create preview content
    modal.innerHTML = `
      <div class="modal-header">
        <h3>${recommendation.title}</h3>
        <div class="modal-hashtags">${recommendation.hashtags.map(tag => `#${tag}`).join(' ')}</div>
      </div>
      <div class="modal-body">
        <p>${recommendation.description}</p>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary modal-cancel-btn">Cancel</button>
        <button class="btn-primary modal-post-btn">Post to Feed</button>
      </div>
    `;
    
    // Add close button to modal
    modal.appendChild(closeBtn);
    
    // Add modal to overlay
    overlay.appendChild(modal);
    
    // Add overlay to body
    document.body.appendChild(overlay);
    
    // Add event listener to cancel button
    const cancelBtn = modal.querySelector('.modal-cancel-btn');
    cancelBtn.addEventListener('click', () => {
      document.body.removeChild(overlay);
    });
    
    // Add event listener to post button
    const postBtn = modal.querySelector('.modal-post-btn');
    postBtn.addEventListener('click', async () => {
      try {
        // Create content
        await this.createAIContent({
          user_id: 'current', // This would need to be replaced with actual user ID
          post_content: recommendation.description,
          hashtags: recommendation.hashtags,
          title: recommendation.title
        });
        
        // Remove modal
        document.body.removeChild(overlay);
        
        // Show success message
        this.showNotification('Post created successfully!');
        
        // Refresh feed
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      } catch (error) {
        console.error('Error creating content from recommendation:', error);
        this.showNotification('Failed to create post. Please try again.', 'error');
      }
    });
  }
  
  showNotification(message, type = 'success') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    // Add to body
    document.body.appendChild(notification);
    
    // Remove after 3 seconds
    setTimeout(() => {
      notification.classList.add('fade-out');
      setTimeout(() => {
        if (document.body.contains(notification)) {
          document.body.removeChild(notification);
        }
      }, 500);
    }, 3000);
  }
  
  handleRefreshRecommendations() {
    this.loadRecommendations();
  }

  handleVoiceInput() {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      alert('Your browser does not support speech recognition. Please try a different browser.');
      return;
    }
    
    // Get the post input textarea
    const textarea = document.querySelector('.post-input');
    if (!textarea) return;
    
    // Create speech recognition object
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    // Configure recognition
    recognition.continuous = false;
    recognition.interimResults = true;
    recognition.lang = 'en-US';
    
    // Change button to indicate recording
    const button = document.querySelector('.voice-input-btn');
    const originalHTML = button.innerHTML;
    button.innerHTML = '<i class="fas fa-microphone-slash"></i><span>Recording...</span>';
    button.classList.add('recording');
    
    // Variables to store results
    let finalTranscript = '';
    
    // Handle results
    recognition.onresult = (event) => {
      let interimTranscript = '';
      
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        
        if (event.results[i].isFinal) {
          finalTranscript += transcript;
        } else {
          interimTranscript += transcript;
        }
      }
      
      // Update textarea with current transcript
      textarea.value = finalTranscript + interimTranscript;
    };
    
    // Handle end of speech recognition
    recognition.onend = () => {
      // Reset button
      button.innerHTML = originalHTML;
      button.classList.remove('recording');
      
      // If no text was recognized, show a message
      if (!finalTranscript && !textarea.value) {
        alert('No speech was detected. Please try again.');
      }
    };
    
    // Handle errors
    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      
      // Reset button
      button.innerHTML = originalHTML;
      button.classList.remove('recording');
      
      // Show error message
      if (event.error === 'no-speech') {
        alert('No speech was detected. Please try again.');
      } else {
        alert(`Error occurred in recognition: ${event.error}`);
      }
    };
    
    // Start recognition
    recognition.start();
  }

  async handleAIAssist() {
    // Get the post input textarea
    const textarea = document.querySelector('.post-input');
    if (!textarea || !textarea.value.trim()) {
      this.showNotification('Please enter some text first.', 'error');
      return;
    }
    
    // Get the current text
    const currentText = textarea.value.trim();
    
    // Create modal for AI assist options
    const overlay = document.createElement('div');
    overlay.className = 'modal-overlay';
    
    // Create modal content
    const modal = document.createElement('div');
    modal.className = 'modal-content ai-assist-modal';
    
    // Add close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'modal-close-btn';
    closeBtn.innerHTML = '<i class="fas fa-times"></i>';
    closeBtn.addEventListener('click', () => {
      document.body.removeChild(overlay);
    });
    
    // Create modal content
    modal.innerHTML = `
      <div class="modal-header">
        <h3>AI Writing Assistant</h3>
      </div>
      <div class="modal-body">
        <div class="ai-assist-options">
          <button class="ai-assist-option" data-action="improve">
            <i class="fas fa-star"></i>
            <span>Improve Writing</span>
          </button>
          <button class="ai-assist-option" data-action="expand">
            <i class="fas fa-expand-alt"></i>
            <span>Expand Content</span>
          </button>
          <button class="ai-assist-option" data-action="shorten">
            <i class="fas fa-compress-alt"></i>
            <span>Make Concise</span>
          </button>
          <button class="ai-assist-option" data-action="hashtags">
            <i class="fas fa-hashtag"></i>
            <span>Suggest Hashtags</span>
          </button>
          <button class="ai-assist-option" data-action="title">
            <i class="fas fa-heading"></i>
            <span>Generate Title</span>
          </button>
        </div>
        <div class="ai-assist-preview">
          <div class="ai-assist-loading" style="display: none;">
            <i class="fas fa-spinner fa-spin"></i> Processing...
          </div>
          <div class="ai-assist-result" style="display: none;">
            <h4>Result:</h4>
            <div class="ai-assist-result-content"></div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn-secondary modal-cancel-btn">Cancel</button>
        <button class="btn-primary modal-apply-btn" disabled>Apply Changes</button>
      </div>
    `;
    
    // Add close button to modal
    modal.appendChild(closeBtn);
    
    // Add modal to overlay
    overlay.appendChild(modal);
    
    // Add overlay to body
    document.body.appendChild(overlay);
    
    // Add event listeners to option buttons
    const optionButtons = modal.querySelectorAll('.ai-assist-option');
    optionButtons.forEach(button => {
      button.addEventListener('click', async () => {
        // Get the action
        const action = button.dataset.action;
        
        // Show loading
        const loadingElement = modal.querySelector('.ai-assist-loading');
        const resultElement = modal.querySelector('.ai-assist-result');
        const resultContentElement = modal.querySelector('.ai-assist-result-content');
        
        loadingElement.style.display = 'flex';
        resultElement.style.display = 'none';
        
        try {
          // Process the text with AI
          const result = await this.processTextWithAI(currentText, action);
          
          // Hide loading and show result
          loadingElement.style.display = 'none';
          resultElement.style.display = 'block';
          
          // Display the result
          resultContentElement.textContent = result;
          
          // Enable apply button
          const applyButton = modal.querySelector('.modal-apply-btn');
          applyButton.disabled = false;
          
// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const gemini = new GeminiIntegration();
}); 