"""Centralized exception definitions for AgentUI."""


class AgentUIError(Exception):
    """Base exception for all AgentUI errors."""

    pass


class ConfigurationError(AgentUIError):
    """Configuration-related errors."""

    pass


class BridgeError(AgentUIError):
    """Bridge communication errors."""

    pass


class ConnectionError(BridgeError):
    """Bridge connection failures."""

    pass


class ProtocolError(BridgeError):
    """Protocol parsing/validation errors."""

    pass


class ToolExecutionError(AgentUIError):
    """Tool execution failures."""

    pass


class ProviderError(AgentUIError):
    """LLM provider errors."""

    pass


class ValidationError(AgentUIError):
    """Input validation errors."""

    pass


class SkillLoadError(AgentUIError):
    """Skill loading failures."""

    pass
