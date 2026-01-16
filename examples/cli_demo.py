#!/usr/bin/env python3
"""
CLI Demo - Test the CLI fallback interface.

This demo works without the Go TUI binary.
It shows Rich-based rendering of UI elements.

Run:
    python examples/cli_demo.py
"""

import asyncio
from agentui.bridge import CLIBridge, TUIConfig
from agentui.primitives import (
    UIForm,
    UIProgress,
    UIProgressStep,
    UITable,
    UICode,
    UIConfirm,
    UISelect,
    text_field,
    select_field,
    checkbox_field,
)


async def demo_cli_elements():
    """Demonstrate CLI fallback rendering."""
    config = TUIConfig(
        app_name="CLI Demo",
        tagline="Testing Rich fallback",
    )
    
    bridge = CLIBridge(config)
    await bridge.start()
    
    print("\n" + "=" * 50)
    print("1. Text & Markdown")
    print("=" * 50)
    
    await bridge.send_text("Hello! This is streaming text...")
    await bridge.send_text(" and more text", done=True)
    print()
    
    await bridge.send_markdown("""
## Markdown Demo

This is **bold** and this is *italic*.

- Bullet point 1
- Bullet point 2
- Bullet point 3

```python
def hello():
    print("Hello, World!")
```
""")
    
    print("\n" + "=" * 50)
    print("2. Tables")
    print("=" * 50 + "\n")
    
    await bridge.send_table(
        columns=["Service", "Cost", "Status"],
        rows=[
            ["EC2", "$30.00", "Running"],
            ["RDS", "$25.00", "Running"],
            ["S3", "$5.00", "Active"],
        ],
        title="Cloud Costs",
    )
    
    print("\n" + "=" * 50)
    print("3. Code Blocks")
    print("=" * 50 + "\n")
    
    await bridge.send_code(
        code='''async def main():
    app = AgentApp(
        name="my-agent",
        provider="claude",
    )
    await app.run()''',
        language="python",
        title="example.py",
    )
    
    print("\n" + "=" * 50)
    print("4. Progress")
    print("=" * 50 + "\n")
    
    await bridge.send_progress(
        message="Processing...",
        percent=75,
    )
    
    print("\n" + "=" * 50)
    print("5. Alerts")
    print("=" * 50 + "\n")
    
    await bridge.send_alert("This is an info alert", severity="info")
    await bridge.send_alert("Operation successful!", severity="success")
    await bridge.send_alert("Warning: check configuration", severity="warning")
    await bridge.send_alert("Error: connection failed", severity="error")
    
    print("\n" + "=" * 50)
    print("6. Forms (Interactive)")
    print("=" * 50 + "\n")
    
    # Form demo
    form_result = await bridge.request_form(
        fields=[
            text_field("name", "Project Name").to_dict(),
            select_field("language", "Language", ["Python", "Go", "Rust"]).to_dict(),
            checkbox_field("docker", "Include Docker").to_dict(),
        ],
        title="Project Setup",
        description="Configure your new project",
    )
    
    if form_result:
        print(f"\nForm submitted: {form_result}")
    
    print("\n" + "=" * 50)
    print("7. Confirmation (Interactive)")
    print("=" * 50 + "\n")
    
    confirmed = await bridge.request_confirm(
        "Deploy to production?",
        title="Confirm Deployment",
    )
    print(f"Confirmed: {confirmed}")
    
    print("\n" + "=" * 50)
    print("8. Selection (Interactive)")
    print("=" * 50 + "\n")
    
    selected = await bridge.request_select(
        "Choose your theme:",
        ["Catppuccin Mocha", "Dracula", "Nord", "Tokyo Night"],
    )
    print(f"Selected: {selected}")
    
    print("\n" + "=" * 50)
    print("Demo Complete!")
    print("=" * 50)
    
    await bridge.stop()


if __name__ == "__main__":
    asyncio.run(demo_cli_elements())
