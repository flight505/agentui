"""Tests for skills system."""

import pytest
from pathlib import Path

from agentui.exceptions import SkillLoadError
from agentui.skills import Skill, load_skill


def test_skill_without_handler_raises_error(tmp_path):
    """Test that loading skill without handler implementation fails."""
    # Create incomplete skill (YAML only, no skill.py)
    skill_dir = tmp_path / "incomplete_skill"
    skill_dir.mkdir()

    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: incomplete
tools:
  - name: test_tool
    description: Test tool
    parameters: {}
"""
    )

    with pytest.raises(SkillLoadError, match="has no skill.py"):
        load_skill(skill_dir)


def test_skill_with_missing_function_raises_error(tmp_path):
    """Test that skill with skill.py but missing function fails."""
    skill_dir = tmp_path / "missing_function"
    skill_dir.mkdir()

    # Create YAML
    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: missing_function
tools:
  - name: test_tool
    description: Test
    parameters: {}
"""
    )

    # Create implementation but with wrong function name
    skill_py = skill_dir / "skill.py"
    skill_py.write_text(
        """
def wrong_name():
    return "wrong"
"""
    )

    with pytest.raises(SkillLoadError, match="function not found"):
        load_skill(skill_dir)


def test_skill_with_non_callable_raises_error(tmp_path):
    """Test that skill with non-callable handler fails."""
    skill_dir = tmp_path / "non_callable"
    skill_dir.mkdir()

    # Create YAML
    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: non_callable
tools:
  - name: test_tool
    description: Test
    parameters: {}
"""
    )

    # Create implementation with non-callable
    skill_py = skill_dir / "skill.py"
    skill_py.write_text(
        """
test_tool = "not a function"
"""
    )

    with pytest.raises(SkillLoadError, match="not callable"):
        load_skill(skill_dir)


def test_skill_with_handler_loads_successfully(tmp_path):
    """Test that skill with proper implementation loads."""
    skill_dir = tmp_path / "complete_skill"
    skill_dir.mkdir()

    # Create YAML
    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: complete
tools:
  - name: test_tool
    description: Test tool
    parameters: {}
"""
    )

    # Create implementation
    skill_py = skill_dir / "skill.py"
    skill_py.write_text(
        """
def test_tool():
    return "real implementation"
"""
    )

    skill = load_skill(skill_dir)

    assert skill.name == "complete_skill"
    assert len(skill.tools) == 1
    assert skill.tools[0].name == "test_tool"

    # Verify it's a real handler, not placeholder
    result = skill.tools[0].handler()
    assert result == "real implementation"


def test_skill_with_multiple_tools(tmp_path):
    """Test that skill with multiple tools loads correctly."""
    skill_dir = tmp_path / "multi_tool"
    skill_dir.mkdir()

    # Create YAML with multiple tools
    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: multi
tools:
  - name: tool_one
    description: First tool
    parameters: {}
  - name: tool_two
    description: Second tool
    parameters: {}
"""
    )

    # Create implementation with both functions
    skill_py = skill_dir / "skill.py"
    skill_py.write_text(
        """
def tool_one():
    return "one"

def tool_two():
    return "two"
"""
    )

    skill = load_skill(skill_dir)

    assert len(skill.tools) == 2
    assert skill.tools[0].name == "tool_one"
    assert skill.tools[1].name == "tool_two"

    # Verify both handlers work
    assert skill.tools[0].handler() == "one"
    assert skill.tools[1].handler() == "two"


def test_skill_with_parameters(tmp_path):
    """Test that skill handlers can accept parameters."""
    skill_dir = tmp_path / "with_params"
    skill_dir.mkdir()

    # Create YAML
    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: with_params
tools:
  - name: greet
    description: Greet someone
    parameters:
      type: object
      properties:
        name:
          type: string
"""
    )

    # Create implementation
    skill_py = skill_dir / "skill.py"
    skill_py.write_text(
        """
def greet(name: str) -> str:
    return f"Hello, {name}!"
"""
    )

    skill = load_skill(skill_dir)

    # Verify handler works with parameters
    result = skill.tools[0].handler(name="World")
    assert result == "Hello, World!"


