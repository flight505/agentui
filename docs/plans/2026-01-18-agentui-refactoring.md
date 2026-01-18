# AgentUI Refactoring Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor AgentUI codebase to professional production-ready state, eliminating code smells, technical debt, and inconsistencies from rapid 6-phase development.

**Architecture:** Systematic cleanup in 5 phases: (1) Code quality fixes, (2) Test coverage expansion, (3) Module decomposition, (4) Architecture cleanup, (5) Documentation and polish.

**Tech Stack:** Python 3.11+, pytest, ruff, mypy, Go 1.22+, uv package manager

---

## Current State Analysis

**Code Quality Issues (491 ruff errors):**
- 414 blank lines with whitespace
- 41 unused imports
- 18 lines too long
- 11 complex structures (cyclomatic complexity)
- Bare except, undefined names, f-string issues

**Missing Test Coverage:**
- `app.py` - no tests
- `cli.py` - no tests
- `core.py` - no direct unit tests
- `setup_assistant.py` - no tests
- `streaming.py` - no tests
- `types.py` - no tests
- `providers/claude.py` - no tests
- `providers/openai.py` - no tests

**Architecture Issues:**
- Large files: `bridge.py` (814 lines), `core.py` (613 lines)
- Possible circular dependencies
- Inconsistent error handling patterns
- Mixed responsibilities in some modules

---

## Phase 1: Code Quality Fixes (Automated)

### Task 1: Fix Whitespace and Formatting Issues

**Files:**
- Modify: All Python files in `src/agentui/`
- Tool: `ruff`

**Step 1: Run ruff with auto-fix for safe issues**

```bash
uv run ruff check src/agentui --fix
```

Expected: Fixes ~400 whitespace and formatting issues automatically

**Step 2: Verify no tests broken**

```bash
uv run pytest tests/ -v
```

Expected: All 77 tests still passing

**Step 3: Review changes**

```bash
git diff src/agentui/
```

Expected: Only whitespace/formatting changes, no logic changes

**Step 4: Commit**

```bash
git add src/agentui/
git commit -m "refactor: fix whitespace and auto-fixable formatting issues

- Remove 414 blank lines with whitespace
- Fix trailing whitespace
- Fix f-string formatting
- Auto-fixed by ruff --fix"
```

---

### Task 2: Remove Unused Imports

**Files:**
- Modify: All files with unused imports (41 files identified by ruff)

**Step 1: Generate list of unused imports**

```bash
uv run ruff check src/agentui --select F401 --output-format=json > /tmp/unused_imports.json
```

Expected: JSON list of all unused imports

**Step 2: Use ruff to auto-remove unused imports**

```bash
uv run ruff check src/agentui --select F401 --fix
```

Expected: Removes 41 unused imports

**Step 3: Verify imports still work**

```bash
uv run python -c "from agentui import AgentApp; from agentui.core import AgentCore; print('Imports OK')"
```

Expected: "Imports OK" printed

**Step 4: Run full test suite**

```bash
uv run pytest tests/ -v
```

Expected: All 77 tests passing

**Step 5: Commit**

```bash
git add src/agentui/
git commit -m "refactor: remove 41 unused imports

- Cleaned up import statements across all modules
- Auto-fixed by ruff F401
- All tests passing"
```

---

### Task 3: Fix Lines Too Long

**Files:**
- Modify: 18 files with long lines (>88 characters)

**Step 1: Identify long lines**

```bash
uv run ruff check src/agentui --select E501
```

Expected: List of 18 lines exceeding 88 characters

**Step 2: Manually refactor long lines**

For each long line, apply appropriate strategy:
- Break long strings with parentheses
- Split chained method calls
- Extract complex expressions to variables

Example before:
```python
result = some_function(very_long_argument_1, very_long_argument_2, very_long_argument_3, very_long_argument_4)
```

Example after:
```python
result = some_function(
    very_long_argument_1,
    very_long_argument_2,
    very_long_argument_3,
    very_long_argument_4
)
```

**Step 3: Verify formatting**

```bash
uv run ruff check src/agentui --select E501
```

Expected: 0 errors

**Step 4: Run tests**

```bash
uv run pytest tests/ -v
```

Expected: All tests passing

**Step 5: Commit**

```bash
git add src/agentui/
git commit -m "refactor: fix 18 lines exceeding 88 character limit

- Break long lines using appropriate strategies
- Improve readability of complex expressions"
```

---

### Task 4: Fix Complex Structures (Cyclomatic Complexity)

**Files:**
- Identify with: `uv run ruff check src/agentui --select C901`
- Likely candidates: `core.py`, `bridge.py`, `component_selector.py`

**Step 1: Identify complex functions**

```bash
uv run ruff check src/agentui --select C901 --output-format=text
```

Expected: List of 11 functions with high complexity

**Step 2: For each complex function, apply refactoring**

Strategies:
- Extract nested conditions to helper functions
- Replace nested if/else with early returns
- Extract complex boolean logic to named variables
- Use dict dispatch instead of long if/elif chains

Example before (in `component_selector.py`):
```python
def select_component(data):
    if isinstance(data, dict):
        if "columns" in data and "rows" in data:
            return ("table", UITable(...))
        elif "code" in data and "language" in data:
            return ("code", UICode(...))
        elif "fields" in data:
            return ("form", UIForm(...))
        # ... 10 more elif
    elif isinstance(data, list):
        # ... more nesting
```

