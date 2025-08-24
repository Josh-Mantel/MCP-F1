"""
HTTP streaming server for F1 MCP Server
Provides HTTP endpoints with OAuth authentication
"""

import json
import asyncio
from typing import Dict, Any, Optional
from urllib.parse import parse_qs, urlparse
import logging

from .auth import oauth_provider

logger = logging.getLogger(__name__)

class HTTPStreamServer:
    """Basic HTTP server with streaming support."""
    
    def __init__(self, host: str = "localhost", port: int = 8080):
        self.host = host
        self.port = port
        self.server = None
    
    async def start(self):
        """Start the HTTP server."""
        self.server = await asyncio.start_server(
            self.handle_client,
            self.host,
            self.port
        )
        logger.info(f"HTTP server started on {self.host}:{self.port}")
        
    async def stop(self):
        """Stop the HTTP server."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
    
    async def handle_client(self, reader, writer):
        """Handle incoming HTTP requests."""
        try:
            # Read HTTP request
            request_line = await reader.readline()
            if not request_line:
                return
            
            request_line = request_line.decode().strip()
            method, path, version = request_line.split(' ', 2)
            
            # Read headers
            headers = {}
            while True:
                line = await reader.readline()
                if line == b'\r\n':
                    break
                if line:
                    key, value = line.decode().strip().split(':', 1)
                    headers[key.lower()] = value.strip()
            
            # Read body if present
            body = b""
            if 'content-length' in headers:
                content_length = int(headers['content-length'])
                body = await reader.read(content_length)
            
            # Route request
            await self.route_request(writer, method, path, headers, body)
            
        except Exception as e:
            logger.error(f"Error handling request: {e}")
            await self.send_error(writer, 500, "Internal Server Error")
        finally:
            writer.close()
            await writer.wait_closed()
    
    async def route_request(self, writer, method: str, path: str, headers: Dict[str, str], body: bytes):
        """Route HTTP requests to appropriate handlers."""
        parsed_url = urlparse(path)
        path_only = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        if path_only == "/authorize" and method == "GET":
            await self.handle_authorize(writer, query_params)
        elif path_only == "/token" and method == "POST":
            await self.handle_token(writer, body)
        elif path_only == "/f1/stream" and method == "GET":
            await self.handle_f1_stream(writer, headers, query_params)
        elif path_only == "/callback" and method == "GET":
            await self.handle_callback(writer, query_params)
        else:
            await self.send_error(writer, 404, "Not Found")
    
    async def handle_authorize(self, writer, query_params: Dict[str, list]):
        """Handle OAuth authorization endpoint."""
        try:
            client_id = query_params.get("client_id", [None])[0]
            redirect_uri = query_params.get("redirect_uri", [None])[0]
            state = query_params.get("state", [None])[0]
            
            if not client_id:
                await self.send_error(writer, 400, "Missing client_id")
                return
            
            # Generate authorization code
            auth_code = oauth_provider.generate_authorization_code(client_id)
            
            # Redirect with authorization code
            redirect_url = f"{redirect_uri}?code={auth_code}"
            if state:
                redirect_url += f"&state={state}"
            
            response = f"""HTTP/1.1 302 Found\r
Location: {redirect_url}\r
Content-Length: 0\r
\r
"""
            writer.write(response.encode())
            await writer.drain()
            
        except Exception as e:
            await self.send_error(writer, 400, str(e))
    
    async def handle_token(self, writer, body: bytes):
        """Handle OAuth token endpoint."""
        try:
            # Parse form data
            body_str = body.decode()
            params = parse_qs(body_str)
            
            grant_type = params.get("grant_type", [None])[0]
            
            if grant_type == "authorization_code":
                code = params.get("code", [None])[0]
                client_id = params.get("client_id", [None])[0]
                client_secret = params.get("client_secret", [None])[0]
                
                token_data = oauth_provider.exchange_code_for_token(code, client_id, client_secret)
                
            elif grant_type == "refresh_token":
                refresh_token = params.get("refresh_token", [None])[0]
                token_data = oauth_provider.refresh_access_token(refresh_token)
                
            else:
                await self.send_error(writer, 400, "Unsupported grant_type")
                return
            
            response_body = json.dumps(token_data)
            response = f"""HTTP/1.1 200 OK\r
