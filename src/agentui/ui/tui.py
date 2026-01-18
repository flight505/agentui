"""
TUI Renderer using Textual - Charm-inspired beautiful terminal UI.
"""

import asyncio
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
    UITable,
)
from agentui.ui import Renderer

# Charm-inspired CSS theme
CHARM_CSS = """
/* Charm-inspired styling - Catppuccin Mocha palette */
$primary: #cba6f7;
$secondary: #f5c2e7;
$surface: #1e1e2e;
$surface-light: #313244;
$text: #cdd6f4;
$subtext: #a6adc8;
$success: #a6e3a1;
$warning: #f9e2af;
$error: #f38ba8;
$info: #89b4fa;

Screen {
    background: $surface;
}

/* Header */
#header {
    dock: top;
    height: 3;
    background: $surface-light;
    color: $primary;
    text-align: center;
    padding: 1;
}

#header-title {
    text-style: bold;
}

/* Main content area */
#main {
    height: 1fr;
    padding: 1 2;
}

/* Chat messages */
.message-container {
    margin: 1 0;
    padding: 1 2;
}

.message-user {
    background: $surface-light;
    border: round $primary;
}

.message-assistant {
    background: $surface;
    border: round $subtext;
}

/* Input area */
#input-area {
    dock: bottom;
    height: auto;
    padding: 1 2;
    background: $surface-light;
}

#prompt-input {
    width: 100%;
    border: round $primary;
}

#prompt-input:focus {
    border: round $secondary;
}

/* Forms */
.form-container {
    background: $surface-light;
    border: round $primary;
    padding: 2;
    margin: 1;
    width: 80%;
}

.form-title {
    text-style: bold;
    color: $primary;
    margin-bottom: 1;
}

.form-field {
    margin: 1 0;
}

.form-label {
    color: $text;
    margin-bottom: 0;
}

.form-input {
    width: 100%;
    border: round $subtext;
}

.form-input:focus {
    border: round $primary;
}

/* Buttons */
Button {
    margin: 1;
}

Button.primary {
    background: $primary;
    color: $surface;
}

Button.secondary {
    background: $surface-light;
    color: $text;
    border: round $subtext;
}

Button.danger {
    background: $error;
    color: $surface;
}

/* Tables */
DataTable {
    background: $surface-light;
    border: round $subtext;
}

DataTable > .datatable--header {
    background: $surface;
    color: $primary;
    text-style: bold;
}

DataTable > .datatable--cursor {
    background: $primary;
    color: $surface;
}

/* Progress */
.progress-container {
    padding: 1 2;
    background: $surface-light;
    border: round $info;
    margin: 1;
}

ProgressBar > .bar--bar {
    color: $primary;
}

ProgressBar > .bar--complete {
    color: $success;
}

/* Alerts */
.alert {
    padding: 1 2;
    margin: 1;
    border: round $info;
}

.alert-info {
    border: round $info;
    background: $surface-light;
}

.alert-success {
    border: round $success;
    background: $surface-light;
}

.alert-warning {
    border: round $warning;
    background: $surface-light;
}

.alert-error {
    border: round $error;
    background: $surface-light;
}

/* Code blocks */
.code-container {
    background: $surface;
    border: round $subtext;
    padding: 1;
    margin: 1;
}

/* Confirm dialog */
.confirm-dialog {
    background: $surface-light;
    border: round $warning;
    padding: 2;
    width: 60;
    height: auto;
}

/* Status bar */
#status-bar {
    dock: bottom;
    height: 1;
    background: $surface-light;
    color: $subtext;
    padding: 0 2;
}

/* Spinner */
.spinner {
    color: $primary;
}

/* Footer */
#footer {
    dock: bottom;
    height: 1;
    background: $surface-light;
    color: $subtext;
}
"""


