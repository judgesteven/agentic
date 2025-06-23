#!/usr/bin/env python3
"""
Basic tests for the agentic AI system.
"""

import pytest
import asyncio
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import AgentConfig
from core.exceptions import ConfigurationError
from memory.conversation import ConversationMemory
from tools.base import ToolRegistry, BaseTool, ToolResult
from planning.task import Task, TaskStatus, TaskResult


class TestConfig:
    """Test configuration management."""
    
    def test_config_creation(self):
        """Test that configuration can be created."""
        config = AgentConfig()
        assert config.agent_name == "AgenticAI"
        assert config.openai_model == "gpt-4"
    
    def test_config_validation(self):
        """Test configuration validation."""
        config = AgentConfig()
        # This should not raise an exception
        config.validate_config()
    
    def test_config_from_dict(self):
        """Test creating config from dictionary."""
        config_dict = {
            "agent_name": "TestAgent",
            "openai_model": "gpt-3.5-turbo"
        }
        config = AgentConfig.from_dict(config_dict)
        assert config.agent_name == "TestAgent"
        assert config.openai_model == "gpt-3.5-turbo"


class TestMemory:
    """Test memory functionality."""
    
    @pytest.mark.asyncio
    async def test_memory_creation(self):
        """Test memory system creation."""
        memory = ConversationMemory(max_size=10)
        assert memory.max_size == 10
        assert len(memory.memories) == 0
    
    @pytest.mark.asyncio
    async def test_memory_add(self):
        """Test adding items to memory."""
        memory = ConversationMemory()
        memory_id = await memory.add("test content")
        assert memory_id is not None
        assert len(memory.memories) == 1
    
    @pytest.mark.asyncio
    async def test_memory_search(self):
        """Test memory search functionality."""
        memory = ConversationMemory()
        await memory.add("This is a test message about Python")
        await memory.add("Another message about programming")
        
        results = await memory.search("Python")
        assert len(results) == 1
        assert "Python" in str(results[0].content)


class TestTools:
    """Test tool functionality."""
    
    def test_tool_registry(self):
        """Test tool registry."""
        registry = ToolRegistry()
        assert len(registry.list_tools()) == 0
    
    def test_tool_registration(self):
        """Test tool registration."""
        registry = ToolRegistry()
        
        class TestTool(BaseTool):
            async def execute(self, **kwargs):
                return ToolResult(success=True, data="test")
        
        tool = TestTool("test_tool", "A test tool")
        registry.register(tool)
        
        assert "test_tool" in registry.list_tools()
        assert registry.get_tool("test_tool") == tool
    
    @pytest.mark.asyncio
    async def test_tool_execution(self):
        """Test tool execution."""
        registry = ToolRegistry()
        
        class TestTool(BaseTool):
            async def execute(self, **kwargs):
                return ToolResult(success=True, data=kwargs.get("input", "default"))
        
        tool = TestTool("test_tool", "A test tool")
        registry.register(tool)
        
        result = await registry.execute_tool("test_tool", input="hello")
        assert result.success
        assert result.data == "hello"


class TestTasks:
    """Test task functionality."""
    
    def test_task_creation(self):
        """Test task creation."""
        task = Task(
            id="test_task",
            title="Test Task",
            description="A test task"
        )
        assert task.id == "test_task"
        assert task.title == "Test Task"
        assert task.status == TaskStatus.PENDING
    
    def test_task_lifecycle(self):
        """Test task lifecycle."""
        task = Task(
            id="test_task",
            title="Test Task",
            description="A test task"
        )
        
        # Start task
        task.start()
        assert task.status == TaskStatus.IN_PROGRESS
        assert task.started_at is not None
        
        # Complete task
        result = TaskResult(success=True, data="completed")
        task.complete(result)
        assert task.status == TaskStatus.COMPLETED
        assert task.result == result
        assert task.completed_at is not None
    
    def test_task_dependencies(self):
        """Test task dependencies."""
        task = Task(
            id="test_task",
            title="Test Task",
            description="A test task",
            dependencies=["dep1", "dep2"]
        )
        
        # Should not be ready without dependencies
        assert not task.is_ready([])
        assert not task.is_ready(["dep1"])
        
        # Should be ready with all dependencies
        assert task.is_ready(["dep1", "dep2"])
        assert task.is_ready(["dep1", "dep2", "dep3"])  # Extra dependencies are OK


class TestIntegration:
    """Test integration between components."""
    
    @pytest.mark.asyncio
    async def test_memory_and_tools_integration(self):
        """Test memory and tools working together."""
        memory = ConversationMemory()
        registry = ToolRegistry()
        
        # Add some memory
        await memory.add("User asked about Python")
        
        # Create a tool that uses memory
        class MemoryAwareTool(BaseTool):
            def __init__(self, memory):
                super().__init__("memory_tool", "A tool that uses memory")
                self.memory = memory
            
            async def execute(self, **kwargs):
                memories = await self.memory.search("Python")
                return ToolResult(success=True, data=len(memories))
        
        tool = MemoryAwareTool(memory)
        registry.register(tool)
        
        result = await registry.execute_tool("memory_tool")
        assert result.success
        assert result.data == 1


if __name__ == "__main__":
    # Run basic tests
    print("Running basic tests...")
    
    # Test config
    test_config = TestConfig()
    test_config.test_config_creation()
    test_config.test_config_validation()
    print("✅ Config tests passed")
    
    # Test memory
    async def test_memory():
        test_memory = TestMemory()
        await test_memory.test_memory_creation()
        await test_memory.test_memory_add()
        await test_memory.test_memory_search()
        print("✅ Memory tests passed")
    
    # Test tools
    test_tools = TestTools()
    test_tools.test_tool_registry()
    test_tools.test_tool_registration()
    print("✅ Tool tests passed")
    
    # Test tasks
    test_tasks = TestTasks()
    test_tasks.test_task_creation()
    test_tasks.test_task_lifecycle()
    test_tasks.test_task_dependencies()
    print("✅ Task tests passed")
    
    # Run async tests
    asyncio.run(test_memory())
    
    print("🎉 All basic tests passed!") 