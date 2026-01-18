"""
Generative UI v2.0 Demo - State-of-the-Art Component Selection

Demonstrates Phases 1 & 2:
1. LLM-aware component catalog (Phase 1) - LLM knows all display_* tools
2. Data-driven component selection (Phase 2) - Tools return plain data

Run: uv run python examples/generative_ui_v2_demo.py
"""

import asyncio
from agentui import AgentApp


# Create app
app = AgentApp(
    name="Generative UI v2.0",
    tagline="Data-driven UI - Tools return plain data, framework chooses components",
    provider="claude",
)


# ===== Phase 2 Demo: Tools return plain data =====

@app.tool(
    name="get_system_status",
    description="Get current system status with services and metrics",
    parameters={"type": "object", "properties": {}},
)
def get_system_status():
    """Returns plain list of dicts → Auto-converts to UITable"""
    return [
        {"service": "API Server", "status": "✓", "cpu": "45%", "memory": "1.2GB"},
        {"service": "Database", "status": "✓", "cpu": "12%", "memory": "3.8GB"},
        {"service": "Cache", "status": "✗", "cpu": "0%", "memory": "0GB"},
    ]


@app.tool(
    name="get_config",
    description="Get application configuration",
    parameters={"type": "object", "properties": {}},
)
def get_config():
    """Returns dict with 4+ keys → Auto-converts to UICode (JSON)"""
    return {
        "environment": "production",
        "debug": False,
        "api_version": "v2.1.0",
        "features": {"auth": True, "caching": True},
        "database": {"host": "db.example.com", "port": 5432},
    }


@app.tool(
    name="generate_function",
    description="Generate a Python function",
    parameters={"type": "object", "properties": {}},
)
def generate_function():
    """Returns code string → Auto-converts to UICode with language detection"""
    return '''def process_items(data):
    """Filter and process items."""
    result = []
    for item in data:
        if item.get("active"):
            result.append(item)
    return result
'''


async def main():
    """Run the demo."""
    print("=" * 70)
    print("AgentUI Generative UI v2.0 Demo")
    print("=" * 70)
    print()
    print("This demo showcases Phase 1 & 2 of Generative UI:")
    print("  ✓ Tools return plain data (no UI coupling)")
    print("  ✓ Framework auto-selects optimal components")
    print("  ✓ LLM-aware component catalog")
    print()
    print("Try:")
    print("  → 'Show me the system status'")
    print("  → 'What's the current config?'")
    print("  → 'Generate a Python function'")
    print()

    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
