/**
 * Chat Panel - Webview Provider for AI Chat Interface
 * Provides the main chat UI in VS Code sidebar
 */

import * as vscode from 'vscode';
import { AIClient } from './aiClient';
import { HistoryManager, ChatMessage } from './historyManager';

export class ChatPanelProvider implements vscode.WebviewViewProvider {
    public static readonly viewType = 'dlnk-ai.chatView';
    
    private _view?: vscode.WebviewView;
    private _extensionUri: vscode.Uri;
    private _aiClient: AIClient;
    private _historyManager: HistoryManager;
    private _currentStreamContent = '';

    constructor(
        extensionUri: vscode.Uri,
        aiClient: AIClient,
        historyManager: HistoryManager
    ) {
        this._extensionUri = extensionUri;
        this._aiClient = aiClient;
        this._historyManager = historyManager;
    }

    public resolveWebviewView(
        webviewView: vscode.WebviewView,
        context: vscode.WebviewViewResolveContext,
        _token: vscode.CancellationToken
    ) {
        this._view = webviewView;

        webviewView.webview.options = {
            enableScripts: true,
            localResourceRoots: [this._extensionUri]
        };

        webviewView.webview.html = this._getHtmlContent(webviewView.webview);

        // Handle messages from webview
        webviewView.webview.onDidReceiveMessage(async (message) => {
            switch (message.type) {
                case 'sendMessage':
                    await this.handleUserMessage(message.content);
                    break;
                case 'clearHistory':
                    this.clearChat();
                    break;
                case 'copyCode':
                    await vscode.env.clipboard.writeText(message.code);
                    vscode.window.showInformationMessage('Code copied to clipboard');
                    break;
                case 'insertCode':
                    await this.insertCodeToEditor(message.code);
                    break;
                case 'ready':
                    this.loadHistory();
                    break;
            }
        });

        // Listen to AI client status changes
        this._aiClient.onStatusChange((connected) => {
            this.updateConnectionStatus(connected);
        });
    }

    /**
     * Send message from external command
     */
    public async sendMessage(message: string): Promise<void> {
        if (this._view) {
            await this.handleUserMessage(message);
        }
    }

    /**
     * Clear chat
     */
    public clearChat(): void {
        this._historyManager.clearHistory();
        if (this._view) {
            this._view.webview.postMessage({ type: 'clearMessages' });
        }
    }

    /**
     * Refresh chat with history
     */
    public refreshChat(): void {
        this.loadHistory();
    }

    // Private methods

    private async handleUserMessage(content: string): Promise<void> {
        if (!content.trim()) return;

        // Add user message to UI and history
        const userMessage: ChatMessage = {
            id: Date.now().toString(),
            role: 'user',
            content: content,
            timestamp: new Date()
        };
        
        this._historyManager.addMessage(userMessage);
        this.postMessage({ type: 'addMessage', role: 'user', content: content });
        
        // Show typing indicator
        this.postMessage({ type: 'setTyping', typing: true });

        try {
            const config = vscode.workspace.getConfiguration('dlnk-ai');
            const useStream = config.get<boolean>('streamResponse', true);

            if (useStream) {
                // Streaming response
                this._currentStreamContent = '';
                const assistantMessageId = Date.now().toString();
                
                this.postMessage({ type: 'startStream', messageId: assistantMessageId });

                await this._aiClient.sendMessageWithStream(
                    content,
                    (chunk, done) => {
                        this._currentStreamContent += chunk;
                        this.postMessage({ 
                            type: 'streamChunk', 
                            chunk: chunk,
                            done: done,
                            messageId: assistantMessageId
                        });

                        if (done) {
                            // Save to history
                            const assistantMessage: ChatMessage = {
                                id: assistantMessageId,
                                role: 'assistant',
                                content: this._currentStreamContent,
                                timestamp: new Date()
                            };
                            this._historyManager.addMessage(assistantMessage);
                            this._currentStreamContent = '';
                        }
                    }
                );
            } else {
                // Non-streaming response
                const response = await this._aiClient.sendMessage(content);
                
                const assistantMessage: ChatMessage = {
                    id: response.id,
                    role: 'assistant',
                    content: response.content,
                    timestamp: new Date()
                };
                
                this._historyManager.addMessage(assistantMessage);
                this.postMessage({ type: 'addMessage', role: 'assistant', content: response.content });
            }
        } catch (error) {
            const errorMessage = error instanceof Error ? error.message : 'Unknown error';
            this.postMessage({ type: 'addMessage', role: 'error', content: `Error: ${errorMessage}` });
        } finally {
            this.postMessage({ type: 'setTyping', typing: false });
        }
    }

