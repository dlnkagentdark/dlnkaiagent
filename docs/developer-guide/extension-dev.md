# 🧩 Extension Development

คู่มือการพัฒนา Extension สำหรับ dLNk IDE

---

## 📋 Overview

dLNk IDE รองรับ VS Code Extensions ทั้งหมด รวมถึง Extensions ที่พัฒนาเฉพาะสำหรับ dLNk

---

## 🚀 Quick Start

### 1. สร้าง Extension ใหม่

```bash
# ติดตั้ง Yeoman และ VS Code Extension Generator
npm install -g yo generator-code

# สร้าง Extension
yo code

# เลือก:
# - New Extension (TypeScript)
# - Extension name: my-dlnk-extension
# - Identifier: my-dlnk-extension
# - Description: My dLNk Extension
```

### 2. โครงสร้างโปรเจ็ค

```
my-dlnk-extension/
├── src/
│   └── extension.ts      # Entry point
├── package.json          # Extension manifest
├── tsconfig.json         # TypeScript config
└── .vscode/
    └── launch.json       # Debug config
```

### 3. Extension Entry Point

```typescript
// src/extension.ts
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    console.log('My dLNk Extension is now active!');
    
    // Register command
    let disposable = vscode.commands.registerCommand('myExtension.helloWorld', () => {
        vscode.window.showInformationMessage('Hello from dLNk!');
    });
    
    context.subscriptions.push(disposable);
}

export function deactivate() {}
```

### 4. Package.json

```json
{
    "name": "my-dlnk-extension",
    "displayName": "My dLNk Extension",
    "description": "My custom extension for dLNk IDE",
    "version": "0.0.1",
    "engines": {
        "vscode": "^1.85.0"
    },
    "categories": ["Other"],
    "activationEvents": [],
    "main": "./out/extension.js",
    "contributes": {
        "commands": [
            {
                "command": "myExtension.helloWorld",
                "title": "Hello World"
            }
        ]
    },
    "scripts": {
        "vscode:prepublish": "npm run compile",
        "compile": "tsc -p ./",
        "watch": "tsc -watch -p ./",
        "pretest": "npm run compile"
    },
    "devDependencies": {
        "@types/vscode": "^1.85.0",
        "@types/node": "18.x",
        "typescript": "^5.3.0"
    }
}
```

### 5. Build และ Run

```bash
# Build
npm run compile

# Run ใน Extension Development Host
# กด F5 ใน VS Code/dLNk IDE
```

---

## 🔌 dLNk-Specific APIs

### Access dLNk AI

```typescript
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
    // Get dLNk Extension API
    const dlnkExtension = vscode.extensions.getExtension('dlnk.dlnk-ai');
    
    if (dlnkExtension) {
        const dlnkApi = dlnkExtension.exports;
        
        // Use AI Chat
        dlnkApi.chat('How do I use this API?').then(response => {
            console.log(response);
        });
        
        // Get completion
        dlnkApi.complete('def hello(', 'python').then(completion => {
            console.log(completion);
        });
    }
}
```

### dLNk API Interface

```typescript
interface DLNKApi {
    // Chat with AI
    chat(message: string, context?: ChatContext): Promise<string>;
    
    // Get code completion
    complete(prefix: string, language: string): Promise<string>;
    
    // Explain code
    explain(code: string, language: string): Promise<string>;
    
    // Refactor code
    refactor(code: string, instruction: string): Promise<string>;
    
    // Check license status
    getLicenseStatus(): Promise<LicenseStatus>;
    
    // Events
    onChatMessage: vscode.Event<ChatMessage>;
    onLicenseChange: vscode.Event<LicenseStatus>;
}

interface ChatContext {
    file?: string;
    language?: string;
    selection?: string;
    history?: ChatMessage[];
}

interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}

interface LicenseStatus {
    valid: boolean;
    type: 'trial' | 'standard' | 'pro' | 'enterprise';
    expiresAt: Date;
    features: string[];
}
```

---

