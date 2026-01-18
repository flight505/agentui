"""
UI Primitives - Dataclasses for generative UI elements.

These primitives are serialized to JSON and sent to the Go TUI for rendering.
They can also be rendered in fallback CLI mode using Rich.
"""

from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class UIFormField:
    """A single form field."""
    name: str
    label: str
    type: Literal["text", "select", "checkbox", "number", "password", "textarea"] = "text"
    options: list[str] | None = None
    default: Any = None
    required: bool = False
    description: str | None = None
    placeholder: str | None = None

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {
            "name": self.name,
            "label": self.label,
            "type": self.type,
        }
        if self.options:
            d["options"] = self.options
        if self.default is not None:
            d["default"] = self.default
        if self.required:
            d["required"] = self.required
        if self.description:
            d["description"] = self.description
        if self.placeholder:
            d["placeholder"] = self.placeholder
        return d


@dataclass
class UIForm:
    """A form for collecting user input."""
    fields: list[UIFormField]
    title: str | None = None
    description: str | None = None
    submit_label: str = "Submit"
    cancel_label: str = "Cancel"

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        return {
            "title": self.title,
            "description": self.description,
            "fields": [f.to_dict() for f in self.fields],
            "submit_label": self.submit_label,
            "cancel_label": self.cancel_label,
        }


@dataclass
class UIProgressStep:
    """A step in a multi-step progress indicator."""
    label: str
    status: Literal["pending", "running", "complete", "error"] = "pending"
    detail: str | None = None

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {"label": self.label, "status": self.status}
        if self.detail:
            d["detail"] = self.detail
        return d


@dataclass
class UIProgress:
    """Progress indicator with optional steps."""
    message: str
    percent: float | None = None
    steps: list[UIProgressStep] | None = None

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {"message": self.message}
        if self.percent is not None:
            d["percent"] = self.percent
        if self.steps:
            d["steps"] = [s.to_dict() for s in self.steps]
        return d


@dataclass
class UITable:
    """A data table."""
    columns: list[str]
    rows: list[list[str]]
    title: str | None = None
    footer: str | None = None

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {"columns": self.columns, "rows": self.rows}
        if self.title:
            d["title"] = self.title
        if self.footer:
            d["footer"] = self.footer
        return d


@dataclass
class UICode:
    """A syntax-highlighted code block."""
    code: str
    language: str = "text"
    title: str | None = None
    line_numbers: bool = True

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {
            "code": self.code,
            "language": self.language,
            "line_numbers": self.line_numbers,
        }
        if self.title:
            d["title"] = self.title
        return d


@dataclass
class UIConfirm:
    """A confirmation dialog."""
    message: str
    title: str | None = None
    confirm_label: str = "Yes"
    cancel_label: str = "No"
    destructive: bool = False

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {
            "message": self.message,
            "confirm_label": self.confirm_label,
            "cancel_label": self.cancel_label,
            "destructive": self.destructive,
        }
        if self.title:
            d["title"] = self.title
        return d


@dataclass
class UISelect:
    """A selection menu."""
    label: str
    options: list[str]
    default: str | None = None

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {"label": self.label, "options": self.options}
        if self.default:
            d["default"] = self.default
        return d


@dataclass
class UIAlert:
    """A notification alert."""
    message: str
    severity: Literal["info", "success", "warning", "error"] = "info"
    title: str | None = None

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {"message": self.message, "severity": self.severity}
        if self.title:
            d["title"] = self.title
        return d


@dataclass
class UIText:
    """Plain text content (for streaming)."""
    content: str
    done: bool = False

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        return {"content": self.content, "done": self.done}


@dataclass
class UIMarkdown:
    """Markdown content."""
    content: str
    title: str | None = None

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {"content": self.content}
        if self.title:
            d["title"] = self.title
        return d


@dataclass
class UIInput:
    """A text input field."""
    label: str
    default: str | None = None
    password: bool = False

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        d = {"label": self.label, "password": self.password}
        if self.default:
            d["default"] = self.default
        return d


@dataclass
class UISpinner:
    """A spinner/loading indicator."""
    message: str

    def to_dict(self) -> dict:
        """Convert to protocol dict."""
        return {"message": self.message}


# --- Convenience constructors ---

def text_field(
    name: str,
    label: str,
    required: bool = False,
    placeholder: str | None = None,
    default: str | None = None,
) -> UIFormField:
    """Create a text input field."""
    return UIFormField(
        name=name,
        label=label,
        type="text",
        required=required,
        placeholder=placeholder,
        default=default,
    )


def select_field(
    name: str,
    label: str,
    options: list[str],
    required: bool = False,
    default: str | None = None,
) -> UIFormField:
    """Create a select field."""
    return UIFormField(
        name=name,
        label=label,
        type="select",
        options=options,
        required=required,
        default=default,
    )


def checkbox_field(
    name: str,
    label: str,
    default: bool = False,
) -> UIFormField:
    """Create a checkbox field."""
    return UIFormField(
        name=name,
        label=label,
        type="checkbox",
        default=default,
    )


def number_field(
    name: str,
    label: str,
    required: bool = False,
    default: int | float | None = None,
) -> UIFormField:
    """Create a number field."""
    return UIFormField(
        name=name,
        label=label,
        type="number",
        required=required,
        default=default,
    )


def textarea_field(
    name: str,
    label: str,
    required: bool = False,
    placeholder: str | None = None,
) -> UIFormField:
    """Create a textarea field."""
    return UIFormField(
        name=name,
        label=label,
        type="textarea",
        required=required,
        placeholder=placeholder,
    )


# Type alias for all UI primitive types
UIPrimitive = (
    UIForm
    | UIConfirm
    | UISelect
    | UITable
    | UICode
    | UIProgress
    | UIAlert
    | UIMarkdown
    | UIText
    | UIInput
    | UISpinner
)
