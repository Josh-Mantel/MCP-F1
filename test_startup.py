#!/usr/bin/env python3
"""
Test script to verify the server can start without errors
"""

import sys
import os

def test_server_import():
    """Test that the server module can be imported."""
    print("🧪 Testing server import...")
    
    try:
        # Ensure cache directory exists
        if not os.path.exists("cache"):
            os.makedirs("cache", exist_ok=True)
            print("📁 Created cache directory")
        
        # Test server import
        from f1_mcp_server import server
        print("✅ Server module imported successfully")
        
        # Test that FastF1 cache is working
        import fastf1
        print("✅ FastF1 imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

def test_combined_server_import():
    """Test that the combined server can be imported."""
    print("\n🧪 Testing combined server import...")
    
    try:
        from f1_mcp_server import combined_server
        print("✅ Combined server module imported successfully")
        return True
        
    except Exception as e:
        print(f"❌ Combined server import failed: {e}")
        return False

def main():
    """Main test function."""
    print("🏎️  F1 MCP Server Startup Test")
    print("=" * 35)
    
    server_ok = test_server_import()
    combined_ok = test_combined_server_import()
    
    print("\n" + "=" * 35)
    if server_ok and combined_ok:
        print("🎉 All server modules can be imported successfully!")
        print("\nReady to run:")
        print("  make mcp    - Start MCP server")
        print("  make http   - Start HTTP server")
        return 0
    else:
        print("❌ Some startup issues found.")
        return 1

if __name__ == "__main__":
    sys.exit(main())