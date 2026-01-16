# AgentUI — Design Document v2

> **A framework for building beautiful AI agent applications with Charm-quality TUIs**

## Vision

Create the most beautiful terminal-based AI agent framework by combining:
- **Charm/Bubbletea** for stunning, responsive TUIs (Go)
- **Python ecosystem** for LLM providers, skills, and tools
- **Simple protocol** connecting them seamlessly

Users get Charm-level aesthetics while developers get full Python ecosystem access.

---

## Architecture: Split Process Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              USER'S TERMINAL                                │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        GO TUI PROCESS                                 │  │
│  │                     (Bubbletea + Lip Gloss + Glamour)                 │  │
│  │                                                                       │  │
│  │  ╭─────────────────────────────────────────────────────────────────╮  │  │
│  │  │  AgentUI · Project Planner                              ⚙ ? ✕  │  │  │
│  │  ├─────────────────────────────────────────────────────────────────┤  │  │
│  │  │                                                                 │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────┐   │  │  │
│  │  │  │ 🤖 How can I help you today?                            │   │  │  │
│  │  │  └─────────────────────────────────────────────────────────┘   │  │  │
│  │  │                                                                 │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────┐   │  │  │
│  │  │  │ 👤 Plan a B2B SaaS inventory management system          │   │  │  │
│  │  │  └─────────────────────────────────────────────────────────┘   │  │  │
│  │  │                                                                 │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────┐   │  │  │
│  │  │  │ 🤖 I'll help you plan that. Let me gather some info...  │   │  │  │
│  │  │  │                                                         │   │  │  │
│  │  │  │  ╭─ Project Configuration ─────────────────────────╮    │   │  │  │
│  │  │  │  │                                                 │    │   │  │  │
│  │  │  │  │  Project Name: █                                │    │   │  │  │
│  │  │  │  │                                                 │    │   │  │  │
│  │  │  │  │  Tech Stack:  ○ Python/FastAPI                  │    │   │  │  │
│  │  │  │  │              ● Node.js/Express                  │    │   │  │  │
│  │  │  │  │              ○ Go/Gin                           │    │   │  │  │
│  │  │  │  │                                                 │    │   │  │  │
│  │  │  │  │  Cloud:      ● AWS  ○ GCP  ○ Azure              │    │   │  │  │
│  │  │  │  │                                                 │    │   │  │  │
│  │  │  │  │         [ Cancel ]  [ Continue → ]              │    │   │  │  │
│  │  │  │  ╰─────────────────────────────────────────────────╯    │   │  │  │
│  │  │  └─────────────────────────────────────────────────────────┘   │  │  │
│  │  │                                                                 │  │  │
│  │  ├─────────────────────────────────────────────────────────────────┤  │  │
│  │  │  > Type a message...                                    ⏎ Send  │  │  │
│  │  ╰─────────────────────────────────────────────────────────────────╯  │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                      │                                      │
│                                      │ JSON Protocol (stdio)                │
│                                      │                                      │
│  ┌───────────────────────────────────▼───────────────────────────────────┐  │
│  │                        PYTHON AGENT PROCESS                           │  │
│  │                                                                       │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │  Providers  │  │    Agent    │  │   Skills    │  │    Tools    │  │  │
│  │  │             │  │    Core     │  │   Loader    │  │  Executor   │  │  │
│  │  │ • Claude    │  │             │  │             │  │             │  │  │
│  │  │ • OpenAI    │  │ • Loop      │  │ • SKILL.md  │  │ • Built-in  │  │  │
│  │  │ • Gemini    │  │ • Context   │  │ • Tools     │  │ • Custom    │  │  │
│  │  │ • Ollama    │  │ • State     │  │ • Config    │  │ • MCP       │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │                                                                       │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Why Split Process?

| Challenge | Solution |
|-----------|----------|
| Charm is Go, LLM SDKs are Python | Separate processes, best of both |
| Python TUIs look mediocre | Go handles all rendering |
| Need plugin ecosystem | Python plugins work unchanged |
| Distribution complexity | Single Go binary + pip package |
| Performance concerns | Go renders (fast), Python thinks (flexible) |

### Proven Pattern

This architecture is battle-tested:
- **Neovim** — C core + Lua/Python plugins via msgpack-rpc
- **VS Code** — Electron shell + language server protocol
- **Zed** — Rust core + extension protocol
- **Charm's soft-serve** — Go TUI + Git backend

