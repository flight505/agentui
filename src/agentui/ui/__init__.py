"""
UI Renderers - TUI, CLI, and base classes.
"""

from abc import ABC, abstractmethod
from typing import Any, cast

from agentui.primitives import (
    UIAlert,
    UICode,
    UIConfirm,
    UIForm,
    UIInput,
    UIMarkdown,
    UIPrimitive,
    UIProgress,
    UISelect,
    UISpinner,
    UITable,
)


class Renderer(ABC):
    """Abstract base class for UI renderers."""

    @abstractmethod
    async def render(self, primitive: UIPrimitive) -> Any:
        """
        Render a UI primitive and return user response if interactive.

        Args:
            primitive: The UI primitive to render

        Returns:
            User response for interactive primitives, None otherwise
        """
        ...

    @abstractmethod
    async def stream_text(self, text: str) -> None:
        """Stream text output to the display."""
        ...

    @abstractmethod
    async def show_tool_use(self, tool_name: str, args: dict) -> None:
        """Show that a tool is being called."""
        ...

    @abstractmethod
    async def confirm_tool(self, tool_name: str, args: dict) -> bool:
        """Ask user to confirm tool execution."""
        ...

    @abstractmethod
    async def show_error(self, message: str) -> None:
        """Display an error message."""
        ...

    @abstractmethod
    async def flush(self) -> None:
        """Flush any buffered output."""
        ...


