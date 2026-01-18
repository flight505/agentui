"""
Tests for LLM providers (Claude and OpenAI).
"""

import json
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest

from agentui.providers.claude import ClaudeProvider
from agentui.providers.openai import OpenAIProvider


class TestClaudeProviderInitialization:
    """Test Claude provider initialization."""

    def test_init_with_default_model(self):
        """Test Claude provider initializes with default model."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()

            assert provider.model == ClaudeProvider.DEFAULT_MODEL
            assert provider.api_key == "test-key"
            assert provider.max_tokens == 4096
            assert provider._client is None

    def test_init_with_custom_model(self):
        """Test Claude provider initializes with custom model."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider(model="claude-opus-4", max_tokens=8192)

            assert provider.model == "claude-opus-4"
            assert provider.max_tokens == 8192

    def test_init_with_explicit_api_key(self):
        """Test Claude provider initializes with explicit API key."""
        provider = ClaudeProvider(api_key="explicit-key")

        assert provider.api_key == "explicit-key"

    def test_init_from_environment(self):
        """Test Claude provider reads API key from environment."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "env-key"}):
            provider = ClaudeProvider()

            assert provider.api_key == "env-key"

    def test_init_without_api_key_deferred(self):
        """Test Claude provider can initialize without API key (fails on use)."""
        with patch.dict("os.environ", {}, clear=True):
            provider = ClaudeProvider()

            assert provider.api_key is None
            assert provider._client is None


class TestClaudeProviderClient:
    """Test Claude provider client management."""

    def test_get_client_lazy_initialization(self):
        """Test client is lazy-initialized on first use."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()

            assert provider._client is None

            # Mock anthropic module
            mock_anthropic_module = MagicMock()
            mock_client = Mock()
            mock_anthropic_module.Anthropic.return_value = mock_client

            with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
                client = provider._get_client()

                assert client == mock_client
                assert provider._client == mock_client
                mock_anthropic_module.Anthropic.assert_called_once_with(api_key="test-key")

    def test_get_client_reuses_instance(self):
        """Test client is reused on subsequent calls."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()

            mock_anthropic_module = MagicMock()
            mock_client = Mock()
            mock_anthropic_module.Anthropic.return_value = mock_client

            with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
                client1 = provider._get_client()
                client2 = provider._get_client()

                assert client1 == client2
                mock_anthropic_module.Anthropic.assert_called_once()

    def test_get_client_missing_api_key_error(self):
        """Test error is raised when API key is missing."""
        with patch.dict("os.environ", {}, clear=True):
            provider = ClaudeProvider()

            mock_anthropic_module = MagicMock()
            with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
                with pytest.raises(ValueError, match="Anthropic API key not found"):
                    provider._get_client()

    def test_get_client_missing_anthropic_package(self):
        """Test error is raised when anthropic package not installed."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()

            with patch.dict("sys.modules", {"anthropic": None}):
                with pytest.raises(ImportError, match="anthropic package not installed"):
                    provider._get_client()


class TestClaudeProviderMessageConversion:
    """Test Claude provider message conversion."""

    def test_convert_messages_basic(self):
        """Test basic message conversion."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()

            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
            ]

            result = provider._convert_messages(messages)

            assert result == [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
            ]

    def test_convert_messages_filters_system(self):
        """Test system messages are filtered (handled separately)."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()

            messages = [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"},
            ]

            result = provider._convert_messages(messages)

            assert result == [{"role": "user", "content": "Hello"}]

    def test_convert_messages_with_tool_results(self):
        """Test conversion of tool results."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()

            messages = [
                {
                    "role": "user",
                    "content": "",
                    "tool_results": [
                        {"tool_use_id": "tool_123", "content": "result data"}
                    ],
                }
            ]

            result = provider._convert_messages(messages)

            assert result == [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "tool_123",
                            "content": "result data",
                        }
                    ],
                }
            ]

    def test_convert_tools(self):
        """Test tool definition conversion."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()

            tools = [
                {
                    "name": "get_weather",
                    "description": "Get weather data",
                    "input_schema": {"type": "object", "properties": {}},
                }
            ]

            result = provider._convert_tools(tools)

            assert result == [
                {
                    "name": "get_weather",
                    "description": "Get weather data",
                    "input_schema": {"type": "object", "properties": {}},
                }
            ]