Example after:
```python
def select_component(data):
    if isinstance(data, dict):
        return _select_from_dict(data)
    elif isinstance(data, list):
        return _select_from_list(data)
    elif isinstance(data, str):
        return _select_from_string(data)
    return ("text", UIText(content=str(data)))

def _select_from_dict(data):
    # Dict-based component patterns
    component_patterns = {
        ("columns", "rows"): lambda d: ("table", UITable(columns=d["columns"], rows=d["rows"])),
        ("code", "language"): lambda d: ("code", UICode(code=d["code"], language=d["language"])),
        ("fields",): lambda d: ("form", UIForm(fields=d["fields"])),
        # ... more patterns
    }

    for keys, builder in component_patterns.items():
        if all(k in data for k in keys):
            return builder(data)

    # Default for dicts
    return _dict_to_code(data)
```

**Step 3: Write tests for extracted functions**

```python
# tests/test_component_selector.py - add to existing file

def test_select_from_dict_with_table_pattern():
    """Test _select_from_dict recognizes table pattern."""
    data = {"columns": ["A"], "rows": [["1"]]}
    component_type, ui = ComponentSelector._select_from_dict(data)
    assert component_type == "table"

def test_select_from_dict_with_code_pattern():
    """Test _select_from_dict recognizes code pattern."""
    data = {"code": "test", "language": "python"}
    component_type, ui = ComponentSelector._select_from_dict(data)
    assert component_type == "code"
```

**Step 4: Run tests**

```bash
uv run pytest tests/test_component_selector.py -v
```

Expected: All tests passing

**Step 5: Verify complexity reduced**

```bash
uv run ruff check src/agentui --select C901
```

Expected: Fewer than 5 violations remaining

**Step 6: Commit**

```bash
git add src/agentui/component_selector.py tests/test_component_selector.py
git commit -m "refactor: reduce cyclomatic complexity in component_selector

- Extract _select_from_dict, _select_from_list, _select_from_string helpers
- Use dict dispatch pattern for component selection
- Add tests for helper functions
- Reduce complexity from 15 to 6"
```

**Repeat Steps 2-6 for other complex functions identified in Step 1**

---

### Task 5: Fix Bare Except and Error Handling

**Files:**
- Identify with: `uv run ruff check src/agentui --select E722`

**Step 1: Find bare except clauses**

```bash
grep -rn "except:" src/agentui/
```

Expected: 1 bare except clause

**Step 2: Replace with specific exception**

Before:
```python
try:
    risky_operation()
except:
    handle_error()
```

After:
```python
try:
    risky_operation()
except Exception as e:
    logger.error(f"Operation failed: {e}")
    handle_error()
```

**Step 3: Run tests**

```bash
uv run pytest tests/ -v
```

Expected: All tests passing

**Step 4: Commit**

```bash
git add src/agentui/
git commit -m "refactor: replace bare except with specific Exception

- Add proper exception logging
- Improve error traceability"
```

---

## Phase 2: Test Coverage Expansion

### Task 6: Add Tests for app.py

**Files:**
- Create: `tests/test_app.py`
- Test: `src/agentui/app.py`

**Step 1: Write test for AgentApp initialization**

```python
# tests/test_app.py
import pytest
from agentui.app import AgentApp
from agentui.types import ToolDefinition


def test_agent_app_initialization():
    """Test AgentApp initializes with correct defaults."""
    app = AgentApp(name="TestAgent")

    assert app.name == "TestAgent"
    assert app.tools == {}
    assert app.config is not None


def test_agent_app_tool_registration():
    """Test tool registration via decorator."""
    app = AgentApp(name="TestAgent")

    @app.tool("test_tool", description="Test tool", parameters={})
    def test_tool():
        return "test result"

    assert "test_tool" in app.tools
    assert app.tools["test_tool"].name == "test_tool"
    assert app.tools["test_tool"].description == "Test tool"


def test_agent_app_tool_execution():
    """Test tool execution through app."""
    app = AgentApp(name="TestAgent")

    @app.tool("echo", description="Echo tool", parameters={"type": "object", "properties": {"msg": {"type": "string"}}})
    async def echo(msg: str):
        return msg

    result = await app.core.execute_tool("echo", "test-id", {"msg": "hello"})
    assert result.result == "hello"
```

**Step 2: Run tests to verify they fail**

```bash
uv run pytest tests/test_app.py -v
```

Expected: Tests fail (not yet implemented properly)

**Step 3: Fix any issues in tests**

Review test failures and adjust tests to match actual implementation.

**Step 4: Run tests to verify they pass**

```bash
uv run pytest tests/test_app.py -v
```

Expected: All new tests passing

**Step 5: Commit**

```bash
git add tests/test_app.py
git commit -m "test: add comprehensive tests for AgentApp

- Test initialization
- Test tool registration decorator
- Test tool execution
- Coverage: app.py now at ~80%"
```

---

### Task 7: Add Tests for core.py

**Files:**
- Create: `tests/test_core.py`
- Test: `src/agentui/core.py`

**Step 1: Write tests for AgentCore**

