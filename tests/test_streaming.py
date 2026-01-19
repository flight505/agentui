"""
Tests for progressive UI streaming (streaming.py).

Tests UIStream class for multi-phase rendering and @streaming_tool decorator.
"""

import pytest
from unittest.mock import Mock, AsyncMock
import uuid

from agentui.streaming import UIStream, streaming_tool
from agentui.primitives import UITable, UICode, UIProgress, UIAlert


class TestUIStreamInitialization:
    """Test UIStream initialization."""

    def test_initialization_with_bridge(self):
        """Test UIStream initializes with bridge."""
        bridge = Mock()
        stream = UIStream(bridge)

        assert stream.bridge is bridge
        assert stream.component_id is not None
        assert isinstance(stream.component_id, str)
        assert stream._current_type is None

    def test_initialization_without_bridge(self):
        """Test UIStream initializes without bridge (None)."""
        stream = UIStream(None)

        assert stream.bridge is None
        assert stream.component_id is not None
        assert stream._current_type is None

    def test_component_id_is_uuid(self):
        """Test component_id is a valid UUID."""
        stream = UIStream(Mock())

        # Should be valid UUID
        try:
            uuid.UUID(stream.component_id)
        except ValueError:
            pytest.fail("component_id is not a valid UUID")

    def test_unique_component_ids(self):
        """Test each stream gets unique component ID."""
        stream1 = UIStream(Mock())
        stream2 = UIStream(Mock())

        assert stream1.component_id != stream2.component_id


class TestUIStreamProgress:
    """Test UIStream progress updates."""

    @pytest.mark.asyncio
    async def test_send_progress_initial(self):
        """Test sending initial progress (creates new component)."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        await stream.send_progress("Loading...", 50.0)

        bridge.send_progress.assert_called_once_with(
            message="Loading...",
            percent=50.0,
            steps=None,
        )
        assert stream._current_type == "progress"

    @pytest.mark.asyncio
    async def test_send_progress_with_steps(self):
        """Test sending progress with multi-step configuration."""
        bridge = AsyncMock()
        stream = UIStream(bridge)
        steps = [{"label": "Step 1", "status": "complete"}]

        await stream.send_progress("Processing...", None, steps)

        bridge.send_progress.assert_called_once_with(
            message="Processing...",
            percent=None,
            steps=steps,
        )

    @pytest.mark.asyncio
    async def test_send_progress_update(self):
        """Test updating existing progress component."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        # Initial progress
        await stream.send_progress("Loading...", 0.0)
        # Update progress
        await stream.send_progress("Still loading...", 75.0)

        # Second call should use UPDATE message
        assert bridge.send_message.call_count == 1
        call_args = bridge.send_message.call_args
        assert call_args[0][0].value == "update"  # MessageType.UPDATE

    @pytest.mark.asyncio
    async def test_send_progress_no_bridge(self):
        """Test send_progress with no bridge (graceful no-op)."""
        stream = UIStream(None)

        # Should not raise
        await stream.send_progress("Loading...", 50.0)

    @pytest.mark.asyncio
    async def test_send_progress_bridge_error(self):
        """Test send_progress handles bridge errors gracefully."""
        from agentui.bridge import BridgeError

        bridge = AsyncMock()
        bridge.send_progress.side_effect = BridgeError("Bridge error")
        stream = UIStream(bridge)

        # Should not raise (catches BridgeError)
        await stream.send_progress("Loading...", 50.0)


