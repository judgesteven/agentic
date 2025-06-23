"""
Base memory interface for the agentic AI system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class MemoryItem(BaseModel):
    """A single memory item."""
    
    id: str
    content: Any
    timestamp: datetime
    metadata: Dict[str, Any] = {}
    importance: float = 1.0
    
    class Config:
        arbitrary_types_allowed = True


class BaseMemory(ABC):
    """Base class for memory systems."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.memories: List[MemoryItem] = []
    
    @abstractmethod
    async def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new memory item."""
        pass
    
    @abstractmethod
    async def get(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific memory item."""
        pass
    
    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search for relevant memories."""
        pass
    
    @abstractmethod
    async def update(self, memory_id: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update an existing memory item."""
        pass
    
    @abstractmethod
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory item."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all memories."""
        pass
    
    @abstractmethod
    async def save(self) -> None:
        """Save memories to persistent storage."""
        pass
    
    @abstractmethod
    async def load(self) -> None:
        """Load memories from persistent storage."""
        pass
    
    def _generate_id(self) -> str:
        """Generate a unique memory ID."""
        import uuid
        return str(uuid.uuid4())
    
    def _cleanup_old_memories(self) -> None:
        """Remove old memories when max size is exceeded."""
        if len(self.memories) > self.max_size:
            # Sort by importance and timestamp, keep the most important/recent
            self.memories.sort(key=lambda x: (x.importance, x.timestamp), reverse=True)
            self.memories = self.memories[:self.max_size] 