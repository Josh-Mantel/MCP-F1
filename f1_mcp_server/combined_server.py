#!/usr/bin/env python3
"""
Combined F1 MCP Server - Supports both MCP protocol and HTTP streaming
"""

import asyncio
import argparse
import logging
from typing import Optional

from .server import app as mcp_app, main as mcp_main
from .http_server import HTTPStreamServer
from .auth import oauth_provider

logger = logging.getLogger(__name__)

class CombinedF1Server:
    """Combined server supporting both MCP and HTTP protocols."""
    
    def __init__(self, http_host: str = "localhost", http_port: int = 8080):
        self.http_server = HTTPStreamServer(http_host, http_port)
        self.http_host = http_host
        self.http_port = http_port
    
    async def start_http_only(self):
        """Start only the HTTP server."""
        logger.info("Starting F1 HTTP server...")
        await self.http_server.start()
        
        # Print OAuth information
        auth_url = oauth_provider.generate_authorization_url()
        print(f"\n🏎️  F1 MCP HTTP Server started!")
        print(f"📍 Server: http://{self.http_host}:{self.http_port}")
        print(f"🔐 OAuth Authorization URL: {auth_url}")
        print(f"📊 Stream endpoint: http://{self.http_host}:{self.http_port}/f1/stream")
        print(f"🔑 Client ID: {oauth_provider.client_id}")
        print(f"🔒 Client Secret: {oauth_provider.client_secret}")
        print("\nTo test the OAuth flow:")
        print("1. Visit the authorization URL above")
        print("2. Copy the authorization code from the callback")
        print("3. Exchange it for an access token at /token endpoint")
        print("4. Use the access token to access /f1/stream")
        print("\nPress Ctrl+C to stop the server")
        
        try:
            # Keep the server running
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down HTTP server...")
            await self.http_server.stop()
    
    async def start_mcp_only(self):
        """Start only the MCP server."""
        logger.info("Starting F1 MCP server...")
        await mcp_main()

async def main():
    """Main entry point with argument parsing."""
    parser = argparse.ArgumentParser(description="F1 MCP Server")
    parser.add_argument(
        "--mode",
        choices=["mcp", "http", "both"],
        default="mcp",
        help="Server mode (default: mcp)"
    )
    parser.add_argument(
        "--http-host",
        default="localhost",
        help="HTTP server host (default: localhost)"
    )
    parser.add_argument(
        "--http-port",
        type=int,
        default=8080,
        help="HTTP server port (default: 8080)"
    )
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Log level (default: INFO)"
    )
    
    args = parser.parse_args()
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    server = CombinedF1Server(args.http_host, args.http_port)
    
    if args.mode == "mcp":
        await server.start_mcp_only()
    elif args.mode == "http":
        await server.start_http_only()
    elif args.mode == "both":
        # Start both servers concurrently
        await asyncio.gather(
            server.start_mcp_only(),
            server.start_http_only()
        )

if __name__ == "__main__":
    asyncio.run(main())