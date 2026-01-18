"""
Test Phase 2: Data-Driven Component Selection

Verifies:
1. Intelligent component selection based on data structure
2. Language detection for code blocks
3. Markdown detection
4. List of dicts → Table conversion
5. Component override mechanisms
6. Integration with tool execution
"""

import pytest
from agentui.component_selector import ComponentSelector
from agentui.primitives import UITable, UICode, UIProgress, UIAlert, UISelect, UIMarkdown, UIText
from agentui.core import AgentCore
from agentui.types import ToolDefinition


class TestComponentSelection:
    """Test automatic component selection based on data structure."""

    def test_list_of_dicts_to_table(self):
        """Test list of dicts → Table."""
        data = [
            {"name": "Alice", "age": 30, "city": "NYC"},
            {"name": "Bob", "age": 25, "city": "SF"},
            {"name": "Charlie", "age": 35, "city": "LA"},
        ]

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "table"
        assert isinstance(ui, UITable)
        assert ui.columns == ["name", "age", "city"]
        assert len(ui.rows) == 3
        assert ui.rows[0] == ["Alice", "30", "NYC"]

    def test_empty_list(self):
        """Test empty list handling."""
        data = []

        component_type, ui = ComponentSelector.select_component(data)

        # Empty list should become text
        assert component_type in ("text", "table")

    def test_list_of_primitives_to_table(self):
        """Test list of primitives → Single column table."""
        data = ["apple", "banana", "cherry"]

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "table"
        assert isinstance(ui, UITable)
        assert ui.columns == ["Items"]
        assert ui.rows == [["apple"], ["banana"], ["cherry"]]

    def test_dict_with_columns_rows(self):
        """Test dict with explicit table structure."""
        data = {
            "columns": ["Name", "Status"],
            "rows": [["API", "✓"], ["DB", "✓"]],
            "title": "Services",
        }

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "table"
        assert isinstance(ui, UITable)
        assert ui.title == "Services"

    def test_dict_with_code_language(self):
        """Test dict with code/language → Code."""
        data = {
            "code": "def hello():\n    print('Hello')",
            "language": "python",
            "title": "Example",
        }

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "code"
        assert isinstance(ui, UICode)
        assert ui.language == "python"
        assert "def hello" in ui.code

    def test_long_string_with_code(self):
        """Test long string with code patterns → Code block."""
        data = """
def calculate_sum(numbers):
    total = 0
    for num in numbers:
        total += num
    return total

class Calculator:
    def __init__(self):
        self.result = 0
""" * 3  # Make it long enough

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "code"
        assert isinstance(ui, UICode)
        assert ui.language == "python"

    def test_dict_with_message_severity(self):
        """Test dict with message/severity → Alert."""
        data = {
            "message": "Operation successful!",
            "severity": "success",
            "title": "Success",
        }

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "alert"
        assert isinstance(ui, UIAlert)
        assert ui.message == "Operation successful!"
        assert ui.severity == "success"

    def test_dict_with_percent(self):
        """Test dict with percent → Progress."""
        data = {
            "message": "Processing...",
            "percent": 65,
        }

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "progress"
        assert isinstance(ui, UIProgress)
        assert ui.percent == 65

    def test_dict_with_label_options(self):
        """Test dict with label/options → Select."""
        data = {
            "label": "Choose environment",
            "options": ["dev", "staging", "prod"],
            "default": "staging",
        }

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "select"
        assert isinstance(ui, UISelect)
        assert ui.options == ["dev", "staging", "prod"]

    def test_large_dict_to_json_code(self):
        """Test large dict → JSON code block."""
        data = {
            "user": "alice",
            "email": "alice@example.com",
            "settings": {"theme": "dark", "notifications": True},
            "permissions": ["read", "write"],
        }

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "code"
        assert isinstance(ui, UICode)
        assert ui.language == "json"
        assert "alice" in ui.code

    def test_ui_primitive_passthrough(self):
        """Test UI primitives are returned as-is."""
        original = UITable(columns=["A"], rows=[["1"]])

        component_type, ui = ComponentSelector.select_component(original)

        assert component_type == "ui_primitive"
        assert ui is original  # Same instance

    def test_markdown_detection(self):
        """Test markdown content detection."""
        data = """
# My Heading

This is a **bold** paragraph with *italic* text.

- Item 1
- Item 2
- Item 3

```python
print("code block")
```

[Link](https://example.com)
"""

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "markdown"
        assert isinstance(ui, UIMarkdown)

    def test_component_override_with_key(self):
        """Test _component override key."""
        data = {
            "_component": "code",
            "_language": "yaml",
            "data": "config:\n  debug: true",
        }

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "code"
        assert isinstance(ui, UICode)
        assert ui.language == "yaml"

    def test_boolean_to_text(self):
        """Test boolean → Text."""
        component_type, ui = ComponentSelector.select_component(True)

        assert component_type == "text"
        assert isinstance(ui, UIText)
        assert ui.content == "True"


