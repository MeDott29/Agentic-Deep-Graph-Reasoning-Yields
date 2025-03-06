/**
 * AI Agents Chat - Handles direct messaging with AI agents
 */
class AIAgentsChat {
  constructor() {
    this.activeChats = {};
    this.currentChatId = null;
    this.apiEndpoint = '/api/v1';
    
    // Chat container element
    this.chatContainer = null;
    
    // Initialize the module
    this.init();
  }
  
  /**
   * Initialize the AI agents chat module
   */
  init() {
    // Create the chat container if it doesn't exist
    this.createChatContainer();
    
    console.log('AI Agents Chat initialized');
  }
  
  /**
   * Create the chat container element
   */
  createChatContainer() {
    // Check if the container already exists
    if (document.getElementById('ai-chat-container')) {
      this.chatContainer = document.getElementById('ai-chat-container');
      return;
    }
    
    // Create the container
    this.chatContainer = document.createElement('div');
    this.chatContainer.id = 'ai-chat-container';
    this.chatContainer.className = 'ai-chat-container';
    
    // Add the container to the body
    document.body.appendChild(this.chatContainer);
  }
  
  /**
   * Open a chat with an AI agent
   * @param {string} agentId - The ID of the agent to chat with
   * @param {Object} agentInfo - Information about the agent
   */
  openChat(agentId, agentInfo) {
    // Check if the chat is already open
    if (this.activeChats[agentId]) {
      // Just focus the existing chat
      this.focusChat(agentId);
      return;
    }
    
    // Create a new chat window
    const chatWindow = document.createElement('div');
    chatWindow.className = 'ai-chat-window';
    chatWindow.dataset.agentId = agentId;
    chatWindow.innerHTML = `
      <div class="ai-chat-header">
        <div class="ai-chat-agent-info">
          <img src="${agentInfo.avatar}" alt="${agentInfo.name}" class="ai-chat-agent-img">
          <div class="ai-chat-agent-name">
            ${agentInfo.name}
            <span class="agent-status ${agentInfo.status}"></span>
          </div>
        </div>
        <div class="ai-chat-actions">
          <button class="ai-chat-minimize"><i class="fas fa-minus"></i></button>
          <button class="ai-chat-close"><i class="fas fa-times"></i></button>
        </div>
      </div>
      <div class="ai-chat-messages">
        <div class="ai-chat-welcome">
          <div class="ai-chat-message ai-message">
            <div class="ai-chat-message-content">
              <p>Hello! I'm ${agentInfo.name}, an AI agent specialized in knowledge graphs and data science. How can I assist you today?</p>
            </div>
            <div class="ai-chat-message-time">Just now</div>
          </div>
        </div>
      </div>
      <div class="ai-chat-input-container">
        <input type="text" class="ai-chat-input" placeholder="Type a message...">
        <button class="ai-chat-send"><i class="fas fa-paper-plane"></i></button>
      </div>
    `;
    
    // Add the chat window to the container
    this.chatContainer.appendChild(chatWindow);
    
    // Store the chat in active chats
    this.activeChats[agentId] = {
      window: chatWindow,
      agent: agentInfo,
      messages: []
    };
    
    // Set as current chat
    this.currentChatId = agentId;
    
    // Add event listeners
    this.addChatEventListeners(chatWindow, agentId);
    
    // Focus the input
    chatWindow.querySelector('.ai-chat-input').focus();
  }
  
