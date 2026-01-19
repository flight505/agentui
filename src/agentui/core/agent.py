"""
Main AgentCore implementation.

Core agent execution engine that delegates to specialized components.
"""

import asyncio
import logging
from collections.abc import AsyncIterator

from agentui.bridge import CLIBridge, TUIBridge
from agentui.component_catalog import ComponentCatalog
from agentui.core.display_tools import DisplayToolRegistry
from agentui.core.message_handler import MessageHandler
from agentui.core.tool_executor import ToolExecutor
from agentui.core.ui_handler import UIHandler
from agentui.exceptions import (
    AgentUIError as AgentError,
    BridgeError,
    ConfigurationError,
)
from agentui.protocol import MessageType
from agentui.types import AgentConfig, AgentState, StreamChunk, ToolDefinition, ToolResult

logger = logging.getLogger(__name__)


class AgentCore:
    """
    Core agent execution engine.

    Manages the agent loop, tool execution, and UI updates.
    Delegates specialized tasks to component handlers.
    """

    def __init__(
        self,
        config: AgentConfig | None = None,
        bridge: TUIBridge | CLIBridge | None = None,
    ):
        self.config = config or AgentConfig()
        self.bridge = bridge
        self.state = AgentState()

        # Delegate to specialized components (pass self to access bridge dynamically)
        self.tool_executor = ToolExecutor(bridge_getter=lambda: self.bridge)
        self.message_handler = MessageHandler(state=self.state)
        self.ui_handler = UIHandler(bridge_getter=lambda: self.bridge)
        self.display_tools = DisplayToolRegistry(bridge_getter=lambda: self.bridge)

        self._provider = None
        self._setup_assistant = None  # Fallback when provider fails
        self._running = False

        # Enhance system prompt with component catalog (Phase 1: Generative UI)
        self._enhance_system_prompt_with_catalog()

        # Auto-register display tools (Phase 1: Generative UI)
        self.display_tools.register_display_tools(self.tool_executor)

    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool for the agent to use."""
        self.tool_executor.register_tool(tool)

    def get_tool_schemas(self) -> list[dict]:
        """Get tool schemas for the LLM."""
        return self.tool_executor.get_tool_schemas()

    @property
    def tools(self) -> dict:
        """Get registered tools (for backward compatibility)."""
        return self.tool_executor.tools

    @property
    def _cancel_requested(self) -> bool:
        """Check if cancellation was requested (for backward compatibility)."""
        return self.message_handler.is_cancelled()

    @_cancel_requested.setter
    def _cancel_requested(self, value: bool) -> None:
        """Set cancellation state (for backward compatibility)."""
        if value:
            self.message_handler.request_cancel()
        else:
            self.message_handler.reset_cancel()

    def _create_error_result(self, tool_name: str, tool_id: str, error: str):
        """Create an error ToolResult (for backward compatibility)."""
        return self.tool_executor._create_error_result(tool_name, tool_id, error)

    async def _stream_provider_response(self, provider):
        """Stream provider response (for backward compatibility)."""
        return await self.message_handler.stream_provider_response(
            provider,
            self.config.system_prompt,
            self.get_tool_schemas() if self.tool_executor.tools else None,
        )

    def _enhance_system_prompt_with_catalog(self) -> None:
        """
        Enhance system prompt with component catalog (Phase 1: Generative UI).

        Adds LLM-friendly documentation of all available UI components,
        usage guidelines, and selection heuristics.
        """
        catalog_prompt = ComponentCatalog.get_catalog_prompt()

        # Append catalog to existing system prompt
        enhanced_prompt = f"""{self.config.system_prompt}

