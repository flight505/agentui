# AgentUI 🤖✨

> Build beautiful AI agent applications with Charm-quality TUIs

<p align="center">
  <img src="https://img.shields.io/badge/go-1.22+-00ADD8.svg" alt="Go 1.22+">
  <img src="https://img.shields.io/badge/python-3.11+-blue.svg" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
</p>

AgentUI combines the beauty of [Charm](https://charm.sh/) terminal UIs with the power of Python's AI ecosystem. Build stunning agent applications that work with Claude, OpenAI, Gemini, and more.

## ✨ Features

- **🎨 Charm-Level Beauty** — Built with Bubbletea, Lip Gloss, and Glamour
- **🔄 Model Agnostic** — Same app works with any LLM provider
- **🎭 Generative UI** — Forms, progress, tables generated at runtime
- **📦 Easy Distribution** — Single binary TUI + pip package
- **🎨 Themes** — Catppuccin, Dracula, Nord, Tokyo Night built-in

## Architecture

```
┌──────────────────────────────────────────────────────┐
│              Terminal (your beautiful TUI)           │
│                   Go + Bubbletea                     │
└──────────────────────────────────────────────────────┘
                         │ JSON protocol
                         ▼
┌──────────────────────────────────────────────────────┐
│                 Python Agent Process                  │
│          Claude / OpenAI / Gemini + Skills           │
└──────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

```bash
# Install
pip install agentui

# Create a new app
agentui init my-agent

# Run it
cd my-agent && agentui run
```

### Simple Agent

```python
import asyncio
from agentui import AgentApp

app = AgentApp(
    name="my-assistant",
    provider="claude",
)

@app.tool(
    name="get_weather",
    description="Get current weather",
    parameters={
        "type": "object",
        "properties": {
            "city": {"type": "string"}
        }
    }
)
def get_weather(city: str):
    return {"city": city, "temp": 22, "conditions": "Sunny"}

asyncio.run(app.run())
```

## 🎨 Themes

Built-in themes:
- `catppuccin-mocha` (default) — Soothing dark purples
- `catppuccin-latte` — Light mode
- `dracula` — Classic dark
- `nord` — Arctic blues
- `tokyo-night` — Vibrant dark

```bash
agentui run --theme dracula
```

## 🎭 Generative UI

The AI can generate beautiful UI elements at runtime:

```python
@app.tool(name="configure_project", is_ui_tool=True)
async def configure_project():
    # This renders as a beautiful form in the TUI
    from agentui.protocol import form_field
    return {
        "type": "form",
        "title": "Project Setup",
        "fields": [
            form_field("name", "Project Name", "text", required=True),
            form_field("stack", "Tech Stack", "select", 
                      options=["Python", "Node.js", "Go"]),
        ]
    }
```

**UI Primitives:**
- Forms with validation
- Progress bars with steps
- Data tables
- Syntax-highlighted code
- Confirmation dialogs
- Selection menus
- Markdown content
- Alerts & notifications

## 📁 Project Structure

```
my-agent/
├── app.yaml              # Configuration
├── skills/               # Agent skills
│   └── research/
│       ├── SKILL.md      # LLM instructions
│       └── skill.yaml    # Tool definitions
└── main.py               # Entry point
```

## 🔧 Development

```bash
# Clone
git clone https://github.com/flight505/agentui
cd agentui

# Install Python deps
pip install -e ".[dev]"

# Build Go TUI
make build-tui

# Run demo
make demo
```

### Building from Source

```bash
# Build everything
make build

# Build for all platforms
make build-all-platforms

# Run tests
make test
```

## 📚 Documentation

- [Design Document](./DESIGN.md) — Architecture deep-dive
- [Protocol Spec](./docs/protocol.md) — JSON protocol reference
- [Theme Guide](./docs/themes.md) — Creating custom themes

## 🗺️ Roadmap

- [x] Protocol design
- [x] Go TUI scaffold
- [x] Python bridge
- [x] Theme system
- [ ] Full TUI components
- [ ] More providers
- [ ] MCP integration
- [ ] Plugin marketplace

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md).

## 📄 License

MIT License — see [LICENSE](./LICENSE).

---

<p align="center">
  Built with 💜 using <a href="https://charm.sh">Charm</a>
</p>
