"""
Code execution tool for the agentic AI system.
"""

import subprocess
import tempfile
import os
from typing import Any, Dict
from .base import BaseTool, ToolResult


class CodeExecutionTool(BaseTool):
    """Tool for executing code safely."""
    
    def __init__(self):
        super().__init__(
            name="code_execution",
            description="Execute Python code safely in a controlled environment"
        )
        self.parameters = {
            "code": {
                "type": "string",
                "description": "The Python code to execute",
                "required": True
            },
            "timeout": {
                "type": "integer",
                "description": "Execution timeout in seconds",
                "default": 30
            }
        }
    
    async def execute(self, **kwargs) -> ToolResult:
        """Execute Python code safely."""
        code = kwargs.get("code")
        timeout = kwargs.get("timeout", 30)
        
        if not code:
            return ToolResult(
                success=False,
                error="Code parameter is required"
            )
        
        try:
            # Create a temporary file for the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute the code with timeout
            result = subprocess.run(
                [sys.executable, temp_file],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=os.getcwd()
            )
            
            # Clean up temporary file
            os.unlink(temp_file)
            
            if result.returncode == 0:
                return ToolResult(
                    success=True,
                    data={
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    },
                    metadata={
                        "timeout": timeout,
                        "execution_time": "completed"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    error=f"Code execution failed: {result.stderr}",
                    data={
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "returncode": result.returncode
                    }
                )
        
        except subprocess.TimeoutExpired:
            return ToolResult(
                success=False,
                error=f"Code execution timed out after {timeout} seconds"
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Code execution error: {str(e)}"
            )
    
    def validate_parameters(self, **kwargs) -> bool:
        """Validate code execution parameters."""
        code = kwargs.get("code")
        if not code or not isinstance(code, str):
            return False
        
        timeout = kwargs.get("timeout", 30)
        if not isinstance(timeout, int) or timeout < 1 or timeout > 300:
            return False
        
        return True


# Import sys for subprocess
import sys 