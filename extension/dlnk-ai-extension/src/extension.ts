/**
 * dLNk AI Extension - Main Entry Point
 * AI-Powered Code Assistant for dLNk IDE
 */

import * as vscode from 'vscode';
import { ChatPanelProvider } from './chatPanel';
import { AIClient } from './aiClient';
import { HistoryManager } from './historyManager';

let aiClient: AIClient;
let historyManager: HistoryManager;
let chatPanelProvider: ChatPanelProvider;

export function activate(context: vscode.ExtensionContext) {
    console.log('dLNk AI Extension is now active!');

    // Initialize components
    historyManager = new HistoryManager(context);
    aiClient = new AIClient(context);

    // Register Chat Panel Provider
    chatPanelProvider = new ChatPanelProvider(
        context.extensionUri,
        aiClient,
        historyManager
    );

    context.subscriptions.push(
        vscode.window.registerWebviewViewProvider(
            'dlnk-ai.chatView',
            chatPanelProvider,
            {
                webviewOptions: {
                    retainContextWhenHidden: true
                }
            }
        )
    );

    // Register Commands
    registerCommands(context);

    // Auto-connect if enabled
    const config = vscode.workspace.getConfiguration('dlnk-ai');
    if (config.get('autoConnect')) {
        aiClient.connect().catch(err => {
            console.log('Auto-connect failed:', err.message);
        });
    }

    // Status bar item
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    statusBarItem.command = 'dlnk-ai.openChat';
    updateStatusBar(statusBarItem, aiClient);
    statusBarItem.show();
    context.subscriptions.push(statusBarItem);

    // Update status bar on connection changes
    aiClient.onStatusChange(() => {
        updateStatusBar(statusBarItem, aiClient);
    });
}

function registerCommands(context: vscode.ExtensionContext) {
    // Open Chat Command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.openChat', () => {
            vscode.commands.executeCommand('dlnk-ai.chatView.focus');
        })
    );

    // Explain Code Command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.explainCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const selection = editor.document.getText(editor.selection);
                if (selection) {
                    const language = editor.document.languageId;
                    const prompt = `Explain this ${language} code:\n\`\`\`${language}\n${selection}\n\`\`\``;
                    await sendToChatAndFocus(prompt);
                } else {
                    vscode.window.showWarningMessage('Please select code to explain');
                }
            }
        })
    );

    // Generate Code Command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.generateCode', async () => {
            const prompt = await vscode.window.showInputBox({
                prompt: 'What code do you want to generate?',
                placeHolder: 'e.g., Create a function that sorts an array'
            });
            if (prompt) {
                await sendToChatAndFocus(`Generate code: ${prompt}`);
            }
        })
    );

    // Fix Code Command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.fixCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (editor) {
                const selection = editor.document.getText(editor.selection);
                if (selection) {
                    const language = editor.document.languageId;
                    const prompt = `Fix this ${language} code:\n\`\`\`${language}\n${selection}\n\`\`\``;
                    await sendToChatAndFocus(prompt);
                } else {
                    vscode.window.showWarningMessage('Please select code to fix');
                }
            }
        })
    );

    // Clear History Command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.clearHistory', async () => {
            const confirm = await vscode.window.showWarningMessage(
                'Clear all chat history?',
                'Yes',
                'No'
            );
            if (confirm === 'Yes') {
                historyManager.clearHistory();
                chatPanelProvider.clearChat();
                vscode.window.showInformationMessage('Chat history cleared');
            }
        })
    );

    // Export History Command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.exportHistory', async () => {
            const history = historyManager.getHistory();
            if (history.length === 0) {
                vscode.window.showWarningMessage('No chat history to export');
                return;
            }

            const uri = await vscode.window.showSaveDialog({
                defaultUri: vscode.Uri.file('dlnk-ai-history.json'),
                filters: { 'JSON': ['json'] }
            });

            if (uri) {
                const data = JSON.stringify(history, null, 2);
                await vscode.workspace.fs.writeFile(uri, Buffer.from(data, 'utf8'));
                vscode.window.showInformationMessage('Chat history exported successfully');
            }
        })
    );

    // Import History Command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.importHistory', async () => {
            const uri = await vscode.window.showOpenDialog({
                canSelectMany: false,
                filters: { 'JSON': ['json'] }
            });

            if (uri && uri[0]) {
                try {
                    const data = await vscode.workspace.fs.readFile(uri[0]);
                    const history = JSON.parse(data.toString());
                    historyManager.importHistory(history);
                    chatPanelProvider.refreshChat();
                    vscode.window.showInformationMessage('Chat history imported successfully');
                } catch (error) {
                    vscode.window.showErrorMessage('Failed to import chat history');
                }
            }
        })
    );
}

async function sendToChatAndFocus(message: string) {
    await vscode.commands.executeCommand('dlnk-ai.chatView.focus');
    chatPanelProvider.sendMessage(message);
}

function updateStatusBar(statusBarItem: vscode.StatusBarItem, client: AIClient) {
    const isConnected = client.isConnected();
    statusBarItem.text = isConnected ? '$(check) dLNk AI' : '$(circle-slash) dLNk AI';
    statusBarItem.tooltip = isConnected ? 'dLNk AI: Connected' : 'dLNk AI: Disconnected - Click to open chat';
    statusBarItem.backgroundColor = isConnected 
        ? undefined 
        : new vscode.ThemeColor('statusBarItem.warningBackground');
}

export function deactivate() {
    if (aiClient) {
        aiClient.disconnect();
    }
}
