"""
Component Tester - Test AgentUI components in isolation

Like Storybook for terminal UIs: render individual components,
capture ANSI output, and verify rendering without running full app.
"""

import subprocess
import json
from pathlib import Path
from typing import Union, Optional
from dataclasses import dataclass

from ..primitives import UICode, UITable, UIProgress, UIForm, UIConfirm


@dataclass
class RenderResult:
    """Result of rendering a UI component"""
    output: str  # Raw ANSI output
    exit_code: int
    stderr: str
    success: bool

    @property
    def plain_text(self) -> str:
        """Output with ANSI codes stripped"""
        import re
        ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
        return ansi_escape.sub('', self.output)

    def has_ansi_codes(self) -> bool:
        """Check if output contains ANSI escape sequences"""
        return '\x1b[' in self.output

    def find_color_code(self, ansi_code: str) -> bool:
        """Check if specific ANSI color code is present"""
        return ansi_code in self.output


class ComponentTester:
    """
    Test AgentUI components in isolation

    Similar to Storybook for web components: renders individual UI primitives
    without requiring full AgentUI app or LLM integration.

    Examples:
        >>> tester = ComponentTester(theme="charm-dark")
        >>>
        >>> # Test code rendering
        >>> code = UICode(title="Test", language="python", code="def hello(): pass")
        >>> result = tester.render(code)
        >>>
        >>> # Verify syntax highlighting
        >>> assert result.has_ansi_codes()
        >>> assert result.find_color_code("\\x1b[38;5;212m")  # Pink keywords
        >>>
        >>> # Snapshot testing
        >>> tester.snapshot_match("python-hello", result.output)
    """

    def __init__(
        self,
        theme: str = "charm-dark",
        tui_binary: Optional[Path] = None,
        width: int = 80,
        height: int = 24
    ):
        """
        Initialize ComponentTester

        Args:
            theme: Theme to use (charm-dark, charm-light, etc.)
            tui_binary: Path to agentui-tui binary (auto-detected if None)
            width: Terminal width for rendering
            height: Terminal height for rendering
        """
        self.theme = theme
        self.width = width
        self.height = height
        self.tui_binary = tui_binary or self._find_tui_binary()

        if not self.tui_binary.exists():
            raise FileNotFoundError(
                f"TUI binary not found at {self.tui_binary}. "
                f"Run 'make build-tui' first."
            )

    def _find_tui_binary(self) -> Path:
        """Auto-detect TUI binary location"""
        # Check common locations
        locations = [
            Path("bin/agentui-tui"),
            Path("../../bin/agentui-tui"),  # If running from src/
            Path(__file__).parent.parent.parent.parent / "bin" / "agentui-tui"
        ]

        for loc in locations:
            if loc.exists():
                return loc.resolve()

        # Fallback: assume in project root
        return Path("bin/agentui-tui")

    def render(
        self,
        component: Union[UICode, UITable, UIProgress, UIForm, UIConfirm]
    ) -> RenderResult:
        """
        Render a UI component and capture output

        Args:
            component: UI primitive to render (UICode, UITable, etc.)

        Returns:
            RenderResult with ANSI output and metadata
        """
        # Create protocol message
        message = self._component_to_protocol(component)

        # Render via TUI subprocess
        return self._render_message(message)

    def _component_to_protocol(
        self,
        component: Union[UICode, UITable, UIProgress, UIForm, UIConfirm]
    ) -> dict:
        """Convert UI component to protocol message"""
        if isinstance(component, UICode):
            return {
                "type": "code",
                "payload": {
                    "title": component.title,
                    "language": component.language,
                    "code": component.code
                }
            }
        elif isinstance(component, UITable):
            return {
                "type": "table",
                "payload": component.to_dict()
            }
        elif isinstance(component, UIProgress):
            return {
                "type": "progress",
                "payload": component.to_dict()
            }
        elif isinstance(component, UIForm):
            return {
                "type": "form",
                "payload": component.to_dict()
            }
        elif isinstance(component, UIConfirm):
            return {
                "type": "confirm",
                "payload": component.to_dict()
            }
        else:
            raise ValueError(f"Unknown component type: {type(component)}")

    def _render_message(self, message: dict) -> RenderResult:
        """Render protocol message via TUI subprocess in headless mode"""
        # Create JSON message as a single line (required by protocol)
        json_message = json.dumps(message) + "\n"

        try:
            # Run TUI in headless mode with message as stdin
            result = subprocess.run(
                [str(self.tui_binary), "--headless", "--theme", self.theme],
                input=json_message,
                capture_output=True,
                text=True,
                timeout=5  # Prevent hanging
            )

            return RenderResult(
                output=result.stdout,
                exit_code=result.returncode,
                stderr=result.stderr,
                success=result.returncode == 0
            )

        except subprocess.TimeoutExpired:
            return RenderResult(
                output="",
                exit_code=124,  # Timeout exit code
                stderr="TUI rendering timed out",
                success=False
            )
        except FileNotFoundError:
            return RenderResult(
                output="",
                exit_code=127,
                stderr=f"TUI binary not found: {self.tui_binary}",
                success=False
            )

    def render_code(
        self,
        language: str,
        code: str,
        title: str = "Code Example"
    ) -> RenderResult:
        """
        Convenience method: render code with syntax highlighting

        Args:
            language: Programming language (python, go, typescript, rust)
            code: Source code to render
            title: Title for code block

        Returns:
            RenderResult with highlighted code
        """
        component = UICode(title=title, language=language, code=code)
        return self.render(component)

    def render_table(
        self,
        columns: list[str],
        rows: list[list[str]],
        title: str = "Table"
    ) -> RenderResult:
        """
        Convenience method: render table

        Args:
            columns: Column headers
            rows: Table rows
            title: Title for table

        Returns:
            RenderResult with rendered table
        """
        component = UITable(title=title, columns=columns, rows=rows)
        return self.render(component)

    def snapshot_match(self, name: str, output: str):
        """
        Snapshot assertion: compare output to baseline

        This is a convenience wrapper around ANSISnapshotter.
        For more control, use ANSISnapshotter directly.

        Args:
            name: Snapshot name (e.g., "python-fibonacci")
            output: ANSI output to compare

        Raises:
            AssertionError: If output doesn't match baseline
        """
        from .snapshot import ANSISnapshotter

        snapshotter = ANSISnapshotter()
        diff = snapshotter.compare(name, output)

        if not diff.matched:
            raise AssertionError(
                f"Snapshot mismatch for '{name}':\n{diff.render()}"
            )
