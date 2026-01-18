"""
Phase 5: Multi-Component Layouts - Test Suite

Tests for dashboard-style multi-component layouts.
"""

import pytest
from agentui.layout import UILayout, LayoutComponent
from agentui.protocol import MessageType, layout_payload


class TestUILayout:
    """Test UILayout class for multi-component compositions."""

    def test_layout_creation(self):
        """Test basic layout creation."""
        layout = UILayout(title="Dashboard", description="System overview")

        assert layout.title == "Dashboard"
        assert layout.description == "System overview"
        assert len(layout.components) == 0

    def test_add_table_component(self):
        """Test adding table to layout."""
        layout = UILayout()
        layout.add_table(
            columns=["Service", "Status"],
            rows=[["API", "Running"], ["DB", "Running"]],
            title="Services",
            area="left"
        )

        assert len(layout.components) == 1
        comp = layout.components[0]
        assert comp.type == "table"
        assert comp.area == "left"
        assert comp.payload["columns"] == ["Service", "Status"]
        assert comp.payload["title"] == "Services"

    def test_add_code_component(self):
        """Test adding code block to layout."""
        layout = UILayout()
        layout.add_code(
            code="def hello(): pass",
            language="python",
            title="Example",
            area="right"
        )

        assert len(layout.components) == 1
        comp = layout.components[0]
        assert comp.type == "code"
        assert comp.area == "right"
        assert comp.payload["code"] == "def hello(): pass"
        assert comp.payload["language"] == "python"

    def test_add_progress_component(self):
        """Test adding progress indicator to layout."""
        layout = UILayout()
        layout.add_progress(
            message="Processing...",
            percent=75.0,
            area="top"
        )

        assert len(layout.components) == 1
        comp = layout.components[0]
        assert comp.type == "progress"
        assert comp.area == "top"
        assert comp.payload["message"] == "Processing..."
        assert comp.payload["percent"] == 75.0

    def test_add_alert_component(self):
        """Test adding alert to layout."""
        layout = UILayout()
        layout.add_alert(
            message="Warning!",
            severity="warning",
            title="Alert",
            area="bottom"
        )

        assert len(layout.components) == 1
        comp = layout.components[0]
        assert comp.type == "alert"
        assert comp.area == "bottom"
        assert comp.payload["message"] == "Warning!"
        assert comp.payload["severity"] == "warning"

    def test_add_generic_component(self):
        """Test adding generic component to layout."""
        layout = UILayout()
        layout.add_component(
            component_type="custom",
            payload={"data": "value"},
            area="center",
            width=50,
            height=20
        )

        assert len(layout.components) == 1
        comp = layout.components[0]
        assert comp.type == "custom"
        assert comp.area == "center"
        assert comp.width == 50
        assert comp.height == 20

    def test_layout_chaining(self):
        """Test method chaining for layout building."""
        layout = (
            UILayout(title="System Dashboard")
            .add_table(["Name"], [["Test"]], area="left")
            .add_code("code", "python", area="right")
            .add_progress("Loading...", 50, area="bottom")
        )

        assert len(layout.components) == 3
        assert layout.components[0].type == "table"
        assert layout.components[1].type == "code"
        assert layout.components[2].type == "progress"

    def test_layout_to_dict(self):
        """Test layout serialization to dict."""
        layout = UILayout(title="Dashboard", description="Overview")
        layout.add_table(["A"], [["1"]], area="left")
        layout.add_code("test", "text", area="right")

        result = layout.to_dict()

        assert result["title"] == "Dashboard"
        assert result["description"] == "Overview"
        assert len(result["components"]) == 2

        # Check first component
        comp1 = result["components"][0]
        assert comp1["type"] == "table"
        assert comp1["area"] == "left"
        assert "payload" in comp1

        # Check second component
        comp2 = result["components"][1]
        assert comp2["type"] == "code"
        assert comp2["area"] == "right"

    def test_layout_component_dataclass(self):
        """Test LayoutComponent dataclass."""
        comp = LayoutComponent(
            type="table",
            payload={"columns": ["A"], "rows": [["1"]]},
            area="left",
            width=50,
            height=30
        )

        assert comp.type == "table"
        assert comp.payload["columns"] == ["A"]
        assert comp.area == "left"
        assert comp.width == 50
        assert comp.height == 30

    def test_layout_component_optional_fields(self):
        """Test LayoutComponent with optional fields."""
        comp = LayoutComponent(
            type="code",
            payload={"code": "test"}
        )

        assert comp.type == "code"
        assert comp.area is None
        assert comp.width is None
        assert comp.height is None

    def test_complex_dashboard_layout(self):
        """Test complex dashboard with multiple components."""
        layout = UILayout(title="System Monitor")

        # Left: Service table
        layout.add_table(
            columns=["Service", "Status", "Uptime"],
            rows=[
                ["API", "✓", "99.9%"],
                ["DB", "✓", "100%"],
                ["Cache", "✓", "98.5%"]
            ],
            title="Services",
            area="left"
        )

        # Right top: CPU usage
        layout.add_progress(
            message="CPU Usage",
            percent=65.0,
            area="right-top"
        )

        # Right middle: Memory usage
        layout.add_progress(
            message="Memory Usage",
            percent=78.0,
            area="right-middle"
        )

        # Right bottom: Config
        layout.add_code(
            code='{"timeout": 30, "retries": 3}',
            language="json",
            title="Configuration",
            area="right-bottom"
        )

        # Bottom: Alert
        layout.add_alert(
            message="All systems operational",
            severity="success",
            area="bottom"
        )

        assert len(layout.components) == 5

        # Verify component types
        types = [c.type for c in layout.components]
        assert types == ["table", "progress", "progress", "code", "alert"]

        # Verify areas
        areas = [c.area for c in layout.components]
        assert areas == ["left", "right-top", "right-middle", "right-bottom", "bottom"]


