"""
Multi-Component Layouts - Dashboard-style compositions (Phase 5).

Enables displaying multiple UI components in a single view, inspired by
dashboard layouts. Components can be organized with layout hints.
"""

from typing import Any, Literal
from dataclasses import dataclass, field


@dataclass
class LayoutComponent:
    """A component within a layout with positioning hints."""
    type: str  # "table", "code", "progress", "alert", etc.
    payload: dict[str, Any]
    area: str | None = None  # Layout area hint: "left", "right", "top", "bottom", "center"
    width: int | None = None  # Width hint (percentage or cols)
    height: int | None = None  # Height hint (percentage or rows)


class UILayout:
    """
    Multi-component layout for dashboard-style UIs (Phase 5).

    Composes multiple UI components into a single view with layout hints.
    The TUI renderer can arrange components based on available space.

    Usage:
        layout = UILayout(title="System Dashboard")

        layout.add_table(
            columns=["Service", "Status"],
            rows=[["API", "✓"], ["DB", "✓"]],
            area="left"
        )

        layout.add_progress(
            message="CPU Usage",
            percent=65,
            area="right-top"
        )

        layout.add_code(
            code="config = {...}",
            language="json",
            area="right-bottom"
        )

        return layout
    """

    def __init__(self, title: str | None = None, description: str | None = None):
        """
        Initialize layout.

        Args:
            title: Layout title
            description: Optional description
        """
        self.title = title
        self.description = description
        self.components: list[LayoutComponent] = []

    def add_table(
        self,
        columns: list[str],
        rows: list[list[str]],
        title: str | None = None,
        footer: str | None = None,
        area: str | None = None,
        **kwargs
    ) -> "UILayout":
        """
        Add table component to layout.

        Args:
            columns: Column headers
            rows: Table data
            title: Table title
            footer: Table footer
            area: Layout area hint
            **kwargs: Additional layout hints

        Returns:
            Self for chaining
        """
        self.components.append(LayoutComponent(
            type="table",
            payload={
                "columns": columns,
                "rows": rows,
                "title": title,
                "footer": footer,
            },
            area=area,
            width=kwargs.get("width"),
            height=kwargs.get("height"),
        ))
        return self

    def add_code(
        self,
        code: str,
        language: str = "text",
        title: str | None = None,
        area: str | None = None,
        **kwargs
    ) -> "UILayout":
        """
        Add code component to layout.

        Args:
            code: Source code
            language: Programming language
            title: Code block title
            area: Layout area hint
            **kwargs: Additional layout hints

        Returns:
            Self for chaining
        """
        self.components.append(LayoutComponent(
            type="code",
            payload={
                "code": code,
                "language": language,
                "title": title,
            },
            area=area,
            width=kwargs.get("width"),
            height=kwargs.get("height"),
        ))
        return self

    def add_progress(
        self,
        message: str,
        percent: float | None = None,
        steps: list[dict] | None = None,
        area: str | None = None,
        **kwargs
    ) -> "UILayout":
        """
        Add progress component to layout.

        Args:
            message: Progress message
            percent: Percentage (0-100)
            steps: Multi-step progress
            area: Layout area hint
            **kwargs: Additional layout hints

        Returns:
            Self for chaining
        """
        self.components.append(LayoutComponent(
            type="progress",
            payload={
                "message": message,
                "percent": percent,
                "steps": steps,
            },
            area=area,
            width=kwargs.get("width"),
            height=kwargs.get("height"),
        ))
        return self

    def add_alert(
        self,
        message: str,
        severity: Literal["info", "success", "warning", "error"] = "info",
        title: str | None = None,
        area: str | None = None,
        **kwargs
    ) -> "UILayout":
        """
        Add alert component to layout.

        Args:
            message: Alert message
            severity: Alert severity
            title: Alert title
            area: Layout area hint
            **kwargs: Additional layout hints

        Returns:
            Self for chaining
        """
        self.components.append(LayoutComponent(
            type="alert",
            payload={
                "message": message,
                "severity": severity,
                "title": title,
            },
            area=area,
            width=kwargs.get("width"),
            height=kwargs.get("height"),
        ))
        return self

    def add_component(
        self,
        component_type: str,
        payload: dict[str, Any],
        area: str | None = None,
        **kwargs
    ) -> "UILayout":
        """
        Add generic component to layout.

        Args:
            component_type: Component type
            payload: Component payload
            area: Layout area hint
            **kwargs: Additional layout hints

        Returns:
            Self for chaining
        """
        self.components.append(LayoutComponent(
            type=component_type,
            payload=payload,
            area=area,
            width=kwargs.get("width"),
            height=kwargs.get("height"),
        ))
        return self

    def to_dict(self) -> dict[str, Any]:
        """
        Convert layout to dict for protocol serialization.

        Returns:
            Dict representation
        """
        return {
            "title": self.title,
            "description": self.description,
            "components": [
                {
                    "type": comp.type,
                    "payload": comp.payload,
                    "area": comp.area,
                    "width": comp.width,
                    "height": comp.height,
                }
                for comp in self.components
            ]
        }

    def __repr__(self) -> str:
        """String representation."""
        return f"UILayout(title={self.title!r}, components={len(self.components)})"
