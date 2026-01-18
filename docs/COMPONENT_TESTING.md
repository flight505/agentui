# Component Testing with AgentUI

**ComponentTester** - Test AgentUI components in isolation, like Storybook for terminal UIs.

## Overview

The AgentUI testing framework allows you to test UI components (UICode, UITable, UIProgress) in isolation without requiring a full AgentUI app or LLM integration.

### Features

- ✅ **Isolated rendering**: Test components without full app
- ✅ **Snapshot testing**: Capture ANSI output for regression testing
- ✅ **Theme support**: Test with CharmDark, CharmLight, etc.
- ✅ **Syntax highlighting**: Verify Chroma highlighting works
- ✅ **ANSI assertions**: Check colors, styles, and formatting
- ✅ **Fast execution**: No LLM API calls needed

---

## Installation

The testing framework is included with AgentUI:

```bash
# Install with testing extras
uv sync --extra testing

# Or add to existing project
uv add --dev pytest pytest-asyncio
```

---

## Quick Start

### Basic Usage

```python
from agentui.testing import ComponentTester, ANSIAsserter

# Initialize tester
tester = ComponentTester(theme="charm-dark")
asserter = ANSIAsserter()

# Render a code component
result = tester.render_code(
    language="python",
    code="def hello(): print('world')"
)

# Verify rendering
assert result.success
assert result.has_ansi_codes()

# Verify syntax highlighting
asserter.assert_has_pink_keywords(result.output)  # Keywords in pink
asserter.assert_has_teal_strings(result.output)   # Strings in teal
asserter.assert_has_bold_text(result.output)      # Bold styling
```

---

## How It Works: Headless Mode

ComponentTester uses the Go TUI binary in **headless mode** for testing. This mode allows automated rendering without requiring an interactive terminal (TTY).

### Headless Mode Overview

The `--headless` flag enables non-interactive rendering:

```bash
# Headless rendering
./bin/agentui-tui --headless --theme charm-dark < message.json > output.ansi
```

**What happens in headless mode:**
1. TUI skips TTY initialization (no interactive terminal needed)
2. Reads a single JSON protocol message from stdin
3. Renders the appropriate view (CodeView, TableView, etc.)
4. Outputs ANSI-formatted result to stdout
5. Exits immediately (non-interactive)

**Why this matters:**
- ✅ Enables automated testing in CI/CD (no TTY required)
- ✅ Fast execution (single render, immediate exit)
- ✅ Deterministic output (same input = same output)
- ✅ Protocol validation (tests Python↔Go communication)

### Direct Headless Usage

You can use headless mode directly for debugging:

```bash
# Create test message
echo '{"type":"code","payload":{"language":"python","code":"def hello(): pass","title":"Test"}}' | \
  ./bin/agentui-tui --headless --theme charm-dark > output.ansi

# View the ANSI output
cat output.ansi

# Or convert to plain text
cat output.ansi | sed 's/\x1b\[[0-9;]*m//g'
```

### ComponentTester Implementation

ComponentTester wraps headless mode for easy Python testing:

```python
# This code...
result = tester.render_code("python", "def hello(): pass")

# ...internally runs:
# echo '{"type":"code",...}' | ./bin/agentui-tui --headless --theme charm-dark
```

**Process flow:**
1. ComponentTester converts UI component to protocol JSON
2. Spawns TUI subprocess with `--headless --theme <theme>` flags
3. Sends JSON message to stdin
4. Captures stdout (ANSI output)
5. Returns RenderResult with output and metadata

---

## ComponentTester API

### Initialization

```python
tester = ComponentTester(
    theme="charm-dark",      # Theme to use
    tui_binary=None,         # Path to TUI binary (auto-detected)
    width=80,                # Terminal width
    height=24                # Terminal height
)
```

### Rendering Components

#### UICode (Syntax-Highlighted Code)

```python
result = tester.render_code(
    language="python",
    code="def fibonacci(n):\n    if n <= 1:\n        return n",
    title="Fibonacci"
)
```

**Supported languages**: Python, Go, TypeScript, Rust

#### UITable

```python
result = tester.render_table(
    headers=["Name", "Age", "City"],
    rows=[
        ["Alice", "30", "NYC"],
        ["Bob", "25", "SF"]
    ],
    title="User Table"
)
```

#### Generic Component Rendering

```python
from agentui.types import UICode, UIProgress

# Create component
component = UICode(
    title="Example",
    language="go",
    code="func main() {}"
)

# Render it
result = tester.render(component)
```

### RenderResult

The `render()` methods return a `RenderResult`:

```python
class RenderResult:
    output: str          # Raw ANSI output
    exit_code: int       # TUI exit code
    stderr: str          # Error output
    success: bool        # True if rendering succeeded

    # Properties
    plain_text: str      # Output with ANSI stripped

    # Methods
    has_ansi_codes() -> bool
    find_color_code(ansi_code: str) -> bool
```

**Example**:

```python
result = tester.render_code("python", "x = 42")

print(result.output)      # ANSI-formatted output
print(result.plain_text)  # Plain text without colors
print(result.success)     # True

if result.find_color_code("\x1b[38;5;212m"):
    print("Pink color found!")
```

