"""
Core type definitions for AgentUI.

This module defines the core types used throughout AgentUI for representing
agent state, tool definitions, messages, and configuration.

Key types:
    - ToolDefinition: Defines a callable tool with LLM schema
    - Message: Conversation message with role and content
    - ToolResult: Result of executing a tool
    - AgentState: Current state of the running agent
    - StreamChunk: Streaming response chunk
    - AppManifest: Application manifest loaded from app.yaml

Configuration types (re-exported from agentui.config):
    - ProviderType: LLM provider enumeration
    - AgentConfig: Agent configuration
    - TUIConfig: TUI display configuration
"""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

# Import configuration classes from dedicated config module
# Re-exported here for backward compatibility
from agentui.config import AgentConfig, ProviderType, TUIConfig

# Make mypy happy with re-exports
__all__ = ["ProviderType", "AgentConfig", "TUIConfig", "ToolDefinition", "Message",
           "ToolResult", "AgentState", "StreamChunk", "AppManifest"]


@dataclass
class ToolDefinition:
    """
    Definition of a callable tool for LLM use.

    Defines a tool that the agent can call, including its schema for the LLM
    and the handler function that executes when called.

    Attributes:
        name: Tool name exposed to the LLM
        description: Tool description shown to the LLM
        parameters: JSON Schema describing tool parameters
        handler: Sync or async function that executes the tool
        is_ui_tool: If True, handler returns UI primitives instead of data
        requires_confirmation: If True, prompts user before execution

    Example:
        >>> def get_weather(city: str) -> dict:
        ...     return {"temp": 72, "conditions": "sunny"}
        >>>
        >>> tool = ToolDefinition(
        ...     name="get_weather",
        ...     description="Get current weather for a city",
        ...     parameters={
        ...         "type": "object",
        ...         "properties": {
        ...             "city": {"type": "string"}
        ...         },
        ...         "required": ["city"]
        ...     },
        ...     handler=get_weather
        ... )
    """
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any] | Callable[..., Awaitable[Any]]
    is_ui_tool: bool = False  # If True, returns UI primitives
    requires_confirmation: bool = False

    def to_schema(self) -> dict:
        """
        Convert to LLM tool schema format.

        Returns:
            Dictionary in Anthropic tool schema format with name,
            description, and input_schema
        """
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


@dataclass
class Message:
    """
    A single message in the conversation history.

    Attributes:
        role: Message role ("user", "assistant", or "system")
        content: Message text content
        tool_calls: Optional list of tool calls made by assistant
        tool_results: Optional list of tool execution results
    """
    role: str  # "user", "assistant", "system"
    content: str
    tool_calls: list[dict] | None = None
    tool_results: list[dict] | None = None


@dataclass
class ToolResult:
    """
    Result of executing a tool.

    Encapsulates the outcome of a tool execution, including success/error
    status and the returned value.

    Attributes:
        tool_name: Name of the tool that was executed
        tool_id: Unique ID for this tool execution
        result: The value returned by the tool handler
        error: Error message if execution failed
        is_ui: If True, result is a UI primitive object
    """
    tool_name: str
    tool_id: str
    result: Any
    error: str | None = None
    is_ui: bool = False  # If True, result is a UI primitive


@dataclass
class AgentState:
    """
    Current state of a running agent.

    Tracks conversation history, execution status, and token usage.

    Attributes:
        messages: Conversation history (list of Message objects)
        is_running: Whether the agent is currently processing
        current_tool: Name of tool currently being executed (if any)
        total_input_tokens: Total input tokens used in conversation
        total_output_tokens: Total output tokens generated in conversation
    """
    messages: list[Message] = field(default_factory=list)
    is_running: bool = False
    current_tool: str | None = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0


@dataclass
class StreamChunk:
    """
    A chunk of streaming LLM response.

    Used to incrementally deliver LLM responses as they're generated.

    Attributes:
        content: Text content of this chunk
        is_complete: Whether this is the final chunk
        input_tokens: Input tokens used (included in final chunk)
        output_tokens: Output tokens generated (included in final chunk)
    """
    content: str
    is_complete: bool = False
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass
class AppManifest:
    """
    Application manifest loaded from app.yaml.

    Defines app metadata, provider configuration, UI settings, and skills.

    Attributes:
        name: Application identifier
        version: Semantic version string
        description: App description
        display_name: Display name for UI (falls back to name)
        icon: Icon emoji for the app
        tagline: Tagline shown in UI header
        provider: Default LLM provider ("claude", "openai", "gemini")
        model: Model identifier (optional, uses provider default if None)
        max_tokens: Maximum tokens for responses
        skills: List of skill directory paths to load
        system_prompt: System prompt defining agent behavior
        theme: UI theme name
        welcome_title: Welcome screen title
        welcome_subtitle: Welcome screen subtitle
        welcome_features: List of feature bullet points for welcome screen
        output_directory: Directory for saving outputs

    Example:
        From app.yaml:

        ```yaml
        name: my-agent
        display_name: "My Agent"
        tagline: "Helpful AI Assistant"
        provider: claude
        model: claude-3-5-sonnet-20241022
        skills:
          - ./skills/weather
          - ./skills/calculator
        ```
    """
    name: str
    version: str = "1.0.0"
    description: str = ""
    display_name: str | None = None
    icon: str = "🤖"
    tagline: str = ""

    # Provider config
    provider: str = "claude"
    model: str | None = None
    max_tokens: int = 4096

    # Skills
    skills: list[str] = field(default_factory=list)

    # System prompt
    system_prompt: str = ""

    # UI config
    theme: str = "catppuccin-mocha"

    # Welcome screen
    welcome_title: str | None = None
    welcome_subtitle: str | None = None
    welcome_features: list[str] = field(default_factory=list)

    # Output config
    output_directory: str = "./outputs"

    @classmethod
    def from_dict(cls, data: dict) -> "AppManifest":
        """
        Create AppManifest from parsed YAML dictionary.

        Args:
            data: Dictionary parsed from app.yaml

        Returns:
            AppManifest instance with nested values extracted
        """
        # Extract nested values
        providers = data.get("providers", {})
        default_provider = providers.get("default", "claude")
        provider_config = providers.get(default_provider, {})

        ui = data.get("ui", {})
        welcome = ui.get("welcome", {})
        output = data.get("output", {})

        return cls(
            name=data.get("name", "agent"),
            version=data.get("version", "1.0.0"),
            description=data.get("description", ""),
            display_name=data.get("display_name"),
            icon=data.get("icon", "🤖"),
            tagline=data.get("tagline", ""),
            provider=default_provider,
            model=provider_config.get("model"),
            max_tokens=provider_config.get("max_tokens", 4096),
            skills=data.get("skills", []),
            system_prompt=data.get("system_prompt", ""),
            theme=ui.get("theme", "catppuccin-mocha"),
            welcome_title=welcome.get("title"),
            welcome_subtitle=welcome.get("subtitle"),
            welcome_features=welcome.get("features", []),
            output_directory=output.get("directory", "./outputs"),
        )
