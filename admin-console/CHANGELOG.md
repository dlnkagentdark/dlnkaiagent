# Changelog

All notable changes to dLNk Admin Console will be documented in this file.

## [1.0.0] - 2025-12-24

### Added
- Initial release of dLNk Admin Console
- Login system with Admin Key authentication
- 2FA (TOTP) support
- Dashboard with real-time statistics
- License management (create, extend, revoke)
- User management (view, ban, unban)
- C2 Log viewer with filtering
- Security alerts monitoring
- Antigravity token management
- Settings panel for configuration
- Dark theme matching dLNk IDE
- Mock data support for offline testing
- Session management
- Window icon integration
- Complete documentation

### Features
- **Dashboard View**: Stats cards, usage charts, recent activity
- **License Management**: Full CRUD operations for licenses
- **User Management**: User listing, activity logs, ban/unban
- **Log Viewer**: C2 logs, alerts, filtering, export
- **Token Management**: Token listing, refresh, revoke
- **Settings**: Telegram bot, alert thresholds, API endpoints, security

### Technical
- Built with Python CustomTkinter
- Modular architecture (app, views, components, utils)
- API client with mock data fallback
- Session-based authentication
- Cross-platform support (Windows, Linux, macOS)

### Dependencies
- customtkinter >= 5.2.0
- pillow >= 10.0.0
- requests >= 2.31.0
- matplotlib >= 3.7.0
- cryptography >= 41.0.0
- pyotp >= 2.9.0