```python
# tests/test_core.py
import pytest
from agentui.core import AgentCore, AgentError, ToolExecutionError
from agentui.types import AgentConfig, ToolDefinition
from agentui.primitives import UITable


@pytest.mark.asyncio
async def test_agent_core_initialization():
    """Test AgentCore initializes with default config."""
    core = AgentCore()

    assert core.config is not None
    assert core.tools == {}
    assert core.state.conversation_history == []


@pytest.mark.asyncio
async def test_agent_core_tool_registration():
    """Test manual tool registration."""
    core = AgentCore()

    async def test_handler():
        return "result"

    tool = ToolDefinition(
        name="test_tool",
        description="Test",
        parameters={},
        handler=test_handler
    )

    core.register_tool(tool)

    assert "test_tool" in core.tools
    assert core.tools["test_tool"].name == "test_tool"


@pytest.mark.asyncio
async def test_agent_core_execute_tool():
    """Test tool execution."""
    core = AgentCore()

    async def test_handler(arg: str):
        return f"echo: {arg}"

    tool = ToolDefinition(
        name="echo",
        description="Echo",
        parameters={"type": "object", "properties": {"arg": {"type": "string"}}},
        handler=test_handler
    )

    core.register_tool(tool)

    result = await core.execute_tool("echo", "test-id", {"arg": "hello"})

    assert result.tool_name == "echo"
    assert result.result == "echo: hello"
    assert result.is_ui is False


@pytest.mark.asyncio
async def test_agent_core_auto_selects_ui_component():
    """Test core auto-selects UI component for plain data."""
    core = AgentCore()

    async def get_data():
        return [{"name": "Alice", "age": 30}]

    tool = ToolDefinition(
        name="get_data",
        description="Get data",
        parameters={},
        handler=get_data
    )

    core.register_tool(tool)

    result = await core.execute_tool("get_data", "test-id", {})

    assert result.is_ui is True
    assert isinstance(result.result, UITable)


@pytest.mark.asyncio
async def test_agent_core_handles_tool_errors():
    """Test core handles tool execution errors gracefully."""
    core = AgentCore()

    async def failing_tool():
        raise ValueError("Test error")

    tool = ToolDefinition(
        name="fail",
        description="Failing tool",
        parameters={},
        handler=failing_tool
    )

    core.register_tool(tool)

    with pytest.raises(ToolExecutionError):
        await core.execute_tool("fail", "test-id", {})


@pytest.mark.asyncio
async def test_agent_core_system_prompt_has_catalog():
    """Test system prompt contains component catalog."""
    core = AgentCore()

    assert "Available UI Components" in core.config.system_prompt
    assert "display_table" in core.config.system_prompt


@pytest.mark.asyncio
async def test_agent_core_display_tools_registered():
    """Test display_* tools auto-registered."""
    core = AgentCore()

    display_tools = [
        "display_table",
        "display_form",
        "display_code",
        "display_progress",
        "display_confirm",
        "display_alert",
        "display_select"
    ]

    for tool_name in display_tools:
        assert tool_name in core.tools
        assert core.tools[tool_name].is_ui_tool is True
```

**Step 2: Run tests**

```bash
uv run pytest tests/test_core.py -v
```

Expected: All tests passing (or identify issues to fix)

**Step 3: Commit**

```bash
git add tests/test_core.py
git commit -m "test: add comprehensive tests for AgentCore

- Test initialization and configuration
- Test tool registration and execution
- Test auto UI component selection
- Test error handling
- Test display_* tool auto-registration
- Coverage: core.py now at ~75%"
```

---

### Task 8: Add Tests for streaming.py

**Files:**
- Create: `tests/test_streaming.py`
- Test: `src/agentui/streaming.py`

**Step 1: Write tests for UIStream**

```python
# tests/test_streaming.py
import pytest
from unittest.mock import Mock, AsyncMock
from agentui.streaming import UIStream, streaming_tool
from agentui.primitives import UITable, UIProgress


@pytest.mark.asyncio
async def test_uistream_initialization():
    """Test UIStream initializes with bridge."""
    bridge = Mock()
    stream = UIStream(bridge)

    assert stream.bridge is bridge
    assert stream.component_id is not None
    assert stream._current_type is None


@pytest.mark.asyncio
async def test_uistream_send_progress():
    """Test UIStream sends progress updates."""
    bridge = AsyncMock()
    stream = UIStream(bridge)

    await stream.send_progress("Loading...", 50.0)

    bridge.send_message.assert_called_once()
    call_args = bridge.send_message.call_args
    assert "Loading..." in str(call_args)
    assert stream._current_type == "progress"


@pytest.mark.asyncio
async def test_uistream_send_table():
    """Test UIStream sends table updates."""
    bridge = AsyncMock()
    stream = UIStream(bridge)

    await stream.send_table(["Name"], [["Alice"]], title="Users")

    bridge.send_message.assert_called_once()
    call_args = bridge.send_message.call_args
    assert "Name" in str(call_args)
    assert stream._current_type == "table"


@pytest.mark.asyncio
async def test_uistream_finalize_table():
    """Test UIStream finalizes as table."""
    bridge = Mock()
    stream = UIStream(bridge)

    result = stream.finalize_table(["Col1"], [["Val1"]])

    assert isinstance(result, UITable)
    assert result.columns == ["Col1"]
    assert result.rows == [["Val1"]]


@pytest.mark.asyncio
async def test_uistream_finalize_progress():
    """Test UIStream finalizes as progress."""
    bridge = Mock()
    stream = UIStream(bridge)

    result = stream.finalize_progress("Complete", 100.0)

    assert isinstance(result, UIProgress)
    assert result.message == "Complete"
    assert result.percent == 100.0


def test_streaming_tool_decorator():
    """Test @streaming_tool decorator marks function."""
    @streaming_tool
    async def test_func():
        return "result"

    assert hasattr(test_func, "_is_streaming")
    assert test_func._is_streaming is True


@pytest.mark.asyncio
async def test_streaming_tool_execution():
    """Test streaming tool can be executed."""
    @streaming_tool
    async def stream_data():
        # Simulated streaming operation
        return {"data": "result"}

    result = await stream_data()
    assert result == {"data": "result"}
```

**Step 2: Run tests**

```bash
uv run pytest tests/test_streaming.py -v
```

Expected: All tests passing

**Step 3: Commit**

```bash
git add tests/test_streaming.py
git commit -m "test: add comprehensive tests for streaming module

- Test UIStream initialization
- Test progressive updates (progress, table)
- Test finalization methods
- Test @streaming_tool decorator
- Coverage: streaming.py now at ~85%"
```

---

### Task 9: Add Tests for Providers

**Files:**
- Create: `tests/test_providers.py`
- Test: `src/agentui/providers/claude.py`, `src/agentui/providers/openai.py`

**Step 1: Write tests for Claude provider**

