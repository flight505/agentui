# Storybook Assistant Expansion Design

**Purpose**: Design document for expanding [Storybook Assistant](https://github.com/flight505/storybook-assistant) to support both web components AND terminal UI testing.

**Status**: Planning / Future Consideration
**Author**: Jesper
**Date**: 2026-01-18

---

## Vision: Universal Component Testing Framework

Transform Storybook Assistant from a web-only testing tool into a **unified component testing framework** that handles:

- ✅ **Web Components** (existing): React, Vue, Svelte → Browser rendering
- 🆕 **Terminal Components** (new): AgentUI, Bubbletea → Terminal rendering

---

## Architecture Evolution

### Current Structure (Web-Only)

```
storybook-assistant/
├── skills/           # 18 skills (web-focused)
├── commands/         # 12 commands (Storybook setup, story generation)
├── agents/           # 3 agents (a11y audit, component generation)
└── hooks/            # Environment detection
```

### Proposed Structure (Universal)

```
component-testing-assistant/  # Renamed for clarity
├── core/
│   ├── renderer.ts           # Abstract renderer interface
│   ├── snapshot.ts           # Snapshot engine (multi-format)
│   └── differ.ts             # Universal diff engine
│
├── environments/
│   ├── web/                  # Existing Storybook functionality
│   │   ├── skills/           # Web-specific testing knowledge
│   │   ├── commands/         # /generate-stories, /setup-storybook
│   │   └── renderer.ts       # Browser rendering engine
│   │
│   └── terminal/             # New terminal UI support
│       ├── skills/           # Terminal-specific testing knowledge
│       ├── commands/         # /test-component, /snapshot-terminal
│       └── renderer.py       # Terminal rendering (Go TUI bridge)
│
├── shared/
│   ├── skills/
│   │   ├── ACCESSIBILITY.md       # Universal a11y principles
│   │   ├── TESTING_PATTERNS.md    # Cross-environment testing
│   │   └── REGRESSION_TESTING.md  # Snapshot strategies
│   │
│   └── commands/
│       └── /test-all              # Test all components (any env)
│
└── hooks/
    └── SessionStart.sh            # Detect project type, load environment
```

---

## Required Extensions

### 1. Dual Rendering Engine Support

**Current**: Browser-based rendering only
**Needed**: Abstract rendering layer supporting multiple environments

```typescript
// New core interface
interface ComponentRenderer {
  render(component: Component): RenderOutput
  capture(): Snapshot
}

// Web implementation (existing)
class WebRenderer implements ComponentRenderer {
  render(component: ReactComponent): HTMLElement {
    return ReactDOM.render(component)
  }

  capture(): ImageSnapshot {
    return await page.screenshot()
  }
}

// Terminal implementation (new)
class TerminalRenderer implements ComponentRenderer {
  render(component: UICode): ANSIOutput {
    // Bridge to Go TUI
    return this.tuiBridge.renderComponent(component)
  }

  capture(): ANSISnapshot {
    // Capture terminal output with ANSI codes
    return this.tuiBridge.captureOutput()
  }
}
```

**Plugin Detection**:
```bash
# hooks/SessionStart.sh (enhanced)

if [ -f "pyproject.toml" ] && grep -q "agentui" pyproject.toml; then
  echo "✅ AgentUI project detected"
  export COMPONENT_ENV="terminal"
  export RENDERER="TerminalRenderer"

elif [ -f "package.json" ] && grep -q "storybook" package.json; then
  echo "✅ Web component project detected"
  export COMPONENT_ENV="web"
  export RENDERER="WebRenderer"
fi
```

---

### 2. Terminal-Specific Testing Tools

**New Plugin Structure**:

```
storybook-assistant/
└── environments/terminal/
    │
    ├── skills/
    │   ├── TERMINAL_UI_TESTING.md
    │   │   - ANSI escape sequence validation
    │   │   - Unicode box drawing verification
    │   │   - Terminal color palette testing
    │   │   - Protocol message validation
    │   │
    │   ├── SYNTAX_HIGHLIGHTING_TESTING.md
    │   │   - Chroma integration verification
    │   │   - Color code validation (ANSI → Hex)
    │   │   - Language lexer testing
    │   │
    │   └── PROTOCOL_TESTING.md
    │       - Python↔Go message validation
    │       - Request/response correlation
    │       - JSON Lines protocol testing
    │
    ├── commands/
    │   ├── /test-tui-component.md
    │   │   - Interactive wizard for component testing
    │   │   - Detects UI primitives (UICode, UITable, UIProgress)
    │   │   - Generates test cases automatically
    │   │
    │   ├── /snapshot-terminal.md
    │   │   - Creates ANSI snapshot baselines
    │   │   - Compares current output to baseline
    │   │   - Shows diff with highlighted changes
    │   │
    │   └── /validate-syntax.md
    │       - Checks syntax highlighting works
    │       - Validates color codes per language
    │       - Verifies theme application
    │
    └── agents/
        ├── TERMINAL_COMPONENT_TESTER.md
        │   - Autonomous testing of UI components
        │   - Generates comprehensive test suites
        │   - Reports results with pass/fail
        │
        └── REGRESSION_VALIDATOR.md
            - Compares snapshots across changes
            - Identifies visual regressions
            - Generates HTML diff reports
```

---

### 3. Snapshot Testing for ANSI Output

**Web Snapshots** (current):
```typescript
// Button.test.tsx.snap
exports[`Button renders primary variant`] = `
<button class="btn-primary">
  Click me
</button>
`;
```

**Terminal Snapshots** (needed):
```python
# tests/__snapshots__/test_ui_components/python-fibonacci.ansi
\x1b[1m\x1b[38;5;212mdef\x1b[0m \x1b[38;5;99mfibonacci\x1b[0m\x1b[38;5;146m(\x1b[0m\x1b[38;5;231mn\x1b[0m\x1b[38;5;146m)\x1b[0m\x1b[38;5;146m:\x1b[0m
\x1b[0m\x1b[38;5;236m    \x1b[0m\x1b[1m\x1b[38;5;212mif\x1b[0m\x1b[38;5;236m \x1b[0m\x1b[38;5;231mn\x1b[0m\x1b[38;5;236m \x1b[0m\x1b[38;5;212m<\x1b[0m\x1b[38;5;212m=\x1b[0m\x1b[38;5;236m \x1b[0m\x1b[38;5;212m1\x1b[0m\x1b[38;5;146m:\x1b[0m
```

**Implementation**:
```python
# agentui/testing/snapshot.py
class ANSISnapshotter:
    """Snapshot testing for terminal output"""

    def __init__(self, snapshot_dir: Path):
        self.snapshot_dir = snapshot_dir

    def save_baseline(self, name: str, output: str):
        """Save ANSI output as baseline snapshot"""
        snapshot_file = self.snapshot_dir / f"{name}.ansi"
        snapshot_file.write_text(output)

        # Also save human-readable version
        readable_file = self.snapshot_dir / f"{name}.txt"
        readable_file.write_text(self._strip_ansi(output))

    def compare(self, name: str, current: str) -> SnapshotDiff:
        """Compare current output to baseline"""
        baseline_file = self.snapshot_dir / f"{name}.ansi"

        if not baseline_file.exists():
            raise SnapshotNotFoundError(f"No baseline for {name}")

        baseline = baseline_file.read_text()

        if baseline == current:
            return SnapshotDiff(matched=True, diff=None)

        return SnapshotDiff(
            matched=False,
            diff=self._diff_ansi(baseline, current)
        )
```

**Plugin Commands**:
```bash
# Create snapshot baseline
/snapshot-terminal create python-fibonacci
→ Renders UICode component
→ Saves ANSI output to snapshots/python-fibonacci.ansi
→ Creates regression test

# Compare against baseline
/snapshot-terminal compare python-fibonacci
→ Re-renders component
→ Diffs against baseline
→ Shows changes in ANSI codes with highlighting

# Update baseline (after intentional changes)
/snapshot-terminal update python-fibonacci
→ Replaces baseline with current output
```

---

### 4. Accessibility Testing Adaptation

**Web A11y** (current): axe-core for WCAG compliance
```javascript
const { violations } = await axe.run(component);
// Checks: color contrast, ARIA labels, keyboard navigation
```

**Terminal A11y** (needed): Different concerns
```python
# agentui/testing/accessibility.py
class TerminalA11yChecker:
    """Accessibility checker for terminal UIs"""

    def check_color_contrast(self, fg: str, bg: str) -> ContrastReport:
        """Verify readable contrast ratios for terminal colors"""
        # ANSI 212 (pink) on dark bg = 7.2:1 (AAA compliant)
        # ANSI 60 (gray) on dark bg = 3.8:1 (Fails AA)

        ratio = self._calculate_contrast_ratio(fg, bg)

        return ContrastReport(
            ratio=ratio,
            wcag_aa=ratio >= 4.5,
            wcag_aaa=ratio >= 7.0,
            recommendation=self._get_recommendation(ratio)
        )

    def check_unicode_compatibility(self, output: str) -> CompatReport:
        """Ensure box-drawing chars work in common terminals"""
        issues = []

        # Check for problematic characters
        if "╭" in output or "╰" in output:
            # Modern terminals: ✅
            # Legacy (Windows Console): ❌
            issues.append(UnicodeIssue(
                char="╭╰",
                terminals_ok=["iTerm2", "Windows Terminal", "Alacritty"],
                terminals_fail=["Windows Console (legacy)"],
                fallback="+--+"
            ))

        return CompatReport(issues=issues)

    def check_screen_reader_compat(self, output: str) -> A11yReport:
        """Verify output is readable by terminal screen readers"""
        # Strip ANSI codes
        plain_text = self._strip_ansi(output)

        # Check if meaning is preserved
        if self._has_visual_only_info(output):
            return A11yReport(
                accessible=False,
                issue="Visual information not available to screen readers",
                suggestion="Add text descriptions for visual elements"
            )

        return A11yReport(accessible=True)
```

**Plugin Skill**:
```markdown
# skills/TERMINAL_ACCESSIBILITY.md

## Terminal Accessibility Concerns

### Color Contrast
Ensure sufficient contrast ratios for readability:

- **Minimum**: 4.5:1 for normal text (WCAG AA)
- **Enhanced**: 7.0:1 for optimal readability (WCAG AAA)

Test across:
- 16-color terminals (basic ANSI)
- 256-color terminals (extended ANSI)
- TrueColor terminals (24-bit RGB)

Common terminal backgrounds:
- Dark: #1a1a2e, #000000, #282828
- Light: #ffffff, #fafafa, #f0f0f0

### Unicode Compatibility
Box-drawing characters compatibility matrix:

| Character | Modern Terminals | Legacy Terminals | Fallback |
|-----------|------------------|------------------|----------|
| ╭─╮       | ✅ iTerm2, WT    | ❌ Cmd.exe       | +--+     |
| │ │       | ✅ Alacritty     | ❌ PuTTY         | \| \|    |
| ╰─╯       | ✅ Kitty         | ❌ xterm (old)   | +--+     |

### Screen Reader Support
Terminal screen readers (BRLTTY, Orca):
- Read plain text after stripping ANSI codes
- Cannot interpret visual-only information

Best practices:
- Provide text alternatives for visual elements
- Ensure progress bars have percentage text
- Include semantic descriptions
- Test with `cat output.txt | strip-ansi | espeak`

### Testing Commands
```bash
# Check color contrast
/test-a11y contrast --fg "212" --bg "#1a1a2e"

# Verify unicode compatibility
/test-a11y unicode --check-chars "╭─╮│╰╯"

# Test screen reader output
/test-a11y screen-reader --component UICode
```
```

---

### 5. Protocol Testing (AgentUI-Specific)

**New Testing Layer**: Validate Python↔Go communication

```python
# agentui/testing/protocol_tester.py
class ProtocolTester:
    """Test the JSON Lines protocol between Python and Go TUI"""

    def __init__(self, tui_binary: Path = None):
        self.tui_binary = tui_binary or self._find_tui_binary()
        self.process = None

    def start_tui(self, theme: str = "charm-dark"):
        """Start TUI subprocess"""
        self.process = subprocess.Popen(
            [str(self.tui_binary), "--theme", theme],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

    def send_message(self, msg_type: str, payload: dict) -> str:
        """Send protocol message, capture TUI response"""
        message = {"type": msg_type, "payload": payload}
        json_msg = json.dumps(message) + "\n"

        self.process.stdin.write(json_msg)
        self.process.stdin.flush()

        # Read until we get complete output
        return self._read_until_complete()

    def test_code_rendering(self):
        """Test that code messages render correctly"""
        output = self.send_message("code", {
            "title": "Test Code",
            "language": "python",
            "code": "def hello(): pass"
        })

        # Verify rendering
        assert "Test Code" in output
        assert "╭" in output  # Border rendered
        assert "\x1b[" in output  # ANSI codes applied
        assert "def" in output

        return ProtocolTestResult(
            passed=True,
            message_type="code",
            output_length=len(output)
        )

    def test_request_response(self):
        """Test request/response correlation"""
        request_id = str(uuid.uuid4())

        output = self.send_message("form", {
            "id": request_id,
            "title": "Test Form",
            "fields": [{"name": "username", "type": "text"}]
        })

        # Simulate user input
        self.process.stdin.write(json.dumps({
            "type": "form_response",
            "id": request_id,
            "values": {"username": "test"}
        }) + "\n")

        # Verify correlation
        assert request_id in output
```

**Plugin Command**:
```bash
/test-protocol

# Interactive wizard:
Which protocol message type?
[x] code
[ ] table
[ ] progress
[ ] form
[ ] confirm

Which theme?
[x] charm-dark
[ ] charm-light

# Agent generates:
1. Sample protocol message JSON
2. Expected TUI output
3. Validation test
4. Snapshot baseline
```

---

### 6. Visual Regression for Terminal Output

**Web**: Compare pixel screenshots
**Terminal**: Compare ANSI output with smart diffing

```python
# agentui/testing/ansi_differ.py
class ANSIDiffer:
    """Diff terminal output accounting for ANSI codes"""

    def diff(self, baseline: str, current: str) -> ANSIDiff:
        """Compare two ANSI outputs"""

        # Parse ANSI escape sequences into structured tokens
        baseline_tokens = self._parse_ansi(baseline)
        current_tokens = self._parse_ansi(current)

        # Perform structured diff
        changes = self._diff_tokens(baseline_tokens, current_tokens)

        return ANSIDiff(changes=changes)

    def _parse_ansi(self, text: str) -> list[Token]:
        """Parse ANSI string into tokens"""
        tokens = []
        current_pos = 0

        # Find all ANSI escape sequences
        for match in re.finditer(r'\x1b\[[0-9;]*m', text):
            # Add text before escape
            if match.start() > current_pos:
                tokens.append(TextToken(text[current_pos:match.start()]))

            # Add ANSI code
            tokens.append(ANSIToken(match.group()))
            current_pos = match.end()

        # Add remaining text
        if current_pos < len(text):
            tokens.append(TextToken(text[current_pos:]))

        return tokens

    def render_diff(self, diff: ANSIDiff) -> str:
        """Render diff in human-readable format"""
        lines = []

        for change in diff.changes:
            if change.type == ChangeType.COLOR_CHANGED:
                lines.append(
                    f"  Line {change.line}: Color changed\n"
                    f"    - {self._decode_ansi(change.old_code)} "
                    f"(baseline: {change.old_color})\n"
                    f"    + {self._decode_ansi(change.new_code)} "
                    f"(current: {change.new_color})"
                )
            elif change.type == ChangeType.TEXT_CHANGED:
                lines.append(
                    f"  Line {change.line}: Text changed\n"
                    f"    - \"{change.old_text}\"\n"
                    f"    + \"{change.new_text}\""
                )

        return "\n".join(lines)

    def _decode_ansi(self, code: str) -> str:
        """Decode ANSI code to human-readable color name"""
        # \x1b[38;5;212m → "Pink (ANSI 212)"
        # \x1b[1m → "Bold"
        # \x1b[3m → "Italic"
        mapping = {
            "\x1b[38;5;212m": "Pink (ANSI 212)",
            "\x1b[38;5;35m": "Teal (ANSI 35)",
            "\x1b[38;5;99m": "Purple (ANSI 99)",
            "\x1b[1m": "Bold",
            "\x1b[3m": "Italic",
            "\x1b[0m": "Reset"
        }
        return mapping.get(code, code)
```

**HTML Diff Report**:
```html
<!-- generated by /visual-regression-terminal -->
<html>
<head>
  <style>
    .diff-container { font-family: monospace; }
    .removed { background: #ffdddd; }
    .added { background: #ddffdd; }
    .changed { background: #ffffdd; }
  </style>
</head>
<body>
  <h1>Terminal Snapshot Diff: python-fibonacci</h1>

  <div class="diff-container">
    <h2>Baseline</h2>
    <pre style="color: #FF87D7; font-weight: bold;">def</pre>

    <h2>Current</h2>
    <pre style="color: #875FFF;">def</pre>

    <h2>Changes</h2>
    <div class="changed">
      Line 1: Keyword color changed
      - Pink #FF87D7 (baseline)
      + Purple #875FFF (current)
    </div>
  </div>
</body>
</html>
```

**Plugin Integration**:
```bash
/visual-regression-terminal

# Workflow:
1. Detects all snapshots in snapshots/terminal/
2. Re-renders each component
3. Compares to baseline
4. Generates HTML report at reports/terminal-regression.html
5. Opens report in browser
```

---

### 7. Component Detection & Scaffolding

**Web**: Detects React components, generates `.stories.tsx`
**Terminal**: Detect UI primitives, generate tests

```python
# agentui/testing/component_scanner.py
import inspect
from typing import Callable, get_type_hints

class ComponentScanner:
    """Scan AgentUI project for UI primitives and tools"""

    def find_ui_tools(self, app: AgentApp) -> list[UIToolInfo]:
        """Find all @app.ui_tool decorated functions"""
        tools = []

        # Scan all registered tools
        for name, tool_fn in app._tools.items():
            # Get function signature and return type
            sig = inspect.signature(tool_fn)
            hints = get_type_hints(tool_fn)
            return_type = hints.get('return')

            # Check if it returns a UI primitive
            if self._is_ui_primitive(return_type):
                tools.append(UIToolInfo(
                    name=name,
                    function=tool_fn,
                    return_type=return_type,
                    parameters=tool_fn.__tool_params__
                ))

        return tools

    def _is_ui_primitive(self, type_hint) -> bool:
        """Check if type is a UI primitive"""
        ui_types = {UICode, UITable, UIProgress, UIForm, UIConfirm}
        return type_hint in ui_types

    def generate_tests(self, tools: list[UIToolInfo]) -> str:
        """Generate comprehensive test file for all UI tools"""
        test_functions = []

        for tool in tools:
            test_fn = self._generate_test_function(tool)
            test_functions.append(test_fn)

        return f'''# tests/test_ui_components.py
# Auto-generated by /scaffold-tui-tests

import pytest
from agentui.testing import ComponentTester

tester = ComponentTester(theme="charm-dark")

{"".join(test_functions)}
'''

    def _generate_test_function(self, tool: UIToolInfo) -> str:
        """Generate test function for a single tool"""
        # Infer test parameters
        params = self._infer_test_params(tool)

        return f'''
def test_{tool.name}():
    """Test {tool.name} UI component rendering"""
    # Call the tool
    result = {tool.name}({params})

    # Render the UI primitive
    output = tester.render(result)

    # Verify rendering
    assert output is not None
    assert len(output) > 0

    # Check for ANSI codes (syntax highlighting)
    assert "\\x1b[" in output

    # Snapshot test
    tester.snapshot_match("{tool.name}", output)
'''

    def _infer_test_params(self, tool: UIToolInfo) -> str:
        """Infer sensible test parameters"""
        # If tool takes 'language', use 'python'
        if 'language' in tool.parameters:
            return 'language="python"'

        # If tool takes no params, return empty
        if not tool.parameters:
            return ''

        # Generate defaults based on parameter types
        params = []
        for param, schema in tool.parameters.items():
            if schema['type'] == 'string':
                params.append(f'{param}="test"')
            elif schema['type'] == 'integer':
                params.append(f'{param}=42')

        return ', '.join(params)
```

**Plugin Command**:
```bash
/scaffold-tui-tests

# Agent workflow:
1. Scans project for AgentApp instance
2. Finds all @app.ui_tool decorated functions:
   - show_code_example (returns UICode)
   - show_benchmark_results (returns UITable)
   - simulate_deployment (returns UIProgress)

3. Generates test file:
   tests/test_ui_components.py

4. Creates snapshot directory:
   tests/__snapshots__/test_ui_components/

5. Generates CI workflow:
   .github/workflows/tui-tests.yml

# Output:
✅ Generated 3 test functions
✅ Created snapshot baselines
✅ Added CI workflow
```

---

## Technical Requirements

### Dependencies

**Python (Terminal Testing)**:
```toml
# pyproject.toml
[project.optional-dependencies]
testing = [
    "pytest>=8.0.0",
    "pytest-snapshot>=0.9.0",     # Snapshot testing
    "pytest-asyncio>=0.23.0",     # Async test support
    "pexpect>=4.9.0",             # Terminal interaction
    "ansi2html>=1.9.0",           # ANSI → HTML conversion
    "colorama>=0.4.6",            # Cross-platform ANSI
]
```

**TypeScript (Plugin Core)**:
```json
{
  "name": "component-testing-assistant",
  "dependencies": {
    "@anthropic/sdk": "^0.30.0",
    "terminal-kit": "^3.0.0",     // Terminal rendering utilities
    "ansi-escapes": "^7.0.0",     // ANSI code manipulation
    "ansi-diff": "^1.2.0",        // Terminal output diffing
    "chalk": "^5.3.0",            // Colored terminal output
    "strip-ansi": "^7.1.0"        // ANSI code removal
  }
}
```

**Go (TUI Testing)**:
```go
// For testing the Go TUI directly
import (
    "testing"
    "github.com/charmbracelet/bubbletea"
    "github.com/Netflix/go-expect"  // Terminal interaction
)
```

---

## Implementation Roadmap

### Phase 1: Foundation (Week 1)
- [ ] Abstract core rendering interface
- [ ] Create `TerminalRenderer` class (Python bridge to Go TUI)
- [ ] Build ANSI snapshot system (`ANSISnapshotter`)
- [ ] Add terminal project detection to hooks
- [ ] Create basic `ComponentTester` class

**Deliverable**: Can test a single UICode component

### Phase 2: Testing Infrastructure (Week 2)
- [ ] Component scanner (`ComponentScanner`)
- [ ] Protocol message tester (`ProtocolTester`)
- [ ] ANSI differ with visual output (`ANSIDiffer`)
- [ ] Terminal a11y checker (`TerminalA11yChecker`)
- [ ] HTML diff report generator

**Deliverable**: Full testing suite for AgentUI projects

### Phase 3: Plugin Integration (Week 3)
- [ ] Create `/test-tui-component` command
- [ ] Create `/snapshot-terminal` command
- [ ] Create `/scaffold-tui-tests` command
- [ ] Build terminal component tester agent
- [ ] Write terminal testing skills

**Deliverable**: Storybook Assistant supports terminal UIs

### Phase 4: Developer Experience (Week 4)
- [ ] Interactive test generation wizard
- [ ] CI/CD integration templates (GitHub Actions)
- [ ] Documentation with examples
- [ ] Demo video and quickstart guide
- [ ] Plugin marketplace submission

**Deliverable**: Production-ready universal testing framework

---

## Key Challenges & Solutions

### Challenge 1: Dual Language Support
**Problem**: Plugin core is TypeScript, AgentUI testing is Python + Go
**Solution**: Use child processes with JSON communication
```typescript
// Plugin spawns Python test runner
const testRunner = spawn('uv', ['run', 'python', '-m', 'agentui.testing']);
testRunner.stdin.write(JSON.stringify({ command: 'test', component: 'UICode' }));
const result = JSON.parse(testRunner.stdout.read());
```

### Challenge 2: Snapshot Storage Format
**Problem**: ANSI codes are binary, hard to review in version control
**Solution**: Store both raw ANSI and human-readable versions
```
snapshots/
├── python-fibonacci.ansi          # Raw ANSI (for exact comparison)
└── python-fibonacci.txt           # Plain text (for human review)
```

### Challenge 3: Visual Regression Detection
**Problem**: Pixels (web) vs characters/colors (terminal)
**Solution**: Custom diff algorithm for ANSI sequences
```python
# Detect semantic changes, not just byte differences
diff = ANSIDiffer().diff(baseline, current)
# Returns: "Keyword color changed from pink to purple on line 3"
```

### Challenge 4: CI/CD Integration
**Problem**: Terminal output requires pseudo-TTY
**Solution**: Use `script` command or pexpect
```yaml
# .github/workflows/tui-tests.yml
- name: Run TUI tests
  run: |
    script -qec "uv run pytest tests/test_ui_components.py" /dev/null
```

### Challenge 5: Cross-Platform Terminal Compatibility
**Problem**: ANSI codes render differently across terminals
**Solution**: Test matrix with common terminals
```yaml
strategy:
  matrix:
    terminal: [xterm-256color, screen-256color, tmux-256color]
env:
  TERM: ${{ matrix.terminal }}
```

---

## Success Metrics

### For AgentUI Projects
- ✅ **Component testing**: All UI primitives testable in isolation
- ✅ **Snapshot regression**: Visual changes caught automatically
- ✅ **Protocol validation**: Python↔Go communication verified
- ✅ **A11y compliance**: Color contrast and screen reader compatibility

### For Storybook Assistant Plugin
- ✅ **Dual environment**: Supports both web and terminal projects
- ✅ **Unified workflow**: Same commands work across environments
- ✅ **Auto-detection**: Automatically identifies project type
- ✅ **Developer adoption**: Used in 10+ AgentUI projects

### For Component Testing Community
- ✅ **Reusable framework**: Other TUI frameworks can adopt
- ✅ **Best practices**: Establishes standards for terminal UI testing
- ✅ **Documentation**: Comprehensive guides and examples
- ✅ **Marketplace presence**: Listed in Claude plugin marketplace

---

## Future Enhancements

### Terminal Recording & Playback
```bash
/record-session demo.tape
# Records user interactions
# Saves as Asciinema format
# Can replay for testing
```

### Performance Benchmarking
```python
class PerformanceTester:
    def benchmark_render_time(self, component: UICode):
        """Measure component rendering speed"""
        # Track: time to first render, ANSI code generation time
```

### Multi-Terminal Testing
```bash
/test-cross-terminal
# Tests component in:
# - iTerm2 (macOS)
# - Windows Terminal (Windows)
# - Alacritty (Linux)
# - tmux (multiplexed)
```

### Integration with VHS (Charm's tool)
```bash
# Generate VHS tape from test
/generate-vhs-demo python-fibonacci
# Output: demo.tape (can create GIFs)
```

---

## Resources & References

### AgentUI Testing
- ComponentTester implementation (to be built)
- Protocol specification: `src/agentui/protocol.py`
- TUI rendering: `internal/ui/views/`

### Storybook Assistant
- GitHub: https://github.com/flight505/storybook-assistant
- Architecture: Skills, Commands, Agents, Hooks
- Testing patterns: Interaction, visual regression, a11y

### Terminal Testing Tools
- **pexpect**: Terminal interaction automation
- **Asciinema**: Terminal session recording
- **VHS**: Terminal GIF generation (Charm)
- **ansi2html**: Convert ANSI to HTML for reports

### Related Frameworks
- **Ink** (React for CLIs): Testing with `ink-testing-library`
- **Textual** (Python TUIs): Snapshot testing built-in
- **Bubbletea** (Go TUIs): Unit testing with mocks

---

## Next Steps

### Immediate (This Week)
1. Build `ComponentTester` in AgentUI repo
2. Validate testing patterns with real components
3. Document API and usage

### Short-term (Next 2-4 Weeks)
1. Design plugin architecture in detail
2. Create terminal testing skills
3. Build `/test-tui-component` command prototype

### Long-term (Next 2-3 Months)
1. Full plugin integration
2. CI/CD templates
3. Marketplace submission
4. Community adoption

---

## Contact & Collaboration

**Author**: Jesper (flight505)
**AgentUI**: https://github.com/flight505/agent-ui-framework
**Storybook Assistant**: https://github.com/flight505/storybook-assistant

**Questions?** Open an issue on either repository or reach out directly.

---

**Last Updated**: 2026-01-18
**Status**: Planning Phase
**Next Review**: After ComponentTester is built and validated