class TestLayoutProtocol:
    """Test layout protocol integration."""

    def test_layout_payload_minimal(self):
        """Test layout payload with minimal fields."""
        payload = layout_payload()

        assert payload == {}

    def test_layout_payload_with_title(self):
        """Test layout payload with title."""
        payload = layout_payload(title="Dashboard")

        assert payload["title"] == "Dashboard"
        assert "description" not in payload
        assert "components" not in payload

    def test_layout_payload_with_components(self):
        """Test layout payload with components."""
        components = [
            {"type": "table", "payload": {"columns": ["A"], "rows": [["1"]]}},
            {"type": "code", "payload": {"code": "test", "language": "text"}}
        ]

        payload = layout_payload(
            title="Dashboard",
            description="Overview",
            components=components
        )

        assert payload["title"] == "Dashboard"
        assert payload["description"] == "Overview"
        assert len(payload["components"]) == 2

    def test_layout_integration_with_uilayout(self):
        """Test UILayout to_dict integration with layout_payload."""
        layout = UILayout(title="Test Dashboard")
        layout.add_table(["Name"], [["Alice"]], area="left")
        layout.add_code("code", "python", area="right")

        # Convert layout to dict
        layout_dict = layout.to_dict()

        # Create payload from dict
        payload = layout_payload(
            title=layout_dict["title"],
            description=layout_dict["description"],
            components=layout_dict["components"]
        )

        assert payload["title"] == "Test Dashboard"
        assert len(payload["components"]) == 2

    def test_layout_message_type_exists(self):
        """Test that LAYOUT message type exists in protocol."""
        assert hasattr(MessageType, "LAYOUT")
        assert MessageType.LAYOUT == "layout"


class TestLayoutEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_layout(self):
        """Test layout with no components."""
        layout = UILayout()

        result = layout.to_dict()

        assert result["title"] is None
        assert result["description"] is None
        assert result["components"] == []

    def test_layout_only_title(self):
        """Test layout with only title, no components."""
        layout = UILayout(title="Empty Dashboard")

        result = layout.to_dict()

        assert result["title"] == "Empty Dashboard"
        assert len(result["components"]) == 0

    def test_layout_repr(self):
        """Test layout string representation."""
        layout = UILayout(title="Dashboard")
        layout.add_table(["A"], [["1"]])

        repr_str = repr(layout)

        assert "UILayout" in repr_str
        assert "Dashboard" in repr_str
        assert "1" in repr_str  # component count

    def test_component_without_area(self):
        """Test component without area hint."""
        layout = UILayout()
        layout.add_table(["A"], [["1"]])  # No area specified

        comp = layout.components[0]
        assert comp.area is None

    def test_component_with_size_hints(self):
        """Test component with width/height hints."""
        layout = UILayout()
        layout.add_table(
            ["A"], [["1"]],
            width=80,
            height=20
        )

        comp = layout.components[0]
        assert comp.width == 80
        assert comp.height == 20


# Success criteria check
def test_phase5_success_criteria():
    """Verify Phase 5 meets all success criteria."""

    # ✅ UILayout class exists and is usable
    layout = UILayout(title="Test")
    assert layout is not None

    # ✅ Can add multiple component types
    layout.add_table(["A"], [["1"]], area="left")
    layout.add_code("code", "python", area="right")
    layout.add_progress("Loading", 50, area="top")
    layout.add_alert("Info", "info", area="bottom")
    assert len(layout.components) == 4

    # ✅ Method chaining works
    chained_layout = (
        UILayout(title="Chained")
        .add_table(["A"], [["1"]])
        .add_code("test", "text")
    )
    assert len(chained_layout.components) == 2

    # ✅ Serialization to dict works
    layout_dict = layout.to_dict()
    assert "components" in layout_dict
    assert len(layout_dict["components"]) == 4

    # ✅ LAYOUT message type exists in protocol
    assert MessageType.LAYOUT == "layout"

    # ✅ layout_payload helper exists
    payload = layout_payload(title="Test", components=[])
    assert "title" in payload

    print("✅ Phase 5 success criteria met!")
