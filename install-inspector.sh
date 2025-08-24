#!/bin/bash
# Install MCP Inspector for F1 MCP Server

set -e

echo "🔍 Installing MCP Inspector"
echo "=========================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed!"
    echo ""
    echo "Please install Node.js first:"
    echo "  macOS: brew install node"
    echo "  Or download from: https://nodejs.org/"
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 16 ]; then
    echo "❌ Node.js 16+ is required (found v$NODE_VERSION)"
    echo "Please update Node.js: https://nodejs.org/"
    exit 1
fi

echo "✅ Node.js $(node --version) detected"

# Install MCP Inspector
echo "📦 Installing MCP Inspector..."
npm install -g @modelcontextprotocol/inspector

# Verify installation
if command -v mcp-inspector &> /dev/null; then
    echo "✅ MCP Inspector installed successfully!"
    echo ""
    echo "🚀 Ready to use:"
    echo "  make inspector                    - Start F1 server with inspector"
    echo "  mcp-inspector --help             - Show inspector help"
    echo "  Open http://localhost:5173       - Inspector web interface"
    echo ""
    echo "📖 See MCP_INSPECTOR_GUIDE.md for detailed usage instructions"
else
    echo "❌ MCP Inspector installation failed"
    exit 1
fi