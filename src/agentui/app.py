"""
AgentApp - High-level application wrapper for building AI agents.

This module provides the primary API for creating AI agents with AgentUI.
It offers a decorator-based interface for registering tools and a simple
async API for running agents with either a TUI or CLI interface.

The AgentApp class handles:
- LLM provider configuration and initialization
- Tool registration and management
- Application manifest loading
- Bridge lifecycle management (TUI/CLI fallback)
- Agent execution loop

Example:
    Basic agent with a custom tool:

    >>> from agentui import AgentApp
    >>> import asyncio
    >>>
    >>> app = AgentApp(name="weather-agent", provider="claude")
    >>>
    >>> @app.tool(
    ...     name="get_weather",
    ...     description="Get current weather for a city",
    ...     parameters={
    ...         "type": "object",
    ...         "properties": {
    ...             "city": {"type": "string", "description": "City name"}
    ...         },
    ...         "required": ["city"]
    ...     }
    ... )
    ... async def get_weather(city: str):
    ...     return {"temperature": 72, "conditions": "sunny"}
    >>>
    >>> asyncio.run(app.run())

    Loading from manifest:

    >>> app = AgentApp(manifest="./app.yaml")
    >>> asyncio.run(app.run(prompt="Hello!"))
"""

import logging
import os
from collections.abc import Callable
from pathlib import Path
from typing import Any

import yaml

from agentui.bridge import CLIBridge, TUIBridge, TUIConfig, managed_bridge
from agentui.core import AgentCore
from agentui.types import (
    AgentConfig,
    AppManifest,
    ProviderType,
    ToolDefinition,
)

logger = logging.getLogger(__name__)


