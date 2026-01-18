"""
Agent Core - The main agent execution loop.

Handles:
- Message processing with streaming
- Tool execution with UI support
- Provider communication
- Graceful error handling
"""

import asyncio
import inspect
import logging
from typing import Any, AsyncIterator

from agentui.types import (
    AgentConfig,
    AgentState,
    ToolDefinition,
    ToolResult,
    StreamChunk,
    Message,
)
from agentui.bridge import TUIBridge, CLIBridge, TUIConfig, create_bridge, BridgeError
from agentui.primitives import (
    UIForm, UIConfirm, UISelect, UIProgress, UITable, UICode,
    UIAlert, UIText, UIMarkdown
)
from agentui.protocol import MessageType
from agentui.component_catalog import ComponentCatalog
from agentui.component_selector import ComponentSelector

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Base exception for agent errors."""
    pass


class ToolExecutionError(AgentError):
    """Error during tool execution."""
    pass


class AgentCore:
    """
    Core agent execution engine.
    
    Manages the agent loop, tool execution, and UI updates.
    """
    
    def __init__(
        self,
        config: AgentConfig | None = None,
        bridge: TUIBridge | CLIBridge | None = None,
    ):
        self.config = config or AgentConfig()
        self.bridge = bridge
        self.state = AgentState()
        self.tools: dict[str, ToolDefinition] = {}
        self._provider = None
        self._setup_assistant = None  # Fallback when provider fails
        self._running = False
        self._cancel_requested = False

        # Enhance system prompt with component catalog (Phase 1: Generative UI)
        self._enhance_system_prompt_with_catalog()

        # Auto-register display_* tools (Phase 1: Generative UI)
        self._register_display_tools()
    
    def register_tool(self, tool: ToolDefinition) -> None:
        """Register a tool for the agent to use."""
        self.tools[tool.name] = tool
        logger.debug(f"Registered tool: {tool.name}")
    
    def get_tool_schemas(self) -> list[dict]:
        """Get tool schemas for the LLM."""
        return [tool.to_schema() for tool in self.tools.values()]

    def _enhance_system_prompt_with_catalog(self) -> None:
        """
        Enhance system prompt with component catalog (Phase 1: Generative UI).

        Adds LLM-friendly documentation of all available UI components,
        usage guidelines, and selection heuristics.
        """
        catalog_prompt = ComponentCatalog.get_catalog_prompt()

        # Append catalog to existing system prompt
        enhanced_prompt = f"""{self.config.system_prompt}

