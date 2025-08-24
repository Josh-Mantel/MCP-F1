# F1 MCP Server Usage Guide

## Quick Start

### 1. Installation

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies with uv
uv sync
uv pip install -e .

# Or use the setup script
python setup.py
```

### 2. Test MCP Functionality

```bash
# Test MCP tools directly
uv run python mcp_test.py

# Test with MCP Inspector (requires Node.js)
npm install -g @modelcontextprotocol/inspector
mcp-inspector uv run python -m f1_mcp_server.server
```

### 3. Test HTTP Server with OAuth

```bash
# Start HTTP server
uv run python -m f1_mcp_server.combined_server --mode http

# In another terminal, test OAuth flow
uv run python test_client.py
```

## MCP Mode

The server implements the Model Context Protocol and provides these tools:

### Available Tools

1. **get_race_schedule** - Get F1 race schedule for a season
   ```json
   {
     "year": 2024
   }
   ```

2. **get_session_results** - Get results for a specific session
   ```json
   {
     "year": 2024,
     "round_number": 1,
     "session": "R"
   }
   ```

3. **get_driver_standings** - Get driver championship standings
   ```json
   {
     "year": 2024,
     "round_number": 10
   }
   ```

4. **get_constructor_standings** - Get constructor standings
   ```json
   {
     "year": 2024,
     "round_number": 10
   }
   ```

5. **get_lap_times** - Get lap times for a session
   ```json
   {
     "year": 2024,
     "round_number": 1,
     "session": "R",
     "driver": "VER"
   }
   ```

### Session Types
- `FP1`, `FP2`, `FP3` - Free Practice sessions
- `Q` - Qualifying
- `R` - Race

## HTTP Mode with OAuth

### OAuth Flow

1. **Authorization Request**
   ```
   GET /authorize?client_id=f1-mcp-client&redirect_uri=http://localhost:8080/callback&response_type=code&scope=f1:read&state=random-state
   ```

2. **Token Exchange**
   ```bash
   curl -X POST http://localhost:8080/token \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -d "grant_type=authorization_code&code=AUTH_CODE&client_id=f1-mcp-client&client_secret=f1-mcp-secret-key"
   ```

3. **Access Protected Resource**
   ```bash
   curl -H "Authorization: Bearer ACCESS_TOKEN" \
     "http://localhost:8080/f1/stream?year=2024"
   ```

### HTTP Endpoints

- `GET /authorize` - OAuth authorization endpoint
- `POST /token` - OAuth token endpoint  
- `GET /callback` - OAuth callback (for testing)
- `GET /f1/stream` - Server-Sent Events stream for F1 data

### Streaming Example

```bash
# Get authorization URL and visit it
curl "http://localhost:8080/authorize?client_id=f1-mcp-client&redirect_uri=http://localhost:8080/callback&response_type=code"

# Exchange code for token (replace AUTH_CODE)
curl -X POST http://localhost:8080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=AUTH_CODE&client_id=f1-mcp-client&client_secret=f1-mcp-secret-key"

# Stream F1 data (replace ACCESS_TOKEN)
curl -H "Authorization: Bearer ACCESS_TOKEN" \
  "http://localhost:8080/f1/stream?year=2024"
```

## Configuration

### Default OAuth Credentials
- **Client ID**: `f1-mcp-client`
- **Client Secret**: `f1-mcp-secret-key`
- **Redirect URI**: `http://localhost:8080/callback`

### Server Options

```bash
# MCP mode (default)
uv run python -m f1_mcp_server.combined_server --mode mcp

# HTTP mode
uv run python -m f1_mcp_server.combined_server --mode http --http-host localhost --http-port 8080

# Both modes (not recommended for production)
uv run python -m f1_mcp_server.combined_server --mode both
```

## Testing

### Run All Tests
```bash
uv run python run_tests.py
```

### Manual Testing

1. **MCP Inspector**
   ```bash
   # Install MCP Inspector first
   npm install -g @modelcontextprotocol/inspector
   
   # Run with inspector
   make inspector
   # or: mcp-inspector uv run python -m f1_mcp_server.server
   
   # Then open http://localhost:5173 in your browser
   ```

2. **OAuth Flow**
   ```bash
   uv run python test_client.py
   ```

3. **Direct FastF1 Test**
   ```python
   import fastf1
   fastf1.Cache.enable_cache('cache')
   schedule = fastf1.get_event_schedule(2024)
   print(schedule.head())
   ```

## Troubleshooting

### Common Issues

1. **FastF1 Cache Issues**
   - Delete the `cache` directory and restart
   - Ensure internet connection for F1 data

2. **MCP Inspector Connection**
   - Ensure Python path is correct
   - Check that all dependencies are installed

3. **OAuth Flow Issues**
   - Verify client credentials match
   - Check redirect URI configuration
   - Ensure server is running on correct port

### Debug Mode

```bash
uv run python -m f1_mcp_server.combined_server --mode http --log-level DEBUG
```

## Data Sources

This server uses the [FastF1](https://github.com/theOehrly/Fast-F1) Python package, which provides:

- Official F1 timing data
- Telemetry data
- Session results
- Historical data back to 2018
- Live timing during race weekends

## Limitations

- Historical data availability depends on FastF1
- Some telemetry data requires session loading (can be slow)
- OAuth implementation is basic (for demonstration)
- HTTP streaming is simplified (production would use WebSockets)

## Next Steps

- Add WebSocket support for real-time data
- Implement proper OAuth scopes and permissions
- Add caching for frequently requested data
- Add more F1 data endpoints (weather, track info, etc.)
- Add rate limiting and proper error handling