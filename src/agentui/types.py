"""
Core types for AgentUI.
"""

from dataclasses import dataclass, field
from typing import Any, Callable, Awaitable
from enum import Enum


class ProviderType(str, Enum):
    """Supported LLM providers."""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    OLLAMA = "ollama"


@dataclass
class ToolDefinition:
    """Definition of a tool that the agent can use."""
    name: str
    description: str
    parameters: dict[str, Any]
    handler: Callable[..., Any] | Callable[..., Awaitable[Any]]
    is_ui_tool: bool = False  # If True, returns UI primitives
    requires_confirmation: bool = False
    
    def to_schema(self) -> dict:
        """Convert to LLM tool schema format."""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.parameters,
        }


@dataclass
class Message:
    """A conversation message."""
    role: str  # "user", "assistant", "system"
    content: str
    tool_calls: list[dict] | None = None
    tool_results: list[dict] | None = None


@dataclass
class AgentConfig:
    """Configuration for the agent."""
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


@dataclass
class ToolResult:
    """Result of a tool execution."""
    tool_name: str
    tool_id: str
    result: Any
    error: str | None = None
    is_ui: bool = False  # If True, result is a UI primitive


@dataclass
class AgentState:
    """Current state of the agent."""
    messages: list[Message] = field(default_factory=list)
    is_running: bool = False
    current_tool: str | None = None
    total_input_tokens: int = 0
    total_output_tokens: int = 0


@dataclass
class StreamChunk:
    """A chunk of streamed content."""
    content: str
    is_complete: bool = False
    input_tokens: int | None = None
    output_tokens: int | None = None


@dataclass
class AppManifest:
    """Application manifest (from app.yaml)."""
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
        """Create from dictionary (parsed YAML)."""
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
