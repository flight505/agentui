# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AgentUI is a hybrid Go/Python framework for building beautiful AI agent applications with Charm-quality TUIs. It uses a split-process architecture where a Go TUI (Bubbletea) handles rendering and a Python process manages LLM interactions.

**Key Architecture Points:**
- **Two-process design**: Go TUI subprocess communicates with Python agent via JSON Lines over stdio
- **Protocol-based communication**: All interaction between Go and Python happens through a JSON protocol (see `src/agentui/protocol.py` and `internal/protocol/`)
- **Model-agnostic**: Same app works with Claude, OpenAI, Gemini via provider abstraction
- **Generative UI**: Python can send UI primitives (forms, tables, progress bars) to Go for rendering

## Technology Stack

- **Python**: 3.11+ (agent runtime, LLM providers, skill system)
- **Go**: 1.22+ (TUI built with Charm libraries)
- **Charm libraries**: Bubbletea (TUI framework), Lip Gloss (styling), Glamour (markdown), Bubbles (components)

## Development Commands

### Python Development
```bash
# Install in dev mode (preferred)
uv sync
uv add --dev <package>

# Run tests
uv run pytest tests/ -v

# Run specific test
uv run pytest tests/test_protocol.py::test_name -v

# Lint and format
uv run ruff check src/ tests/ examples/
uv run ruff format src/ tests/ examples/

# Type checking
uv run mypy src/
```

### Go Development
```bash
# Build TUI binary
make build-tui

# Run Go tests
make test-go
go test ./... -v

# Format Go code
go fmt ./...

# Lint Go code
go vet ./...
```

### Integration Testing
```bash
# Build everything
make build

# Run demo with TUI
make demo

# Run example apps
uv run python examples/simple_agent.py
uv run python examples/generative_ui_demo.py
```

## Code Architecture

### Python Side (`src/agentui/`)

**Core Components:**
- `app.py`: `AgentApp` - High-level API for creating agents with decorator-based tool registration
- `core.py`: `AgentCore` - Agent execution loop, tool calling, context management
- `bridge.py`: `TUIBridge` - Manages subprocess communication with Go TUI
  - Handles async message passing, request/response correlation, reconnection
  - Also includes `CLIBridge` fallback using Rich when TUI binary unavailable
- `protocol.py`: Protocol message types and payload builders
- `providers/`: LLM provider implementations (Claude, OpenAI)
  - Each provider implements streaming, tool calling, context management
- `skills/`: Skill loader and registry for loading SKILL.md files with tool definitions

**Key Design Patterns:**
- Bridge manages all stdio communication - never write to TUI stdin/stdout directly
- Use `create_request()` for messages expecting responses (forms, confirms)
- Use `create_message()` for fire-and-forget (text, progress, alerts)
- All blocking UI operations (forms, confirms) use request/response pattern with UUIDs

### Go Side (`cmd/agentui/`, `internal/`)

**Core Components:**
- `cmd/agentui/main.go`: Entry point, CLI argument parsing
- `internal/app/app.go`: Main Bubbletea model (Elm architecture)
- `internal/protocol/`: JSON protocol reading/writing, message dispatch
- `internal/ui/views/`: UI component renderers (forms, tables, chat, progress)
- `internal/theme/`: Theme system with Charm aesthetic (CharmDark/CharmLight/CharmAuto as default)

**Key Design Patterns:**
- Everything is a Bubbletea model with Update/View pattern
- Protocol messages arrive as Bubbletea messages via stdin reader
- UI state is immutable - Update returns new model
- Views are pure functions that render lipgloss.Styles

### Communication Flow

```
Python Agent → bridge.send() → JSON → TUI stdin → protocol.handler → Bubbletea Update → View render
User Input → Bubbletea Update → protocol.writer → JSON → bridge.events() → Agent Loop
```