class TestUIStreamTable:
    """Test UIStream table updates."""

    @pytest.mark.asyncio
    async def test_send_table_initial(self):
        """Test sending initial table (creates new component)."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        await stream.send_table(["Name"], [["Alice"]], title="Users")

        bridge.send_table.assert_called_once_with(
            columns=["Name"],
            rows=[["Alice"]],
            title="Users",
            footer=None,
        )
        assert stream._current_type == "table"

    @pytest.mark.asyncio
    async def test_send_table_with_footer(self):
        """Test sending table with title and footer."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        await stream.send_table(
            ["Col1", "Col2"],
            [["A", "B"], ["C", "D"]],
            title="Data",
            footer="Total: 2 rows",
        )

        bridge.send_table.assert_called_once()
        call_kwargs = bridge.send_table.call_args[1]
        assert call_kwargs["title"] == "Data"
        assert call_kwargs["footer"] == "Total: 2 rows"

    @pytest.mark.asyncio
    async def test_send_table_update(self):
        """Test updating existing table component."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        # Initial table
        await stream.send_table(["Name"], [["Alice"]])
        # Update table
        await stream.send_table(["Name"], [["Alice"], ["Bob"]])

        # Second call should use UPDATE message
        assert bridge.send_message.call_count == 1

    @pytest.mark.asyncio
    async def test_send_table_no_bridge(self):
        """Test send_table with no bridge (graceful no-op)."""
        stream = UIStream(None)

        await stream.send_table(["Col"], [["Val"]])

    @pytest.mark.asyncio
    async def test_send_table_bridge_error(self):
        """Test send_table handles bridge errors gracefully."""
        from agentui.bridge import BridgeError

        bridge = AsyncMock()
        bridge.send_table.side_effect = BridgeError("Bridge error")
        stream = UIStream(bridge)

        await stream.send_table(["Col"], [["Val"]])


class TestUIStreamCode:
    """Test UIStream code updates."""

    @pytest.mark.asyncio
    async def test_send_code_initial(self):
        """Test sending initial code (creates new component)."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        await stream.send_code("def hello(): pass", "python", "Example")

        bridge.send_code.assert_called_once_with(
            code="def hello(): pass",
            language="python",
            title="Example",
        )
        assert stream._current_type == "code"

    @pytest.mark.asyncio
    async def test_send_code_default_language(self):
        """Test sending code with default language (text)."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        await stream.send_code("Some text")

        call_kwargs = bridge.send_code.call_args[1]
        assert call_kwargs["language"] == "text"

    @pytest.mark.asyncio
    async def test_send_code_update(self):
        """Test updating existing code component."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        # Initial code
        await stream.send_code("x = 1", "python")
        # Update code
        await stream.send_code("x = 1\ny = 2", "python")

        # Second call should use UPDATE message
        assert bridge.send_message.call_count == 1

    @pytest.mark.asyncio
    async def test_send_code_no_bridge(self):
        """Test send_code with no bridge (graceful no-op)."""
        stream = UIStream(None)

        await stream.send_code("code", "python")

    @pytest.mark.asyncio
    async def test_send_code_bridge_error(self):
        """Test send_code handles bridge errors gracefully."""
        from agentui.bridge import BridgeError

        bridge = AsyncMock()
        bridge.send_code.side_effect = BridgeError("Bridge error")
        stream = UIStream(bridge)

        await stream.send_code("code", "python")


