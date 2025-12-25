# dLNk AI Extension

🤖 **AI-Powered Code Assistant for dLNk IDE**

dLNk AI is a VS Code extension that provides intelligent code assistance powered by AI. It integrates seamlessly with the dLNk AI Bridge service to offer real-time code explanations, generation, and fixes.

## Features

### 💬 AI Chat Panel
- Side panel chat interface for conversing with AI
- Markdown rendering with syntax highlighting
- Code block copy and insert functionality
- Streaming response support (real-time text display)
- Conversation history management

### 🔍 Code Explanation
- Select code and get instant explanations
- Detailed step-by-step breakdowns
- Context menu integration

### ⚡ Code Generation
- Generate code from natural language descriptions
- Support for multiple programming languages
- Insert generated code directly into editor

### 🔧 Code Fixing
- Analyze and fix selected code
- Bug detection and suggestions
- Performance optimization recommendations

### 📝 Additional Features
- Inline code completion
- Automatic documentation generation
- Unit test generation
- Error explanation
- Code refactoring suggestions

## Installation

1. Open VS Code
2. Go to Extensions (Ctrl+Shift+X)
3. Search for "dLNk AI"
4. Click Install

Or install from VSIX:
```bash
code --install-extension dlnk-ai-1.0.0.vsix
```

## Requirements

- VS Code 1.85.0 or higher
- dLNk AI Bridge service running (for AI functionality)

## Configuration

Open Settings (Ctrl+,) and search for "dLNk AI":

| Setting | Default | Description |
|---------|---------|-------------|
| `dlnk-ai.serverUrl` | `ws://localhost:8765` | WebSocket server URL |
| `dlnk-ai.apiUrl` | `http://localhost:8766/api` | REST API URL |
| `dlnk-ai.autoConnect` | `true` | Auto-connect on startup |
| `dlnk-ai.streamResponse` | `true` | Enable streaming responses |
| `dlnk-ai.maxReconnectAttempts` | `5` | Max reconnection attempts |
| `dlnk-ai.reconnectInterval` | `5000` | Reconnection interval (ms) |

## Keyboard Shortcuts

| Shortcut | Command |
|----------|---------|
| `Ctrl+Shift+A` | Open AI Chat |
| `Ctrl+Shift+E` | Explain Selected Code |

## Commands

Access commands via Command Palette (Ctrl+Shift+P):

- `dLNk AI: Open Chat` - Open the AI chat panel
- `dLNk AI: Explain Selected Code` - Explain the selected code
- `dLNk AI: Generate Code` - Generate code from description
- `dLNk AI: Fix Selected Code` - Fix issues in selected code
- `dLNk AI: Clear Chat History` - Clear conversation history
- `dLNk AI: Export Chat History` - Export history to JSON
- `dLNk AI: Import Chat History` - Import history from JSON

## Context Menu

Right-click on selected code to access:
- Explain Selected Code
- Fix Selected Code

## Usage

### Chat with AI
1. Click the dLNk AI icon in the Activity Bar
2. Type your question in the input field
3. Press Enter or click Send

### Explain Code
1. Select code in the editor
2. Right-click and choose "dLNk AI: Explain Selected Code"
3. Or use Ctrl+Shift+E

### Generate Code
1. Open Command Palette (Ctrl+Shift+P)
2. Type "dLNk AI: Generate Code"
3. Enter your description
4. Code will be generated and shown in chat

### Fix Code
1. Select problematic code
2. Right-click and choose "dLNk AI: Fix Selected Code"
3. AI will analyze and suggest fixes

## Architecture

```
┌─────────────────┐     ┌─────────────────┐
│   VS Code       │     │   AI Bridge     │
│   Extension     │◄───►│   Service       │
│                 │ WS  │                 │
│  ┌───────────┐  │     │  ┌───────────┐  │
│  │Chat Panel │  │     │  │ AI Models │  │
│  └───────────┘  │     │  └───────────┘  │
│  ┌───────────┐  │     └─────────────────┘
│  │AI Client  │  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │History Mgr│  │
│  └───────────┘  │
└─────────────────┘
```

## Development

### Build
```bash
npm install
npm run compile
```

### Watch Mode
```bash
npm run watch
```

### Package
```bash
npm run package
```

### Test
```bash
npm test
```

## Troubleshooting

### Connection Issues
1. Ensure dLNk AI Bridge service is running
2. Check server URL in settings
3. Verify firewall settings

### Extension Not Loading
1. Check VS Code version (requires 1.85.0+)
2. Reload VS Code window
3. Check Output panel for errors

## License

Proprietary - dLNk IDE Project

## Support

For issues and feature requests, please contact the dLNk development team.

---

Made with ❤️ by dLNk Team
