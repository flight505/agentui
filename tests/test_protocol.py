"""
Tests for the protocol module.
"""

import json
import pytest
from agentui.protocol import (
    Message,
    MessageType,
    create_message,
    create_request,
    form_field,
    form_payload,
    table_payload,
    code_payload,
    text_payload,
    progress_payload,
)


def test_message_to_json():
    """Test message serialization."""
    msg = create_message(MessageType.TEXT, text_payload("Hello"))
    json_str = msg.to_json()
    
    parsed = json.loads(json_str)
    assert parsed["type"] == "text"
    assert parsed["payload"]["content"] == "Hello"


def test_message_from_json():
    """Test message deserialization."""
    json_str = '{"type": "input", "payload": {"content": "Hello"}}'
    msg = Message.from_json(json_str)
    
    assert msg.type == "input"
    assert msg.payload["content"] == "Hello"


def test_create_request_has_id():
    """Test that requests have auto-generated IDs."""
    msg = create_request(MessageType.FORM, form_payload([]))
    
    assert msg.id is not None
    assert len(msg.id) > 0


def test_form_field():
    """Test form field creation."""
    field = form_field(
        name="email",
        label="Email Address",
        field_type="text",
        required=True,
        placeholder="you@example.com",
    )
    
    assert field["name"] == "email"
    assert field["label"] == "Email Address"
    assert field["type"] == "text"
    assert field["required"] is True
    assert field["placeholder"] == "you@example.com"


def test_form_payload():
    """Test form payload creation."""
    fields = [
        form_field("name", "Name", "text"),
        form_field("role", "Role", "select", options=["Admin", "User"]),
    ]
    
    payload = form_payload(
        fields=fields,
        title="User Form",
        description="Enter user details",
    )
    
    assert payload["title"] == "User Form"
    assert payload["description"] == "Enter user details"
    assert len(payload["fields"]) == 2


def test_table_payload():
    """Test table payload creation."""
    payload = table_payload(
        columns=["Name", "Value"],
        rows=[["A", "1"], ["B", "2"]],
        title="Test Table",
        footer="Total: 2",
    )
    
    assert payload["title"] == "Test Table"
    assert payload["columns"] == ["Name", "Value"]
    assert len(payload["rows"]) == 2
    assert payload["footer"] == "Total: 2"


def test_code_payload():
    """Test code payload creation."""
    payload = code_payload(
        code="print('hello')",
        language="python",
        title="example.py",
    )
    
    assert payload["code"] == "print('hello')"
    assert payload["language"] == "python"
    assert payload["title"] == "example.py"
    assert payload["line_numbers"] is True


def test_progress_payload():
    """Test progress payload creation."""
    payload = progress_payload(
        message="Processing...",
        percent=50.0,
        steps=[
            {"label": "Step 1", "status": "complete"},
            {"label": "Step 2", "status": "running"},
        ],
    )
    
    assert payload["message"] == "Processing..."
    assert payload["percent"] == 50.0
    assert len(payload["steps"]) == 2
