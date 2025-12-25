# Changelog

All notable changes to the "dLNk AI" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-12-25

### Added
- Initial release of dLNk AI Extension
- AI Chat Panel with side panel interface
- WebSocket connection to AI Bridge service
- REST API fallback support
- Streaming response support (real-time text display)
- Conversation history management
  - Save to VS Code globalState
  - Export/Import functionality
  - Clear history command
- Code explanation feature
  - Select code and explain
  - Context menu integration
- Code generation feature
  - Generate from natural language
  - Insert directly to editor
- Code fixing feature
  - Analyze selected code
  - Suggest improvements
- Inline commands
  - Code completion
  - Documentation generation
  - Code refactoring
  - Test generation
- Error explanation feature
- Keyboard shortcuts
  - Ctrl+Shift+A: Open Chat
  - Ctrl+Shift+E: Explain Code
- Configuration options
  - Server URL
  - API URL
  - Auto-connect
  - Stream response
  - Reconnection settings
- Status bar integration
- Auto-reconnect functionality
- Message queue for offline support

### Technical
- TypeScript implementation
- Webview-based chat UI
- Markdown rendering with syntax highlighting
- Code block copy/insert buttons
- VS Code theme integration
- CSP-compliant webview

## [Unreleased]

### Planned
- Multi-conversation support
- Code diff view for fixes
- Inline completion provider
- Language-specific prompts
- Custom AI model selection
- Team collaboration features
