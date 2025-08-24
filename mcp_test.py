#!/usr/bin/env python3
"""
Test script for MCP Inspector compatibility
"""

import asyncio
import json
from f1_mcp_server.server import app

async def test_mcp_tools():
    """Test MCP tools directly."""
    print("🏎️  Testing F1 MCP Server Tools")
    print("=" * 40)
    
    # Test list_tools
    print("\n1. Testing list_tools...")
    tools = await app.list_tools()
    print(f"Available tools: {len(tools)}")
    for tool in tools:
        print(f"  - {tool.name}: {tool.description}")
    
    # Test get_race_schedule
    print("\n2. Testing get_race_schedule...")
    try:
        result = await app.call_tool("get_race_schedule", {"year": 2024})
        print("✅ Race schedule retrieved successfully")
        print(f"Response length: {len(result[0].text)} characters")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test get_session_results
    print("\n3. Testing get_session_results...")
    try:
        result = await app.call_tool("get_session_results", {
            "year": 2024,
            "round_number": 1,
            "session": "R"
        })
        print("✅ Session results retrieved successfully")
        print(f"Response length: {len(result[0].text)} characters")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n✅ MCP tool testing completed!")
    print("\nTo test with MCP Inspector:")
    print("1. Install: npm install -g @modelcontextprotocol/inspector")
    print("2. Run: mcp-inspector python -m f1_mcp_server.server")

if __name__ == "__main__":
    asyncio.run(test_mcp_tools())