class TestClaudeProviderStreaming:
    """Test Claude provider streaming."""

    @pytest.mark.asyncio
    async def test_stream_message_text_only(self):
        """Test streaming text-only response."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            mock_anthropic_module = MagicMock()
            mock_client = Mock()
            mock_stream = Mock()

            # Simulate streaming events
            mock_text_delta_1 = Mock()
            mock_text_delta_1.type = "content_block_delta"
            delta1 = Mock()
            delta1.type = "text_delta"
            delta1.text = "Hello"
            mock_text_delta_1.delta = delta1

            mock_text_delta_2 = Mock()
            mock_text_delta_2.type = "content_block_delta"
            delta2 = Mock()
            delta2.type = "text_delta"
            delta2.text = " world"
            mock_text_delta_2.delta = delta2

            mock_stream.__enter__ = Mock(return_value=mock_stream)
            mock_stream.__exit__ = Mock(return_value=False)
            mock_stream.__iter__ = Mock(return_value=iter([mock_text_delta_1, mock_text_delta_2]))

            mock_client.messages.stream.return_value = mock_stream
            mock_anthropic_module.Anthropic.return_value = mock_client

            with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
                provider = ClaudeProvider()

                messages = [{"role": "user", "content": "Test"}]
                chunks = []

                async for chunk in provider.stream_message(messages):
                    chunks.append(chunk)

                assert len(chunks) == 2
                assert chunks[0] == {"type": "text", "content": "Hello"}
                assert chunks[1] == {"type": "text", "content": " world"}

    @pytest.mark.asyncio
    async def test_stream_message_with_system_prompt(self):
        """Test streaming with system prompt."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            mock_anthropic_module = MagicMock()
            mock_client = Mock()
            mock_stream = Mock()
            mock_stream.__enter__ = Mock(return_value=mock_stream)
            mock_stream.__exit__ = Mock(return_value=False)
            mock_stream.__iter__ = Mock(return_value=iter([]))

            mock_client.messages.stream.return_value = mock_stream
            mock_anthropic_module.Anthropic.return_value = mock_client

            with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
                provider = ClaudeProvider()

                messages = [{"role": "user", "content": "Test"}]

                async for _ in provider.stream_message(messages, system="You are helpful"):
                    pass

                # Verify stream was called with system prompt
                call_args = mock_client.messages.stream.call_args
                assert call_args is not None
                assert call_args[1]["system"] == "You are helpful"

    @pytest.mark.asyncio
    async def test_stream_message_with_tool_use(self):
        """Test streaming with tool use."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            mock_anthropic_module = MagicMock()
            mock_client = Mock()
            mock_stream = Mock()

            # Simulate tool use events
            mock_tool_start = Mock()
            mock_tool_start.type = "content_block_start"
            tool_block = Mock()
            tool_block.type = "tool_use"
            tool_block.id = "tool_123"
            tool_block.name = "get_weather"
            mock_tool_start.content_block = tool_block

            mock_tool_input = Mock()
            mock_tool_input.type = "content_block_delta"
            input_delta = Mock()
            input_delta.type = "input_json_delta"
            input_delta.partial_json = '{"city": "NYC"}'
            mock_tool_input.delta = input_delta

            mock_tool_stop = Mock()
            mock_tool_stop.type = "content_block_stop"

            mock_stream.__enter__ = Mock(return_value=mock_stream)
            mock_stream.__exit__ = Mock(return_value=False)
            mock_stream.__iter__ = Mock(
                return_value=iter([mock_tool_start, mock_tool_input, mock_tool_stop])
            )

            mock_client.messages.stream.return_value = mock_stream
            mock_anthropic_module.Anthropic.return_value = mock_client

            with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
                provider = ClaudeProvider()

                messages = [{"role": "user", "content": "What's the weather?"}]
                chunks = []

                async for chunk in provider.stream_message(messages):
                    chunks.append(chunk)

                # Should get tool use chunk
                tool_chunks = [c for c in chunks if c.get("type") == "tool_use"]
                assert len(tool_chunks) == 1
                assert tool_chunks[0]["id"] == "tool_123"
                assert tool_chunks[0]["name"] == "get_weather"
                assert tool_chunks[0]["input"] == {"city": "NYC"}

    @pytest.mark.asyncio
    async def test_stream_message_with_usage_info(self):
        """Test streaming captures usage information."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            mock_anthropic_module = MagicMock()
            mock_client = Mock()
            mock_stream = Mock()

            mock_message_delta = Mock()
            mock_message_delta.type = "message_delta"
            usage = Mock()
            usage.input_tokens = 100
            usage.output_tokens = 50
            mock_message_delta.usage = usage

            mock_stream.__enter__ = Mock(return_value=mock_stream)
            mock_stream.__exit__ = Mock(return_value=False)
            mock_stream.__iter__ = Mock(return_value=iter([mock_message_delta]))

            mock_client.messages.stream.return_value = mock_stream
            mock_anthropic_module.Anthropic.return_value = mock_client

            with patch.dict("sys.modules", {"anthropic": mock_anthropic_module}):
                provider = ClaudeProvider()

                messages = [{"role": "user", "content": "Test"}]
                chunks = []

                async for chunk in provider.stream_message(messages):
                    chunks.append(chunk)

                # Should get message_end chunk with usage
                end_chunks = [c for c in chunks if c.get("type") == "message_end"]
                assert len(end_chunks) == 1
                assert end_chunks[0]["input_tokens"] == 100
                assert end_chunks[0]["output_tokens"] == 50