## 🎨 UI Components

### Webview Panel

```typescript
import * as vscode from 'vscode';

export function createWebviewPanel(context: vscode.ExtensionContext) {
    const panel = vscode.window.createWebviewPanel(
        'myPanel',
        'My Panel',
        vscode.ViewColumn.One,
        {
            enableScripts: true,
            retainContextWhenHidden: true
        }
    );
    
    panel.webview.html = getWebviewContent();
    
    // Handle messages from webview
    panel.webview.onDidReceiveMessage(
        message => {
            switch (message.command) {
                case 'alert':
                    vscode.window.showInformationMessage(message.text);
                    return;
            }
        },
        undefined,
        context.subscriptions
    );
    
    return panel;
}

function getWebviewContent() {
    return `
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { padding: 20px; }
                button { padding: 10px 20px; }
            </style>
        </head>
        <body>
            <h1>My Panel</h1>
            <button onclick="sendMessage()">Click Me</button>
            <script>
                const vscode = acquireVsCodeApi();
                function sendMessage() {
                    vscode.postMessage({ command: 'alert', text: 'Hello!' });
                }
            </script>
        </body>
        </html>
    `;
}
```

### Tree View

```typescript
import * as vscode from 'vscode';

class MyTreeDataProvider implements vscode.TreeDataProvider<TreeItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<TreeItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;
    
    getTreeItem(element: TreeItem): vscode.TreeItem {
        return element;
    }
    
    getChildren(element?: TreeItem): Thenable<TreeItem[]> {
        if (!element) {
            return Promise.resolve([
                new TreeItem('Item 1', vscode.TreeItemCollapsibleState.None),
                new TreeItem('Item 2', vscode.TreeItemCollapsibleState.None)
            ]);
        }
        return Promise.resolve([]);
    }
    
    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }
}

class TreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
    }
}

// Register
export function activate(context: vscode.ExtensionContext) {
    const treeDataProvider = new MyTreeDataProvider();
    vscode.window.registerTreeDataProvider('myTreeView', treeDataProvider);
}
```

### Status Bar

```typescript
import * as vscode from 'vscode';

export function createStatusBarItem(context: vscode.ExtensionContext) {
    const statusBarItem = vscode.window.createStatusBarItem(
        vscode.StatusBarAlignment.Right,
        100
    );
    
    statusBarItem.text = '$(rocket) dLNk';
    statusBarItem.tooltip = 'dLNk AI Status';
    statusBarItem.command = 'myExtension.showStatus';
    statusBarItem.show();
    
    context.subscriptions.push(statusBarItem);
    
    return statusBarItem;
}
```

---

## 📝 Common Patterns

### Code Actions

```typescript
import * as vscode from 'vscode';

class MyCodeActionProvider implements vscode.CodeActionProvider {
    provideCodeActions(
        document: vscode.TextDocument,
        range: vscode.Range,
        context: vscode.CodeActionContext,
        token: vscode.CancellationToken
    ): vscode.CodeAction[] {
        const actions: vscode.CodeAction[] = [];
        
        // Add "Explain with AI" action
        const explainAction = new vscode.CodeAction(
            'Explain with AI',
            vscode.CodeActionKind.QuickFix
        );
        explainAction.command = {
            command: 'dlnk.explain',
            title: 'Explain with AI',
            arguments: [document.getText(range)]
        };
        actions.push(explainAction);
        
        return actions;
    }
}

// Register
vscode.languages.registerCodeActionsProvider(
    { scheme: 'file' },
    new MyCodeActionProvider()
);
```

### Completion Provider

```typescript
import * as vscode from 'vscode';

class MyCompletionProvider implements vscode.CompletionItemProvider {
    provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): vscode.CompletionItem[] {
        const items: vscode.CompletionItem[] = [];
        
        const item = new vscode.CompletionItem(
            'mySnippet',
            vscode.CompletionItemKind.Snippet
        );
        item.insertText = new vscode.SnippetString('console.log($1);');
        item.documentation = 'Insert console.log';
        items.push(item);
        
        return items;
    }
}

// Register
vscode.languages.registerCompletionItemProvider(
    'javascript',
    new MyCompletionProvider(),
    '.'
);
```

