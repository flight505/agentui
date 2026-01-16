"""
Claude Provider - Anthropic Claude integration.
"""

import os
from typing import Any, AsyncIterator


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
    
    def _get_client(self):
        """Get or create the Anthropic client."""
        if self._client is None:
            try:
                import anthropic
            except ImportError:
                raise ImportError(
                    "anthropic package not installed. "
                    "Install with: pip install anthropic"
                )
            
            if not self.api_key:
                raise ValueError(
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
        
        # Build request
        request = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": self._convert_messages(messages),
        }
        
        if system:
            request["system"] = system
        
        if tools:
            request["tools"] = self._convert_tools(tools)
        
        # Stream response using sync client in executor
        # (anthropic doesn't have async streaming in all versions)
        loop = asyncio.get_event_loop()
        
        def stream_sync():
            with client.messages.stream(**request) as stream:
                for event in stream:
                    yield event
        
        # Collect events (simpler than true async for now)
        events = await loop.run_in_executor(None, lambda: list(stream_sync()))
        
        current_tool = None
        current_tool_input = ""
        
        for event in events:
            event_type = getattr(event, "type", None)
            
            if event_type == "content_block_start":
                block = event.content_block
                if hasattr(block, "type"):
                    if block.type == "tool_use":
                        current_tool = {
                            "id": block.id,
                            "name": block.name,
                        }
                        current_tool_input = ""
            
            elif event_type == "content_block_delta":
                delta = event.delta
                if hasattr(delta, "type"):
                    if delta.type == "text_delta":
                        yield {"type": "text", "content": delta.text}
                    elif delta.type == "input_json_delta":
                        current_tool_input += delta.partial_json
            
            elif event_type == "content_block_stop":
                if current_tool:
                    # Parse tool input
                    import json
                    try:
                        tool_input = json.loads(current_tool_input) if current_tool_input else {}
                    except json.JSONDecodeError:
                        tool_input = {}
                    
                    yield {
                        "type": "tool_use",
                        "id": current_tool["id"],
                        "name": current_tool["name"],
                        "input": tool_input,
                    }
                    current_tool = None
                    current_tool_input = ""
            
            elif event_type == "message_stop":
                pass
            
            elif event_type == "message_delta":
                usage = getattr(event, "usage", None)
                if usage:
                    yield {
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
