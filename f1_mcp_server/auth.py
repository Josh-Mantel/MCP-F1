"""
OAuth implementation for F1 MCP Server
Basic OAuth 2.0 flow for demonstration purposes
"""

import base64
import hashlib
import secrets
import urllib.parse
from typing import Dict, Optional
from datetime import datetime, timedelta

class BasicOAuthProvider:
    """Basic OAuth 2.0 provider for demonstration."""
    
    def __init__(self):
        self.client_id = "f1-mcp-client"
        self.client_secret = "f1-mcp-secret-key"
        self.redirect_uri = "http://localhost:8080/callback"
        self.authorization_codes = {}
        self.access_tokens = {}
        self.refresh_tokens = {}
    
    def generate_authorization_url(self, state: Optional[str] = None) -> str:
        """Generate OAuth authorization URL."""
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            "response_type": "code",
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "scope": "f1:read",
            "state": state
        }
        
        base_url = "http://localhost:8080/authorize"
        return f"{base_url}?{urllib.parse.urlencode(params)}"
    
    def generate_authorization_code(self, client_id: str) -> str:
        """Generate authorization code."""
        if client_id != self.client_id:
            raise ValueError("Invalid client_id")
        
        code = secrets.token_urlsafe(32)
        self.authorization_codes[code] = {
            "client_id": client_id,
            "expires_at": datetime.now() + timedelta(minutes=10),
            "used": False
        }
        return code
    
    def exchange_code_for_token(self, code: str, client_id: str, client_secret: str) -> Dict[str, str]:
        """Exchange authorization code for access token."""
        if client_id != self.client_id or client_secret != self.client_secret:
            raise ValueError("Invalid client credentials")
        
        if code not in self.authorization_codes:
            raise ValueError("Invalid authorization code")
        
        code_data = self.authorization_codes[code]
        
        if code_data["used"]:
            raise ValueError("Authorization code already used")
        
        if datetime.now() > code_data["expires_at"]:
            raise ValueError("Authorization code expired")
        
        # Mark code as used
        code_data["used"] = True
        
        # Generate tokens
        access_token = secrets.token_urlsafe(32)
        refresh_token = secrets.token_urlsafe(32)
        
        # Store tokens
        self.access_tokens[access_token] = {
            "client_id": client_id,
            "expires_at": datetime.now() + timedelta(hours=1),
            "scope": "f1:read"
        }
        
        self.refresh_tokens[refresh_token] = {
            "client_id": client_id,
            "access_token": access_token,
            "expires_at": datetime.now() + timedelta(days=30)
        }
        
        return {
            "access_token": access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "refresh_token": refresh_token,
            "scope": "f1:read"
        }
    
    def validate_token(self, access_token: str) -> bool:
        """Validate access token."""
        if access_token not in self.access_tokens:
            return False
        
        token_data = self.access_tokens[access_token]
        return datetime.now() < token_data["expires_at"]
    
    def refresh_access_token(self, refresh_token: str) -> Dict[str, str]:
        """Refresh access token using refresh token."""
        if refresh_token not in self.refresh_tokens:
            raise ValueError("Invalid refresh token")
        
        refresh_data = self.refresh_tokens[refresh_token]
        
        if datetime.now() > refresh_data["expires_at"]:
            raise ValueError("Refresh token expired")
        
        # Invalidate old access token
        old_access_token = refresh_data["access_token"]
        if old_access_token in self.access_tokens:
            del self.access_tokens[old_access_token]
        
        # Generate new access token
        new_access_token = secrets.token_urlsafe(32)
        
        self.access_tokens[new_access_token] = {
            "client_id": refresh_data["client_id"],
            "expires_at": datetime.now() + timedelta(hours=1),
            "scope": "f1:read"
        }
        
        # Update refresh token mapping
        refresh_data["access_token"] = new_access_token
        
        return {
            "access_token": new_access_token,
            "token_type": "Bearer",
            "expires_in": 3600,
            "scope": "f1:read"
        }

# Global OAuth provider instance
oauth_provider = BasicOAuthProvider()