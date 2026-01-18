"""
UI Renderers - TUI, CLI, and base classes.
"""

from abc import ABC, abstractmethod
from typing import Any

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

    def __init__(self):
        try:
            from rich.console import Console
        except ImportError:
            raise ImportError("rich package required: uv add rich")

        self.console = Console()
        self._text_buffer = ""

    async def render(self, primitive: UIPrimitive) -> Any:
        """Render a UI primitive."""
        from rich.markdown import Markdown
        from rich.panel import Panel
        from rich.prompt import Confirm, Prompt
        from rich.syntax import Syntax
        from rich.table import Table

        match primitive:
            case UIMarkdown():
                md = Markdown(primitive.content)
                if primitive.title:
                    self.console.print(Panel(md, title=primitive.title))
                else:
                    self.console.print(md)
                return None

            case UITable():
                table = Table(title=primitive.title)
                for col in primitive.columns:
                    if isinstance(col, str):
                        table.add_column(col)
                    else:
                        table.add_column(col.label, justify=col.align)
                for row in primitive.rows:
                    if isinstance(row, dict):
                        values = [str(row.get(c.key if hasattr(c, 'key') else c, ""))
                                  for c in primitive.columns]
                    else:
                        values = [str(v) for v in row]
                    table.add_row(*values)
                if primitive.footer:
                    table.caption = primitive.footer
                self.console.print(table)
                return None

            case UICode():
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

            case UIConfirm():
                return Confirm.ask(
                    primitive.message,
                    default=primitive.default,
                )

            case UIInput():
                return Prompt.ask(
                    primitive.label,
                    default=primitive.default or "",
                    password=primitive.password,
                )

            case UISelect():
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

            case UIForm():
                results = {}
                if primitive.title:
                    self.console.print(f"\n[bold]{primitive.title}[/bold]")
                if primitive.description:
                    self.console.print(f"[dim]{primitive.description}[/dim]\n")

                for field in primitive.fields:
                    if field.field_type == "checkbox":
                        results[field.name] = Confirm.ask(
                            field.label, default=field.default or False
                        )
                    elif field.field_type == "select" and field.options:
                        self.console.print(f"[bold]{field.label}[/bold]")
                        for i, opt in enumerate(field.options, 1):
                            self.console.print(f"  {i}. {opt}")
                        while True:
                            choice = Prompt.ask("Enter number")
                            try:
                                idx = int(choice) - 1
                                if 0 <= idx < len(field.options):
                                    results[field.name] = field.options[idx]
                                    break
                            except ValueError:
                                pass
                            self.console.print("[red]Invalid choice[/red]")
                    else:
                        results[field.name] = Prompt.ask(
                            field.label,
                            default=str(field.default) if field.default else "",
                            password=field.field_type == "password",
                        )
                return results

            case UIProgress():
                # For CLI, just print the message (progress is typically non-blocking)
                self.console.print(f"[dim]{primitive.message}[/dim]")
                return None

            case UIAlert():
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

            case UISpinner():
                self.console.print(f"[dim]⟳ {primitive.message}[/dim]")
                return None

            case _:
                self.console.print(
                    f"[dim]Unsupported UI primitive: {type(primitive).__name__}[/dim]"
                )
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
