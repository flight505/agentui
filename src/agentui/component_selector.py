"""
Component Selector - Intelligent component selection based on data structure.

Automatically selects the optimal UI component based on:
- Data type and structure
- Content analysis
- Size and complexity heuristics
- Optional context hints (Phase 4)

Inspired by CopilotKit's declarative generative UI pattern.
"""

import re
from collections.abc import Callable
from functools import wraps
from typing import Any, Literal

from agentui.primitives import (
    UIAlert,
    UICode,
    UIConfirm,
    UIForm,
    UIMarkdown,
    UIProgress,
    UISelect,
    UITable,
    UIText,
)

ComponentType = Literal[
    "table", "code", "progress", "form", "confirm",
    "select", "alert", "text", "markdown", "ui_primitive"
]


class ComponentSelector:
    """
    Intelligent component selection based on data structure.

    Heuristics:
    - List of dicts with consistent keys → Table
    - Dict with "code"/"language" → Code
    - String >500 chars with newlines → Code (auto-detect language)
    - Dict with "fields" → Form
    - Dict with "message"+"severity" → Alert
    - Dict with "percent"/"steps" → Progress
    - Default → Text
    """

    @staticmethod
    def select_component(
        data: Any, context: dict[str, Any] | None = None
    ) -> tuple[ComponentType, Any]:
        """
        Select UI component based on data structure and optional context.

        Args:
            data: Data to display
            context: Optional context hints for better selection
                - user_intent: What user asked for
                - data_size: "small"|"medium"|"large"
                - interaction_needed: bool
                - operation_duration: float (seconds)

        Returns:
            Tuple of (component_type, ui_primitive)
        """
        context = context or {}

        # Phase 4: Context-aware selection
        # Check for interaction hints first
        if context.get("interaction_needed"):
            if isinstance(data, bool) or "yes/no" in str(data).lower():
                return ("confirm", UIConfirm(message=str(data)))

        # Check for operation duration hints
        if context.get("operation_duration", 0) > 2.0:
            # Long operations should show progress
            if isinstance(data, dict) and "message" in data:
                return ("progress", UIProgress(
                    message=data.get("message", "Processing..."),
                    percent=data.get("percent"),
                ))

        # Apply data size hints for lists
        if context.get("data_size") == "large" and isinstance(data, list):
            if len(data) > 50:
                # Large dataset → table with footer
                if all(isinstance(item, dict) for item in data):
                    component_type, ui = ComponentSelector._list_of_dicts_to_table(data[:50])
                    if isinstance(ui, UITable):
                        ui.footer = f"Showing 50 of {len(data)} items"
                    return (component_type, ui)

        # Fall through to standard selection logic
        return ComponentSelector._select_component_impl(data)

    @staticmethod
    def _select_component_impl(data: Any) -> tuple[ComponentType, Any]:
        """
        Internal implementation: Select UI component based on data structure only.

        This is called after context-aware selection logic.

        Args:
            data: Data to display (can be dict, list, str, UI primitive, etc.)

        Returns:
            Tuple of (component_type, ui_primitive)
        """
        # Already a UI primitive - return as-is
        if isinstance(
            data,
            (UITable, UICode, UIForm, UIConfirm, UISelect, UIProgress, UIAlert, UIText, UIMarkdown),
        ):
            return ("ui_primitive", data)

        # Dispatch based on data type
        if isinstance(data, dict):
            return ComponentSelector._select_from_dict(data)
        if isinstance(data, list):
            return ComponentSelector._select_from_list(data)
        if isinstance(data, str):
            return ComponentSelector._select_from_string(data)
        if isinstance(data, bool):
            return ("text", UIText(content=str(data)))

        # Fallback to text
        return ("text", UIText(content=str(data)))

    @staticmethod
    def _select_from_dict(data: dict) -> tuple[ComponentType, Any]:
        """Select component from dictionary data."""
        # Handle _component override key
        if "_component" in data:
            return ComponentSelector._handle_component_override(data)

        # Check for UI primitive patterns using dict-based dispatch
        patterns = [
            (("columns", "rows"), ComponentSelector._dict_to_table),
            (("code", "language"), ComponentSelector._dict_to_code_block),
            (("fields",), ComponentSelector._dict_to_form),
            (("message", "severity"), ComponentSelector._dict_to_alert),
            (("percent",), ComponentSelector._dict_to_progress),
            (("steps",), ComponentSelector._dict_to_progress),
            (("label", "options"), ComponentSelector._dict_to_select),
        ]

        for required_keys, builder in patterns:
            if all(key in data for key in required_keys):
                return builder(data)

        # Single dict with multiple keys - might be good as code (JSON)
        if len(data) > 3:
            return ComponentSelector._dict_to_code(data)

        return ("text", UIText(content=str(data)))

    @staticmethod
    def _select_from_list(data: list) -> tuple[ComponentType, Any]:
        """Select component from list data."""
        if len(data) == 0:
            return ("text", UIText(content="[]"))

        # Check if all items are dicts with consistent keys
        if all(isinstance(item, dict) for item in data):
            # Single item or consistent schema → Table
            if len(data) == 1 or ComponentSelector._has_consistent_schema(data):
                return ComponentSelector._list_of_dicts_to_table(data)

        # List of primitives → Simple table with single column
        if all(isinstance(item, (str, int, float, bool)) for item in data):
            return ("table", UITable(
                columns=["Items"],
                rows=[[str(item)] for item in data],
            ))

        return ("text", UIText(content=str(data)))

    @staticmethod
    def _select_from_string(data: str) -> tuple[ComponentType, Any]:
        """Select component from string data."""
        # Very long string with newlines → Code block
        if len(data) > 500 and "\n" in data:
            language = ComponentSelector._detect_language(data)
            return ("code", UICode(code=data, language=language))

        # Markdown patterns (headers, lists, code blocks)
        if ComponentSelector._is_markdown(data):
            return ("markdown", UIMarkdown(content=data))

        # Code patterns in shorter strings
        if len(data) > 100 and ComponentSelector._has_code_patterns(data):
            language = ComponentSelector._detect_language(data)
            return ("code", UICode(code=data, language=language))

        return ("text", UIText(content=data))

    @staticmethod
    def _dict_to_table(data: dict) -> tuple[ComponentType, UITable]:
        """Convert dict with columns/rows to table."""
        return ("table", UITable(
            columns=data["columns"],
            rows=data["rows"],
            title=data.get("title"),
            footer=data.get("footer"),
        ))

    @staticmethod
    def _dict_to_code_block(data: dict) -> tuple[ComponentType, UICode]:
        """Convert dict with code/language to code block."""
        return ("code", UICode(
            code=data["code"],
            language=data["language"],
            title=data.get("title"),
            line_numbers=data.get("line_numbers", True),
        ))

    @staticmethod
    def _dict_to_form(data: dict) -> tuple[ComponentType, UIForm]:
        """Convert dict with fields to form."""
        return ("form", UIForm(
            fields=data["fields"],
            title=data.get("title"),
            description=data.get("description"),
        ))

    @staticmethod
    def _dict_to_alert(data: dict) -> tuple[ComponentType, UIAlert]:
        """Convert dict with message/severity to alert."""
        return ("alert", UIAlert(
            message=data["message"],
            severity=data["severity"],
            title=data.get("title"),
        ))

    @staticmethod
    def _dict_to_progress(data: dict) -> tuple[ComponentType, UIProgress]:
        """Convert dict with percent/steps to progress."""
        return ("progress", UIProgress(
            message=data.get("message", "Processing..."),
            percent=data.get("percent"),
            steps=data.get("steps"),
        ))

    @staticmethod
    def _dict_to_select(data: dict) -> tuple[ComponentType, UISelect]:
        """Convert dict with label/options to select."""
        return ("select", UISelect(
            label=data["label"],
            options=data["options"],
            default=data.get("default"),
        ))

    @staticmethod
    def _handle_component_override(data: dict) -> tuple[ComponentType, Any]:
        """Handle explicit _component override in data dict."""
        component_type = data.pop("_component")

        if component_type == "code":
            language = data.pop("_language", "text")
            code_data = data.pop("data", str(data))
            return ("code", UICode(
                code=code_data if isinstance(code_data, str) else str(code_data),
                language=language,
            ))

        if component_type == "table":
            # Extract columns/rows from data
            if "columns" in data and "rows" in data:
                return ("table", UITable(
                    columns=data["columns"],
                    rows=data["rows"],
                    title=data.get("title"),
                    footer=data.get("footer"),
                ))

        # Unknown override, treat as text
        return ("text", UIText(content=str(data)))

    @staticmethod
    def _has_consistent_schema(data: list[dict]) -> bool:
        """Check if list of dicts has consistent schema."""
        if not data or len(data) < 2:
            return False

        # Get all unique keys
        all_keys = set()
        for item in data:
            all_keys.update(item.keys())

        # Check overlap - require at least 50% consistency
        first_keys = set(data[0].keys())
        overlap = len(first_keys & all_keys) / len(all_keys) if all_keys else 0

        return overlap >= 0.5

    @staticmethod
    def _list_of_dicts_to_table(data: list[dict]) -> tuple[ComponentType, Any]:
        """Convert list of dicts to table."""
        if not data:
            return ("text", UIText(content="Empty list"))

        # Use keys from first item as columns
        columns = list(data[0].keys())

        # Build rows
        rows = []
        for item in data:
            row = [str(item.get(col, "")) for col in columns]
            rows.append(row)

        # Add footer if large dataset
        footer = None
        if len(data) > 50:
            footer = f"Showing {min(50, len(data))} of {len(data)} items"
            rows = rows[:50]  # Limit to first 50

        return ("table", UITable(
            columns=columns,
            rows=rows,
            footer=footer,
        ))

    @staticmethod
    def _dict_to_code(data: dict) -> tuple[ComponentType, UICode]:
        """Convert dict to JSON code block."""
        import json
        code = json.dumps(data, indent=2)
        return ("code", UICode(
            code=code,
            language="json",
            title="Data",
        ))

    @staticmethod
    def _detect_language(code: str) -> str:
        """Auto-detect programming language from code content."""
        # Language detection patterns
        patterns = {
            "python": [r"\bdef\s+\w+\(", r"\bclass\s+\w+", r"\bimport\s+\w+", r"\bfrom\s+\w+"],
            "javascript": [r"\bfunction\s+\w+", r"\bconst\s+\w+", r"\blet\s+\w+", r"=>\s*{"],
            "typescript": [r"\binterface\s+\w+", r"\btype\s+\w+\s*=", r": \w+\[\]"],
            "go": [r"\bfunc\s+\w+", r"\bpackage\s+\w+", r"\btype\s+\w+\s+struct"],
            "rust": [r"\bfn\s+\w+", r"\blet\s+mut\s+", r"\bpub\s+fn"],
            "json": [r'^\s*[\{\[]', r'"\s*:\s*"', r'"\s*:\s*\d+'],
            "yaml": [r'^\w+:', r'^\s+-\s+', r':\s*\|'],
            "bash": [r"^#!/bin/(ba)?sh", r"\$\{\w+\}", r"\becho\s+"],
            "sql": [r"\bSELECT\s+", r"\bFROM\s+", r"\bWHERE\s+", r"\bINSERT\s+INTO"],
        }

        # Count pattern matches for each language
        scores = {}
        for lang, lang_patterns in patterns.items():
            score = sum(
                1
                for pattern in lang_patterns
                if re.search(pattern, code, re.MULTILINE | re.IGNORECASE)
            )
            if score > 0:
                scores[lang] = score

        # Return language with highest score
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return "text"

    @staticmethod
    def _has_code_patterns(text: str) -> bool:
        """Check if text contains code-like patterns."""
        code_indicators = [
            r"\bdef\s+\w+",      # Python function
            r"\bclass\s+\w+",    # Class definition
            r"\bfunction\s+\w+", # JS function
            r"=>\s*{",           # Arrow function
            r"\{[\s\S]*\}",      # Code blocks
            r";\s*$",            # Statement terminator
            r"^\s*//",           # Comments
            r"^\s*#",            # Python/bash comments
        ]

        return any(re.search(pattern, text, re.MULTILINE) for pattern in code_indicators)

    @staticmethod
    def _is_markdown(text: str) -> bool:
        """Check if text looks like markdown."""
        markdown_patterns = [
            r"^#{1,6}\s+",       # Headers
            r"^\*\s+",           # Unordered list
            r"^\d+\.\s+",        # Ordered list
            r"\*\*\w+\*\*",      # Bold
            r"\*\w+\*",          # Italic
            r"```[\s\S]*```",    # Code blocks
            r"\[.*\]\(.*\)",     # Links
        ]

        matches = sum(1 for pattern in markdown_patterns if re.search(pattern, text, re.MULTILINE))
        return matches >= 2  # At least 2 markdown patterns


