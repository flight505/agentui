#!/usr/bin/env python3
"""
AgentUI CLI - Command line interface for AgentUI.

Commands:
    run     - Run an agent app from a manifest
    init    - Create a new agent app scaffold
    quick   - Quick one-shot interaction
    themes  - List available themes
"""

import argparse
import asyncio
import sys
from pathlib import Path


def cmd_run(args):
    """Run an agent app."""
    from agentui.app import AgentApp
    
    app_path = Path(args.path)
    
    if not app_path.exists():
        print(f"Error: Path not found: {app_path}", file=sys.stderr)
        sys.exit(1)
    
    app = AgentApp(
        manifest=app_path,
        provider=args.provider if args.provider else None,
        model=args.model if args.model else None,
        theme=args.theme,
    )
    
    asyncio.run(app.run())


def cmd_init(args):
    """Create a new agent app scaffold."""
    name = args.name
    target = Path(args.path or name)
    
    if target.exists():
        print(f"Error: Directory already exists: {target}", file=sys.stderr)
        sys.exit(1)
    
    # Create directory structure
    target.mkdir(parents=True)
    (target / "skills").mkdir()
    (target / "outputs").mkdir()
    
    # Create app.yaml
    app_yaml = f'''# {name} - AgentUI Application
name: {name}
version: 1.0.0
description: An AI-powered agent application

display_name: "{name.replace('-', ' ').title()}"
icon: 🤖
tagline: "AI Agent Interface"

providers:
  default: claude
  
  claude:
    model: claude-sonnet-4-5-20250929
    max_tokens: 4096
  
  openai:
    model: gpt-4o

skills: []

system_prompt: |
  You are a helpful AI assistant.
  Be concise and friendly.

ui:
  theme: catppuccin-mocha
  
  welcome:
    title: "Welcome to {name.replace('-', ' ').title()}"
    subtitle: "How can I help you today?"
    features:
      - "🤖 AI-powered assistance"
      - "🔧 Tool integration"
      - "📊 Rich UI elements"

output:
  directory: ./outputs
'''
    
    (target / "app.yaml").write_text(app_yaml)
    
    # Create main.py
    main_py = f'''#!/usr/bin/env python3
"""
{name} - Main entry point.
"""

import asyncio
from agentui import AgentApp

app = AgentApp(manifest="app.yaml")


# Example tool - customize this!
@app.tool(
    name="greet",
    description="Greet someone by name",
    parameters={{
        "type": "object",
        "properties": {{
            "name": {{"type": "string", "description": "Name to greet"}}
        }},
        "required": ["name"]
    }}
)
def greet(name: str) -> dict:
    """Return a greeting."""
    return {{"greeting": f"Hello, {{name}}!"}}


async def main():
    """Run the agent."""
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
'''
    
    (target / "main.py").write_text(main_py)
    
    # Create README
    readme = f'''# {name}

An AI agent application built with AgentUI.

## Run

```bash
cd {name}
agentui run .
```

Or with Python:

```bash
python main.py
```

## Configuration

Edit `app.yaml` to configure:
- LLM provider and model
- System prompt
- UI theme
- Skills

## Adding Tools

Add tools in `main.py` using the `@app.tool` decorator:

```python
@app.tool(
    name="my_tool",
    description="What this tool does",
    parameters={{...}}
)
def my_tool(arg1: str) -> dict:
    return {{"result": "..."}}
```
'''
    
    (target / "README.md").write_text(readme)
    
    print(f"✨ Created new agent app: {target}")
    print()
    print("Get started:")
    print(f"  cd {target}")
    print(f"  agentui run .")


def cmd_quick(args):
    """Quick one-shot interaction."""
    from agentui.app import quick_chat
    
    prompt = " ".join(args.prompt)
    if not prompt:
        print("Error: Please provide a prompt", file=sys.stderr)
        sys.exit(1)
    
    response = asyncio.run(quick_chat(
        message=prompt,
        provider=args.provider,
        model=args.model,
    ))
    
    print(response)


def cmd_themes(args):
    """List available themes."""
    themes = [
        ("catppuccin-mocha", "Soothing dark with purple accents (default)"),
        ("catppuccin-latte", "Light mode with soft colors"),
        ("dracula", "Classic dark theme"),
        ("nord", "Arctic, bluish colors"),
        ("tokyo-night", "Vibrant dark theme"),
    ]
    
    print("Available themes:")
    print()
    for name, desc in themes:
        marker = "→" if name == "catppuccin-mocha" else " "
        print(f"  {marker} {name:<20} {desc}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="agentui",
        description="Build beautiful AI agent applications",
    )
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="agentui 0.1.0",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # run command
    run_parser = subparsers.add_parser("run", help="Run an agent app")
    run_parser.add_argument("path", help="Path to app directory or app.yaml")
    run_parser.add_argument("--provider", "-p", help="Override LLM provider")
    run_parser.add_argument("--model", "-m", help="Override model")
    run_parser.add_argument("--theme", "-t", default="catppuccin-mocha", help="UI theme")
    run_parser.set_defaults(func=cmd_run)
    
    # init command
    init_parser = subparsers.add_parser("init", help="Create a new agent app")
    init_parser.add_argument("name", help="Application name")
    init_parser.add_argument("--path", help="Target directory (default: ./<name>)")
    init_parser.set_defaults(func=cmd_init)
    
    # quick command
    quick_parser = subparsers.add_parser("quick", help="Quick one-shot interaction")
    quick_parser.add_argument("prompt", nargs="*", help="Prompt to send")
    quick_parser.add_argument("--provider", "-p", default="claude", help="LLM provider")
    quick_parser.add_argument("--model", "-m", help="Model name")
    quick_parser.set_defaults(func=cmd_quick)
    
    # themes command
    themes_parser = subparsers.add_parser("themes", help="List available themes")
    themes_parser.set_defaults(func=cmd_themes)
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == "__main__":
    main()
