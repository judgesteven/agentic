"""
Conversation memory for tracking chat history.
"""

import json
from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import BaseMemory, MemoryItem


class ConversationMemory(BaseMemory):
    """Memory system for tracking conversation history."""
    
    def __init__(self, max_size: int = 100):
        super().__init__(max_size)
        self.conversation_id: Optional[str] = None
    
    async def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a conversation turn to memory."""
        memory_id = self._generate_id()
        
        # Ensure metadata exists
        if metadata is None:
            metadata = {}
        
        # Add conversation-specific metadata
        metadata.update({
            "type": "conversation",
            "conversation_id": self.conversation_id,
            "turn_number": len(self.memories) + 1
        })
        
        memory_item = MemoryItem(
            id=memory_id,
            content=content,
            timestamp=datetime.now(),
            metadata=metadata,
            importance=1.0
        )
        
        self.memories.append(memory_item)
        self._cleanup_old_memories()
        
        return memory_id
    
    async def get(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific conversation memory."""
        for memory in self.memories:
            if memory.id == memory_id:
                return memory
        return None
    
    async def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search conversation history for relevant content."""
        # Simple keyword-based search for now
        # In a real implementation, you might use embeddings or more sophisticated search
        query_lower = query.lower()
        relevant_memories = []
        
        for memory in reversed(self.memories):  # Search from most recent
            if isinstance(memory.content, str):
                if query_lower in memory.content.lower():
                    relevant_memories.append(memory)
            elif isinstance(memory.content, dict):
                # Search in dictionary content
                content_str = str(memory.content).lower()
                if query_lower in content_str:
                    relevant_memories.append(memory)
            
            if len(relevant_memories) >= limit:
                break
        
        return relevant_memories
    
    async def update(self, memory_id: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a conversation memory."""
        for memory in self.memories:
            if memory.id == memory_id:
                memory.content = content
                if metadata:
                    memory.metadata.update(metadata)
                memory.timestamp = datetime.now()
                return True
        return False
    
    async def delete(self, memory_id: str) -> bool:
        """Delete a conversation memory."""
        for i, memory in enumerate(self.memories):
            if memory.id == memory_id:
                del self.memories[i]
                return True
        return False
    
    async def clear(self) -> None:
        """Clear all conversation memories."""
        self.memories.clear()
    
    async def save(self) -> None:
        """Save conversation memories to file."""
        # This is a simple implementation - in production you might use a database
        pass
    
    async def load(self) -> None:
        """Load conversation memories from file."""
        # This is a simple implementation - in production you might use a database
        pass
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the current conversation."""
        if not self.memories:
            return "No conversation history."
        
        summary_parts = []
        for memory in self.memories[-5:]:  # Last 5 turns
            if isinstance(memory.content, str):
                summary_parts.append(f"Turn {memory.metadata.get('turn_number', '?')}: {memory.content[:100]}...")
            elif isinstance(memory.content, dict):
                summary_parts.append(f"Turn {memory.metadata.get('turn_number', '?')}: {str(memory.content)[:100]}...")
        
        return "\n".join(summary_parts)
    
    def start_new_conversation(self) -> str:
        """Start a new conversation and return the conversation ID."""
        import uuid
        self.conversation_id = str(uuid.uuid4())
        return self.conversation_id 