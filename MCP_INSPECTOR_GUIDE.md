# MCP Inspector Guide for F1 MCP Server

This guide walks you through using the MCP Inspector to test and explore the F1 MCP Server's capabilities.

## Prerequisites

- F1 MCP Server installed and working (`make test-startup`)
- Node.js 16+ installed
- MCP Inspector installed globally

## Quick Setup

```bash
# 1. Install Node.js (if needed)
brew install node  # macOS
# or download from https://nodejs.org/

# 2. Install MCP Inspector
npm install -g @modelcontextprotocol/inspector

# 3. Start F1 server with inspector
make inspector
```

## Using the Inspector

### 1. Web Interface

Once started, open your browser to `http://localhost:5173`. You'll see:

- **Tools Panel** - List of available F1 tools
- **Request Builder** - JSON input for tool parameters
- **Response Viewer** - Formatted F1 data output
- **Schema Validator** - Real-time parameter validation

### 2. Available F1 Tools

#### `get_race_schedule`
Get the complete race calendar for any F1 season.

**Parameters:**
```json
{
  "year": 2024
}
```

**Use Cases:**
- View all race dates and locations
- Check event formats (Sprint weekends, etc.)
- Plan viewing schedule

#### `get_session_results`
Get detailed results for practice, qualifying, or race sessions.

**Parameters:**
```json
{
  "year": 2024,
  "round_number": 1,
  "session": "R"
}
```

**Session Types:**
- `"FP1"`, `"FP2"`, `"FP3"` - Free Practice
- `"Q"` - Qualifying
- `"R"` - Race

**Use Cases:**
- Analyze race finishing positions
- Compare qualifying performance
- Review practice session times

#### `get_driver_standings`
Get current driver championship standings.

**Parameters:**
```json
{
  "year": 2024,
  "round_number": 10
}
```

**Use Cases:**
- Track championship battles
- Analyze points progression
- Compare driver performance

#### `get_constructor_standings`
Get team championship standings.

**Parameters:**
```json
{
  "year": 2024,
  "round_number": 10
}
```

**Use Cases:**
- Monitor team performance
- Analyze constructor battles
- Track development progress

#### `get_lap_times`
Get detailed lap timing data with telemetry.

**Parameters:**
```json
{
  "year": 2024,
  "round_number": 1,
  "session": "R",
  "driver": "VER"
}
```

**Use Cases:**
- Analyze driver pace
- Compare sector times
- Study tire strategies

## Example Workflows

### 1. Race Weekend Analysis

```bash
# 1. Get race schedule to find round numbers
{"year": 2024}

# 2. Get qualifying results
{"year": 2024, "round_number": 8, "session": "Q"}

# 3. Get race results
{"year": 2024, "round_number": 8, "session": "R"}

# 4. Analyze lap times for top drivers
{"year": 2024, "round_number": 8, "session": "R", "driver": "VER"}
{"year": 2024, "round_number": 8, "session": "R", "driver": "LEC"}
```

### 2. Championship Analysis

```bash
# 1. Get current driver standings
{"year": 2024, "round_number": 15}

# 2. Get constructor standings
{"year": 2024, "round_number": 15}

# 3. Compare with mid-season standings
{"year": 2024, "round_number": 10}
```

### 3. Historical Comparison

```bash
# Compare different seasons
{"year": 2023}  # 2023 schedule
{"year": 2024}  # 2024 schedule

# Compare championship battles
{"year": 2023, "round_number": 22}  # Final 2023 standings
{"year": 2024, "round_number": 15}  # Current 2024 standings
```

## Tips and Tricks

### 1. Finding Round Numbers
Use `get_race_schedule` first to see all rounds and their corresponding race names.

### 2. Driver Abbreviations
Common driver codes:
- `VER` - Max Verstappen
- `HAM` - Lewis Hamilton  
- `LEC` - Charles Leclerc
- `RUS` - George Russell
- `NOR` - Lando Norris

### 3. Data Caching
The server caches F1 data locally. First requests may be slower as data is downloaded.

### 4. Error Handling
If a tool returns an error:
- Check parameter spelling and values
- Verify the round number exists for that year
- Some historical data may not be available

## Troubleshooting

### Inspector Won't Start
```bash
# Check Node.js version
node --version  # Should be 16+

# Reinstall inspector
npm uninstall -g @modelcontextprotocol/inspector
npm install -g @modelcontextprotocol/inspector
```

### Server Connection Issues
```bash
# Test server independently
make test-startup
make mcp

# Check for port conflicts
lsof -ti:5173 | xargs kill -9
```

### F1 Data Errors
```bash
# Clear cache and retry
make clean
make install

# Check internet connection (F1 data is downloaded)
```

### Performance Issues
```bash
# First requests are slower (downloading data)
# Subsequent requests use cached data
# Large datasets (lap times) may take time to process
```

## Advanced Usage

### Custom Queries
The inspector supports complex JSON queries. Experiment with different parameter combinations to explore F1 data relationships.

### Data Export
Copy response data from the inspector to use in other applications or analysis tools.

### Batch Testing
Use the inspector to test multiple scenarios quickly, building a comprehensive understanding of F1 data patterns.

## Quick Reference

### MCP Inspector Commands
```bash
# Start inspector with F1 server
make inspector

# Test server startup
make test-startup

# Install inspector dependencies
./install-inspector.sh
```