{catalog_prompt}
"""
        self.config.system_prompt = enhanced_prompt
        logger.debug("Enhanced system prompt with component catalog")

    def _register_display_tools(self) -> None:
        """
        Auto-register display_* tools for UI primitives (Phase 1: Generative UI).

        Registers tools for:
        - display_table: Show tabular data
        - display_form: Collect user input
        - display_code: Show syntax-highlighted code
        - display_progress: Show progress indicators
        - display_confirm: Ask yes/no questions
        - display_alert: Show notifications
        - display_select: Single-choice selection
        """
        tool_schemas = ComponentCatalog.get_tool_schemas()

        for schema in tool_schemas:
            tool_name = schema["name"]

            # Create handler that sends UI message via bridge
            handler = self._create_display_handler(tool_name, schema)

            # Register tool
            self.register_tool(ToolDefinition(
                name=tool_name,
                description=schema["description"],
                parameters=schema["input_schema"],
                handler=handler,
                is_ui_tool=True,
            ))

        logger.debug(f"Auto-registered {len(tool_schemas)} display_* tools")

    def _create_display_handler(self, tool_name: str, schema: dict):
        """
        Create handler function for a display_* tool.

        The handler sends the appropriate UI message via the bridge.
        """
        async def handler(**kwargs):
            if not self.bridge:
                # No bridge available, return text representation
                return f"[Would display {tool_name} with: {kwargs}]"

            # Map tool name to message type (remove 'display_' prefix)
            msg_type = tool_name.replace("display_", "")

            # Send message via bridge
            try:
                if msg_type == "form":
                    # Forms return data, use request
                    result = await self.bridge.request_form(
                        fields=kwargs.get("fields", []),
                        title=kwargs.get("title"),
                        description=kwargs.get("description"),
                    )
                    return result
                elif msg_type == "confirm":
                    # Confirms return bool, use request
                    result = await self.bridge.request_confirm(
                        message=kwargs["message"],
                        title=kwargs.get("title"),
                        destructive=kwargs.get("destructive", False),
                    )
                    return result
                elif msg_type == "select":
                    # Selects return choice, use request
                    result = await self.bridge.request_select(
                        label=kwargs["label"],
                        options=kwargs["options"],
                        default=kwargs.get("default"),
                    )
                    return result
                elif msg_type == "table":
                    await self.bridge.send_table(
                        columns=kwargs["columns"],
                        rows=kwargs["rows"],
                        title=kwargs.get("title"),
                        footer=kwargs.get("footer"),
                    )
                    return f"Displayed table: {kwargs.get('title', 'Table')}"
                elif msg_type == "code":
                    await self.bridge.send_code(
                        code=kwargs["code"],
                        language=kwargs.get("language", "text"),
                        title=kwargs.get("title"),
                    )
                    return f"Displayed code: {kwargs.get('title', 'Code')}"
                elif msg_type == "progress":
                    await self.bridge.send_progress(
                        message=kwargs["message"],
                        percent=kwargs.get("percent"),
                        steps=kwargs.get("steps"),
                    )
                    return f"Displayed progress: {kwargs['message']}"
                elif msg_type == "alert":
                    await self.bridge.send_alert(
                        message=kwargs["message"],
                        severity=kwargs.get("severity", "info"),
                        title=kwargs.get("title"),
                    )
                    return f"Displayed alert: {kwargs['message']}"
                else:
                    return f"Unknown display type: {msg_type}"

            except BridgeError as e:
                logger.error(f"Failed to send {msg_type} message: {e}")
                return f"Error displaying {msg_type}: {e}"

        return handler

    async def _get_provider(self):
        """Get or create the LLM provider."""
        if self._provider is None:
            provider_name = self.config.provider.value
            
            if provider_name == "claude":
                from agentui.providers.claude import ClaudeProvider
                self._provider = ClaudeProvider(
                    model=self.config.model,
                    api_key=self.config.api_key,
                    max_tokens=self.config.max_tokens,
                )
            elif provider_name == "openai":
                from agentui.providers.openai import OpenAIProvider
                self._provider = OpenAIProvider(
                    model=self.config.model,
                    api_key=self.config.api_key,
                    max_tokens=self.config.max_tokens,
                )
            else:
                raise ValueError(f"Unsupported provider: {provider_name}")
            
            logger.info(f"Initialized provider: {provider_name}")
        
        return self._provider
    
    async def execute_tool(self, tool_name: str, tool_id: str, arguments: dict) -> ToolResult:
        """Execute a tool and return the result."""
        if tool_name not in self.tools:
            logger.warning(f"Unknown tool requested: {tool_name}")
            return ToolResult(
                tool_name=tool_name,
                tool_id=tool_id,
                result=None,
                error=f"Unknown tool: {tool_name}",
            )
        
        tool = self.tools[tool_name]
        logger.debug(f"Executing tool: {tool_name} with args: {arguments}")
        
        # Check if confirmation is required
        if tool.requires_confirmation and self.bridge:
            try:
                confirmed = await self.bridge.request_confirm(
                    f"Allow tool '{tool_name}' to execute?",
                    title="Tool Confirmation",
                )
                if not confirmed:
                    logger.info(f"Tool {tool_name} execution cancelled by user")
                    return ToolResult(
                        tool_name=tool_name,
                        tool_id=tool_id,
                        result=None,
                        error="Tool execution cancelled by user",
                    )
            except BridgeError as e:
                logger.error(f"Failed to request confirmation: {e}")
        
        # Update status
        if self.bridge:
            try:
                await self.bridge.send_spinner(f"Running {tool_name}...")
            except BridgeError:
                pass
        
        try:
            # Execute the handler
            if asyncio.iscoroutinefunction(tool.handler):
                result = await tool.handler(**arguments)
            else:
                # Run sync function in executor
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None, lambda: tool.handler(**arguments)
                )
            
            # Phase 2: Data-Driven Component Selection
            # Auto-select UI component if result is not already a UI primitive
            is_ui = tool.is_ui_tool or isinstance(
                result, (UIForm, UIConfirm, UISelect, UIProgress, UITable, UICode, UIAlert, UIText, UIMarkdown)
            )

            # If not a UI tool and not already a UI primitive, auto-select component
            if not is_ui and not isinstance(
                result, (UIForm, UIConfirm, UISelect, UIProgress, UITable, UICode, UIAlert, UIText, UIMarkdown)
            ):
                # Auto-select component based on data structure
                component_type, ui_primitive = ComponentSelector.select_component(result)

                if component_type != "text" or isinstance(ui_primitive, (UITable, UICode, UIMarkdown)):
                    # Replace result with UI primitive
                    logger.debug(f"Auto-selected component: {component_type} for tool {tool_name}")
                    result = ui_primitive
                    is_ui = True

            logger.debug(f"Tool {tool_name} completed successfully")

            return ToolResult(
                tool_name=tool_name,
                tool_id=tool_id,
                result=result,
                is_ui=is_ui,
            )
            
        except Exception as e:
            logger.error(f"Tool {tool_name} execution failed: {e}")
            return ToolResult(
                tool_name=tool_name,
                tool_id=tool_id,
                result=None,
                error=str(e),
            )
    
    async def handle_ui_result(self, result: Any) -> Any:
        """Handle UI primitive results from tools."""
        if not self.bridge:
            return result
        
        try:
            if isinstance(result, UIForm):
                return await self.bridge.request_form(
                    fields=[f.to_dict() for f in result.fields],
                    title=result.title,
                    description=result.description,
                )
            
            elif isinstance(result, UIConfirm):
                return await self.bridge.request_confirm(
                    result.message,
                    title=result.title,
                    destructive=result.destructive,
                )
            
            elif isinstance(result, UISelect):
                return await self.bridge.request_select(
                    result.label,
                    result.options,
                    result.default,
                )
            
            elif isinstance(result, UIProgress):
                await self.bridge.send_progress(
                    result.message,
                    result.percent,
                    [s.to_dict() for s in result.steps] if result.steps else None,
                )
                return None
            
            elif isinstance(result, UITable):
                await self.bridge.send_table(
                    result.columns,
                    result.rows,
                    result.title,
                    result.footer,
                )
                return None
            
            elif isinstance(result, UICode):
                await self.bridge.send_code(
                    result.code,
                    result.language,
                    result.title,
                )
                return None
            
        except BridgeError as e:
            logger.error(f"Failed to handle UI result: {e}")
        
        return result
    
    async def process_message(self, user_input: str) -> AsyncIterator[StreamChunk]:
        """
        Process a user message and yield response chunks.
        
        This is the main agent loop for a single turn.
        """
        self._cancel_requested = False
        
        # Add user message to state
        self.state.messages.append(Message(role="user", content=user_input))
        
        try:
            provider = await self._get_provider()
        except Exception as e:
            logger.error(f"Failed to get provider: {e}")

            # Use setup assistant instead of failing
            if self._setup_assistant is None:
                from agentui.setup_assistant import SetupAssistant
                self._setup_assistant = SetupAssistant(provider_error=str(e))

            # Let setup assistant handle the conversation
            async for response_text in self._setup_assistant.process_message(user_input):
                yield StreamChunk(content=response_text, is_complete=True)
            return
        
        iterations = 0
        
        while iterations < self.config.max_tool_iterations:
            if self._cancel_requested:
                logger.info("Processing cancelled by user")
                yield StreamChunk(content=" [Cancelled]", is_complete=True)
                return
            
            iterations += 1
            
            # Build messages for provider
            messages = [
                {"role": msg.role, "content": msg.content}
                for msg in self.state.messages
            ]
            
            # Stream response from provider
            full_response = ""
            tool_calls = []
            
            try:
                async for chunk in provider.stream_message(
                    messages=messages,
                    system=self.config.system_prompt,
                    tools=self.get_tool_schemas() if self.tools else None,
                ):
                    if self._cancel_requested:
                        break
                    
                    if chunk.get("type") == "text":
                        text = chunk.get("content", "")
                        full_response += text
                        yield StreamChunk(content=text)
                    
                    elif chunk.get("type") == "tool_use":
                        tool_calls.append(chunk)
                    
                    elif chunk.get("type") == "message_end":
                        yield StreamChunk(
                            content="",
                            is_complete=not tool_calls,  # Complete if no tool calls
                            input_tokens=chunk.get("input_tokens"),
                            output_tokens=chunk.get("output_tokens"),
                        )
                        if chunk.get("input_tokens"):
                            self.state.total_input_tokens += chunk["input_tokens"]
                        if chunk.get("output_tokens"):
                            self.state.total_output_tokens += chunk["output_tokens"]
                        
            except Exception as e:
                logger.error(f"Provider error: {e}")
                yield StreamChunk(
                    content=f"\n\nError: {e}",
                    is_complete=True,
                )
                return
            
            # If no tool calls, we're done
            if not tool_calls:
                if full_response:
                    self.state.messages.append(
                        Message(role="assistant", content=full_response)
                    )
                break
            
            # Add assistant message with tool calls
            self.state.messages.append(
                Message(
                    role="assistant",
                    content=full_response,
                    tool_calls=tool_calls,
                )
            )
            
            # Execute tools
            tool_results = []
            for call in tool_calls:
                if self._cancel_requested:
                    break
                
                result = await self.execute_tool(
                    tool_name=call["name"],
                    tool_id=call["id"],
                    arguments=call.get("input", {}),
                )
                
                # Handle UI results
                if result.is_ui and result.result:
                    ui_response = await self.handle_ui_result(result.result)
                    if ui_response is not None:
                        result = ToolResult(
                            tool_name=result.tool_name,
                            tool_id=result.tool_id,
                            result=ui_response,
                        )
                
                tool_results.append(result)
            
            # Add tool results to messages
            for result in tool_results:
                content = result.error if result.error else str(result.result)
                self.state.messages.append(
                    Message(
                        role="user",
                        content=f"Tool result for {result.tool_name}: {content}",
                        tool_results=[{
                            "tool_use_id": result.tool_id,
                            "content": content,
                        }],
                    )
                )
        
        # Final completion marker
        yield StreamChunk(content="", is_complete=True)
    
    def cancel(self) -> None:
        """Request cancellation of current processing."""
        self._cancel_requested = True
    
    async def run_loop(self) -> None:
        """
        Run the main agent loop.
        
        Listens for user input and processes messages.
        """
        if not self.bridge:
            raise RuntimeError("Bridge not set")
        
        self._running = True
        
        # Send initial status
        try:
            await self.bridge.send_status(
                f"Ready · {self.config.provider.value}",
                input_tokens=0,
                output_tokens=0,
            )
        except BridgeError as e:
            logger.error(f"Failed to send initial status: {e}")
        
        # Main loop
        try:
            async for event in self.bridge.events():
                if not self._running:
                    break
                
                event_type = event.type
                
                if event_type == MessageType.INPUT.value:
                    user_input = event.payload.get("content", "")
                    if not user_input:
                        continue
                    
                    logger.debug(f"Processing input: {user_input[:50]}...")
                    
                    try:
                        async for chunk in self.process_message(user_input):
                            if chunk.content:
                                await self.bridge.send_text(
                                    chunk.content,
                                    done=chunk.is_complete,
                                )
                            
                            if chunk.is_complete:
                                await self.bridge.send_status(
                                    f"Ready · {self.config.provider.value}",
                                    input_tokens=self.state.total_input_tokens,
                                    output_tokens=self.state.total_output_tokens,
                                )
                        
                        await self.bridge.send_done()
                        
                    except BridgeError as e:
                        logger.error(f"Bridge error while processing: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                        try:
                            await self.bridge.send_alert(
                                str(e),
                                severity="error",
                                title="Error",
                            )
                        except BridgeError:
                            pass
                
                elif event_type == MessageType.QUIT.value:
                    logger.info("Quit requested")
                    self._running = False
                    break
                
                elif event_type == MessageType.CANCEL.value:
                    logger.info("Cancel requested")
                    self.cancel()
                
                elif event_type == "resize":
                    # Handle resize if needed
                    pass
                    
        except asyncio.CancelledError:
            logger.info("Agent loop cancelled")
        except Exception as e:
            logger.error(f"Unexpected error in agent loop: {e}")
        finally:
            self._running = False
    
    def stop(self) -> None:
        """Stop the agent loop."""
        self._running = False
        self._cancel_requested = True
