/**
 * Inline Commands - Inline code suggestions and completions
 */

import * as vscode from 'vscode';
import { AIClient } from '../aiClient';

export function registerInlineCommands(
    context: vscode.ExtensionContext,
    aiClient: AIClient
): void {
    // Inline completion command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.inlineComplete', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const document = editor.document;
            const position = editor.selection.active;
            
            // Get context around cursor
            const _linePrefix = document.lineAt(position.line).text.substring(0, position.character);
            const _lineSuffix = document.lineAt(position.line).text.substring(position.character);
            
            // Get surrounding lines for context
            const startLine = Math.max(0, position.line - 10);
            const endLine = Math.min(document.lineCount - 1, position.line + 5);
            const contextBefore = document.getText(new vscode.Range(startLine, 0, position.line, position.character));
            const contextAfter = document.getText(new vscode.Range(position.line, position.character, endLine, document.lineAt(endLine).text.length));

            const prompt = `Complete the following ${document.languageId} code at the cursor position (marked with |):

\`\`\`${document.languageId}
${contextBefore}|${contextAfter}
\`\`\`

Provide only the code to insert at the cursor position, without explanation.`;

            try {
                vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Generating completion...',
                    cancellable: true
                }, async (progress, token) => {
                    const response = await aiClient.sendMessage(prompt, { type: 'code' });
                    
                    if (token.isCancellationRequested) {return;}

                    // Extract code from response
                    const code = extractCode(response.content);
                    
                    if (code) {
                        await editor.edit(editBuilder => {
                            editBuilder.insert(position, code);
                        });
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Completion failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        })
    );

    // Add documentation command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.addDocumentation', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showWarningMessage('Please select code to document');
                return;
            }

            const language = editor.document.languageId;
            const prompt = `Add documentation/comments to this ${language} code. Use the appropriate documentation style for ${language} (e.g., JSDoc for JavaScript/TypeScript, docstrings for Python).

\`\`\`${language}
${selection}
\`\`\`

Return only the documented code.`;

            try {
                vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Adding documentation...',
                    cancellable: true
                }, async (progress, token) => {
                    const response = await aiClient.sendMessage(prompt, { type: 'code' });
                    
                    if (token.isCancellationRequested) {return;}

                    const code = extractCode(response.content);
                    
                    if (code) {
                        await editor.edit(editBuilder => {
                            editBuilder.replace(editor.selection, code);
                        });
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Documentation failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        })
    );

    // Refactor code command
    context.subscriptions.push(
        vscode.commands.registerCommand('dlnk-ai.refactorCode', async () => {
            const editor = vscode.window.activeTextEditor;
            if (!editor) {
                vscode.window.showWarningMessage('No active editor');
                return;
            }

            const selection = editor.document.getText(editor.selection);
            if (!selection) {
                vscode.window.showWarningMessage('Please select code to refactor');
                return;
            }

            const refactorType = await vscode.window.showQuickPick([
                { label: 'Improve readability', value: 'readability' },
                { label: 'Optimize performance', value: 'performance' },
                { label: 'Add error handling', value: 'error-handling' },
                { label: 'Extract function', value: 'extract' },
                { label: 'Simplify logic', value: 'simplify' }
            ], {
                placeHolder: 'Select refactoring type'
            });

            if (!refactorType) {return;}

            const language = editor.document.languageId;
            const prompt = `Refactor this ${language} code to ${refactorType.label.toLowerCase()}:

\`\`\`${language}
${selection}
\`\`\`

Return only the refactored code.`;

            try {
                vscode.window.withProgress({
                    location: vscode.ProgressLocation.Notification,
                    title: 'Refactoring code...',
                    cancellable: true
                }, async (progress, token) => {
                    const response = await aiClient.sendMessage(prompt, { type: 'code' });
                    
                    if (token.isCancellationRequested) {return;}

                    const code = extractCode(response.content);
                    
                    if (code) {
                        await editor.edit(editBuilder => {
                            editBuilder.replace(editor.selection, code);
                        });
                    }
                });
            } catch (error) {
                vscode.window.showErrorMessage(`Refactoring failed: ${error instanceof Error ? error.message : 'Unknown error'}`);
            }
        })
    );
}

function extractCode(content: string): string {
    // Try to extract code from markdown code blocks
    const codeBlockMatch = content.match(/```[\w]*\n([\s\S]*?)```/);
    if (codeBlockMatch) {
        return codeBlockMatch[1].trim();
    }
    
    // Return content as-is if no code block found
    return content.trim();
}
