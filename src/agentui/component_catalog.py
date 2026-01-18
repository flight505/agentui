"""
Component Catalog - LLM-friendly documentation of available UI primitives.

Inspired by Google A2UI's catalog-based security model where agents can only
request pre-approved components. The catalog provides:
- Component schemas with descriptions
- Usage guidelines for when to use each component
- Examples with payload structures
- Selection heuristics for intelligent component choice
"""



class ComponentCatalog:
    """Component catalog for LLM discovery and intelligent selection."""

    @staticmethod
    def get_catalog_prompt() -> str:
        """
        Generate component catalog documentation for system prompt.

        This catalog makes the LLM aware of all available UI primitives,
        when to use them, and how to structure their payloads.

        Returns:
            Markdown documentation of all UI components
        """
        return """
## Available UI Components

You have access to the following display_* tools for presenting information to the user.
Choose the most appropriate component based on the data structure and user intent.

### 1. display_table(columns, rows, title=None, footer=None)
**When to use:** Structured tabular data with 2+ items of consistent schema
**Best for:** Lists of objects, comparison data, multi-column datasets
**Schema:**
  - columns: list[str] - Column headers
  - rows: list[list[str]] - Data rows (each row matches column count)
  - title: str | None - Optional table title
  - footer: str | None - Optional footer (e.g., "Showing 10 of 100 items")

**Example:**
```python
display_table(
    columns=["Name", "Status", "CPU"],
    rows=[
        ["api-server", "✓ Running", "45%"],
        ["database", "✓ Running", "12%"],
        ["cache", "✗ Stopped", "0%"]
    ],
    title="Service Status",
    footer="3 services total"
)
```

### 2. display_form(fields, title=None, description=None)
**When to use:** Need to collect structured user input
**Best for:** Configuration wizards, user preferences, data entry
**Schema:**
  - fields: list[Field] - Form fields (name, label, type, options, etc.)
  - title: str | None - Form title
  - description: str | None - Form description/instructions

**Field types:** text, select, checkbox, number, password, textarea

**Example:**
```python
display_form(
    fields=[
        {"name": "server", "label": "Server Name", "type": "text", "required": True},
        {"name": "region", "label": "Region", "type": "select", "options": ["us-east", "eu-west"]},
        {"name": "auto_scale", "label": "Enable Auto-scaling", "type": "checkbox"}
    ],
    title="Deploy Configuration",
    description="Configure your deployment settings"
)
```

### 3. display_code(code, language, title=None, line_numbers=True)
**When to use:** Source code, configs, logs, JSON, or any text >100 characters
**Best for:** Syntax-highlighted content, file previews, structured text
**Schema:**
  - code: str - The code or text content
  - language: str - Language for syntax highlighting (python, javascript, json, yaml, bash, etc.)
  - title: str | None - Optional title
  - line_numbers: bool - Show line numbers (default: True)

**Example:**
```python
display_code(
    code='def hello(name):\n    return f"Hello, {name}!"',
    language="python",
    title="Generated Function"
)
```

### 4. display_progress(message, percent=None, steps=None)
**When to use:** Long-running operations, multi-step workflows, loading states
**Best for:** Async tasks, multi-phase operations, progress tracking
**Schema:**
  - message: str - Current operation description
  - percent: float | None - Progress percentage (0-100)
  - steps: list[dict] | None - Multi-step progress with status per step

**Example:**
```python
display_progress(
    message="Deploying application...",
    percent=65,
    steps=[
        {"label": "Build", "status": "complete"},
        {"label": "Test", "status": "running"},
        {"label": "Deploy", "status": "pending"}
    ]
)
```

### 5. display_confirm(message, title=None, destructive=False)
**When to use:** Binary yes/no decisions, confirmations before destructive actions
**Best for:** User approval, safety confirmations, binary choices
**Schema:**
  - message: str - Question or confirmation prompt
  - title: str | None - Dialog title
  - destructive: bool - Red styling for dangerous actions (default: False)

**Returns:** bool (True if confirmed, False if cancelled)

**Example:**
```python
confirmed = display_confirm(
    message="This will delete all cached data. Continue?",
    title="Confirm Deletion",
    destructive=True
)
```

### 6. display_alert(message, severity, title=None)
**When to use:** Notifications, status messages, warnings, errors
**Best for:** Non-blocking status updates, completed actions, warnings
**Schema:**
  - message: str - Alert content
  - severity: "info" | "success" | "warning" | "error" - Alert type
  - title: str | None - Optional title

**Example:**
```python
display_alert(
    message="Configuration updated successfully",
    severity="success",
    title="Success"
)
```

### 7. display_select(label, options, default=None)
**When to use:** Single choice from 3-10 options
**Best for:** Menu selection, option picking, single-choice questions
**Schema:**
  - label: str - Selection prompt
  - options: list[str] - Available choices
  - default: str | None - Pre-selected option

**Returns:** str (selected option)

**Example:**
```python
choice = display_select(
    label="Choose deployment environment:",
    options=["development", "staging", "production"],
    default="staging"
)
```

## Component Selection Guidelines

**Choose the right component based on these heuristics:**

1. **Structured data with 2+ items** → `display_table`
   - List of objects with consistent keys
   - Comparison data (multiple items with same attributes)
   - Multi-column datasets

2. **Need user input** → `display_form` or `display_confirm` or `display_select`
   - Multiple fields → `display_form`
   - Yes/no question → `display_confirm`
   - Single choice from options → `display_select`

3. **Long text, code, or logs** → `display_code`
   - Anything >100 characters with structure
   - Source code, JSON, YAML, configs
   - Multi-line content

4. **Long operation in progress** → `display_progress`
   - Operations taking >2 seconds
   - Multi-step workflows
   - Need to show completion percentage

5. **Status message or notification** → `display_alert`
   - Completed actions
   - Warnings or errors
   - FYI messages

6. **Binary decision** → `display_confirm`
   - Yes/no questions
   - Approval required
   - Destructive action confirmation

7. **Single choice from options** → `display_select`
   - 3-10 options to choose from
   - Menu-style selection

## Edge Cases

- **Empty lists:** Use `display_alert` with info message instead of empty table
- **Single item:** Consider `display_code` (if object) or plain text (if simple)
- **Large datasets:** Use `display_table` with footer showing "X of Y items"
- **Nested objects:** Flatten to table or use `display_code` with JSON
- **Mixed types:** Serialize to consistent format first

## Best Practices

1. **Always provide titles** for tables and forms to give context
2. **Use footers** for tables with partial data (e.g., "Showing 50 of 200")
3. **Choose appropriate language** for `display_code` (enables syntax highlighting)
4. **Set destructive=True** for confirms on dangerous operations
5. **Use severity correctly** for alerts (success for completions, warning for cautions, error for failures)
"""

    @staticmethod
    def get_tool_schemas() -> list[dict]:
        """
        Tool schemas for display_* functions (callable by LLM).

        These schemas follow the Anthropic/OpenAI tool calling format.
        Each display_* tool renders a UI component.

        Returns:
            List of tool schemas for LLM tool calling
        """
        return [
            {
                "name": "display_table",
                "description": "Display structured tabular data with columns and rows. Best for lists of objects, comparison data, or multi-column datasets.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Column headers"
                        },
                        "rows": {
                            "type": "array",
                            "items": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "description": "Data rows (each row must match column count)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional table title"
                        },
                        "footer": {
                            "type": "string",
                            "description": "Optional footer (e.g., 'Showing X of Y items')"
                        }
                    },
                    "required": ["columns", "rows"]
                }
            },
            {
                "name": "display_form",
                "description": "Display an interactive form for collecting structured user input. Returns submitted form data.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "fields": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Form fields with name, label, type, options, etc."
                        },
                        "title": {
                            "type": "string",
                            "description": "Form title"
                        },
                        "description": {
                            "type": "string",
                            "description": "Form description/instructions"
                        }
                    },
                    "required": ["fields"]
                }
            },
            {
                "name": "display_code",
                "description": "Display syntax-highlighted code or structured text. Best for source code, configs, logs, JSON, or text >100 chars.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "code": {
                            "type": "string",
                            "description": "The code or text content"
                        },
                        "language": {
                            "type": "string",
                            "description": "Language for syntax highlighting (python, javascript, json, yaml, bash, text, etc.)"
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional title"
                        },
                        "line_numbers": {
                            "type": "boolean",
                            "description": "Show line numbers (default: true)"
                        }
                    },
                    "required": ["code", "language"]
                }
            },
            {
                "name": "display_progress",
                "description": "Display progress indicator for long-running operations. Can show percentage and multi-step progress.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Current operation description"
                        },
                        "percent": {
                            "type": "number",
                            "description": "Progress percentage (0-100)"
                        },
                        "steps": {
                            "type": "array",
                            "items": {"type": "object"},
                            "description": "Multi-step progress with label and status per step"
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "display_confirm",
                "description": "Display yes/no confirmation dialog. Returns boolean indicating user choice.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Question or confirmation prompt"
                        },
                        "title": {
                            "type": "string",
                            "description": "Dialog title"
                        },
                        "destructive": {
                            "type": "boolean",
                            "description": "Use red styling for dangerous actions (default: false)"
                        }
                    },
                    "required": ["message"]
                }
            },
            {
                "name": "display_alert",
                "description": "Display notification alert with severity level (info, success, warning, error).",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Alert content"
                        },
                        "severity": {
                            "type": "string",
                            "enum": ["info", "success", "warning", "error"],
                            "description": "Alert severity level"
                        },
                        "title": {
                            "type": "string",
                            "description": "Optional alert title"
                        }
                    },
                    "required": ["message", "severity"]
                }
            },
            {
                "name": "display_select",
                "description": "Display single-choice selection menu. Returns the selected option.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "label": {
                            "type": "string",
                            "description": "Selection prompt"
                        },
                        "options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Available choices"
                        },
                        "default": {
                            "type": "string",
                            "description": "Pre-selected option"
                        }
                    },
                    "required": ["label", "options"]
                }
            }
        ]