---

## Component Specifications

### 1. Go TUI (`agentui-tui`)

The terminal interface built with Charm's stack:

| Library | Purpose |
|---------|---------|
| **Bubbletea** | TUI framework (Elm architecture) |
| **Lip Gloss** | Styling (colors, borders, layout) |
| **Glamour** | Markdown rendering |
| **Bubbles** | Pre-built components (inputs, lists, tables) |
| **Huh** | Form components |

**Directory Structure:**
```
cmd/agentui/
├── main.go                 # Entry point
├── app/
│   ├── app.go              # Main Bubbletea model
│   ├── keymap.go           # Key bindings
│   └── commands.go         # Bubbletea commands
├── ui/
│   ├── views/
│   │   ├── chat.go         # Chat message view
│   │   ├── form.go         # Dynamic form renderer
│   │   ├── table.go        # Data table view
│   │   ├── progress.go     # Progress indicators
│   │   ├── code.go         # Syntax-highlighted code
│   │   ├── markdown.go     # Rich markdown
│   │   ├── confirm.go      # Confirmation dialogs
│   │   ├── select.go       # Selection menus
│   │   └── tree.go         # Tree view
│   ├── components/
│   │   ├── header.go       # App header
│   │   ├── footer.go       # Status bar
│   │   ├── input.go        # Message input
│   │   ├── spinner.go      # Loading spinners
│   │   └── toast.go        # Notifications
│   └── layout/
│       ├── container.go    # Layout containers
│       └── responsive.go   # Terminal size handling
├── protocol/
│   ├── types.go            # Message type definitions
│   ├── reader.go           # JSON line reader
│   ├── writer.go           # JSON line writer
│   └── handler.go          # Message dispatch
├── themes/
│   ├── theme.go            # Theme interface
│   ├── catppuccin.go       # Catppuccin variants
│   ├── dracula.go          # Dracula theme
│   ├── nord.go             # Nord theme
│   └── custom.go           # User-defined themes
└── config/
    ├── config.go           # Configuration loading
    └── defaults.go         # Default settings
```

**Key Design Decisions:**

1. **Elm Architecture** — Bubbletea's Model-Update-View pattern keeps UI predictable
2. **Component Isolation** — Each UI primitive is a self-contained Bubbletea model
3. **Adaptive Layout** — Responds to terminal resize elegantly
4. **Theme System** — Colors/styles defined centrally, applied consistently

---

### 2. Communication Protocol

JSON Lines over stdio — simple, debuggable, language-agnostic.

#### Message Format

```go
// Base message structure
type Message struct {
    Type    string          `json:"type"`              // Message type
    ID      string          `json:"id,omitempty"`      // For request/response correlation
    Payload json.RawMessage `json:"payload,omitempty"` // Type-specific data
}
```

#### Python → Go (Render Commands)

```json
// Stream text content
{"type": "text", "payload": {"content": "Analyzing your project..."}}

// Stream markdown
{"type": "markdown", "payload": {"content": "## Results\n\n- Found 3 competitors..."}}

// Show progress
{"type": "progress", "payload": {
  "message": "Researching market...",
  "percent": 45,
  "steps": [
    {"label": "Market Research", "status": "complete"},
    {"label": "Architecture", "status": "running"},
    {"label": "Cost Analysis", "status": "pending"}
  ]
}}

// Request form input (waits for response)
{"type": "form", "id": "project-config", "payload": {
  "title": "Project Configuration",
  "fields": [
    {"name": "name", "label": "Project Name", "type": "text", "required": true},
    {"name": "stack", "label": "Tech Stack", "type": "select", 
     "options": ["Python", "Node.js", "Go"]},
    {"name": "cloud", "label": "Cloud Provider", "type": "select",
     "options": ["AWS", "GCP", "Azure"]}
  ]
}}

// Show data table
{"type": "table", "payload": {
  "title": "Cost Breakdown",
  "columns": ["Service", "Tier", "Monthly Cost"],
  "rows": [
    ["EC2", "t3.medium", "$30.00"],
    ["RDS", "db.t3.small", "$25.00"],
    ["S3", "Standard", "$5.00"]
  ],
  "footer": "Total: $60.00/month"
}}

// Show code block
{"type": "code", "payload": {
  "language": "python",
  "code": "def hello():\n    print('Hello, World!')",
  "title": "main.py"
}}

// Request confirmation
{"type": "confirm", "id": "approve-tool", "payload": {
  "message": "Allow tool 'web_search'?",
  "destructive": false
}}

// Show alert/notification
{"type": "alert", "payload": {
  "severity": "success",
  "title": "Complete",
  "message": "Project plan saved to ./planning_outputs/"
}}

// Update status bar
{"type": "status", "payload": {
  "message": "Using Claude Sonnet 4.5",
  "tokens": {"input": 1250, "output": 430}
}}

// Clear/reset view
{"type": "clear", "payload": {"scope": "chat"}}

// Agent finished
{"type": "done", "payload": {"summary": "Created 12 files"}}
```

