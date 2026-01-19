"""
Centralized exception definitions for AgentUI.

This module defines the exception hierarchy used throughout AgentUI.
All exceptions inherit from AgentUIError for easy catching.

Exception Hierarchy:
    AgentUIError (base)
    ├── ConfigurationError (invalid configuration)
    ├── BridgeError (UI communication failures)
    │   ├── ConnectionError (bridge connection failed)
    │   └── ProtocolError (invalid protocol messages)
    ├── ToolExecutionError (tool handler failures)
    ├── ProviderError (LLM provider errors)
    ├── ValidationError (input validation failures)
    └── SkillLoadError (skill loading failures)
"""


class AgentUIError(Exception):
    """
    Base exception for all AgentUI errors.

    All custom exceptions in AgentUI inherit from this class,
    allowing users to catch all framework errors with a single except clause.
    """

    pass


class ConfigurationError(AgentUIError):
    """
    Configuration-related errors.

    Raised when:
    - Invalid provider specified
    - Missing required API keys
    - Invalid manifest format
    - Malformed configuration values
    """

    pass


class BridgeError(AgentUIError):
    """
    Bridge communication errors.

    Base class for errors related to UI bridge communication
    (TUI subprocess or CLI fallback).
    """

    pass


class ConnectionError(BridgeError):
    """
    Bridge connection failures.

    Raised when:
    - TUI binary cannot be found or started
    - Bridge subprocess crashes
    - Connection cannot be established
    """

    pass


class ProtocolError(BridgeError):
    """
    Protocol parsing/validation errors.

    Raised when:
    - Invalid JSON received from TUI
    - Message type unknown
    - Required message fields missing
    - Protocol version mismatch
    """

    pass


class ToolExecutionError(AgentUIError):
    """
    Tool execution failures.

    Raised when:
    - Tool handler raises an exception
    - Tool parameters are invalid
    - Tool not found in registry
    """

    pass


class ProviderError(AgentUIError):
    """
    LLM provider errors.

    Raised when:
    - API key invalid or missing
    - API rate limit exceeded
    - Model not available
    - Provider API returns an error
    """

    pass


class ValidationError(AgentUIError):
    """
    Input validation errors.

    Raised when:
    - User input fails validation
    - Required form fields missing
    - Input type mismatch
    """

    pass


class SkillLoadError(AgentUIError):
    """
    Skill loading failures.

    Raised when:
    - SKILL.md file not found
    - skill.yaml malformed
    - Skill directory structure invalid
    """

    pass
