"""
UI Primitives - Dataclasses for generative UI components.

This module defines the UI primitive types that agents can return from tools
to render rich, interactive interfaces. These primitives are serialized to
JSON and sent to the Go TUI for rendering (or Rich for CLI fallback).

UI primitives enable "Generative UI" - the LLM can decide which UI components
to render based on the task. For example, returning a UITable for data,
UIForm for input collection, or UIProgress for long-running operations.

All primitives implement `to_dict()` for protocol serialization.

Available Primitives:
    - UIForm: Multi-field forms for collecting user input
    - UIConfirm: Yes/no confirmation dialogs
    - UISelect: Selection menus
    - UITable: Data tables with columns and rows
    - UICode: Syntax-highlighted code blocks
    - UIProgress: Progress indicators with optional steps
    - UIAlert: Notification alerts (info/success/warning/error)
    - UIMarkdown: Rendered markdown content
    - UIText: Plain text (used for streaming)
    - UIInput: Single text input field
    - UISpinner: Loading spinner

Example:
    Return a table from a tool:

    >>> from agentui.primitives import UITable
    >>>
    >>> @app.ui_tool(name="search", description="Search database", parameters={...})
    >>> async def search(query: str):
    ...     results = await database.search(query)
    ...     return UITable(
    ...         columns=["ID", "Name", "Score"],
    ...         rows=[[r.id, r.name, str(r.score)] for r in results],
    ...         title=f"Results for: {query}",
    ...         footer=f"{len(results)} items found"
    ...     )

    Collect user input with a form:

    >>> from agentui.primitives import UIForm, text_field, select_field
    >>>
    >>> @app.ui_tool(name="configure", description="Configure settings", parameters={})
    >>> async def configure():
    ...     return UIForm(
    ...         title="Configuration",
    ...         fields=[
    ...             text_field("name", "Your Name", required=True),
    ...             select_field("theme", "Theme", ["dark", "light"], default="dark"),
    ...         ]
    ...     )
"""

from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class UIFormField:
    """
    A single field in a UIForm.

    Represents one input field with its configuration, validation rules,
    and display properties.

    Attributes:
        name: Field identifier (used as key in form results)
        label: Display label for the field
        type: Field input type (text, select, checkbox, number, password, textarea)
        options: List of choices for select fields (required if type="select")
        default: Default value for the field
        required: Whether the field must be filled
        description: Optional help text shown below the field
        placeholder: Placeholder text for empty fields

    Example:
        >>> field = UIFormField(
        ...     name="email",
        ...     label="Email Address",
        ...     type="text",
        ...     required=True,
        ...     placeholder="user@example.com",
        ...     description="We'll never share your email"
        ... )
    """
    name: str
    label: str
    type: Literal["text", "select", "checkbox", "number", "password", "textarea"] = "text"
    options: list[str] | None = None
    default: Any = None
    required: bool = False
    description: str | None = None
    placeholder: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to protocol dictionary for JSON serialization.

        Returns:
            Dictionary with field configuration
        """
        d: dict[str, Any] = {
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
    """
    A multi-field form for collecting structured user input.

    UIForm allows agents to request complex input with multiple fields,
    validation rules, and custom styling. The form blocks until the user
    submits or cancels.

    Attributes:
        fields: List of UIFormField objects defining the form inputs
        title: Optional form title
        description: Optional description shown above fields
        submit_label: Text for submit button (default: "Submit")
        cancel_label: Text for cancel button (default: "Cancel")

    Returns:
        When submitted, returns a dict mapping field names to values.
        Returns None if cancelled.

    Example:
        >>> from agentui.primitives import UIForm, text_field, select_field
        >>>
        >>> form = UIForm(
        ...     title="User Registration",
        ...     description="Please fill out all required fields",
        ...     fields=[
        ...         text_field("username", "Username", required=True),
        ...         text_field("email", "Email", required=True),
        ...         select_field("role", "Role", ["user", "admin"]),
        ...     ]
        ... )
    """
    fields: list[UIFormField]
    title: str | None = None
    description: str | None = None
    submit_label: str = "Submit"
    cancel_label: str = "Cancel"

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to protocol dictionary for JSON serialization.

        Returns:
            Dictionary with form configuration and field definitions
        """
        return {
            "title": self.title,
            "description": self.description,
            "fields": [f.to_dict() for f in self.fields],
            "submit_label": self.submit_label,
            "cancel_label": self.cancel_label,
        }