**Critical Points:**
- TUI must respond to requests (forms, confirms) by echoing the request ID
- Python awaits responses using Future pattern in `_pending_requests`
- If TUI crashes, bridge attempts reconnection (configurable retries)

## Common Development Tasks

### Adding a New UI Primitive

1. Define message type in `src/agentui/protocol.py` (MessageType enum)
2. Create payload builder function (e.g., `new_primitive_payload()`)
3. Add convenience method to TUIBridge (e.g., `send_new_primitive()`)
4. Implement Go renderer in `internal/ui/views/`
5. Wire up in `internal/protocol/handler.go` dispatch
6. Add to main Bubbletea model's View() in `internal/app/app.go`

### Adding a New LLM Provider

1. Create `src/agentui/providers/new_provider.py`
2. Implement async streaming and tool calling
3. Match interface used by Claude provider (see `providers/claude.py`)
4. Add provider type to `types.py` ProviderType enum
5. Update `AgentApp._get_api_key()` for environment variable mapping
6. Add to `pyproject.toml` optional dependencies

### Adding Built-in Tools

1. Add tool definition to `src/agentui/skills/builtins.py`
2. Tool handler should be async and return dict or UI primitive
3. Register in core or expose via decorator pattern

## Testing Strategy

- Python: pytest with async support (`pytest-asyncio`)
- Go: standard `go test` with table-driven tests
- Integration: Run examples/ scripts that exercise full Python↔Go flow
- Protocol: Test message serialization/deserialization independently

## Environment Variables

- `ANTHROPIC_API_KEY`: For Claude provider
- `OPENAI_API_KEY`: For OpenAI provider
- `GOOGLE_API_KEY`: For Gemini provider

## Binary Distribution

- Go binary built for multiple platforms via `make build-all-platforms`
- Python package includes pre-built binaries in `src/agentui/bin/`
- Bridge searches: dev location `../../../bin/`, package `src/agentui/bin/`, system PATH
- Falls back to Rich CLI rendering if binary not found

## Skills System

Skills are directories with:
- `SKILL.md`: Instructions for LLM (loaded into context)
- `skill.yaml`: Tool definitions (name, parameters, description)

Skills auto-load from manifest `skills:` list. See `examples/skills/weather/` for reference.

## Important Constraints

- **Never block Python event loop**: All subprocess I/O uses `run_in_executor()`
- **TUI binary must be stateless**: All state lives in Python, TUI just renders
- **Protocol is line-delimited**: Each message must be single line JSON
- **IDs are required for requests**: Use `create_request()` which auto-generates UUID
- **Type hints required**: Project uses mypy strict mode (`disallow_untyped_defs = true`)

## Theme & Aesthetic Direction

**IMPORTANT**: The aesthetic goal is to match the Charmbracelet style (Glow, Mods, Huh, etc.).

**Primary Themes (built-in):**
- `CharmDark` - Signature pink/purple/teal on dark (DEFAULT)
- `CharmLight` - Purple-focused light variant
- `CharmAuto` - Auto-detects terminal background

**Charm Signature Colors:**
```go
CharmPurple = "#7D56F4"   // The iconic Charm purple
CharmPink   = "212"       // ANSI 212 (~#ff87d7)
CharmTeal   = "35"        // ANSI 35 (~#00af5f)
```

**DO NOT:**
- Implement Sage, Obsidian, Zephyr, Ember themes (archived direction)
- Bundle many community themes by default
- Use `CompleteAdaptiveColor` everywhere (simple `lipgloss.Color` is fine)

**Theme System:**
- `internal/theme/theme.go`: Core types with `TerminalColor` interface
- `internal/theme/charm.go`: CharmDark, CharmLight, CharmAuto
- `internal/theme/community_themes.go`: Opt-in Catppuccin, Dracula, Nord, Tokyo Night
- `internal/theme/loader.go`: JSON theme loading for extensibility
- Users create themes via JSON in `themes/` directory

**For Implementation Plans**: See `docs/plans/README.md` - only follow the ACTIVE plan.