```python
# tests/test_providers.py
import pytest
from unittest.mock import Mock, AsyncMock, patch
from agentui.providers.claude import ClaudeProvider
from agentui.types import Message


@pytest.mark.asyncio
async def test_claude_provider_initialization():
    """Test Claude provider initializes with API key."""
    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        provider = ClaudeProvider()
        assert provider.api_key == 'test-key'


@pytest.mark.asyncio
async def test_claude_provider_missing_api_key():
    """Test Claude provider raises error without API key."""
    with patch.dict('os.environ', {}, clear=True):
        with pytest.raises(ValueError, match="ANTHROPIC_API_KEY"):
            ClaudeProvider()


@pytest.mark.asyncio
@patch('anthropic.AsyncAnthropic')
async def test_claude_provider_stream_messages(mock_anthropic):
    """Test Claude provider streams messages."""
    # Mock streaming response
    mock_client = AsyncMock()
    mock_stream = AsyncMock()
    mock_stream.__aenter__.return_value = mock_stream
    mock_stream.__aiter__.return_value = iter([
        Mock(type="content_block_delta", delta=Mock(type="text_delta", text="Hello")),
        Mock(type="content_block_delta", delta=Mock(type="text_delta", text=" world")),
    ])

    mock_client.messages.stream.return_value = mock_stream
    mock_anthropic.return_value = mock_client

    with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'test-key'}):
        provider = ClaudeProvider()

        messages = [Message(role="user", content="Test")]
        chunks = []

        async for chunk in provider.stream(messages, tools=[]):
            chunks.append(chunk.content)

        assert chunks == ["Hello", " world"]


@pytest.mark.asyncio
async def test_openai_provider_initialization():
    """Test OpenAI provider initializes with API key."""
    with patch.dict('os.environ', {'OPENAI_API_KEY': 'test-key'}):
        from agentui.providers.openai import OpenAIProvider
        provider = OpenAIProvider()
        assert provider.api_key == 'test-key'
```

**Step 2: Run tests**

```bash
uv run pytest tests/test_providers.py -v
```

Expected: Tests passing (with mocked API calls)

**Step 3: Commit**

```bash
git add tests/test_providers.py
git commit -m "test: add tests for LLM providers

- Test Claude provider initialization and streaming
- Test OpenAI provider initialization
- Mock external API calls
- Coverage: providers at ~70%"
```

---

## Phase 3: Module Decomposition

### Task 10: Split bridge.py (814 lines)

**Files:**
- Modify: `src/agentui/bridge.py`
- Create: `src/agentui/bridge/tui_bridge.py`
- Create: `src/agentui/bridge/cli_bridge.py`
- Create: `src/agentui/bridge/base.py`
- Create: `src/agentui/bridge/__init__.py`

**Step 1: Create bridge package structure**

```bash
mkdir -p src/agentui/bridge
touch src/agentui/bridge/__init__.py
```

**Step 2: Extract base bridge interface**

```python
# src/agentui/bridge/base.py
"""Base bridge interface for UI communication."""

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator
import asyncio


class BaseBridge(ABC):
    """Abstract base class for UI bridges."""

    @abstractmethod
    async def send_message(self, msg_type: str, payload: dict) -> None:
        """Send message to UI."""
        pass

    @abstractmethod
    async def wait_for_response(self, request_id: str, timeout: float = 30.0) -> Any:
        """Wait for UI response."""
        pass

    @abstractmethod
    async def events(self) -> AsyncIterator[dict]:
        """Stream UI events."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close bridge connection."""
        pass
```

**Step 3: Move TUIBridge to separate file**

Extract TUIBridge class and related code from `bridge.py` to `bridge/tui_bridge.py`

```python
# src/agentui/bridge/tui_bridge.py
"""TUI Bridge for Go subprocess communication."""

from agentui.bridge.base import BaseBridge
# ... rest of TUIBridge implementation
```

**Step 4: Move CLIBridge to separate file**

```python
# src/agentui/bridge/cli_bridge.py
"""CLI Bridge using Rich for fallback rendering."""

from agentui.bridge.base import BaseBridge
# ... rest of CLIBridge implementation
```

**Step 5: Update bridge/__init__.py**

```python
# src/agentui/bridge/__init__.py
"""Bridge package for UI communication."""

from agentui.bridge.base import BaseBridge
from agentui.bridge.tui_bridge import TUIBridge, TUIConfig, BridgeError, managed_bridge
from agentui.bridge.cli_bridge import CLIBridge

__all__ = [
    "BaseBridge",
    "TUIBridge",
    "CLIBridge",
    "TUIConfig",
    "BridgeError",
    "managed_bridge",
]


def create_bridge(use_tui: bool = True, config: TUIConfig | None = None) -> BaseBridge:
    """Factory function to create appropriate bridge."""
    if use_tui:
        return TUIBridge(config or TUIConfig())
    return CLIBridge()
```

**Step 6: Update imports across codebase**

```bash
# Update all files importing from bridge
find src/agentui -name "*.py" -exec sed -i '' 's/from agentui.bridge import/from agentui.bridge import/g' {} \;
```

**Step 7: Run tests**

```bash
uv run pytest tests/test_bridge.py -v
```

Expected: All tests passing

**Step 8: Remove old bridge.py**

```bash
git rm src/agentui/bridge.py
```

**Step 9: Commit**

```bash
git add src/agentui/bridge/
git commit -m "refactor: split bridge.py into modular package

- Create bridge package with base, tui_bridge, cli_bridge
- Extract BaseBridge abstract interface
- Separate TUIBridge (450 lines) and CLIBridge (200 lines)
- Add factory function create_bridge()
- All tests passing"
```

---

### Task 11: Split core.py (613 lines)

**Files:**
- Modify: `src/agentui/core.py`
- Create: `src/agentui/core/agent.py`
- Create: `src/agentui/core/tool_executor.py`
- Create: `src/agentui/core/message_handler.py`
- Create: `src/agentui/core/__init__.py`