class TestClaudeProviderEventHandling:
    """Test Claude provider event handling."""

    def test_handle_content_block_start_text(self):
        """Test handling content block start for text."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()
            tool_state = {"current_tool": None, "current_tool_input": ""}

            event = Mock()
            event.content_block = Mock(type="text")

            provider._handle_content_block_start(event, tool_state)

            # Should not set current_tool for text blocks
            assert tool_state["current_tool"] is None

    def test_handle_content_block_start_tool(self):
        """Test handling content block start for tool use."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()
            tool_state = {"current_tool": None, "current_tool_input": ""}

            event = Mock()
            # Create a mock with proper attributes
            block = Mock()
            block.type = "tool_use"
            block.id = "tool_123"
            block.name = "get_weather"
            event.content_block = block

            provider._handle_content_block_start(event, tool_state)

            assert tool_state["current_tool"] == {"id": "tool_123", "name": "get_weather"}
            assert tool_state["current_tool_input"] == ""

    def test_handle_content_block_delta_text(self):
        """Test handling text delta."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()
            tool_state = {"current_tool": None, "current_tool_input": ""}

            event = Mock()
            event.delta = Mock(type="text_delta", text="Hello")

            result = provider._handle_content_block_delta(event, tool_state)

            assert result == {"type": "text", "content": "Hello"}

    def test_handle_content_block_delta_tool_input(self):
        """Test handling tool input delta."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()
            tool_state = {"current_tool": {"id": "tool_123", "name": "test"}, "current_tool_input": ""}

            event = Mock()
            event.delta = Mock(type="input_json_delta", partial_json='{"key":')

            result = provider._handle_content_block_delta(event, tool_state)

            assert result is None
            assert tool_state["current_tool_input"] == '{"key":'

    def test_handle_content_block_stop_with_tool(self):
        """Test handling content block stop with tool use."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()
            tool_state = {
                "current_tool": {"id": "tool_123", "name": "get_weather"},
                "current_tool_input": '{"city": "NYC"}',
            }

            result = provider._handle_content_block_stop(tool_state)

            assert result == {
                "type": "tool_use",
                "id": "tool_123",
                "name": "get_weather",
                "input": {"city": "NYC"},
            }
            # Should reset tool state
            assert tool_state["current_tool"] is None
            assert tool_state["current_tool_input"] == ""

    def test_handle_content_block_stop_without_tool(self):
        """Test handling content block stop without tool use."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()
            tool_state = {"current_tool": None, "current_tool_input": ""}

            result = provider._handle_content_block_stop(tool_state)

            assert result is None

    def test_handle_content_block_stop_with_invalid_json(self):
        """Test handling content block stop with invalid JSON."""
        with patch.dict("os.environ", {"ANTHROPIC_API_KEY": "test-key"}):
            provider = ClaudeProvider()
            tool_state = {
                "current_tool": {"id": "tool_123", "name": "test"},
                "current_tool_input": "invalid json",
            }

            result = provider._handle_content_block_stop(tool_state)

            # Should return empty dict for invalid JSON
            assert result["input"] == {}