  /**
   * Add event listeners to a chat window
   * @param {HTMLElement} chatWindow - The chat window element
   * @param {string} agentId - The ID of the agent
   */
  addChatEventListeners(chatWindow, agentId) {
    // Close button
    chatWindow.querySelector('.ai-chat-close').addEventListener('click', () => {
      this.closeChat(agentId);
    });
    
    // Minimize button
    chatWindow.querySelector('.ai-chat-minimize').addEventListener('click', () => {
      this.minimizeChat(agentId);
    });
    
    // Send button
    chatWindow.querySelector('.ai-chat-send').addEventListener('click', () => {
      this.sendMessage(agentId);
    });
    
    // Input keypress (Enter)
    chatWindow.querySelector('.ai-chat-input').addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.sendMessage(agentId);
      }
    });
    
    // Focus the chat when clicked
    chatWindow.addEventListener('click', () => {
      this.focusChat(agentId);
    });
  }
  
  /**
   * Focus a chat window
   * @param {string} agentId - The ID of the agent
   */
  focusChat(agentId) {
    if (!this.activeChats[agentId]) return;
    
    // Remove focus from all chats
    Object.values(this.activeChats).forEach(chat => {
      chat.window.classList.remove('active');
    });
    
    // Add focus to this chat
    this.activeChats[agentId].window.classList.add('active');
    
    // Set as current chat
    this.currentChatId = agentId;
    
    // Focus the input
    this.activeChats[agentId].window.querySelector('.ai-chat-input').focus();
  }
  
  /**
   * Minimize a chat window
   * @param {string} agentId - The ID of the agent
   */
  minimizeChat(agentId) {
    if (!this.activeChats[agentId]) return;
    
    // Toggle the minimized class
    this.activeChats[agentId].window.classList.toggle('minimized');
  }
  
  /**
   * Close a chat window
   * @param {string} agentId - The ID of the agent
   */
  closeChat(agentId) {
    if (!this.activeChats[agentId]) return;
    
    // Remove the window from the DOM
    this.activeChats[agentId].window.remove();
    
    // Remove from active chats
    delete this.activeChats[agentId];
    
    // Update current chat
    if (this.currentChatId === agentId) {
      this.currentChatId = Object.keys(this.activeChats)[0] || null;
      
      // Focus the new current chat if there is one
      if (this.currentChatId) {
        this.focusChat(this.currentChatId);
      }
    }
  }
  
  /**
   * Send a message in a chat
   * @param {string} agentId - The ID of the agent
   */
  async sendMessage(agentId) {
    if (!this.activeChats[agentId]) return;
    
    const chatWindow = this.activeChats[agentId].window;
    const inputElement = chatWindow.querySelector('.ai-chat-input');
    const messageContent = inputElement.value.trim();
    
    // Don't send empty messages
    if (!messageContent) return;
    
    // Clear the input
    inputElement.value = '';
    
    // Add the message to the chat
    this.addUserMessage(agentId, messageContent);
    
    // Generate a response
    await this.generateAgentResponse(agentId, messageContent);
  }
  
  /**
   * Add a user message to a chat
   * @param {string} agentId - The ID of the agent
   * @param {string} content - The message content
   */
  addUserMessage(agentId, content) {
    if (!this.activeChats[agentId]) return;
    
    const chatWindow = this.activeChats[agentId].window;
    const messagesContainer = chatWindow.querySelector('.ai-chat-messages');
    
    // Create the message element
    const messageElement = document.createElement('div');
    messageElement.className = 'ai-chat-message user-message';
    messageElement.innerHTML = `
      <div class="ai-chat-message-content">
        <p>${content}</p>
      </div>
      <div class="ai-chat-message-time">Just now</div>
    `;
    
    // Add the message to the container
    messagesContainer.appendChild(messageElement);
    
    // Store the message
    this.activeChats[agentId].messages.push({
      sender: 'user',
      content: content,
      timestamp: new Date()
    });
    
    // Scroll to the bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  /**
   * Generate a response from an AI agent
   * @param {string} agentId - The ID of the agent
   * @param {string} userMessage - The user's message
   */
  async generateAgentResponse(agentId, userMessage) {
    if (!this.activeChats[agentId]) return;
    
    const chatWindow = this.activeChats[agentId].window;
    const messagesContainer = chatWindow.querySelector('.ai-chat-messages');
    
    // Create a typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'ai-chat-typing-indicator';
    typingIndicator.innerHTML = `
      <div class="ai-chat-message ai-message">
        <div class="ai-chat-message-content">
          <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </div>
    `;
    
    // Add the typing indicator to the container
    messagesContainer.appendChild(typingIndicator);
    
    // Scroll to the bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    try {
      // In a real implementation, this would call the backend API
      // For now, we'll simulate a response after a delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Remove the typing indicator
      typingIndicator.remove();
      
      // Generate a response based on the agent and user message
      let responseContent = '';
      
      // Simple response generation based on keywords in the user message
      if (userMessage.toLowerCase().includes('knowledge graph')) {
        responseContent = `Knowledge graphs are powerful tools for representing connected data. They allow us to model relationships between entities in a way that's both machine-readable and intuitive for humans to understand.`;
      } else if (userMessage.toLowerCase().includes('graph database')) {
        responseContent = `Graph databases like Neo4j, ArangoDB, or Amazon Neptune are excellent for storing and querying highly connected data. They excel at relationship-heavy queries that would be complex in traditional relational databases.`;
      } else if (userMessage.toLowerCase().includes('machine learning') || userMessage.toLowerCase().includes('ml')) {
        responseContent = `Machine learning and knowledge graphs can work together beautifully. Graph-based features can enhance ML models, while ML can help build and refine knowledge graphs automatically.`;
      } else if (userMessage.toLowerCase().includes('hello') || userMessage.toLowerCase().includes('hi')) {
        responseContent = `Hello! How can I help you with knowledge graphs or data science today?`;
      } else {
        responseContent = `That's an interesting point. In the context of knowledge graphs, we might approach this by thinking about the relationships between entities and how they form a network of information. Would you like me to elaborate on any specific aspect?`;
      }
      
      // Add the agent's response
      this.addAgentMessage(agentId, responseContent);
      
    } catch (error) {
      console.error('Error generating agent response:', error);
      
      // Remove the typing indicator
      typingIndicator.remove();
      
      // Add an error message
      this.addSystemMessage(agentId, 'Sorry, I encountered an error while generating a response. Please try again.');
    }
  }
  
  /**
   * Add an agent message to a chat
   * @param {string} agentId - The ID of the agent
   * @param {string} content - The message content
   */
  addAgentMessage(agentId, content) {
    if (!this.activeChats[agentId]) return;
    
    const chatWindow = this.activeChats[agentId].window;
    const messagesContainer = chatWindow.querySelector('.ai-chat-messages');
    
    // Create the message element
    const messageElement = document.createElement('div');
    messageElement.className = 'ai-chat-message ai-message';
    messageElement.innerHTML = `
      <div class="ai-chat-message-content">
        <p>${content}</p>
      </div>
      <div class="ai-chat-message-time">Just now</div>
    `;
    
    // Add the message to the container
    messagesContainer.appendChild(messageElement);
    
    // Store the message
    this.activeChats[agentId].messages.push({
      sender: 'agent',
      content: content,
      timestamp: new Date()
    });
    
    // Scroll to the bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
  
  /**
   * Add a system message to a chat
   * @param {string} agentId - The ID of the agent
   * @param {string} content - The message content
   */
  addSystemMessage(agentId, content) {
    if (!this.activeChats[agentId]) return;
    
    const chatWindow = this.activeChats[agentId].window;
    const messagesContainer = chatWindow.querySelector('.ai-chat-messages');
    
    // Create the message element
    const messageElement = document.createElement('div');
    messageElement.className = 'ai-chat-message system-message';
    messageElement.innerHTML = `
      <div class="ai-chat-message-content">
        <p>${content}</p>
      </div>
    `;
    
    // Add the message to the container
    messagesContainer.appendChild(messageElement);
    
    // Store the message
    this.activeChats[agentId].messages.push({
      sender: 'system',
      content: content,
      timestamp: new Date()
    });
    
    // Scroll to the bottom
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
  }
}

// Initialize the AI Agents Chat when the DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  window.AIAgentsChat = new AIAgentsChat();
}); 