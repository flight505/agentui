"""
Test Phase 1: Component Catalog Integration

Verifies:
1. Component catalog is added to system prompt
2. Display_* tools are auto-registered
3. Tool schemas are correctly generated
"""

import pytest
from agentui.core import AgentCore
from agentui.types import AgentConfig
from agentui.component_catalog import ComponentCatalog


def test_catalog_in_system_prompt():
    """Test that component catalog is added to system prompt."""
    config = AgentConfig(system_prompt="You are a test agent.")
    core = AgentCore(config=config)

    # Verify original prompt is preserved
    assert "You are a test agent." in core.config.system_prompt

    # Verify catalog content is added
    assert "Available UI Components" in core.config.system_prompt
    assert "display_table" in core.config.system_prompt
    assert "display_form" in core.config.system_prompt
    assert "display_code" in core.config.system_prompt
    assert "display_progress" in core.config.system_prompt
    assert "display_confirm" in core.config.system_prompt
    assert "display_alert" in core.config.system_prompt
    assert "display_select" in core.config.system_prompt

    # Verify selection guidelines are included
    assert "Component Selection Guidelines" in core.config.system_prompt
    assert "When to use:" in core.config.system_prompt


def test_display_tools_registered():
    """Test that display_* tools are auto-registered."""
    core = AgentCore()

    # Verify all 7 display tools are registered
    expected_tools = [
        "display_table",
        "display_form",
        "display_code",
        "display_progress",
        "display_confirm",
        "display_alert",
        "display_select",
    ]

    for tool_name in expected_tools:
        assert tool_name in core.tools, f"Tool {tool_name} not registered"

        # Verify tool is marked as UI tool
        tool = core.tools[tool_name]
        assert tool.is_ui_tool is True, f"Tool {tool_name} not marked as UI tool"

        # Verify tool has description
        assert tool.description, f"Tool {tool_name} missing description"

        # Verify tool has parameters
        assert tool.parameters, f"Tool {tool_name} missing parameters"


def test_tool_schemas_generated():
    """Test that tool schemas are correctly generated for LLM."""
    core = AgentCore()
    schemas = core.get_tool_schemas()

    # Verify we have at least 7 schemas (the display_* tools)
    assert len(schemas) >= 7

    # Verify schema format
    schema_names = [s["name"] for s in schemas]
    assert "display_table" in schema_names
    assert "display_code" in schema_names

    # Verify schema structure (Anthropic/OpenAI format)
    for schema in schemas:
        if schema["name"].startswith("display_"):
            assert "name" in schema
            assert "description" in schema
            assert "input_schema" in schema
            assert "type" in schema["input_schema"]
            assert "properties" in schema["input_schema"]


def test_catalog_tool_schemas_match():
    """Test that catalog tool schemas match what's registered."""
    catalog_schemas = ComponentCatalog.get_tool_schemas()
    core = AgentCore()

    # Verify count matches
    assert len(catalog_schemas) == 7

    # Verify each catalog schema is registered
    for catalog_schema in catalog_schemas:
        tool_name = catalog_schema["name"]
        assert tool_name in core.tools

        # Verify description matches
        registered_tool = core.tools[tool_name]
        assert registered_tool.description == catalog_schema["description"]

        # Verify parameters match
        assert registered_tool.parameters == catalog_schema["input_schema"]


@pytest.mark.asyncio
async def test_display_handler_without_bridge():
    """Test display handlers work without bridge (return text)."""
    core = AgentCore(bridge=None)

    # Test display_table handler
    result = await core.tools["display_table"].handler(
        columns=["Name", "Age"],
        rows=[["Alice", "30"], ["Bob", "25"]],
    )

    # Without bridge, should return text description
    assert "[Would display display_table with:" in result
    assert "columns" in result
    assert "rows" in result


def test_phase1_success_criteria():
    """Verify all Phase 1 success criteria are met."""
    core = AgentCore()

    # ✅ Component catalog appears in system prompt
    assert "Available UI Components" in core.config.system_prompt

    # ✅ LLM can call display_* tools (verified by registration)
    assert "display_table" in core.tools
    assert "display_form" in core.tools
    assert "display_code" in core.tools
    assert "display_progress" in core.tools
    assert "display_confirm" in core.tools
    assert "display_alert" in core.tools
    assert "display_select" in core.tools

    # ✅ 7 display_* tools auto-registered (updated from 6 in plan)
    display_tools = [name for name in core.tools if name.startswith("display_")]
    assert len(display_tools) == 7

    # ✅ Tool schemas are correctly formatted for LLM
    schemas = core.get_tool_schemas()
    display_schemas = [s for s in schemas if s["name"].startswith("display_")]
    assert len(display_schemas) == 7

    print("✅ Phase 1 Success Criteria Met:")
    print(f"  - Component catalog in system prompt: {len(core.config.system_prompt)} chars")
    print(f"  - Display tools registered: {len(display_tools)}")
    print(f"  - Tool schemas generated: {len(display_schemas)}")
