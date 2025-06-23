"""
Task planner for the agentic AI system.
"""

from typing import List, Dict, Any, Optional
from .task import Task, TaskStatus


class TaskPlanner:
    """Plans and organizes tasks for execution."""
    
    def __init__(self):
        self.tasks: List[Task] = []
        self.execution_order: List[str] = []
    
    def add_task(self, task: Task) -> None:
        """Add a task to the planner."""
        self.tasks.append(task)
        self._update_execution_order()
    
    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the planner."""
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                del self.tasks[i]
                self._update_execution_order()
                return True
        return False
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def get_ready_tasks(self, completed_tasks: List[str]) -> List[Task]:
        """Get tasks that are ready to execute (dependencies satisfied)."""
        ready_tasks = []
        for task in self.tasks:
            if task.status == TaskStatus.PENDING and task.is_ready(completed_tasks):
                ready_tasks.append(task)
        return ready_tasks
    
    def get_execution_order(self) -> List[str]:
        """Get the recommended execution order for tasks."""
        return self.execution_order.copy()
    
    def _update_execution_order(self) -> None:
        """Update the execution order based on dependencies."""
        # Simple topological sort for now
        # In a more sophisticated system, you might use a proper topological sort algorithm
        
        # Reset execution order
        self.execution_order = []
        
        # Add tasks without dependencies first
        for task in self.tasks:
            if not task.dependencies:
                self.execution_order.append(task.id)
        
        # Add tasks with dependencies
        remaining_tasks = [task for task in self.tasks if task.dependencies]
        
        while remaining_tasks:
            added_this_round = False
            
            for task in remaining_tasks[:]:
                if all(dep in self.execution_order for dep in task.dependencies):
                    self.execution_order.append(task.id)
                    remaining_tasks.remove(task)
                    added_this_round = True
            
            if not added_this_round and remaining_tasks:
                # Handle circular dependencies by adding remaining tasks
                for task in remaining_tasks:
                    self.execution_order.append(task.id)
                break
    
    def get_task_summary(self) -> Dict[str, Any]:
        """Get a summary of all tasks."""
        total_tasks = len(self.tasks)
        pending_tasks = len([t for t in self.tasks if t.status == TaskStatus.PENDING])
        in_progress_tasks = len([t for t in self.tasks if t.status == TaskStatus.IN_PROGRESS])
        completed_tasks = len([t for t in self.tasks if t.status == TaskStatus.COMPLETED])
        failed_tasks = len([t for t in self.tasks if t.status == TaskStatus.FAILED])
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "failed_tasks": failed_tasks,
            "execution_order": self.execution_order
        }
    
    def clear_completed_tasks(self) -> None:
        """Remove completed tasks from the planner."""
        self.tasks = [task for task in self.tasks if task.status != TaskStatus.COMPLETED]
        self._update_execution_order()
    
    def reset_all_tasks(self) -> None:
        """Reset all tasks to pending status."""
        for task in self.tasks:
            task.status = TaskStatus.PENDING
            task.started_at = None
            task.completed_at = None
            task.result = None 