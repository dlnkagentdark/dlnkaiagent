#!/bin/bash
# dLNk IDE - Deployment Script
# ============================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOY_DIR="$SCRIPT_DIR"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════╗"
    echo "║                                                           ║"
    echo "║     ██████╗ ██╗     ███╗   ██╗██╗  ██╗                   ║"
    echo "║     ██╔══██╗██║     ████╗  ██║██║ ██╔╝                   ║"
    echo "║     ██║  ██║██║     ██╔██╗ ██║█████╔╝                    ║"
    echo "║     ██║  ██║██║     ██║╚██╗██║██╔═██╗                    ║"
    echo "║     ██████╔╝███████╗██║ ╚████║██║  ██╗                   ║"
    echo "║     ╚═════╝ ╚══════╝╚═╝  ╚═══╝╚═╝  ╚═╝                   ║"
    echo "║                                                           ║"
    echo "║              IDE Deployment Script                        ║"
    echo "║                                                           ║"
    echo "╚═══════════════════════════════════════════════════════════╝"
    echo ""
}

check_requirements() {
    log_info "Checking requirements..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    log_success "All requirements met"
}

setup_env() {
    log_info "Setting up environment..."
    
    # Create .env file if not exists
    if [ ! -f "$DEPLOY_DIR/.env" ]; then
        log_info "Creating .env file from template..."
        cat > "$DEPLOY_DIR/.env" << EOF
# dLNk IDE Environment Configuration
# ===================================

# Antigravity/Jetski API
ANTIGRAVITY_ENDPOINT=https://antigravity-worker.google.com/exa.language_server_pb.LanguageServerService/SendUserCascadeMessage

# Fallback AI Providers (optional)
OPENAI_API_KEY=
GEMINI_API_KEY=
GROQ_API_KEY=

# Telegram Alerts (optional)
TELEGRAM_BOT_TOKEN=
TELEGRAM_ADMIN_CHAT_ID=

# Log Level
LOG_LEVEL=INFO
EOF
        log_warning "Please edit $DEPLOY_DIR/.env with your API keys"
    fi
    
    log_success "Environment setup complete"
}

build_images() {
    log_info "Building Docker images..."
    
    cd "$DEPLOY_DIR"
    
    if docker compose version &> /dev/null; then
        docker compose build
    else
        docker-compose build
    fi
    
    log_success "Docker images built successfully"
}

start_services() {
    log_info "Starting services..."
    
    cd "$DEPLOY_DIR"
    
    if docker compose version &> /dev/null; then
        docker compose up -d
    else
        docker-compose up -d
    fi
    
    log_success "Services started"
}

stop_services() {
    log_info "Stopping services..."
    
    cd "$DEPLOY_DIR"
    
    if docker compose version &> /dev/null; then
        docker compose down
    else
        docker-compose down
    fi
    
    log_success "Services stopped"
}

show_status() {
    log_info "Service status:"
    
    cd "$DEPLOY_DIR"
    
    if docker compose version &> /dev/null; then
        docker compose ps
    else
        docker-compose ps
    fi
    
    echo ""
    log_info "Service endpoints:"
    echo "  - License API:     http://localhost:8088"
    echo "  - AI Bridge REST:  http://localhost:8766"
    echo "  - AI Bridge WS:    ws://localhost:8765"
    echo "  - Security API:    http://localhost:8089"
    echo "  - Nginx Proxy:     http://localhost:80"
}

show_logs() {
    log_info "Showing logs..."
    
    cd "$DEPLOY_DIR"
    
    if docker compose version &> /dev/null; then
        docker compose logs -f
    else
        docker-compose logs -f
    fi
}

run_tests() {
    log_info "Running integration tests..."
    
    cd "$PROJECT_ROOT"
    python3 tests/integration_test.py
    
    log_success "Tests completed"
}

# Main
print_banner

case "${1:-help}" in
    build)
        check_requirements
        build_images
        ;;
    start)
        check_requirements
        setup_env
        start_services
        show_status
        ;;
    stop)
        stop_services
        ;;
    restart)
        stop_services
        start_services
        show_status
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    test)
        run_tests
        ;;
    setup)
        check_requirements
        setup_env
        build_images
        start_services
        show_status
        ;;
    help|*)
        echo "Usage: $0 {build|start|stop|restart|status|logs|test|setup|help}"
        echo ""
        echo "Commands:"
        echo "  build    - Build Docker images"
        echo "  start    - Start all services"
        echo "  stop     - Stop all services"
        echo "  restart  - Restart all services"
        echo "  status   - Show service status"
        echo "  logs     - Show service logs"
        echo "  test     - Run integration tests"
        echo "  setup    - Full setup (build + start)"
        echo "  help     - Show this help message"
        ;;
esac
