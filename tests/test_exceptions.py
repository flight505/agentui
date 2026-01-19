"""Tests for centralized exception handling."""

import pytest

from agentui.exceptions import (
    AgentUIError,
    BridgeError,
    ConfigurationError,
    ConnectionError,
    ProtocolError,
    ProviderError,
    SkillLoadError,
    ToolExecutionError,
    ValidationError,
)


def test_exception_hierarchy():
    """Test exception inheritance."""
    assert issubclass(ConfigurationError, AgentUIError)
    assert issubclass(BridgeError, AgentUIError)
    assert issubclass(ConnectionError, BridgeError)
    assert issubclass(ProtocolError, BridgeError)
    assert issubclass(ToolExecutionError, AgentUIError)
    assert issubclass(ProviderError, AgentUIError)
    assert issubclass(ValidationError, AgentUIError)
    assert issubclass(SkillLoadError, AgentUIError)


def test_exception_messages():
    """Test exceptions can carry messages."""
    error = ToolExecutionError("Tool failed")
    assert str(error) == "Tool failed"

    error = BridgeError("Connection lost")
    assert str(error) == "Connection lost"


def test_bridge_error_subclasses():
    """Test BridgeError has specific subclasses."""
    conn_error = ConnectionError("Failed to connect")
    proto_error = ProtocolError("Invalid JSON")

    assert isinstance(conn_error, BridgeError)
    assert isinstance(proto_error, BridgeError)
    assert isinstance(conn_error, AgentUIError)
    assert isinstance(proto_error, AgentUIError)


def test_all_exceptions_are_catchable_as_agentui_error():
    """Test that all custom exceptions can be caught with base class."""
    exceptions = [
        ConfigurationError("config"),
        BridgeError("bridge"),
        ConnectionError("connection"),
        ProtocolError("protocol"),
        ToolExecutionError("tool"),
        ProviderError("provider"),
        ValidationError("validation"),
        SkillLoadError("skill"),
    ]

    for exc in exceptions:
        assert isinstance(exc, AgentUIError)


def test_configuration_error():
    """Test ConfigurationError for config-related errors."""
    error = ConfigurationError("Invalid configuration")
    assert str(error) == "Invalid configuration"
    assert isinstance(error, AgentUIError)


def test_provider_error():
    """Test ProviderError for LLM provider errors."""
    error = ProviderError("API key not found")
    assert str(error) == "API key not found"
    assert isinstance(error, AgentUIError)


def test_skill_load_error():
    """Test SkillLoadError for skill loading failures."""
    error = SkillLoadError("Skill not found")
    assert str(error) == "Skill not found"
    assert isinstance(error, AgentUIError)


def test_validation_error():
    """Test ValidationError for input validation."""
    error = ValidationError("Invalid input")
    assert str(error) == "Invalid input"
    assert isinstance(error, AgentUIError)


def test_exceptions_are_distinct():
    """Test that different exception types are distinct."""
    conn_error = ConnectionError("connection")
    proto_error = ProtocolError("protocol")

    # Both are BridgeErrors
    assert isinstance(conn_error, BridgeError)
    assert isinstance(proto_error, BridgeError)

    # But they are distinct types
    assert type(conn_error) != type(proto_error)
    assert not isinstance(conn_error, ProtocolError)
    assert not isinstance(proto_error, ConnectionError)


def test_exception_catching_with_base_class():
    """Test that exceptions can be caught with their base class."""
    with pytest.raises(BridgeError):
        raise ConnectionError("test")

    with pytest.raises(AgentUIError):
        raise BridgeError("test")

    with pytest.raises(AgentUIError):
        raise ToolExecutionError("test")