**Step 1: Create core package structure**

```bash
mkdir -p src/agentui/core
touch src/agentui/core/__init__.py
```

**Step 2: Extract tool execution logic**

```python
# src/agentui/core/tool_executor.py
"""Tool execution and result handling."""

from typing import Any
from agentui.types import ToolDefinition, ToolResult
from agentui.component_selector import ComponentSelector
from agentui.primitives import UIForm, UIConfirm, UISelect
import logging

logger = logging.getLogger(__name__)


class ToolExecutor:
    """Handles tool execution and result processing."""

    def __init__(self):
        self.tools: dict[str, ToolDefinition] = {}

    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool for execution."""
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    async def execute_tool(
        self,
        tool_name: str,
        tool_id: str,
        arguments: dict[str, Any]
    ) -> ToolResult:
        """Execute a tool and return the result."""
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")

        tool = self.tools[tool_name]

        try:
            # Execute handler
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**arguments)
            else:
                result = tool.handler(**arguments)

            # Determine if result is UI
            is_ui = tool.is_ui_tool or isinstance(
                result,
                (UIForm, UIConfirm, UISelect, UITable, UICode, UIProgress, UIAlert, UIText, UIMarkdown)
            )

            # Auto-select component if needed
            if not is_ui and not isinstance(result, (UIForm, UIConfirm, UISelect)):
                component_type, ui_primitive = ComponentSelector.select_component(result)
                if component_type != "text" or isinstance(ui_primitive, (UITable, UICode, UIMarkdown)):
                    result = ui_primitive
                    is_ui = True

            return ToolResult(
                tool_name=tool_name,
                tool_id=tool_id,
                result=result,
                is_ui=is_ui
            )

        except Exception as e:
            logger.error(f"Tool execution failed: {tool_name} - {e}")
            raise ToolExecutionError(f"Tool {tool_name} failed: {e}") from e
```

**Step 3: Extract message handling logic**

```python
# src/agentui/core/message_handler.py
"""Message processing and streaming."""

from typing import AsyncIterator
from agentui.types import Message, StreamChunk
import logging

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles message processing and streaming."""

    async def process_streaming_response(
        self,
        provider_stream: AsyncIterator[StreamChunk]
    ) -> AsyncIterator[StreamChunk]:
        """Process streaming LLM response."""
        async for chunk in provider_stream:
            # Process chunk (logging, filtering, etc.)
            logger.debug(f"Received chunk: {chunk.type}")
            yield chunk

    def build_messages(
        self,
        conversation_history: list[Message],
        system_prompt: str
    ) -> list[Message]:
        """Build message list for LLM."""
        messages = []

        if system_prompt:
            messages.append(Message(role="system", content=system_prompt))

        messages.extend(conversation_history)

        return messages
```

**Step 4: Create main AgentCore in core/agent.py**

```python
# src/agentui/core/agent.py
"""Main AgentCore implementation."""

from agentui.core.tool_executor import ToolExecutor
from agentui.core.message_handler import MessageHandler
from agentui.types import AgentConfig, AgentState
from agentui.component_catalog import ComponentCatalog

class AgentCore:
    """Core agent execution engine."""

    def __init__(self, config: AgentConfig | None = None, bridge=None):
        self.config = config or AgentConfig()
        self.bridge = bridge
        self.state = AgentState()

        # Delegate to specialized components
        self.tool_executor = ToolExecutor()
        self.message_handler = MessageHandler()

        # Enhance system prompt with catalog
        self._enhance_system_prompt_with_catalog()

        # Auto-register display tools
        self._register_display_tools()

    # ... delegate methods to tool_executor and message_handler
```

**Step 5: Update core/__init__.py**

```python
# src/agentui/core/__init__.py
"""Core agent execution components."""

from agentui.core.agent import AgentCore
from agentui.core.tool_executor import ToolExecutor
from agentui.core.message_handler import MessageHandler

__all__ = ["AgentCore", "ToolExecutor", "MessageHandler"]
```

**Step 6: Update imports**

```bash
# Update imports across codebase
find src/agentui -name "*.py" ! -path "*/core/*" -exec sed -i '' 's/from agentui.core import AgentCore/from agentui.core import AgentCore/g' {} \;
```

**Step 7: Run tests**

```bash
uv run pytest tests/test_core.py -v
```

Expected: All tests passing

**Step 8: Remove old core.py**

```bash
git rm src/agentui/core.py
```

**Step 9: Commit**

```bash
git add src/agentui/core/
git commit -m "refactor: split core.py into modular package

- Create core package with agent, tool_executor, message_handler
- Separate concerns: tool execution (200 lines), message handling (150 lines)
- Main AgentCore delegates to specialized components
- Reduce single file from 613 to ~250 lines
- All tests passing"
```

---

## Phase 4: Architecture Cleanup

### Task 12: Remove Placeholder/Stub Code from Skills System

**Files:**
- Modify: `src/agentui/skills/__init__.py`
- Remove: `examples/skills/weather/` (incomplete example)

**Step 1: Identify the stub code**

```bash
grep -A10 "_create_placeholder_handler" src/agentui/skills/__init__.py
```

Expected: Shows placeholder handler that returns error dict

**Step 2: Replace placeholder with proper error handling**

Before:
```python
@staticmethod
def _create_placeholder_handler(tool_name: str):
    """Create a placeholder handler for YAML-defined tools."""
    def handler(**kwargs):
        return {
            "error": f"Tool '{tool_name}' is defined in YAML but has no Python handler."
        }
    return handler
```

