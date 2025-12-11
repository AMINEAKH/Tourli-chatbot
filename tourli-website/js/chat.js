// ===== CHAT PAGE JAVASCRIPT =====
// ===== CHAT APPLICATION (Optimized for External API) =====

const STORAGE_KEY = 'chatbot_all_chats';

class ChatInterface {
    constructor() {
        // DOM Elements
        this.userInput = document.getElementById('userInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.messagesContainer = document.getElementById('messagesContainer');
        this.welcomeSection = document.getElementById('welcomeSection');
        this.sidebar = document.getElementById('sidebar');
        this.menuBtn = document.getElementById('menuBtn');
        this.closeSidebarBtn = document.getElementById('closeSidebar');
        this.loadingIndicator = document.getElementById('loadingIndicator');
        
        // Configuration
        this.apiUrl = 'http://localhost:5000/api/chat';
        this.isAPIAvailable = true; 

        // Chat State
        this.allChats = this.loadAllChats();
        // Set current chat to the most recent one, or the initial new chat
        this.currentChat = this.allChats.length > 0 ? this.allChats[0] : null;

        this.init();
    }

    // --- DATA MANAGEMENT ---

    loadAllChats() {
        const historyString = localStorage.getItem(STORAGE_KEY);
        let chats = historyString ? JSON.parse(historyString) : [];
        
        // If no chats exist, create a default "New Chat" instance
        if (chats.length === 0) {
            const initialChat = { id: `chat-${Date.now()}`, title: 'New Chat', messages: [] };
            return [initialChat]; 
        }
        return chats;
    }

    saveAllChats() {
        localStorage.setItem(STORAGE_KEY, JSON.stringify(this.allChats));
        if (window.historyManager) {
            window.historyManager.renderSidebar();
        }
    }
    
    createNewChat(isInitialLoad = false) {
        const newChat = { id: `chat-${Date.now()}`, title: 'New Chat', messages: [] };
        
        if (isInitialLoad) return [newChat]; 
        
        this.allChats.unshift(newChat);
        this.saveAllChats();
        this.currentChat = newChat;
        return newChat;
    }
    
    updateChatTitle(messageText) {
        if (!this.currentChat || this.currentChat.title !== 'New Chat') return;

        let title = messageText.substring(0, 30);
        if (messageText.length > 30) title += '...';
        
        this.currentChat.title = title;
        this.saveAllChats();
    }
    
    // --- INITIALIZATION ---

    init() {
        // Setup Event Listeners
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        this.menuBtn.addEventListener('click', () => this.sidebar.classList.add('active'));
        this.closeSidebarBtn.addEventListener('click', () => this.sidebar.classList.remove('active'));
        
        document.querySelectorAll('.prompt-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.userInput.value = btn.dataset.prompt;
                this.userInput.focus();
                setTimeout(() => this.sendMessage(), 100);
            });
        });

        this.userInput.focus();
        this.checkAPIStatus();
        
        // Load the chat content
        if (this.currentChat) {
             this.renderChat(this.currentChat.messages);
        }
    }
    
    checkAPIStatus() {
        fetch('http://localhost:5000/api/init', { method: 'POST' })
            .then(res => res.json())
            .then(() => {
                console.log('✓ Chatbot API initialized.');
                this.isAPIAvailable = true;
            })
            .catch(err => {
                console.warn('⚠ Chatbot API not available. Chat will be disabled.', err.message);
                this.isAPIAvailable = false;
                this.userInput.placeholder = "Chat is unavailable: Backend server not running.";
                this.userInput.disabled = true;
            });
    }

    // --- MESSAGE HANDLING ---

    sendMessage() {
        const message = this.userInput.value.trim();
        if (!message || !this.isAPIAvailable) return;

        if (this.welcomeSection.offsetParent !== null) {
            this.welcomeSection.style.display = 'none';
        }

        this.addMessage(message, 'user');
        this.updateChatTitle(message); 

        this.userInput.value = '';
        this.userInput.focus();
        this.showLoading();

        this.getResponseFromAPI(message);
    }

    getResponseFromAPI(message) {
        fetch(this.apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            this.hideLoading();
            const botResponse = data.response || 'Sorry, the chatbot returned an empty response.';
            this.addMessage(botResponse, 'bot');
            this.saveAllChats();
        })
        .catch(error => {
            console.error('API Error:', error);
            this.hideLoading();
            this.addMessage('Error: Could not connect to the chat service.', 'bot');
            this.saveAllChats();
        });
    }

    // isRenderingOldChat prevents saving messages already in history
    addMessage(text, sender, isRenderingOldChat = false) {
        if (this.currentChat && !isRenderingOldChat) {
            this.currentChat.messages.push({ sender, text });
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.textContent = text;

        messageDiv.appendChild(contentDiv);
        this.messagesContainer.appendChild(messageDiv);

        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }, 0);
    }
    
    // --- RENDERING ---

    renderChat(messages) {
        this.messagesContainer.innerHTML = '';
        this.welcomeSection.style.display = messages.length > 0 ? 'none' : 'flex'; 
        
        messages.forEach(msg => {
            this.addMessage(msg.text, msg.sender, true);
        });
    }

    showLoading() {
        this.loadingIndicator.classList.add('active');
    }

    hideLoading() {
        this.loadingIndicator.classList.remove('active');
    }
}