def test_skill_with_skill_md(tmp_path):
    """Test that skill loads SKILL.md instructions."""
    skill_dir = tmp_path / "with_instructions"
    skill_dir.mkdir()

    # Create SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("# Test Skill\n\nThese are instructions for the LLM.")

    # Create minimal YAML
    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: with_instructions
tools:
  - name: test_tool
    description: Test
    parameters: {}
"""
    )

    # Create implementation
    skill_py = skill_dir / "skill.py"
    skill_py.write_text(
        """
def test_tool():
    return "test"
"""
    )

    skill = load_skill(skill_dir)

    assert skill.instructions == "# Test Skill\n\nThese are instructions for the LLM."
    assert "Test Skill" in skill.get_system_prompt_section()


def test_skill_without_yaml_loads_with_no_tools(tmp_path):
    """Test that skill without YAML loads but has no tools."""
    skill_dir = tmp_path / "no_yaml"
    skill_dir.mkdir()

    # Create only SKILL.md
    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text("# Minimal Skill")

    skill = Skill.load(skill_dir)

    assert skill.name == "no_yaml"
    assert skill.instructions == "# Minimal Skill"
    assert len(skill.tools) == 0


def test_weather_skill_example_loads():
    """Test that the weather example skill loads correctly."""
    # This tests the actual weather skill in examples/
    weather_path = Path(__file__).parent.parent / "examples" / "skills" / "weather"

    if not weather_path.exists():
        pytest.skip("Weather skill example not found")

    skill = Skill.load(weather_path)

    assert skill.name == "weather"
    assert len(skill.tools) == 2

    # Verify tools are defined
    tool_names = {tool.name for tool in skill.tools}
    assert "get_weather" in tool_names
    assert "get_forecast" in tool_names

    # Verify handlers work (they return demo data)
    import asyncio
    for tool in skill.tools:
        if tool.name == "get_weather":
            result = tool.handler(city="Copenhagen")
            # Handler is sync, not async
            assert not asyncio.iscoroutinefunction(tool.handler)
            assert isinstance(result, dict)
            assert "city" in result
            assert result["city"] == "Copenhagen"
            assert "temperature" in result

        elif tool.name == "get_forecast":
            result = tool.handler(city="New York", days=3)
            # Handler is sync, not async
            assert not asyncio.iscoroutinefunction(tool.handler)
            assert isinstance(result, dict)
            assert "city" in result
            assert result["city"] == "New York"
            assert "forecast" in result
            assert len(result["forecast"]) == 3


def test_skill_error_message_includes_helpful_info(tmp_path):
    """Test that error messages are clear and actionable."""
    skill_dir = tmp_path / "helpful_errors"
    skill_dir.mkdir()

    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: helpful
tools:
  - name: my_tool
    description: Test
    parameters: {}
"""
    )

    # Test without skill.py
    with pytest.raises(SkillLoadError) as exc_info:
        load_skill(skill_dir)

    error_msg = str(exc_info.value)
    assert "my_tool" in error_msg
    assert "skill.py" in error_msg
    assert "helpful_errors" in error_msg


def test_skill_load_from_string_path(tmp_path):
    """Test that skills can be loaded from string paths."""
    skill_dir = tmp_path / "string_path"
    skill_dir.mkdir()

    skill_yaml = skill_dir / "skill.yaml"
    skill_yaml.write_text(
        """
name: string_path
tools:
  - name: test_tool
    description: Test
    parameters: {}
"""
    )

    skill_py = skill_dir / "skill.py"
    skill_py.write_text(
        """
def test_tool():
    return "works"
"""
    )

    # Load using string path instead of Path object
    skill = load_skill(str(skill_dir))

    assert skill.name == "string_path"
    assert len(skill.tools) == 1
