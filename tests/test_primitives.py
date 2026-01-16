"""
Tests for the primitives module.
"""

import pytest
from agentui.primitives import (
    UIForm,
    UIFormField,
    UIProgress,
    UIProgressStep,
    UITable,
    UICode,
    UIConfirm,
    UISelect,
    text_field,
    select_field,
    checkbox_field,
    number_field,
)


def test_form_field_to_dict():
    """Test form field serialization."""
    field = UIFormField(
        name="username",
        label="Username",
        type="text",
        required=True,
        placeholder="Enter username",
    )
    
    d = field.to_dict()
    
    assert d["name"] == "username"
    assert d["label"] == "Username"
    assert d["type"] == "text"
    assert d["required"] is True
    assert d["placeholder"] == "Enter username"


def test_form_field_optional_fields():
    """Test that optional fields are excluded when None."""
    field = UIFormField(name="test", label="Test")
    d = field.to_dict()
    
    assert "options" not in d
    assert "description" not in d
    assert "placeholder" not in d


def test_form_to_dict():
    """Test form serialization."""
    form = UIForm(
        title="Test Form",
        description="A test form",
        fields=[
            UIFormField(name="field1", label="Field 1"),
            UIFormField(name="field2", label="Field 2", type="select", options=["A", "B"]),
        ],
        submit_label="Save",
    )
    
    d = form.to_dict()
    
    assert d["title"] == "Test Form"
    assert d["description"] == "A test form"
    assert len(d["fields"]) == 2
    assert d["submit_label"] == "Save"


def test_progress_to_dict():
    """Test progress serialization."""
    progress = UIProgress(
        message="Loading...",
        percent=75.0,
        steps=[
            UIProgressStep("Step 1", "complete"),
            UIProgressStep("Step 2", "running", "Processing..."),
        ],
    )
    
    d = progress.to_dict()
    
    assert d["message"] == "Loading..."
    assert d["percent"] == 75.0
    assert len(d["steps"]) == 2
    assert d["steps"][0]["status"] == "complete"
    assert d["steps"][1]["detail"] == "Processing..."


def test_table_to_dict():
    """Test table serialization."""
    table = UITable(
        title="Data",
        columns=["A", "B", "C"],
        rows=[["1", "2", "3"], ["4", "5", "6"]],
        footer="Total: 6",
    )
    
    d = table.to_dict()
    
    assert d["title"] == "Data"
    assert d["columns"] == ["A", "B", "C"]
    assert len(d["rows"]) == 2
    assert d["footer"] == "Total: 6"


def test_code_to_dict():
    """Test code block serialization."""
    code = UICode(
        code="def hello(): pass",
        language="python",
        title="example.py",
        line_numbers=True,
    )
    
    d = code.to_dict()
    
    assert d["code"] == "def hello(): pass"
    assert d["language"] == "python"
    assert d["title"] == "example.py"
    assert d["line_numbers"] is True


def test_confirm_to_dict():
    """Test confirm dialog serialization."""
    confirm = UIConfirm(
        message="Are you sure?",
        title="Confirm",
        confirm_label="Yes",
        cancel_label="No",
        destructive=True,
    )
    
    d = confirm.to_dict()
    
    assert d["message"] == "Are you sure?"
    assert d["title"] == "Confirm"
    assert d["confirm_label"] == "Yes"
    assert d["destructive"] is True


def test_select_to_dict():
    """Test select menu serialization."""
    select = UISelect(
        label="Choose option",
        options=["A", "B", "C"],
        default="B",
    )
    
    d = select.to_dict()
    
    assert d["label"] == "Choose option"
    assert d["options"] == ["A", "B", "C"]
    assert d["default"] == "B"


def test_convenience_text_field():
    """Test text_field convenience function."""
    field = text_field("email", "Email", required=True, placeholder="you@example.com")
    
    assert field.name == "email"
    assert field.type == "text"
    assert field.required is True


def test_convenience_select_field():
    """Test select_field convenience function."""
    field = select_field("color", "Color", ["Red", "Green", "Blue"])
    
    assert field.name == "color"
    assert field.type == "select"
    assert field.options == ["Red", "Green", "Blue"]


def test_convenience_checkbox_field():
    """Test checkbox_field convenience function."""
    field = checkbox_field("agree", "I agree", default=True)
    
    assert field.name == "agree"
    assert field.type == "checkbox"
    assert field.default is True


def test_convenience_number_field():
    """Test number_field convenience function."""
    field = number_field("count", "Count", default=10)
    
    assert field.name == "count"
    assert field.type == "number"
    assert field.default == 10