Content-Type: application/json\r
Content-Length: {len(response_body)}\r
\r
{response_body}"""
            
            writer.write(response.encode())
            await writer.drain()
            
        except Exception as e:
            await self.send_error(writer, 400, str(e))
    
    async def handle_f1_stream(self, writer, headers: Dict[str, str], query_params: Dict[str, list]):
        """Handle F1 data streaming endpoint."""
        try:
            # Check authorization
            auth_header = headers.get("authorization", "")
            if not auth_header.startswith("Bearer "):
                await self.send_error(writer, 401, "Unauthorized")
                return
            
            access_token = auth_header[7:]  # Remove "Bearer " prefix
            if not oauth_provider.validate_token(access_token):
                await self.send_error(writer, 401, "Invalid or expired token")
                return
            
            # Start streaming response
            response_headers = """HTTP/1.1 200 OK\r
Content-Type: text/event-stream\r
Cache-Control: no-cache\r
Connection: keep-alive\r
Access-Control-Allow-Origin: *\r
\r
"""
            writer.write(response_headers.encode())
            await writer.drain()
            
            # Stream F1 data
            await self.stream_f1_data(writer, query_params)
            
        except Exception as e:
            logger.error(f"Error in F1 stream: {e}")
            await self.send_error(writer, 500, str(e))
    
    async def stream_f1_data(self, writer, query_params: Dict[str, list]):
        """Stream F1 data as Server-Sent Events."""
        try:
            year = int(query_params.get("year", ["2024"])[0])
            
            # Send initial data
            event_data = {
                "type": "schedule",
                "year": year,
                "message": f"Starting F1 {year} data stream..."
            }
            
            await self.send_sse_event(writer, "f1_data", event_data)
            
            # Simulate streaming updates every 5 seconds
            for i in range(10):
                await asyncio.sleep(5)
                
                update_data = {
                    "type": "update",
                    "timestamp": str(asyncio.get_event_loop().time()),
                    "message": f"Stream update #{i + 1}",
                    "year": year
                }
                
                await self.send_sse_event(writer, "f1_update", update_data)
            
            # Send completion event
            completion_data = {
                "type": "complete",
                "message": "Stream completed"
            }
            await self.send_sse_event(writer, "f1_complete", completion_data)
            
        except Exception as e:
            error_data = {
                "type": "error",
                "message": str(e)
            }
            await self.send_sse_event(writer, "f1_error", error_data)
    
    async def send_sse_event(self, writer, event_type: str, data: Dict[str, Any]):
        """Send Server-Sent Event."""
        event = f"event: {event_type}\n"
        event += f"data: {json.dumps(data)}\n\n"
        
        writer.write(event.encode())
        await writer.drain()
    
    async def handle_callback(self, writer, query_params: Dict[str, list]):
        """Handle OAuth callback (for testing)."""
        code = query_params.get("code", [None])[0]
        state = query_params.get("state", [None])[0]
        
        response_body = f"""
<!DOCTYPE html>
<html>
<head>
    <title>OAuth Callback</title>
</head>
<body>
    <h1>OAuth Authorization Complete</h1>
    <p>Authorization Code: <code>{code}</code></p>
    <p>State: <code>{state}</code></p>
    <p>You can now exchange this code for an access token.</p>
</body>
</html>
"""
        
        response = f"""HTTP/1.1 200 OK\r
Content-Type: text/html\r
Content-Length: {len(response_body)}\r
\r
{response_body}"""
        
        writer.write(response.encode())
        await writer.drain()
    
    async def send_error(self, writer, status_code: int, message: str):
        """Send HTTP error response."""
        response_body = json.dumps({"error": message})
        response = f"""HTTP/1.1 {status_code} {message}\r
Content-Type: application/json\r
Content-Length: {len(response_body)}\r
\r
{response_body}"""
        
        writer.write(response.encode())
        await writer.drain()