class TestOpenAIProviderInitialization:
    """Test OpenAI provider initialization."""

    def test_init_with_default_model(self):
        """Test OpenAI provider initializes with default model."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            assert provider.model == OpenAIProvider.DEFAULT_MODEL
            assert provider.api_key == "test-key"
            assert provider.max_tokens == 4096
            assert provider._client is None

    def test_init_with_custom_model(self):
        """Test OpenAI provider initializes with custom model."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider(model="gpt-4-turbo", max_tokens=8192)

            assert provider.model == "gpt-4-turbo"
            assert provider.max_tokens == 8192

    def test_init_with_explicit_api_key(self):
        """Test OpenAI provider initializes with explicit API key."""
        provider = OpenAIProvider(api_key="explicit-key")

        assert provider.api_key == "explicit-key"

    def test_init_from_environment(self):
        """Test OpenAI provider reads API key from environment."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "env-key"}):
            provider = OpenAIProvider()

            assert provider.api_key == "env-key"


class TestOpenAIProviderClient:
    """Test OpenAI provider client management."""

    def test_get_client_lazy_initialization(self):
        """Test client is lazy-initialized on first use."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            assert provider._client is None

            mock_openai_module = MagicMock()
            mock_client = Mock()
            mock_openai_module.OpenAI.return_value = mock_client

            with patch.dict("sys.modules", {"openai": mock_openai_module}):
                client = provider._get_client()

                assert client == mock_client
                assert provider._client == mock_client
                mock_openai_module.OpenAI.assert_called_once_with(api_key="test-key")

    def test_get_client_missing_api_key_error(self):
        """Test error is raised when API key is missing."""
        with patch.dict("os.environ", {}, clear=True):
            provider = OpenAIProvider()

            mock_openai_module = MagicMock()
            with patch.dict("sys.modules", {"openai": mock_openai_module}):
                with pytest.raises(ValueError, match="OpenAI API key not found"):
                    provider._get_client()

    def test_get_client_missing_openai_package(self):
        """Test error is raised when openai package not installed."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            with patch.dict("sys.modules", {"openai": None}):
                with pytest.raises(ImportError, match="openai package not installed"):
                    provider._get_client()


class TestOpenAIProviderMessageConversion:
    """Test OpenAI provider message conversion."""

    def test_convert_messages_basic(self):
        """Test basic message conversion."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            messages = [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
            ]

            result = provider._convert_messages(messages)

            assert result == [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there"},
            ]

    def test_convert_messages_with_system(self):
        """Test conversion includes system messages."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            messages = [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"},
            ]

            result = provider._convert_messages(messages)

            assert result == [
                {"role": "system", "content": "You are helpful"},
                {"role": "user", "content": "Hello"},
            ]

    def test_convert_messages_with_tool_calls(self):
        """Test conversion of assistant messages with tool calls."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            messages = [
                {
                    "role": "assistant",
                    "content": "",
                    "tool_calls": [
                        {"id": "call_123", "name": "get_weather", "input": {"city": "NYC"}}
                    ],
                }
            ]

            result = provider._convert_messages(messages)

            assert len(result) == 1
            assert result[0]["role"] == "assistant"
            assert len(result[0]["tool_calls"]) == 1
            assert result[0]["tool_calls"][0]["id"] == "call_123"
            assert result[0]["tool_calls"][0]["function"]["name"] == "get_weather"
            assert json.loads(result[0]["tool_calls"][0]["function"]["arguments"]) == {"city": "NYC"}

    def test_convert_messages_with_tool_results(self):
        """Test conversion of tool results."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            messages = [
                {
                    "role": "user",
                    "content": "",
                    "tool_results": [
                        {"tool_use_id": "call_123", "content": "Weather is sunny"}
                    ],
                }
            ]

            result = provider._convert_messages(messages)

            assert len(result) == 1
            assert result[0]["role"] == "tool"
            assert result[0]["tool_call_id"] == "call_123"
            assert result[0]["content"] == "Weather is sunny"

    def test_convert_tools(self):
        """Test tool definition conversion."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            tools = [
                {
                    "name": "get_weather",
                    "description": "Get weather data",
                    "input_schema": {"type": "object", "properties": {"city": {"type": "string"}}},
                }
            ]

            result = provider._convert_tools(tools)

            assert len(result) == 1
            assert result[0]["type"] == "function"
            assert result[0]["function"]["name"] == "get_weather"
            assert result[0]["function"]["description"] == "Get weather data"
            assert result[0]["function"]["parameters"]["properties"]["city"]["type"] == "string"


