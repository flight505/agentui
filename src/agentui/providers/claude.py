"""
Claude Provider - Anthropic Claude integration.
"""

import os
from collections.abc import AsyncIterator

from agentui.exceptions import ProviderError


class ClaudeProvider:
    """
    Provider for Anthropic Claude models.

    Supports streaming responses and tool use.
    """

    DEFAULT_MODEL = "claude-sonnet-4-5-20250929"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 4096,
    ):
        self.model = model or self.DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.max_tokens = max_tokens
        self._client = None

    def _get_client(self) -> object:
        """Get or create the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Install with: uv sync --extra claude  (or: uv add anthropic)"
                )

            if not self.api_key:
                raise ProviderError(
                    "Anthropic API key not found. "
                    "Set ANTHROPIC_API_KEY environment variable or pass api_key."
                )

            self._client = anthropic.Anthropic(api_key=self.api_key)

        return self._client

    async def stream_message(
        self,
        messages: list[dict],
        system: str | None = None,
        tools: list[dict] | None = None,
    ) -> AsyncIterator[dict]:
        """
        Stream a message response.

        Args:
            messages: Conversation messages
            system: System prompt
            tools: Tool definitions

        Yields:
            Response chunks with type and content
        """
        import asyncio

        client = self._get_client()
        request = self._build_request(messages, system, tools)

        # Stream response using sync client in executor
        loop = asyncio.get_event_loop()
        events = await loop.run_in_executor(
            None, lambda: list(self._stream_sync(client, request))
        )

        # Process events and yield chunks
        tool_state = {"current_tool": None, "current_tool_input": ""}

        for event in events:
            async for chunk in self._process_event(event, tool_state):
                yield chunk

    def _build_request(
        self,
        messages: list[dict],
        system: str | None,
        tools: list[dict] | None,
    ) -> dict:
        """Build request payload for Anthropic API."""
        request = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": self._convert_messages(messages),
        }

        if system:
            request["system"] = system

        if tools:
            request["tools"] = self._convert_tools(tools)

        return request

    def _stream_sync(self, client: object, request: dict) -> list[object]:
        """Synchronous streaming helper for executor."""
        with client.messages.stream(**request) as stream:  # type: ignore[attr-defined]
            return list(stream)

    async def _process_event(self, event: object, tool_state: dict) -> AsyncIterator[dict]:
        """Process a single streaming event and yield response chunks."""
        event_type = getattr(event, "type", None)

        if event_type == "content_block_start":
            self._handle_content_block_start(event, tool_state)

        elif event_type == "content_block_delta":
            chunk = self._handle_content_block_delta(event, tool_state)
            if chunk:
                yield chunk

        elif event_type == "content_block_stop":
            chunk = self._handle_content_block_stop(tool_state)
            if chunk:
                yield chunk

        elif event_type == "message_delta":
            chunk = self._handle_message_delta(event)
            if chunk:
                yield chunk

    def _handle_content_block_start(self, event: object, tool_state: dict) -> None:
        """Handle start of content block (e.g., tool use)."""
        block = event.content_block  # type: ignore[attr-defined]
        if hasattr(block, "type") and block.type == "tool_use":
            tool_state["current_tool"] = {
                "id": block.id,
                "name": block.name,
            }
            tool_state["current_tool_input"] = ""

    def _handle_content_block_delta(self, event: object, tool_state: dict) -> dict | None:
        """Handle content block delta (text or tool input)."""
        delta = event.delta  # type: ignore[attr-defined]
        if not hasattr(delta, "type"):
            return None

        if delta.type == "text_delta":
            return {"type": "text", "content": delta.text}

        if delta.type == "input_json_delta":
            tool_state["current_tool_input"] += delta.partial_json

        return None

    def _handle_content_block_stop(self, tool_state: dict) -> dict | None:
        """Handle end of content block (emit tool use if applicable)."""
        current_tool = tool_state.get("current_tool")
        if not current_tool:
            return None

        import json

        try:
            tool_input = (
                json.loads(tool_state["current_tool_input"])
                if tool_state["current_tool_input"]
                else {}
            )
        except json.JSONDecodeError:
            tool_input = {}

        chunk = {
            "type": "tool_use",
            "id": current_tool["id"],
            "name": current_tool["name"],
            "input": tool_input,
        }

        # Reset tool state
        tool_state["current_tool"] = None
        tool_state["current_tool_input"] = ""

        return chunk

    def _handle_message_delta(self, event: object) -> dict | None:
        """Handle message delta (token usage)."""
        usage = getattr(event, "usage", None)
        if not usage:
            return None

        return {
            "type": "message_end",
            "input_tokens": getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
        }

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """Convert messages to Anthropic format."""
        result = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            tool_results = msg.get("tool_results")

            if role == "system":
                continue  # System handled separately

            # Handle tool results
            if tool_results:
                result.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tr["tool_use_id"],
                            "content": tr["content"],
                        }
                        for tr in tool_results
                    ],
                })
            else:
                result.append({
                    "role": role,
                    "content": content,
                })

        return result

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert tools to Anthropic format."""
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "input_schema": tool["input_schema"],
            }
            for tool in tools
        ]