class TUIRenderer(Renderer):
    """
    TUI renderer using Textual for Charm-like beautiful terminal UI.
    
    This renderer creates rich, interactive terminal interfaces with
    forms, progress indicators, tables, and more.
    """

    def __init__(self, app: "AgentTUIApp | None" = None):
        self.app = app
        self._text_buffer = ""
        self._pending_response: asyncio.Future | None = None

    async def render(self, primitive: UIPrimitive) -> Any:
        """Render a UI primitive."""
        if self.app is None:
            # Fallback to CLI renderer if no TUI app
            from agentui.ui import CLIRenderer
            cli = CLIRenderer()
            return await cli.render(primitive)

        match primitive:
            case UIForm():
                return await self._render_form(primitive)
            case UIConfirm():
                return await self._render_confirm(primitive)
            case UIInput():
                return await self._render_input(primitive)
            case UISelect():
                return await self._render_select(primitive)
            case UITable():
                await self._render_table(primitive)
                return None
            case UIMarkdown():
                await self._render_markdown(primitive)
                return None
            case UICode():
                await self._render_code(primitive)
                return None
            case UIProgress():
                await self._render_progress(primitive)
                return None
            case UIAlert():
                await self._render_alert(primitive)
                return None
            case _:
                # Fallback: render as text
                await self.stream_text(f"[{type(primitive).__name__}]\n")
                return None

    async def _render_form(self, form: UIForm) -> dict[str, Any]:
        """Render an interactive form and wait for submission."""
        # This would mount a form widget and wait for response
        # For now, return a placeholder
        self._pending_response = asyncio.get_event_loop().create_future()

        # Tell app to show form
        if self.app:
            self.app.show_form(form, self._pending_response)

        # Wait for user to submit
        result = await self._pending_response
        self._pending_response = None
        return result

    async def _render_confirm(self, confirm: UIConfirm) -> bool:
        """Render a confirmation dialog."""
        self._pending_response = asyncio.get_event_loop().create_future()

        if self.app:
            self.app.show_confirm(confirm, self._pending_response)

        result = await self._pending_response
        self._pending_response = None
        return result

    async def _render_input(self, input_prim: UIInput) -> str:
        """Render a text input."""
        self._pending_response = asyncio.get_event_loop().create_future()

        if self.app:
            self.app.show_input(input_prim, self._pending_response)

        result = await self._pending_response
        self._pending_response = None
        return result

    async def _render_select(self, select: UISelect) -> str:
        """Render a selection."""
        self._pending_response = asyncio.get_event_loop().create_future()

        if self.app:
            self.app.show_select(select, self._pending_response)

        result = await self._pending_response
        self._pending_response = None
        return result

    async def _render_table(self, table: UITable) -> None:
        """Render a data table."""
        if self.app:
            self.app.show_table(table)

    async def _render_markdown(self, md: UIMarkdown) -> None:
        """Render markdown content."""
        if self.app:
            self.app.show_markdown(md)

    async def _render_code(self, code: UICode) -> None:
        """Render a code block."""
        if self.app:
            self.app.show_code(code)

    async def _render_progress(self, progress: UIProgress) -> None:
        """Update progress indicator."""
        if self.app:
            self.app.update_progress(progress)

    async def _render_alert(self, alert: UIAlert) -> None:
        """Show an alert."""
        if self.app:
            self.app.show_alert(alert)

    async def stream_text(self, text: str) -> None:
        """Stream text to the TUI."""
        self._text_buffer += text
        if self.app:
            self.app.append_text(text)

    async def show_tool_use(self, tool_name: str, args: dict) -> None:
        """Show tool being used."""
        if self.app:
            self.app.show_tool_use(tool_name, args)

    async def confirm_tool(self, tool_name: str, args: dict) -> bool:
        """Ask user to confirm tool."""
        confirm = UIConfirm(
            message=f"Allow tool '{tool_name}'?",
            title="Tool Permission",
        )
        return await self._render_confirm(confirm)

    async def show_error(self, message: str) -> None:
        """Show error message."""
        alert = UIAlert(
            message=message,
            severity="error",
            title="Error",
        )
        await self._render_alert(alert)

    async def flush(self) -> None:
        """Flush text buffer."""
        if self.app and self._text_buffer:
            self.app.flush_text()
        self._text_buffer = ""


