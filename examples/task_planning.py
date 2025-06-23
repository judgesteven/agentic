#!/usr/bin/env python3
"""
Task planning and execution example for the agentic AI system.
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.agent import Agent
from core.config import AgentConfig
from planning.task import Task


async def task_planning_example():
    """Example of task planning and execution."""
    print("🎯 Agentic AI - Task Planning Example")
    print("=" * 40)
    
    # Create agent
    agent = Agent(AgentConfig())
    
    # Start conversation
    await agent.start_conversation()
    
    # Example tasks
    tasks = [
        "Analyze the current market trends",
        "Create a project plan for a new feature",
        "Organize and categorize a collection of documents",
        "Research and compile a report on emerging technologies"
    ]
    
    for i, task_goal in enumerate(tasks, 1):
        print(f"\n🎯 Task {i}: {task_goal}")
        print("-" * 30)
        
        # Plan the task
        task = await agent.plan_task(task_goal)
        print(f"📋 Task ID: {task.id}")
        print(f"📋 Title: {task.title}")
        print(f"📋 Priority: {task.priority}")
        print(f"📋 Subtasks: {len(task.subtasks)}")
        
        # Show subtasks
        for j, subtask in enumerate(task.subtasks, 1):
            print(f"  {j}. {subtask.title} (Priority: {subtask.priority})")
            if subtask.dependencies:
                print(f"     Dependencies: {', '.join(subtask.dependencies)}")
        
        # Execute the task
        print(f"\n⚡ Executing task...")
        result = await agent.execute_task(task)
        
        if result.success:
            print(f"✅ Task completed successfully!")
            print(f"⏱️  Execution time: {result.execution_time:.2f} seconds")
            print(f"📊 Data: {result.data}")
        else:
            print(f"❌ Task failed: {result.error}")
        
        await asyncio.sleep(1)  # Pause between tasks
    
    # Show final status
    status = agent.get_status()
    print(f"\n📊 Final Status:")
    print(f"  Tasks completed: {status['task_history_count']}")
    print(f"  Memory size: {status['memory_size']}")
    
    # Cleanup
    await agent.shutdown()
    print("\n✅ Task planning example completed!")


async def custom_task_example():
    """Example of creating and executing a custom task."""
    print("\n🔧 Custom Task Example")
    print("=" * 30)
    
    agent = Agent(AgentConfig())
    await agent.start_conversation()
    
    # Create a custom task with specific subtasks
    from planning.task import Task, TaskStatus
    
    main_task = Task(
        id="custom_task_001",
        title="Custom Data Processing Task",
        description="Process and analyze a dataset with multiple steps",
        priority=8
    )
    
    # Add custom subtasks
    subtasks = [
        Task(
            id="custom_task_001_step1",
            title="Data Validation",
            description="Validate input data format and completeness",
            priority=1
        ),
        Task(
            id="custom_task_001_step2",
            title="Data Cleaning",
            description="Clean and preprocess the data",
            priority=2,
            dependencies=["custom_task_001_step1"]
        ),
        Task(
            id="custom_task_001_step3",
            title="Analysis",
            description="Perform statistical analysis",
            priority=3,
            dependencies=["custom_task_001_step2"]
        ),
        Task(
            id="custom_task_001_step4",
            title="Report Generation",
            description="Generate analysis report",
            priority=4,
            dependencies=["custom_task_001_step3"]
        )
    ]
    
    for subtask in subtasks:
        main_task.add_subtask(subtask)
    
    print(f"📋 Custom Task: {main_task.title}")
    print(f"📋 Subtasks: {len(main_task.subtasks)}")
    
    # Execute the custom task
    result = await agent.execute_task(main_task)
    
    if result.success:
        print(f"✅ Custom task completed successfully!")
        print(f"⏱️  Total execution time: {result.execution_time:.2f} seconds")
    else:
        print(f"❌ Custom task failed: {result.error}")
    
    await agent.shutdown()


if __name__ == "__main__":
    print("Choose an example:")
    print("1. Basic task planning")
    print("2. Custom task creation")
    print("3. Both examples")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        asyncio.run(task_planning_example())
    elif choice == "2":
        asyncio.run(custom_task_example())
    elif choice == "3":
        asyncio.run(task_planning_example())
        asyncio.run(custom_task_example())
    else:
        print("Invalid choice. Running basic task planning example.")
        asyncio.run(task_planning_example()) 