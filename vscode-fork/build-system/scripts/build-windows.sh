#!/bin/bash
# dLNk IDE - Windows Build Script
# Builds dLNk IDE for Windows (x64, ia32)

set -e

echo "🪟 dLNk IDE - Windows Build Script"
echo "==================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/vscode-fork"
DIST_DIR="$PROJECT_ROOT/dist"

echo "📁 Project Root: $PROJECT_ROOT"
echo "📦 Build Directory: $BUILD_DIR"
echo ""

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Node.js $(node --version)${NC}"
echo -e "${GREEN}✅ npm $(npm --version)${NC}"
echo ""

# Navigate to build directory
cd "$BUILD_DIR/build-system/build"

# Install dependencies
echo "📦 Installing build dependencies..."
npm install
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Build for Windows
echo "🏗️  Building for Windows..."
echo "  Target: NSIS installer (x64, ia32)"
echo "  Target: ZIP archive (x64, ia32)"
echo ""

npm run build:win

# Check output
echo ""
echo "📦 Build artifacts:"
if [ -d "$DIST_DIR" ]; then
    ls -lh "$DIST_DIR" | grep -E '\.(exe|zip)$' || echo "No Windows artifacts found"
else
    echo "Output directory not found"
fi

echo ""
echo -e "${GREEN}🎉 Windows build completed!${NC}"
