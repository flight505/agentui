#!/usr/bin/env python3
"""
Quick Test Script - Verify Python components work correctly.

This runs without the Go TUI to test the Python-side implementation.

Run:
    python examples/quick_test.py
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def test_protocol():
    """Test protocol module."""
    print("Testing protocol module...")
    
    from agentui.protocol import (
        Message, MessageType, create_message, create_request,
        text_payload, form_payload, form_field, table_payload
    )
    
    # Test message creation
    msg = create_message(MessageType.TEXT, text_payload("Hello"))
    assert msg.type == "text"
    assert msg.payload["content"] == "Hello"
    print("  ✓ Message creation works")
    
    # Test request creation (with ID)
    req = create_request(MessageType.FORM, form_payload([
        form_field("name", "Name", "text"),
    ]))
    assert req.id is not None
    assert len(req.id) > 0
    print("  ✓ Request creation works")
    
    # Test serialization
    json_str = msg.to_json()
    assert "text" in json_str
    assert "Hello" in json_str
    print("  ✓ JSON serialization works")
    
    # Test deserialization
    parsed = Message.from_json(json_str)
    assert parsed.type == "text"
    print("  ✓ JSON deserialization works")
    
    print("  All protocol tests passed!\n")


async def test_primitives():
    """Test primitives module."""
    print("Testing primitives module...")
    
    from agentui.primitives import (
        UIForm, UIFormField, UITable, UICode, UIProgress, UIProgressStep,
        text_field, select_field, checkbox_field
    )
    
    # Test form field
    field = text_field("email", "Email", required=True)
    assert field.name == "email"
    assert field.required is True
    print("  ✓ Form field creation works")
    
    # Test form
    form = UIForm(
        title="Test Form",
        fields=[
            text_field("name", "Name"),
            select_field("type", "Type", ["A", "B", "C"]),
        ]
    )
    d = form.to_dict()
    assert d["title"] == "Test Form"
    assert len(d["fields"]) == 2
    print("  ✓ Form creation works")
    
    # Test table
    table = UITable(
        columns=["A", "B"],
        rows=[["1", "2"], ["3", "4"]],
        title="Test Table"
    )
    d = table.to_dict()
    assert len(d["rows"]) == 2
    print("  ✓ Table creation works")
    
    # Test code
    code = UICode(code="print('hello')", language="python")
    d = code.to_dict()
    assert d["language"] == "python"
    print("  ✓ Code block creation works")
    
    # Test progress
    progress = UIProgress(
        message="Loading...",
        percent=50,
        steps=[UIProgressStep("Step 1", "complete")]
    )
    d = progress.to_dict()
    assert d["percent"] == 50
    print("  ✓ Progress creation works")
    
    print("  All primitives tests passed!\n")


async def test_cli_bridge():
    """Test CLI bridge."""
    print("Testing CLI bridge...")
    
    from agentui.bridge import CLIBridge, TUIConfig
    
    config = TUIConfig(
        app_name="Test",
        tagline="Testing",
    )
    
    bridge = CLIBridge(config)
    
    # Test lifecycle
    await bridge.start()
    assert bridge.is_running
    print("  ✓ Bridge starts correctly")
    
    # Test sending (these just print to console)
    await bridge.send_text("Test message", done=True)
    print("  ✓ send_text works")
    
    await bridge.send_alert("Test alert", severity="info")
    print("  ✓ send_alert works")
    
    await bridge.send_progress("Testing...", percent=75)
    print("  ✓ send_progress works")
    
    await bridge.stop()
    assert not bridge.is_running
    print("  ✓ Bridge stops correctly")
    
    print("  All CLI bridge tests passed!\n")


async def test_types():
    """Test types module."""
    print("Testing types module...")
    
    from agentui.types import (
        AgentConfig, ToolDefinition, AppManifest, ProviderType
    )
    
    # Test AgentConfig
    config = AgentConfig(
        provider=ProviderType.CLAUDE,
        model="claude-sonnet-4-5-20250929",
        max_tokens=4096,
    )
    assert config.provider == ProviderType.CLAUDE
    print("  ✓ AgentConfig works")
    
    # Test ToolDefinition
    def dummy_handler(x: str) -> dict:
        return {"result": x}
    
    tool = ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters={"type": "object", "properties": {}},
        handler=dummy_handler,
    )
    schema = tool.to_schema()
    assert schema["name"] == "test_tool"
    print("  ✓ ToolDefinition works")
    
    # Test AppManifest
    manifest = AppManifest.from_dict({
        "name": "test-app",
        "version": "1.0.0",
        "providers": {"default": "claude"},
    })
    assert manifest.name == "test-app"
    print("  ✓ AppManifest works")
    
    print("  All types tests passed!\n")


async def test_skills():
    """Test skills loader."""
    print("Testing skills module...")
    
    from agentui.skills import Skill, SkillRegistry
    
    # Test skill loading from examples
    skill_path = Path(__file__).parent / "skills" / "weather"
    if skill_path.exists():
        skill = Skill.load(skill_path)
        assert skill.name == "weather"
        assert "weather" in skill.instructions.lower()
        print("  ✓ Skill loading works")
        
        # Test registry
        registry = SkillRegistry()
        registry.load(skill_path)
        assert registry.get("weather") is not None
        print("  ✓ Skill registry works")
    else:
        print("  ⚠ Skipping skill tests (example skill not found)")
    
    print("  Skills tests passed!\n")


async def main():
    """Run all tests."""
    print("=" * 50)
    print("AgentUI Quick Test")
    print("=" * 50)
    print()
    
    tests = [
        ("Protocol", test_protocol),
        ("Primitives", test_primitives),
        ("CLI Bridge", test_cli_bridge),
        ("Types", test_types),
        ("Skills", test_skills),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"  ✗ {name} test failed: {e}")
            failed += 1
            import traceback
            traceback.print_exc()
            print()
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 50)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
