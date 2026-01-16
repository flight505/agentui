"""
AgentUI - Beautiful AI agent applications with Charm-quality TUIs.
"""

from agentui.app import AgentApp
from agentui.bridge import TUIBridge, CLIBridge, TUIConfig, create_bridge
from agentui.core import AgentCore
from agentui.primitives import (
    UIForm,
    UIFormField,
    UIProgress,
    UIProgressStep,
    UITable,
    UICode,
    UIConfirm,
    UISelect,
    UIAlert,
    UIText,
    UIMarkdown,
)
from agentui.protocol import (
    Message,
    MessageType,
    form_field,
    form_payload,
    table_payload,
    code_payload,
    progress_payload,
    confirm_payload,
    select_payload,
    alert_payload,
)

__version__ = "0.1.0"

__all__ = [
    # Main classes
    "AgentApp",
    "AgentCore",
    "TUIBridge",
    "CLIBridge",
    "TUIConfig",
    "create_bridge",
    # UI Primitives
    "UIForm",
    "UIFormField",
    "UIProgress",
    "UIProgressStep",
    "UITable",
    "UICode",
    "UIConfirm",
    "UISelect",
    "UIAlert",
    "UIText",
    "UIMarkdown",
    # Protocol helpers
    "Message",
    "MessageType",
    "form_field",
    "form_payload",
    "table_payload",
    "code_payload",
    "progress_payload",
    "confirm_payload",
    "select_payload",
    "alert_payload",
]
