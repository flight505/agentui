"""TUI Bridge for Go subprocess communication."""

import asyncio
import json
import logging
import shutil
import subprocess
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from agentui.bridge.base import BaseBridge
from agentui.protocol import (
    Message,
    MessageType,
    alert_payload,
    clear_payload,
    code_payload,
    confirm_payload,
    create_message,
    create_request,
    done_payload,
    form_payload,
    markdown_payload,
    progress_payload,
    select_payload,
    spinner_payload,
    status_payload,
    table_payload,
    text_payload,
)

logger = logging.getLogger(__name__)


class BridgeError(Exception):
    """Base exception for bridge errors."""
    pass


class ConnectionError(BridgeError):
    """TUI process connection error."""
    pass


class ProtocolError(BridgeError):
    """Protocol communication error."""
    pass


@dataclass
class TUIConfig:
    """Configuration for the TUI."""
    theme: str = "catppuccin-mocha"
    app_name: str = "AgentUI"
    tagline: str = "AI Agent Interface"
    tui_path: str | None = None
    debug: bool = False
    reconnect_attempts: int = 3
    reconnect_delay: float = 1.0


class TUIBridge(BaseBridge):
    """
    Manages communication with the Go TUI subprocess.

    Features:
    - Async message passing
    - Request/response correlation
    - Graceful error handling
    - Connection recovery
    """

    def __init__(self, config: TUIConfig | None = None):
        self.config = config or TUIConfig()
        self._process: subprocess.Popen | None = None
        self._reader_task: asyncio.Task | None = None
        self._writer_task: asyncio.Task | None = None
        self._pending_requests: dict[str, asyncio.Future] = {}
        self._event_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._outgoing_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._running = False
        self._shutting_down = False
        self._lock = asyncio.Lock()

    def _find_tui_binary(self) -> str:
        """Find the agentui-tui binary."""
        if self.config.tui_path:
            path = Path(self.config.tui_path)
            if path.exists():
                return str(path)
            raise FileNotFoundError(f"TUI binary not found at: {path}")

        # Check common locations
        candidates = [
            # Development location (relative to this file)
            Path(__file__).parent.parent.parent.parent / "bin" / "agentui-tui",
            # Installed via pip (in package)
            Path(__file__).parent / "bin" / "agentui-tui",
            # System PATH
            "agentui-tui",
        ]

        for candidate in candidates:
            if isinstance(candidate, Path):
                if candidate.exists():
                    return str(candidate)
            else:
                found = shutil.which(candidate)
                if found:
                    return found

        raise FileNotFoundError(
            "agentui-tui binary not found. "
            "Build it with 'make build-tui' or set tui_path in config."
        )

    async def start(self) -> None:
        """Start the TUI subprocess."""
        if self._running:
            return

        async with self._lock:
            await self._start_process()

    async def _start_process(self) -> None:
        """Internal method to start the TUI process."""
        tui_binary = self._find_tui_binary()

        cmd = [
            tui_binary,
            "--theme", self.config.theme,
            "--name", self.config.app_name,
            "--tagline", self.config.tagline,
        ]

        if self.config.debug:
            logger.info(f"Starting TUI: {' '.join(cmd)}")

        try:
            self._process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
            )
        except OSError as e:
            raise ConnectionError(f"Failed to start TUI process: {e}")

        self._running = True
        self._shutting_down = False

        # Start reader and writer tasks
        self._reader_task = asyncio.create_task(self._read_loop())
        self._writer_task = asyncio.create_task(self._write_loop())

        # Start stderr reader for debugging
        if self.config.debug:
            asyncio.create_task(self._stderr_loop())

    async def stop(self) -> None:
        """Stop the TUI subprocess gracefully."""
        if not self._running:
            return

        self._shutting_down = True
        self._running = False

        # Cancel pending requests
        for future in self._pending_requests.values():
            if not future.done():
                future.cancel()
        self._pending_requests.clear()

        # Cancel tasks
        for task in [self._reader_task, self._writer_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await asyncio.wait_for(task, timeout=1.0)
                except (TimeoutError, asyncio.CancelledError):
                    pass

        # Terminate process
        if self._process:
            process = self._process  # Capture for type safety in lambda
            try:
                process.terminate()
                await asyncio.get_event_loop().run_in_executor(
                    None, lambda: process.wait(timeout=2)
                )
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                logger.warning(f"Error stopping TUI process: {e}")
            finally:
                self._process = None

    async def _read_loop(self) -> None:
        """Read messages from TUI stdout."""
        if not self._process or not self._process.stdout:
            return

        loop = asyncio.get_event_loop()

        while self._running:
            try:
                line = await loop.run_in_executor(
                    None, self._process.stdout.readline
                )

                if not line:
                    await self._handle_closed_stdout()
                    break

                await self._process_line(line.strip())

            except asyncio.CancelledError:
                break
            except Exception as e:
                if self._running and not self._shutting_down:
                    logger.error(f"Error reading from TUI: {e}")
                break

    async def _handle_closed_stdout(self) -> None:
        """Handle TUI process closing stdout."""
        if not self._shutting_down:
            logger.warning("TUI process closed stdout")
            await self._handle_disconnect()

    async def _process_line(self, line: str) -> None:
        """Process a single line from TUI stdout."""
        if not line:
            return

        if self.config.debug:
            logger.debug(f"← TUI: {line[:100]}...")

        try:
            msg = Message.from_json(line)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from TUI: {e}")
            return

        await self._route_message(msg)

    async def _route_message(self, msg: Message) -> None:
        """Route message to pending request or event queue."""
        if msg.id and msg.id in self._pending_requests:
            future = self._pending_requests.pop(msg.id)
            if not future.done():
                future.set_result(msg.payload)
        else:
            await self._event_queue.put(msg)

    async def _write_loop(self) -> None:
        """Write messages to TUI stdin."""
        while self._running:
            try:
                msg = await asyncio.wait_for(
                    self._outgoing_queue.get(),
                    timeout=0.1
                )
                await self._send_raw(msg)
            except TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self._running:
                    logger.error(f"Error writing to TUI: {e}")

    async def _stderr_loop(self) -> None:
        """Read and log stderr from TUI."""
        if not self._process or not self._process.stderr:
            return

        loop = asyncio.get_event_loop()

        while self._running:
            try:
                line = await loop.run_in_executor(
                    None, self._process.stderr.readline
                )
                if line:
                    logger.debug(f"TUI stderr: {line.strip()}")
                elif not self._running:
                    break
            except Exception:
                break

    async def _handle_disconnect(self) -> None:
        """Handle unexpected TUI disconnect."""
        if self._shutting_down:
            return

        logger.warning("TUI disconnected unexpectedly")

        # Try to reconnect
        for attempt in range(self.config.reconnect_attempts):
            logger.info(f"Reconnection attempt {attempt + 1}/{self.config.reconnect_attempts}")
            await asyncio.sleep(self.config.reconnect_delay)

            try:
                await self._start_process()
                logger.info("Reconnected to TUI")
                return
            except Exception as e:
                logger.warning(f"Reconnection failed: {e}")

        logger.error("Failed to reconnect to TUI")
        self._running = False

    async def _send_raw(self, message: Message) -> None:
        """Send a message directly to TUI stdin."""
        if not self._process or not self._process.stdin:
            raise ConnectionError("TUI not connected")

        line = message.to_json() + "\n"

        if self.config.debug:
            logger.debug(f"→ TUI: {line[:100]}...")

        try:
            self._process.stdin.write(line)
            self._process.stdin.flush()
        except BrokenPipeError:
            raise ConnectionError("TUI connection broken")
        except Exception as e:
            raise ProtocolError(f"Failed to send message: {e}")

    async def send(self, message: Message) -> None:
        """Queue a message to be sent to the TUI."""
        if not self._running:
            raise ConnectionError("TUI not running")
        await self._outgoing_queue.put(message)

    async def send_sync(self, message: Message) -> None:
        """Send a message synchronously (bypass queue)."""
        if not self._running:
            raise ConnectionError("TUI not running")
        await self._send_raw(message)

    async def request(self, message: Message, timeout: float = 30.0) -> Any:
        """Send a request and wait for response."""
        if not message.id:
            raise ValueError("Request must have an ID")

        if not self._running:
            raise ConnectionError("TUI not running")

        future = asyncio.get_event_loop().create_future()
        self._pending_requests[message.id] = future

        try:
            await self._send_raw(message)
            return await asyncio.wait_for(future, timeout=timeout)
        except TimeoutError:
            self._pending_requests.pop(message.id, None)
            raise ProtocolError(f"Request timed out after {timeout}s")
        except Exception:
            self._pending_requests.pop(message.id, None)
            raise

    async def events(self) -> AsyncIterator[Message]:
        """Iterate over user events from the TUI."""
        while self._running:
            try:
                msg = await asyncio.wait_for(
                    self._event_queue.get(),
                    timeout=0.1
                )
                yield msg
            except TimeoutError:
                continue
            except asyncio.CancelledError:
                break

    @property
    def is_running(self) -> bool:
        """Check if the bridge is running."""
        return self._running

    # --- Convenience methods ---

    async def send_text(self, content: str, done: bool = False) -> None:
        """Send streaming text."""
        msg = create_message(MessageType.TEXT, text_payload(content, done))
        await self.send(msg)

    async def send_markdown(self, content: str, title: str | None = None) -> None:
        """Send markdown content."""
        msg = create_message(MessageType.MARKDOWN, markdown_payload(content, title))
        await self.send(msg)

    async def send_progress(
        self,
        message: str,
        percent: float | None = None,
        steps: list[dict] | None = None,
    ) -> None:
        """Send progress update."""
        msg = create_message(
            MessageType.PROGRESS,
            progress_payload(message, percent, steps)
        )
        await self.send(msg)

    async def request_form(
        self,
        fields: list[dict],
        title: str | None = None,
        description: str | None = None,
    ) -> dict | None:
        """Show a form and wait for response."""
        msg = create_request(
            MessageType.FORM,
            form_payload(fields, title, description)
        )
        result = await self.request(msg)
        return result.get("values") if result else None

    async def send_table(
        self,
        columns: list[str],
        rows: list[list[str]],
        title: str | None = None,
        footer: str | None = None,
    ) -> None:
        """Send a data table."""
        msg = create_message(
            MessageType.TABLE,
            table_payload(columns, rows, title, footer)
        )
        await self.send(msg)

    async def send_code(
        self,
        code: str,
        language: str = "text",
        title: str | None = None,
    ) -> None:
        """Send a code block."""
        msg = create_message(
            MessageType.CODE,
            code_payload(code, language, title)
        )
        await self.send(msg)

    async def request_confirm(
        self,
        message: str,
        title: str | None = None,
        destructive: bool = False,
    ) -> bool:
        """Show confirmation dialog and wait for response."""
        msg = create_request(
            MessageType.CONFIRM,
            confirm_payload(message, title, destructive=destructive)
        )
        result = await self.request(msg)
        return result.get("confirmed", False) if result else False

    async def request_select(
        self,
        label: str,
        options: list[str],
        default: str | None = None,
    ) -> str | None:
        """Show selection and wait for response."""
        msg = create_request(
            MessageType.SELECT,
            select_payload(label, options, default)
        )
        result = await self.request(msg)
        return result.get("value") if result else None

    async def send_alert(
        self,
        message: str,
        severity: str = "info",
        title: str | None = None,
    ) -> None:
        """Show an alert notification."""
        msg = create_message(
            MessageType.ALERT,
            alert_payload(message, severity, title)
        )
        await self.send(msg)

    async def send_spinner(self, message: str) -> None:
        """Show a loading spinner."""
        msg = create_message(MessageType.SPINNER, spinner_payload(message))
        await self.send(msg)

    async def send_status(
        self,
        message: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
    ) -> None:
        """Update the status bar."""
        tokens = None
        if input_tokens is not None or output_tokens is not None:
            tokens = {"input": input_tokens or 0, "output": output_tokens or 0}
        msg = create_message(MessageType.STATUS, status_payload(message, tokens))
        await self.send(msg)

    async def send_clear(self, scope: str = "chat") -> None:
        """Clear part of the UI."""
        msg = create_message(MessageType.CLEAR, clear_payload(scope))
        await self.send(msg)

    async def send_done(self, summary: str | None = None) -> None:
        """Signal completion."""
        msg = create_message(MessageType.DONE, done_payload(summary))
        await self.send(msg)


@asynccontextmanager
async def managed_bridge(config: TUIConfig | None = None, fallback: bool = True):
    """Context manager for bridge lifecycle."""
    from agentui.bridge import create_bridge
    bridge = create_bridge(config, fallback)
    await bridge.start()
    try:
        yield bridge
    finally:
        await bridge.stop()