---

## Snapshot Testing

Capture component output and compare against baselines for regression testing.

### Creating Baselines

```python
from agentui.testing import ANSISnapshotter

snapshotter = ANSISnapshotter()

# Render component
result = tester.render_code("python", "def hello(): pass")

# Save as baseline
snapshotter.save_baseline("python-hello", result.output)
```

**Files created**:
```
tests/__snapshots__/
├── python-hello.ansi    # Raw ANSI output
└── python-hello.txt     # Human-readable (colors stripped)
```

### Comparing Against Baselines

```python
# Later, after code changes
new_result = tester.render_code("python", "def hello(): pass")

# Compare to baseline
diff = snapshotter.compare("python-hello", new_result.output)

if diff.matched:
    print("✅ Snapshot matched!")
else:
    print(f"❌ Snapshot mismatch:\n{diff.render()}")
```

### Updating Baselines

After intentional changes:

```python
# Update baseline with new output
snapshotter.update("python-hello", new_output)
```

### In pytest Tests

```python
def test_syntax_highlighting():
    result = tester.render_code("python", "def hello(): pass")

    # Snapshot assertion
    tester.snapshot_match("python-hello", result.output)
    # Raises AssertionError if doesn't match
```

---

## ANSI Assertions

Verify colors, styles, and formatting in rendered output.

### Basic Assertions

```python
from agentui.testing import ANSIAsserter

asserter = ANSIAsserter()

result = tester.render_code("python", code)

# ANSI codes present
asserter.assert_has_ansi_codes(result.output)

# Borders present
asserter.assert_has_borders(result.output)

# Text content
asserter.assert_contains_text(result.output, "hello")
```

### Color Assertions (CharmDark Theme)

```python
# Pink keywords (def, if, for, async)
asserter.assert_has_pink_keywords(result.output)

# Teal strings ("...", '...')
asserter.assert_has_teal_strings(result.output)

# Purple functions
asserter.assert_has_purple_functions(result.output)

# Gray comments (# ...)
asserter.assert_has_gray_comments(result.output)
```

### Style Assertions

```python
# Bold text
asserter.assert_has_bold_text(result.output)

# Italic text
asserter.assert_has_italic_text(result.output)
```

### Size Assertions

Verify syntax highlighting increases output size:

```python
plain_code = "def hello(): pass"
result = tester.render_code("python", plain_code)

# Highlighted code should be 2-8x larger
asserter.assert_larger_than_plain(
    result.output,
    plain_code,
    min_ratio=2.0
)
```

### Custom Color Codes

```python
# Check for specific ANSI code
asserter.assert_has_color_code(result.output, "212")  # Pink

# Or use directly
if result.find_color_code("\x1b[38;5;212m"):
    print("Pink keywords found!")
```

---

## pytest Integration

### Example Test File

```python
# tests/test_ui_components.py

import pytest
from agentui.testing import ComponentTester, ANSIAsserter

tester = ComponentTester(theme="charm-dark")
asserter = ANSIAsserter()


class TestSyntaxHighlighting:
    """Test syntax highlighting across languages"""

    def test_python_highlighting(self):
        result = tester.render_code("python", 'def hello(): print("hi")')

        assert result.success
        asserter.assert_has_pink_keywords(result.output)
        asserter.assert_has_teal_strings(result.output)

    def test_go_highlighting(self):
        result = tester.render_code("go", 'func main() { fmt.Println("hi") }')

        assert result.success
        asserter.assert_has_ansi_codes(result.output)

    @pytest.mark.parametrize("language", ["python", "go", "typescript", "rust"])
    def test_all_languages(self, language):
        code_samples = {
            "python": "def hello(): pass",
            "go": "func main() {}",
            "typescript": "function hello() {}",
            "rust": "fn main() {}"
        }

        result = tester.render_code(language, code_samples[language])

        assert result.success
        asserter.assert_has_ansi_codes(result.output)


class TestSnapshots:
    """Test snapshot regression"""

    def test_python_fibonacci(self):
        code = "def fibonacci(n):\n    if n <= 1:\n        return n"
        result = tester.render_code("python", code)

        # This will fail if output changed
        tester.snapshot_match("fibonacci", result.output)
```

### Running Tests

```bash
# Run all tests
uv run pytest tests/test_ui_components.py -v

# Run specific test
uv run pytest tests/test_ui_components.py::TestSyntaxHighlighting -v

# Run with output
uv run pytest tests/test_ui_components.py -v -s
```

---

## Theme Testing

Test components across different themes:

```python
@pytest.mark.parametrize("theme", ["charm-dark", "charm-light"])
def test_theme_rendering(theme):
    tester = ComponentTester(theme=theme)

    result = tester.render_code("python", "x = 42")

    assert result.success
    assert result.has_ansi_codes()
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/test-ui-components.yml

name: UI Component Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync --extra testing

      - name: Build TUI binary
        run: make build-tui

      - name: Run component tests
        run: uv run pytest tests/test_component_tester.py -v

      - name: Upload snapshots
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: test-snapshots
          path: tests/__snapshots__/
```

