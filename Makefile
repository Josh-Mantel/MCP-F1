# F1 MCP Server Makefile

.PHONY: install test clean dev mcp http inspector

# Install dependencies
install:
	@echo "🏎️  Installing F1 MCP Server with uv..."
	@echo "🐍 Ensuring Python 3.13..."
	uv python install 3.13
	uv sync
	uv pip install -e .
	@$(MAKE) setup-cache

# Development setup
dev: install
	@echo "🔧 Setting up development environment..."
	uv pip install -e ".[dev]"

# Run tests
test:
	@echo "🧪 Running tests..."
	uv run python run_tests.py

# Test dependencies
test-deps:
	@echo "🧪 Testing Python 3.13 compatibility..."
	uv run python test_deps.py

# Test server startup
test-startup:
	@echo "🧪 Testing server startup..."
	uv run python test_startup.py

# Test MCP tools directly
test-mcp:
	@echo "🧪 Testing MCP tools..."
	uv run python mcp_test.py

# Start MCP server
mcp:
	@echo "🚀 Starting MCP server..."
	uv run python -m f1_mcp_server.server

# Start HTTP server
http:
	@echo "🌐 Starting HTTP server..."
	uv run python -m f1_mcp_server.combined_server --mode http

# Run with MCP Inspector
inspector:
	@echo "🔍 Starting MCP Inspector..."
	mcp-inspector uv run python -m f1_mcp_server.server

# Test OAuth flow
test-oauth:
	@echo "🔐 Testing OAuth flow..."
	uv run python test_client.py

# Setup cache directory
setup-cache:
	@echo "📁 Setting up FastF1 cache directory..."
	mkdir -p cache

# Clean cache and temporary files
clean:
	@echo "🧹 Cleaning up..."
	rm -rf cache/
	rm -rf __pycache__/
	rm -rf f1_mcp_server/__pycache__/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete

# Format code
format:
	@echo "🎨 Formatting code..."
	uv run black .
	uv run ruff check --fix .

# Show help
help:
	@echo "F1 MCP Server Commands:"
	@echo "  make install     - Install dependencies"
	@echo "  make dev         - Setup development environment"
	@echo "  make test        - Run all tests"
	@echo "  make test-deps   - Test Python 3.13 compatibility"
	@echo "  make test-startup- Test server startup"
	@echo "  make test-mcp    - Test MCP tools only"
	@echo "  make mcp         - Start MCP server"
	@echo "  make http        - Start HTTP server"
	@echo "  make inspector   - Run with MCP Inspector"
	@echo "  make test-oauth  - Test OAuth flow"
	@echo "  make setup-cache - Setup FastF1 cache directory"
	@echo "  make clean       - Clean temporary files"
	@echo "  make format      - Format code"
	@echo ""
	@echo "MCP Inspector:"
	@echo "  make inspector   - Run with MCP Inspector (requires Node.js)"
	@echo "  See MCP_INSPECTOR_GUIDE.md for detailed usage instructions"