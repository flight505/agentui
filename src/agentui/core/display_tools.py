"""
Display tool registration and handling.

Auto-registers display_* tools for UI primitives (Generative UI Phase 1).
"""

import logging
from typing import Any

from agentui.bridge import BridgeError
from agentui.component_catalog import ComponentCatalog
from agentui.types import ToolDefinition

logger = logging.getLogger(__name__)


class DisplayToolRegistry:
    """Manages registration and execution of display_* tools."""

    def __init__(self, bridge_getter=None):
        """Initialize the display tool registry.

        Args:
            bridge_getter: Optional callable that returns the current bridge
        """
        self._bridge_getter = bridge_getter

    @property
    def bridge(self):
        """Get the current bridge."""
        return self._bridge_getter() if self._bridge_getter else None

    def register_display_tools(self, tool_executor) -> None:
        """
        Auto-register display_* tools for UI primitives (Phase 1: Generative UI).

        Registers tools for:
        - display_table: Show tabular data
        - display_form: Collect user input
        - display_code: Show syntax-highlighted code
        - display_progress: Show progress indicators
        - display_confirm: Ask yes/no questions
        - display_alert: Show notifications
        - display_select: Single-choice selection

        Args:
            tool_executor: ToolExecutor instance to register tools with
        """
        tool_schemas = ComponentCatalog.get_tool_schemas()

        for schema in tool_schemas:
            tool_name = schema["name"]

            # Create handler that sends UI message via bridge
            handler = self._create_display_handler(tool_name, schema)

            # Register tool
            tool_executor.register_tool(
                ToolDefinition(
                    name=tool_name,
                    description=schema["description"],
                    parameters=schema["input_schema"],
                    handler=handler,
                    is_ui_tool=True,
                )
            )

        logger.debug(f"Auto-registered {len(tool_schemas)} display_* tools")

    def _create_display_handler(self, tool_name: str, schema: dict):
        """
        Create handler function for a display_* tool.

        The handler sends the appropriate UI message via the bridge.
        """

        async def handler(**kwargs):
            if not self.bridge:
                return f"[Would display {tool_name} with: {kwargs}]"

            msg_type = tool_name.replace("display_", "")

            try:
                return await self._execute_display_message(msg_type, kwargs)
            except BridgeError as e:
                logger.error(f"Failed to send {msg_type} message: {e}")
                return f"Error displaying {msg_type}: {e}"

        return handler

    async def _execute_display_message(self, msg_type: str, kwargs: dict):
        """Execute a display message based on type."""
        # Interactive messages that return data
        if msg_type == "form":
            return await self.bridge.request_form(
                fields=kwargs.get("fields", []),
                title=kwargs.get("title"),
                description=kwargs.get("description"),
            )

        if msg_type == "confirm":
            return await self.bridge.request_confirm(
                message=kwargs["message"],
                title=kwargs.get("title"),
                destructive=kwargs.get("destructive", False),
            )

        if msg_type == "select":
            return await self.bridge.request_select(
                label=kwargs["label"],
                options=kwargs["options"],
                default=kwargs.get("default"),
            )

        # Non-interactive display messages
        if msg_type == "table":
            await self.bridge.send_table(
                columns=kwargs["columns"],
                rows=kwargs["rows"],
                title=kwargs.get("title"),
                footer=kwargs.get("footer"),
            )
            return f"Displayed table: {kwargs.get('title', 'Table')}"

        if msg_type == "code":
            await self.bridge.send_code(
                code=kwargs["code"],
                language=kwargs.get("language", "text"),
                title=kwargs.get("title"),
            )
            return f"Displayed code: {kwargs.get('title', 'Code')}"

        if msg_type == "progress":
            await self.bridge.send_progress(
                message=kwargs["message"],
                percent=kwargs.get("percent"),
                steps=kwargs.get("steps"),
            )
            return f"Displayed progress: {kwargs['message']}"

        if msg_type == "alert":
            await self.bridge.send_alert(
                message=kwargs["message"],
                severity=kwargs.get("severity", "info"),
                title=kwargs.get("title"),
            )
            return f"Displayed alert: {kwargs['message']}"

        return f"Unknown display type: {msg_type}"