After:
```python
@staticmethod
def _validate_tool_has_handler(tool_def: dict, skill_path: Path) -> None:
    """Validate that YAML-defined tools have corresponding Python handlers."""
    # Check if skill.py exists with handler implementation
    skill_py = skill_path / "skill.py"

    if not skill_py.exists():
        raise ValueError(
            f"Skill '{skill_path.name}' defines tool '{tool_def['name']}' in YAML "
            f"but has no skill.py with handler implementation. "
            f"Create {skill_py} with a function named '{tool_def['name']}'"
        )

    # Import and verify handler exists
    import importlib.util
    spec = importlib.util.spec_from_file_location("skill", skill_py)
    if spec is None or spec.loader is None:
        raise ValueError(f"Could not load {skill_py}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, tool_def["name"]):
        raise ValueError(
            f"Tool '{tool_def['name']}' defined in YAML but function not found in {skill_py}"
        )

    return getattr(module, tool_def["name"])

# Update the load method:
@classmethod
def load(cls, path: str | Path) -> "Skill":
    """Load a skill from a directory."""
    path = Path(path)

    # ... existing code ...

    if skill_yaml.exists():
        with open(skill_yaml) as f:
            config = yaml.safe_load(f) or {}

        # Extract tool definitions and validate they have handlers
        for tool_def in config.get("tools", []):
            handler = cls._validate_tool_has_handler(tool_def, path)

            tools.append(ToolDefinition(
                name=tool_def["name"],
                description=tool_def.get("description", ""),
                parameters=tool_def.get("parameters", {}),
                handler=handler,  # Real handler, not placeholder
            ))
```

**Step 3: Remove incomplete example**

```bash
# Remove weather skill example that has no implementation
trash examples/skills/weather/
```

Or provide a complete implementation:

```python
# examples/skills/weather/skill.py
"""Weather skill implementation."""

import random  # For demo purposes - replace with real API

def get_weather(city: str, units: str = "celsius") -> dict:
    """Get current weather for a city."""
    # TODO: Replace with real weather API call
    temp = random.randint(10, 30)
    return {
        "city": city,
        "temperature": temp,
        "units": units,
        "conditions": "Partly cloudy",
        "humidity": "65%"
    }

def get_forecast(city: str, days: int = 3) -> list:
    """Get weather forecast."""
    # TODO: Replace with real weather API call
    forecast = []
    for i in range(days):
        forecast.append({
            "day": i + 1,
            "high": random.randint(15, 30),
            "low": random.randint(5, 15),
            "conditions": ["Sunny", "Cloudy", "Rainy"][i % 3]
        })
    return forecast
```

**Step 4: Add test for skill loading with missing handler**

```python
# tests/test_skills.py
import pytest
from pathlib import Path
from agentui.skills import load_skill


def test_skill_without_handler_raises_error(tmp_path):
    """Test that loading skill without handler implementation fails."""
    # Create incomplete skill (YAML only, no skill.py)
    skill_dir = tmp_path / "incomplete_skill"
    skill_dir.mkdir()

    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text("""
name: incomplete
tools:
  - name: test_tool
    description: Test
    parameters: {}
    """)

    with pytest.raises(ValueError, match="has no skill.py"):
        load_skill(skill_dir)


def test_skill_with_handler_loads_successfully(tmp_path):
    """Test that skill with proper implementation loads."""
    skill_dir = tmp_path / "complete_skill"
    skill_dir.mkdir()

    # Create YAML
    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text("""
name: complete
tools:
  - name: test_tool
    description: Test
    parameters: {}
    """)

    # Create implementation
    skill_py = skill_dir / "skill.py"
    skill_py.write_text("""
def test_tool():
    return "real implementation"
    """)

    skill = load_skill(skill_dir)

    assert skill.name == "complete"
    assert len(skill.tools) == 1
    assert skill.tools[0].name == "test_tool"

    # Verify it's a real handler, not placeholder
    result = skill.tools[0].handler()
    assert result == "real implementation"
```

**Step 5: Run tests**

```bash
uv run pytest tests/test_skills.py -v
```

Expected: Tests pass, skills require real implementations

**Step 6: Update documentation**

```markdown
# docs/SKILLS.md (create or update)

## Creating Skills

Skills MUST have both:
1. `skill.yaml` - Tool definitions
2. `skill.py` - Python implementations

### Example

```yaml
# skill.yaml
tools:
  - name: greet
    description: Greet user
    parameters:
      type: object
      properties:
        name: {type: string}
```

```python
# skill.py
def greet(name: str) -> str:
    return f"Hello, {name}!"
```

**Error:** Creating skill.yaml without skill.py will raise `ValueError` at load time.
```

**Step 7: Commit**

```bash
git add src/agentui/skills/ tests/test_skills.py docs/SKILLS.md
git rm -r examples/skills/weather/  # Or add implementation
git commit -m "refactor: remove placeholder handlers from skills system

- Skills now REQUIRE real Python implementations
- Validate handler exists at load time, not runtime
- Raise clear error if skill.py missing
- Remove incomplete weather skill example
- Add comprehensive skill loading tests
- No more stub/placeholder code in production"
```

---

### Task 13: Standardize Error Handling

**Files:**
- Create: `src/agentui/exceptions.py`
- Modify: All files with custom exceptions

**Step 1: Create centralized exceptions module**

```python
# src/agentui/exceptions.py
"""Centralized exception definitions for AgentUI."""


class AgentUIError(Exception):
    """Base exception for all AgentUI errors."""
    pass


class ConfigurationError(AgentUIError):
    """Configuration-related errors."""
    pass


class BridgeError(AgentUIError):
    """Bridge communication errors."""
    pass


class ToolExecutionError(AgentUIError):
    """Tool execution failures."""
    pass


class ProviderError(AgentUIError):
    """LLM provider errors."""
    pass


class ValidationError(AgentUIError):
    """Input validation errors."""
    pass
```

**Step 2: Replace scattered exception definitions**

Update each module to use centralized exceptions:

