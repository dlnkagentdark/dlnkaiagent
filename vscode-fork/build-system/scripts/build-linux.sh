#!/bin/bash
# dLNk IDE - Linux Build Script
# Builds dLNk IDE for Linux (x64, arm64)

set -e

echo "🐧 dLNk IDE - Linux Build Script"
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

echo -e "${GREEN}✅ Node.js $(node --version)${NC}"
echo -e "${GREEN}✅ npm $(npm --version)${NC}"
echo ""

# Check for required tools
echo "🔍 Checking Linux build tools..."

# Check for dpkg (for .deb)
if command -v dpkg &> /dev/null; then
    echo -e "${GREEN}✅ dpkg available (for .deb packages)${NC}"
else
    echo -e "${YELLOW}⚠️  dpkg not found - .deb packages may not build${NC}"
fi

# Check for rpmbuild (for .rpm)
if command -v rpmbuild &> /dev/null; then
    echo -e "${GREEN}✅ rpmbuild available (for .rpm packages)${NC}"
else
    echo -e "${YELLOW}⚠️  rpmbuild not found - .rpm packages may not build${NC}"
fi

echo ""

# Navigate to build directory
cd "$BUILD_DIR/build-system/build"

# Install dependencies
echo "📦 Installing build dependencies..."
npm install
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Build for Linux
echo "🏗️  Building for Linux..."
echo "  Target: AppImage (x64, arm64)"
echo "  Target: DEB package (x64, arm64)"
echo "  Target: RPM package (x64, arm64)"
echo "  Target: tar.gz archive (x64, arm64)"
echo ""

npm run build:linux

# Check output
echo ""
echo "📦 Build artifacts:"
if [ -d "$DIST_DIR" ]; then
    ls -lh "$DIST_DIR" | grep -E '\.(AppImage|deb|rpm|tar\.gz)$' || echo "No Linux artifacts found"
else
    echo "Output directory not found"
fi

echo ""
echo -e "${GREEN}🎉 Linux build completed!${NC}"
