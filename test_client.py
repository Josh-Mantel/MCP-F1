#!/usr/bin/env python3
"""
Test client for F1 MCP Server
Demonstrates OAuth flow and HTTP streaming
"""

import asyncio
import json
import urllib.parse
import urllib.request
from typing import Dict, Any

class F1TestClient:
    """Test client for F1 MCP Server."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client_id = "f1-mcp-client"
        self.client_secret = "f1-mcp-secret-key"
        self.access_token = None
    
    def get_authorization_url(self) -> str:
        """Get OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": f"{self.base_url}/callback",
            "scope": "f1:read",
            "state": "test-state"
        }
        return f"{self.base_url}/authorize?{urllib.parse.urlencode(params)}"
    
    def exchange_code_for_token(self, authorization_code: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        data = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": f"{self.base_url}/callback"
        }
        
        encoded_data = urllib.parse.urlencode(data).encode()
        
        req = urllib.request.Request(
            f"{self.base_url}/token",
            data=encoded_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        with urllib.request.urlopen(req) as response:
            token_data = json.loads(response.read().decode())
            self.access_token = token_data["access_token"]
            return token_data
    
    async def test_stream(self, year: int = 2024):
        """Test F1 data streaming."""
        if not self.access_token:
            raise ValueError("No access token. Please authenticate first.")
        
        print(f"🏎️  Testing F1 stream for year {year}...")
        
        # This is a simplified example - in practice you'd use aiohttp or similar
        print(f"Stream URL: {self.base_url}/f1/stream?year={year}")
        print(f"Authorization: Bearer {self.access_token}")
        print("\nTo test streaming, use curl:")
        print(f'curl -H "Authorization: Bearer {self.access_token}" "{self.base_url}/f1/stream?year={year}"')

def main():
    """Main test function."""
    client = F1TestClient()
    
    print("🏎️  F1 MCP Server Test Client")
    print("=" * 40)
    
    # Step 1: Get authorization URL
    auth_url = client.get_authorization_url()
    print(f"1. Visit this URL to authorize: {auth_url}")
    
    # Step 2: Get authorization code from user
    auth_code = input("\n2. Enter the authorization code from the callback: ").strip()
    
    if not auth_code:
        print("No authorization code provided. Exiting.")
        return
    
    try:
        # Step 3: Exchange code for token
        print("\n3. Exchanging code for access token...")
        token_data = client.exchange_code_for_token(auth_code)
        print(f"✅ Access token obtained: {token_data['access_token'][:20]}...")
        print(f"   Expires in: {token_data['expires_in']} seconds")
        
        # Step 4: Test streaming
        print("\n4. Testing stream endpoint...")
        asyncio.run(client.test_stream())
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()