class TestLanguageDetection:
    """Test programming language detection."""

    def test_detect_python(self):
        """Test Python detection."""
        code = "def hello():\n    import sys\n    class Foo:\n        pass"
        lang = ComponentSelector._detect_language(code)
        assert lang == "python"

    def test_detect_javascript(self):
        """Test JavaScript detection."""
        code = "function hello() {\n    const x = 10;\n    let y = () => {};\n}"
        lang = ComponentSelector._detect_language(code)
        assert lang == "javascript"

    def test_detect_go(self):
        """Test Go detection."""
        code = "package main\n\nfunc main() {\n    type User struct {}\n}"
        lang = ComponentSelector._detect_language(code)
        assert lang == "go"

    def test_detect_json(self):
        """Test JSON detection."""
        code = '{\n  "name": "test",\n  "value": 123\n}'
        lang = ComponentSelector._detect_language(code)
        assert lang == "json"

    def test_detect_yaml(self):
        """Test YAML detection."""
        code = "name: test\nvalue: 123\nlist:\n  - item1\n  - item2"
        lang = ComponentSelector._detect_language(code)
        assert lang == "yaml"

    def test_detect_sql(self):
        """Test SQL detection."""
        code = "SELECT * FROM users WHERE id = 1"
        lang = ComponentSelector._detect_language(code)
        assert lang == "sql"

    def test_detect_bash(self):
        """Test Bash detection."""
        code = "#!/bin/bash\necho ${USER}\nls -la"
        lang = ComponentSelector._detect_language(code)
        assert lang == "bash"

    def test_unknown_defaults_to_text(self):
        """Test unknown language defaults to text."""
        code = "some random content without patterns"
        lang = ComponentSelector._detect_language(code)
        assert lang == "text"


class TestLargeDatasets:
    """Test handling of large datasets."""

    def test_large_list_truncation(self):
        """Test large lists are truncated with footer."""
        data = [{"id": i, "name": f"Item {i}"} for i in range(100)]

        component_type, ui = ComponentSelector.select_component(data)

        assert component_type == "table"
        assert isinstance(ui, UITable)
        assert len(ui.rows) == 50  # Truncated to 50
        assert ui.footer is not None
        assert "50 of 100" in ui.footer


@pytest.mark.asyncio
async def test_integration_with_tool_execution():
    """Test ComponentSelector integration in tool execution."""
    core = AgentCore()

    # Register a test tool that returns plain data
    def get_users():
        return [
            {"name": "Alice", "role": "admin"},
            {"name": "Bob", "role": "user"},
        ]

    core.register_tool(ToolDefinition(
        name="get_users",
        description="Get user list",
        parameters={"type": "object", "properties": {}},
        handler=get_users,
    ))

    # Execute tool
    result = await core.execute_tool("get_users", "test-id", {})

    # Verify auto-selection occurred
    assert result.is_ui is True
    assert isinstance(result.result, UITable)
    assert result.result.columns == ["name", "role"]
    assert len(result.result.rows) == 2


@pytest.mark.asyncio
async def test_integration_with_ui_primitive_return():
    """Test that explicit UI primitive returns are not modified."""
    core = AgentCore()

    # Register a test tool that returns explicit UI primitive
    def get_status():
        return UIAlert(
            message="System healthy",
            severity="success",
        )

    core.register_tool(ToolDefinition(
        name="get_status",
        description="Get system status",
        parameters={"type": "object", "properties": {}},
        handler=get_status,
    ))

    # Execute tool
    result = await core.execute_tool("get_status", "test-id", {})

    # Verify primitive is unchanged
    assert result.is_ui is True
    assert isinstance(result.result, UIAlert)
    assert result.result.message == "System healthy"


def test_phase2_success_criteria():
    """Verify all Phase 2 success criteria are met."""
    # ✅ Tools can return plain data structures
    data = [{"a": 1}, {"a": 2}]
    component_type, ui = ComponentSelector.select_component(data)
    assert component_type == "table"

    # ✅ Backward compatible with explicit UI primitives
    explicit_ui = UITable(columns=["X"], rows=[["1"]])
    component_type, ui = ComponentSelector.select_component(explicit_ui)
    assert component_type == "ui_primitive"
    assert ui is explicit_ui

    # ✅ Override mechanism available (_component key)
    override_data = {"_component": "code", "_language": "json", "data": "test"}
    component_type, ui = ComponentSelector.select_component(override_data)
    assert component_type == "code"

    print("✅ Phase 2 Success Criteria Met:")
    print("  - Tools can return plain data")
    print("  - Backward compatible with UI primitives")
    print("  - Override mechanism works")
    print("  - Component selection heuristics functional")


def test_component_selection_accuracy():
    """Test overall component selection accuracy on diverse inputs."""
    test_cases = [
        # (input, expected_type)
        ([{"name": "A"}], "table"),
        ("def x(): pass\n" * 10, "code"),
        ({"percent": 50}, "progress"),
        ({"message": "Hi", "severity": "info"}, "alert"),
        ({"label": "Pick", "options": ["a", "b"]}, "select"),
        (True, "text"),
        (123, "text"),
        ("# Header\n\n**bold**", "markdown"),
        ({"a": 1, "b": 2, "c": 3, "d": 4}, "code"),  # Large dict → JSON
    ]

    correct = 0
    for data, expected in test_cases:
        actual, _ = ComponentSelector.select_component(data)
        if actual == expected:
            correct += 1
        else:
            print(f"MISS: {data} → {actual} (expected {expected})")

    accuracy = correct / len(test_cases)
    assert accuracy >= 0.9, f"Selection accuracy {accuracy:.1%} below 90% threshold"

    print(f"✅ Component Selection Accuracy: {accuracy:.1%} ({correct}/{len(test_cases)})")