class TestUIStreamAlert:
    """Test UIStream alert updates."""

    @pytest.mark.asyncio
    async def test_send_alert_initial(self):
        """Test sending initial alert (creates new component)."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        await stream.send_alert("Success!", "success", "Done")

        bridge.send_alert.assert_called_once_with(
            message="Success!",
            severity="success",
            title="Done",
        )
        assert stream._current_type == "alert"

    @pytest.mark.asyncio
    async def test_send_alert_default_severity(self):
        """Test sending alert with default severity (info)."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        await stream.send_alert("Information")

        call_kwargs = bridge.send_alert.call_args[1]
        assert call_kwargs["severity"] == "info"

    @pytest.mark.asyncio
    async def test_send_alert_all_severities(self):
        """Test all alert severity levels."""
        bridge = AsyncMock()

        for severity in ["info", "success", "warning", "error"]:
            stream = UIStream(bridge)
            await stream.send_alert("Message", severity)

            call_kwargs = bridge.send_alert.call_args[1]
            assert call_kwargs["severity"] == severity
            bridge.reset_mock()

    @pytest.mark.asyncio
    async def test_send_alert_update(self):
        """Test updating existing alert component."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        # Initial alert
        await stream.send_alert("Processing...", "info")
        # Update alert
        await stream.send_alert("Done!", "success")

        # Second call should use UPDATE message
        assert bridge.send_message.call_count == 1

    @pytest.mark.asyncio
    async def test_send_alert_no_bridge(self):
        """Test send_alert with no bridge (graceful no-op)."""
        stream = UIStream(None)

        await stream.send_alert("Message", "info")

    @pytest.mark.asyncio
    async def test_send_alert_bridge_error(self):
        """Test send_alert handles bridge errors gracefully."""
        from agentui.bridge import BridgeError

        bridge = AsyncMock()
        bridge.send_alert.side_effect = BridgeError("Bridge error")
        stream = UIStream(bridge)

        await stream.send_alert("Message", "info")


class TestUIStreamFinalize:
    """Test UIStream finalize methods."""

    def test_finalize_table(self):
        """Test finalizing stream as table primitive."""
        stream = UIStream(Mock())

        result = stream.finalize_table(
            ["Col1", "Col2"],
            [["A", "B"], ["C", "D"]],
            title="Data",
            footer="Total",
        )

        assert isinstance(result, UITable)
        assert result.columns == ["Col1", "Col2"]
        assert result.rows == [["A", "B"], ["C", "D"]]
        assert result.title == "Data"
        assert result.footer == "Total"

    def test_finalize_table_minimal(self):
        """Test finalizing table with minimal parameters."""
        stream = UIStream(Mock())

        result = stream.finalize_table(["Name"], [["Alice"]])

        assert isinstance(result, UITable)
        assert result.columns == ["Name"]
        assert result.rows == [["Alice"]]
        assert result.title is None
        assert result.footer is None

    def test_finalize_code(self):
        """Test finalizing stream as code primitive."""
        stream = UIStream(Mock())

        result = stream.finalize_code(
            "def hello(): pass",
            "python",
            "Example Function",
        )

        assert isinstance(result, UICode)
        assert result.code == "def hello(): pass"
        assert result.language == "python"
        assert result.title == "Example Function"

    def test_finalize_code_default_language(self):
        """Test finalizing code with default language."""
        stream = UIStream(Mock())

        result = stream.finalize_code("Some text")

        assert isinstance(result, UICode)
        assert result.language == "text"
        assert result.title is None

    def test_finalize_progress(self):
        """Test finalizing stream as progress primitive."""
        stream = UIStream(Mock())

        result = stream.finalize_progress("Done", 100.0)

        assert isinstance(result, UIProgress)
        assert result.message == "Done"
        assert result.percent == 100.0
        assert result.steps is None

    def test_finalize_progress_with_steps(self):
        """Test finalizing progress with steps."""
        from agentui.primitives import UIProgressStep
        stream = UIStream(Mock())
        steps = [{"label": "Step 1", "status": "complete"}]

        result = stream.finalize_progress("Processing", None, steps)

        assert isinstance(result, UIProgress)
        assert len(result.steps) == 1
        assert isinstance(result.steps[0], UIProgressStep)
        assert result.steps[0].label == "Step 1"
        assert result.steps[0].status == "complete"

    def test_finalize_alert(self):
        """Test finalizing stream as alert primitive."""
        stream = UIStream(Mock())

        result = stream.finalize_alert("Success!", "success", "Done")

        assert isinstance(result, UIAlert)
        assert result.message == "Success!"
        assert result.severity == "success"
        assert result.title == "Done"

    def test_finalize_alert_default_severity(self):
        """Test finalizing alert with default severity."""
        stream = UIStream(Mock())

        result = stream.finalize_alert("Info message")

        assert isinstance(result, UIAlert)
        assert result.severity == "info"
        assert result.title is None


class TestStreamingToolDecorator:
    """Test @streaming_tool decorator."""

    def test_decorator_marks_function(self):
        """Test decorator sets _is_streaming flag."""

        @streaming_tool
        async def test_func():
            return "result"

        assert hasattr(test_func, "_is_streaming")
        assert test_func._is_streaming is True

    def test_decorator_preserves_function(self):
        """Test decorator preserves original function."""

        async def original():
            return "value"

        decorated = streaming_tool(original)

        assert decorated.__name__ == "original"
        assert decorated._is_streaming is True

    @pytest.mark.asyncio
    async def test_decorated_function_callable(self):
        """Test decorated function is still callable."""

        @streaming_tool
        async def compute():
            return 42

        result = await compute()
        assert result == 42

    def test_decorator_on_multiple_functions(self):
        """Test decorator can be applied to multiple functions."""

        @streaming_tool
        async def func1():
            pass

        @streaming_tool
        async def func2():
            pass

        assert func1._is_streaming is True
        assert func2._is_streaming is True


class TestUIStreamIntegration:
    """Integration tests for realistic streaming workflows."""

    @pytest.mark.asyncio
    async def test_progressive_rendering_workflow(self):
        """Test realistic progressive rendering: progress -> update -> finalize."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        # Phase 1: Show initial progress
        await stream.send_progress("Analyzing...", 0.0)
        assert stream._current_type == "progress"

        # Phase 2: Update progress
        await stream.send_progress("Processing...", 50.0)
        # Type remains the same, uses UPDATE message
        assert stream._current_type == "progress"

        # Phase 3: Update with more progress
        await stream.send_progress("Almost done...", 90.0)

        # Phase 4: Finalize as table
        result = stream.finalize_table(
            ["File", "Lines"],
            [["test.py", "100"], ["main.py", "200"]],
        )

        assert isinstance(result, UITable)
        assert len(result.rows) == 2

    @pytest.mark.asyncio
    async def test_code_streaming_workflow(self):
        """Test code streaming: progress -> code -> finalize."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        # Phase 1: Loading
        await stream.send_progress("Generating code...", 0.0)

        # Phase 2: Partial code
        await stream.send_code("def hello():", "python")

        # Phase 3: Complete code
        result = stream.finalize_code(
            "def hello():\n    print('Hello')",
            "python",
            "Generated Function",
        )

        assert isinstance(result, UICode)
        assert "print" in result.code

    @pytest.mark.asyncio
    async def test_alert_workflow(self):
        """Test alert workflow: progress -> alert -> finalize."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        # Show progress
        await stream.send_progress("Validating...", 50.0)

        # Show alert
        await stream.send_alert("Validation complete", "success")

        # Finalize
        result = stream.finalize_alert("All checks passed", "success", "Done")

        assert isinstance(result, UIAlert)
        assert result.severity == "success"

    @pytest.mark.asyncio
    async def test_component_id_consistency(self):
        """Test component_id remains consistent throughout stream lifecycle."""
        bridge = AsyncMock()
        stream = UIStream(bridge)

        original_id = stream.component_id

        await stream.send_progress("Step 1", 25.0)
        assert stream.component_id == original_id

        await stream.send_table(["A"], [["1"]])
        assert stream.component_id == original_id

        await stream.send_code("code", "text")
        assert stream.component_id == original_id
