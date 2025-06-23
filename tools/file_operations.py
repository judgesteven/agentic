"""
File operations tool for the agentic AI system.
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from .base import BaseTool, ToolResult


class FileOperationsTool(BaseTool):
    """Tool for file system operations."""
    
    def __init__(self):
        super().__init__(
            name="file_operations",
            description="Perform file system operations like read, write, list, and delete files"
        )
        self.parameters = {
            "operation": {
                "type": "string",
                "description": "The operation to perform: read, write, list, delete, create_directory",
                "required": True,
                "enum": ["read", "write", "list", "delete", "create_directory"]
            },
            "path": {
                "type": "string",
                "description": "The file or directory path",
                "required": True
            },
            "content": {
                "type": "string",
                "description": "Content to write (for write operation)",
                "required": False
            },
            "encoding": {
                "type": "string",
                "description": "File encoding (default: utf-8)",
                "default": "utf-8"
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute file operation."""
        operation = kwargs.get("operation")
        path = kwargs.get("path")
        content = kwargs.get("content")
        encoding = kwargs.get("encoding", "utf-8")
        
        if not operation or not path:
            return ToolResult(
                success=False,
                error="Operation and path parameters are required"
            )
        
        try:
            # Ensure path is within safe boundaries
            safe_path = self._ensure_safe_path(path)
            
            if operation == "read":
                return await self._read_file(safe_path, encoding)
            elif operation == "write":
                return await self._write_file(safe_path, content, encoding)
            elif operation == "list":
                return await self._list_directory(safe_path)
            elif operation == "delete":
                return await self._delete_file(safe_path)
            elif operation == "create_directory":
                return await self._create_directory(safe_path)
            else:
                return ToolResult(
                    success=False,
                    error=f"Unknown operation: {operation}"
                )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"File operation failed: {str(e)}"
            )
    
    def _ensure_safe_path(self, path: str) -> Path:
        """Ensure the path is safe and within allowed boundaries."""
        # Convert to Path object
        path_obj = Path(path).resolve()
        
        # For safety, only allow operations in the current working directory
        # In a production system, you might want more sophisticated path validation
        cwd = Path.cwd().resolve()
        
        if not str(path_obj).startswith(str(cwd)):
            raise ValueError(f"Path {path} is outside allowed directory")
        
        return path_obj
    
    async def _read_file(self, path: Path, encoding: str) -> ToolResult:
        """Read a file."""
        if not path.exists():
            return ToolResult(
                success=False,
                error=f"File does not exist: {path}"
            )
        
        if not path.is_file():
            return ToolResult(
                success=False,
                error=f"Path is not a file: {path}"
            )
        
        try:
            with open(path, 'r', encoding=encoding) as f:
                content = f.read()
            
            return ToolResult(
                success=True,
                data={
                    "content": content,
                    "size": len(content),
                    "path": str(path)
                },
                metadata={
                    "operation": "read",
                    "encoding": encoding
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to read file: {str(e)}"
            )
    
    async def _write_file(self, path: Path, content: str, encoding: str) -> ToolResult:
        """Write content to a file."""
        if content is None:
            return ToolResult(
                success=False,
                error="Content is required for write operation"
            )
        
        try:
            # Create parent directories if they don't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding=encoding) as f:
                f.write(content)
            
            return ToolResult(
                success=True,
                data={
                    "path": str(path),
                    "size": len(content),
                    "created": not path.exists()  # True if file was created
                },
                metadata={
                    "operation": "write",
                    "encoding": encoding
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to write file: {str(e)}"
            )
    
    async def _list_directory(self, path: Path) -> ToolResult:
        """List contents of a directory."""
        if not path.exists():
            return ToolResult(
                success=False,
                error=f"Directory does not exist: {path}"
            )
        
        if not path.is_dir():
            return ToolResult(
                success=False,
                error=f"Path is not a directory: {path}"
            )
        
        try:
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                })
            
            return ToolResult(
                success=True,
                data={
                    "path": str(path),
                    "items": items,
                    "count": len(items)
                },
                metadata={
                    "operation": "list"
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to list directory: {str(e)}"
            )
    
    async def _delete_file(self, path: Path) -> ToolResult:
        """Delete a file or directory."""
        if not path.exists():
            return ToolResult(
                success=False,
                error=f"Path does not exist: {path}"
            )
        
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                import shutil
                shutil.rmtree(path)
            
            return ToolResult(
                success=True,
                data={
                    "path": str(path),
                    "deleted": True
                },
                metadata={
                    "operation": "delete"
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to delete: {str(e)}"
            )
    
    async def _create_directory(self, path: Path) -> ToolResult:
        """Create a directory."""
        try:
            path.mkdir(parents=True, exist_ok=True)
            
            return ToolResult(
                success=True,
                data={
                    "path": str(path),
                    "created": True
                },
                metadata={
                    "operation": "create_directory"
                }
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Failed to create directory: {str(e)}"
            )
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate file operation parameters."""
        operation = kwargs.get("operation")
        if operation not in ["read", "write", "list", "delete", "create_directory"]:
            return False
        
        path = kwargs.get("path")
        if not path or not isinstance(path, str):
            return False
        
        if operation == "write" and kwargs.get("content") is None:
            return False
        
        return True 