def create_tui_app(title: str = "AgentUI", css: str | None = None):
    """
    Create a Textual TUI application.
    
    This is a factory function that creates the app with proper imports.
    """
    try:
        from textual.app import App, ComposeResult
        from textual.containers import Container, Horizontal, ScrollableContainer, Vertical
        from textual.screen import ModalScreen
        from textual.widgets import (
            Button,
            DataTable,
            Footer,
            Header,
            Input,
            Label,
            Markdown,
            ProgressBar,
            Static,
        )
    except ImportError:
        raise ImportError("textual package required: uv add textual")

    class AgentTUIApp(App):
        """Main TUI application for AgentUI."""

        CSS = css or CHARM_CSS
        TITLE = title

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.renderer = TUIRenderer(self)
            self._message_container = None
            self._current_text = ""

        def compose(self) -> ComposeResult:
            yield Header()
            yield ScrollableContainer(id="main")
            yield Input(placeholder="Enter your message...", id="prompt-input")
            yield Footer()

        def on_mount(self) -> None:
            """Set up the app on mount."""
            self._message_container = self.query_one("#main")

        def append_text(self, text: str) -> None:
            """Append streaming text to current message."""
            self._current_text += text
            # Update the display (simplified)
            if self._message_container:
                # In real implementation, update a specific widget
                pass

        def flush_text(self) -> None:
            """Flush accumulated text."""
            if self._current_text and self._message_container:
                widget = Static(self._current_text, classes="message-assistant")
                self._message_container.mount(widget)
            self._current_text = ""

        def show_form(self, form: UIForm, future: asyncio.Future) -> None:
            """Show a form dialog."""
            # In real implementation, push a form screen
            # For now, resolve with empty dict
            future.set_result({})

        def show_confirm(self, confirm: UIConfirm, future: asyncio.Future) -> None:
            """Show a confirm dialog."""
            # In real implementation, push a confirm screen
            future.set_result(True)

        def show_input(self, input_prim: UIInput, future: asyncio.Future) -> None:
            """Show an input dialog."""
            future.set_result("")

        def show_select(self, select: UISelect, future: asyncio.Future) -> None:
            """Show a select dialog."""
            future.set_result(select.options[0] if select.options else "")

        def show_table(self, table: UITable) -> None:
            """Show a data table."""
            if self._message_container:
                dt = DataTable()
                for col in table.columns:
                    label = col if isinstance(col, str) else col.label
                    dt.add_column(label)
                for row in table.rows:
                    values = row if isinstance(row, list) else list(row.values())
                    dt.add_row(*[str(v) for v in values])
                self._message_container.mount(dt)

        def show_markdown(self, md: UIMarkdown) -> None:
            """Show markdown content."""
            if self._message_container:
                widget = Markdown(md.content)
                self._message_container.mount(widget)

        def show_code(self, code: UICode) -> None:
            """Show a code block."""
            if self._message_container:
                # Use Static with syntax highlighting via Rich
                from rich.syntax import Syntax
                syntax = Syntax(code.code, code.language, line_numbers=code.line_numbers)
                widget = Static(syntax)
                self._message_container.mount(widget)

        def update_progress(self, progress: UIProgress) -> None:
            """Update progress indicator."""
            # In real implementation, update progress bar widget
            pass

        def show_alert(self, alert: UIAlert) -> None:
            """Show an alert."""
            if self._message_container:
                widget = Static(
                    f"[{alert.severity.upper()}] {alert.message}",
                    classes=f"alert alert-{alert.severity}"
                )
                self._message_container.mount(widget)

        def show_tool_use(self, tool_name: str, args: dict) -> None:
            """Show tool being used."""
            if self._message_container:
                widget = Static(f"🔧 Using: {tool_name}", classes="tool-use")
                self._message_container.mount(widget)

    return AgentTUIApp()
