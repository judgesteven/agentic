"""
Base tool interface and registry for the agentic AI system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Result from a tool execution."""
    
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseTool(ABC):
    """Base class for all tools."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.parameters: Dict[str, Any] = {}
    
    @abstractmethod
    async def execute(self, **kwargs) -> ToolResult:
        """Execute the tool with given parameters."""
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get the tool's schema for parameter validation."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate input parameters."""
        # Basic validation - subclasses can override
        return True


class ToolRegistry:
    """Registry for managing available tools."""
    
    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Register a new tool."""
        self._tools[tool.name] = tool
    
    def unregister(self, tool_name: str) -> None:
        """Unregister a tool."""
        if tool_name in self._tools:
            del self._tools[tool_name]
    
    def get_tool(self, tool_name: str) -> Optional[BaseTool]:
        """Get a tool by name."""
        return self._tools.get(tool_name)
    
    def list_tools(self) -> List[str]:
        """List all available tool names."""
        return list(self._tools.keys())
    
    def get_tool_schemas(self) -> Dict[str, Dict[str, Any]]:
        """Get schemas for all registered tools."""
        return {name: tool.get_schema() for name, tool in self._tools.items()}
    
    async def execute_tool(self, tool_name: str, **kwargs) -> ToolResult:
        """Execute a tool by name."""
        tool = self.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                error=f"Tool '{tool_name}' not found"
            )
        
        try:
            if not tool.validate_parameters(**kwargs):
                return ToolResult(
                    success=False,
                    error=f"Invalid parameters for tool '{tool_name}'"
                )
            
            return await tool.execute(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Error executing tool '{tool_name}': {str(e)}"
            )


# Global tool registry instance
tool_registry = ToolRegistry() 