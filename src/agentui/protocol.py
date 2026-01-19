"""
Protocol handling for communication with Go TUI.

JSON Lines protocol over stdio.
"""

import json
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal


class MessageType(str, Enum):
    """Message types for the protocol."""
    # Python → Go (render commands)
    TEXT = "text"
    MARKDOWN = "markdown"
    PROGRESS = "progress"
    FORM = "form"
    TABLE = "table"
    CODE = "code"
    CONFIRM = "confirm"
    SELECT = "select"
    ALERT = "alert"
    SPINNER = "spinner"
    STATUS = "status"
    CLEAR = "clear"
    DONE = "done"
    UPDATE = "update"  # Phase 3: Progressive streaming - update existing component
    LAYOUT = "layout"  # Phase 5: Multi-component layouts

    # Go → Python (user events)
    INPUT = "input"
    FORM_RESPONSE = "form_response"
    CONFIRM_RESPONSE = "confirm_response"
    SELECT_RESPONSE = "select_response"
    CANCEL = "cancel"
    QUIT = "quit"
    RESIZE = "resize"


@dataclass
class Message:
    """Base message for protocol communication."""
    type: str
    id: str | None = None
    payload: dict | None = None

    def to_json(self) -> str:
        """Serialize to JSON line."""
        data: dict[str, Any] = {"type": self.type}
        if self.id:
            data["id"] = self.id
        if self.payload:
            data["payload"] = self.payload
        return json.dumps(data)

    @classmethod
    def from_json(cls, line: str) -> "Message":
        """Deserialize from JSON line."""
        data = json.loads(line)
        return cls(
            type=data.get("type", ""),
            id=data.get("id"),
            payload=data.get("payload"),
        )


# --- Payload builders for Python → Go ---

def text_payload(content: str, done: bool = False) -> dict[str, Any]:
    """Create text payload."""
    return {"content": content, "done": done}


def markdown_payload(content: str, title: str | None = None) -> dict[str, Any]:
    """Create markdown payload."""
    payload: dict[str, Any] = {"content": content}
    if title:
        payload["title"] = title
    return payload


def progress_payload(
    message: str,
    percent: float | None = None,
    steps: list[dict] | None = None,
) -> dict[str, Any]:
    """Create progress payload."""
    payload: dict[str, Any] = {"message": message}
    if percent is not None:
        payload["percent"] = percent
    if steps:
        payload["steps"] = steps
    return payload


def form_payload(
    fields: list[dict],
    title: str | None = None,
    description: str | None = None,
    submit_label: str = "Submit",
    cancel_label: str = "Cancel",
) -> dict[str, Any]:
    """Create form payload."""
    payload: dict[str, Any] = {"fields": fields}
    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    payload["submit_label"] = submit_label
    payload["cancel_label"] = cancel_label
    return payload


def form_field(
    name: str,
    label: str,
    field_type: str = "text",
    options: list[str] | None = None,
    default: Any = None,
    required: bool = False,
    description: str | None = None,
    placeholder: str | None = None,
) -> dict[str, Any]:
    """Create a form field definition."""
    field: dict[str, Any] = {
        "name": name,
        "label": label,
        "type": field_type,
    }
    if options:
        field["options"] = options
    if default is not None:
        field["default"] = default
    if required:
        field["required"] = required
    if description:
        field["description"] = description
    if placeholder:
        field["placeholder"] = placeholder
    return field


def table_payload(
    columns: list[str | dict],
    rows: list[list[str]],
    title: str | None = None,
    footer: str | None = None,
) -> dict[str, Any]:
    """Create table payload."""
    payload: dict[str, Any] = {"columns": columns, "rows": rows}
    if title:
        payload["title"] = title
    if footer:
        payload["footer"] = footer
    return payload


def code_payload(
    code: str,
    language: str = "text",
    title: str | None = None,
    line_numbers: bool = True,
) -> dict[str, Any]:
    """Create code payload."""
    payload: dict[str, Any] = {
        "code": code,
        "language": language,
        "line_numbers": line_numbers,
    }
    if title:
        payload["title"] = title
    return payload


def confirm_payload(
    message: str,
    title: str | None = None,
    confirm_label: str = "Yes",
    cancel_label: str = "No",
    destructive: bool = False,
) -> dict[str, Any]:
    """Create confirm payload."""
    payload: dict[str, Any] = {
        "message": message,
        "confirm_label": confirm_label,
        "cancel_label": cancel_label,
        "destructive": destructive,
    }
    if title:
        payload["title"] = title
    return payload


def select_payload(
    label: str,
    options: list[str],
    default: str | None = None,
) -> dict[str, Any]:
    """Create select payload."""
    payload: dict[str, Any] = {"label": label, "options": options}
    if default:
        payload["default"] = default
    return payload


def alert_payload(
    message: str,
    severity: Literal["info", "success", "warning", "error"] = "info",
    title: str | None = None,
) -> dict[str, Any]:
    """Create alert payload."""
    payload: dict[str, Any] = {"message": message, "severity": severity}
    if title:
        payload["title"] = title
    return payload


def spinner_payload(message: str) -> dict[str, Any]:
    """Create spinner payload."""
    return {"message": message}


def status_payload(
    message: str,
    tokens: dict | None = None,
) -> dict[str, Any]:
    """Create status payload."""
    payload: dict[str, Any] = {"message": message}
    if tokens:
        payload["tokens"] = tokens
    return payload


def clear_payload(scope: str = "chat") -> dict[str, Any]:
    """Create clear payload."""
    return {"scope": scope}


def done_payload(summary: str | None = None) -> dict[str, Any]:
    """Create done payload."""
    payload: dict[str, Any] = {}
    if summary:
        payload["summary"] = summary
    return payload


def update_payload(component_id: str, **updates: Any) -> dict[str, Any]:
    """
    Create update payload for progressive streaming (Phase 3).

    Used to update an existing component in-place by ID.

    Args:
        component_id: ID of component to update
        **updates: Fields to update (e.g., percent=50, rows=[...])

    Returns:
        Payload dict with id and update fields
    """
    return {"id": component_id, **updates}


def layout_payload(
    title: str | None = None,
    description: str | None = None,
    components: list[dict] | None = None,
) -> dict[str, Any]:
    """
    Create layout payload for multi-component layouts (Phase 5).

    Args:
        title: Layout title
        description: Layout description
        components: List of component dicts with type, payload, area

    Returns:
        Payload dict for layout message
    """
    payload: dict[str, Any] = {}
    if title:
        payload["title"] = title
    if description:
        payload["description"] = description
    if components:
        payload["components"] = components
    return payload


# --- Message constructors ---

def create_message(
    msg_type: MessageType | str,
    payload: dict | None = None,
    msg_id: str | None = None,
) -> Message:
    """Create a protocol message."""
    if isinstance(msg_type, MessageType):
        msg_type = msg_type.value
    return Message(type=msg_type, id=msg_id, payload=payload)


def create_request(
    msg_type: MessageType | str,
    payload: dict | None = None,
) -> Message:
    """Create a request message with auto-generated ID."""
    return create_message(msg_type, payload, msg_id=str(uuid.uuid4()))
