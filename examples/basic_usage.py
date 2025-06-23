#!/usr/bin/env python3
"""
Basic usage example for the agentic AI system.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.config import AgentConfig


async def basic_example():
    """Basic example of using the agent."""
    print("🤖 Agentic AI - Basic Usage Example")
    print("=" * 40)
    
    # Create agent configuration
    config = AgentConfig()
    
    # Create agent
    agent = Agent(config)
    
    # Start a conversation
    conversation_id = await agent.start_conversation()
    print(f"Started conversation: {conversation_id}")
    
    # Simple conversation
    messages = [
        "Hello! How are you today?",
        "Can you tell me about artificial intelligence?",
        "What are your capabilities?",
        "Thank you for the information!"
    ]
    
    for message in messages:
        print(f"\n👤 User: {message}")
        response = await agent.process_message(message)
        print(f"🤖 Agent: {response}")
        await asyncio.sleep(1)  # Small pause for readability
    
    # Get agent status
    status = agent.get_status()
    print(f"\n📊 Final Status:")
    print(f"  Memory size: {status['memory_size']}")
    print(f"  Available tools: {status['available_tools']}")
    
    # Cleanup
    await agent.shutdown()
    print("\n✅ Example completed!")


if __name__ == "__main__":
    asyncio.run(basic_example()) 