// Material 3 Enhanced Animations and Scroll Effects

// Intersection Observer for scroll-triggered animations
function initializeScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
            }
        });
    }, observerOptions);
    
    // Add animation classes to elements
    const sections = document.querySelectorAll('section');
    sections.forEach((section, index) => {
        section.classList.add('fade-in-up');
        section.style.animationDelay = `${index * 0.1}s`;
        observer.observe(section);
    });
    
    // Animate cards in how-it-works section
    const cards = document.querySelectorAll('.m3-card');
    cards.forEach((card, index) => {
        card.classList.add('fade-in-up');
        card.style.animationDelay = `${index * 0.2}s`;
        observer.observe(card);
    });
}

// Enhanced header scroll effect
function initializeHeaderScrollEffect() {
    const header = document.querySelector('header');
    let lastScrollY = window.scrollY;
    
    function updateHeader() {
        const scrollY = window.scrollY;
        
        if (scrollY > 100) {
            header.style.backdropFilter = 'blur(20px)';
            header.style.backgroundColor = 'rgba(255, 251, 254, 0.9)';
            header.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.backdropFilter = 'blur(10px)';
            header.style.backgroundColor = '';
            header.style.boxShadow = '';
        }
        
        // Hide/show header on scroll
        if (scrollY > lastScrollY && scrollY > 200) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        
        lastScrollY = scrollY;
    }
    
    // Throttled scroll handler
    let ticking = false;
    function handleScroll() {
        if (!ticking) {
            requestAnimationFrame(() => {
                updateHeader();
                ticking = false;
            });
            ticking = true;
        }
    }
    
    window.addEventListener('scroll', handleScroll);
}

// Enhanced tab switching with smooth transitions
function switchTabEnhanced(tabName, event) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
        tab.style.transform = 'scale(0.95)';
        setTimeout(() => {
            tab.style.transform = '';
        }, 150);
    });
    
    document.querySelectorAll('.tab-content').forEach(content => {
        content.style.opacity = '0';
        content.style.transform = 'translateY(10px)';
        setTimeout(() => {
            content.classList.remove('active');
        }, 200);
    });
    
    // Add active class to selected tab and content with delay
    setTimeout(() => {
        if (event && event.target) {
            const clickedTab = event.target.closest('.tab');
            if (clickedTab) {
                clickedTab.classList.add('active');
                clickedTab.style.transform = 'scale(1.05)';
                setTimeout(() => {
                    clickedTab.style.transform = '';
                }, 200);
            }
        }
        
        const targetContent = document.getElementById(tabName + '-tab');
        if (targetContent) {
            targetContent.classList.add('active');
            targetContent.style.opacity = '1';
            targetContent.style.transform = 'translateY(0)';
        }
    }, 200);
}

// Enhanced button click effects
function addButtonRippleEffect() {
    // Add CSS for ripple effect if not exists
    if (!document.getElementById('ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            .ripple {
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.6);
                transform: scale(0);
                animation: ripple-animation 0.6s linear;
                pointer-events: none;
                z-index: 1;
            }
            
            @keyframes ripple-animation {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
            
            .m3-button {
                position: relative;
                overflow: hidden;
            }
        `;
        document.head.appendChild(style);
    }
    
    document.querySelectorAll('.m3-button').forEach(button => {
        // Remove existing ripple listeners to prevent duplicates
        button.removeEventListener('click', handleRippleClick);
        button.addEventListener('click', handleRippleClick);
    });
}

function handleRippleClick(e) {
    const ripple = document.createElement('span');
    const rect = this.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = e.clientX - rect.left - size / 2;
    const y = e.clientY - rect.top - size / 2;
    
    ripple.style.width = ripple.style.height = size + 'px';
    ripple.style.left = x + 'px';
    ripple.style.top = y + 'px';
    ripple.classList.add('ripple');
    
    this.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

// Enhanced theme toggle animation
function themeToggleEnhanced() {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    
    // Add transition class to body
    document.body.style.transition = 'all 0.5s cubic-bezier(0.25, 0.46, 0.45, 0.94)';
    
    // Call the original theme toggle if it exists
    if (typeof toggleTheme === 'function') {
        toggleTheme();
    } else {
        // Fallback theme switching
        document.documentElement.setAttribute('data-theme', newTheme);
        localStorage.setItem('theme', newTheme);
        
        // Apply theme with smooth transition
        if (newTheme === 'dark') {
            if (typeof applyDarkTheme === 'function') applyDarkTheme();
        } else {
            if (typeof applyLightTheme === 'function') applyLightTheme();
        }
        
        if (typeof updateThemeToggleButton === 'function') {
            updateThemeToggleButton(newTheme);
        }
    }
    
    // Remove transition class after animation
    setTimeout(() => {
        document.body.style.transition = '';
    }, 500);
}

// Initialize all enhanced animations
function initializeEnhancedAnimations() {
    console.log('Initializing enhanced animations...');
    
    initializeScrollAnimations();
    initializeHeaderScrollEffect();
    addButtonRippleEffect();
    
    console.log('Enhanced animations initialized');
}

// Initialize on DOM load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Initializing Material 3 animations...');
    initializeEnhancedAnimations();

    // Make enhanced functions available globally without overriding
    window.switchTabEnhanced = switchTabEnhanced;
    window.themeToggleEnhanced = themeToggleEnhanced;
    window.addButtonRippleEffect = addButtonRippleEffect;
});