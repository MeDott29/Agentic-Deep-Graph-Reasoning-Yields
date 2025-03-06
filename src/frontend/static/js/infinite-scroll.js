/**
 * Knowledge Graph Social Network - Infinite Scrolling
 * 
 * This script handles the infinite scrolling functionality for the feed.
 */

class InfiniteScroll {
  constructor(options) {
    // Default options
    this.options = {
      container: '.infinite-scroll-container',
      loadingIndicator: '.loading-indicator',
      itemsSelector: '.post-card',
      nextPageUrl: '/api/recommendations/feed',
      threshold: 200,
      limit: 10,
      offset: 0,
      useLoadMoreButton: true,
      ...options
    };
    
    // Initialize properties
    this.container = document.querySelector(this.options.container);
    this.loadingIndicator = document.querySelector(this.options.loadingIndicator);
    this.isLoading = false;
    this.hasMoreItems = true;
    this.offset = this.options.offset;
    
    // Bind methods
    this.handleScroll = this.handleScroll.bind(this);
    this.loadMoreItems = this.loadMoreItems.bind(this);
    this.renderItems = this.renderItems.bind(this);
    this.handleLoadMoreClick = this.handleLoadMoreClick.bind(this);
    
    // Initialize
    this.init();
  }
  
  init() {
    // Add scroll event listener if not using load more button
    if (!this.options.useLoadMoreButton) {
      window.addEventListener('scroll', this.handleScroll);
    }
    
    // Create load more button if needed
    if (this.options.useLoadMoreButton) {
      this.createLoadMoreButton();
    }
    
    // Initial load
    this.loadMoreItems();
  }
  
  createLoadMoreButton() {
    // Create button element
    this.loadMoreButton = document.createElement('button');
    this.loadMoreButton.className = 'btn-primary load-more-btn';
    this.loadMoreButton.textContent = 'Load More';
    this.loadMoreButton.addEventListener('click', this.handleLoadMoreClick);
    
    // Insert before loading indicator
    this.container.insertBefore(this.loadMoreButton, this.loadingIndicator);
    
    // Hide loading indicator initially
    this.loadingIndicator.style.display = 'none';
  }
  
  handleLoadMoreClick() {
    if (!this.isLoading && this.hasMoreItems) {
      this.loadMoreItems();
    }
  }
  
  handleScroll() {
    // If already loading or no more items, return
    if (this.isLoading || !this.hasMoreItems) return;
    
    // Calculate distance from bottom
    const scrollTop = window.scrollY || document.documentElement.scrollTop;
    const windowHeight = window.innerHeight;
    const documentHeight = document.documentElement.scrollHeight;
    const distanceFromBottom = documentHeight - (scrollTop + windowHeight);
    
    // If close to bottom, load more items
    if (distanceFromBottom < this.options.threshold) {
      this.loadMoreItems();
    }
  }
  
  async loadMoreItems() {
    try {
      // Set loading state
      this.isLoading = true;
      
      // Update UI based on loading method
      if (this.options.useLoadMoreButton && this.loadMoreButton) {
        this.loadMoreButton.disabled = true;
        this.loadMoreButton.textContent = 'Loading...';
        this.loadMoreButton.style.display = 'block';
      } else {
        this.loadingIndicator.style.display = 'block';
      }
      
      // Build URL with parameters
      const url = new URL(this.options.nextPageUrl, window.location.origin);
      url.searchParams.append('limit', this.options.limit);
      url.searchParams.append('offset', this.offset);
      
      // Fetch data
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update offset for next page
      this.offset += data.items.length;
      
      // Check if there are more items
      this.hasMoreItems = data.items.length === this.options.limit;
      
      // Render items
      this.renderItems(data.items);
      
    } catch (error) {
      console.error('Error loading more items:', error);
    } finally {
      // Reset loading state
      this.isLoading = false;
      
      // Update UI based on loading method and whether there are more items
      if (this.options.useLoadMoreButton && this.loadMoreButton) {
        this.loadMoreButton.disabled = false;
        this.loadMoreButton.textContent = 'Load More';
        this.loadMoreButton.style.display = this.hasMoreItems ? 'block' : 'none';
      } else {
        this.loadingIndicator.style.display = this.hasMoreItems ? 'block' : 'none';
      }
    }
  }
  
  renderItems(items) {
    // If no items, mark as no more items
    if (!items || items.length === 0) {
      this.hasMoreItems = false;
      return;
    }
    
    // Create document fragment for better performance
    const fragment = document.createDocumentFragment();
    
    // Create and append items
    items.forEach(item => {
      const postElement = this.createPostElement(item);
      fragment.appendChild(postElement);
    });
    
    // Append to container
    this.container.insertBefore(fragment, this.loadingIndicator);
    
    // Initialize any components in the new items
    this.initializeComponents();
  }
  
  createPostElement(post) {
    // Create post element
    const postElement = document.createElement('div');
    postElement.className = 'post-card';
    postElement.dataset.postId = post.id;
    
    // Create post HTML
    postElement.innerHTML = `
      <div class="post-header">
        <img src="${post.user.profile_picture || '/static/images/default-avatar.png'}" alt="${post.user.username}" class="post-user-img">
        <div class="post-user-info">
          <div class="post-username">${post.user.username}</div>
          <div class="post-time">${this.formatDate(post.created_at)}</div>
        </div>
        <div class="post-options">
          <i class="fas fa-ellipsis-h"></i>
        </div>
      </div>
      <div class="post-content">
        ${post.video_url ? `
          <video class="post-video" controls>
            <source src="${post.video_url}" type="video/mp4">
            Your browser does not support the video tag.
          </video>
        ` : ''}
        <div class="post-text">
          ${post.title ? `<div class="post-title">${post.title}</div>` : ''}
          <div class="post-description">${post.description || ''}</div>
          ${post.hashtags && post.hashtags.length > 0 ? `
            <div class="post-hashtags">
              ${post.hashtags.map(tag => `#${tag}`).join(' ')}
            </div>
          ` : ''}
        </div>
      </div>
      <div class="post-actions">
        <div class="post-action" data-action="like">
          <i class="far fa-heart"></i>
          <span>${post.like_count || 0}</span>
        </div>
        <div class="post-action" data-action="comment">
          <i class="far fa-comment"></i>
          <span>${post.comment_count || 0}</span>
        </div>
        <div class="post-action" data-action="share">
          <i class="far fa-share-square"></i>
          <span>${post.share_count || 0}</span>
        </div>
      </div>
    `;
    
    return postElement;
  }
  
  formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHour / 24);
    
    if (diffSec < 60) {
      return 'just now';
    } else if (diffMin < 60) {
      return `${diffMin}m ago`;
    } else if (diffHour < 24) {
      return `${diffHour}h ago`;
    } else if (diffDay < 7) {
      return `${diffDay}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  }
  
  initializeComponents() {
    // Initialize like buttons
    const likeButtons = document.querySelectorAll('.post-action[data-action="like"]');
    likeButtons.forEach(button => {
      if (!button.hasListener) {
        button.addEventListener('click', this.handleLike.bind(this));
        button.hasListener = true;
      }
    });
    
    // Initialize comment buttons
    const commentButtons = document.querySelectorAll('.post-action[data-action="comment"]');
    commentButtons.forEach(button => {
      if (!button.hasListener) {
        button.addEventListener('click', this.handleComment.bind(this));
        button.hasListener = true;
      }
    });
    
    // Initialize share buttons
    const shareButtons = document.querySelectorAll('.post-action[data-action="share"]');
    shareButtons.forEach(button => {
      if (!button.hasListener) {
        button.addEventListener('click', this.handleShare.bind(this));
        button.hasListener = true;
      }
    });
    
    // Initialize videos (lazy loading)
    const videos = document.querySelectorAll('.post-video');
    videos.forEach(video => {
      if (!video.hasListener) {
        video.addEventListener('play', this.handleVideoPlay.bind(this));
        video.hasListener = true;
      }
    });
  }
  
  async handleLike(event) {
    const button = event.currentTarget;
    const postCard = button.closest('.post-card');
    const postId = postCard.dataset.postId;
    
    try {
      const response = await fetch(`/api/content/${postId}/like`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update UI
      const countElement = button.querySelector('span');
      countElement.textContent = data.like_count;
      
      // Toggle liked class
      button.classList.toggle('liked');
      const icon = button.querySelector('i');
      if (button.classList.contains('liked')) {
        icon.classList.replace('far', 'fas');
      } else {
        icon.classList.replace('fas', 'far');
      }
      
    } catch (error) {
      console.error('Error liking post:', error);
    }
  }
  
  handleComment(event) {
    const button = event.currentTarget;
    const postCard = button.closest('.post-card');
    const postId = postCard.dataset.postId;
    
    // Redirect to post detail page with comment section focused
    window.location.href = `/post/${postId}#comments`;
  }
  
  async handleShare(event) {
    const button = event.currentTarget;
    const postCard = button.closest('.post-card');
    const postId = postCard.dataset.postId;
    
    try {
      // For now, just copy the URL to clipboard
      const postUrl = `${window.location.origin}/post/${postId}`;
      await navigator.clipboard.writeText(postUrl);
      
      // Show toast notification
      alert('Link copied to clipboard!');
      
      // Record share
      const response = await fetch(`/api/content/${postId}/share`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ platform: 'clipboard' })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      
      const data = await response.json();
      
      // Update UI
      const countElement = button.querySelector('span');
      countElement.textContent = data.share_count;
      
    } catch (error) {
      console.error('Error sharing post:', error);
    }
  }
  
  async handleVideoPlay(event) {
    const video = event.currentTarget;
    const postCard = video.closest('.post-card');
    const postId = postCard.dataset.postId;
    
    try {
      // Record view when video starts playing
      fetch(`/api/content/${postId}/view`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ duration: 0 }) // Initial view
      });
      
      // Pause other videos
      const allVideos = document.querySelectorAll('.post-video');
      allVideos.forEach(v => {
        if (v !== video && !v.paused) {
          v.pause();
        }
      });
      
    } catch (error) {
      console.error('Error recording view:', error);
    }
  }
  
  destroy() {
    // Remove event listeners
    window.removeEventListener('scroll', this.handleScroll);
    
    // Remove load more button if it exists
    if (this.loadMoreButton) {
      this.loadMoreButton.removeEventListener('click', this.handleLoadMoreClick);
    }
  }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  // Initialize for feed page
  if (document.querySelector('.feed')) {
    const feedScroll = new InfiniteScroll({
      container: '.feed',
      loadingIndicator: '.loading-indicator',
      nextPageUrl: '/api/recommendations/feed'
    });
  }
  
  // Initialize for explore page
  if (document.querySelector('.explore')) {
    const exploreScroll = new InfiniteScroll({
      container: '.explore',
      loadingIndicator: '.loading-indicator',
      nextPageUrl: '/api/social/explore'
    });
  }
  
  // Initialize for profile page
  if (document.querySelector('.profile-content')) {
    const userId = document.querySelector('.profile').dataset.userId;
    const profileScroll = new InfiniteScroll({
      container: '.profile-content',
      loadingIndicator: '.loading-indicator',
      nextPageUrl: `/api/content/user/${userId}`
    });
  }
}); 