---

## Best Practices

### 1. Create Baselines Early

```python
# In conftest.py or setup
@pytest.fixture(scope="session", autouse=True)
def setup_snapshots():
    """Create snapshot baselines before tests run"""
    snapshotter = ANSISnapshotter()

    # Create baselines for common components
    baselines = {
        "python-simple": tester.render_code("python", "x = 42"),
        "go-simple": tester.render_code("go", "x := 42"),
    }

    for name, result in baselines.items():
        snapshotter.save_baseline(name, result.output, overwrite=True)
```

### 2. Use Parametrized Tests

```python
@pytest.mark.parametrize("lang,code", [
    ("python", "def hello(): pass"),
    ("go", "func main() {}"),
    ("typescript", "function hello() {}"),
])
def test_language_rendering(lang, code):
    result = tester.render_code(lang, code)
    assert result.success
```

### 3. Test Edge Cases

```python
def test_empty_code():
    result = tester.render_code("python", "")
    assert result.success

def test_very_long_code():
    code = "x = 1\n" * 1000
    result = tester.render_code("python", code)
    assert result.success

def test_unicode_in_code():
    result = tester.render_code("python", 'print("你好 🎨")')
    assert result.success
```

### 4. Verify Theme Consistency

```python
def test_charm_dark_colors():
    """Verify CharmDark theme applies correct colors"""
    result = tester.render_code("python", "def hello(): pass")

    # Check specific ANSI codes for CharmDark
    assert result.find_color_code("\x1b[38;5;212m")  # Pink
    assert result.find_color_code("\x1b[38;5;35m")   # Teal
```

---

## Troubleshooting

### TUI Binary Not Found

```python
FileNotFoundError: TUI binary not found at bin/agentui-tui
```

**Solution**: Build the TUI binary first:
```bash
make build-tui
```

### Headless Mode Not Working

```
Error: could not open a new TTY: open /dev/tty: device not configured
```

**Solution**: Ensure you're using the latest TUI binary with `--headless` mode support:
```bash
# Rebuild TUI with headless support
make clean
make build-tui

# Test headless mode directly
echo '{"type":"code","payload":{"language":"python","code":"x=1","title":"Test"}}' | \
  ./bin/agentui-tui --headless --theme charm-dark
```

If the error persists, check that your TUI binary includes the headless mode implementation (added in commit a66aa94).

### Snapshot Mismatch

```python
AssertionError: Snapshot mismatch for 'python-hello'
```

**Solution**: Review changes, then update baseline:
```python
snapshotter.update("python-hello", new_output)
```

### No ANSI Codes in Output

```python
AssertionError: Output does not contain ANSI escape sequences
```

**Solution**: Ensure TUI binary is built with Chroma support:
```bash
make clean
make build-tui
```

---

## Examples

See these files for complete examples:

- `tests/test_component_tester.py` - Comprehensive test suite
- `examples/test_syntax_visual.py` - Visual testing demo
- `docs/STORYBOOK_ASSISTANT_EXPANSION.md` - Future plugin design

---

## API Reference

### ComponentTester

```python
class ComponentTester:
    def __init__(theme="charm-dark", tui_binary=None, width=80, height=24)

    def render(component: UIComponent) -> RenderResult
    def render_code(language: str, code: str, title="Code") -> RenderResult
    def render_table(headers, rows, title="Table") -> RenderResult
    def snapshot_match(name: str, output: str) -> None
```

### ANSISnapshotter

```python
class ANSISnapshotter:
    def __init__(snapshot_dir="tests/__snapshots__")

    def save_baseline(name: str, output: str, overwrite=False)
    def compare(name: str, current: str) -> SnapshotDiff
    def update(name: str, new_output: str)
    def list_snapshots() -> list[str]
    def delete(name: str)
```

### ANSIAsserter

```python
class ANSIAsserter:
    # ANSI Detection
    def has_ansi_codes(output) -> bool
    def assert_has_ansi_codes(output)

    # Colors (CharmDark)
    def assert_has_pink_keywords(output)
    def assert_has_teal_strings(output)
    def assert_has_purple_functions(output)
    def assert_has_gray_comments(output)

    # Styles
    def assert_has_bold_text(output)
    def assert_has_italic_text(output)

    # Content
    def assert_contains_text(output, text)
    def assert_has_borders(output)

    # Size
    def assert_larger_than_plain(highlighted, plain, min_ratio=2.0)
```

---

## Next Steps

- Read [STORYBOOK_ASSISTANT_EXPANSION.md](./STORYBOOK_ASSISTANT_EXPANSION.md) for plugin integration plans
- See [TESTING_LLM.md](./TESTING_LLM.md) for full app testing with real LLM
- Check [ANIMATIONS.md](./ANIMATIONS.md) for animation testing

---

**Last Updated**: 2026-01-18 (Added headless mode documentation)
**Status**: Production Ready ✅
**Headless Mode**: Implemented in commit a66aa94
