"""
Task executor for the agentic AI system.
"""

import asyncio
from typing import List, Dict, Any, Optional
from .task import Task, TaskStatus, TaskResult
from .planner import TaskPlanner


class TaskExecutor:
    """Executes tasks according to a plan."""
    
    def __init__(self, planner: TaskPlanner):
        self.planner = planner
        self.completed_tasks: List[str] = []
        self.failed_tasks: List[str] = []
        self.execution_log: List[Dict[str, Any]] = []
    
    async def execute_all_tasks(self) -> Dict[str, Any]:
        """Execute all tasks in the planner."""
        execution_order = self.planner.get_execution_order()
        
        for task_id in execution_order:
            task = self.planner.get_task(task_id)
            if task and task.status == TaskStatus.PENDING:
                result = await self.execute_task(task)
                
                if result.success:
                    self.completed_tasks.append(task_id)
                else:
                    self.failed_tasks.append(task_id)
        
        return {
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "execution_log": self.execution_log
        }
    
    async def execute_task(self, task: Task) -> TaskResult:
        """Execute a single task."""
        try:
            task.start()
            
            # Log execution start
            self.execution_log.append({
                "task_id": task.id,
                "action": "started",
                "timestamp": task.started_at.isoformat() if task.started_at else None
            })
            
            # Execute the task based on its type
            if task.subtasks:
                result = await self._execute_composite_task(task)
            else:
                result = await self._execute_simple_task(task)
            
            # Log execution completion
            self.execution_log.append({
                "task_id": task.id,
                "action": "completed" if result.success else "failed",
                "timestamp": task.completed_at.isoformat() if task.completed_at else None,
                "result": result.data if result.success else result.error
            })
            
            return result
        
        except Exception as e:
            error_result = TaskResult(success=False, error=str(e))
            task.fail(str(e))
            
            # Log execution failure
            self.execution_log.append({
                "task_id": task.id,
                "action": "failed",
                "timestamp": task.completed_at.isoformat() if task.completed_at else None,
                "error": str(e)
            })
            
            return error_result
    
    async def _execute_composite_task(self, task: Task) -> TaskResult:
        """Execute a task with subtasks."""
        completed_subtasks = []
        
        for subtask in task.subtasks:
            if subtask.is_ready(completed_subtasks):
                subtask_result = await self.execute_task(subtask)
                
                if subtask_result.success:
                    subtask.complete(subtask_result)
                    completed_subtasks.append(subtask.id)
                else:
                    subtask.fail(subtask_result.error)
                    task.fail(f"Subtask {subtask.id} failed: {subtask_result.error}")
                    return task.result
        
        # All subtasks completed successfully
        result = TaskResult(
            success=True,
            data={"completed_subtasks": len(completed_subtasks)},
            execution_time=task.get_execution_time() or 0.0
        )
        task.complete(result)
        return result
    
    async def _execute_simple_task(self, task: Task) -> TaskResult:
        """Execute a simple task without subtasks."""
        # This is a placeholder implementation
        # In a real system, you would have specific task executors for different task types
        
        # Simulate task execution
        await asyncio.sleep(1)  # Simulate work
        
        # For now, just return success
        result = TaskResult(
            success=True,
            data={"message": f"Task '{task.title}' completed successfully"},
            execution_time=task.get_execution_time() or 0.0
        )
        task.complete(result)
        return result
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """Get a summary of task execution."""
        return {
            "total_tasks": len(self.planner.tasks),
            "completed_tasks": len(self.completed_tasks),
            "failed_tasks": len(self.failed_tasks),
            "success_rate": len(self.completed_tasks) / len(self.planner.tasks) if self.planner.tasks else 0,
            "execution_log": self.execution_log
        }
    
    def reset_execution_state(self) -> None:
        """Reset the execution state."""
        self.completed_tasks.clear()
        self.failed_tasks.clear()
        self.execution_log.clear()
        self.planner.reset_all_tasks()
    
    async def execute_until_failure(self) -> Dict[str, Any]:
        """Execute tasks until one fails."""
        execution_order = self.planner.get_execution_order()
        
        for task_id in execution_order:
            task = self.planner.get_task(task_id)
            if task and task.status == TaskStatus.PENDING:
                result = await self.execute_task(task)
                
                if result.success:
                    self.completed_tasks.append(task_id)
                else:
                    self.failed_tasks.append(task_id)
                    break  # Stop on first failure
        
        return {
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "execution_log": self.execution_log
        } 