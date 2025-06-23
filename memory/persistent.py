"""
Persistent memory implementation for the agentic AI system.
"""

import json
import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import BaseMemory, MemoryItem


class PersistentMemory(BaseMemory):
    """Persistent memory system that saves to disk."""
    
    def __init__(self, file_path: str = "./data/agent_memory.json", max_size: int = 1000):
        super().__init__(max_size)
        self.file_path = file_path
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """Ensure the memory file exists."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, 'w') as f:
                json.dump([], f)
    
    async def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new memory item."""
        memory_id = self._generate_id()
        
        if metadata is None:
            metadata = {}
        
        memory_item = MemoryItem(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata,
            importance=1.0
        )
        
        self.memories.append(memory_item)
        self._cleanup_old_memories()
        
        # Save to disk
        await self.save()
        
        return memory_id
    
    async def get(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific memory item."""
        for memory in self.memories:
            if memory.id == memory_id:
                return memory
        return None
    
    async def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search for relevant memories."""
        query_lower = query.lower()
        relevant_memories = []
        
        for memory in reversed(self.memories):
            if isinstance(memory.content, str):
                if query_lower in memory.content.lower():
                    relevant_memories.append(memory)
            elif isinstance(memory.content, dict):
                content_str = str(memory.content).lower()
                if query_lower in content_str:
                    relevant_memories.append(memory)
            
            if len(relevant_memories) >= limit:
                break
        
        return relevant_memories
    
    async def update(self, memory_id: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update an existing memory item."""
        for memory in self.memories:
            if memory.id == memory_id:
                memory.content = content
                if metadata:
                    memory.metadata.update(metadata)
                memory.timestamp = datetime.now()
                await self.save()
                return True
        return False
    
    async def delete(self, memory_id: str) -> bool:
        """Delete a memory item."""
        for i, memory in enumerate(self.memories):
            if memory.id == memory_id:
                del self.memories[i]
                await self.save()
                return True
        return False
    
    async def clear(self) -> None:
        """Clear all memories."""
        self.memories.clear()
        await self.save()
    
    async def save(self) -> None:
        """Save memories to persistent storage."""
        try:
            # Convert memories to serializable format
            serializable_memories = []
            for memory in self.memories:
                serializable_memory = {
                    "id": memory.id,
                    "content": memory.content,
                    "timestamp": memory.timestamp.isoformat(),
                    "metadata": memory.metadata,
                    "importance": memory.importance
                }
                serializable_memories.append(serializable_memory)
            
            with open(self.file_path, 'w') as f:
                json.dump(serializable_memories, f, indent=2)
        
        except Exception as e:
            print(f"Error saving memory: {e}")
    
    async def load(self) -> None:
        """Load memories from persistent storage."""
        try:
            if not os.path.exists(self.file_path):
                return
            
            with open(self.file_path, 'r') as f:
                data = json.load(f)
            
            self.memories.clear()
            for item_data in data:
                memory_item = MemoryItem(
                    id=item_data["id"],
                    content=item_data["content"],
                    timestamp=datetime.fromisoformat(item_data["timestamp"]),
                    metadata=item_data.get("metadata", {}),
                    importance=item_data.get("importance", 1.0)
                )
                self.memories.append(memory_item)
        
        except Exception as e:
            print(f"Error loading memory: {e}")
            self.memories = [] 