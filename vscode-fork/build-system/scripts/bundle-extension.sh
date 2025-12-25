#!/bin/bash
# dLNk IDE - Bundle Extension Script
# Bundles the dLNk AI Extension into VSCode fork

set -e

echo "🔌 dLNk IDE - Bundle Extension Script"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
EXTENSION_SRC="$PROJECT_ROOT/extension/dlnk-ai-extension"
EXTENSION_DEST="$PROJECT_ROOT/vscode-fork/extensions/dlnk-ai"

echo "📁 Project Root: $PROJECT_ROOT"
echo "📦 Extension Source: $EXTENSION_SRC"
echo "📤 Extension Destination: $EXTENSION_DEST"
echo ""

# Check if extension source exists
if [ ! -d "$EXTENSION_SRC" ]; then
    echo -e "${RED}❌ Extension source not found at: $EXTENSION_SRC${NC}"
    echo "Please ensure the extension is available before bundling."
    exit 1
fi

echo -e "${GREEN}✅ Extension source found${NC}"
echo ""

# Create destination directory
echo "📁 Creating destination directory..."
mkdir -p "$EXTENSION_DEST"
echo -e "${GREEN}✅ Directory created${NC}"
echo ""

# Copy extension files
echo "📋 Copying extension files..."
cp -r "$EXTENSION_SRC"/* "$EXTENSION_DEST/"
echo -e "${GREEN}✅ Files copied${NC}"
echo ""

# Install extension dependencies
echo "📦 Installing extension dependencies..."
cd "$EXTENSION_DEST"

if command -v pnpm &> /dev/null; then
    pnpm install --frozen-lockfile 2>/dev/null || pnpm install
elif command -v npm &> /dev/null; then
    npm ci 2>/dev/null || npm install
else
    echo -e "${RED}❌ No package manager found${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Compile TypeScript
echo "🔨 Compiling TypeScript..."
if [ -f "package.json" ]; then
    if grep -q '"compile"' package.json; then
        npm run compile
        echo -e "${GREEN}✅ TypeScript compiled${NC}"
    else
        echo -e "${YELLOW}⚠️  No compile script found, skipping${NC}"
    fi
fi
echo ""

# Clean up unnecessary files
echo "🧹 Cleaning up..."
rm -rf "$EXTENSION_DEST/node_modules/.cache" 2>/dev/null || true
rm -rf "$EXTENSION_DEST/.git" 2>/dev/null || true
rm -f "$EXTENSION_DEST/.gitignore" 2>/dev/null || true
rm -f "$EXTENSION_DEST/.eslintrc.json" 2>/dev/null || true
rm -f "$EXTENSION_DEST/tsconfig.json" 2>/dev/null || true
rm -rf "$EXTENSION_DEST/src" 2>/dev/null || true  # Keep only compiled output
echo -e "${GREEN}✅ Cleanup complete${NC}"
echo ""

# Verify bundle
echo "🔍 Verifying bundle..."
if [ -f "$EXTENSION_DEST/package.json" ]; then
    EXTENSION_NAME=$(node -p "require('$EXTENSION_DEST/package.json').name" 2>/dev/null || echo "unknown")
    EXTENSION_VERSION=$(node -p "require('$EXTENSION_DEST/package.json').version" 2>/dev/null || echo "unknown")
    echo -e "${BLUE}  Name: $EXTENSION_NAME${NC}"
    echo -e "${BLUE}  Version: $EXTENSION_VERSION${NC}"
    echo -e "${GREEN}✅ Bundle verified${NC}"
else
    echo -e "${RED}❌ Bundle verification failed - package.json not found${NC}"
    exit 1
fi
echo ""

# Summary
echo "✨ Extension Bundle Complete!"
echo "============================="
echo ""
echo "📦 Extension bundled to: $EXTENSION_DEST"
echo ""
echo "📋 Contents:"
ls -la "$EXTENSION_DEST" | head -15
echo ""
echo -e "${GREEN}🎉 Extension ready for build!${NC}"