# ===== Phase 4: Component Override Decorators =====

def prefer_component(component_type: str, language: str | None = None):
    """
    Decorator to hint preferred component type for a tool (Phase 4).

    This provides an override mechanism for cases where auto-selection
    might not choose the optimal component.

    Args:
        component_type: Preferred component ("code", "table", "markdown", etc.)
        language: Optional language hint for code components

    Usage:
        @app.tool("get_logs", ...)
        @prefer_component("code", language="text")
        def get_logs():
            return fetch_logs()

    The decorator sets metadata that can be checked during component selection.
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)

            # If result is plain data, wrap with component hint
            if not isinstance(
                result,
                (
                    UITable,
                    UICode,
                    UIForm,
                    UIConfirm,
                    UISelect,
                    UIProgress,
                    UIAlert,
                    UIText,
                    UIMarkdown,
                ),
            ):
                # Add _component hint to dict results
                if isinstance(result, dict):
                    result["_component"] = component_type
                    if language:
                        result["_language"] = language
                # For non-dict results, wrap in dict with hint
                else:
                    result = {
                        "_component": component_type,
                        "_language": language if language else "text",
                        "data": result
                    }

            return result

        # Mark function with metadata for introspection
        wrapper._preferred_component = component_type  # type: ignore
        wrapper._preferred_language = language  # type: ignore

        return wrapper
    return decorator
