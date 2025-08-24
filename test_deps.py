#!/usr/bin/env python3
"""
Test script to verify Python 3.13 compatibility and dependencies
"""

import sys
import importlib.util

def check_python_version():
    """Check if we're running Python 3.13."""
    print(f"🐍 Python version: {sys.version}")
    
    if sys.version_info.major != 3 or sys.version_info.minor != 13:
        print("⚠️  Warning: This project is designed for Python 3.13")
        return False
    
    print("✅ Python 3.13 detected")
    return True

def check_dependency(name: str, import_name: str = None):
    """Check if a dependency can be imported."""
    if import_name is None:
        import_name = name
    
    try:
        spec = importlib.util.find_spec(import_name)
        if spec is None:
            print(f"❌ {name} not found")
            return False
        
        # Try to import
        module = importlib.import_module(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"✅ {name} {version}")
        return True
        
    except ImportError as e:
        print(f"❌ {name} import failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Testing Python 3.13 compatibility and dependencies")
    print("=" * 55)
    
    # Check Python version
    python_ok = check_python_version()
    
    print("\n📦 Checking dependencies...")
    
    # Core dependencies
    deps = [
        ("MCP", "mcp"),
        ("FastF1", "fastf1"),
        ("HTTPX", "httpx"),
        ("Pydantic", "pydantic"),
        ("Pandas", "pandas"),
        ("NumPy", "numpy")
    ]
    
    all_ok = True
    for name, import_name in deps:
        if not check_dependency(name, import_name):
            all_ok = False
    
    print("\n" + "=" * 55)
    if python_ok and all_ok:
        print("🎉 All dependencies are compatible with Python 3.13!")
        return 0
    else:
        print("❌ Some issues found. Run 'make install' to fix dependencies.")
        return 1

if __name__ == "__main__":
    sys.exit(main())