// --- CHAT HISTORY MANAGER ---

class ChatHistoryManager {
    constructor(chatApp) {
        this.chatApp = chatApp; 
        this.sidebarHistory = document.querySelector('.chat-history');
        this.newChatBtn = document.querySelector('.new-chat-btn');
        
        this.init();
        this.renderSidebar(); 
    }

    init() {
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
    }
    
    startNewChat() {
        // 🌟 FIX: Ensure the current chat is fully saved before starting a new one
        const currentChat = this.chatApp.currentChat;
        if (currentChat && currentChat.messages.length > 0) {
            // This ensures the title is finalized and the sidebar is updated 
            // with the final state of the old chat.
            this.chatApp.saveAllChats(); 
        }

        // 1. Create a new chat object and set it as current
        this.chatApp.createNewChat(); 
        
        // 2. Render the new, empty chat in the main area
        this.chatApp.renderChat([]); 
        
        // 3. Update the sidebar UI (new chat will be at the top and active)
        this.renderSidebar();
        
        // 4. Close the sidebar (optional) and focus input
        document.getElementById('sidebar').classList.remove('active');
        document.getElementById('userInput').focus();
    }
    
    // ... rest of the class (renderSidebar, loadChat, deleteChat) ...
    
    renderSidebar() {
        this.sidebarHistory.innerHTML = '';
        
        this.chatApp.allChats.forEach(chat => {
            const item = document.createElement('div');
            item.classList.add('history-item');
            
            if (this.chatApp.currentChat && this.chatApp.currentChat.id === chat.id) {
                item.classList.add('active');
            }
            
            const titleText = chat.title || 'Untitled Chat';
            
            item.innerHTML = `<p>${titleText}</p><span class="delete-btn">×</span>`;
            
            item.addEventListener('click', (e) => {
                if (!e.target.closest('.delete-btn')) {
                    this.loadChat(chat.id);
                }
            });

            item.querySelector('.delete-btn').addEventListener('click', (e) => {
                e.stopPropagation(); 
                this.deleteChat(chat.id);
            });

            this.sidebarHistory.appendChild(item);
        });
    }

    loadChat(chatId) {
        const chatToLoad = this.chatApp.allChats.find(chat => chat.id === chatId);
        
        if (chatToLoad) {
            this.chatApp.currentChat = chatToLoad;
            this.chatApp.renderChat(chatToLoad.messages);
            this.renderSidebar();
            document.getElementById('sidebar').classList.remove('active');
        }
    }

    deleteChat(chatId) {
        const wasActive = this.chatApp.currentChat && this.chatApp.currentChat.id === chatId;
        
        this.chatApp.allChats = this.chatApp.allChats.filter(chat => chat.id !== chatId);
        this.chatApp.saveAllChats();
        
        if (wasActive) {
            if (this.chatApp.allChats.length > 0) {
                this.loadChat(this.chatApp.allChats[0].id);
            } else {
                this.startNewChat();
            }
        } else {
            this.renderSidebar();
        }
    }
}
// --- SETTINGS AND GLOBAL INIT ---

class ChatSettings {
    constructor() {
        this.settingsBtn = document.querySelector('.settings-btn');
        this.init();
    }

    init() {
        this.settingsBtn.addEventListener('click', () => {
            const confirmed = confirm('Do you want to clear ALL chat history? This cannot be undone.');
            if (confirmed) {
                localStorage.removeItem(STORAGE_KEY);
                alert('All chat history has been cleared. The page will now reload.');
                window.location.reload();
            }
        });
    }
}

// Global Initialization
document.addEventListener('DOMContentLoaded', () => {
    console.log('Chat page loaded');
    
    // Expose instances globally for inter-class communication
    window.chatApp = new ChatInterface();
    window.historyManager = new ChatHistoryManager(window.chatApp);
    
    new ChatSettings();
});