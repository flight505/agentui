"""CLI Bridge using Rich for fallback rendering."""

import logging
from collections.abc import AsyncIterator
from typing import Literal

from agentui.bridge.base import BaseBridge
from agentui.bridge.tui_bridge import TUIConfig
from agentui.protocol import Message

logger = logging.getLogger(__name__)


class CLIBridge(BaseBridge):
    """
    Fallback bridge that uses Rich for CLI rendering.

    Used when the Go TUI binary is not available.
    """

    def __init__(self, config: TUIConfig | None = None):
        self.config = config or TUIConfig()
        self._running = False
        self._console = None

        try:
            from rich.console import Console
            self._console = Console()
        except ImportError:
            pass

    @property
    def is_running(self) -> bool:
        return self._running

    async def start(self) -> None:
        """Start CLI mode."""
        self._running = True
        if self._console:
            self._console.print()
            self._console.print(
                f"[bold blue]{self.config.app_name}[/bold blue] - {self.config.tagline}"
            )
            self._console.print()

    async def stop(self) -> None:
        """Stop CLI mode."""
        self._running = False
        if self._console:
            self._console.print("\n[dim]Goodbye![/dim]")

    async def send_text(self, content: str, done: bool = False) -> None:
        """Print text."""
        if self._console:
            self._console.print(content, end="" if not done else "\n")
        else:
            print(content, end="" if not done else "\n")

    async def send_markdown(self, content: str, title: str | None = None) -> None:
        """Print markdown."""
        if self._console:
            from rich.markdown import Markdown
            if title:
                self._console.print(f"\n[bold]{title}[/bold]")
            self._console.print(Markdown(content))
        else:
            if title:
                print(f"\n=== {title} ===")
            print(content)

    async def send_progress(
        self,
        message: str,
        percent: float | None = None,
        steps: list[dict] | None = None,
    ) -> None:
        """Show progress."""
        if self._console:
            if percent is not None:
                self._console.print(f"[dim]{message}[/dim] [{percent:.0f}%]")
            else:
                self._console.print(f"[dim]⟳ {message}[/dim]")

            if steps:
                for step in steps:
                    status_icons = {
                        "complete": "[green]✓[/green]",
                        "running": "[blue]●[/blue]",
                        "error": "[red]✗[/red]",
                        "pending": "[dim]○[/dim]",
                    }
                    icon = status_icons.get(step.get("status", "pending"), "○")
                    self._console.print(f"  {icon} {step.get('label', '')}")

    async def request_form(
        self,
        fields: list[dict],
        title: str | None = None,
        description: str | None = None,
    ) -> dict | None:
        """Collect form input via CLI."""
        if not self._console:
            return {}

        from rich.prompt import Confirm, Prompt

        if title:
            self._console.print(f"\n[bold]{title}[/bold]")
        if description:
            self._console.print(f"[dim]{description}[/dim]\n")

        from typing import Any
        values: dict[str, Any] = {}
        for field in fields:
            name = field.get("name", "")
            label = field.get("label", name)
            field_type = field.get("type", "text")
            default = field.get("default", "")

            if field_type == "checkbox":
                # Confirm.ask returns bool, not bool | str
                values[name] = bool(Confirm.ask(label, default=bool(default)))
            elif field_type == "select":
                options = field.get("options", [])
                if options:
                    self._console.print(f"[bold]{label}[/bold]")
                    for i, opt in enumerate(options, 1):
                        self._console.print(f"  {i}. {opt}")
                    choice = Prompt.ask("Enter number", default="1")
                    try:
                        idx = int(choice) - 1
                        values[name] = options[idx] if 0 <= idx < len(options) else options[0]
                    except ValueError:
                        values[name] = options[0]
            else:
                # Text input always returns a string
                text_value = Prompt.ask(label, default=str(default) if default else "")
                values[name] = str(text_value)

        return values

    async def request_confirm(
        self,
        message: str,
        title: str | None = None,
        destructive: bool = False,
    ) -> bool:
        """Get confirmation via CLI."""
        if self._console:
            from rich.prompt import Confirm
            style = "[yellow]" if destructive else ""
            return Confirm.ask(f"{style}{message}")
        else:
            response = input(f"{message} [y/N]: ").strip().lower()
            return response in ("y", "yes")

    async def request_select(
        self,
        label: str,
        options: list[str],
        default: str | None = None,
    ) -> str | None:
        """Get selection via CLI."""
        if self._console:
            self._console.print(f"\n[bold]{label}[/bold]")
            for i, opt in enumerate(options, 1):
                marker = "→ " if opt == default else "  "
                self._console.print(f"{marker}{i}. {opt}")

            from rich.prompt import Prompt
            choice = Prompt.ask("Enter number", default="1")
            try:
                idx = int(choice) - 1
                return options[idx] if 0 <= idx < len(options) else None
            except ValueError:
                return default
        else:
            print(f"\n{label}")
            for i, opt in enumerate(options, 1):
                print(f"  {i}. {opt}")
            choice = input("Enter number: ").strip()
            try:
                idx = int(choice) - 1
                return options[idx] if 0 <= idx < len(options) else None
            except ValueError:
                return default

    async def send_table(
        self,
        columns: list[str],
        rows: list[list[str]],
        title: str | None = None,
        footer: str | None = None,
    ) -> None:
        """Display table."""
        if self._console:
            from rich.table import Table
            table = Table(title=title)
            for col in columns:
                table.add_column(col)
            for row in rows:
                table.add_row(*row)
            self._console.print(table)
            if footer:
                self._console.print(f"[dim]{footer}[/dim]")

    async def send_code(
        self,
        code: str,
        language: str = "text",
        title: str | None = None,
    ) -> None:
        """Display code."""
        if self._console:
            from rich.panel import Panel
            from rich.syntax import Syntax
            syntax = Syntax(code, language, theme="monokai", line_numbers=True)
            self._console.print(Panel(syntax, title=title))

    async def send_alert(
        self,
        message: str,
        severity: Literal["info", "success", "warning", "error"] = "info",
        title: str | None = None,
    ) -> None:
        """Show alert."""
        if self._console:
            styles = {
                "info": "blue",
                "success": "green",
                "warning": "yellow",
                "error": "red"
            }
            style = styles.get(severity, "blue")
            if title:
                self._console.print(f"[{style} bold]{title}[/{style} bold]")
            self._console.print(f"[{style}]{message}[/{style}]")

    async def send_spinner(self, message: str) -> None:
        if self._console:
            self._console.print(f"[dim]⟳ {message}[/dim]")

    async def send_status(
        self,
        message: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        pass  # No status bar in CLI mode

    async def send_clear(self, scope: str = "chat") -> None:
        if self._console:
            self._console.clear()

    async def send_done(self, summary: str | None = None) -> None:
        if summary and self._console:
            self._console.print(f"\n[green]✓ {summary}[/green]")

    async def events(self) -> AsyncIterator[Message]:
        """Interactive input loop."""
        while self._running:
            try:
                if self._console:
                    from rich.prompt import Prompt
                    user_input = Prompt.ask("\n[bold]You[/bold]")
                else:
                    user_input = input("\nYou: ")

                if user_input.lower() in ("quit", "exit", "q"):
                    yield Message(type="quit", payload={})
                    break

                yield Message(type="input", payload={"content": user_input})

            except (KeyboardInterrupt, EOFError):
                yield Message(type="quit", payload={})
                break
            except Exception as e:
                logger.error(f"Input error: {e}")
                continue
