"""
AgentApp - High-level application wrapper.

Provides the simple, decorator-based API for creating agents.
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
    Main application class for creating AI agents.
    
    Usage:
        app = AgentApp(name="my-agent", provider="claude")
        
        @app.tool(
            name="get_weather",
            description="Get current weather",
            parameters={...}
        )
        def get_weather(city: str):
            return {"temp": 22}
        
        asyncio.run(app.run())
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
        
        Args:
            name: Application name
            manifest: Path to app.yaml or AppManifest object
            provider: LLM provider ("claude", "openai")
            model: Model name (uses provider default if not specified)
            api_key: API key (uses env var if not specified)
            max_tokens: Max tokens for responses
            temperature: Temperature for generation
            system_prompt: System prompt for the agent
            theme: UI theme name
            tagline: Tagline shown in UI header
            debug: Enable debug logging
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
        """Load manifest from file."""
        path = Path(path)

        if path.is_dir():
            path = path / "app.yaml"

        if not path.exists():
            raise FileNotFoundError(f"Manifest not found: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        return AppManifest.from_dict(data)

    def _get_api_key(self, provider: str) -> str | None:
        """Get API key from environment."""
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
        
        Shorthand for @tool(..., is_ui_tool=True)
        """
        return self.tool(name, description, parameters, is_ui_tool=True)

    async def run(self, prompt: str | None = None) -> None:
        """
        Run the agent application.
        
        Args:
            prompt: Optional initial prompt to send
        """
        tui_config = TUIConfig(
            theme=self.config.theme,
            app_name=self.config.app_name,
            tagline=self.config.tagline,
            debug=self._debug,
        )

        async with managed_bridge(tui_config, fallback=True) as bridge:
            self._bridge = bridge

            # Create core
            self._core = AgentCore(config=self.config, bridge=bridge)

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
        Send a single message and get a response.
        
        Useful for programmatic use without the TUI.
        
        Args:
            message: User message
            
        Returns:
            Assistant response
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
    **kwargs,
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
