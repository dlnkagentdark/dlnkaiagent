#!/bin/bash
# dLNk IDE - macOS Build Script
# Builds dLNk IDE for macOS (x64, arm64)

set -e

echo "🍎 dLNk IDE - macOS Build Script"
echo "================================="
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

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${YELLOW}⚠️  Not running on macOS. DMG creation may fail.${NC}"
    echo -e "${YELLOW}   For best results, run this script on macOS.${NC}"
    echo ""
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

# Generate ICNS from iconset (if on macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    ICONSET_DIR="$BUILD_DIR/resources/darwin/dlnk-logo.iconset"
    ICNS_FILE="$BUILD_DIR/resources/dlnk-logo.icns"
    
    if [ -d "$ICONSET_DIR" ] && ! [ -f "$ICNS_FILE" ]; then
        echo "🎨 Generating ICNS file from iconset..."
        iconutil -c icns "$ICONSET_DIR" -o "$ICNS_FILE"
        echo -e "${GREEN}✅ ICNS file generated${NC}"
        echo ""
    fi
fi

# Build for macOS
echo "🏗️  Building for macOS..."
echo "  Target: DMG installer (x64, arm64)"
echo "  Target: ZIP archive (x64, arm64)"
echo ""

npm run build:mac

# Check output
echo ""
echo "📦 Build artifacts:"
if [ -d "$DIST_DIR" ]; then
    ls -lh "$DIST_DIR" | grep -E '\.(dmg|zip)$' || echo "No macOS artifacts found"
else
    echo "Output directory not found"
fi

echo ""
echo -e "${GREEN}🎉 macOS build completed!${NC}"