#### Go → Python (User Events)

```json
// User typed a message
{"type": "input", "payload": {"content": "Plan a B2B SaaS app"}}

// Form submitted
{"type": "form_response", "id": "project-config", "payload": {
  "values": {
    "name": "InventoryPro",
    "stack": "Python",
    "cloud": "AWS"
  }
}}

// Confirmation response
{"type": "confirm_response", "id": "approve-tool", "payload": {"confirmed": true}}

// User requested cancel
{"type": "cancel", "payload": {}}

// User requested quit
{"type": "quit", "payload": {}}

// Terminal resized
{"type": "resize", "payload": {"width": 120, "height": 40}}
```

#### Protocol Rules

1. **One JSON object per line** — newline delimited
2. **UTF-8 encoding** — always
3. **ID correlation** — requests needing response include `id`, responses echo it
4. **Streaming** — text/markdown can stream character-by-character
5. **Blocking requests** — form/confirm block Python until Go responds

---

### 3. Python Package (`agentui`)

The agent runtime and LLM integration layer.

**Directory Structure:**
```
src/agentui/
├── __init__.py             # Public API exports
├── app.py                  # High-level AgentApp class
├── core.py                 # Agent execution loop
├── types.py                # Core type definitions
├── primitives.py           # UI primitive dataclasses
├── protocol.py             # JSON protocol handling
├── bridge.py               # Go TUI process management
├── providers/
│   ├── __init__.py         # Provider base class
│   ├── claude.py           # Anthropic Claude
│   ├── openai.py           # OpenAI GPT
│   ├── gemini.py           # Google Gemini
│   └── ollama.py           # Local Ollama
├── skills/
│   ├── __init__.py         # Skill loader
│   ├── registry.py         # Skill/tool registry
│   └── builtins.py         # Built-in tools
├── config/
│   ├── __init__.py         # Config management
│   ├── manifest.py         # App manifest parser
│   └── keys.py             # API key handling
└── cli.py                  # CLI entry point
```

**Key Classes:**

```python
# High-level app creation
class AgentApp:
    """Main application wrapper."""
    
    def __init__(
        self,
        manifest: str | Path | AppManifest | None = None,
        provider: str = "claude",
        model: str | None = None,
    ): ...
    
    def tool(self, name: str, description: str, parameters: dict):
        """Decorator to register a tool."""
        ...
    
    async def run(self, prompt: str | None = None) -> None:
        """Run the agent with TUI."""
        ...


# TUI bridge
class TUIBridge:
    """Manages communication with Go TUI process."""
    
    async def start(self) -> None:
        """Spawn Go TUI subprocess."""
        ...
    
    async def send(self, message: UIMessage) -> None:
        """Send message to TUI."""
        ...
    
    async def receive(self) -> UserEvent:
        """Receive event from TUI."""
        ...
    
    async def request(self, message: UIMessage) -> Any:
        """Send request and wait for response."""
        ...


# UI primitives (sent to Go for rendering)
@dataclass
class UIForm:
    type: Literal["form"] = "form"
    title: str | None = None
    fields: list[UIFormField] = field(default_factory=list)
    
@dataclass
class UIProgress:
    type: Literal["progress"] = "progress"
    message: str = ""
    percent: float | None = None
    steps: list[UIProgressStep] | None = None

# ... etc for all primitives
```

---

### 4. Theme System

Themes define the visual identity. Built into Go binary, selectable at runtime.

