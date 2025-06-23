"""
API client tool for the agentic AI system.
"""

import aiohttp
import json
from typing import Any, Dict, Optional
from .base import BaseTool, ToolResult


class APIClientTool(BaseTool):
    """Tool for making API calls."""
    
    def __init__(self):
        super().__init__(
            name="api_client",
            description="Make HTTP requests to external APIs"
        )
        self.parameters = {
            "url": {
                "type": "string",
                "description": "The URL to make the request to",
                "required": True
            },
            "method": {
                "type": "string",
                "description": "HTTP method (GET, POST, PUT, DELETE)",
                "default": "GET",
                "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"]
            },
            "headers": {
                "type": "object",
                "description": "HTTP headers to include in the request",
                "default": {}
            },
            "data": {
                "type": "object",
                "description": "Data to send with the request (for POST/PUT)",
                "default": {}
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds",
                "default": 30
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute API request."""
        url = kwargs.get("url")
        method = kwargs.get("method", "GET").upper()
        headers = kwargs.get("headers", {})
        data = kwargs.get("data", {})
        timeout = kwargs.get("timeout", 30)
        
        if not url:
            return ToolResult(
                success=False,
                error="URL parameter is required"
            )
        
        try:
            timeout_obj = aiohttp.ClientTimeout(total=timeout)
            
            async with aiohttp.ClientSession(timeout=timeout_obj) as session:
                if method == "GET":
                    async with session.get(url, headers=headers) as response:
                        return await self._handle_response(response)
                
                elif method == "POST":
                    async with session.post(url, headers=headers, json=data) as response:
                        return await self._handle_response(response)
                
                elif method == "PUT":
                    async with session.put(url, headers=headers, json=data) as response:
                        return await self._handle_response(response)
                
                elif method == "DELETE":
                    async with session.delete(url, headers=headers) as response:
                        return await self._handle_response(response)
                
                elif method == "PATCH":
                    async with session.patch(url, headers=headers, json=data) as response:
                        return await self._handle_response(response)
                
                else:
                    return ToolResult(
                        success=False,
                        error=f"Unsupported HTTP method: {method}"
                    )
        
        except aiohttp.ClientError as e:
            return ToolResult(
                success=False,
                error=f"HTTP client error: {str(e)}"
            )
        except asyncio.TimeoutError:
            return ToolResult(
                success=False,
                error=f"Request timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"API request error: {str(e)}"
            )
    
    async def _handle_response(self, response: aiohttp.ClientResponse) -> ToolResult:
        """Handle the API response."""
        try:
            # Try to get JSON response
            try:
                response_data = await response.json()
            except:
                # Fall back to text response
                response_data = await response.text()
            
            return ToolResult(
                success=response.status < 400,
                data={
                    "status_code": response.status,
                    "headers": dict(response.headers),
                    "data": response_data
                },
                error=None if response.status < 400 else f"HTTP {response.status}: {response.reason}",
                metadata={
                    "url": str(response.url),
                    "method": response.method
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error processing response: {str(e)}"
            )
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate API request parameters."""
        url = kwargs.get("url")
        if not url or not isinstance(url, str):
            return False
        
        method = kwargs.get("method", "GET")
        if method not in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
            return False
        
        timeout = kwargs.get("timeout", 30)
        if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
            return False
        
        return True


# Import asyncio for timeout handling
import asyncio 