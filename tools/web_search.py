"""
Web search tool for the agentic AI system.
"""

import aiohttp
import json
from typing import Any, Dict, List
from .base import BaseTool, ToolResult


class WebSearchTool(BaseTool):
    """Tool for performing web searches."""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="Search the web for information using DuckDuckGo"
        )
        self.parameters = {
            "query": {
                "type": "string",
                "description": "The search query",
                "required": True
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of results to return",
                "default": 5
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute web search."""
        query = kwargs.get("query")
        max_results = kwargs.get("max_results", 5)
        
        if not query:
            return ToolResult(
                success=False,
                error="Query parameter is required"
            )
        
        try:
            # Using DuckDuckGo Instant Answer API (no API key required)
            url = "https://api.duckduckgo.com/"
            params = {
                "q": query,
                "format": "json",
                "no_html": "1",
                "skip_disambig": "1"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        results = []
                        
                        # Extract instant answer
                        if data.get("Abstract"):
                            results.append({
                                "title": data.get("Heading", "Instant Answer"),
                                "snippet": data.get("Abstract"),
                                "url": data.get("AbstractURL", ""),
                                "type": "instant_answer"
                            })
                        
                        # Extract related topics
                        for topic in data.get("RelatedTopics", [])[:max_results]:
                            if isinstance(topic, dict) and topic.get("Text"):
                                results.append({
                                    "title": topic.get("Text", "").split(" - ")[0] if " - " in topic.get("Text", "") else topic.get("Text", "")[:50],
                                    "snippet": topic.get("Text", ""),
                                    "url": topic.get("FirstURL", ""),
                                    "type": "related_topic"
                                })
                        
                        return ToolResult(
                            success=True,
                            data={
                                "query": query,
                                "results": results[:max_results],
                                "total_results": len(results)
                            },
                            metadata={
                                "source": "DuckDuckGo",
                                "max_results": max_results
                            }
                        )
                    else:
                        return ToolResult(
                            success=False,
                            error=f"HTTP {response.status}: {response.reason}"
                        )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Search failed: {str(e)}"
            )
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate search parameters."""
        query = kwargs.get("query")
        if not query or not isinstance(query, str):
            return False
        
        max_results = kwargs.get("max_results", 5)
        if not isinstance(max_results, int) or max_results < 1 or max_results > 20:
            return False
        
        return True 