    private loadHistory(): void {
        const history = this._historyManager.getHistory();
        if (this._view) {
            this._view.webview.postMessage({ type: 'loadHistory', messages: history });
        }
        this.updateConnectionStatus(this._aiClient.isConnected());
    }

    private updateConnectionStatus(connected: boolean): void {
        this.postMessage({ type: 'connectionStatus', connected: connected });
    }

    private async insertCodeToEditor(code: string): Promise<void> {
        const editor = vscode.window.activeTextEditor;
        if (editor) {
            await editor.edit((editBuilder) => {
                editBuilder.insert(editor.selection.active, code);
            });
        } else {
            // Create new file with code
            const doc = await vscode.workspace.openTextDocument({ content: code });
            await vscode.window.showTextDocument(doc);
        }
    }

    private postMessage(message: unknown): void {
        if (this._view) {
            this._view.webview.postMessage(message);
        }
    }

    private _getHtmlContent(webview: vscode.Webview): string {
        const styleUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.css')
        );
        const scriptUri = webview.asWebviewUri(
            vscode.Uri.joinPath(this._extensionUri, 'media', 'chat.js')
        );

        const nonce = this.getNonce();

        return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource} 'unsafe-inline'; script-src 'nonce-${nonce}'; img-src ${webview.cspSource} data:;">
    <link href="${styleUri}" rel="stylesheet">
    <title>dLNk AI Chat</title>
</head>
<body>
    <div class="chat-container">
        <div class="chat-header">
            <div class="header-title">
                <span class="logo">🤖</span>
                <span>dLNk AI</span>
            </div>
            <div class="header-status">
                <span class="status-dot disconnected" id="statusDot"></span>
                <span class="status-text" id="statusText">Disconnected</span>
            </div>
        </div>
        
        <div class="messages-container" id="messagesContainer">
            <div class="welcome-message">
                <div class="welcome-icon">🚀</div>
                <h3>Welcome to dLNk AI</h3>
                <p>Your AI-powered code assistant. Ask me anything about coding!</p>
                <div class="quick-actions">
                    <button class="quick-action" data-action="explain">Explain Code</button>
                    <button class="quick-action" data-action="generate">Generate Code</button>
                    <button class="quick-action" data-action="fix">Fix Code</button>
                </div>
            </div>
        </div>
        
        <div class="typing-indicator" id="typingIndicator">
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-text">AI is thinking...</span>
        </div>
        
        <div class="input-container">
            <textarea 
                id="messageInput" 
                placeholder="Ask me anything..." 
                rows="1"
            ></textarea>
            <button id="sendButton" class="send-button" title="Send message">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M1.724 1.053a.5.5 0 0 0-.714.545l1.403 4.85a.5.5 0 0 0 .397.354l5.69.953c.268.053.268.437 0 .49l-5.69.953a.5.5 0 0 0-.397.354l-1.403 4.85a.5.5 0 0 0 .714.545l13-6.5a.5.5 0 0 0 0-.894l-13-6.5z"/>
                </svg>
            </button>
        </div>
    </div>
    
    <script nonce="${nonce}" src="${scriptUri}"></script>
</body>
</html>`;
    }

    private getNonce(): string {
        let text = '';
        const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
        for (let i = 0; i < 32; i++) {
            text += possible.charAt(Math.floor(Math.random() * possible.length));
        }
        return text;
    }
}