```python
# Before (in core.py):
class AgentError(Exception):
    pass

class ToolExecutionError(AgentError):
    pass

# After:
from agentui.exceptions import AgentUIError, ToolExecutionError
```

**Step 3: Add exception handling tests**

```python
# tests/test_exceptions.py
import pytest
from agentui.exceptions import (
    AgentUIError,
    ConfigurationError,
    BridgeError,
    ToolExecutionError,
    ProviderError,
    ValidationError
)


def test_exception_hierarchy():
    """Test exception inheritance."""
    assert issubclass(ConfigurationError, AgentUIError)
    assert issubclass(BridgeError, AgentUIError)
    assert issubclass(ToolExecutionError, AgentUIError)
    assert issubclass(ProviderError, AgentUIError)
    assert issubclass(ValidationError, AgentUIError)


def test_exception_messages():
    """Test exceptions can carry messages."""
    error = ToolExecutionError("Tool failed")
    assert str(error) == "Tool failed"
```

**Step 4: Run tests**

```bash
uv run pytest tests/ -v
```

Expected: All tests passing

**Step 5: Commit**

```bash
git add src/agentui/exceptions.py tests/test_exceptions.py
git commit -m "refactor: centralize exception definitions

- Create exceptions.py with consistent hierarchy
- Replace scattered exception definitions
- Add exception tests
- Improve error traceability"
```

---

### Task 13: Add Type Annotations Validation

**Files:**
- Modify: All Python files
- Tool: mypy

**Step 1: Run mypy to identify type issues**

```bash
uv run mypy src/agentui --strict
```

Expected: List of type errors

**Step 2: Add missing type annotations**

For each error, add appropriate type hints:

```python
# Before:
def process_data(data):
    return data

# After:
def process_data(data: Any) -> Any:
    return data
```

**Step 3: Create mypy configuration**

```ini
# pyproject.toml - add to existing [tool.mypy] section
[tool.mypy]
python_version = "3.11"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = false  # Too strict for now
```

**Step 4: Run mypy again**

```bash
uv run mypy src/agentui
```

Expected: 0 errors

**Step 5: Commit**

```bash
git add src/agentui/ pyproject.toml
git commit -m "refactor: add comprehensive type annotations

- Pass mypy strict mode
- Add type hints to all functions
- Configure mypy in pyproject.toml
- Improve IDE support and type safety"
```

---

### Task 14: Consolidate Configuration

**Files:**
- Modify: `src/agentui/types.py`
- Create: `src/agentui/config.py`

**Step 1: Extract configuration to dedicated module**

```python
# src/agentui/config.py
"""Configuration management for AgentUI."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import os


@dataclass
class AgentConfig:
    """Main agent configuration."""

    model: str = "claude-sonnet-4-5-20250929"
    provider: str = "claude"
    system_prompt: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    stream: bool = True

    # API keys (loaded from environment by default)
    anthropic_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    openai_api_key: Optional[str] = field(
        default_factory=lambda: os.getenv("OPENAI_API_KEY")
    )

    @classmethod
    def from_env(cls) -> "AgentConfig":
        """Create config from environment variables."""
        return cls(
            model=os.getenv("AGENTUI_MODEL", cls.model),
            provider=os.getenv("AGENTUI_PROVIDER", cls.provider),
            max_tokens=int(os.getenv("AGENTUI_MAX_TOKENS", cls.max_tokens)),
            temperature=float(os.getenv("AGENTUI_TEMPERATURE", cls.temperature)),
        )

    @classmethod
    def from_file(cls, path: Path) -> "AgentConfig":
        """Load config from YAML file."""
        import yaml
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


@dataclass
class TUIConfig:
    """TUI bridge configuration."""

    binary_path: Optional[Path] = None
    theme: str = "charm-dark"
    headless: bool = False
    reconnect_attempts: int = 3
    timeout: float = 120.0
```

**Step 2: Update types.py to import from config**

```python
# src/agentui/types.py
from agentui.config import AgentConfig, TUIConfig

# Re-export for backward compatibility
__all__ = [..., "AgentConfig", "TUIConfig"]
```

**Step 3: Add configuration tests**

```python
# tests/test_config.py
import pytest
from pathlib import Path
from agentui.config import AgentConfig, TUIConfig
import os


def test_agent_config_defaults():
    """Test default configuration values."""
    config = AgentConfig()

    assert config.model == "claude-sonnet-4-5-20250929"
    assert config.provider == "claude"
    assert config.max_tokens == 4096
    assert config.temperature == 0.7


def test_agent_config_from_env(monkeypatch):
    """Test loading config from environment."""
    monkeypatch.setenv("AGENTUI_MODEL", "custom-model")
    monkeypatch.setenv("AGENTUI_MAX_TOKENS", "8192")

    config = AgentConfig.from_env()

    assert config.model == "custom-model"
    assert config.max_tokens == 8192


def test_tui_config_defaults():
    """Test TUI config defaults."""
    config = TUIConfig()

    assert config.theme == "charm-dark"
    assert config.headless is False
    assert config.reconnect_attempts == 3
```

**Step 4: Run tests**

```bash
uv run pytest tests/test_config.py -v
```

Expected: All tests passing

**Step 5: Commit**

```bash
git add src/agentui/config.py tests/test_config.py
git commit -m "refactor: consolidate configuration management

- Create dedicated config.py module
- Support loading from env and file
- Add configuration tests
- Improve configuration discoverability"
```

---

## Phase 5: Documentation and Polish

### Task 15: Add Docstrings to All Public APIs

**Files:**
- Modify: All public modules, classes, and functions

**Step 1: Audit missing docstrings**

```bash
uv run pydocstyle src/agentui --count
```

Expected: Count of missing docstrings

**Step 2: Add module-level docstrings**

For each module without a docstring:

