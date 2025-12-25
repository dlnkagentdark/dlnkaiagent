#!/bin/bash
#
# dLNk AI Bridge - Antigravity Only Edition
# Run script
#

echo ""
echo "╔═══════════════════════════════════════════════════════════════════════════════╗"
echo "║              dLNk Unified AI Bridge - Antigravity Only Edition                ║"
echo "║                         No Limits • No Fallbacks                              ║"
echo "╚═══════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+"
    exit 1
fi

# Check dependencies
echo "🔍 Checking dependencies..."
python3 -c "import httpx; import aiohttp; import websockets; import cryptography" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing dependencies..."
    pip3 install httpx[http2] aiohttp websockets cryptography
fi

# Run the bridge
echo ""
echo "🚀 Starting dLNk AI Bridge..."
echo ""

cd "$(dirname "$0")"
python3 dlnk_antigravity_only.py