### OAuth Quick Commands
```bash
# 1. Start HTTP server
make http

# 2. Get authorization (visit in browser)
open "http://localhost:8080/authorize?response_type=code&client_id=f1-mcp-client&redirect_uri=http://localhost:8080/callback&scope=f1:read&state=test"

# 3. Exchange code for token (replace AUTH_CODE)
curl -X POST http://localhost:8080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=AUTH_CODE&client_id=f1-mcp-client&client_secret=f1-mcp-secret-key&redirect_uri=http://localhost:8080/callback"

# 4. Use bearer token (replace YOUR_TOKEN)
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8080/f1/stream?year=2024"

# 5. Automated testing
uv run python test_client.py
```

### Common F1 Data Queries
```json
// Current season schedule
{"year": 2024}

// Latest race results
{"year": 2024, "round_number": 20, "session": "R"}

// Championship standings
{"year": 2024, "round_number": 20}

// Driver lap analysis
{"year": 2024, "round_number": 1, "session": "R", "driver": "VER"}
```

## OAuth Configuration for HTTP API

While MCP Inspector uses the direct MCP protocol, you can also test the F1 server's HTTP API with OAuth authentication.

### 1. Start HTTP Server

```bash
# Start the HTTP server with OAuth support
make http

# Or manually
uv run python -m f1_mcp_server.combined_server --mode http
```

The server will display:
```
🏎️  F1 MCP HTTP Server started!
📍 Server: http://localhost:8080
🔐 OAuth Authorization URL: http://localhost:8080/authorize?...
📊 Stream endpoint: http://localhost:8080/f1/stream
🔑 Client ID: f1-mcp-client
🔒 Client Secret: f1-mcp-secret-key
```

### 2. OAuth Flow Steps

#### Step 1: Get Authorization Code

Visit the authorization URL in your browser:
```
http://localhost:8080/authorize?response_type=code&client_id=f1-mcp-client&redirect_uri=http://localhost:8080/callback&scope=f1:read&state=test-state
```

This will redirect you to a callback page with an authorization code.

#### Step 2: Exchange Code for Bearer Token

Use curl to exchange the authorization code for an access token:

```bash
# Replace AUTH_CODE with the code from step 1
curl -X POST http://localhost:8080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code&code=AUTH_CODE&client_id=f1-mcp-client&client_secret=f1-mcp-secret-key&redirect_uri=http://localhost:8080/callback"
```

**Response:**
```json
{
  "access_token": "your-bearer-token-here",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "your-refresh-token-here",
  "scope": "f1:read"
}
```

#### Step 3: Use Bearer Token

Now you can access the streaming endpoint with your bearer token:

```bash
# Replace YOUR_BEARER_TOKEN with the access_token from step 2
curl -H "Authorization: Bearer YOUR_BEARER_TOKEN" \
  "http://localhost:8080/f1/stream?year=2024"
```

### 3. Automated OAuth Testing

Use the provided test client for easier OAuth testing:

```bash
# Run the OAuth test client
uv run python test_client.py
```

**Test Client Workflow:**
1. Displays authorization URL
2. Prompts for authorization code
3. Exchanges code for token automatically
4. Shows streaming endpoint usage

### 4. OAuth Configuration Details

**Default Credentials:**
- **Client ID**: `f1-mcp-client`
- **Client Secret**: `f1-mcp-secret-key`
- **Redirect URI**: `http://localhost:8080/callback`
- **Scope**: `f1:read`

**Token Lifetimes:**
- **Access Token**: 1 hour (3600 seconds)
- **Refresh Token**: 30 days
- **Authorization Code**: 10 minutes

### 5. Refresh Token Usage

When your access token expires, use the refresh token:

```bash
curl -X POST http://localhost:8080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=refresh_token&refresh_token=YOUR_REFRESH_TOKEN&client_id=f1-mcp-client&client_secret=f1-mcp-secret-key"
```

### 6. HTTP API Endpoints

Once you have a bearer token, you can access:

#### Streaming Endpoint
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8080/f1/stream?year=2024"
```

**Features:**
- Server-Sent Events (SSE) streaming
- Real-time F1 data updates
- Year parameter for season selection

#### OAuth Endpoints
- `GET /authorize` - Authorization endpoint
- `POST /token` - Token exchange endpoint
- `GET /callback` - OAuth callback (for testing)

### 7. Testing with Postman/Insomnia

You can also test the OAuth flow with API clients:

**1. Authorization Request:**
- Method: GET
- URL: `http://localhost:8080/authorize`
- Params: `response_type=code`, `client_id=f1-mcp-client`, etc.

**2. Token Exchange:**
- Method: POST
- URL: `http://localhost:8080/token`
- Headers: `Content-Type: application/x-www-form-urlencoded`
- Body: `grant_type=authorization_code&code=...`

**3. Protected Resource:**
- Method: GET
- URL: `http://localhost:8080/f1/stream?year=2024`
- Headers: `Authorization: Bearer YOUR_TOKEN`

### 8. OAuth Security Notes

**For Development Only:**
- This OAuth implementation is for testing/demonstration
- Uses simple in-memory storage
- Not suitable for production use

**Security Features:**
- Authorization code flow (not implicit)
- State parameter for CSRF protection
- Token expiration and refresh
- Scope-based access control

### 9. Troubleshooting OAuth

**Invalid Authorization Code:**
- Codes expire after 10 minutes
- Each code can only be used once
- Generate a new code if expired

**Token Expired:**
- Access tokens expire after 1 hour
- Use refresh token to get new access token
- Re-authorize if refresh token expired

**Connection Refused:**
- Ensure HTTP server is running (`make http`)
- Check server is on correct port (8080)
- Verify no firewall blocking connections

## Next Steps

After mastering both MCP Inspector and OAuth:
1. Compare MCP vs HTTP API performance
2. Build applications using both protocols
3. Explore real-time streaming capabilities
4. Integrate F1 data into web applications
5. Develop custom OAuth clients for production use