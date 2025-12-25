/**
 * dLNk IDE - Chat Panel JavaScript
 * AI-04 UI/UX Designer
 * Version: 1.0.0
 * 
 * Interactive functionality for the chat panel
 */

// DOM Elements
const messagesContainer = document.getElementById('messagesContainer');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const charCount = document.getElementById('charCount');
const settingsPanel = document.getElementById('settingsPanel');

// Configuration
const MAX_CHARS = 4000;
let isProcessing = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeChat();
    setupEventListeners();
});

/**
 * Initialize chat functionality
 */
function initializeChat() {
    // Enable/disable send button based on input
    updateSendButton();
    
    // Scroll to bottom
    scrollToBottom();
    
    // Focus input
    messageInput.focus();
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Input change
    messageInput.addEventListener('input', () => {
        updateCharCount();
        updateSendButton();
    });
    
    // Prevent default form submission
    messageInput.addEventListener('keydown', handleKeyDown);
}

/**
 * Handle keyboard events
 */
function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

/**
 * Auto-resize textarea
 */
function autoResize(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 150) + 'px';
}

/**
 * Update character count
 */
function updateCharCount() {
    const count = messageInput.value.length;
    charCount.textContent = `${count} / ${MAX_CHARS}`;
    
    if (count > MAX_CHARS * 0.9) {
        charCount.style.color = 'var(--accent-warning)';
    } else if (count >= MAX_CHARS) {
        charCount.style.color = 'var(--accent-error)';
    } else {
        charCount.style.color = 'var(--text-muted)';
    }
}

/**
 * Update send button state
 */
function updateSendButton() {
    const hasContent = messageInput.value.trim().length > 0;
    const withinLimit = messageInput.value.length <= MAX_CHARS;
    sendBtn.disabled = !hasContent || !withinLimit || isProcessing;
}

/**
 * Send message
 */
async function sendMessage() {
    const message = messageInput.value.trim();
    
    if (!message || isProcessing) return;
    
    // Add user message
    addMessage(message, 'user');
    
    // Clear input
    messageInput.value = '';
    autoResize(messageInput);
    updateCharCount();
    updateSendButton();
    
    // Show loading
    isProcessing = true;
    updateSendButton();
    const loadingId = showLoading();
    
    // Simulate AI response (replace with actual API call)
    try {
        await simulateAIResponse(message, loadingId);
    } catch (error) {
        removeLoading(loadingId);
        addMessage('Sorry, an error occurred. Please try again.', 'ai', true);
    }
    
    isProcessing = false;
    updateSendButton();
}

/**
 * Add message to chat
 */
function addMessage(content, sender, isError = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;
    
    const time = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    const avatarIcon = sender === 'ai' 
        ? `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
           </svg>`
        : `<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
           </svg>`;
    
    const senderName = sender === 'ai' ? 'dLNk AI' : 'You';
    
    messageDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar ${sender}">
                ${avatarIcon}
            </div>
            <span class="message-sender">${senderName}</span>
            <span class="message-time">${time}</span>
        </div>
        <div class="message-content" ${isError ? 'style="border-left: 3px solid var(--accent-error);"' : ''}>
            ${formatMessage(content)}
        </div>
    `;
    
    messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

/**
 * Format message content (Markdown-like)
 */
function formatMessage(content) {
    // Escape HTML
    let formatted = escapeHtml(content);
    
    // Code blocks
    formatted = formatted.replace(/```(\w+)?\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<div class="code-block">
            <div class="code-header">
                <span class="code-language">${lang || 'code'}</span>
                <button class="copy-btn" onclick="copyCode(this)">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                    </svg>
                    Copy
                </button>
            </div>
            <pre class="code-content"><code>${code.trim()}</code></pre>
        </div>`;
    });
    
    // Inline code
    formatted = formatted.replace(/`([^`]+)`/g, '<code>$1</code>');
    
    // Bold
    formatted = formatted.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    
    // Italic
    formatted = formatted.replace(/\*([^*]+)\*/g, '<em>$1</em>');
    
    // Line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Wrap in paragraph if no block elements
    if (!formatted.includes('<div') && !formatted.includes('<ul') && !formatted.includes('<ol')) {
        formatted = `<p>${formatted}</p>`;
    }
    
    return formatted;
}

/**
 * Escape HTML special characters
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Show loading indicator
 */
function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'message ai';
    loadingDiv.id = 'loading-' + Date.now();
    
    loadingDiv.innerHTML = `
        <div class="message-header">
            <div class="message-avatar ai">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
            </div>
            <span class="message-sender">dLNk AI</span>
            <span class="message-time typing-indicator">Thinking...</span>
        </div>
        <div class="message-content">
            <div class="loading">
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
                <div class="loading-dot"></div>
            </div>
        </div>
    `;
    
    messagesContainer.appendChild(loadingDiv);
    scrollToBottom();
    
    return loadingDiv.id;
}