class TestOpenAIProviderStreaming:
    """Test OpenAI provider streaming."""

    @pytest.mark.asyncio
    async def test_stream_message_text_only(self):
        """Test streaming text-only response."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            mock_openai_module = MagicMock()
            mock_client = Mock()

            # Simulate streaming chunks
            chunk1 = Mock()
            delta1 = Mock()
            delta1.content = "Hello"
            delta1.tool_calls = None
            chunk1.choices = [Mock(delta=delta1)]
            chunk1.usage = None

            chunk2 = Mock()
            delta2 = Mock()
            delta2.content = " world"
            delta2.tool_calls = None
            chunk2.choices = [Mock(delta=delta2)]
            usage = Mock()
            usage.prompt_tokens = 10
            usage.completion_tokens = 5
            chunk2.usage = usage

            mock_client.chat.completions.create.return_value = iter([chunk1, chunk2])
            mock_openai_module.OpenAI.return_value = mock_client

            with patch.dict("sys.modules", {"openai": mock_openai_module}):
                provider = OpenAIProvider()

                messages = [{"role": "user", "content": "Test"}]
                chunks = []

                async for chunk in provider.stream_message(messages):
                    chunks.append(chunk)

                # Should get text chunks and message_end
                text_chunks = [c for c in chunks if c.get("type") == "text"]
                assert len(text_chunks) == 2
                assert text_chunks[0]["content"] == "Hello"
                assert text_chunks[1]["content"] == " world"

                # Should get message_end with usage
                end_chunks = [c for c in chunks if c.get("type") == "message_end"]
                assert len(end_chunks) == 1
                assert end_chunks[0]["input_tokens"] == 10
                assert end_chunks[0]["output_tokens"] == 5

    @pytest.mark.asyncio
    async def test_stream_message_with_system_prompt(self):
        """Test streaming with system prompt."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            mock_openai_module = MagicMock()
            mock_client = Mock()
            mock_client.chat.completions.create.return_value = iter([])
            mock_openai_module.OpenAI.return_value = mock_client

            with patch.dict("sys.modules", {"openai": mock_openai_module}):
                provider = OpenAIProvider()

                messages = [{"role": "user", "content": "Test"}]

                async for _ in provider.stream_message(messages, system="You are helpful"):
                    pass

                # Verify create was called with system message
                call_args = mock_client.chat.completions.create.call_args
                assert call_args is not None
                messages_arg = call_args[1]["messages"]
                assert messages_arg[0]["role"] == "system"
                assert messages_arg[0]["content"] == "You are helpful"

    @pytest.mark.asyncio
    async def test_stream_message_with_tool_calls(self):
        """Test streaming with tool calls."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            mock_openai_module = MagicMock()
            mock_client = Mock()

            # Simulate tool call chunks
            chunk1 = Mock()
            func1 = Mock()
            func1.name = "get_weather"
            func1.arguments = '{"city":'
            tc1 = Mock()
            tc1.index = 0
            tc1.id = "call_123"
            tc1.function = func1
            delta1 = Mock()
            delta1.content = None
            delta1.tool_calls = [tc1]
            chunk1.choices = [Mock(delta=delta1)]
            chunk1.usage = None

            chunk2 = Mock()
            func2 = Mock()
            func2.name = None
            func2.arguments = ' "NYC"}'
            tc2 = Mock()
            tc2.index = 0
            tc2.id = None
            tc2.function = func2
            delta2 = Mock()
            delta2.content = None
            delta2.tool_calls = [tc2]
            chunk2.choices = [Mock(delta=delta2)]
            usage = Mock()
            usage.prompt_tokens = 10
            usage.completion_tokens = 5
            chunk2.usage = usage

            mock_client.chat.completions.create.return_value = iter([chunk1, chunk2])
            mock_openai_module.OpenAI.return_value = mock_client

            with patch.dict("sys.modules", {"openai": mock_openai_module}):
                provider = OpenAIProvider()

                messages = [{"role": "user", "content": "What's the weather?"}]
                chunks = []

                async for chunk in provider.stream_message(messages):
                    chunks.append(chunk)

                # Should get tool_use chunk at the end
                tool_chunks = [c for c in chunks if c.get("type") == "tool_use"]
                assert len(tool_chunks) == 1
                assert tool_chunks[0]["id"] == "call_123"
                assert tool_chunks[0]["name"] == "get_weather"
                assert tool_chunks[0]["input"] == {"city": "NYC"}


class TestOpenAIProviderToolAccumulation:
    """Test OpenAI provider tool call accumulation."""

    def test_accumulate_tool_calls_initial(self):
        """Test initial tool call accumulation."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()
            tool_calls = {}

            func = Mock()
            func.name = "get_weather"
            func.arguments = '{"city":'
            tc = Mock()
            tc.index = 0
            tc.id = "call_123"
            tc.function = func
            provider._accumulate_tool_calls([tc], tool_calls)

            assert 0 in tool_calls
            assert tool_calls[0]["id"] == "call_123"
            assert tool_calls[0]["name"] == "get_weather"
            assert tool_calls[0]["arguments"] == '{"city":'

    def test_accumulate_tool_calls_continuation(self):
        """Test continuation of tool call accumulation."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()
            tool_calls = {
                0: {"id": "call_123", "name": "get_weather", "arguments": '{"city":'}
            }

            tc = Mock(index=0, id=None, function=Mock(name=None, arguments=' "NYC"}'))
            provider._accumulate_tool_calls([tc], tool_calls)

            assert tool_calls[0]["arguments"] == '{"city": "NYC"}'

    def test_accumulate_tool_calls_multiple(self):
        """Test accumulating multiple tool calls."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()
            tool_calls = {}

            tc1 = Mock(index=0, id="call_1", function=Mock(name="tool_1", arguments="{}"))
            tc2 = Mock(index=1, id="call_2", function=Mock(name="tool_2", arguments="{}"))

            provider._accumulate_tool_calls([tc1, tc2], tool_calls)

            assert len(tool_calls) == 2
            assert tool_calls[0]["id"] == "call_1"
            assert tool_calls[1]["id"] == "call_2"