```go
// theme.go
type Theme struct {
    Name        string
    Colors      ColorPalette
    Typography  Typography
    Borders     BorderStyle
    Spacing     Spacing
}

type ColorPalette struct {
    Primary     lipgloss.Color
    Secondary   lipgloss.Color
    Background  lipgloss.Color
    Surface     lipgloss.Color
    Text        lipgloss.Color
    TextMuted   lipgloss.Color
    Success     lipgloss.Color
    Warning     lipgloss.Color
    Error       lipgloss.Color
    Info        lipgloss.Color
}

// catppuccin.go
var CatppuccinMocha = Theme{
    Name: "Catppuccin Mocha",
    Colors: ColorPalette{
        Primary:    lipgloss.Color("#cba6f7"), // Mauve
        Secondary:  lipgloss.Color("#f5c2e7"), // Pink
        Background: lipgloss.Color("#1e1e2e"), // Base
        Surface:    lipgloss.Color("#313244"), // Surface0
        Text:       lipgloss.Color("#cdd6f4"), // Text
        TextMuted:  lipgloss.Color("#a6adc8"), // Subtext0
        Success:    lipgloss.Color("#a6e3a1"), // Green
        Warning:    lipgloss.Color("#f9e2af"), // Yellow
        Error:      lipgloss.Color("#f38ba8"), // Red
        Info:       lipgloss.Color("#89b4fa"), // Blue
    },
    // ...
}
```

**Built-in Themes:**
- Catppuccin Mocha (default dark)
- Catppuccin Latte (light)
- Dracula
- Nord
- Tokyo Night
- Gruvbox
- One Dark

---

### 5. App Manifest

Applications are defined by `app.yaml`:

```yaml
# app.yaml
name: project-planner
version: 1.0.0
description: AI-powered project planning assistant

# Branding (shown in TUI header)
display_name: "Project Planner"
icon: 🏗️
tagline: "From idea to implementation"

# Provider configuration
providers:
  default: claude
  
  claude:
    model: claude-sonnet-4-5-20250929
    max_tokens: 8192
    
  openai:
    model: gpt-4o

# Skills (directories with SKILL.md + tools)
skills:
  - ./skills/research
  - ./skills/architecture
  - ./skills/cost-analysis
  - ./skills/sprint-planning

# System prompt
system_prompt: |
  You are a project planning assistant. Help users:
  1. Research markets and competitors
  2. Design software architecture
  3. Estimate costs and timelines
  4. Create actionable sprint plans
  
  Use tools to gather information and display results.
  Always save outputs to the planning_outputs/ directory.

# UI configuration
ui:
  theme: catppuccin-mocha
  
  # Welcome screen
  welcome:
    title: "Welcome to Project Planner"
    subtitle: "AI-powered software project planning"
    features:
      - "📊 Market research & competitive analysis"
      - "🏛️ Architecture design with C4 diagrams"
      - "💰 Cloud cost analysis & ROI projections"
      - "📋 Sprint planning with INVEST stories"

# Output configuration  
output:
  directory: ./planning_outputs
  format: "{date}_{name}"
```

---

## Distribution

### Installation

```bash
# Option 1: pip (downloads Go binary automatically)
pip install agentui

# Option 2: Homebrew (macOS/Linux)
brew install agentui

# Option 3: Direct download
curl -fsSL https://agentui.dev/install.sh | sh
```

### Package Structure

```
PyPI Package (agentui):
├── agentui/                 # Python package
├── bin/
│   ├── agentui-tui-darwin-amd64
│   ├── agentui-tui-darwin-arm64
│   ├── agentui-tui-linux-amd64
│   └── agentui-tui-windows-amd64.exe
└── setup.py                 # Handles binary installation

Homebrew Formula:
- Downloads Go binary
- Installs to /usr/local/bin/agentui-tui
- User installs Python package separately
```

### Running an App

```bash
# From manifest
agentui run ./my-app/

# Quick interaction (no manifest)
agentui quick --provider claude "Help me plan a project"

# With specific provider
agentui run ./my-app/ --provider openai --model gpt-4o

# List available providers
agentui providers

# Create new app scaffold
agentui init my-new-app
```

---

## Development Phases

### Phase 1: Foundation (2 weeks)

**Week 1: Go TUI Core**
- [ ] Bubbletea app scaffold
- [ ] Basic chat view (messages in/out)
- [ ] Message input component
- [ ] Lip Gloss styling foundation
- [ ] Catppuccin theme implementation
- [ ] JSON protocol reader/writer

**Week 2: Python Bridge**
- [ ] TUI process spawning
- [ ] Protocol send/receive
- [ ] Basic AgentApp class
- [ ] Claude provider (streaming)
- [ ] Simple tool registration

