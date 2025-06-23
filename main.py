#!/usr/bin/env python3
"""
Main entry point for the agentic AI system.
"""

import asyncio
import sys
from typing import Optional

from core.agent import Agent
from core.config import AgentConfig
from core.exceptions import ConfigurationError


async def interactive_chat(agent: Agent) -> None:
    """Run an interactive chat session with the agent."""
    print(f"\n🤖 {agent.config.agent_name} is ready to chat!")
    print("Type 'quit', 'exit', or 'bye' to end the conversation.")
    print("Type 'status' to see agent status.")
    print("Type 'task <goal>' to plan and execute a task.")
    print("-" * 50)
    
    # Start conversation
    await agent.start_conversation()
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            if not user_input:
                continue
            
            # Check for special commands
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("\n🤖 Goodbye! Thanks for chatting with me.")
                break
            
            elif user_input.lower() == 'status':
                status = agent.get_status()
                print(f"\n📊 Agent Status:")
                print(f"  Name: {status['agent_name']}")
                print(f"  Conversation ID: {status['conversation_id']}")
                print(f"  Memory Size: {status['memory_size']}")
                print(f"  Available Tools: {', '.join(status['available_tools'])}")
                print(f"  Task History: {status['task_history_count']} tasks")
                continue
            
            elif user_input.lower().startswith('task '):
                goal = user_input[5:].strip()
                if goal:
                    print(f"\n🎯 Planning task: {goal}")
                    task = await agent.plan_task(goal)
                    print(f"Task created: {task.title}")
                    print("Executing task...")
                    result = await agent.execute_task(task)
                    if result.success:
                        print(f"✅ Task completed successfully!")
                        print(f"Execution time: {result.execution_time:.2f} seconds")
                    else:
                        print(f"❌ Task failed: {result.error}")
                else:
                    print("Please provide a goal for the task.")
                continue
            
            # Process regular message
            print("\n🤖 Agent: ", end="", flush=True)
            response = await agent.process_message(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\n\n🤖 Interrupted by user. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


async def demo_mode(agent: Agent) -> None:
    """Run a demonstration of the agent's capabilities."""
    print(f"\n🎬 {agent.config.agent_name} Demo Mode")
    print("=" * 50)
    
    # Start conversation
    await agent.start_conversation()
    
    # Demo messages
    demo_messages = [
        "Hello! I'm excited to meet you.",
        "Can you search for information about artificial intelligence?",
        "What's the weather like today?",
        "Can you help me plan a task to organize my files?",
        "Thank you for your help!"
    ]
    
    for message in demo_messages:
        print(f"\n👤 User: {message}")
        print("🤖 Agent: ", end="", flush=True)
        response = await agent.process_message(message)
        print(response)
        await asyncio.sleep(1)  # Pause for readability
    
    # Demo task planning and execution
    print(f"\n🎯 Demo Task Planning:")
    task = await agent.plan_task("Create a simple text file with a greeting")
    print(f"Task: {task.title}")
    print("Executing...")
    result = await agent.execute_task(task)
    print(f"Result: {'Success' if result.success else 'Failed'}")
    
    print(f"\n✅ Demo completed!")


def main():
    """Main entry point."""
    print("🚀 Starting Agentic AI System...")
    
    try:
        # Load configuration
        config = AgentConfig()
        config.validate_config()
        
        # Create agent
        agent = Agent(config)
        
        # Check command line arguments
        if len(sys.argv) > 1:
            if sys.argv[1] == "--demo":
                asyncio.run(demo_mode(agent))
            elif sys.argv[1] == "--help":
                print("Usage:")
                print("  python main.py          # Interactive chat mode")
                print("  python main.py --demo   # Demo mode")
                print("  python main.py --help   # Show this help")
                return
            else:
                print(f"Unknown argument: {sys.argv[1]}")
                print("Use --help for usage information.")
                return
        else:
            # Interactive mode
            asyncio.run(interactive_chat(agent))
    
    except ConfigurationError as e:
        print(f"❌ Configuration error: {e}")
        print("Please check your environment variables and configuration.")
        return
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return
    finally:
        # Cleanup
        try:
            asyncio.run(agent.shutdown())
        except:
            pass


if __name__ == "__main__":
    main() 