/**
 * Remove loading indicator
 */
function removeLoading(loadingId) {
    const loadingDiv = document.getElementById(loadingId);
    if (loadingDiv) {
        loadingDiv.remove();
    }
}

/**
 * Simulate AI response (demo purposes)
 */
async function simulateAIResponse(userMessage, loadingId) {
    // Simulate network delay
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));
    
    removeLoading(loadingId);
    
    // Generate response based on user message
    let response = generateDemoResponse(userMessage);
    
    addMessage(response, 'ai');
}

/**
 * Generate demo response
 */
function generateDemoResponse(userMessage) {
    const lowerMessage = userMessage.toLowerCase();
    
    if (lowerMessage.includes('hello') || lowerMessage.includes('hi')) {
        return "Hello! 👋 How can I assist you with your coding today?";
    }
    
    if (lowerMessage.includes('help')) {
        return "I'm here to help! I can assist you with:\n\n" +
               "• **Writing code** in various languages\n" +
               "• **Debugging** and fixing errors\n" +
               "• **Explaining** complex concepts\n" +
               "• **Optimizing** your code\n" +
               "• **Documentation** generation\n\n" +
               "Just ask me anything!";
    }
    
    if (lowerMessage.includes('python') || lowerMessage.includes('code')) {
        return "Here's an example Python function:\n\n" +
               "```python\ndef greet(name: str) -> str:\n" +
               "    \"\"\"Return a greeting message.\"\"\"\n" +
               "    return f\"Hello, {name}! Welcome to dLNk IDE.\"\n\n" +
               "# Usage\n" +
               "message = greet(\"Developer\")\n" +
               "print(message)\n```\n\n" +
               "This function demonstrates type hints and f-strings in Python 3.";
    }
    
    return "I understand you're asking about: **" + userMessage.substring(0, 50) + 
           (userMessage.length > 50 ? "..." : "") + "**\n\n" +
           "Let me help you with that. Could you provide more details about what you're trying to achieve?";
}

/**
 * Copy code to clipboard
 */
async function copyCode(button) {
    const codeBlock = button.closest('.code-block');
    const code = codeBlock.querySelector('.code-content code').textContent;
    
    try {
        await navigator.clipboard.writeText(code);
        
        // Visual feedback
        const originalText = button.innerHTML;
        button.innerHTML = `
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="20 6 9 17 4 12"/>
            </svg>
            Copied!
        `;
        button.classList.add('copied');
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.classList.remove('copied');
        }, 2000);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
}

/**
 * Clear chat history
 */
function clearChat() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        messagesContainer.innerHTML = '';
        
        // Add welcome message
        addMessage(
            "👋 Hello! I'm your AI-powered coding assistant. How can I help you today?",
            'ai'
        );
    }
}

/**
 * Toggle settings panel
 */
function toggleSettings() {
    settingsPanel.classList.toggle('open');
}

/**
 * Scroll to bottom of messages
 */
function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

// Export functions for external use
window.sendMessage = sendMessage;
window.copyCode = copyCode;
window.clearChat = clearChat;
window.toggleSettings = toggleSettings;
window.handleKeyDown = handleKeyDown;
window.autoResize = autoResize;
