/**
 * TOURLI - ADVANCED FEATURES & CUSTOMIZATION GUIDE
 * Optional enhancements and extended functionality
 */

/* ============================================
   ADVANCED JAVASCRIPT FEATURES (Optional)
   ============================================ */

/**
 * Dark/Light Mode Toggle
 */
class ThemeToggle {
  constructor() {
    this.isDark = localStorage.getItem('theme-dark') !== 'false';
    this.init();
  }

  init() {
    // Apply saved theme
    this.applyTheme(this.isDark);

    // Create toggle button if needed
    this.createToggleButton();

    // Listen to system preference changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
      this.setTheme(e.matches);
    });
  }

  createToggleButton() {
    const button = document.createElement('button');
    button.className = 'theme-toggle';
    button.innerHTML = this.isDark ? '☀️' : '🌙';
    button.addEventListener('click', () => this.toggle());
    document.querySelector('.nav-menu')?.appendChild(button);
  }

  toggle() {
    this.isDark = !this.isDark;
    this.applyTheme(this.isDark);
    localStorage.setItem('theme-dark', this.isDark);
  }

  applyTheme(isDark) {
    if (isDark) {
      document.body.classList.remove('light-mode');
    } else {
      document.body.classList.add('light-mode');
    }
  }

  setTheme(isDark) {
    this.isDark = isDark;
    this.applyTheme(isDark);
  }
}

/**
 * Advanced Analytics Tracking
 */
class AnalyticsTracker {
  constructor() {
    this.events = [];
    this.init();
  }

  init() {
    // Track page view
    this.trackEvent('page_view', {
      page: document.title,
      timestamp: new Date().toISOString()
    });

    // Track button clicks
    document.querySelectorAll('button').forEach(btn => {
      btn.addEventListener('click', () => {
        this.trackEvent('button_click', {
          button: btn.textContent,
          class: btn.className
        });
      });
    });

    // Track scroll depth
    window.addEventListener('scroll', () => {
      const scrollPercent = (window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100;
      if (scrollPercent > 50 && !this.mid) {
        this.trackEvent('scroll_50');
        this.mid = true;
      }
      if (scrollPercent > 90 && !this.bottom) {
        this.trackEvent('scroll_90');
        this.bottom = true;
      }
    });
  }

  trackEvent(eventName, data = {}) {
    const event = {
      name: eventName,
      data,
      timestamp: Date.now()
    };

    this.events.push(event);
    console.log('📊 Event:', eventName, data);

    // Send to analytics service
    // this.sendToAnalytics(event);
  }

  sendToAnalytics(event) {
    // Implement your analytics endpoint
    // fetch('/api/analytics', {
    //   method: 'POST',
    //   body: JSON.stringify(event)
    // });
  }
}

/**
 * Advanced Form Handling with LocalStorage
 */
class FormPersistence {
  constructor() {
    this.forms = document.querySelectorAll('form, .newsletter-form');
    this.init();
  }

  init() {
    this.forms.forEach(form => {
      // Load saved data
      this.loadFormData(form);

      // Save on input
      form.addEventListener('input', (e) => {
        this.saveFormData(form);
      });

      // Clear on submit
      form.addEventListener('submit', (e) => {
        this.clearFormData(form);
      });
    });
  }

  saveFormData(form) {
    const data = new FormData(form);
    const formData = {};
    data.forEach((value, key) => {
      formData[key] = value;
    });
    localStorage.setItem(`form-${form.id || 'default'}`, JSON.stringify(formData));
  }

  loadFormData(form) {
    const saved = localStorage.getItem(`form-${form.id || 'default'}`);
    if (saved) {
      const data = JSON.parse(saved);
      Object.keys(data).forEach(key => {
        const input = form.elements[key];
        if (input) input.value = data[key];
      });
    }
  }

  clearFormData(form) {
    localStorage.removeItem(`form-${form.id || 'default'}`);
  }
}

/**
 * Advanced Mouse Tracking for Interactive Effects
 */
class MouseTracker {
  constructor() {
    this.x = 0;
    this.y = 0;
    this.init();
  }

  init() {
    document.addEventListener('mousemove', (e) => {
      this.x = e.clientX;
      this.y = e.clientY;
      this.updateElements();
    });
  }

