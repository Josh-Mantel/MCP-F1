#!/usr/bin/env python3
"""
Test runner for F1 MCP Server
"""

import asyncio
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor

async def test_mcp_server():
    """Test MCP server functionality."""
    print("🧪 Testing MCP Server...")
    
    try:
        # Run MCP test with uv
        result = subprocess.run([
            "uv", "run", "python", "mcp_test.py"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ MCP server test passed")
            print(result.stdout)
        else:
            print("❌ MCP server test failed")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("⏰ MCP server test timed out")
    except Exception as e:
        print(f"❌ MCP server test error: {e}")

async def test_http_server():
    """Test HTTP server functionality."""
    print("\n🧪 Testing HTTP Server...")
    
    try:
        # Start HTTP server in background with uv
        process = subprocess.Popen([
            "uv", "run", "python", "-m", "f1_mcp_server.combined_server", 
            "--mode", "http", "--http-port", "8081"
        ])
        
        # Wait a bit for server to start
        await asyncio.sleep(3)
        
        # Test basic endpoints
        import urllib.request
        import json
        
        # Test authorization endpoint
        try:
            auth_url = "http://localhost:8081/authorize?client_id=f1-mcp-client&redirect_uri=http://localhost:8081/callback&response_type=code"
            response = urllib.request.urlopen(auth_url)
            print("✅ Authorization endpoint accessible")
        except Exception as e:
            print(f"❌ Authorization endpoint error: {e}")
        
        # Cleanup
        process.terminate()
        process.wait(timeout=5)
        print("✅ HTTP server test completed")
        
    except Exception as e:
        print(f"❌ HTTP server test error: {e}")

async def main():
    """Main test runner."""
    print("🏎️  F1 MCP Server Test Suite")
    print("=" * 40)
    
    # Run tests
    await test_mcp_server()
    await test_http_server()
    
    print("\n🏁 Test suite completed!")
    print("\nManual testing:")
    print("1. MCP Inspector: mcp-inspector uv run python -m f1_mcp_server.server")
    print("2. HTTP OAuth flow: uv run python test_client.py")
    print("3. HTTP streaming: curl -H 'Authorization: Bearer <token>' http://localhost:8080/f1/stream")

if __name__ == "__main__":
    asyncio.run(main())