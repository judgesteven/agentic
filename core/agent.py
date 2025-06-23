"""
Main agent class for the agentic AI system.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from openai import AsyncOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage

from .config import AgentConfig
from .exceptions import AgentError, ConfigurationError
from memory.conversation import ConversationMemory
from tools.base import ToolRegistry, tool_registry
from tools.web_search import WebSearchTool
from tools.file_operations import FileOperationsTool
from planning.task import Task, TaskStatus, TaskResult


class Agent:
    """Main agentic AI agent."""
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """Initialize the agent."""
        self.config = config or AgentConfig()
        self.config.validate_config()
        
        # Initialize components
        self.client = AsyncOpenAI(api_key=self.config.openai_api_key)
        self.memory = ConversationMemory(max_size=self.config.max_memory_size)
        self.tool_registry = tool_registry
        
        # Register default tools
        self._register_default_tools()
        
        # Setup logging
        self._setup_logging()
        
        # Agent state
        self.conversation_id: Optional[str] = None
        self.current_task: Optional[Task] = None
        self.task_history: List[Task] = []
        
        self.logger.info(f"Agent '{self.config.agent_name}' initialized successfully")
    
    def _setup_logging(self) -> None:
        """Setup logging for the agent."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level.upper()),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.config.log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.config.agent_name)
    
    def _register_default_tools(self) -> None:
        """Register default tools."""
        if self.config.enable_web_search:
            self.tool_registry.register(WebSearchTool())
        
        if self.config.enable_file_operations:
            self.tool_registry.register(FileOperationsTool())
    
    async def start_conversation(self) -> str:
        """Start a new conversation."""
        self.conversation_id = self.memory.start_new_conversation()
        self.logger.info(f"Started new conversation: {self.conversation_id}")
        return self.conversation_id
    
    async def process_message(self, message: str, use_tools: bool = True) -> str:
        """Process a user message and return a response."""
        try:
            # Add user message to memory
            await self.memory.add({
                "role": "user",
                "content": message,
                "timestamp": datetime.now()
            })
            
            # Generate response
            response = await self._generate_response(message, use_tools)
            
            # Add agent response to memory
            await self.memory.add({
                "role": "assistant",
                "content": response,
                "timestamp": datetime.now()
            })
            
            return response
        
        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.logger.error(error_msg)
            return f"I encountered an error: {error_msg}"
    
    async def _generate_response(self, message: str, use_tools: bool) -> str:
        """Generate a response to the user message."""
        # Build conversation context
        messages = self._build_conversation_context(message)
        
        # Add system message
        system_message = self._build_system_message(use_tools)
        messages.insert(0, system_message)
        
        # Generate response
        response = await self.client.chat.completions.create(
            model=self.config.openai_model,
            messages=[msg.dict() for msg in messages],
            temperature=0.7,
            max_tokens=1000
        )
        
        response_content = response.choices[0].message.content
        
        # If tools are enabled, check if we need to use them
        if use_tools and self._should_use_tools(response_content):
            return await self._handle_tool_usage(message, response_content)
        
        return response_content
    
    def _build_conversation_context(self, current_message: str) -> List[Union[HumanMessage, AIMessage]]:
        """Build conversation context from memory."""
        messages = []
        
        # Get recent conversation history
        recent_memories = self.memory.memories[-self.config.max_conversation_length:]
        
        for memory in recent_memories:
            if isinstance(memory.content, dict):
                role = memory.content.get("role")
                content = memory.content.get("content")
                
                if role == "user":
                    messages.append(HumanMessage(content=content))
                elif role == "assistant":
                    messages.append(AIMessage(content=content))
        
        # Add current message
        messages.append(HumanMessage(content=current_message))
        
        return messages
    
    def _build_system_message(self, use_tools: bool) -> SystemMessage:
        """Build the system message for the agent."""
        system_content = f"""You are {self.config.agent_name}, an {self.config.agent_personality} AI assistant.

Your capabilities include:
- Understanding and responding to user queries
- Using tools to gather information and perform tasks
- Planning and executing complex tasks
- Learning from interactions

Current conversation ID: {self.conversation_id or 'None'}

Please respond in a helpful, clear, and concise manner."""

        if use_tools:
            tool_schemas = self.tool_registry.get_tool_schemas()
            if tool_schemas:
                system_content += "\n\nAvailable tools:\n"
                for tool_name, schema in tool_schemas.items():
                    system_content += f"- {tool_name}: {schema['description']}\n"
        
        return SystemMessage(content=system_content)
    
    def _should_use_tools(self, response: str) -> bool:
        """Determine if the response indicates tool usage is needed."""
        # Simple heuristic - look for keywords that suggest tool usage
        tool_keywords = [
            "search", "find", "look up", "get information", "read file",
            "write file", "create", "delete", "list", "check"
        ]
        
        response_lower = response.lower()
        return any(keyword in response_lower for keyword in tool_keywords)
    
    async def _handle_tool_usage(self, original_message: str, initial_response: str) -> str:
        """Handle tool usage and generate final response."""
        # For now, implement a simple tool selection strategy
        # In a more sophisticated system, you might use function calling or structured output
        
        # Try to identify which tool to use based on the message
        if any(word in original_message.lower() for word in ["search", "find", "look up"]):
            # Use web search
            search_query = original_message
            result = await self.tool_registry.execute_tool("web_search", query=search_query)
            
            if result.success:
                search_results = result.data.get("results", [])
                if search_results:
                    response = f"I found some information for you:\n\n"
                    for i, result_item in enumerate(search_results[:3], 1):
                        response += f"{i}. {result_item['title']}\n"
                        response += f"   {result_item['snippet'][:200]}...\n\n"
                    return response
                else:
                    return "I searched but couldn't find relevant information for your query."
            else:
                return f"I tried to search for information but encountered an error: {result.error}"
        
        elif any(word in original_message.lower() for word in ["read", "file", "open"]):
            # Use file operations
            # This is a simplified implementation
            return "I can help with file operations. Please specify the exact file path you'd like me to work with."
        
        # If no specific tool is identified, return the initial response
        return initial_response
    
    async def plan_task(self, goal: str) -> Task:
        """Plan a complex task."""
        # Create a main task
        task = Task(
            id=f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            title=goal,
            description=f"Task to achieve: {goal}",
            priority=5
        )
        
        # For now, create a simple plan
        # In a more sophisticated system, you would use the LLM to break down the task
        subtasks = [
            Task(
                id=f"{task.id}_subtask_1",
                title="Analyze requirements",
                description="Understand what needs to be done",
                priority=1
            ),
            Task(
                id=f"{task.id}_subtask_2",
                title="Execute main task",
                description="Perform the main work",
                priority=2,
                dependencies=[f"{task.id}_subtask_1"]
            ),
            Task(
                id=f"{task.id}_subtask_3",
                title="Verify results",
                description="Check that the task was completed successfully",
                priority=3,
                dependencies=[f"{task.id}_subtask_2"]
            )
        ]
        
        for subtask in subtasks:
            task.add_subtask(subtask)
        
        self.current_task = task
        self.task_history.append(task)
        
        return task
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a task."""
        try:
            task.start()
            self.logger.info(f"Starting task: {task.title}")
            
            # Execute subtasks in order
            completed_subtasks = []
            
            for subtask in task.subtasks:
                if subtask.is_ready(completed_subtasks):
                    subtask_result = await self._execute_subtask(subtask)
                    if subtask_result.success:
                        subtask.complete(subtask_result)
                        completed_subtasks.append(subtask.id)
                    else:
                        subtask.fail(subtask_result.error)
                        task.fail(f"Subtask failed: {subtask_result.error}")
                        return task.result
                else:
                    task.fail(f"Subtask {subtask.id} dependencies not satisfied")
                    return task.result
            
            # Task completed successfully
            result = TaskResult(
                success=True,
                data={"completed_subtasks": len(completed_subtasks)},
                execution_time=task.get_execution_time() or 0.0
            )
            task.complete(result)
            
            self.logger.info(f"Task completed: {task.title}")
            return result
        
        except Exception as e:
            error_msg = f"Task execution failed: {str(e)}"
            self.logger.error(error_msg)
            task.fail(error_msg)
            return task.result
    
    async def _execute_subtask(self, subtask: Task) -> TaskResult:
        """Execute a subtask."""
        try:
            subtask.start()
            
            # Simple execution logic - in a real system, this would be more sophisticated
            if "analyze" in subtask.title.lower():
                # Simulate analysis
                await asyncio.sleep(1)
                return TaskResult(success=True, data={"analysis": "completed"})
            
            elif "execute" in subtask.title.lower():
                # Simulate execution
                await asyncio.sleep(2)
                return TaskResult(success=True, data={"execution": "completed"})
            
            elif "verify" in subtask.title.lower():
                # Simulate verification
                await asyncio.sleep(0.5)
                return TaskResult(success=True, data={"verification": "passed"})
            
            else:
                return TaskResult(success=True, data={"subtask": "completed"})
        
        except Exception as e:
            return TaskResult(success=False, error=str(e))
    
    def get_status(self) -> Dict[str, Any]:
        """Get the current status of the agent."""
        return {
            "agent_name": self.config.agent_name,
            "conversation_id": self.conversation_id,
            "memory_size": len(self.memory.memories),
            "available_tools": self.tool_registry.list_tools(),
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "task_history_count": len(self.task_history)
        }
    
    async def learn_from_interaction(self, user_feedback: str, success: bool) -> None:
        """Learn from user feedback."""
        # Add learning experience to memory
        await self.memory.add({
            "type": "learning",
            "feedback": user_feedback,
            "success": success,
            "timestamp": datetime.now()
        })
        
        self.logger.info(f"Learning from feedback: {user_feedback} (success: {success})")
    
    async def shutdown(self) -> None:
        """Shutdown the agent gracefully."""
        self.logger.info("Shutting down agent...")
        
        # Save memory
        await self.memory.save()
        
        # Close any open connections
        if hasattr(self, 'client'):
            await self.client.close()
        
        self.logger.info("Agent shutdown complete") 