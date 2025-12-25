/**
 * AI Integration Module for Antigravity
 * เชื่อมต่อ Antigravity IDE กับ dLNk AI Bridge Service
 * รองรับการสื่อสารแบบ real-time และ persistent connection
 */

const vscode = require('vscode');
const WebSocket = require('ws');
const http = require('http');
const path = require('path');
const fs = require('fs');

// Configuration
const CONFIG = {
    BRIDGE_HOST: 'localhost',
    BRIDGE_PORT: 8765,
    RECONNECT_INTERVAL: 5000,
    MAX_RECONNECT_ATTEMPTS: 10,
    HEARTBEAT_INTERVAL: 30000,
    MESSAGE_TIMEOUT: 60000
};

/**
 * Connection Status Enum
 */
const ConnectionStatus = {
    DISCONNECTED: 'disconnected',
    CONNECTING: 'connecting',
    CONNECTED: 'connected',
    RECONNECTING: 'reconnecting',
    ERROR: 'error'
};

/**
 * AI Provider Types
 */
const AIProvider = {
    JETSKI: 'jetski',
    GEMINI: 'gemini',
    OPENAI: 'openai',
    LOCAL: 'local'
};

/**
 * AI Integration Manager
 * จัดการการเชื่อมต่อและการสื่อสารกับ AI
 */