**Deliverable:** Basic chat working end-to-end

### Phase 2: UI Primitives (2 weeks)

**Week 3: Interactive Components**
- [ ] Form renderer (text, select, checkbox)
- [ ] Confirmation dialogs
- [ ] Selection menus
- [ ] Form response handling

**Week 4: Display Components**
- [ ] Progress indicators (with steps)
- [ ] Data tables
- [ ] Code blocks (syntax highlighting)
- [ ] Markdown rendering
- [ ] Alerts/toasts

**Deliverable:** All UI primitives rendering correctly

### Phase 3: Agent Features (2 weeks)

**Week 5: Agent Core**
- [ ] Full agent loop
- [ ] Tool execution pipeline
- [ ] Permission handling (confirm tools)
- [ ] Context management
- [ ] OpenAI provider

**Week 6: Skills & Config**
- [ ] Skill loader (SKILL.md + yaml)
- [ ] App manifest parser
- [ ] API key management
- [ ] Theme switching
- [ ] CLI commands

**Deliverable:** Complete agent apps working

### Phase 4: Polish & Distribution (1 week)

**Week 7: Production Ready**
- [ ] Error handling & recovery
- [ ] Responsive layout (terminal resize)
- [ ] Binary packaging
- [ ] pip distribution
- [ ] Documentation
- [ ] Example apps

**Deliverable:** v0.1.0 release

---

## Example: Project Planner Migration

Your existing `claude-project-planner` would become:

```
project-planner/
├── app.yaml                    # Manifest (replaces plugin.json)
├── main.py                     # Optional custom entry point
├── skills/                     # Existing skills work unchanged
│   ├── research-lookup/
│   │   ├── SKILL.md
│   │   └── skill.yaml
│   ├── architecture-research/
│   ├── building-blocks/
│   ├── sprint-planning/
│   └── ...
└── prompts/
    └── planner.md              # System prompt
```

```python
# main.py (optional - for custom tools)
from agentui import AgentApp

app = AgentApp(manifest="app.yaml")

@app.tool(
    name="generate_diagram",
    description="Generate architecture diagram",
    parameters={...}
)
async def generate_diagram(diagram_type: str, components: list):
    # Custom implementation
    ...

if __name__ == "__main__":
    import asyncio
    asyncio.run(app.run())
```

---

## Technical Decisions

### Why JSON Lines over stdio?

| Alternative | Rejected Because |
|-------------|------------------|
| gRPC | Overkill, adds complexity |
| WebSocket | Requires network stack |
| Unix sockets | Platform-specific |
| msgpack | Less debuggable than JSON |
| **JSON Lines** | ✅ Simple, debuggable, universal |

### Why Bubbletea?

| Alternative | Rejected Because |
|-------------|------------------|
| tcell (Go) | Lower level, more work |
| tview (Go) | Less flexible than Bubbletea |
| Textual (Python) | Aesthetics don't match Charm |
| **Bubbletea** | ✅ Elm architecture, Charm ecosystem |

### Why Subprocess?

| Alternative | Rejected Because |
|-------------|------------------|
| CGO bindings | Complex, fragile |
| WASM | Performance, maturity |
| Rewrite in Go | Lose Python ecosystem |
| **Subprocess** | ✅ Simple, proven, reliable |

---

## Success Metrics

1. **Beauty** — Screenshots indistinguishable from native Charm apps
2. **Performance** — <100ms latency for UI updates
3. **Compatibility** — Existing Claude Code skills work unchanged
4. **Simplicity** — Hello world in <10 lines of Python
5. **Distribution** — `pip install` just works

---

## Open Questions

1. **Binary distribution** — Vendor in pip, or separate install?
2. **Windows support** — Priority level?
3. **Web fallback** — Provide browser UI for non-terminal environments?
4. **Plugin marketplace** — Central registry for skills/apps?

---

## References

- [Charm](https://charm.sh/) — The gold standard for terminal UIs
- [Bubbletea](https://github.com/charmbracelet/bubbletea) — TUI framework
- [Lip Gloss](https://github.com/charmbracelet/lipgloss) — Styling
- [Glamour](https://github.com/charmbracelet/glamour) — Markdown
- [Huh](https://github.com/charmbracelet/huh) — Forms
- [Catppuccin](https://catppuccin.com/) — Color palette
- [Claude Agent SDK](https://docs.anthropic.com/en/docs/claude-code) — Reference implementation
