"""Bridge package for UI communication."""

import logging

from agentui.bridge.base import BaseBridge
from agentui.bridge.cli_bridge import CLIBridge
from agentui.bridge.tui_bridge import (
    BridgeError,
    ConnectionError,
    ProtocolError,
    TUIBridge,
    TUIConfig,
    managed_bridge,
)

logger = logging.getLogger(__name__)

__all__ = [
    "BaseBridge",
    "TUIBridge",
    "CLIBridge",
    "TUIConfig",
    "BridgeError",
    "ConnectionError",
    "ProtocolError",
    "managed_bridge",
    "create_bridge",
]


def create_bridge(config: TUIConfig | None = None, fallback: bool = True) -> TUIBridge | CLIBridge:
    """
    Create a bridge instance.

    Tries to use TUI, falls back to CLI if not available.
    """
    config = config or TUIConfig()

    try:
        bridge = TUIBridge(config)
        bridge._find_tui_binary()
        return bridge
    except FileNotFoundError:
        if fallback:
            logger.info("TUI binary not found, using CLI fallback")
            return CLIBridge(config)
        raise
