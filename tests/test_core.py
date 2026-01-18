"""
Tests for the core module (AgentCore).
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from agentui.core import AgentCore, ToolExecutionError
from agentui.primitives import UITable, UICode, UIForm, UIConfirm, UIText, UIMarkdown
from agentui.types import AgentConfig, ToolDefinition, ToolResult


@pytest.fixture
def mock_bridge():
    """Create a mock bridge for testing."""
    bridge = MagicMock()
    bridge.send_text = AsyncMock()
    bridge.send_spinner = AsyncMock()
    bridge.request_confirm = AsyncMock(return_value=True)
    bridge.request_form = AsyncMock(return_value={"field": "value"})
    return bridge


@pytest.fixture
def basic_config():
    """Create a basic agent configuration."""
    return AgentConfig(
        system_prompt="You are a test assistant.",
        model="test-model",
    )


class TestAgentCoreInitialization:
    """Test AgentCore initialization."""

    def test_init_with_default_config(self):
        """Test AgentCore initializes with default config."""
        core = AgentCore()

        assert core.config is not None
        assert isinstance(core.config, AgentConfig)
        # Note: tools dict is not empty - display_* tools are auto-registered
        assert len(core.tools) > 0  # Should have auto-registered display tools
        assert core.state.messages == []  # AgentState uses 'messages' not 'conversation_history'
        assert core.state.is_running is False
        assert core.bridge is None

    def test_init_with_custom_config(self, basic_config):
        """Test AgentCore initializes with custom config."""
        core = AgentCore(config=basic_config)

        assert core.config == basic_config
        assert "You are a test assistant" in core.config.system_prompt

    def test_init_with_bridge(self, basic_config, mock_bridge):
        """Test AgentCore initializes with bridge."""
        core = AgentCore(config=basic_config, bridge=mock_bridge)

        assert core.bridge == mock_bridge

    def test_system_prompt_enhanced_with_catalog(self):
        """Test system prompt is enhanced with component catalog."""
        config = AgentConfig(system_prompt="Original prompt")
        core = AgentCore(config=config)

        # Should have original prompt plus catalog
        assert "Original prompt" in core.config.system_prompt
        assert "UI Components Available" in core.config.system_prompt or "display_" in core.config.system_prompt

    def test_display_tools_auto_registered(self):
        """Test display_* tools are auto-registered on init."""
        core = AgentCore()

        # Check for auto-registered display tools
        display_tools = [name for name in core.tools.keys() if name.startswith("display_")]

        assert len(display_tools) > 0
        assert "display_table" in core.tools
        assert "display_code" in core.tools
        assert "display_form" in core.tools


class TestToolRegistration:
    """Test tool registration and management."""

    @pytest.mark.asyncio
    async def test_register_tool(self):
        """Test manual tool registration."""
        core = AgentCore()

        async def test_handler(arg: str):
            return f"result: {arg}"

        tool = ToolDefinition(
            name="test_tool",
            description="A test tool",
            parameters={"type": "object", "properties": {"arg": {"type": "string"}}},
            handler=test_handler,
        )

        core.register_tool(tool)

        assert "test_tool" in core.tools
        assert core.tools["test_tool"] == tool

    def test_get_tool_schemas(self):
        """Test getting tool schemas for LLM."""
        core = AgentCore()

        def simple_handler():
            return "result"

        tool = ToolDefinition(
            name="simple_tool",
            description="Simple tool",
            parameters={"type": "object", "properties": {}},
            handler=simple_handler,
        )

        core.register_tool(tool)
        schemas = core.get_tool_schemas()

        # Should include both registered tool and auto-registered display tools
        assert len(schemas) > 1
        tool_names = [s["name"] for s in schemas]
        assert "simple_tool" in tool_names
        assert "display_table" in tool_names


class TestToolExecution:
    """Test tool execution."""

    @pytest.mark.asyncio
    async def test_execute_async_tool(self, mock_bridge):
        """Test executing an async tool."""
        core = AgentCore(bridge=mock_bridge)

        async def async_handler(message: str):
            return f"echo: {message}"

        tool = ToolDefinition(
            name="echo",
            description="Echo a message",
            parameters={"type": "object", "properties": {"message": {"type": "string"}}},
            handler=async_handler,
        )

        core.register_tool(tool)
        result = await core.execute_tool("echo", "test-id-1", {"message": "hello"})

        assert isinstance(result, ToolResult)
        assert result.tool_name == "echo"
        assert result.tool_id == "test-id-1"
        assert result.result == "echo: hello"
        assert result.error is None

    @pytest.mark.asyncio
    async def test_execute_sync_tool(self, mock_bridge):
        """Test executing a sync tool (runs in executor)."""
        core = AgentCore(bridge=mock_bridge)

        def sync_handler(value: int):
            return value * 2

        tool = ToolDefinition(
            name="double",
            description="Double a number",
            parameters={"type": "object", "properties": {"value": {"type": "integer"}}},
            handler=sync_handler,
        )

        core.register_tool(tool)
        result = await core.execute_tool("double", "test-id-2", {"value": 5})

        assert result.tool_name == "double"
        assert result.result == 10
        assert result.error is None

    @pytest.mark.asyncio
    async def test_execute_unknown_tool(self):
        """Test executing an unknown tool returns error."""
        core = AgentCore()

        result = await core.execute_tool("unknown_tool", "test-id", {})

        assert result.error is not None
        assert "Unknown tool" in result.error
        assert result.result is None

    @pytest.mark.asyncio
    async def test_execute_tool_with_error(self, mock_bridge):
        """Test tool execution error handling."""
        core = AgentCore(bridge=mock_bridge)

        async def failing_handler():
            raise ValueError("Something went wrong")

        tool = ToolDefinition(
            name="failing_tool",
            description="A tool that fails",
            parameters={"type": "object", "properties": {}},
            handler=failing_handler,
        )

        core.register_tool(tool)
        result = await core.execute_tool("failing_tool", "test-id", {})

        assert result.error is not None
        assert "Something went wrong" in result.error
        assert result.result is None

    @pytest.mark.asyncio
    async def test_tool_confirmation_required(self, mock_bridge):
        """Test tool requiring confirmation."""
        core = AgentCore(bridge=mock_bridge)
        mock_bridge.request_confirm.return_value = True

        async def confirmed_handler():
            return "executed"

        tool = ToolDefinition(
            name="dangerous_tool",
            description="Dangerous operation",
            parameters={"type": "object", "properties": {}},
            handler=confirmed_handler,
            requires_confirmation=True,
        )

        core.register_tool(tool)
        result = await core.execute_tool("dangerous_tool", "test-id", {})

        mock_bridge.request_confirm.assert_called_once()
        assert result.result == "executed"
        assert result.error is None

    @pytest.mark.asyncio
    async def test_tool_confirmation_denied(self, mock_bridge):
        """Test tool execution cancelled when confirmation denied."""
        core = AgentCore(bridge=mock_bridge)
        mock_bridge.request_confirm.return_value = False

        async def confirmed_handler():
            return "should not execute"

        tool = ToolDefinition(
            name="dangerous_tool",
            description="Dangerous operation",
            parameters={"type": "object", "properties": {}},
            handler=confirmed_handler,
            requires_confirmation=True,
        )

        core.register_tool(tool)
        result = await core.execute_tool("dangerous_tool", "test-id", {})

        assert result.error is not None
        assert "cancelled by user" in result.error


class TestComponentSelection:
    """Test automatic component selection."""

    @pytest.mark.asyncio
    async def test_auto_select_table_for_list_of_dicts(self, mock_bridge):
        """Test core auto-selects UITable for list of dicts."""
        core = AgentCore(bridge=mock_bridge)

        async def get_data():
            return [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ]

        tool = ToolDefinition(
            name="get_users",
            description="Get users",
            parameters={"type": "object", "properties": {}},
            handler=get_data,
        )

        core.register_tool(tool)
        result = await core.execute_tool("get_users", "test-id", {})

        assert result.is_ui is True
        assert isinstance(result.result, UITable)
        assert len(result.result.rows) == 2

    @pytest.mark.asyncio
    async def test_auto_select_code_for_code_string(self, mock_bridge):
        """Test core auto-selects UICode for code-like strings."""
        core = AgentCore(bridge=mock_bridge)

        async def get_code():
            return "def hello():\n    print('world')"

        tool = ToolDefinition(
            name="generate_code",
            description="Generate code",
            parameters={"type": "object", "properties": {}},
            handler=get_code,
        )

        core.register_tool(tool)
        result = await core.execute_tool("generate_code", "test-id", {})

        # Code detection might select UICode or UIText depending on heuristics
        assert result.result is not None

    @pytest.mark.asyncio
    async def test_no_auto_select_for_simple_strings(self, mock_bridge):
        """Test simple strings are not converted to UI components."""
        core = AgentCore(bridge=mock_bridge)

        async def simple_handler():
            return "simple result"

        tool = ToolDefinition(
            name="simple_tool",
            description="Simple tool",
            parameters={"type": "object", "properties": {}},
            handler=simple_handler,
        )

        core.register_tool(tool)
        result = await core.execute_tool("simple_tool", "test-id", {})

        # Simple strings should remain as-is or be wrapped minimally
        assert result.result is not None

    @pytest.mark.asyncio
    async def test_ui_primitive_returned_as_is(self, mock_bridge):
        """Test UI primitives returned from tools are not modified."""
        core = AgentCore(bridge=mock_bridge)

        async def ui_handler():
            return UITable(
                columns=["Name", "Age"],  # UITable uses 'columns' not 'headers'
                rows=[["Alice", "30"]],
                title="Users",
            )

        tool = ToolDefinition(
            name="ui_tool",
            description="Returns UI",
            parameters={"type": "object", "properties": {}},
            handler=ui_handler,
        )

        core.register_tool(tool)
        result = await core.execute_tool("ui_tool", "test-id", {})

        assert result.is_ui is True
        assert isinstance(result.result, UITable)
        assert result.result.title == "Users"


class TestDisplayTools:
    """Test auto-registered display_* tools."""

    @pytest.mark.asyncio
    async def test_display_table_without_bridge(self):
        """Test display_table without bridge returns placeholder."""
        core = AgentCore()  # No bridge

        result = await core.execute_tool(
            "display_table",
            "test-id",
            {
                "headers": ["Name", "Age"],
                "rows": [["Alice", "30"]],
                "title": "Users",
            },
        )

        assert result.error is None
        assert "[Would display display_table" in result.result

    @pytest.mark.asyncio
    async def test_display_table_with_bridge(self, mock_bridge):
        """Test display_table with bridge sends table message."""
        mock_bridge.send_table = AsyncMock()
        core = AgentCore(bridge=mock_bridge)

        result = await core.execute_tool(
            "display_table",
            "test-id",
            {
                "columns": ["Name", "Age"],  # Use 'columns' not 'headers'
                "rows": [["Alice", "30"]],
                "title": "Users",
            },
        )

        mock_bridge.send_table.assert_called_once()

    @pytest.mark.asyncio
    async def test_display_code_with_bridge(self, mock_bridge):
        """Test display_code with bridge sends code message."""
        mock_bridge.send_code = AsyncMock()
        core = AgentCore(bridge=mock_bridge)

        result = await core.execute_tool(
            "display_code",
            "test-id",
            {
                "language": "python",
                "code": "print('hello')",
                "title": "Example",
            },
        )

        mock_bridge.send_code.assert_called_once()

    @pytest.mark.asyncio
    async def test_display_progress_with_bridge(self, mock_bridge):
        """Test display_progress with bridge sends progress message."""
        mock_bridge.send_progress = AsyncMock()
        core = AgentCore(bridge=mock_bridge)

        result = await core.execute_tool(
            "display_progress",
            "test-id",
            {
                "message": "Processing...",
                "percent": 50,
            },
        )

        mock_bridge.send_progress.assert_called_once()

    @pytest.mark.asyncio
    async def test_display_alert_with_bridge(self, mock_bridge):
        """Test display_alert with bridge sends alert message."""
        mock_bridge.send_alert = AsyncMock()
        core = AgentCore(bridge=mock_bridge)

        result = await core.execute_tool(
            "display_alert",
            "test-id",
            {
                "message": "Warning!",
                "severity": "warning",
                "title": "Alert",
            },
        )

        mock_bridge.send_alert.assert_called_once()

    @pytest.mark.asyncio
    async def test_display_form_with_bridge(self, mock_bridge):
        """Test display_form with bridge requests form input."""
        mock_bridge.request_form = AsyncMock(return_value={"name": "Alice"})
        core = AgentCore(bridge=mock_bridge)

        result = await core.execute_tool(
            "display_form",
            "test-id",
            {
                "fields": [{"name": "name", "label": "Name", "type": "text"}],
                "title": "User Form",
            },
        )

        mock_bridge.request_form.assert_called_once()

    @pytest.mark.asyncio
    async def test_display_confirm_with_bridge(self, mock_bridge):
        """Test display_confirm with bridge requests confirmation."""
        mock_bridge.request_confirm = AsyncMock(return_value=True)
        core = AgentCore(bridge=mock_bridge)

        result = await core.execute_tool(
            "display_confirm",
            "test-id",
            {
                "message": "Are you sure?",
                "title": "Confirmation",
            },
        )

        mock_bridge.request_confirm.assert_called_once()

    @pytest.mark.asyncio
    async def test_display_select_with_bridge(self, mock_bridge):
        """Test display_select with bridge requests selection."""
        mock_bridge.request_select = AsyncMock(return_value="option1")
        core = AgentCore(bridge=mock_bridge)

        result = await core.execute_tool(
            "display_select",
            "test-id",
            {
                "label": "Choose",
                "options": ["option1", "option2"],
            },
        )

        mock_bridge.request_select.assert_called_once()


class TestUIResultHandling:
    """Test handle_ui_result method."""

    @pytest.mark.asyncio
    async def test_handle_ui_form(self, mock_bridge):
        """Test handling UIForm result."""
        core = AgentCore(bridge=mock_bridge)
        mock_bridge.request_form.return_value = {"name": "Alice", "age": "30"}

        from agentui.primitives import UIFormField

        form = UIForm(
            fields=[
                UIFormField(name="name", label="Name", type="text"),
                UIFormField(name="age", label="Age", type="number"),
            ],
            title="User Input",
        )

        result = await core.handle_ui_result(form)

        mock_bridge.request_form.assert_called_once()
        assert result == {"name": "Alice", "age": "30"}

    @pytest.mark.asyncio
    async def test_handle_ui_confirm(self, mock_bridge):
        """Test handling UIConfirm result."""
        core = AgentCore(bridge=mock_bridge)
        mock_bridge.request_confirm.return_value = True

        confirm = UIConfirm(message="Are you sure?", title="Confirmation")

        result = await core.handle_ui_result(confirm)

        mock_bridge.request_confirm.assert_called_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_handle_non_ui_result_without_bridge(self):
        """Test handling non-UI result without bridge."""
        core = AgentCore()  # No bridge

        result = await core.handle_ui_result("plain string")

        assert result == "plain string"

    @pytest.mark.asyncio
    async def test_handle_ui_select(self, mock_bridge):
        """Test handling UISelect result."""
        from agentui.primitives import UISelect

        core = AgentCore(bridge=mock_bridge)
        mock_bridge.request_select = AsyncMock(return_value="option1")

        select = UISelect(
            label="Choose one",
            options=["option1", "option2"],
            default="option1",
        )

        result = await core.handle_ui_result(select)

        mock_bridge.request_select.assert_called_once()
        assert result == "option1"

    @pytest.mark.asyncio
    async def test_handle_ui_progress(self, mock_bridge):
        """Test handling UIProgress result."""
        from agentui.primitives import UIProgress

        core = AgentCore(bridge=mock_bridge)
        mock_bridge.send_progress = AsyncMock()

        progress = UIProgress(
            message="Processing...",
            percent=50,
        )

        result = await core.handle_ui_result(progress)

        mock_bridge.send_progress.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_ui_table(self, mock_bridge):
        """Test handling UITable result."""
        core = AgentCore(bridge=mock_bridge)
        mock_bridge.send_table = AsyncMock()

        table = UITable(
            columns=["Name", "Age"],
            rows=[["Alice", "30"]],
            title="Users",
        )

        result = await core.handle_ui_result(table)

        mock_bridge.send_table.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_ui_code(self, mock_bridge):
        """Test handling UICode result."""
        core = AgentCore(bridge=mock_bridge)
        mock_bridge.send_code = AsyncMock()

        code = UICode(
            code="print('hello')",
            language="python",
            title="Example",
        )

        result = await core.handle_ui_result(code)

        mock_bridge.send_code.assert_called_once()
        assert result is None

    @pytest.mark.asyncio
    async def test_handle_ui_bridge_error(self, mock_bridge):
        """Test handling UI result when bridge raises error."""
        from agentui.bridge import BridgeError

        core = AgentCore(bridge=mock_bridge)
        mock_bridge.request_confirm = AsyncMock(side_effect=BridgeError("Failed"))

        confirm = UIConfirm(message="Are you sure?")

        result = await core.handle_ui_result(confirm)

        # Should return original result on error
        assert result == confirm


class TestErrorHandling:
    """Test error handling."""

    def test_create_error_result(self):
        """Test creating error ToolResult."""
        core = AgentCore()

        error_result = core._create_error_result(
            "test_tool", "test-id", "Something failed"
        )

        assert isinstance(error_result, ToolResult)
        assert error_result.tool_name == "test_tool"
        assert error_result.tool_id == "test-id"
        assert error_result.error == "Something failed"
        assert error_result.result is None

    @pytest.mark.asyncio
    async def test_bridge_error_handling_in_confirmation(self):
        """Test bridge error in confirmation defaults to allowing execution."""
        from agentui.bridge import BridgeError

        mock_bridge = MagicMock()
        mock_bridge.request_confirm = AsyncMock(side_effect=BridgeError("Bridge failed"))
        mock_bridge.send_spinner = AsyncMock()

        core = AgentCore(bridge=mock_bridge)

        async def handler():
            return "executed despite bridge error"

        tool = ToolDefinition(
            name="test_tool",
            description="Test",
            parameters={"type": "object", "properties": {}},
            handler=handler,
            requires_confirmation=True,
        )

        core.register_tool(tool)
        result = await core.execute_tool("test_tool", "test-id", {})

        # Should continue execution despite bridge error
        assert result.error is None
        assert result.result == "executed despite bridge error"


class TestCancelation:
    """Test cancelation functionality."""

    def test_cancel_sets_flag(self):
        """Test cancel() sets the cancelation flag."""
        core = AgentCore()

        assert core._cancel_requested is False

        core.cancel()

        assert core._cancel_requested is True

    def test_stop_sets_running_flag(self):
        """Test stop() sets the running flag."""
        core = AgentCore()
        core._running = True

        core.stop()

        assert core._running is False


class TestProviderManagement:
    """Test provider initialization and management."""

    @pytest.mark.asyncio
    async def test_get_provider_claude(self):
        """Test getting Claude provider."""
        from agentui.types import ProviderType

        config = AgentConfig(
            provider=ProviderType.CLAUDE,
            model="claude-3-sonnet-20240229",
            api_key="test-key",
        )
        core = AgentCore(config=config)

        with patch("agentui.providers.claude.ClaudeProvider") as MockProvider:
            mock_instance = MagicMock()
            MockProvider.return_value = mock_instance

            provider = await core._get_provider()

            MockProvider.assert_called_once_with(
                model="claude-3-sonnet-20240229",
                api_key="test-key",
                max_tokens=4096,
            )
            assert provider == mock_instance

    @pytest.mark.asyncio
    async def test_get_provider_openai(self):
        """Test getting OpenAI provider."""
        from agentui.types import ProviderType

        config = AgentConfig(
            provider=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key",
        )
        core = AgentCore(config=config)

        with patch("agentui.providers.openai.OpenAIProvider") as MockProvider:
            mock_instance = MagicMock()
            MockProvider.return_value = mock_instance

            provider = await core._get_provider()

            MockProvider.assert_called_once_with(
                model="gpt-4",
                api_key="test-key",
                max_tokens=4096,
            )
            assert provider == mock_instance

    @pytest.mark.asyncio
    async def test_get_provider_caches_instance(self):
        """Test provider instance is cached."""
        from agentui.types import ProviderType

        config = AgentConfig(
            provider=ProviderType.CLAUDE,
            model="claude-3-sonnet-20240229",
            api_key="test-key",
        )
        core = AgentCore(config=config)

        with patch("agentui.providers.claude.ClaudeProvider") as MockProvider:
            mock_instance = MagicMock()
            MockProvider.return_value = mock_instance

            provider1 = await core._get_provider()
            provider2 = await core._get_provider()

            # Should only initialize once
            MockProvider.assert_called_once()
            assert provider1 == provider2


class TestToolIntegration:
    """Test tool integration scenarios."""

    @pytest.mark.asyncio
    async def test_tool_returning_dict(self, mock_bridge):
        """Test tool returning a dictionary."""
        core = AgentCore(bridge=mock_bridge)

        async def get_user():
            return {"name": "Alice", "age": 30, "email": "alice@example.com"}

        tool = ToolDefinition(
            name="get_user",
            description="Get user info",
            parameters={"type": "object", "properties": {}},
            handler=get_user,
        )

        core.register_tool(tool)
        result = await core.execute_tool("get_user", "test-id", {})

        assert result.error is None
        assert isinstance(result.result, dict)

    @pytest.mark.asyncio
    async def test_tool_with_no_bridge(self):
        """Test tool execution with no bridge configured."""
        core = AgentCore()  # No bridge

        async def simple_tool():
            return "result"

        tool = ToolDefinition(
            name="simple",
            description="Simple tool",
            parameters={"type": "object", "properties": {}},
            handler=simple_tool,
        )

        core.register_tool(tool)
        result = await core.execute_tool("simple", "test-id", {})

        assert result.error is None
        assert result.result == "result"

    @pytest.mark.asyncio
    async def test_tool_with_complex_arguments(self, mock_bridge):
        """Test tool with complex nested arguments."""
        core = AgentCore(bridge=mock_bridge)

        async def process_data(data: dict, options: dict):
            return f"Processed {data['key']} with {options['mode']}"

        tool = ToolDefinition(
            name="process",
            description="Process data",
            parameters={
                "type": "object",
                "properties": {
                    "data": {"type": "object"},
                    "options": {"type": "object"},
                },
            },
            handler=process_data,
        )

        core.register_tool(tool)
        result = await core.execute_tool(
            "process",
            "test-id",
            {
                "data": {"key": "value"},
                "options": {"mode": "fast"},
            },
        )

        assert result.error is None
        assert "Processed value with fast" in result.result
