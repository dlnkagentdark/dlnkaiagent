# 📝 Changelog - dLNk IDE

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2025-12-25

### 🎉 Initial Release

This is the first public release of dLNk IDE, a VS Code fork supercharged with integrated AI capabilities.

### Added

- **VS Code Fork**: Core application based on VS Code with custom dLNk branding, new icons, and a unique dark theme.
- **dLNk AI Extension**: Integrated AI chat panel, context-aware code completion, and other AI-powered assistance features.
- **AI Bridge Backend**: A central service connecting the IDE to multiple AI providers (Antigravity/Jetski, Gemini, OpenAI, etc.) with WebSocket and REST APIs.
- **License & Authentication System**: Robust license management with hardware binding, offline validation, and a secure local database.
- **Admin Console**: A full-featured, terminal-based UI (TUI) for administrators to manage users, licenses, and system settings.
- **Security Framework**: Comprehensive security module including a prompt filter, anomaly detection, rate limiting, and encrypted storage.
- **Telegram Bot Integration**: Admin notifications for critical system events, security alerts, and basic management commands.
- **Full Documentation**: Complete User, Admin, and Developer guides, including detailed API references and test plans.

### Changed

- Replaced all Microsoft branding and telemetry with dLNk-specific assets and configurations.
- Unified multiple Python scripts for AI connectivity into a single, robust AI Bridge service.
- Enhanced the original license system with hardware binding and offline capabilities.

### Fixed

- Resolved gRPC protocol decoding issues for communication with the Antigravity/Jetski endpoint.
- Stabilized token management with an auto-refresh mechanism to prevent session expiry.

---

## [0.9.0-beta] - 2025-12-15

### Added
- Beta release for internal testing.
- Core AI Chat functionality.
- Basic License System.
- Admin Console prototype.

### Known Issues
- Potential memory leak in AI Bridge under heavy load.
- Slower completion suggestions in certain edge cases.
- Minor UI glitches on macOS.

---

## [0.8.0-alpha] - 2025-12-01

### Added
- Alpha release for the development team.
- Initial VS Code Fork setup.
- AI Bridge and License Server prototypes.

### Changed
- Refactored AI Bridge architecture for multi-provider support.

### Removed
- Legacy authentication system in favor of the new license server.