class AgentApp:
    """
    Main application class for creating AI agents with AgentUI.

    AgentApp provides the high-level API for building AI agents. It manages
    the agent lifecycle, LLM provider configuration, tool registration, and
    UI bridge setup. Agents can be configured via code or loaded from a
    manifest file (app.yaml).

    The class uses a decorator pattern for tool registration and supports
    both interactive TUI mode and programmatic chat mode.

    Attributes:
        manifest: Application manifest loaded from app.yaml or provided directly
        config: Agent configuration (provider, model, prompts, etc.)
        _core: AgentCore instance (created when run() is called)
        _bridge: UI bridge instance (TUIBridge or CLIBridge)
        _tools: List of registered tool definitions
        _debug: Debug mode flag

    Example:
        Create and run an agent:

        >>> app = AgentApp(name="my-agent", provider="claude")
        >>>
        >>> @app.tool(
        ...     name="get_weather",
        ...     description="Get current weather",
        ...     parameters={
        ...         "type": "object",
        ...         "properties": {
        ...             "city": {"type": "string"}
        ...         },
        ...         "required": ["city"]
        ...     }
        ... )
        ... def get_weather(city: str):
        ...     return {"temp": 22, "conditions": "sunny"}
        >>>
        >>> asyncio.run(app.run())

        Programmatic chat mode:

        >>> app = AgentApp(provider="openai", model="gpt-4")
        >>> response = asyncio.run(app.chat("What is 2+2?"))
        >>> print(response)
        '2 + 2 equals 4.'
    """

    def __init__(
        self,
        name: str = "agent",
        manifest: str | Path | AppManifest | None = None,
        provider: str = "claude",
        model: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        system_prompt: str | None = None,
        theme: str = "catppuccin-mocha",
        tagline: str = "AI Agent Interface",
        debug: bool = False,
    ):
        """
        Initialize the agent application.

        Creates a new agent with the specified configuration. If a manifest
        is provided, configuration values are loaded from it and merged with
        constructor arguments (constructor args take precedence).

        Args:
            name: Application name used for identification
            manifest: Path to app.yaml file, directory containing app.yaml,
                or an AppManifest object. If provided, loads configuration
                from the manifest.
            provider: LLM provider name ("claude", "openai", "gemini")
            model: Model identifier. If None, uses provider default
                (e.g., "claude-3-5-sonnet-20241022" for Claude)
            api_key: API key for the LLM provider. If None, reads from
                environment variables (ANTHROPIC_API_KEY, OPENAI_API_KEY, etc.)
            max_tokens: Maximum tokens for LLM responses
            temperature: Temperature for generation (0.0-1.0). Higher values
                produce more random outputs
            system_prompt: System prompt that defines agent behavior. If None,
                uses manifest system_prompt or default
            theme: UI theme name for the TUI (e.g., "catppuccin-mocha", "charm-dark")
            tagline: Tagline displayed in the UI header
            debug: Enable debug logging to stderr

        Raises:
            FileNotFoundError: If manifest path is provided but file doesn't exist

        Example:
            >>> app = AgentApp(
            ...     name="assistant",
            ...     provider="claude",
            ...     model="claude-3-5-sonnet-20241022",
            ...     system_prompt="You are a helpful coding assistant.",
            ...     debug=True
            ... )
        """
        if debug:
            logging.basicConfig(level=logging.DEBUG)

        # Load manifest if provided
        if manifest:
            if isinstance(manifest, (str, Path)):
                manifest = self._load_manifest(manifest)
            self.manifest = manifest
        else:
            self.manifest = AppManifest(name=name)

        # Build config from manifest and overrides
        self.config = AgentConfig(
            provider=ProviderType(provider),
            model=model or self.manifest.model,
            api_key=api_key or self._get_api_key(provider),
            max_tokens=max_tokens,
            temperature=temperature,
            system_prompt=(
                system_prompt
                or self.manifest.system_prompt
                or "You are a helpful AI assistant."
            ),
            theme=theme,
            app_name=self.manifest.display_name or name,
            tagline=tagline or self.manifest.tagline,
        )

        self._debug = debug
        self._core: AgentCore | None = None
        self._bridge: TUIBridge | CLIBridge | None = None
        self._tools: list[ToolDefinition] = []

    def _load_manifest(self, path: str | Path) -> AppManifest:
        """
        Load application manifest from YAML file.

        Args:
            path: Path to app.yaml file or directory containing it

        Returns:
            Parsed AppManifest object

        Raises:
            FileNotFoundError: If the manifest file doesn't exist
        """
        path = Path(path)

        if path.is_dir():
            path = path / "app.yaml"

        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        return AppManifest.from_dict(data)

    def _get_api_key(self, provider: str) -> str | None:
        """
        Get API key from environment variables.

        Args:
            provider: Provider name ("claude", "openai", "gemini")

        Returns:
            API key from environment, or None if not found
        """
        env_vars = {
            "claude": "ANTHROPIC_API_KEY",
            "openai": "OPENAI_API_KEY",
            "gemini": "GOOGLE_API_KEY",
        }
        var_name = env_vars.get(provider)
        key = os.environ.get(var_name) if var_name else None
        if not key and provider in ("claude", "openai"):
            logger.warning(f"No API key found for {provider}. Set {var_name} environment variable.")
        return key

    def tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
        is_ui_tool: bool = False,
        requires_confirmation: bool = False,
    ) -> Callable:
        """
        Decorator to register a tool.
        
        Args:
            name: Tool name (used by LLM)
            description: Tool description (shown to LLM)
            parameters: JSON schema for parameters
            is_ui_tool: If True, tool returns UI primitives
            requires_confirmation: If True, asks user before executing
        
        Example:
            @app.tool(
                name="search_web",
                description="Search the web",
                parameters={
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"}
                    },
                    "required": ["query"]
                }
            )
            async def search_web(query: str):
                return {"results": [...]}
        """
        def decorator(func: Callable) -> Callable:
            tool_def = ToolDefinition(
                name=name,
                description=description,
                parameters=parameters,
                handler=func,
                is_ui_tool=is_ui_tool,
                requires_confirmation=requires_confirmation,
            )
            self._tools.append(tool_def)
            logger.debug(f"Registered tool: {name}")
            return func
        return decorator

    def ui_tool(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any],
    ) -> Callable:
        """
        Decorator for tools that return UI primitives.

        Convenience decorator for registering tools that return UI components
        (UITable, UIForm, UICode, etc.) instead of plain data. Equivalent to
        using @tool(..., is_ui_tool=True).

        Args:
            name: Tool name (used by LLM)
            description: Tool description (shown to LLM)
            parameters: JSON schema for parameters

        Returns:
            Decorator function

        Example:
            >>> @app.ui_tool(
            ...     name="show_results",
            ...     description="Display search results in a table",
            ...     parameters={
            ...         "type": "object",
            ...         "properties": {
            ...             "results": {"type": "array"}
            ...         }
            ...     }
            ... )
            ... async def show_results(results: list):
            ...     from agentui.primitives import UITable
            ...     return UITable(
            ...         columns=["Name", "Score"],
            ...         rows=[[r["name"], str(r["score"])] for r in results]
            ...     )
        """
        return self.tool(name, description, parameters, is_ui_tool=True)

    async def run(self, prompt: str | None = None) -> None:
        """
        Run the agent application in interactive mode.

        Starts the agent with a TUI interface (or CLI fallback if TUI binary
        is unavailable). The agent runs in a loop, processing user messages
        and executing tools until the user exits.

        This method manages the complete lifecycle:
        1. Initializes the UI bridge (TUI or CLI)
        2. Creates the AgentCore
        3. Registers all tools
        4. Processes initial prompt if provided
        5. Runs the main event loop until user exits

        Args:
            prompt: Optional initial message to send to the agent. If provided,
                the agent processes this message before entering interactive mode.

        Example:
            >>> app = AgentApp(name="assistant", provider="claude")
            >>> await app.run()  # Interactive mode

            >>> await app.run(prompt="Analyze this codebase")  # With initial prompt
        """
        tui_config = TUIConfig(
            theme=self.config.theme,
            app_name=self.config.app_name,
            tagline=self.config.tagline,
            debug=self._debug,
        )

        async with managed_bridge(tui_config, fallback=True) as bridge:
            from typing import cast
            typed_bridge = cast(TUIBridge | CLIBridge, bridge)
            self._bridge = typed_bridge

            # Create core
            self._core = AgentCore(config=self.config, bridge=typed_bridge)

            # Register tools
            for tool in self._tools:
                self._core.register_tool(tool)

            # Send initial prompt if provided
            if prompt:
                try:
                    async for chunk in self._core.process_message(prompt):
                        if chunk.content:
                            await bridge.send_text(chunk.content, done=chunk.is_complete)
                    await bridge.send_done()
                except Exception as e:
                    logger.error(f"Error processing initial prompt: {e}")
                    await bridge.send_alert(str(e), severity="error")

            # Run main loop
            await self._core.run_loop()

    async def chat(self, message: str) -> str:
        """
        Send a single message and get a text response (no UI).

        Provides a programmatic API for interacting with the agent without
        launching the TUI. Useful for scripting, testing, or embedding
        agents in other applications.

        This method creates an AgentCore if needed and maintains conversation
        history across multiple calls. Tool execution is supported but UI
        primitives are not rendered (only their text representation is included).

        Args:
            message: User message to send to the agent

        Returns:
            Complete text response from the agent

        Example:
            >>> app = AgentApp(provider="claude")
            >>> response = await app.chat("What is the capital of France?")
            >>> print(response)
            'The capital of France is Paris.'

            >>> # Conversation context is maintained
            >>> response2 = await app.chat("What is its population?")
            >>> print(response2)
            'Paris has a population of approximately 2.2 million people...'
        """
        if not self._core:
            self._core = AgentCore(config=self.config)
            for tool in self._tools:
                self._core.register_tool(tool)

        response = ""
        async for chunk in self._core.process_message(message):
            response += chunk.content

        return response


# --- Convenience functions ---

def create_app(
    manifest: str | Path | None = None,
    **kwargs: Any,
) -> AgentApp:
    """
    Create an agent application.

    Args:
        manifest: Path to app.yaml or directory containing it
        **kwargs: Additional arguments passed to AgentApp
    
    Returns:
        AgentApp instance
    """
    return AgentApp(manifest=manifest, **kwargs)


async def quick_chat(
    message: str,
    provider: str = "claude",
    model: str | None = None,
    system_prompt: str | None = None,
) -> str:
    """
    Quick one-shot chat without creating an app.
    
    Args:
        message: User message
        provider: LLM provider
        model: Model name
        system_prompt: Optional system prompt
    
    Returns:
        Assistant response
    """
    app = AgentApp(
        provider=provider,
        model=model,
        system_prompt=system_prompt,
    )
    return await app.chat(message)
