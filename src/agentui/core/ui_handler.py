"""
UI result handling.

Manages processing of UI primitive results from tools.
"""

import logging
from collections.abc import Callable
from typing import Any

from agentui.bridge import BridgeError
from agentui.primitives import (
    UICode,
    UIConfirm,
    UIForm,
    UIProgress,
    UISelect,
    UITable,
)

logger = logging.getLogger(__name__)


class UIHandler:
    """Handles UI primitive results from tools."""

    def __init__(self, bridge_getter: Callable[[], Any] | None = None):
        """Initialize the UI handler.

        Args:
            bridge_getter: Optional callable that returns the current bridge
        """
        self._bridge_getter = bridge_getter

    @property
    def bridge(self) -> Any:
        """Get the current bridge."""
        return self._bridge_getter() if self._bridge_getter else None

    async def handle_ui_result(self, result: Any) -> Any:
        """Handle UI primitive results from tools."""
        if not self.bridge:
            return result

        try:
            if isinstance(result, UIForm):
                return await self.bridge.request_form(
                    fields=[f.to_dict() for f in result.fields],
                    title=result.title,
                    description=result.description,
                )

            elif isinstance(result, UIConfirm):
                return await self.bridge.request_confirm(
                    result.message,
                    title=result.title,
                    destructive=result.destructive,
                )

            elif isinstance(result, UISelect):
                return await self.bridge.request_select(
                    result.label,
                    result.options,
                    result.default,
                )

            elif isinstance(result, UIProgress):
                await self.bridge.send_progress(
                    result.message,
                    result.percent,
                    [s.to_dict() for s in result.steps] if result.steps else None,
                )
                return None

            elif isinstance(result, UITable):
                await self.bridge.send_table(
                    result.columns,
                    result.rows,
                    result.title,
                    result.footer,
                )
                return None

            elif isinstance(result, UICode):
                await self.bridge.send_code(
                    result.code,
                    result.language,
                    result.title,
                )
                return None

        except BridgeError as e:
            logger.error(f"Failed to handle UI result: {e}")

        return result
