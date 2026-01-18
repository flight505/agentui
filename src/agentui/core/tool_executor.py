"""
Tool execution and result handling.

Manages tool registration, execution, confirmation, and component selection.
"""

import asyncio
import logging
from typing import Any

from agentui.bridge import BridgeError
from agentui.component_selector import ComponentSelector
from agentui.primitives import (
    UIAlert,
    UICode,
    UIConfirm,
    UIForm,
    UIMarkdown,
    UIProgress,
    UISelect,
    UITable,
    UIText,
)
from agentui.types import ToolDefinition, ToolResult

logger = logging.getLogger(__name__)


class ToolExecutionError(Exception):
    """Error during tool execution."""
    pass


class ToolExecutor:
    """Handles tool execution and result processing."""

    def __init__(self, bridge_getter=None):
        """Initialize the tool executor.

        Args:
            bridge_getter: Optional callable that returns the current bridge
        """
        self.tools: dict[str, ToolDefinition] = {}
        self._bridge_getter = bridge_getter

    @property
    def bridge(self):
        """Get the current bridge."""
        return self._bridge_getter() if self._bridge_getter else None

    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool for execution."""
        self.tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")

    def get_tool_schemas(self) -> list[dict]:
        """Get tool schemas for the LLM."""
        return [tool.to_schema() for tool in self.tools.values()]

    async def execute_tool(
        self, tool_name: str, tool_id: str, arguments: dict
    ) -> ToolResult:
        """Execute a tool and return the result."""
        if tool_name not in self.tools:
            return self._create_error_result(
                tool_name, tool_id, f"Unknown tool: {tool_name}"
            )

        tool = self.tools[tool_name]
        logger.debug(f"Executing tool: {tool_name} with args: {arguments}")

        # Check if confirmation is required
        if not await self._confirm_tool_execution(tool_name, tool):
            return self._create_error_result(
                tool_name, tool_id, "Tool execution cancelled by user"
            )

        # Update status
        await self._send_tool_spinner(tool_name)

        try:
            result = await self._execute_tool_handler(tool, arguments)
            result, is_ui = self._apply_component_selection(tool, result, tool_name)

            logger.debug(f"Tool {tool_name} completed successfully")

            return ToolResult(
                tool_name=tool_name,
                tool_id=tool_id,
                result=result,
                is_ui=is_ui,
            )

        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return self._create_error_result(tool_name, tool_id, str(e))

    def _create_error_result(
        self, tool_name: str, tool_id: str, error: str
    ) -> ToolResult:
        """Create an error ToolResult."""
        logger.warning(f"Tool error: {tool_name} - {error}")
        return ToolResult(
            tool_name=tool_name,
            tool_id=tool_id,
            result=None,
            error=error,
        )

    async def _confirm_tool_execution(self, tool_name: str, tool) -> bool:
        """Check if tool requires confirmation and get user confirmation."""
        if not (tool.requires_confirmation and self.bridge):
            return True

        try:
            confirmed = await self.bridge.request_confirm(
                f"Allow tool '{tool_name}' to execute?",
                title="Tool Confirmation",
            )
            if not confirmed:
                logger.info(f"Tool {tool_name} execution cancelled by user")
            return confirmed
        except BridgeError as e:
            logger.error(f"Failed to request confirmation: {e}")
            return True  # Continue on bridge error

    async def _send_tool_spinner(self, tool_name: str) -> None:
        """Send spinner status update for tool execution."""
        if self.bridge:
            try:
                await self.bridge.send_spinner(f"Running {tool_name}...")
            except BridgeError:
                pass

    async def _execute_tool_handler(self, tool, arguments: dict):
        """Execute the tool handler (async or sync)."""
        if asyncio.iscoroutinefunction(tool.handler):
            return await tool.handler(**arguments)

        # Run sync function in executor
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, lambda: tool.handler(**arguments))

    def _apply_component_selection(
        self, tool, result, tool_name: str
    ) -> tuple[Any, bool]:
        """Apply automatic component selection for tool results."""
        ui_primitives = (
            UIForm,
            UIConfirm,
            UISelect,
            UIProgress,
            UITable,
            UICode,
            UIAlert,
            UIText,
            UIMarkdown,
        )

        is_ui = tool.is_ui_tool or isinstance(result, ui_primitives)

        # Auto-select component if not already a UI primitive
        if not is_ui and not isinstance(result, ui_primitives):
            component_type, ui_primitive = ComponentSelector.select_component(result)

            if component_type != "text" or isinstance(
                ui_primitive, (UITable, UICode, UIMarkdown)
            ):
                logger.debug(
                    f"Auto-selected component: {component_type} for tool {tool_name}"
                )
                result = ui_primitive
                is_ui = True

        return result, is_ui