### Hover Provider

```typescript
import * as vscode from 'vscode';

class MyHoverProvider implements vscode.HoverProvider {
    provideHover(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken
    ): vscode.Hover | undefined {
        const range = document.getWordRangeAtPosition(position);
        const word = document.getText(range);
        
        if (word === 'dLNk') {
            return new vscode.Hover(
                new vscode.MarkdownString('**dLNk IDE** - AI-Powered Code Editor')
            );
        }
        
        return undefined;
    }
}

// Register
vscode.languages.registerHoverProvider('*', new MyHoverProvider());
```

---

## 🔧 Configuration

### Contribute Settings

```json
// package.json
{
    "contributes": {
        "configuration": {
            "title": "My Extension",
            "properties": {
                "myExtension.enableFeature": {
                    "type": "boolean",
                    "default": true,
                    "description": "Enable my feature"
                },
                "myExtension.maxItems": {
                    "type": "number",
                    "default": 10,
                    "description": "Maximum number of items"
                }
            }
        }
    }
}
```

### Read Settings

```typescript
import * as vscode from 'vscode';

function getSettings() {
    const config = vscode.workspace.getConfiguration('myExtension');
    const enableFeature = config.get<boolean>('enableFeature', true);
    const maxItems = config.get<number>('maxItems', 10);
    
    return { enableFeature, maxItems };
}

// Watch for changes
vscode.workspace.onDidChangeConfiguration(e => {
    if (e.affectsConfiguration('myExtension')) {
        const newSettings = getSettings();
        // Update extension behavior
    }
});
```

---

## 🧪 Testing

### Unit Tests

```typescript
// src/test/suite/extension.test.ts
import * as assert from 'assert';
import * as vscode from 'vscode';

suite('Extension Test Suite', () => {
    test('Extension should be present', () => {
        assert.ok(vscode.extensions.getExtension('my-extension'));
    });
    
    test('Should activate', async () => {
        const ext = vscode.extensions.getExtension('my-extension');
        await ext?.activate();
        assert.ok(ext?.isActive);
    });
    
    test('Command should be registered', async () => {
        const commands = await vscode.commands.getCommands();
        assert.ok(commands.includes('myExtension.helloWorld'));
    });
});
```

### Run Tests

```bash
npm test
```

---

## 📦 Packaging

### Create VSIX

```bash
# Install vsce
npm install -g @vscode/vsce

# Package
vsce package

# Output: my-dlnk-extension-0.0.1.vsix
```

### Install VSIX

```bash
# ใน dLNk IDE
# Extensions → ... → Install from VSIX
```

---

## 🔐 Security Guidelines

### DO

- ✅ Validate all user input
- ✅ Use HTTPS for external requests
- ✅ Store secrets in SecretStorage
- ✅ Request minimal permissions

### DON'T

- ❌ Execute arbitrary code
- ❌ Store credentials in settings
- ❌ Access files outside workspace
- ❌ Send user data without consent

### Secret Storage

```typescript
import * as vscode from 'vscode';

async function storeSecret(context: vscode.ExtensionContext) {
    // Store
    await context.secrets.store('myApiKey', 'secret-value');
    
    // Retrieve
    const apiKey = await context.secrets.get('myApiKey');
    
    // Delete
    await context.secrets.delete('myApiKey');
}
```

---

## 📚 Resources

- [VS Code Extension API](https://code.visualstudio.com/api)
- [Extension Guidelines](https://code.visualstudio.com/api/references/extension-guidelines)
- [Extension Samples](https://github.com/microsoft/vscode-extension-samples)
- [dLNk Extension API](#dlnk-specific-apis)

---

**ก่อนหน้า:** [← API Reference](api-reference.md)  
**ถัดไป:** [Contributing Guide →](contributing.md)
