"""
Custom exceptions for the agentic AI system.
"""


class AgentError(Exception):
    """Base exception for agent-related errors."""
    pass


class ToolError(AgentError):
    """Exception raised when a tool fails to execute."""
    pass


class PlanningError(AgentError):
    """Exception raised when task planning fails."""
    pass


class MemoryError(AgentError):
    """Exception raised when memory operations fail."""
    pass


class ConfigurationError(AgentError):
    """Exception raised when configuration is invalid."""
    pass


class LearningError(AgentError):
    """Exception raised when learning operations fail."""
    pass 