class AIIntegrationManager {
    constructor(context) {
        this.context = context;
        this.ws = null;
        this.status = ConnectionStatus.DISCONNECTED;
        this.reconnectAttempts = 0;
        this.heartbeatTimer = null;
        this.messageQueue = [];
        this.pendingRequests = new Map();
        this.eventHandlers = new Map();
        this.sessionId = null;
        this.activeProvider = null;
        
        // Status bar item
        this.statusBarItem = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            100
        );
        this.statusBarItem.command = 'antigravity.showAIStatus';
        this.updateStatusBar();
        this.statusBarItem.show();
    }

    /**
     * Initialize the AI Integration
     */
    async initialize() {
        console.log('[AIIntegration] Initializing...');
        
        // Register commands
        this.registerCommands();
        
        // Load saved configuration
        await this.loadConfiguration();
        
        // Attempt to connect
        await this.connect();
        
        console.log('[AIIntegration] Initialized');
    }

    /**
     * Register VS Code commands
     */
    registerCommands() {
        const commands = [
            vscode.commands.registerCommand('antigravity.connectAI', () => this.connect()),
            vscode.commands.registerCommand('antigravity.disconnectAI', () => this.disconnect()),
            vscode.commands.registerCommand('antigravity.showAIStatus', () => this.showStatus()),
            vscode.commands.registerCommand('antigravity.sendToAI', (message) => this.sendMessage(message)),
            vscode.commands.registerCommand('antigravity.switchAIProvider', () => this.switchProvider()),
            vscode.commands.registerCommand('antigravity.clearAIHistory', () => this.clearHistory())
        ];

        commands.forEach(cmd => this.context.subscriptions.push(cmd));
    }

    /**
     * Load configuration from settings
     */
    async loadConfiguration() {
        const config = vscode.workspace.getConfiguration('antigravity.ai');
        
        CONFIG.BRIDGE_HOST = config.get('bridgeHost', CONFIG.BRIDGE_HOST);
        CONFIG.BRIDGE_PORT = config.get('bridgePort', CONFIG.BRIDGE_PORT);
        CONFIG.RECONNECT_INTERVAL = config.get('reconnectInterval', CONFIG.RECONNECT_INTERVAL);
        
        // Load saved session
        this.sessionId = this.context.globalState.get('aiSessionId');
        this.activeProvider = this.context.globalState.get('aiProvider', AIProvider.JETSKI);
    }

    /**
     * Connect to AI Bridge Service
     */
    async connect() {
        if (this.status === ConnectionStatus.CONNECTING) {
            console.log('[AIIntegration] Already connecting...');
            return;
        }

        this.status = ConnectionStatus.CONNECTING;
        this.updateStatusBar();

        try {
            // First, try WebSocket connection
            const wsUrl = `ws://${CONFIG.BRIDGE_HOST}:${CONFIG.BRIDGE_PORT}/ws`;
            
            return new Promise((resolve, reject) => {
                this.ws = new WebSocket(wsUrl);

                this.ws.on('open', () => {
                    console.log('[AIIntegration] Connected to AI Bridge');
                    this.status = ConnectionStatus.CONNECTED;
                    this.reconnectAttempts = 0;
                    this.updateStatusBar();
                    this.startHeartbeat();
                    this.processMessageQueue();
                    this.emit('connected');
                    resolve(true);
                });

                this.ws.on('message', (data) => {
                    this.handleMessage(data);
                });

                this.ws.on('close', () => {
                    console.log('[AIIntegration] Connection closed');
                    this.handleDisconnect();
                });

                this.ws.on('error', (error) => {
                    console.error('[AIIntegration] WebSocket error:', error);
                    this.status = ConnectionStatus.ERROR;
                    this.updateStatusBar();
                    reject(error);
                });

                // Timeout
                setTimeout(() => {
                    if (this.status === ConnectionStatus.CONNECTING) {
                        this.ws.close();
                        reject(new Error('Connection timeout'));
                    }
                }, 10000);
            });

        } catch (error) {
            console.error('[AIIntegration] Connection failed:', error);
            this.status = ConnectionStatus.ERROR;
            this.updateStatusBar();
            this.scheduleReconnect();
            return false;
        }
    }

    /**
     * Disconnect from AI Bridge
     */
    disconnect() {
        this.stopHeartbeat();
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this.status = ConnectionStatus.DISCONNECTED;
        this.updateStatusBar();
        this.emit('disconnected');
        
        console.log('[AIIntegration] Disconnected');
    }

    /**
     * Handle disconnection
     */
    handleDisconnect() {
        this.stopHeartbeat();
        this.status = ConnectionStatus.DISCONNECTED;
        this.updateStatusBar();
        this.emit('disconnected');
        this.scheduleReconnect();
    }

    /**
     * Schedule reconnection attempt
     */
    scheduleReconnect() {
        if (this.reconnectAttempts >= CONFIG.MAX_RECONNECT_ATTEMPTS) {
            console.log('[AIIntegration] Max reconnect attempts reached');
            this.status = ConnectionStatus.ERROR;
            this.updateStatusBar();
            return;
        }

        this.reconnectAttempts++;
        this.status = ConnectionStatus.RECONNECTING;
        this.updateStatusBar();

        const delay = CONFIG.RECONNECT_INTERVAL * Math.pow(1.5, this.reconnectAttempts - 1);
        console.log(`[AIIntegration] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);

        setTimeout(() => {
            this.connect();
        }, delay);
    }

    /**
     * Start heartbeat
     */
    startHeartbeat() {
        this.heartbeatTimer = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, CONFIG.HEARTBEAT_INTERVAL);
    }

    /**
     * Stop heartbeat
     */
    stopHeartbeat() {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    /**
     * Handle incoming message
     */
    handleMessage(data) {
        try {
            const message = JSON.parse(data.toString());
            
            switch (message.type) {
                case 'response':
                    this.handleResponse(message);
                    break;
                case 'stream':
                    this.handleStream(message);
                    break;
                case 'error':
                    this.handleError(message);
                    break;
                case 'status':
                    this.handleStatusUpdate(message);
                    break;
                case 'heartbeat':
                    // Heartbeat acknowledged
                    break;
                default:
                    console.log('[AIIntegration] Unknown message type:', message.type);
            }
            
            this.emit('message', message);
            
        } catch (error) {
            console.error('[AIIntegration] Failed to parse message:', error);
        }
    }

    /**
     * Handle AI response
     */
    handleResponse(message) {
        const { requestId, content, metadata } = message;
        
        const pending = this.pendingRequests.get(requestId);
        if (pending) {
            pending.resolve({ content, metadata });
            this.pendingRequests.delete(requestId);
        }
        
        this.emit('response', { content, metadata });
    }

    /**
     * Handle streaming response
     */
    handleStream(message) {
        const { requestId, chunk, done } = message;
        
        this.emit('stream', { requestId, chunk, done });
        
        if (done) {
            const pending = this.pendingRequests.get(requestId);
            if (pending) {
                pending.resolve({ done: true });
                this.pendingRequests.delete(requestId);
            }
        }
    }

    /**
     * Handle error
     */
    handleError(message) {
        const { requestId, error } = message;
        
        console.error('[AIIntegration] Error:', error);
        
        const pending = this.pendingRequests.get(requestId);
        if (pending) {
            pending.reject(new Error(error));
            this.pendingRequests.delete(requestId);
        }
        
        this.emit('error', error);
    }

    /**
     * Handle status update
     */
    handleStatusUpdate(message) {
        const { provider, status } = message;
        
        if (provider) {
            this.activeProvider = provider;
            this.context.globalState.update('aiProvider', provider);
        }
        
        this.emit('statusUpdate', message);
    }

    /**
     * Send message to AI
     */
    async sendMessage(message, options = {}) {
        const requestId = this.generateRequestId();
        
        const payload = {
            type: 'chat',
            requestId,
            sessionId: this.sessionId,
            message,
            provider: options.provider || this.activeProvider,
            context: options.context || {},
            stream: options.stream || false
        };

        if (this.status !== ConnectionStatus.CONNECTED) {
            // Queue message for later
            this.messageQueue.push(payload);
            console.log('[AIIntegration] Message queued (not connected)');
            return this.createPendingPromise(requestId);
        }

        return this.sendPayload(payload);
    }

    /**
     * Send payload through WebSocket
     */
    sendPayload(payload) {
        return new Promise((resolve, reject) => {
            const { requestId } = payload;
            
            // Set timeout
            const timeout = setTimeout(() => {
                this.pendingRequests.delete(requestId);
                reject(new Error('Request timeout'));
            }, CONFIG.MESSAGE_TIMEOUT);

            // Store pending request
            this.pendingRequests.set(requestId, {
                resolve: (result) => {
                    clearTimeout(timeout);
                    resolve(result);
                },
                reject: (error) => {
                    clearTimeout(timeout);
                    reject(error);
                }
            });

            // Send
            this.ws.send(JSON.stringify(payload));
        });
    }

    /**
     * Process queued messages
     */
    processMessageQueue() {
        while (this.messageQueue.length > 0) {
            const payload = this.messageQueue.shift();
            this.sendPayload(payload);
        }
    }

    /**
     * Create pending promise for queued messages
     */
    createPendingPromise(requestId) {
        return new Promise((resolve, reject) => {
            this.pendingRequests.set(requestId, { resolve, reject });
        });
    }

    /**
     * Generate unique request ID
     */
    generateRequestId() {
        return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Switch AI provider
     */
    async switchProvider() {
        const providers = Object.values(AIProvider);
        
        const selected = await vscode.window.showQuickPick(providers, {
            placeHolder: 'Select AI Provider',
            title: 'Switch AI Provider'
        });

        if (selected) {
            this.activeProvider = selected;
            this.context.globalState.update('aiProvider', selected);
            
            // Notify bridge service
            if (this.status === ConnectionStatus.CONNECTED) {
                this.ws.send(JSON.stringify({
                    type: 'switchProvider',
                    provider: selected
                }));
            }
            
            vscode.window.showInformationMessage(`Switched to ${selected} AI provider`);
        }
    }

    /**
     * Clear conversation history
     */
    async clearHistory() {
        const confirm = await vscode.window.showWarningMessage(
            'Clear all AI conversation history?',
            'Yes', 'No'
        );

        if (confirm === 'Yes') {
            this.sessionId = this.generateRequestId();
            this.context.globalState.update('aiSessionId', this.sessionId);
            
            if (this.status === ConnectionStatus.CONNECTED) {
                this.ws.send(JSON.stringify({
                    type: 'clearHistory',
                    sessionId: this.sessionId
                }));
            }
            
            vscode.window.showInformationMessage('AI conversation history cleared');
        }
    }

    /**
     * Show AI status
     */
    async showStatus() {
        const statusMessage = [
            `Status: ${this.status}`,
            `Provider: ${this.activeProvider || 'None'}`,
            `Session: ${this.sessionId || 'None'}`,
            `Pending Requests: ${this.pendingRequests.size}`,
            `Queued Messages: ${this.messageQueue.length}`
        ].join('\n');

        vscode.window.showInformationMessage(statusMessage, { modal: true });
    }

    /**
     * Update status bar
     */
    updateStatusBar() {
        const icons = {
            [ConnectionStatus.DISCONNECTED]: '$(circle-slash)',
            [ConnectionStatus.CONNECTING]: '$(sync~spin)',
            [ConnectionStatus.CONNECTED]: '$(check)',
            [ConnectionStatus.RECONNECTING]: '$(sync~spin)',
            [ConnectionStatus.ERROR]: '$(error)'
        };

        const colors = {
            [ConnectionStatus.DISCONNECTED]: 'statusBarItem.warningBackground',
            [ConnectionStatus.CONNECTING]: undefined,
            [ConnectionStatus.CONNECTED]: undefined,
            [ConnectionStatus.RECONNECTING]: 'statusBarItem.warningBackground',
            [ConnectionStatus.ERROR]: 'statusBarItem.errorBackground'
        };

        this.statusBarItem.text = `${icons[this.status]} AI: ${this.status}`;
        this.statusBarItem.backgroundColor = colors[this.status] 
            ? new vscode.ThemeColor(colors[this.status]) 
            : undefined;
        this.statusBarItem.tooltip = `AI Integration - ${this.status}\nClick for details`;
    }

    /**
     * Event handling
     */
    on(event, handler) {
        if (!this.eventHandlers.has(event)) {
            this.eventHandlers.set(event, []);
        }
        this.eventHandlers.get(event).push(handler);
    }

    off(event, handler) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            const index = handlers.indexOf(handler);
            if (index !== -1) {
                handlers.splice(index, 1);
            }
        }
    }

    emit(event, data) {
        const handlers = this.eventHandlers.get(event);
        if (handlers) {
            handlers.forEach(handler => {
                try {
                    handler(data);
                } catch (error) {
                    console.error(`[AIIntegration] Event handler error for ${event}:`, error);
                }
            });
        }
    }

    /**
     * Dispose resources
     */
    dispose() {
        this.disconnect();
        this.statusBarItem.dispose();
        this.pendingRequests.clear();
        this.eventHandlers.clear();
    }
}

/**
 * AI Chat Panel
 * WebView panel สำหรับแสดง UI การสนทนากับ AI
 */
class AIChatPanel {
    static currentPanel = null;
    static viewType = 'antigravityAIChat';

    constructor(panel, extensionUri, aiManager) {
        this.panel = panel;
        this.extensionUri = extensionUri;
        this.aiManager = aiManager;
        this.messages = [];
        this.disposables = [];

        // Set up panel
        this.panel.webview.options = {
            enableScripts: true,
            localResourceRoots: [extensionUri]
        };

        // Set HTML content
        this.panel.webview.html = this.getHtmlContent();

        // Handle messages from webview
        this.panel.webview.onDidReceiveMessage(
            message => this.handleWebviewMessage(message),
            null,
            this.disposables
        );

        // Handle panel disposal
        this.panel.onDidDispose(() => this.dispose(), null, this.disposables);

        // Listen to AI events
        this.aiManager.on('response', (data) => this.handleAIResponse(data));
        this.aiManager.on('stream', (data) => this.handleAIStream(data));
        this.aiManager.on('error', (error) => this.handleAIError(error));
    }

    static createOrShow(extensionUri, aiManager) {
        const column = vscode.window.activeTextEditor
            ? vscode.window.activeTextEditor.viewColumn
            : undefined;

        if (AIChatPanel.currentPanel) {
            AIChatPanel.currentPanel.panel.reveal(column);
            return;
        }

        const panel = vscode.window.createWebviewPanel(
            AIChatPanel.viewType,
            'AI Chat',
            column || vscode.ViewColumn.One,
            {
                enableScripts: true,
                retainContextWhenHidden: true
            }
        );

        AIChatPanel.currentPanel = new AIChatPanel(panel, extensionUri, aiManager);
    }

    handleWebviewMessage(message) {
        switch (message.type) {
            case 'sendMessage':
                this.sendMessage(message.content);
                break;
            case 'clearHistory':
                this.clearHistory();
                break;
            case 'switchProvider':
                this.aiManager.switchProvider();
                break;
        }
    }

    async sendMessage(content) {
        // Add user message to UI
        this.addMessage('user', content);

        try {
            // Send to AI
            const response = await this.aiManager.sendMessage(content);
            
            if (response && response.content) {
                this.addMessage('assistant', response.content);
            }
        } catch (error) {
            this.addMessage('error', `Error: ${error.message}`);
        }
    }

    addMessage(role, content) {
        this.messages.push({ role, content, timestamp: new Date() });
        
        this.panel.webview.postMessage({
            type: 'addMessage',
            role,
            content
        });
    }

    handleAIResponse(data) {
        // Response is handled in sendMessage
    }

    handleAIStream(data) {
        this.panel.webview.postMessage({
            type: 'streamChunk',
            chunk: data.chunk,
            done: data.done
        });
    }

    handleAIError(error) {
        this.addMessage('error', `AI Error: ${error}`);
    }

    clearHistory() {
        this.messages = [];
        this.panel.webview.postMessage({ type: 'clearMessages' });
        this.aiManager.clearHistory();
    }

    getHtmlContent() {
        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chat</title>
    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }
        body {
            font-family: var(--vscode-font-family);
            background: var(--vscode-editor-background);
            color: var(--vscode-editor-foreground);
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            padding: 12px 16px;
            background: var(--vscode-titleBar-activeBackground);
            border-bottom: 1px solid var(--vscode-panel-border);
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .header h2 {
            font-size: 14px;
            font-weight: 600;
        }
        .header-actions button {
            background: transparent;
            border: none;
            color: var(--vscode-button-foreground);
            cursor: pointer;
            padding: 4px 8px;
            margin-left: 8px;
            border-radius: 4px;
        }
        .header-actions button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .messages {
            flex: 1;
            overflow-y: auto;
            padding: 16px;
        }
        .message {
            margin-bottom: 16px;
            padding: 12px;
            border-radius: 8px;
            max-width: 85%;
        }
        .message.user {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            margin-left: auto;
        }
        .message.assistant {
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
        }
        .message.error {
            background: var(--vscode-inputValidation-errorBackground);
            border: 1px solid var(--vscode-inputValidation-errorBorder);
        }
        .message-content {
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        .message-time {
            font-size: 10px;
            opacity: 0.7;
            margin-top: 4px;
        }
        .input-area {
            padding: 16px;
            border-top: 1px solid var(--vscode-panel-border);
            display: flex;
            gap: 8px;
        }
        .input-area textarea {
            flex: 1;
            background: var(--vscode-input-background);
            border: 1px solid var(--vscode-input-border);
            color: var(--vscode-input-foreground);
            padding: 8px 12px;
            border-radius: 4px;
            resize: none;
            font-family: inherit;
            font-size: 13px;
            min-height: 40px;
            max-height: 120px;
        }
        .input-area textarea:focus {
            outline: none;
            border-color: var(--vscode-focusBorder);
        }
        .input-area button {
            background: var(--vscode-button-background);
            color: var(--vscode-button-foreground);
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            cursor: pointer;
            font-weight: 500;
        }
        .input-area button:hover {
            background: var(--vscode-button-hoverBackground);
        }
        .input-area button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }
        .typing-indicator {
            display: none;
            padding: 12px;
            color: var(--vscode-descriptionForeground);
        }
        .typing-indicator.active {
            display: block;
        }
        .typing-indicator span {
            animation: blink 1.4s infinite;
        }
        .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
        .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
        @keyframes blink {
            0%, 100% { opacity: 0.2; }
            50% { opacity: 1; }
        }
    </style>
</head>
<body>
    <div class="header">
        <h2>🤖 AI Assistant</h2>
        <div class="header-actions">
            <button onclick="switchProvider()">Switch Provider</button>
            <button onclick="clearHistory()">Clear</button>
        </div>
    </div>
    
    <div class="messages" id="messages">
        <div class="message assistant">
            <div class="message-content">Hello! I'm your AI assistant. How can I help you today?</div>
        </div>
    </div>
    
    <div class="typing-indicator" id="typing">
        AI is thinking<span>.</span><span>.</span><span>.</span>
    </div>
    
    <div class="input-area">
        <textarea 
            id="input" 
            placeholder="Type your message..." 
            rows="1"
            onkeydown="handleKeydown(event)"
        ></textarea>
        <button id="sendBtn" onclick="sendMessage()">Send</button>
    </div>

    <script>
        const vscode = acquireVsCodeApi();
        const messagesContainer = document.getElementById('messages');
        const input = document.getElementById('input');
        const sendBtn = document.getElementById('sendBtn');
        const typingIndicator = document.getElementById('typing');

        function sendMessage() {
            const content = input.value.trim();
            if (!content) return;

            vscode.postMessage({ type: 'sendMessage', content });
            input.value = '';
            input.style.height = 'auto';
            sendBtn.disabled = true;
            typingIndicator.classList.add('active');
        }

        function handleKeydown(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        }

        function switchProvider() {
            vscode.postMessage({ type: 'switchProvider' });
        }

        function clearHistory() {
            vscode.postMessage({ type: 'clearHistory' });
        }

        function addMessageToUI(role, content) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            const timeDiv = document.createElement('div');
            timeDiv.className = 'message-time';
            timeDiv.textContent = new Date().toLocaleTimeString();
            
            div.appendChild(contentDiv);
            div.appendChild(timeDiv);
            messagesContainer.appendChild(div);
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }

        // Handle messages from extension
        window.addEventListener('message', event => {
            const message = event.data;
            
            switch (message.type) {
                case 'addMessage':
                    addMessageToUI(message.role, message.content);
                    sendBtn.disabled = false;
                    typingIndicator.classList.remove('active');
                    break;
                case 'streamChunk':
                    // Handle streaming (future implementation)
                    break;
                case 'clearMessages':
                    messagesContainer.innerHTML = '';
                    addMessageToUI('assistant', 'Chat history cleared. How can I help you?');
                    break;
            }
        });

        // Auto-resize textarea
        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    </script>
</body>
</html>`;
    }

    dispose() {
        AIChatPanel.currentPanel = null;
        this.panel.dispose();
        this.disposables.forEach(d => d.dispose());
    }
}

// Export modules
module.exports = {
    AIIntegrationManager,
    AIChatPanel,
    ConnectionStatus,
    AIProvider
};
