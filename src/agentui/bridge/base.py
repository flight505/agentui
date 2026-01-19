"""
Base bridge interface for UI communication.

This module defines the abstract interface that all UI bridges must implement.
Bridges handle communication between the Python agent and the UI layer
(either a Go TUI subprocess or a Rich CLI fallback).

The BaseBridge interface defines methods for:
- Sending UI primitives (text, tables, forms, etc.)
- Requesting user input (forms, confirmations, selections)
- Managing bridge lifecycle (start, stop, events)
"""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Literal

from agentui.protocol import Message


class BaseBridge(ABC):
    """
    Abstract base class for UI bridges.

    All UI bridges (TUIBridge, CLIBridge) must implement this interface.
    The bridge handles bidirectional communication between the agent and UI,
    supporting both fire-and-forget messages and request/response patterns.

    Methods fall into three categories:
    1. Lifecycle: start(), stop(), is_running, events()
    2. Non-blocking sends: send_text(), send_table(), send_alert(), etc.
    3. Blocking requests: request_form(), request_confirm(), request_select()
    """

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """
        Check if the bridge is currently running.

        Returns:
            True if bridge is active, False otherwise
        """
        pass

    @abstractmethod
    async def start(self) -> None:
        """
        Start the bridge and establish connection.

        For TUIBridge: launches subprocess and begins reading messages
        For CLIBridge: initializes Rich console

        Raises:
            ConnectionError: If bridge cannot be started
        """
        pass

    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the bridge and clean up resources.

        Gracefully shuts down the UI and closes connections.
        """
        pass

    @abstractmethod
    def events(self) -> AsyncIterator[Message]:
        """
        Stream UI events from the user.

        Yields protocol messages representing user actions (input, clicks, etc.)

        Yields:
            Message objects from the UI
        """
        pass

    @abstractmethod
    async def send_text(self, content: str, done: bool = False) -> None:
        """
        Send streaming text content.

        Args:
            content: Text to display
            done: Whether this is the final chunk
        """
        pass

    @abstractmethod
    async def send_markdown(self, content: str, title: str | None = None) -> None:
        """
        Send rendered markdown content.

        Args:
            content: Markdown text
            title: Optional title
        """
        pass

    @abstractmethod
    async def send_progress(
        self,
        message: str,
        percent: float | None = None,
        steps: list[dict] | None = None,
    ) -> None:
        """
        Send progress indicator update.

        Args:
            message: Progress message
            percent: Optional percentage (0-100)
            steps: Optional list of step dictionaries
        """
        pass

    @abstractmethod
    async def request_form(
        self,
        fields: list[dict],
        title: str | None = None,
        description: str | None = None,
    ) -> dict | None:
        """
        Show a form and block until user submits.

        Args:
            fields: List of field dictionaries
            title: Optional form title
            description: Optional form description

        Returns:
            Dictionary mapping field names to values, or None if cancelled
        """
        pass

    @abstractmethod
    async def send_table(
        self,
        columns: list[str],
        rows: list[list[str]],
        title: str | None = None,
        footer: str | None = None,
    ) -> None:
        """
        Send a data table.

        Args:
            columns: Column headers
            rows: List of row lists
            title: Optional table title
            footer: Optional footer text
        """
        pass

    @abstractmethod
    async def send_code(
        self,
        code: str,
        language: str = "text",
        title: str | None = None,
    ) -> None:
        """
        Send a syntax-highlighted code block.

        Args:
            code: Source code
            language: Language for syntax highlighting
            title: Optional title/filename
        """
        pass

    @abstractmethod
    async def request_confirm(
        self,
        message: str,
        title: str | None = None,
        destructive: bool = False,
    ) -> bool:
        """
        Show confirmation dialog and block until user responds.

        Args:
            message: Confirmation message
            title: Optional dialog title
            destructive: If True, styles as dangerous action

        Returns:
            True if confirmed, False if cancelled
        """
        pass

    @abstractmethod
    async def request_select(
        self,
        label: str,
        options: list[str],
        default: str | None = None,
    ) -> str | None:
        """
        Show selection menu and block until user chooses.

        Args:
            label: Selection prompt
            options: List of choices
            default: Default selection

        Returns:
            Selected option string, or None if cancelled
        """
        pass

    @abstractmethod
    async def send_alert(
        self,
        message: str,
        severity: Literal["info", "success", "warning", "error"] = "info",
        title: str | None = None,
    ) -> None:
        """
        Show a non-blocking alert notification.

        Args:
            message: Alert message
            severity: Alert level
            title: Optional alert title
        """
        pass

    @abstractmethod
    async def send_spinner(self, message: str) -> None:
        """
        Show a loading spinner.

        Args:
            message: Loading message
        """
        pass

    @abstractmethod
    async def send_status(
        self,
        message: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        """
        Update the status bar.

        Args:
            message: Status message
            input_tokens: Optional input token count
            output_tokens: Optional output token count
        """
        pass

    @abstractmethod
    async def send_clear(self, scope: str = "chat") -> None:
        """
        Clear part of the UI.

        Args:
            scope: UI scope to clear (e.g., "chat", "all")
        """
        pass

    @abstractmethod
    async def send_done(self, summary: str | None = None) -> None:
        """
        Signal that agent processing is complete.

        Args:
            summary: Optional completion summary
        """
        pass