class CLIRenderer(Renderer):
    """
    CLI renderer using Rich for styled output.

    This is the fallback renderer for environments without full TUI support.
    """

    def __init__(self) -> None:
        try:
            from rich.console import Console
        except ImportError:
            raise ImportError("rich package required: uv add rich")

        self.console = Console()
        self._text_buffer = ""

    async def render(self, primitive: UIPrimitive) -> Any:
        """Render a UI primitive using type-specific handlers."""
        match primitive:
            case UIMarkdown():
                return self._render_markdown(primitive)
            case UITable():
                return self._render_table(primitive)
            case UICode():
                return self._render_code(primitive)
            case UIConfirm():
                return self._render_confirm(primitive)
            case UIInput():
                return self._render_input(primitive)
            case UISelect():
                return self._render_select(primitive)
            case UIForm():
                return self._render_form(primitive)
            case UIProgress():
                return self._render_progress(primitive)
            case UIAlert():
                return self._render_alert(primitive)
            case UISpinner():
                return self._render_spinner(primitive)
            case _:
                self.console.print(
                    f"[dim]Unsupported UI primitive: {type(primitive).__name__}[/dim]"
                )
                return None

    def _render_markdown(self, primitive: UIMarkdown) -> None:
        """Render markdown primitive."""
        from rich.markdown import Markdown
        from rich.panel import Panel

        md = Markdown(primitive.content)
        if primitive.title:
            self.console.print(Panel(md, title=primitive.title))
        else:
            self.console.print(md)
        return None

    def _render_table(self, primitive: UITable) -> None:
        """Render table primitive."""
        from rich.table import Table

        table = Table(title=primitive.title)
        for col in primitive.columns:
            if isinstance(col, str):
                table.add_column(col)
            else:
                table.add_column(col.label, justify=col.align)

        for row in primitive.rows:
            if isinstance(row, dict):
                values = [
                    str(row.get(getattr(c, "key", c), ""))
                    for c in primitive.columns
                ]
            else:
                values = [str(v) for v in row]
            table.add_row(*values)

        if primitive.footer:
            table.caption = primitive.footer
        self.console.print(table)
        return None

    def _render_code(self, primitive: UICode) -> None:
        """Render code primitive."""
        from rich.panel import Panel
        from rich.syntax import Syntax

        syntax = Syntax(
            primitive.code,
            primitive.language,
            line_numbers=primitive.line_numbers,
            theme="monokai",
        )
        if primitive.title:
            self.console.print(Panel(syntax, title=primitive.title))
        else:
            self.console.print(syntax)
        return None

    def _render_confirm(self, primitive: UIConfirm) -> bool:
        """Render confirm primitive and return user response."""
        from rich.prompt import Confirm

        return Confirm.ask(primitive.message, default=True)

    def _render_input(self, primitive: UIInput) -> str:
        """Render input primitive and return user response."""
        from rich.prompt import Prompt

        return Prompt.ask(
            primitive.label,
            default=primitive.default or "",
            password=primitive.password,
        )

    def _render_select(self, primitive: UISelect) -> str:
        """Render select primitive and return user choice."""
        from rich.prompt import Prompt

        self.console.print(f"\n[bold]{primitive.label}[/bold]")
        for i, option in enumerate(primitive.options, 1):
            self.console.print(f"  {i}. {option}")

        while True:
            choice = Prompt.ask("Enter number")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(primitive.options):
                    return primitive.options[idx]
            except ValueError:
                pass
            self.console.print("[red]Invalid choice[/red]")

    def _render_form(self, primitive: UIForm) -> dict:
        """Render form primitive and return user responses."""
        from rich.prompt import Confirm, Prompt

        results = {}
        if primitive.title:
            self.console.print(f"\n[bold]{primitive.title}[/bold]")
        if primitive.description:
            self.console.print(f"[dim]{primitive.description}[/dim]\n")

        for field in primitive.fields:
            if field.type == "checkbox":
                results[field.name] = Confirm.ask(
                    field.label, default=field.default or False
                )
            elif field.type == "select" and field.options:
                results[field.name] = self._render_form_select_field(field)
            else:
                results[field.name] = Prompt.ask(
                    field.label,
                    default=str(field.default) if field.default else "",
                    password=field.type == "password",
                )
        return results

    def _render_form_select_field(self, field: Any) -> str:
        """Render a select field within a form and return choice."""
        from rich.prompt import Prompt

        self.console.print(f"[bold]{field.label}[/bold]")
        for i, opt in enumerate(field.options, 1):
            self.console.print(f"  {i}. {opt}")

        while True:
            choice = Prompt.ask("Enter number")
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(field.options):
                    return cast(str, field.options[idx])
            except ValueError:
                pass
            self.console.print("[red]Invalid choice[/red]")

    def _render_progress(self, primitive: UIProgress) -> None:
        """Render progress primitive."""
        self.console.print(f"[dim]{primitive.message}[/dim]")
        return None

    def _render_alert(self, primitive: UIAlert) -> None:
        """Render alert primitive."""
        from rich.panel import Panel

        style_map = {
            "info": "blue",
            "success": "green",
            "warning": "yellow",
            "error": "red",
        }
        style = style_map.get(primitive.severity, "blue")
        title = primitive.title or primitive.severity.upper()
        self.console.print(Panel(primitive.message, title=title, border_style=style))
        return None

    def _render_spinner(self, primitive: UISpinner) -> None:
        """Render spinner primitive."""
        self.console.print(f"[dim]⟳ {primitive.message}[/dim]")
        return None

    async def stream_text(self, text: str) -> None:
        """Stream text to console."""
        self.console.print(text, end="")
        self._text_buffer += text

    async def show_tool_use(self, tool_name: str, args: dict) -> None:
        """Show tool being called."""
        self.console.print(f"\n[dim]🔧 Using tool: {tool_name}[/dim]")

    async def confirm_tool(self, tool_name: str, args: dict) -> bool:
        """Confirm tool execution."""
        from rich.prompt import Confirm
        return Confirm.ask(f"Allow [bold]{tool_name}[/bold]?", default=True)

    async def show_error(self, message: str) -> None:
        """Show error message."""
        self.console.print(f"[red]Error: {message}[/red]")

    async def flush(self) -> None:
        """Flush output and add newline if needed."""
        if self._text_buffer and not self._text_buffer.endswith("\n"):
            self.console.print()
        self._text_buffer = ""
