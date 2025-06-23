"""
Configuration management for the agentic AI system.
"""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class AgentConfig(BaseModel):
    """Configuration for the agentic AI system."""
    
    # OpenAI Configuration
    openai_api_key: str = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = Field(default=os.getenv("OPENAI_MODEL", "gpt-4"))
    
    # Agent Configuration
    agent_name: str = Field(default=os.getenv("AGENT_NAME", "AgenticAI"))
    agent_personality: str = Field(
        default=os.getenv("AGENT_PERSONALITY", "helpful, intelligent, and proactive")
    )
    max_memory_size: int = Field(
        default=int(os.getenv("MAX_MEMORY_SIZE", "1000"))
    )
    max_conversation_length: int = Field(
        default=int(os.getenv("MAX_CONVERSATION_LENGTH", "50"))
    )
    
    # Tool Configuration
    enable_web_search: bool = Field(
        default=os.getenv("ENABLE_WEB_SEARCH", "true").lower() == "true"
    )
    enable_file_operations: bool = Field(
        default=os.getenv("ENABLE_FILE_OPERATIONS", "true").lower() == "true"
    )
    enable_code_execution: bool = Field(
        default=os.getenv("ENABLE_CODE_EXECUTION", "true").lower() == "true"
    )
    
    # Memory Configuration
    memory_type: str = Field(default=os.getenv("MEMORY_TYPE", "persistent"))
    memory_file_path: str = Field(
        default=os.getenv("MEMORY_FILE_PATH", "./data/agent_memory.json")
    )
    
    # Logging Configuration
    log_level: str = Field(default=os.getenv("LOG_LEVEL", "INFO"))
    log_file: str = Field(default=os.getenv("LOG_FILE", "./logs/agent.log"))
    
    def validate_config(self) -> None:
        """Validate the configuration."""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is required")
        
        if not os.path.exists(os.path.dirname(self.memory_file_path)):
            os.makedirs(os.path.dirname(self.memory_file_path), exist_ok=True)
        
        if not os.path.exists(os.path.dirname(self.log_file)):
            os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump()
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "AgentConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict) 