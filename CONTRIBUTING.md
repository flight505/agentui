# Contributing to AgentUI

Thank you for your interest in contributing to AgentUI! This document provides guidelines for contributing themes, code, and documentation.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Contributing Themes](#contributing-themes)
- [Contributing Code](#contributing-code)
- [Testing](#testing)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project follows the Contributor Covenant Code of Conduct. Be respectful, inclusive, and constructive in all interactions.

---

## Getting Started

### Prerequisites

- **Go 1.22+** for TUI development
- **Python 3.11+** for agent runtime
- **uv** (preferred) or pip for Python package management
- **pnpm** (if using Node.js examples)

### Development Setup

```bash
# Clone the repository
git clone https://github.com/flight505/agentui.git
cd agentui

# Install Python dependencies
uv sync

# Build the TUI
make build-tui

# Run tests
make test
go test ./...
```

---

## Contributing Themes

AgentUI uses a JSON-based theme system for easy community contributions. You can create custom themes without writing Go code!

### Theme Structure

Create a JSON file in the `themes/` directory:

```json
{
  "id": "my-theme",
  "name": "My Awesome Theme",
  "description": "A beautiful theme inspired by...",
  "author": "Your Name",
  "version": "1.0.0",
  "colors": {
    "primary": "#7D56F4",
    "secondary": "#d946ef",
    "background": "#1a1a2e",
    "surface": "#252538",
    "overlay": "#2f2f45",
    "text": "#FAFAFA",
    "textMuted": "#a9b1d6",
    "textDim": "#565f89",
    "success": "#04B575",
    "warning": "#ffb86c",
    "error": "#ff6b6b",
    "info": "#7dcfff",
    "accent1": "212",
    "accent2": "#7D56F4",
    "accent3": "35"
  }
}
```

### Color Format

Colors can be specified as:
- **Hex**: `"#7D56F4"` (TrueColor)
- **ANSI 256**: `"212"` (256-color terminals)
- **Named**: `"red"`, `"blue"`, etc.

### Color Palette Guidelines

| Color | Purpose | Guidelines |
|-------|---------|-----------|
| `primary` | Main accent color | Headlines, active states, primary CTA |
| `secondary` | Supporting accent | Secondary actions, highlights |
| `background` | Base background | Should have high contrast with `text` |
| `surface` | Elevated surfaces | Forms, modals, cards |
| `overlay` | Overlays/tooltips | Slightly lighter than surface |
| `text` | Primary text | High contrast with background |
| `textMuted` | Secondary text | Labels, supporting text |
| `textDim` | Disabled/placeholder | Line numbers, placeholders |
| `success` | Success states | Completed steps, success alerts |
| `warning` | Warning states | Warnings, cautions |
| `error` | Error states | Errors, failures |
| `info` | Informational | Info alerts, links |
| `accent1` | Accent color 1 | Keywords in code, etc. |
| `accent2` | Accent color 2 | Functions, types in code |
| `accent3` | Accent color 3 | Strings, literals in code |

### Testing Your Theme

1. Create your theme JSON file in `themes/my-theme.json`
2. Test it with the theme test utility:

```bash
uv run python examples/theme_test.py my-theme
```

3. Or load it via environment variable:

```bash
AGENTUI_THEME=themes/my-theme.json uv run python examples/theme_test.py
```

### Theme Checklist

Before submitting a theme PR, verify:

- [ ] Theme has a unique ID (lowercase-with-dashes)
- [ ] All 15 color fields are defined
- [ ] Colors have good contrast (text on background)
- [ ] Theme works on both dark and light terminal backgrounds
- [ ] Tested with `examples/theme_test.py`
- [ ] JSON is valid (use `jsonlint` or similar)
- [ ] Author and description are filled in
- [ ] Theme follows semantic color meanings (success = green-ish, error = red-ish)

### Theme Inspiration

Good sources for color palettes:
- [Catppuccin](https://github.com/catppuccin/catppuccin)
- [Dracula](https://draculatheme.com/)
- [Nord](https://www.nordtheme.com/)
- [Tokyo Night](https://github.com/tokyo-night/tokyo-night-vscode-theme)
- [Gruvbox](https://github.com/morhetz/gruvbox)

---

## Contributing Code

### Code Style

**Python:**
- Follow PEP 8
- Use type hints (project uses mypy strict mode)
- Async/await for I/O operations
- Docstrings for public APIs

**Go:**
- Run `go fmt` before committing
- Follow standard Go conventions
- Document exported functions
- Use descriptive names

### Architecture Guidelines

- **Python** handles LLM logic, tools, state management
- **Go** handles rendering, UI, and visual presentation
- Communication via JSON Lines over stdin/stdout
- Keep TUI stateless; all state lives in Python

### Adding New UI Primitives

1. Define message type in `src/agentui/protocol.py`
2. Create payload builder function
3. Add Go renderer in `internal/ui/views/` or `internal/ui/components/`
4. Wire up in `internal/protocol/handler.go`
5. Add to `internal/app/app.go` Update/View methods
6. Test with Python example

---

## Testing

### Running Tests

```bash
# Go tests
go test ./...
go test ./internal/theme/... -v

# Python tests
uv run pytest tests/ -v

# Integration tests
uv run python examples/theme_test.py
uv run python examples/generative_ui_demo.py
```

### Writing Tests

- **Go**: Use table-driven tests in `*_test.go` files
- **Python**: Use pytest with async support
- **Integration**: Test full Python↔Go communication flow

---

## Pull Request Process

1. **Fork** the repository
2. **Create a branch** from `main`:
   ```bash
   git checkout -b feature/my-feature
   # or
   git checkout -b theme/my-theme
   ```

3. **Make your changes**:
   - Write clean, documented code
   - Add tests for new functionality
   - Update documentation as needed

4. **Test thoroughly**:
   ```bash
   make test
   go test ./...
   uv run python examples/theme_test.py
   ```

5. **Commit** with descriptive messages:
   ```bash
   git commit -m "feat: add awesome new feature"
   git commit -m "theme: add cyberpunk theme"
   git commit -m "fix: resolve animation timing issue"
   ```

6. **Push** to your fork:
   ```bash
   git push origin feature/my-feature
   ```

7. **Open a Pull Request**:
   - Provide a clear description
   - Reference any related issues
   - Include screenshots for visual changes
   - List breaking changes (if any)

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new features
- [ ] Documentation updated (if needed)
- [ ] Commit messages are descriptive
- [ ] No breaking changes (or clearly documented)
- [ ] Screenshots included (for UI changes)

---

## Development Tips

### Debugging the TUI

The Go TUI communicates via stdin/stdout, making direct debugging tricky. Use these approaches:

```go
// Write debug info to stderr (won't interfere with protocol)
fmt.Fprintf(os.Stderr, "Debug: %+v\n", data)

// Or use a debug log file
f, _ := os.OpenFile("/tmp/agentui-debug.log", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
fmt.Fprintf(f, "Debug: %+v\n", data)
```

### Testing Protocol Messages

Test individual protocol messages without LLM:

```python
from agentui.bridge import TUIConfig, managed_bridge

async with managed_bridge(TUIConfig(theme="charm-dark")) as bridge:
    await bridge.send_text("Test message")
    # ... test your message
```

### Theme Development Workflow

1. Create JSON file in `themes/`
2. Test with `AGENTUI_THEME=themes/my-theme.json`
3. Iterate on colors
4. Test all UI components (forms, tables, code, progress)
5. Verify contrast and readability
6. Submit PR

---

## Questions?

- **Issues**: https://github.com/flight505/agentui/issues
- **Discussions**: https://github.com/flight505/agentui/discussions
- **Email**: jesper_vang@me.com

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to AgentUI! 🎨✨
