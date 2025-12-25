/**
 * AI Client - WebSocket + REST API Client for AI Bridge
 * Handles communication with dLNk AI Bridge Service
 */

import * as vscode from 'vscode';
import WebSocket from 'ws';
import * as http from 'http';
import * as https from 'https';

export interface AIMessage {
    id: string;
    type: 'chat' | 'code' | 'explain' | 'fix';
    message: string;
    context?: Record<string, unknown>;
    stream?: boolean;
}

export interface AIResponse {
    id: string;
    content: string;
    done: boolean;
    metadata?: Record<string, unknown>;
}

type StatusChangeCallback = (connected: boolean) => void;
type MessageCallback = (response: AIResponse) => void;
type StreamCallback = (chunk: string, done: boolean) => void;

export class AIClient {
    private ws: WebSocket | null = null;
    private context: vscode.ExtensionContext;
    private messageCallbacks: Map<string, { resolve: (value: AIResponse) => void; reject: (error: Error) => void }> = new Map();
    private streamCallbacks: Map<string, StreamCallback> = new Map();
    private statusChangeCallbacks: StatusChangeCallback[] = [];
    private reconnectAttempts = 0;
    private reconnectTimer: NodeJS.Timeout | null = null;
    private heartbeatTimer: NodeJS.Timeout | null = null;
    private messageQueue: AIMessage[] = [];
    private _isConnected = false;

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
    }

    /**
     * Connect to AI Bridge WebSocket Server
     */
    async connect(): Promise<void> {
        const config = vscode.workspace.getConfiguration('dlnk-ai');
        const serverUrl = config.get<string>('serverUrl') || 'ws://localhost:8765';

        return new Promise((resolve, reject) => {
            try {
                console.log(`[AIClient] Connecting to ${serverUrl}...`);
                this.ws = new WebSocket(serverUrl);

                this.ws.on('open', () => {
                    console.log('[AIClient] Connected to dLNk AI Server');
                    this._isConnected = true;
                    this.reconnectAttempts = 0;
                    this.notifyStatusChange(true);
                    this.startHeartbeat();
                    this.processMessageQueue();
                    resolve();
                });

                this.ws.on('message', (data: WebSocket.Data) => {
                    this.handleMessage(data.toString());
                });

                this.ws.on('close', () => {
                    console.log('[AIClient] Disconnected from dLNk AI Server');
                    this._isConnected = false;
                    this.notifyStatusChange(false);
                    this.stopHeartbeat();
                    this.attemptReconnect();
                });

                this.ws.on('error', (error) => {
                    console.error('[AIClient] WebSocket error:', error);
                    reject(error);
                });

                // Connection timeout
                setTimeout(() => {
                    if (!this._isConnected) {
                        this.ws?.close();
                        reject(new Error('Connection timeout'));
                    }
                }, 10000);

            } catch (error) {
                console.error('[AIClient] Failed to connect:', error);
                this.attemptReconnect();
                reject(error);
            }
        });
    }

    /**
     * Disconnect from AI Bridge
     */
    disconnect(): void {
        this.stopHeartbeat();
        this.stopReconnect();
        
        if (this.ws) {
            this.ws.close();
            this.ws = null;
        }
        
        this._isConnected = false;
        this.notifyStatusChange(false);
        console.log('[AIClient] Disconnected');
    }

    /**
     * Send message to AI
     */
    async sendMessage(message: string, options: { stream?: boolean; type?: string; context?: Record<string, unknown> } = {}): Promise<AIResponse> {
        const messageId = this.generateMessageId();
        const config = vscode.workspace.getConfiguration('dlnk-ai');
        const useStream = options.stream ?? config.get<boolean>('streamResponse', true);

        const payload: AIMessage = {
            id: messageId,
            type: (options.type as AIMessage['type']) || 'chat',
            message: message,
            context: options.context,
            stream: useStream
        };

        if (!this._isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            // Queue message for later
            this.messageQueue.push(payload);
            console.log('[AIClient] Message queued (not connected)');
            
            // Try to connect
            this.connect().catch(() => {});
            
            return new Promise((resolve, reject) => {
                this.messageCallbacks.set(messageId, { resolve, reject });
                
                // Timeout
                setTimeout(() => {
                    if (this.messageCallbacks.has(messageId)) {
                        this.messageCallbacks.delete(messageId);
                        reject(new Error('Request timeout - server not available'));
                    }
                }, 60000);
            });
        }

        return this.sendPayload(payload);
    }

    /**
     * Send message with streaming callback
     */
    async sendMessageWithStream(message: string, onStream: StreamCallback, options: { type?: string; context?: Record<string, unknown> } = {}): Promise<void> {
        const messageId = this.generateMessageId();

        const payload: AIMessage = {
            id: messageId,
            type: (options.type as AIMessage['type']) || 'chat',
            message: message,
            context: options.context,
            stream: true
        };

        this.streamCallbacks.set(messageId, onStream);

        if (!this._isConnected || !this.ws || this.ws.readyState !== WebSocket.OPEN) {
            this.messageQueue.push(payload);
            console.log('[AIClient] Stream message queued (not connected)');
            this.connect().catch(() => {});
            return;
        }

        this.ws.send(JSON.stringify(payload));
    }

    /**
     * Send REST API request (fallback)
     */
    async sendRestRequest(message: string): Promise<AIResponse> {
        const config = vscode.workspace.getConfiguration('dlnk-ai');
        const apiUrl = config.get<string>('apiUrl') || 'http://localhost:8766/api';

        return new Promise((resolve, reject) => {
            const url = new URL(`${apiUrl}/chat`);
            const isHttps = url.protocol === 'https:';
            const client = isHttps ? https : http;

            const postData = JSON.stringify({ message });
            
            const options = {
                hostname: url.hostname,
                port: url.port || (isHttps ? 443 : 80),
                path: url.pathname,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(postData)
                }
            };

            const req = client.request(options, (res) => {
                let data = '';
                res.on('data', (chunk) => { data += chunk; });
                res.on('end', () => {
                    try {
                        const response = JSON.parse(data);
                        resolve({
                            id: this.generateMessageId(),
                            content: response.content || response.message || data,
                            done: true,
                            metadata: response.metadata
                        });
                    } catch {
                        resolve({
                            id: this.generateMessageId(),
                            content: data,
                            done: true
                        });
                    }
                });
            });

            req.on('error', (error) => {
                reject(error);
            });

            req.setTimeout(60000, () => {
                req.destroy();
                reject(new Error('Request timeout'));
            });

            req.write(postData);
            req.end();
        });
    }

    /**
     * Check connection status
     */
    isConnected(): boolean {
        return this._isConnected && this.ws !== null && this.ws.readyState === WebSocket.OPEN;
    }

    /**
     * Register status change callback
     */
    onStatusChange(callback: StatusChangeCallback): void {
        this.statusChangeCallbacks.push(callback);
    }

    /**
     * Register message callback
     */
    onMessage(messageId: string, callback: MessageCallback): void {
        // This is handled via promises
    }

    // Private methods

    private sendPayload(payload: AIMessage): Promise<AIResponse> {
        return new Promise((resolve, reject) => {
            const { id: messageId } = payload;

            // Set timeout
            const timeout = setTimeout(() => {
                this.messageCallbacks.delete(messageId);
                this.streamCallbacks.delete(messageId);
                reject(new Error('Request timeout'));
            }, 60000);

            // Store callback
            this.messageCallbacks.set(messageId, {
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
            this.ws!.send(JSON.stringify(payload));
        });
    }

    private handleMessage(data: string): void {
        try {
            const response = JSON.parse(data);
            
            switch (response.type) {
                case 'response':
                    this.handleResponse(response);
                    break;
                case 'stream':
                    this.handleStream(response);
                    break;
                case 'error':
                    this.handleError(response);
                    break;
                case 'heartbeat':
                    // Heartbeat acknowledged
                    break;
                default:
                    console.log('[AIClient] Unknown message type:', response.type);
            }
        } catch (error) {
            console.error('[AIClient] Failed to parse message:', error);
        }
    }

    private handleResponse(response: { id: string; content: string; metadata?: Record<string, unknown> }): void {
        const callback = this.messageCallbacks.get(response.id);
        if (callback) {
            callback.resolve({
                id: response.id,
                content: response.content,
                done: true,
                metadata: response.metadata
            });
            this.messageCallbacks.delete(response.id);
        }
    }

    private handleStream(response: { id: string; chunk: string; done: boolean }): void {
        const streamCallback = this.streamCallbacks.get(response.id);
        if (streamCallback) {
            streamCallback(response.chunk, response.done);
            
            if (response.done) {
                this.streamCallbacks.delete(response.id);
                
                // Also resolve the message callback if exists
                const callback = this.messageCallbacks.get(response.id);
                if (callback) {
                    callback.resolve({
                        id: response.id,
                        content: response.chunk,
                        done: true
                    });
                    this.messageCallbacks.delete(response.id);
                }
            }
        }
    }

    private handleError(response: { id: string; error: string }): void {
        const callback = this.messageCallbacks.get(response.id);
        if (callback) {
            callback.reject(new Error(response.error));
            this.messageCallbacks.delete(response.id);
        }
        this.streamCallbacks.delete(response.id);
    }

    private attemptReconnect(): void {
        const config = vscode.workspace.getConfiguration('dlnk-ai');
        const maxAttempts = config.get<number>('maxReconnectAttempts', 5);
        const baseInterval = config.get<number>('reconnectInterval', 5000);

        if (this.reconnectAttempts >= maxAttempts) {
            console.log('[AIClient] Max reconnect attempts reached');
            return;
        }

        this.reconnectAttempts++;
        const delay = baseInterval * Math.pow(1.5, this.reconnectAttempts - 1);
        
        console.log(`[AIClient] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${maxAttempts})`);

        this.reconnectTimer = setTimeout(() => {
            this.connect().catch(() => {});
        }, delay);
    }

    private stopReconnect(): void {
        if (this.reconnectTimer) {
            clearTimeout(this.reconnectTimer);
            this.reconnectTimer = null;
        }
        this.reconnectAttempts = 0;
    }

    private startHeartbeat(): void {
        this.heartbeatTimer = setInterval(() => {
            if (this.ws && this.ws.readyState === WebSocket.OPEN) {
                this.ws.send(JSON.stringify({ type: 'heartbeat' }));
            }
        }, 30000);
    }

    private stopHeartbeat(): void {
        if (this.heartbeatTimer) {
            clearInterval(this.heartbeatTimer);
            this.heartbeatTimer = null;
        }
    }

    private processMessageQueue(): void {
        while (this.messageQueue.length > 0) {
            const payload = this.messageQueue.shift();
            if (payload) {
                this.sendPayload(payload).catch(err => {
                    console.error('[AIClient] Failed to send queued message:', err);
                });
            }
        }
    }

    private notifyStatusChange(connected: boolean): void {
        this.statusChangeCallbacks.forEach(callback => {
            try {
                callback(connected);
            } catch (error) {
                console.error('[AIClient] Status change callback error:', error);
            }
        });
    }

    private generateMessageId(): string {
        return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }
}
