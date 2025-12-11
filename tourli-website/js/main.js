/**
 * Tourli Landing Website - Main JavaScript
 * Handles scroll animations, interactions, and smooth behaviors
 */

// ===== CONFIGURATION =====
const CONFIG = {
    scrollThreshold: 0.15,
    animationDuration: 300,
};

// ===== UTILITY FUNCTIONS =====

/**
 * Checks if an element is in the viewport
 */
function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
        rect.top <= (window.innerHeight || document.documentElement.clientHeight) * (1 - CONFIG.scrollThreshold) &&
        rect.bottom >= 0
    );
}

/**
 * Throttle function to limit execution frequency
 */
function throttle(func, limit) {
    let inThrottle;
    return function (...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => (inThrottle = false), limit);
        }
    };
}

/**
 * Debounce function
 */
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// ===== SCROLL ANIMATIONS =====

class ScrollAnimations {
    constructor() {
        this.elements = document.querySelectorAll('.feature-card, .feature-item, .testimonial-card, .preview-card');
        this.init();
    }

    init() {
        // Initial check for elements already in view
        this.checkElements();
        
        // Listen to scroll events
        window.addEventListener('scroll', throttle(() => this.checkElements(), 100));
    }

    checkElements() {
        this.elements.forEach(el => {
            if (isElementInViewport(el) && !el.classList.contains('fade-in')) {
                this.animateElement(el);
            }
        });
    }

    animateElement(el) {
        el.classList.add('fade-in');
        // Stagger animation for multiple elements
        const delay = Array.from(this.elements).indexOf(el) * 100;
        el.style.animation = `fadeIn 0.8s ease-out ${delay}ms forwards`;
    }
}

// ===== SMOOTH SCROLL FOR NAVIGATION =====

class SmoothScroll {
    constructor() {
        this.links = document.querySelectorAll('a[href^="#"]');
        this.init();
    }

    init() {
        this.links.forEach(link => {
            link.addEventListener('click', e => this.handleClick(e));
        });
    }

    handleClick(e) {
        const href = e.currentTarget.getAttribute('href');
        
        if (href === '#') {
            e.preventDefault();
            return;
        }

        const target = document.querySelector(href);
        
        if (target) {
            e.preventDefault();
            this.scrollToElement(target);
        }
    }

    scrollToElement(element) {
        const offsetTop = element.offsetTop - 60; // Account for navbar height
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    }
}

// ===== BUTTON INTERACTIONS =====

class ButtonInteractions {
    constructor() {
        // Select all buttons with class 'btn' and elements with class 'nav-cta'
        this.buttons = document.querySelectorAll('.btn, .nav-cta');
        this.init();
    }

    init() {
        console.log('ButtonInteractions initialized with', this.buttons.length, 'buttons');
        this.buttons.forEach((btn, index) => {
            console.log(`Button ${index}:`, btn.textContent.trim(), btn.className);
            btn.addEventListener('click', e => this.handleButtonClick(e));
            btn.addEventListener('mouseenter', e => this.handleHover(e));
            btn.addEventListener('mouseleave', e => this.handleHoverEnd(e));
        });
    }

    handleButtonClick(e) {
        const btn = e.currentTarget;
        const text = btn.textContent.toLowerCase();
        
        console.log('Button clicked:', text);
        
        // Add ripple effect
        this.createRipple(btn, e);
        
        // Handle different button types
        if (text.includes('start chatting') || text.includes('start your adventure')) {
            console.log('Opening chat');
            this.openChat();
        } else if (text.includes('learn more')) {
            console.log('Scrolling to features');
            this.scrollToSection('#features');
        } else if (text.includes('subscribe')) {
            console.log('Subscribing to newsletter');
            this.handleNewsletterSubscribe(btn);
        }
    }

