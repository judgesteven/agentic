"""
Episodic memory implementation for the agentic AI system.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime
from .base import BaseMemory, MemoryItem


class EpisodicMemory(BaseMemory):
    """Episodic memory system for storing event sequences."""
    
    def __init__(self, max_size: int = 1000):
        super().__init__(max_size)
        self.episodes: List[Dict[str, Any]] = []
    
    async def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a new episodic memory."""
        memory_id = self._generate_id()
        
        if metadata is None:
            metadata = {}
        
        # Create episode
        episode = {
            "id": memory_id,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata,
            "importance": 1.0,
            "episode_type": metadata.get("episode_type", "general")
        }
        
        self.episodes.append(episode)
        self._cleanup_old_episodes()
        
        return memory_id
    
    async def get(self, memory_id: str) -> Optional[MemoryItem]:
        """Retrieve a specific episodic memory."""
        for episode in self.episodes:
            if episode["id"] == memory_id:
                return MemoryItem(
                    id=episode["id"],
                    content=episode["content"],
                    timestamp=episode["timestamp"],
                    metadata=episode["metadata"],
                    importance=episode["importance"]
                )
        return None
    
    async def search(self, query: str, limit: int = 10) -> List[MemoryItem]:
        """Search for relevant episodes."""
        query_lower = query.lower()
        relevant_episodes = []
        
        for episode in reversed(self.episodes):
            if isinstance(episode["content"], str):
                if query_lower in episode["content"].lower():
                    relevant_episodes.append(MemoryItem(
                        id=episode["id"],
                        content=episode["content"],
                        timestamp=episode["timestamp"],
                        metadata=episode["metadata"],
                        importance=episode["importance"]
                    ))
            elif isinstance(episode["content"], dict):
                content_str = str(episode["content"]).lower()
                if query_lower in content_str:
                    relevant_episodes.append(MemoryItem(
                        id=episode["id"],
                        content=episode["content"],
                        timestamp=episode["timestamp"],
                        metadata=episode["metadata"],
                        importance=episode["importance"]
                    ))
            
            if len(relevant_episodes) >= limit:
                break
        
        return relevant_episodes
    
    async def update(self, memory_id: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update an existing episodic memory."""
        for episode in self.episodes:
            if episode["id"] == memory_id:
                episode["content"] = content
                if metadata:
                    episode["metadata"].update(metadata)
                episode["timestamp"] = datetime.now()
                return True
        return False
    
    async def delete(self, memory_id: str) -> bool:
        """Delete an episodic memory."""
        for i, episode in enumerate(self.episodes):
            if episode["id"] == memory_id:
                del self.episodes[i]
                return True
        return False
    
    async def clear(self) -> None:
        """Clear all episodic memories."""
        self.episodes.clear()
    
    async def save(self) -> None:
        """Save episodic memories to persistent storage."""
        # This would implement persistent storage for episodes
        pass
    
    async def load(self) -> None:
        """Load episodic memories from persistent storage."""
        # This would load episodes from persistent storage
        pass
    
    def get_episodes_by_type(self, episode_type: str) -> List[Dict[str, Any]]:
        """Get episodes by type."""
        return [episode for episode in self.episodes if episode.get("episode_type") == episode_type]
    
    def get_recent_episodes(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent episodes."""
        return self.episodes[-count:] if self.episodes else []
    
    def _cleanup_old_episodes(self) -> None:
        """Remove old episodes when max size is exceeded."""
        if len(self.episodes) > self.max_size:
            # Sort by importance and timestamp, keep the most important/recent
            self.episodes.sort(key=lambda x: (x["importance"], x["timestamp"]), reverse=True)
            self.episodes = self.episodes[:self.max_size] 