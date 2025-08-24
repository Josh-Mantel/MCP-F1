# F1 MCP Server

A Model Context Protocol (MCP) server that provides Formula 1 data using the FastF1 Python package.

## Features

- Get race schedules for any F1 season
- Retrieve session results (practice, qualifying, race)
- Access lap times and telemetry data
- Driver and constructor standings
- Circuit information

## Quick Start

### Prerequisites
- Python 3.13
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager

### 1. Install uv (if not already installed)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Setup F1 MCP Server
```bash
# Quick setup
./quick-start.sh

# Or manually
make install
# or: uv sync && uv pip install -e .
```

### 3. Run the server
```bash
# MCP mode (for MCP Inspector)
make mcp

# HTTP mode (for OAuth testing)  
make http

# With MCP Inspector
make inspector
```

## MCP Inspector Setup

The MCP Inspector is a powerful tool for testing and debugging MCP servers. Here's how to set it up:

### 1. Install Node.js (if not already installed)
```bash
# macOS with Homebrew
brew install node

# Or download from https://nodejs.org/
```

### 2. Install MCP Inspector
```bash
# Install globally with npm
npm install -g @modelcontextprotocol/inspector

# Verify installation
mcp-inspector --version
```

### 3. Run F1 MCP Server with Inspector
```bash
# Using make command (recommended)
make inspector

# Or manually
mcp-inspector uv run python -m f1_mcp_server.server
```

### 4. Using MCP Inspector

Once started, the inspector will:
1. **Launch a web interface** (usually at `http://localhost:5173`)
2. **Connect to your F1 MCP server** automatically
3. **Provide an interactive UI** to test all available tools

**Available F1 Tools in Inspector:**
- `get_race_schedule` - Browse F1 race calendars
- `get_session_results` - View race/qualifying results  
- `get_driver_standings` - Check championship standings
- `get_constructor_standings` - Team championship data
- `get_lap_times` - Detailed lap timing analysis

### 5. Example Usage in Inspector

Try these sample requests in the MCP Inspector:

**Get 2024 Race Schedule:**
```json
{
  "year": 2024
}
```

**Get Monaco GP Race Results:**
```json
{
  "year": 2024,
  "round_number": 8,
  "session": "R"
}
```

**Get Lap Times for Verstappen:**
```json
{
  "year": 2024,
  "round_number": 1,
  "session": "R",
  "driver": "VER"
}
```

### Troubleshooting MCP Inspector

**Inspector won't start:**
```bash
# Check Node.js version (needs 16+)
node --version

# Reinstall inspector
npm uninstall -g @modelcontextprotocol/inspector
npm install -g @modelcontextprotocol/inspector
```

**Server connection issues:**
```bash
# Test server directly first
make test-startup

# Check if server starts without inspector
make mcp
```

**Port conflicts:**
```bash
# Inspector uses port 5173 by default
# Kill any processes using the port
lsof -ti:5173 | xargs kill -9
```

## Usage with MCP Inspector

The MCP Inspector provides a web-based interface for testing F1 data tools:

```bash
# Install MCP Inspector (requires Node.js)
npm install -g @modelcontextprotocol/inspector

# Run F1 server with inspector
make inspector

# Or manually
mcp-inspector uv run python -m f1_mcp_server.server
```

**Inspector Features:**
- Interactive web UI at `http://localhost:5173`
- Real-time F1 data testing
- JSON schema validation
- Tool documentation browser

## Available Tools

- `get_race_schedule`: Get the race schedule for a specific season
- `get_session_results`: Get results for a specific session
- `get_driver_standings`: Get driver championship standings
- `get_constructor_standings`: Get constructor championship standings
- `get_lap_times`: Get lap times for a specific session