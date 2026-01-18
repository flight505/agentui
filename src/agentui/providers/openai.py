"""
OpenAI Provider - OpenAI GPT integration.
"""

import json
import os
from collections.abc import AsyncIterator


class OpenAIProvider:
    """
    Provider for OpenAI GPT models.
    
    Supports streaming responses and tool use.
    """

    DEFAULT_MODEL = "gpt-4o"

    def __init__(
        self,
        model: str | None = None,
        api_key: str | None = None,
        max_tokens: int = 4096,
    ):
        self.model = model or self.DEFAULT_MODEL
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.max_tokens = max_tokens
        self._client = None

    def _get_client(self):
        """Get or create the OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError:
                raise ImportError(
                    "openai package not installed. "
                    "Install with: uv sync --extra openai  (or: uv add openai)"
                )

            if not self.api_key:
                raise ValueError(
                    "OpenAI API key not found. "
                    "Set OPENAI_API_KEY environment variable or pass api_key."
                )

            self._client = OpenAI(api_key=self.api_key)

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

        # Build messages with system prompt
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(self._convert_messages(messages))

        # Build request
        request = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": all_messages,
            "stream": True,
        }

        if tools:
            request["tools"] = self._convert_tools(tools)

        # Stream response
        loop = asyncio.get_event_loop()

        def stream_sync():
            stream = client.chat.completions.create(**request)
            for chunk in stream:
                yield chunk

        events = await loop.run_in_executor(None, lambda: list(stream_sync()))

        # Track tool calls being built
        tool_calls = {}
        input_tokens = 0
        output_tokens = 0

        for chunk in events:
            delta = chunk.choices[0].delta if chunk.choices else None

            if not delta:
                continue

            # Text content
            if delta.content:
                yield {"type": "text", "content": delta.content}

            # Tool calls
            if delta.tool_calls:
                for tc in delta.tool_calls:
                    idx = tc.index

                    if idx not in tool_calls:
                        tool_calls[idx] = {
                            "id": tc.id or "",
                            "name": tc.function.name if tc.function else "",
                            "arguments": "",
                        }

                    if tc.id:
                        tool_calls[idx]["id"] = tc.id
                    if tc.function:
                        if tc.function.name:
                            tool_calls[idx]["name"] = tc.function.name
                        if tc.function.arguments:
                            tool_calls[idx]["arguments"] += tc.function.arguments

            # Usage info (in final chunk)
            if chunk.usage:
                input_tokens = chunk.usage.prompt_tokens
                output_tokens = chunk.usage.completion_tokens

        # Emit completed tool calls
        for tc in tool_calls.values():
            try:
                args = json.loads(tc["arguments"]) if tc["arguments"] else {}
            except json.JSONDecodeError:
                args = {}

            yield {
                "type": "tool_use",
                "id": tc["id"],
                "name": tc["name"],
                "input": args,
            }

        # Emit message end
        yield {
            "type": "message_end",
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
        }

    def _convert_messages(self, messages: list[dict]) -> list[dict]:
        """Convert messages to OpenAI format."""
        result = []

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            tool_results = msg.get("tool_results")
            tool_calls = msg.get("tool_calls")

            if role == "system":
                result.append({"role": "system", "content": content})

            elif role == "assistant":
                assistant_msg = {"role": "assistant", "content": content}

                # Add tool calls if present
                if tool_calls:
                    assistant_msg["tool_calls"] = [
                        {
                            "id": tc["id"],
                            "type": "function",
                            "function": {
                                "name": tc["name"],
                                "arguments": json.dumps(tc.get("input", {})),
                            },
                        }
                        for tc in tool_calls
                    ]

                result.append(assistant_msg)

            elif tool_results:
                # Tool results become separate messages in OpenAI
                for tr in tool_results:
                    result.append({
                        "role": "tool",
                        "tool_call_id": tr["tool_use_id"],
                        "content": tr["content"],
                    })

            else:
                result.append({"role": role, "content": content})

        return result

    def _convert_tools(self, tools: list[dict]) -> list[dict]:
        """Convert tools to OpenAI format."""
        return [
            {
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["input_schema"],
                },
            }
            for tool in tools
        ]
