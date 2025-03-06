
// Track view time
let viewStartTime = Date.now();
let currentContentId = null;
let currentAgentId = null;
let isPaused = false;
let pauseStartTime = null;
let totalPauseTime = 0;

// Start tracking view time
function startViewTracking(contentId, agentId) {
    // If already tracking, stop tracking the previous content
    if (currentContentId) {
        stopViewTracking();
    }
    
    currentContentId = contentId;
    currentAgentId = agentId;
    viewStartTime = Date.now();
    isPaused = false;
    totalPauseTime = 0;
    
    // Send start viewing request
    fetch(`/api/engagement/start_viewing/${contentId}`, {
        method: 'POST'
    });
}

// Stop tracking view time
function stopViewTracking() {
    if (!currentContentId) return;
    
    // If paused, resume first
    if (isPaused) {
        resumeViewTracking();
    }
    
    // Calculate view time
    const viewTime = calculateViewTime();
    
    // Send stop viewing request
    fetch(`/api/engagement/stop_viewing`, {
        method: 'POST'
    });
    
    // Reset tracking
    currentContentId = null;
    currentAgentId = null;
}

// Pause tracking when tab is not visible
function pauseViewTracking() {
    if (!currentContentId || isPaused) return;
    
    isPaused = true;
    pauseStartTime = Date.now();
    
    // Send pause request
    fetch(`/api/engagement/pause`, {
        method: 'POST'
    });
}

// Resume tracking when tab becomes visible
function resumeViewTracking() {
    if (!currentContentId || !isPaused) return;
    
    const pauseDuration = Date.now() - pauseStartTime;
    totalPauseTime += pauseDuration;
    isPaused = false;
    
    // Send resume request
    fetch(`/api/engagement/resume`, {
        method: 'POST'
    });
}

// Calculate current view time
function calculateViewTime() {
    if (!currentContentId) return 0;
    
    const now = Date.now();
    const totalTime = now - viewStartTime;
    return Math.max(0, (totalTime - totalPauseTime) / 1000); // Convert to seconds
}

// Handle like button
function likeContent(contentId, agentId) {
    fetch(`/api/engagement/like/${contentId}/${agentId}`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            // Update UI to show liked state
            const likeButton = document.querySelector(`#like-${contentId}`);
            if (likeButton) {
                likeButton.classList.add('btn-success');
                likeButton.disabled = true;
                likeButton.textContent = 'Liked';
            }
        }
    });
}

// Handle skip button
function skipContent(contentId, agentId) {
    fetch(`/api/engagement/skip/${contentId}/${agentId}`, {
        method: 'POST'
    })
    .then(response => {
        if (response.ok) {
            // Navigate to next content
            window.location.href = '/next';
        }
    });
}

// Handle next button
function nextContent() {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to next content
    window.location.href = '/next';
}

// Handle previous button
function previousContent() {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to previous content
    window.location.href = '/previous';
}

// Handle filter by agent
function filterByAgent(agentId) {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to agent filter
    window.location.href = `/filter/agent/${agentId}`;
}

// Handle filter by topic
function filterByTopic(topic) {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to topic filter
    window.location.href = `/filter/topic/${encodeURIComponent(topic)}`;
}

// Handle clear filters
function clearFilters() {
    // Stop tracking current content
    stopViewTracking();
    
    // Navigate to home
    window.location.href = '/';
}

// Handle page visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        pauseViewTracking();
    } else {
        resumeViewTracking();
    }
});

// Handle page unload
window.addEventListener('beforeunload', () => {
    stopViewTracking();
});

// Initialize view tracking when page loads
document.addEventListener('DOMContentLoaded', () => {
    const contentCard = document.querySelector('.content-card');
    if (contentCard) {
        const contentId = contentCard.dataset.contentId;
        const agentId = contentCard.dataset.agentId;
        if (contentId && agentId) {
            startViewTracking(contentId, agentId);
        }
    }
});
    