    createRipple(btn, e) {
        // Remove previous ripple if exists
        const prevRipple = btn.querySelector('.ripple');
        if (prevRipple) prevRipple.remove();
        
        const ripple = document.createElement('span');
        ripple.classList.add('ripple');
        
        const rect = btn.getBoundingClientRect();
        const size = Math.max(rect.width, rect.height);
        const x = e.clientX - rect.left - size / 2;
        const y = e.clientY - rect.top - size / 2;

        ripple.style.width = ripple.style.height = size + 'px';
        ripple.style.left = x + 'px';
        ripple.style.top = y + 'px';
        ripple.style.position = 'absolute';
        ripple.style.background = 'rgba(255, 255, 255, 0.5)';
        ripple.style.borderRadius = '50%';
        ripple.style.pointerEvents = 'none';
        ripple.style.animation = 'ripple-animation 0.6s ease-out';

        btn.style.position = 'relative';
        btn.style.overflow = 'hidden';
        btn.appendChild(ripple);
        
        setTimeout(() => ripple.remove(), 600);
    }

    handleHover(e) {
        const btn = e.currentTarget;
        btn.style.transform = 'translateY(-2px)';
    }

    handleHoverEnd(e) {
        const btn = e.currentTarget;
        btn.style.transform = 'translateY(0)';
    }

    openChat() {
        // Navigate to the dedicated chat page
        window.location.href = 'chat.html';
    }

    scrollToSection(selector) {
        const element = document.querySelector(selector);
        if (element) {
            element.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    handleNewsletterSubscribe(btn) {
        const input = btn.previousElementSibling;
        const email = input?.value?.trim();
        
        if (!email) {
            alert('Please enter your email address');
            return;
        }
        
        // Simple email validation
        if (!email.includes('@')) {
            alert('Please enter a valid email address');
            return;
        }
        
        // Show success feedback
        const originalText = btn.textContent;
        btn.textContent = '✓ Subscribed!';
        btn.style.background = '#05f2db';
        btn.style.color = '#050509';
        
        // Clear input
        input.value = '';
        
        // Reset button after 3 seconds
        setTimeout(() => {
            btn.textContent = originalText;
            btn.style.background = '';
            btn.style.color = '';
        }, 3000);
        
        console.log('Newsletter subscription from:', email);
    }
}

// ===== NAVBAR SCROLL BEHAVIOR =====

class NavbarScroll {
    constructor() {
        this.navbar = document.querySelector('.navbar');
        this.init();
    }

    init() {
        window.addEventListener('scroll', throttle(() => this.updateNavbar(), 100));
    }

    updateNavbar() {
        const scrollTop = window.scrollY;
        
        if (scrollTop > 50) {
            this.navbar.style.borderBottomColor = 'rgba(5, 242, 219, 0.1)';
            this.navbar.style.boxShadow = '0 4px 12px rgba(5, 242, 219, 0.05)';
        } else {
            this.navbar.style.borderBottomColor = 'var(--border-color)';
            this.navbar.style.boxShadow = 'none';
        }
    }
}

// ===== CHAT INPUT FUNCTIONALITY =====

class ChatSimulation {
    constructor() {
        this.chatInput = document.querySelector('.chat-input input');
        this.sendBtn = document.querySelector('.send-btn');
        this.chatMessages = document.querySelector('.chat-messages');
        this.init();
    }

    init() {
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.simulateSendMessage());
            this.chatInput?.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.simulateSendMessage();
                }
            });
        }
    }

    simulateSendMessage() {
        const message = this.chatInput.value.trim();
        
        if (!message) return;

        // Add user message
        this.addMessage(message, 'user');
        this.chatInput.value = '';

        // Simulate bot response
        setTimeout(() => {
            const responses = [
                'That\'s a great question! Let me find the best information for you...',
                'Marrakech is absolutely beautiful! The medina is a must-see...',
                'I\'d recommend visiting during the spring or fall for the best weather...',
                'The food scene in Morocco is incredible! You\'ll love it...',
                'Have you considered the Atlas Mountains? Stunning views guaranteed...'
            ];
            
            const randomResponse = responses[Math.floor(Math.random() * responses.length)];
            this.addMessage(randomResponse, 'bot');
        }, 800);
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.innerHTML = `<p>${text}</p>`;
        
        this.chatMessages.appendChild(messageDiv);
        
        // Auto-scroll to latest message
        this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
        
        // Animate new message
        messageDiv.style.animation = 'slideIn 0.5s ease-out';
    }
}

