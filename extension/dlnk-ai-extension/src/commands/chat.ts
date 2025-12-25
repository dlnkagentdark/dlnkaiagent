/**
 * Chat Commands - Command handlers for chat functionality
 */

import * as vscode from 'vscode';
import { AIClient } from '../aiClient';
import { HistoryManager } from '../historyManager';

export function registerChatCommands(
    context: vscode.ExtensionContext,
    aiClient: AIClient,
    historyManager: HistoryManager
): void {
    // Quick chat command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.quickChat', async () => {
            const input = await vscode.window.showInputBox({
                prompt: 'Ask dLNk AI',
                placeHolder: 'Type your question...'
            });

            if (input) {
                try {
                    const response = await aiClient.sendMessage(input);
                    
                    // Show response in notification
                    const action = await vscode.window.showInformationMessage(
                        truncate(response.content, 200),
                        'Copy',
                        'Open Chat'
                    );

                    if (action === 'Copy') {
                        await vscode.env.clipboard.writeText(response.content);
                    } else if (action === 'Open Chat') {
                        vscode.commands.executeCommand('dlnk-ai.chatView.focus');
                    }
                } catch (error) {
                    vscode.window.showErrorMessage(`AI Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
                }
            }
        })
    );

    // New chat session
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.newSession', () => {
            historyManager.clearHistory();
            vscode.window.showInformationMessage('Started new chat session');
        })
    );

    // Show chat history
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.showHistory', async () => {
            const history = historyManager.getHistory();
            
            if (history.length === 0) {
                vscode.window.showInformationMessage('No chat history');
                return;
            }

            const items = history
                .filter(msg => msg.role === 'user')
                .map(msg => ({
                    label: truncate(msg.content, 50),
                    description: new Date(msg.timestamp).toLocaleString(),
                    detail: msg.content
                }));

            const selected = await vscode.window.showQuickPick(items, {
                placeHolder: 'Select a conversation',
                matchOnDetail: true
            });

            if (selected) {
                // Focus chat and show selected conversation
                vscode.commands.executeCommand('dlnk-ai.chatView.focus');
            }
        })
    );
}

function truncate(text: string, maxLength: number): string {
    if (text.length <= maxLength) {return text;}
    return text.substring(0, maxLength - 3) + '...';
}
