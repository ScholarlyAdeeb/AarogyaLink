// ===== ENHANCED FEATURES - MAIN CONTROLLER =====

// Enhanced features coordination and main functionality
console.log('🎨 Loading enhanced features...');

// Floating Button Control
function controlFloatingButton() {
    const floatingBtn = document.getElementById('floatingCTA');
    const chatSection = document.getElementById('chat');
    
    if (!floatingBtn || !chatSection) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                floatingBtn.classList.add('hidden');
            } else {
                floatingBtn.classList.remove('hidden');
            }
        });
    }, { threshold: 0.1 });
    
    observer.observe(chatSection);
}

// Enhanced message function with avatar support
function addMessageEnhanced(content, isUser = false, isLoading = false) {
    const chatContainer = document.getElementById('chatContainer');
    if (!chatContainer) return null;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user' : 'ai'}${isLoading ? ' loading' : ''}`;
    
    // Create avatar
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'message-avatar';
    
    if (isUser) {
        avatarDiv.innerHTML = '<span class="material-symbols-outlined">person</span>';
    } else {
        avatarDiv.innerHTML = '<span class="material-symbols-outlined">health_and_safety</span>';
    }
    
    // Create bubble
    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    
    if (isLoading) {
        bubbleDiv.innerHTML = `
            <div class="typing-indicator">
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
                <div class="typing-dot"></div>
            </div>
        `;
    } else {
        bubbleDiv.innerHTML = content;
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(bubbleDiv);
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    
    return messageDiv;
}

// Initialize enhanced features
function initializeEnhancedFeatures() {
    console.log('🎨 Initializing enhanced features...');
    
    // Initialize floating button control
    controlFloatingButton();
    
    // Set up global functions
    window.addMessageEnhanced = addMessageEnhanced;
    if (typeof window.addMessage === 'undefined') {
        window.addMessage = addMessageEnhanced;
    }
    
    console.log('✅ Enhanced features initialized');
}

// Make functions globally available
window.addMessageEnhanced = addMessageEnhanced;

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🎯 Enhanced features main controller loaded');
        initializeEnhancedFeatures();
    });
} else {
    console.log('🎯 Enhanced features main controller loaded (DOM already ready)');
    initializeEnhancedFeatures();
}