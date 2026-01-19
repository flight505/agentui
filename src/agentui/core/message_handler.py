"""
Message processing and streaming.

Handles LLM response streaming, tool call collection, and message state management.
"""

import logging
from typing import Any

from agentui.types import AgentState, Message, StreamChunk

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles message processing and streaming."""

    def __init__(self, state: AgentState):
        """Initialize the message handler.

        Args:
            state: Agent state containing message history
        """
        self.state = state
        self._cancel_requested = False

    def request_cancel(self) -> None:
        """Request cancellation of current processing."""
        self._cancel_requested = True

    def reset_cancel(self) -> None:
        """Reset cancellation flag."""
        self._cancel_requested = False

    def is_cancelled(self) -> bool:
        """Check if cancellation was requested."""
        return self._cancel_requested

    async def stream_provider_response(
        self, provider: Any, system_prompt: str, tool_schemas: list[dict] | None
    ) -> tuple[list[StreamChunk], list[dict], bool]:
        """
        Stream response from provider and collect chunks and tool calls.

        Args:
            provider: LLM provider instance
            system_prompt: System prompt for the LLM
            tool_schemas: Optional list of tool schemas

        Returns:
            Tuple of (chunks_to_yield, tool_calls, should_return_early)
        """
        messages = [
            {"role": msg.role, "content": msg.content} for msg in self.state.messages
        ]

        full_response = ""
        tool_calls = []
        chunks_to_yield = []

        try:
            async for chunk in provider.stream_message(
                messages=messages,
                system=system_prompt,
                tools=tool_schemas,
            ):
                if self._cancel_requested:
                    break

                chunk_type = chunk.get("type")

                if chunk_type == "text":
                    text = chunk.get("content", "")
                    full_response += text
                    chunks_to_yield.append(StreamChunk(content=text))

                elif chunk_type == "tool_use":
                    tool_calls.append(chunk)

                elif chunk_type == "message_end":
                    self._update_token_counts(chunk)
                    chunks_to_yield.append(
                        StreamChunk(
                            content="",
                            is_complete=not tool_calls,
                            input_tokens=chunk.get("input_tokens"),
                            output_tokens=chunk.get("output_tokens"),
                        )
                    )

        except Exception as e:
            logger.error(f"Provider error: {e}")
            chunks_to_yield.append(
                StreamChunk(
                    content=f"\n\nError: {e}",
                    is_complete=True,
                )
            )
            return chunks_to_yield, [], True

        # Add assistant message to state
        if full_response or tool_calls:
            self.state.messages.append(
                Message(
                    role="assistant",
                    content=full_response,
                    tool_calls=tool_calls if tool_calls else None,
                )
            )

        return chunks_to_yield, tool_calls, False

    def _update_token_counts(self, chunk: dict) -> None:
        """Update token counts from message_end chunk."""
        if chunk.get("input_tokens"):
            self.state.total_input_tokens += chunk["input_tokens"]
        if chunk.get("output_tokens"):
            self.state.total_output_tokens += chunk["output_tokens"]

    def add_user_message(self, content: str) -> None:
        """Add a user message to the state."""
        self.state.messages.append(Message(role="user", content=content))

    def add_tool_results(self, tool_results: list[Any]) -> None:
        """Add tool results to message state."""
        for result in tool_results:
            content = result.error if result.error else str(result.result)
            self.state.messages.append(
                Message(
                    role="user",
                    content=f"Tool result for {result.tool_name}: {content}",
                    tool_results=[
                        {
                            "tool_use_id": result.tool_id,
                            "content": content,
                        }
                    ],
                )
            )
