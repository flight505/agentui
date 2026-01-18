"""
Progressive UI Streaming - Vercel AI SDK pattern for AgentUI.

Enables tools to yield progressive updates:
- Phase 1: Loading indicator
- Phase 2: Partial results
- Phase 3: Final component

Inspired by Vercel AI SDK's streamUI with async generators.
"""

import uuid
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agentui.bridge import CLIBridge, TUIBridge


class UIStream:
    """
    Progressive UI streaming for multi-phase rendering.

    Usage:
        @app.tool("analyze_code")
        async def analyze_code(file_path: str):
            stream = UIStream(bridge)

            # Phase 1: Loading
            await stream.send_progress("Reading file...", 0)

            # Phase 2: Partial results
            summary = await get_summary()
            await stream.send_table(["Issue"], [[s] for s in summary])

            # Phase 3: Final
            full = await analyze_full()
            return stream.finalize_table(["Line", "Issue"], full)

    Pattern:
        1. Create UIStream instance with bridge
        2. Use send_* methods to push progressive updates
        3. Return finalize_* method to create final UI primitive
        4. Framework handles UPDATE messages to TUI
    """

    def __init__(self, bridge: "TUIBridge | CLIBridge | None" = None):
        """
        Initialize UIStream.

        Args:
            bridge: TUI/CLI bridge for sending messages
        """
        self.bridge = bridge
        self.component_id = str(uuid.uuid4())
        self._current_type: str | None = None

    async def send_progress(
        self,
        message: str,
        percent: float | None = None,
        steps: list[dict] | None = None,
    ) -> None:
        """
        Send/update progress indicator.

        Args:
            message: Progress message
            percent: Percentage (0-100)
            steps: Multi-step progress
        """
        if not self.bridge:
            return

        from agentui.bridge import BridgeError
        from agentui.protocol import MessageType, update_payload

        try:
            if self._current_type:
                # Update existing component
                await self.bridge.send_message(
                    MessageType.UPDATE,
                    update_payload(
                        self.component_id,
                        message=message,
                        percent=percent,
                        steps=steps,
                    ),
                )
            else:
                # Create new progress component
                await self.bridge.send_progress(
                    message=message,
                    percent=percent,
                    steps=steps,
                )
                self._current_type = "progress"
        except BridgeError:
            pass  # Gracefully ignore bridge errors

    async def send_table(
        self,
        columns: list[str],
        rows: list[list[str]],
        title: str | None = None,
        footer: str | None = None,
    ) -> None:
        """
        Send/update table component.

        Args:
            columns: Column headers
            rows: Table data
            title: Optional title
            footer: Optional footer
        """
        if not self.bridge:
            return

        from agentui.bridge import BridgeError
        from agentui.protocol import MessageType, update_payload

        try:
            if self._current_type:
                # Update existing component
                await self.bridge.send_message(
                    MessageType.UPDATE,
                    update_payload(
                        self.component_id,
                        columns=columns,
                        rows=rows,
                        title=title,
                        footer=footer,
                    ),
                )
            else:
                # Create new table component
                await self.bridge.send_table(
                    columns=columns,
                    rows=rows,
                    title=title,
                    footer=footer,
                )
                self._current_type = "table"
        except BridgeError:
            pass

    async def send_code(
        self,
        code: str,
        language: str = "text",
        title: str | None = None,
    ) -> None:
        """
        Send/update code component.

        Args:
            code: Source code
            language: Programming language
            title: Optional title
        """
        if not self.bridge:
            return

        from agentui.bridge import BridgeError
        from agentui.protocol import MessageType, update_payload

        try:
            if self._current_type:
                # Update existing component
                await self.bridge.send_message(
                    MessageType.UPDATE,
                    update_payload(
                        self.component_id,
                        code=code,
                        language=language,
                        title=title,
                    ),
                )
            else:
                # Create new code component
                await self.bridge.send_code(
                    code=code,
                    language=language,
                    title=title,
                )
                self._current_type = "code"
        except BridgeError:
            pass

    async def send_alert(
        self,
        message: str,
        severity: str = "info",
        title: str | None = None,
    ) -> None:
        """
        Send/update alert component.

        Args:
            message: Alert message
            severity: Alert severity (info, success, warning, error)
            title: Optional title
        """
        if not self.bridge:
            return

        from agentui.bridge import BridgeError
        from agentui.protocol import MessageType, update_payload

        try:
            if self._current_type:
                # Update existing component
                await self.bridge.send_message(
                    MessageType.UPDATE,
                    update_payload(
                        self.component_id,
                        message=message,
                        severity=severity,
                        title=title,
                    ),
                )
            else:
                # Create new alert component
                await self.bridge.send_alert(
                    message=message,
                    severity=severity,
                    title=title,
                )
                self._current_type = "alert"
        except BridgeError:
            pass

    # --- Finalize methods (return UI primitives) ---

    def finalize_table(
        self,
        columns: list[str],
        rows: list[list[str]],
        title: str | None = None,
        footer: str | None = None,
    ):
        """
        Finalize as table primitive.

        Returns:
            UITable instance
        """
        from agentui.primitives import UITable
        return UITable(
            columns=columns,
            rows=rows,
            title=title,
            footer=footer,
        )

    def finalize_code(
        self,
        code: str,
        language: str = "text",
        title: str | None = None,
    ):
        """
        Finalize as code primitive.

        Returns:
            UICode instance
        """
        from agentui.primitives import UICode
        return UICode(
            code=code,
            language=language,
            title=title,
        )

    def finalize_progress(
        self,
        message: str,
        percent: float | None = None,
        steps: list[dict] | None = None,
    ):
        """
        Finalize as progress primitive.

        Returns:
            UIProgress instance
        """
        from agentui.primitives import UIProgress
        return UIProgress(
            message=message,
            percent=percent,
            steps=steps,
        )

    def finalize_alert(
        self,
        message: str,
        severity: str = "info",
        title: str | None = None,
    ):
        """
        Finalize as alert primitive.

        Returns:
            UIAlert instance
        """
        from agentui.primitives import UIAlert
        return UIAlert(
            message=message,
            severity=severity,
            title=title,
        )


def streaming_tool(func):
    """
    Decorator to mark a tool as supporting progressive streaming.

    Usage:
        @app.tool("analyze", ...)
        @streaming_tool
        async def analyze(file_path: str):
            stream = UIStream()
            await stream.send_progress("Analyzing...", 0)
            # ... progressive updates ...
            return stream.finalize_table([...], [...])

    The decorator sets a flag that can be checked by the framework.
    """
    func._is_streaming = True
    return func
