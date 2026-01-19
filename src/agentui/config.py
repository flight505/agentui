"""Configuration management for AgentUI."""

import os
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import yaml


class ProviderType(str, Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"


@dataclass
class AgentConfig:
    """
    Main agent configuration.

    Controls LLM provider settings, model parameters, and agent behavior.
    Can be loaded from environment variables or YAML files.

    Attributes:
        provider: LLM provider type (ProviderType or string)
        model: Model name (uses provider default if None)
        api_key: API key for the provider (loaded from env if None)
        max_tokens: Maximum tokens for responses
        temperature: Temperature for generation (0.0-1.0)
        system_prompt: System prompt for the agent
        max_tool_iterations: Maximum tool execution iterations
        theme: UI theme name
        app_name: Application name shown in UI
        tagline: Tagline shown in UI header
    """

    # Provider settings
    provider: ProviderType = ProviderType.CLAUDE
    model: str | None = None
    api_key: str | None = None
    max_tokens: int = 4096
    temperature: float = 0.7

    # System prompt
    system_prompt: str = "You are a helpful AI assistant."

    # Tool settings
    max_tool_iterations: int = 10

    # UI settings
    theme: str = "catppuccin-mocha"
    app_name: str = "AgentUI"
    tagline: str = "AI Agent Interface"

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """
        Create config from environment variables.

        Reads configuration from AGENTUI_* environment variables:
        - AGENTUI_MODEL: Model name
        - AGENTUI_PROVIDER: Provider type
        - AGENTUI_MAX_TOKENS: Maximum tokens (integer)
        - AGENTUI_TEMPERATURE: Temperature (float)
        - AGENTUI_THEME: UI theme name

        Returns:
            AgentConfig with values from environment or defaults
        """
        provider_str = os.getenv("AGENTUI_PROVIDER", "claude")
        provider = ProviderType(provider_str) if provider_str in [p.value for p in ProviderType] else ProviderType.CLAUDE

        return cls(
            model=os.getenv("AGENTUI_MODEL"),
            provider=provider,
            max_tokens=int(os.getenv("AGENTUI_MAX_TOKENS", "4096")),
            temperature=float(os.getenv("AGENTUI_TEMPERATURE", "0.7")),
            theme=os.getenv("AGENTUI_THEME", "catppuccin-mocha"),
        )

    @classmethod
    def from_file(cls, path: Path) -> "AgentConfig":
        """
        Load config from YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            AgentConfig with values from file

        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If file is not valid YAML
        """
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


@dataclass
class TUIConfig:
    """
    TUI bridge configuration.

    Controls how the Python agent communicates with the Go TUI subprocess.

    Attributes:
        theme: UI theme name
        app_name: Application name shown in header
        tagline: Tagline shown in header
        tui_path: Path to agentui-tui binary (auto-detected if None)
        debug: Enable debug logging
        reconnect_attempts: Number of reconnection attempts on failure
        reconnect_delay: Delay between reconnection attempts (seconds)
    """

    theme: str = "catppuccin-mocha"
    app_name: str = "AgentUI"
    tagline: str = "AI Agent Interface"
    tui_path: str | None = None
    debug: bool = False
    reconnect_attempts: int = 3
    reconnect_delay: float = 1.0

    @classmethod
    def from_env(cls) -> "TUIConfig":
        """
        Create config from environment variables.

        Reads configuration from AGENTUI_* environment variables:
        - AGENTUI_THEME: UI theme name
        - AGENTUI_TUI_PATH: Path to TUI binary
        - AGENTUI_DEBUG: Enable debug mode (any non-empty value)

        Returns:
            TUIConfig with values from environment or defaults
        """
        return cls(
            theme=os.getenv("AGENTUI_THEME", "catppuccin-mocha"),
            tui_path=os.getenv("AGENTUI_TUI_PATH"),
            debug=bool(os.getenv("AGENTUI_DEBUG")),
        )


__all__ = ["AgentConfig", "TUIConfig", "ProviderType"]
