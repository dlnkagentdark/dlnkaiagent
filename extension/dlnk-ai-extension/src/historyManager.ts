/**
 * History Manager - Manages conversation history
 * Stores chat history in VS Code globalState
 */

import * as vscode from 'vscode';

export interface ChatMessage {
    id: string;
    role: 'user' | 'assistant' | 'error' | 'system';
    content: string;
    timestamp: Date;
    metadata?: Record<string, unknown>;
}

const HISTORY_KEY = 'dlnk-ai.chatHistory';
const MAX_HISTORY_SIZE = 100;

export class HistoryManager {
    private context: vscode.ExtensionContext;
    private history: ChatMessage[] = [];

    constructor(context: vscode.ExtensionContext) {
        this.context = context;
        this.loadHistory();
    }

    /**
     * Add message to history
     */
    addMessage(message: ChatMessage): void {
        this.history.push({
            ...message,
            timestamp: new Date(message.timestamp)
        });

        // Trim history if too large
        if (this.history.length > MAX_HISTORY_SIZE) {
            this.history = this.history.slice(-MAX_HISTORY_SIZE);
        }

        this.saveHistory();
    }

    /**
     * Get all history
     */
    getHistory(): ChatMessage[] {
        return [...this.history];
    }

    /**
     * Get recent history (last N messages)
     */
    getRecentHistory(count: number = 10): ChatMessage[] {
        return this.history.slice(-count);
    }

    /**
     * Clear all history
     */
    clearHistory(): void {
        this.history = [];
        this.saveHistory();
    }

    /**
     * Import history from external source
     */
    importHistory(messages: ChatMessage[]): void {
        // Validate and convert timestamps
        const validMessages = messages
            .filter(msg => msg.id && msg.role && msg.content)
            .map(msg => ({
                ...msg,
                timestamp: new Date(msg.timestamp)
            }));

        this.history = validMessages.slice(-MAX_HISTORY_SIZE);
        this.saveHistory();
    }

    /**
     * Export history
     */
    exportHistory(): ChatMessage[] {
        return this.history.map(msg => ({
            ...msg,
            timestamp: msg.timestamp
        }));
    }

    /**
     * Get message by ID
     */
    getMessage(id: string): ChatMessage | undefined {
        return this.history.find(msg => msg.id === id);
    }

    /**
     * Delete message by ID
     */
    deleteMessage(id: string): boolean {
        const index = this.history.findIndex(msg => msg.id === id);
        if (index !== -1) {
            this.history.splice(index, 1);
            this.saveHistory();
            return true;
        }
        return false;
    }

    /**
     * Search history
     */
    searchHistory(query: string): ChatMessage[] {
        const lowerQuery = query.toLowerCase();
        return this.history.filter(msg => 
            msg.content.toLowerCase().includes(lowerQuery)
        );
    }

    /**
     * Get conversation context for AI
     */
    getContextForAI(maxMessages: number = 10): Array<{ role: string; content: string }> {
        return this.history
            .filter(msg => msg.role === 'user' || msg.role === 'assistant')
            .slice(-maxMessages)
            .map(msg => ({
                role: msg.role,
                content: msg.content
            }));
    }

    // Private methods

    private loadHistory(): void {
        try {
            const stored = this.context.globalState.get<string>(HISTORY_KEY);
            if (stored) {
                const parsed = JSON.parse(stored);
                this.history = parsed.map((msg: ChatMessage) => ({
                    ...msg,
                    timestamp: new Date(msg.timestamp)
                }));
            }
        } catch (error) {
            console.error('[HistoryManager] Failed to load history:', error);
            this.history = [];
        }
    }

    private saveHistory(): void {
        try {
            const data = JSON.stringify(this.history);
            this.context.globalState.update(HISTORY_KEY, data);
        } catch (error) {
            console.error('[HistoryManager] Failed to save history:', error);
        }
    }
}
