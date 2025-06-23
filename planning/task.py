"""
Task models for the planning system.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Status of a task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskResult(BaseModel):
    """Result of a task execution."""
    
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Task(BaseModel):
    """A task to be executed by the agent."""
    
    id: str
    title: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: int = Field(default=1, ge=1, le=10)
    dependencies: List[str] = Field(default_factory=list)
    subtasks: List["Task"] = Field(default_factory=list)
    result: Optional[TaskResult] = None
    created_at: datetime = Field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    def start(self) -> None:
        """Mark the task as started."""
        self.status = TaskStatus.IN_PROGRESS
        self.started_at = datetime.now()
    
    def complete(self, result: TaskResult) -> None:
        """Mark the task as completed."""
        self.status = TaskStatus.COMPLETED
        self.result = result
        self.completed_at = datetime.now()
    
    def fail(self, error: str) -> None:
        """Mark the task as failed."""
        self.status = TaskStatus.FAILED
        self.result = TaskResult(success=False, error=error)
        self.completed_at = datetime.now()
    
    def cancel(self) -> None:
        """Mark the task as cancelled."""
        self.status = TaskStatus.CANCELLED
        self.completed_at = datetime.now()
    
    def add_subtask(self, subtask: "Task") -> None:
        """Add a subtask to this task."""
        self.subtasks.append(subtask)
    
    def get_execution_time(self) -> Optional[float]:
        """Get the execution time in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def is_ready(self, completed_tasks: List[str]) -> bool:
        """Check if the task is ready to execute (dependencies satisfied)."""
        return all(dep in completed_tasks for dep in self.dependencies)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Task":
        """Create task from dictionary."""
        return cls(**data)


# Update forward references
Task.model_rebuild() 