// ===== PARALLAX EFFECT =====

class ParallaxEffect {
    constructor() {
        this.background = document.querySelector('.hero-background');
        this.init();
    }

    init() {
        window.addEventListener('mousemove', throttle((e) => this.handleMouseMove(e), 50));
    }

    handleMouseMove(e) {
        if (!this.background) return;

        const x = (e.clientX / window.innerWidth) * 20;
        const y = (e.clientY / window.innerHeight) * 20;

        this.background.style.transform = `translate(${x}px, ${y}px)`;
    }
}

// ===== INTERSECTION OBSERVER (Alternative Scroll Detection) =====

class ObserverAnimations {
    constructor() {
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    this.observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        this.init();
    }

    init() {
        document.querySelectorAll('.feature-card, .feature-item, .testimonial-card').forEach(el => {
            this.observer.observe(el);
        });
    }
}

// ===== LOADING PERFORMANCE =====

class PerformanceOptimization {
    constructor() {
        this.init();
    }

    init() {
        // Lazy load images
        this.setupLazyLoading();
        
        // Prefetch links
        this.setupPrefetch();
    }

    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const images = document.querySelectorAll('img[data-lazy]');
            
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        img.src = img.dataset.lazy;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                });
            });

            images.forEach(img => imageObserver.observe(img));
        }
    }

    setupPrefetch() {
        // Prefetch important resources
        const link = document.createElement('link');
        link.rel = 'prefetch';
        link.href = '/chatbot';
        document.head.appendChild(link);
    }
}

// ===== FORM VALIDATION =====

class FormValidation {
    constructor() {
        this.newsletterForm = document.querySelector('.newsletter-form');
        this.init();
    }

    init() {
        if (this.newsletterForm) {
            const input = this.newsletterForm.querySelector('input');
            const button = this.newsletterForm.querySelector('button');

            button?.addEventListener('click', () => this.validateEmail(input));
            input?.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    this.validateEmail(input);
                }
            });
        }
    }

    validateEmail(input) {
        const email = input.value.trim();
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (!email) {
            this.showMessage(input, 'Please enter your email', 'error');
            return;
        }

        if (!emailRegex.test(email)) {
            this.showMessage(input, 'Please enter a valid email', 'error');
            return;
        }

        this.showMessage(input, 'Thanks for subscribing!', 'success');
        input.value = '';
    }

    showMessage(input, message, type) {
        // Remove existing message
        const existing = input.nextElementSibling;
        if (existing?.classList.contains('form-message')) {
            existing.remove();
        }

        // Create and show new message
        const messageEl = document.createElement('div');
        messageEl.className = `form-message form-message-${type}`;
        messageEl.textContent = message;
        messageEl.style.cssText = `
            margin-top: 0.5rem;
            padding: 0.5rem;
            border-radius: 0.25rem;
            font-size: 0.9rem;
            ${type === 'error' ? 'background: rgba(255, 50, 50, 0.1); color: #ff3232;' : 'background: rgba(5, 242, 219, 0.1); color: #05f2db;'}
        `;

        input.parentNode.insertBefore(messageEl, input.nextSibling);

        setTimeout(() => messageEl.remove(), 3000);
    }
}

// ===== INITIALIZATION =====

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all features
    new ScrollAnimations();
    new SmoothScroll();
    new ButtonInteractions();
    new NavbarScroll();
    new ChatSimulation();
    new ParallaxEffect();
    new ObserverAnimations();
    new PerformanceOptimization();
    new FormValidation();

    console.log('✈️ Tourli Landing Website loaded successfully!');
});

// ===== WINDOW RESIZE HANDLER =====

window.addEventListener('resize', debounce(() => {
    console.log('Window resized');
}, 250));

// ===== ERROR HANDLING =====

window.addEventListener('error', (e) => {
    console.error('Error caught:', e.error);
});

// ===== PERFORMANCE MONITORING =====

if (window.performance && window.performance.timing) {
    window.addEventListener('load', () => {
        const perfData = window.performance.timing;
        const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
        console.log(`Page load time: ${pageLoadTime}ms`);
    });
}
