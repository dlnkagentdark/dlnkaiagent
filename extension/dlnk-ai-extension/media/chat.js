/**
 * dLNk AI Chat Panel Scripts
 * Handles UI interactions and message rendering
 */

(function() {
    // VS Code API
    const vscode = acquireVsCodeApi();
    
    // DOM Elements
    const messagesContainer = document.getElementById('messagesContainer');
    const messageInput = document.getElementById('messageInput');
    const sendButton = document.getElementById('sendButton');
    const typingIndicator = document.getElementById('typingIndicator');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');
    
    // State
    let isTyping = false;
    let currentStreamMessage = null;
    let currentStreamContent = '';
    
    // Initialize
    init();
    
    function init() {
        // Event listeners
        sendButton.addEventListener('click', sendMessage);
        messageInput.addEventListener('keydown', handleKeydown);
        messageInput.addEventListener('input', autoResize);
        
        // Quick action buttons
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', () => handleQuickAction(btn.dataset.action));
        });
        
        // Notify extension that webview is ready
        vscode.postMessage({ type: 'ready' });
    }
    
    function sendMessage() {
        const content = messageInput.value.trim();
        if (!content || isTyping) return;
        
        vscode.postMessage({ type: 'sendMessage', content });
        messageInput.value = '';
        autoResize();
    }
    
    function handleKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    }
    
    function autoResize() {
        messageInput.style.height = 'auto';
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + 'px';
    }
    
    function handleQuickAction(action) {
        const prompts = {
            explain: 'Please explain the selected code in my editor.',
            generate: 'Generate code for: ',
            fix: 'Please fix the selected code in my editor.'
        };
        
        if (action === 'generate') {
            messageInput.value = prompts[action];
            messageInput.focus();
            messageInput.setSelectionRange(prompts[action].length, prompts[action].length);
        } else {
            vscode.postMessage({ type: 'sendMessage', content: prompts[action] });
        }
    }
    
    // Message handling from extension
    window.addEventListener('message', event => {
        const message = event.data;
        
        switch (message.type) {
            case 'addMessage':
                addMessage(message.role, message.content);
                break;
            case 'setTyping':
                setTyping(message.typing);
                break;
            case 'startStream':
                startStreamMessage(message.messageId);
                break;
            case 'streamChunk':
                appendStreamChunk(message.chunk, message.done);
                break;
            case 'clearMessages':
                clearMessages();
                break;
            case 'loadHistory':
                loadHistory(message.messages);
                break;
            case 'connectionStatus':
                updateConnectionStatus(message.connected);
                break;
        }
    });
    
    function addMessage(role, content) {
        // Remove welcome message if exists
        const welcome = messagesContainer.querySelector('.welcome-message');
        if (welcome) {
            welcome.remove();
        }
        
        const messageEl = createMessageElement(role, content);
        messagesContainer.appendChild(messageEl);
        scrollToBottom();
    }
    
    function createMessageElement(role, content) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        contentDiv.innerHTML = formatContent(content, role);
        
        div.appendChild(contentDiv);
        
        // Add timestamp
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-time';
        timeDiv.textContent = formatTime(new Date());
        div.appendChild(timeDiv);
        
        // Add code action buttons
        if (role === 'assistant') {
            addCodeActionButtons(contentDiv);
        }
        
        return div;
    }
    
    function formatContent(content, role) {
        if (role === 'user') {
            return escapeHtml(content);
        }
        
        // Simple markdown parsing for assistant messages
        let html = content;
        
        // Code blocks
        html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
            const language = lang || 'plaintext';
            const escapedCode = escapeHtml(code.trim());
            return `<pre><div class="code-header"><span class="code-language">${language}</span><div class="code-actions"><button class="code-action-btn copy-btn" data-code="${encodeURIComponent(code.trim())}">Copy</button><button class="code-action-btn insert-btn" data-code="${encodeURIComponent(code.trim())}">Insert</button></div></div><code class="language-${language}">${escapedCode}</code></pre>`;
        });
        
        // Inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');
        
        // Bold
        html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
        
        // Italic
        html = html.replace(/\*([^*]+)\*/g, '<em>$1</em>');
        
        // Line breaks
        html = html.replace(/\n/g, '<br>');
        
        return html;
    }
    
    function addCodeActionButtons(contentDiv) {
        contentDiv.querySelectorAll('.copy-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const code = decodeURIComponent(btn.dataset.code);
                vscode.postMessage({ type: 'copyCode', code });
                btn.textContent = 'Copied!';
                setTimeout(() => { btn.textContent = 'Copy'; }, 2000);
            });
        });
        
        contentDiv.querySelectorAll('.insert-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const code = decodeURIComponent(btn.dataset.code);
                vscode.postMessage({ type: 'insertCode', code });
            });
        });
    }
    
    function startStreamMessage(messageId) {
        // Remove welcome message if exists
        const welcome = messagesContainer.querySelector('.welcome-message');
        if (welcome) {
            welcome.remove();
        }
        
        currentStreamContent = '';
        currentStreamMessage = document.createElement('div');
        currentStreamMessage.className = 'message assistant';
        currentStreamMessage.id = `stream-${messageId}`;
        
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        currentStreamMessage.appendChild(contentDiv);
        
        messagesContainer.appendChild(currentStreamMessage);
        scrollToBottom();
    }
    
    function appendStreamChunk(chunk, done) {
        if (!currentStreamMessage) return;
        
        currentStreamContent += chunk;
        const contentDiv = currentStreamMessage.querySelector('.message-content');
        contentDiv.innerHTML = formatContent(currentStreamContent, 'assistant');
        
        if (done) {
            // Add timestamp
            const timeDiv = document.createElement('div');
            timeDiv.className = 'message-time';
            timeDiv.textContent = formatTime(new Date());
            currentStreamMessage.appendChild(timeDiv);
            
            // Add code action buttons
            addCodeActionButtons(contentDiv);
            
            currentStreamMessage = null;
            currentStreamContent = '';
        }
        
        scrollToBottom();
    }
    
    function setTyping(typing) {
        isTyping = typing;
        typingIndicator.classList.toggle('active', typing);
        sendButton.disabled = typing;
        
        if (typing) {
            scrollToBottom();
        }
    }
    
    function clearMessages() {
        messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-icon">🚀</div>
                <h3>Chat Cleared</h3>
                <p>Start a new conversation!</p>
                <div class="quick-actions">
                    <button class="quick-action" data-action="explain">Explain Code</button>
                    <button class="quick-action" data-action="generate">Generate Code</button>
                    <button class="quick-action" data-action="fix">Fix Code</button>
                </div>
            </div>
        `;
        
        // Re-attach quick action listeners
        document.querySelectorAll('.quick-action').forEach(btn => {
            btn.addEventListener('click', () => handleQuickAction(btn.dataset.action));
        });
    }
    
    function loadHistory(messages) {
        if (!messages || messages.length === 0) return;
        
        // Clear welcome message
        const welcome = messagesContainer.querySelector('.welcome-message');
        if (welcome) {
            welcome.remove();
        }
        
        // Add messages
        messages.forEach(msg => {
            const messageEl = createMessageElement(msg.role, msg.content);
            messagesContainer.appendChild(messageEl);
        });
        
        scrollToBottom();
    }
    
    function updateConnectionStatus(connected) {
        statusDot.className = `status-dot ${connected ? 'connected' : 'disconnected'}`;
        statusText.textContent = connected ? 'Connected' : 'Disconnected';
    }
    
    function scrollToBottom() {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    function formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
})();
