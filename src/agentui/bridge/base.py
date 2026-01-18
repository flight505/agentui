"""Base bridge interface for UI communication."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Literal

from agentui.protocol import Message


class BaseBridge(ABC):
    """Abstract base class for UI bridges."""

    @property
    @abstractmethod
    def is_running(self) -> bool:
        """Check if the bridge is running."""
        pass

    @abstractmethod
    async def start(self) -> None:
        """Start the bridge."""
        pass

    @abstractmethod
    async def stop(self) -> None:
        """Stop the bridge."""
        pass

    @abstractmethod
    async def events(self) -> AsyncIterator[Message]:
        """Stream UI events."""
        pass

    @abstractmethod
    async def send_text(self, content: str, done: bool = False) -> None:
        """Send streaming text."""
        pass

    @abstractmethod
    async def send_markdown(self, content: str, title: str | None = None) -> None:
        """Send markdown content."""
        pass

    @abstractmethod
    async def send_progress(
        self,
        message: str,
        percent: float | None = None,
        steps: list[dict] | None = None,
    ) -> None:
        """Send progress update."""
        pass

    @abstractmethod
    async def request_form(
        self,
        fields: list[dict],
        title: str | None = None,
        description: str | None = None,
    ) -> dict | None:
        """Show a form and wait for response."""
        pass

    @abstractmethod
    async def send_table(
        self,
        columns: list[str | dict],
        rows: list[list[str]],
        title: str | None = None,
        footer: str | None = None,
    ) -> None:
        """Send a data table."""
        pass

    @abstractmethod
    async def send_code(
        self,
        code: str,
        language: str = "text",
        title: str | None = None,
    ) -> None:
        """Send a code block."""
        pass

    @abstractmethod
    async def request_confirm(
        self,
        message: str,
        title: str | None = None,
        destructive: bool = False,
    ) -> bool:
        """Show confirmation dialog and wait for response."""
        pass

    @abstractmethod
    async def request_select(
        self,
        label: str,
        options: list[str],
        default: str | None = None,
    ) -> str | None:
        """Show selection and wait for response."""
        pass

    @abstractmethod
    async def send_alert(
        self,
        message: str,
        severity: Literal["info", "success", "warning", "error"] = "info",
        title: str | None = None,
    ) -> None:
        """Show an alert notification."""
        pass

    @abstractmethod
    async def send_spinner(self, message: str) -> None:
        """Show a loading spinner."""
        pass

    @abstractmethod
    async def send_status(
        self,
        message: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        """Update the status bar."""
        pass

    @abstractmethod
    async def send_clear(self, scope: str = "chat") -> None:
        """Clear part of the UI."""
        pass

    @abstractmethod
    async def send_done(self, summary: str | None = None) -> None:
        """Signal completion."""
        pass
