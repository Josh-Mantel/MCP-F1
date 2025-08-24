#!/bin/bash
# Quick start script for F1 MCP Server

set -e

echo "🏎️  F1 MCP Server Quick Start"
echo "=============================="

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed!"
    echo ""
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    
    # Source the shell configuration to make uv available
    if [[ -f "$HOME/.bashrc" ]]; then
        source "$HOME/.bashrc"
    elif [[ -f "$HOME/.zshrc" ]]; then
        source "$HOME/.zshrc"
    fi
    
    echo "✅ uv installed successfully!"
fi

echo "🐍 Ensuring Python 3.13..."
uv python install 3.13

echo "📦 Installing dependencies..."
uv sync
uv pip install -e .

echo "📁 Setting up FastF1 cache directory..."
mkdir -p cache

echo "🧪 Testing installation..."
uv run python -c "import f1_mcp_server; import fastf1; import mcp; print('✅ All imports successful')"

echo ""
echo "🚀 Setup completed successfully!"
echo ""
echo "Available commands:"
echo "  make mcp         - Start MCP server"
echo "  make http        - Start HTTP server with OAuth"
echo "  make inspector   - Run with MCP Inspector"
echo "  make test        - Run all tests"
echo "  make help        - Show all available commands"
echo ""
echo "Or use uv directly:"
echo "  uv run python -m f1_mcp_server.server"
echo "  uv run python -m f1_mcp_server.combined_server --mode http"