#!/bin/bash
# dLNk IDE - Master Build Script
# Builds dLNk IDE for all platforms

set -e

echo "🚀 dLNk IDE - Master Build Script"
echo "=================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BUILD_DIR="$PROJECT_ROOT/vscode-fork"
DIST_DIR="$PROJECT_ROOT/dist"
VERSION=$(node -p "require('$BUILD_DIR/package.json').version")

echo "📁 Project Root: $PROJECT_ROOT"
echo "📦 Build Directory: $BUILD_DIR"
echo "📤 Output Directory: $DIST_DIR"
echo "🏷️  Version: $VERSION"
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

# Install dependencies
echo "📦 Installing dependencies..."
cd "$BUILD_DIR"
npm install
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Bundle extension
echo "🔌 Bundling dLNk AI Extension..."
EXTENSION_SRC="$PROJECT_ROOT/extension/dlnk-ai-extension"
EXTENSION_DEST="$BUILD_DIR/extensions/dlnk-ai"

if [ -d "$EXTENSION_SRC" ]; then
    echo "  Copying extension from $EXTENSION_SRC"
    mkdir -p "$EXTENSION_DEST"
    cp -r "$EXTENSION_SRC"/* "$EXTENSION_DEST/"
    
    # Install extension dependencies
    cd "$EXTENSION_DEST"
    npm install
    npm run compile
    
    echo -e "${GREEN}✅ Extension bundled${NC}"
else
    echo -e "${YELLOW}⚠️  Extension source not found, skipping${NC}"
fi
echo ""

# Build for each platform
echo "🏗️  Building for all platforms..."
cd "$BUILD_DIR"

# Determine which platforms to build
BUILD_WINDOWS=true
BUILD_MACOS=true
BUILD_LINUX=true

# Parse arguments
for arg in "$@"; do
    case $arg in
        --windows-only)
            BUILD_MACOS=false
            BUILD_LINUX=false
            ;;
        --macos-only)
            BUILD_WINDOWS=false
            BUILD_LINUX=false
            ;;
        --linux-only)
            BUILD_WINDOWS=false
            BUILD_MACOS=false
            ;;
    esac
done

# Windows
if [ "$BUILD_WINDOWS" = true ]; then
    echo "🪟 Building for Windows..."
    npm run build:win || echo -e "${YELLOW}⚠️  Windows build failed${NC}"
    echo ""
fi

# macOS
if [ "$BUILD_MACOS" = true ]; then
    echo "🍎 Building for macOS..."
    npm run build:mac || echo -e "${YELLOW}⚠️  macOS build failed${NC}"
    echo ""
fi

# Linux
if [ "$BUILD_LINUX" = true ]; then
    echo "🐧 Building for Linux..."
    npm run build:linux || echo -e "${YELLOW}⚠️  Linux build failed${NC}"
    echo ""
fi

# Generate checksums
echo "🔐 Generating checksums..."
cd "$DIST_DIR"
find . -type f \( -name "*.exe" -o -name "*.dmg" -o -name "*.AppImage" -o -name "*.deb" -o -name "*.rpm" \) -exec sha256sum {} \; > SHA256SUMS.txt
echo -e "${GREEN}✅ Checksums generated${NC}"
echo ""

# Summary
echo "✨ Build Complete!"
echo "=================="
echo ""
echo "📦 Build artifacts:"
ls -lh "$DIST_DIR" | grep -E '\.(exe|dmg|AppImage|deb|rpm|zip|tar\.gz)$' || echo "No artifacts found"
echo ""
echo "🔐 Checksums: $DIST_DIR/SHA256SUMS.txt"
echo ""
echo -e "${GREEN}🎉 All builds completed successfully!${NC}"