class TestOpenAIProviderFinalization:
    """Test OpenAI provider stream finalization."""

    @pytest.mark.asyncio
    async def test_finalize_stream_with_tool_calls(self):
        """Test finalization emits tool calls."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            state = {
                "tool_calls": {
                    0: {"id": "call_123", "name": "get_weather", "arguments": '{"city": "NYC"}'}
                },
                "input_tokens": 10,
                "output_tokens": 5,
            }

            chunks = []
            async for chunk in provider._finalize_stream(state):
                chunks.append(chunk)

            # Should emit tool_use and message_end
            assert len(chunks) == 2
            assert chunks[0]["type"] == "tool_use"
            assert chunks[0]["id"] == "call_123"
            assert chunks[0]["name"] == "get_weather"
            assert chunks[0]["input"] == {"city": "NYC"}

            assert chunks[1]["type"] == "message_end"
            assert chunks[1]["input_tokens"] == 10
            assert chunks[1]["output_tokens"] == 5

    @pytest.mark.asyncio
    async def test_finalize_stream_with_invalid_json(self):
        """Test finalization handles invalid JSON gracefully."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            state = {
                "tool_calls": {0: {"id": "call_123", "name": "test", "arguments": "invalid json"}},
                "input_tokens": 0,
                "output_tokens": 0,
            }

            chunks = []
            async for chunk in provider._finalize_stream(state):
                chunks.append(chunk)

            # Should emit tool_use with empty dict
            tool_chunk = next(c for c in chunks if c["type"] == "tool_use")
            assert tool_chunk["input"] == {}

    @pytest.mark.asyncio
    async def test_finalize_stream_without_tool_calls(self):
        """Test finalization without tool calls."""
        with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
            provider = OpenAIProvider()

            state = {"tool_calls": {}, "input_tokens": 10, "output_tokens": 5}

            chunks = []
            async for chunk in provider._finalize_stream(state):
                chunks.append(chunk)

            # Should only emit message_end
            assert len(chunks) == 1
            assert chunks[0]["type"] == "message_end"