@dataclass
class UIProgressStep:
    """
    A single step in a multi-step progress indicator.

    Attributes:
        label: Step name/description
        status: Current status (pending, running, complete, error)
        detail: Optional additional detail text
    """
    label: str
    status: Literal["pending", "running", "complete", "error"] = "pending"
    detail: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {"label": self.label, "status": self.status}
        if self.detail:
            d["detail"] = self.detail
        return d


@dataclass
class UIProgress:
    """
    Progress indicator for long-running operations.

    Shows either a percentage-based progress bar or a multi-step workflow.
    Useful for keeping users informed during lengthy operations.

    Attributes:
        message: Progress message describing current operation
        percent: Optional progress percentage (0-100)
        steps: Optional list of UIProgressStep objects for multi-step workflows

    Example:
        >>> progress = UIProgress(
        ...     message="Processing files...",
        ...     percent=45.5
        ... )
        >>>
        >>> # Or with steps:
        >>> progress = UIProgress(
        ...     message="Building project",
        ...     steps=[
        ...         UIProgressStep("Install dependencies", status="complete"),
        ...         UIProgressStep("Compile code", status="running"),
        ...         UIProgressStep("Run tests", status="pending"),
        ...     ]
        ... )
    """
    message: str
    percent: float | None = None
    steps: list[UIProgressStep] | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {"message": self.message}
        if self.percent is not None:
            d["percent"] = self.percent
        if self.steps:
            d["steps"] = [s.to_dict() for s in self.steps]
        return d


@dataclass
class UITable:
    """
    A data table with columns and rows.

    Displays tabular data with automatic formatting and alignment.
    Perfect for showing structured data, query results, or comparisons.

    Attributes:
        columns: List of column headers
        rows: List of rows, where each row is a list of cell values (as strings)
        title: Optional table title
        footer: Optional footer text (e.g., row count, summary)

    Example:
        >>> table = UITable(
        ...     columns=["Name", "Age", "City"],
        ...     rows=[
        ...         ["Alice", "30", "NYC"],
        ...         ["Bob", "25", "SF"],
        ...         ["Charlie", "35", "LA"],
        ...     ],
        ...     title="User Directory",
        ...     footer="3 users found"
        ... )
    """
    columns: list[str]
    rows: list[list[str]]
    title: str | None = None
    footer: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {"columns": self.columns, "rows": self.rows}
        if self.title:
            d["title"] = self.title
        if self.footer:
            d["footer"] = self.footer
        return d


@dataclass
class UICode:
    """
    A syntax-highlighted code block.

    Renders code with syntax highlighting using Chroma. Supports 200+ languages.

    Attributes:
        code: Source code to display
        language: Language identifier for syntax highlighting (e.g., "python", "javascript")
        title: Optional title/filename to display above code
        line_numbers: Whether to show line numbers (default: True)

    Example:
        >>> code = UICode(
        ...     code='def hello():\n    print("Hello, world!")',
        ...     language="python",
        ...     title="hello.py",
        ...     line_numbers=True
        ... )
    """
    code: str
    language: str = "text"
    title: str | None = None
    line_numbers: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {
            "code": self.code,
            "language": self.language,
            "line_numbers": self.line_numbers,
        }
        if self.title:
            d["title"] = self.title
        return d