```python
# Before:
# Empty or minimal docstring

# After:
"""
Module name - Brief description.

This module provides X functionality for Y purpose.

Example:
    >>> from agentui import AgentApp
    >>> app = AgentApp(name="MyAgent")
    >>> app.run()

See Also:
    - Related module 1
    - Related module 2
"""
```

**Step 3: Add class docstrings**

```python
class MyClass:
    """
    Brief one-line description.

    Longer description explaining purpose, usage, and key concepts.

    Attributes:
        attr1: Description of attribute 1
        attr2: Description of attribute 2

    Example:
        >>> obj = MyClass(param1="value")
        >>> result = obj.method()
    """
```

**Step 4: Add function docstrings**

```python
def my_function(param1: str, param2: int) -> str:
    """
    Brief one-line description.

    Longer description if needed.

    Args:
        param1: Description of param1
        param2: Description of param2

    Returns:
        Description of return value

    Raises:
        ValueError: When invalid input provided
        TypeError: When wrong type provided

    Example:
        >>> result = my_function("test", 42)
        >>> print(result)
        'processed test 42'
    """
```

**Step 5: Run pydocstyle to verify**

```bash
uv run pydocstyle src/agentui
```

Expected: 0 errors

**Step 6: Commit**

```bash
git add src/agentui/
git commit -m "docs: add comprehensive docstrings to public APIs

- Add module-level docstrings to all modules
- Add class docstrings with examples
- Add function docstrings with Args/Returns/Raises
- Pass pydocstyle validation"
```

---

### Task 16: Update README with Examples

**Files:**
- Modify: `README.md`

**Step 1: Add Quick Start section**

```markdown
# README.md

## Quick Start

### Installation

```bash
pip install agentui
```

### Basic Usage

```python
from agentui import AgentApp

app = AgentApp(name="MyAgent")

@app.tool("greet", description="Greet user", parameters={"type": "object", "properties": {"name": {"type": "string"}}})
def greet(name: str):
    return f"Hello, {name}!"

app.run()
```

### Data-Driven UI

Tools return plain data, AgentUI auto-selects optimal UI components:

```python
@app.tool("get_users")
def get_users():
    # Return list of dicts → automatically becomes a table
    return [
        {"name": "Alice", "role": "Admin"},
        {"name": "Bob", "role": "User"}
    ]

@app.tool("analyze_code")
def analyze_code(file_path: str):
    # Return code string → automatically becomes syntax-highlighted code block
    with open(file_path) as f:
        return f.read()
```

### Dashboard Layouts

Compose multiple components into dashboard views:

```python
from agentui import UILayout

@app.tool("system_dashboard")
def system_dashboard():
    return (
        UILayout(title="System Status")
        .add_table(
            columns=["Service", "Status"],
            rows=[["API", "✓"], ["DB", "✓"]],
            area="left"
        )
        .add_progress(
            message="CPU Usage",
            percent=65,
            area="right"
        )
    )
```
```

**Step 2: Commit**

```bash
git add README.md
git commit -m "docs: add comprehensive examples to README

- Add Quick Start section
- Show data-driven UI examples
- Show dashboard layout examples
- Improve discoverability"
```

---

### Task 17: Run Final Validation

**Files:**
- All files

**Step 1: Run full test suite**

```bash
uv run pytest tests/ -v --cov=src/agentui --cov-report=html
```

Expected: All tests passing, coverage >80%

**Step 2: Run all quality checks**

```bash
# Linting
uv run ruff check src/agentui

# Type checking
uv run mypy src/agentui

# Docstring checking
uv run pydocstyle src/agentui

# Security check
uv run bandit -r src/agentui
```

Expected: 0 errors in all checks

**Step 3: Build Go TUI**

```bash
make build-tui
```

Expected: Successful build

**Step 4: Run integration test**

```bash
uv run python examples/generative_ui_v2_demo.py
```

Expected: Demo runs successfully

**Step 5: Create validation report**

```markdown
# docs/REFACTORING_VALIDATION.md

# AgentUI Refactoring Validation Report

**Date**: 2026-01-18

## Test Results

- Total tests: 120+ (increased from 77)
- Pass rate: 100%
- Coverage: 85% (up from ~60%)

## Code Quality

- Ruff violations: 0 (down from 491)
- Mypy errors: 0 (strict mode)
- Pydocstyle errors: 0

## Architecture

- Large files split: bridge.py (814→300 lines), core.py (613→250 lines)
- New modules: 8 (exceptions, config, bridge/*, core/*)
- Cyclomatic complexity: All functions <10

## Documentation

- Module docstrings: 100%
- Class docstrings: 100%
- Function docstrings: 100%
- README updated with examples

## Success Criteria

✅ All automated code quality issues resolved
✅ Test coverage >80%
✅ All modules <400 lines
✅ Consistent error handling
✅ Comprehensive documentation
✅ Type safety verified
```

**Step 6: Final commit**

```bash
git add docs/REFACTORING_VALIDATION.md
git commit -m "docs: add refactoring validation report

All quality metrics achieved:
- 0 ruff violations (491→0)
- 120+ tests passing (77→120+)
- 85% coverage (60%→85%)
- All modules <400 lines
- Type safety verified
- Comprehensive documentation"
```

---

## Summary

**Refactoring Impact:**

**Before:**
- 491 code quality violations
- 77 tests, ~60% coverage
- 2 files >600 lines
- Scattered error handling
- Missing tests for 8 modules

**After:**
- 0 code quality violations
- 120+ tests, 85% coverage
- All files <400 lines
- Centralized exception hierarchy
- Comprehensive test coverage
- Full type safety
- 100% docstring coverage

**Time Estimate:** 3-5 days for full implementation

**Next Steps:**
1. Choose execution approach (subagent-driven or parallel session)
2. Execute plan task-by-task
3. Review after each phase
4. Deploy refactored codebase

---
