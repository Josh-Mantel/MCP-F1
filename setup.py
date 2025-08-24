#!/usr/bin/env python3
"""
Setup script for F1 MCP Server using uv
"""

import subprocess
import sys
import os
import shutil

def check_uv_installed():
    """Check if uv is installed."""
    if shutil.which("uv") is None:
        print("❌ uv is not installed!")
        print("\nTo install uv:")
        print("  macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
        print("  Windows: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        print("  Or visit: https://docs.astral.sh/uv/getting-started/installation/")
        return False
    return True

def install_dependencies():
    """Install required dependencies using uv."""
    print("🏎️  Installing F1 MCP Server dependencies with uv...")
    
    # Sync dependencies
    subprocess.check_call(["uv", "sync"])
    
    # Install in development mode
    subprocess.check_call(["uv", "pip", "install", "-e", "."])
    
    print("✅ Dependencies installed successfully!")

def test_installation():
    """Test the installation."""
    print("\n🧪 Testing installation...")
    
    try:
        # Run with uv python
        result = subprocess.run([
            "uv", "run", "python", "-c", 
            "import f1_mcp_server; import fastf1; import mcp; print('✅ All imports successful')"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
            print("\n🎉 Installation test passed!")
            return True
        else:
            print(f"❌ Import error: {result.stderr}")
            return False
        
    except Exception as e:
        print(f"❌ Test error: {e}")
        return False

def main():
    """Main setup function."""
    print("🏎️  F1 MCP Server Setup (uv)")
    print("=" * 35)
    
    # Check if uv is installed
    if not check_uv_installed():
        sys.exit(1)
    
    # Check Python version
    result = subprocess.run(["uv", "python", "--version"], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ uv detected: {result.stdout.strip()}")
    
    try:
        install_dependencies()
        
        if test_installation():
            print("\n🚀 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Test MCP mode: make mcp")
            print("2. Test HTTP mode: make http")
            print("3. Run MCP Inspector: make inspector")
            print("4. Test OAuth flow: make test-oauth")
            print("5. Run all tests: make test")
            print("\nOr use uv directly:")
            print("- uv run python -m f1_mcp_server.server")
            print("- uv run python -m f1_mcp_server.combined_server --mode http")
        else:
            print("\n❌ Setup completed with errors")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()