@dataclass
class UIConfirm:
    """
    A yes/no confirmation dialog.

    Blocks until the user confirms or cancels. Useful for getting explicit
    permission before destructive or important actions.

    Attributes:
        message: Confirmation question/message
        title: Optional dialog title
        confirm_label: Text for confirm button (default: "Yes")
        cancel_label: Text for cancel button (default: "No")
        destructive: If True, styles confirm button as destructive/dangerous

    Returns:
        True if confirmed, False if cancelled

    Example:
        >>> confirm = UIConfirm(
        ...     message="Are you sure you want to delete all files?",
        ...     title="Confirm Deletion",
        ...     confirm_label="Delete",
        ...     cancel_label="Cancel",
        ...     destructive=True
        ... )
    """
    message: str
    title: str | None = None
    confirm_label: str = "Yes"
    cancel_label: str = "No"
    destructive: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {
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
    """
    A selection menu for choosing from a list of options.

    Attributes:
        label: Prompt/question for the selection
        options: List of choices to display
        default: Default selected option

    Returns:
        Selected option string, or None if cancelled
    """
    label: str
    options: list[str]
    default: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {"label": self.label, "options": self.options}
        if self.default:
            d["default"] = self.default
        return d


@dataclass
class UIAlert:
    """
    A notification alert with severity levels.

    Non-blocking notification shown to the user.

    Attributes:
        message: Alert message text
        severity: Alert level (info, success, warning, error)
        title: Optional alert title
    """
    message: str
    severity: Literal["info", "success", "warning", "error"] = "info"
    title: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {"message": self.message, "severity": self.severity}
        if self.title:
            d["title"] = self.title
        return d


@dataclass
class UIText:
    """
    Plain text content for streaming responses.

    Attributes:
        content: Text content to display
        done: Whether this is the final chunk (for streaming)
    """
    content: str
    done: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        return {"content": self.content, "done": self.done}


@dataclass
class UIMarkdown:
    """
    Rendered markdown content.

    Attributes:
        content: Markdown text to render
        title: Optional title to display above content
    """
    content: str
    title: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {"content": self.content}
        if self.title:
            d["title"] = self.title
        return d


@dataclass
class UIInput:
    """
    A single text input field.

    Attributes:
        label: Input prompt/label
        default: Default value
        password: If True, masks input (for passwords)
    """
    label: str
    default: str | None = None
    password: bool = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        d: dict[str, Any] = {"label": self.label, "password": self.password}
        if self.default:
            d["default"] = self.default
        return d


@dataclass
class UISpinner:
    """
    A loading spinner indicator.

    Attributes:
        message: Loading message to display
    """
    message: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to protocol dictionary for JSON serialization."""
        return {"message": self.message}


# --- Convenience constructors ---

def text_field(
    name: str,
    label: str,
    required: bool = False,
    placeholder: str | None = None,
    default: str | None = None,
) -> UIFormField:
    """
    Create a text input form field.

    Convenience constructor for text-type UIFormField.

    Args:
        name: Field identifier
        label: Display label
        required: Whether field is required
        placeholder: Placeholder text
        default: Default value

    Returns:
        UIFormField with type="text"
    """
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
    """
    Create a select/dropdown form field.

    Args:
        name: Field identifier
        label: Display label
        options: List of options to choose from
        required: Whether field is required
        default: Default selected option

    Returns:
        UIFormField with type="select"
    """
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
    """
    Create a checkbox form field.

    Args:
        name: Field identifier
        label: Display label
        default: Default checked state

    Returns:
        UIFormField with type="checkbox"
    """
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
    """
    Create a number input form field.

    Args:
        name: Field identifier
        label: Display label
        required: Whether field is required
        default: Default numeric value

    Returns:
        UIFormField with type="number"
    """
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
    """
    Create a multi-line textarea form field.

    Args:
        name: Field identifier
        label: Display label
        required: Whether field is required
        placeholder: Placeholder text

    Returns:
        UIFormField with type="textarea"
    """
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