{catalog_prompt}
"""
        self.config.system_prompt = enhanced_prompt
        logger.debug("Enhanced system prompt with component catalog")

    async def _get_provider(self):
        """Get or create the LLM provider."""
        if self._provider is None:
            provider_name = self.config.provider.value

            if provider_name == "claude":
                from agentui.providers.claude import ClaudeProvider

                self._provider = ClaudeProvider(
                    model=self.config.model,
                    api_key=self.config.api_key,
                    max_tokens=self.config.max_tokens,
                )
            elif provider_name == "openai":
                from agentui.providers.openai import OpenAIProvider

                self._provider = OpenAIProvider(
                    model=self.config.model,
                    api_key=self.config.api_key,
                    max_tokens=self.config.max_tokens,
                )
            else:
                raise ConfigurationError(f"Unsupported provider: {provider_name}")

            logger.info(f"Initialized provider: {provider_name}")

        return self._provider

    async def execute_tool(
        self, tool_name: str, tool_id: str, arguments: dict
    ) -> ToolResult:
        """Execute a tool and return the result."""
        return await self.tool_executor.execute_tool(tool_name, tool_id, arguments)

    async def handle_ui_result(self, result):
        """Handle UI primitive results from tools."""
        return await self.ui_handler.handle_ui_result(result)

    async def process_message(self, user_input: str) -> AsyncIterator[StreamChunk]:
        """
        Process a user message and yield response chunks.

        This is the main agent loop for a single turn.
        """
        self.message_handler.reset_cancel()

        # Add user message to state
        self.message_handler.add_user_message(user_input)

        try:
            provider = await self._get_provider()
        except Exception as e:
            async for chunk in self._handle_provider_error(e, user_input):
                yield chunk
            return

        iterations = 0

        while iterations < self.config.max_tool_iterations:
            if self.message_handler.is_cancelled():
                logger.info("Processing cancelled by user")
                yield StreamChunk(content=" [Cancelled]", is_complete=True)
                return

            iterations += 1

            # Stream response and collect tool calls
            (
                full_response,
                tool_calls,
                should_return,
            ) = await self.message_handler.stream_provider_response(
                provider,
                self.config.system_prompt,
                self.get_tool_schemas() if self.tool_executor.tools else None,
            )

            if should_return:
                return

            async for chunk in full_response:
                yield chunk

            # If no tool calls, we're done
            if not tool_calls:
                break

            # Execute tools and add results to messages
            await self._execute_and_record_tools(tool_calls)

        # Final completion marker
        yield StreamChunk(content="", is_complete=True)

    async def _handle_provider_error(
        self, error: Exception, user_input: str
    ) -> AsyncIterator[StreamChunk]:
        """Handle provider initialization error with setup assistant fallback."""
        logger.error(f"Failed to get provider: {error}")

        if self._setup_assistant is None:
            from agentui.setup_assistant import SetupAssistant

            self._setup_assistant = SetupAssistant(provider_error=str(error))

        async for response_text in self._setup_assistant.process_message(user_input):
            yield StreamChunk(content=response_text, is_complete=True)

    async def _execute_and_record_tools(self, tool_calls: list[dict]) -> None:
        """Execute tool calls and add results to message state."""
        tool_results = []

        for call in tool_calls:
            if self.message_handler.is_cancelled():
                break

            result = await self.execute_tool(
                tool_name=call["name"],
                tool_id=call["id"],
                arguments=call.get("input", {}),
            )

            # Handle UI results
            if result.is_ui and result.result:
                ui_response = await self.handle_ui_result(result.result)
                if ui_response is not None:
                    result = ToolResult(
                        tool_name=result.tool_name,
                        tool_id=result.tool_id,
                        result=ui_response,
                    )

            tool_results.append(result)

        # Add tool results to messages
        self.message_handler.add_tool_results(tool_results)

    def cancel(self) -> None:
        """Request cancellation of current processing."""
        self.message_handler.request_cancel()

    async def run_loop(self) -> None:
        """
        Run the main agent loop.

        Listens for user input and processes messages.
        """
        if not self.bridge:
            raise ConfigurationError("Bridge not set")

        self._running = True

        await self._send_initial_status()

        try:
            async for event in self.bridge.events():
                if not self._running:
                    break

                await self._handle_event(event)

        except asyncio.CancelledError:
            logger.info("Agent loop cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in agent loop: {e}")
        finally:
            self._running = False

    async def _send_initial_status(self) -> None:
        """Send initial ready status to bridge."""
        assert self.bridge is not None, "Bridge must be set before sending status"
        try:
            await self.bridge.send_status(
                f"Ready · {self.config.provider.value}",
                input_tokens=0,
                output_tokens=0,
            )
        except BridgeError as e:
            logger.error(f"Failed to send initial status: {e}")

    async def _handle_event(self, event) -> None:
        """Dispatch event to appropriate handler based on event type."""
        event_type = event.type

        if event_type == MessageType.INPUT.value:
            await self._handle_input_event(event)
        elif event_type == MessageType.QUIT.value:
            await self._handle_quit_event()
        elif event_type == MessageType.CANCEL.value:
            await self._handle_cancel_event()
        elif event_type == "resize":
            # Handle resize if needed
            pass

    async def _handle_input_event(self, event) -> None:
        """Handle user input event."""
        assert self.bridge is not None, "Bridge must be set before handling input"
        bridge = self.bridge  # Local variable for type safety
        user_input = event.payload.get("content", "")
        if not user_input:
            return

        logger.debug(f"Processing input: {user_input[:50]}...")

        try:
            async for chunk in self.process_message(user_input):
                if chunk.content:
                    await bridge.send_text(
                        chunk.content,
                        done=chunk.is_complete,
                    )

                if chunk.is_complete:
                    await bridge.send_status(
                        f"Ready · {self.config.provider.value}",
                        input_tokens=self.state.total_input_tokens,
                        output_tokens=self.state.total_output_tokens,
                    )

            await bridge.send_done()

        except BridgeError as e:
            logger.error(f"Bridge error while processing: {e}")
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self._send_error_alert(e)

    async def _send_error_alert(self, error: Exception) -> None:
        """Send error alert to bridge, ignoring bridge errors."""
        if not self.bridge:
            return
        try:
            await self.bridge.send_alert(
                str(error),
                severity="error",
                title="Error",
            )
        except BridgeError:
            pass

    async def _handle_quit_event(self) -> None:
        """Handle quit event."""
        logger.info("Quit requested")
        self._running = False

    async def _handle_cancel_event(self) -> None:
        """Handle cancel event."""
        logger.info("Cancel requested")
        self.cancel()

    def stop(self) -> None:
        """Stop the agent loop."""
        self._running = False
        self.cancel()
