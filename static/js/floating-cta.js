// Floating CTA Button functionality
function initializeFloatingCTA() {
    const floatingCTA = document.getElementById('floatingCTA');
    const chatSection = document.getElementById('chat');
    let hasShown = false;
    
    // Show floating button when user scrolls past hero section
    function handleScroll() {
        const scrollPosition = window.scrollY;
        const heroHeight = window.innerHeight * 0.8; // Roughly hero section height
        
        if (scrollPosition > heroHeight && !hasShown) {
            if (floatingCTA) {
                floatingCTA.style.opacity = '1';
                floatingCTA.style.transform = 'translateY(0) scale(1)';
                floatingCTA.style.pointerEvents = 'all';
                hasShown = true;
                
                // Add pulse effect
                floatingCTA.style.animation = 'pulse 2s infinite';
                
                // Remove pulse animation after 2 seconds
                setTimeout(() => {
                    floatingCTA.style.animation = '';
                }, 2000);
            }
        } else if (scrollPosition <= heroHeight && hasShown) {
            if (floatingCTA) {
                floatingCTA.style.opacity = '0';
                floatingCTA.style.transform = 'translateY(20px) scale(0.8)';
                floatingCTA.style.pointerEvents = 'none';
                hasShown = false;
            }
        }
        
        // Hide when user reaches chat section
        if (chatSection) {
            const chatRect = chatSection.getBoundingClientRect();
            if (chatRect.top <= window.innerHeight && chatRect.bottom >= 0) {
                if (floatingCTA) {
                    floatingCTA.style.opacity = '0';
                    floatingCTA.style.transform = 'translateY(20px) scale(0.8)';
                    floatingCTA.style.pointerEvents = 'none';
                }
            } else if (hasShown && floatingCTA) {
                floatingCTA.style.opacity = '1';
                floatingCTA.style.transform = 'translateY(0) scale(1)';
                floatingCTA.style.pointerEvents = 'all';
            }
        }
    }
    
    // Throttled scroll handler for better performance
    let ticking = false;
    function throttledScrollHandler() {
        if (!ticking) {
            requestAnimationFrame(() => {
                handleScroll();
                ticking = false;
            });
            ticking = true;
        }
    }
    
    // Add scroll listener
    window.addEventListener('scroll', throttledScrollHandler);
    
    // Initial check
    handleScroll();
}

// Smooth scroll to chat section
function scrollToChat() {
    const chatSection = document.getElementById('chat');
    if (chatSection) {
        chatSection.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
        
        // Add a subtle focus effect to the chat input
        setTimeout(() => {
            const messageInput = document.getElementById('messageInput');
            if (messageInput) {
                messageInput.focus();
                messageInput.style.transform = 'scale(1.02)';
                messageInput.style.boxShadow = '0 0 20px rgba(103, 80, 164, 0.3)';
                
                setTimeout(() => {
                    messageInput.style.transform = '';
                    messageInput.style.boxShadow = '';
                }, 300);
            }
        }, 800);
    }
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing floating CTA...');
    initializeFloatingCTA();
});