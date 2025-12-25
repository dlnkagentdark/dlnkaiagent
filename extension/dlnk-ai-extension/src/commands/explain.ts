/**
 * Explain Commands - Code explanation and analysis
 */

import * as vscode from 'vscode';
import { AIClient } from '../aiClient';

export function registerExplainCommands(
    context: vscode.ExtensionContext,
    aiClient: AIClient
): void {
    // Explain code in hover
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.explainInHover', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {return;}

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showWarningMessage('Please select code to explain');
                return;
            }

            const language = editor.document.languageId;
            const prompt = `Briefly explain this ${language} code in 2-3 sentences:

\`\`\`${language}
${selection}
\`\`\``;

            try {
                const response = await aiClient.sendMessage(prompt, { type: 'explain' });
                
                // Show in information message
                vscode.window.showInformationMessage(response.content, { modal: false });
            } catch (error) {
                vscode.window.showErrorMessage(`Explanation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        })
    );

    // Detailed explanation in panel
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.explainDetailed', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {return;}

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showWarningMessage('Please select code to explain');
                return;
            }

            const language = editor.document.languageId;
            const prompt = `Provide a detailed explanation of this ${language} code:

\`\`\`${language}
${selection}
\`\`\`

Include:
1. What the code does
2. How it works step by step
3. Key concepts used
4. Potential improvements or issues`;

            // Send to chat panel
            vscode.commands.executeCommand('dlnk-ai.chatView.focus');
            
            // The chat panel will handle the message
            vscode.commands.executeCommand('dlnk-ai.sendToChat', prompt);
        })
    );

    // Find bugs command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.findBugs', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {return;}

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showWarningMessage('Please select code to analyze');
                return;
            }

            const language = editor.document.languageId;
            const prompt = `Analyze this ${language} code for potential bugs, issues, and improvements:

\`\`\`${language}
${selection}
\`\`\`

List any:
1. Bugs or errors
2. Security vulnerabilities
3. Performance issues
4. Code style problems
5. Suggested fixes`;

            try {
                vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Analyzing code...',
                    cancellable: true
                }, async (progress, token) => {
                    const response = await aiClient.sendMessage(prompt, { type: 'explain' });
                    
                    if (token.isCancellationRequested) {return;}

                    // Show in output channel
                    const outputChannel = vscode.window.createOutputChannel('dLNk AI Analysis');
                    outputChannel.clear();
                    outputChannel.appendLine('=== Code Analysis Results ===\n');
                    outputChannel.appendLine(response.content);
                    outputChannel.show();
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        })
    );

    // Generate tests command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.generateTests', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {return;}

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showWarningMessage('Please select code to generate tests for');
                return;
            }

            const language = editor.document.languageId;
            
            // Determine test framework based on language
            const testFrameworks: Record<string, string> = {
                'typescript': 'Jest',
                'javascript': 'Jest',
                'python': 'pytest',
                'java': 'JUnit',
                'csharp': 'NUnit',
                'go': 'testing package',
                'rust': 'built-in test framework'
            };
            
            const framework = testFrameworks[language] || 'appropriate test framework';

            const prompt = `Generate unit tests for this ${language} code using ${framework}:

\`\`\`${language}
${selection}
\`\`\`

Include:
1. Test for normal cases
2. Edge cases
3. Error cases
4. Mocking if needed`;

            try {
                vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Generating tests...',
                    cancellable: true
                }, async (progress, token) => {
                    const response = await aiClient.sendMessage(prompt, { type: 'code' });
                    
                    if (token.isCancellationRequested) {return;}

                    // Extract code and create new file
                    const code = extractCode(response.content);
                    
                    if (code) {
                        const doc = await vscode.workspace.openTextDocument({
                            content: code,
                            language: language
                        });
                        await vscode.window.showTextDocument(doc, vscode.ViewColumn.Beside);
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Test generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        })
    );

    // Explain error command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.explainError', async () => {
            // Get text from clipboard (user can copy error message)
            const errorText = await vscode.env.clipboard.readText();
            
            if (!errorText) {
                const input = await vscode.window.showInputBox({
                    prompt: 'Paste the error message',
                    placeHolder: 'Error: ...'
                });
                
                if (!input) {return;}
                
                await explainError(input, aiClient);
            } else {
                await explainError(errorText, aiClient);
            }
        })
    );
}

async function explainError(errorText: string, aiClient: AIClient): Promise<void> {
    const prompt = `Explain this error and suggest how to fix it:

\`\`\`
${errorText}
\`\`\`

Include:
1. What the error means
2. Common causes
3. How to fix it
4. Example fix if applicable`;

    try {
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Analyzing error...',
            cancellable: true
        }, async (progress, token) => {
            const response = await aiClient.sendMessage(prompt, { type: 'explain' });
            
            if (token.isCancellationRequested) {return;}

            // Show in output channel
            const outputChannel = vscode.window.createOutputChannel('dLNk AI Error Analysis');
            outputChannel.clear();
            outputChannel.appendLine('=== Error Analysis ===\n');
            outputChannel.appendLine(response.content);
            outputChannel.show();
        });
    } catch (error) {
        vscode.window.showErrorMessage(`Error analysis failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
    }
}

function extractCode(content: string): string {
    const codeBlockMatch = content.match(/```[\w]*\n([\s\S]*?)```/);
    if (codeBlockMatch) {
        return codeBlockMatch[1].trim();
    }
    return content.trim();
}