  updateElements() {
    // Update parallax backgrounds
    const backgrounds = document.querySelectorAll('[data-parallax]');
    backgrounds.forEach(bg => {
      const speed = bg.dataset.parallax || 0.5;
      const x = (this.x / window.innerWidth) * speed * 100;
      const y = (this.y / window.innerHeight) * speed * 100;
      bg.style.transform = `translate(${x}px, ${y}px)`;
    });

    // Update gradient position
    const hero = document.querySelector('.hero-background');
    if (hero) {
      const x = (this.x / window.innerWidth) * 20;
      const y = (this.y / window.innerHeight) * 20;
      hero.style.transform = `translate(${x}px, ${y}px)`;
    }
  }
}

/**
 * Service Worker for Offline Support
 */
class ServiceWorkerManager {
  constructor() {
    this.init();
  }

  init() {
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/sw.js')
        .then(reg => console.log('✅ Service Worker registered'))
        .catch(err => console.log('❌ Service Worker registration failed:', err));
    }
  }
}

/**
 * Notification System
 */
class NotificationManager {
  constructor() {
    this.container = this.createContainer();
  }

  createContainer() {
    const container = document.createElement('div');
    container.id = 'notification-container';
    container.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      z-index: 2000;
      display: flex;
      flex-direction: column;
      gap: 10px;
    `;
    document.body.appendChild(container);
    return container;
  }

  show(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.style.cssText = `
      padding: 1rem;
      border-radius: 0.5rem;
      color: white;
      font-weight: 500;
      animation: slideInRight 0.3s ease-out;
      ${type === 'success' ? 'background: linear-gradient(135deg, #05f2db, #00d9c4);' : ''}
      ${type === 'error' ? 'background: linear-gradient(135deg, #ff3333, #cc0000);' : ''}
      ${type === 'info' ? 'background: linear-gradient(135deg, #6c2eff, #5a24cc);' : ''}
    `;
    notification.textContent = message;

    this.container.appendChild(notification);

    setTimeout(() => {
      notification.style.animation = 'slideOutRight 0.3s ease-out';
      setTimeout(() => notification.remove(), 300);
    }, duration);
  }

  success(message) {
    this.show(message, 'success');
  }

  error(message) {
    this.show(message, 'error');
  }

  info(message) {
    this.show(message, 'info');
  }
}

/**
 * Advanced API Client for Chatbot Integration
 */
class ChatbotAPI {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.headers = {
      'Content-Type': 'application/json'
    };
  }

  async sendMessage(message) {
    try {
      const response = await fetch(`${this.baseURL}/chat`, {
        method: 'POST',
        headers: this.headers,
        body: JSON.stringify({ message })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('❌ Chat API Error:', error);
      throw error;
    }
  }

  async getResponse(userInput) {
    try {
      const data = await this.sendMessage(userInput);
      return data.response || data.message;
    } catch (error) {
      return 'Sorry, I\'m having trouble connecting right now. Please try again later.';
    }
  }

  async getContextualResponses(city) {
    try {
      const response = await fetch(`${this.baseURL}/cities/${city}`);
      return await response.json();
    } catch (error) {
      console.error('Error fetching city data:', error);
      return null;
    }
  }
}

/**
 * Performance Monitor
 */
class PerformanceMonitor {
  constructor() {
    this.metrics = {};
    this.init();
  }

  init() {
    // Core Web Vitals
    if ('PerformanceObserver' in window) {
      // LCP - Largest Contentful Paint
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        const lastEntry = entries[entries.length - 1];
        this.metrics.lcp = lastEntry.renderTime || lastEntry.loadTime;
        console.log('📊 LCP:', this.metrics.lcp);
      }).observe({ entryTypes: ['largest-contentful-paint'] });

      // FID - First Input Delay
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        entries.forEach((entry) => {
          this.metrics.fid = entry.processingDuration;
          console.log('📊 FID:', this.metrics.fid);
        });
      }).observe({ entryTypes: ['first-input'] });
    }

    // Page Load Time
    window.addEventListener('load', () => {
      const perfData = window.performance.timing;
      this.metrics.pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
      console.log('📊 Page Load Time:', this.metrics.pageLoadTime, 'ms');
    });
  }

  getMetrics() {
    return this.metrics;
  }

  report() {
    console.table(this.metrics);
  }
}

/* ============================================
   OPTIONAL: INITIALIZE ADVANCED FEATURES
   ============================================ */

/*
// Uncomment these lines to enable advanced features:

document.addEventListener('DOMContentLoaded', () => {
  // new ThemeToggle();
  // new AnalyticsTracker();
  // new FormPersistence();
  // new MouseTracker();
  // new ServiceWorkerManager();
  // new PerformanceMonitor();
  
  console.log('✨ Advanced features initialized');
});

*/

export {
  ThemeToggle,
  AnalyticsTracker,
  FormPersistence,
  MouseTracker,
  ServiceWorkerManager,
  NotificationManager,
  ChatbotAPI,
  PerformanceMonitor
};
