"""
Skills Loader - Load and manage agent skills.

Skills are directories containing:
- SKILL.md: Instructions for the LLM
- skill.yaml: Tool definitions and configuration
"""

import importlib.util
from pathlib import Path
from typing import Any, Callable

import yaml

from agentui.exceptions import SkillLoadError
from agentui.types import ToolDefinition


class Skill:
    """A loaded skill with its configuration and tools."""

    def __init__(
        self,
        name: str,
        path: Path,
        instructions: str = "",
        tools: list[ToolDefinition] | None = None,
        config: dict[str, Any] | None = None,
    ):
        self.name = name
        self.path = path
        self.instructions = instructions
        self.tools = tools or []
        self.config = config or {}

    @classmethod
    def load(cls, path: str | Path) -> "Skill":
        """
        Load a skill from a directory.
        
        Args:
            path: Path to skill directory
        
        Returns:
            Loaded Skill instance
        """
        path = Path(path)

        if not path.is_dir():
            raise SkillLoadError(f"Skill path must be a directory: {path}")

        name = path.name
        instructions = ""
        config = {}
        tools = []

        # Load SKILL.md
        skill_md = path / "SKILL.md"
        if skill_md.exists():
            instructions = skill_md.read_text()

        # Load skill.yaml
        skill_yaml = path / "skill.yaml"
        if skill_yaml.exists():
            with open(skill_yaml) as f:
                config = yaml.safe_load(f) or {}

            # Extract tool definitions and validate they have handlers
            for tool_def in config.get("tools", []):
                handler = cls._validate_tool_has_handler(tool_def, path)

                tools.append(ToolDefinition(
                    name=tool_def["name"],
                    description=tool_def.get("description", ""),
                    parameters=tool_def.get("parameters", {}),
                    handler=handler,
                ))

        return cls(
            name=name,
            path=path,
            instructions=instructions,
            tools=tools,
            config=config,
        )

    @staticmethod
    def _validate_tool_has_handler(tool_def: dict[str, Any], skill_path: Path) -> Callable[..., Any]:
        """
        Validate that YAML-defined tools have corresponding Python handlers.

        Args:
            tool_def: Tool definition from YAML
            skill_path: Path to skill directory

        Returns:
            Handler function from skill.py

        Raises:
            ValueError: If skill.py missing or handler not found
        """
        tool_name = tool_def["name"]
        skill_py = skill_path / "skill.py"

        if not skill_py.exists():
            raise SkillLoadError(
                f"Skill '{skill_path.name}' defines tool '{tool_name}' in YAML "
                f"but has no skill.py with handler implementation. "
                f"Create {skill_py} with a function named '{tool_name}'"
            )

        # Import skill.py module
        spec = importlib.util.spec_from_file_location("skill", skill_py)
        if spec is None or spec.loader is None:
            raise SkillLoadError(f"Could not load {skill_py}")

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Verify handler function exists
        if not hasattr(module, tool_name):
            raise SkillLoadError(
                f"Tool '{tool_name}' defined in YAML but function not found in {skill_py}. "
                f"Add a function named '{tool_name}' to {skill_py}"
            )

        handler = getattr(module, tool_name)

        # Verify it's callable
        if not callable(handler):
            raise SkillLoadError(
                f"Tool '{tool_name}' in {skill_py} is not callable. "
                f"It must be a function."
            )

        return handler

    def get_system_prompt_section(self) -> str:
        """Get the system prompt section for this skill."""
        if not self.instructions:
            return ""

        return f"""
<skill name="{self.name}">
{self.instructions}
</skill>
"""


class SkillRegistry:
    """Registry for managing loaded skills."""

    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def load(self, path: str | Path) -> Skill:
        """Load a skill and add it to the registry."""
        skill = Skill.load(path)
        self._skills[skill.name] = skill
        return skill

    def load_all(self, paths: list[str | Path]) -> list[Skill]:
        """Load multiple skills."""
        return [self.load(p) for p in paths]

    def get(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self._skills.get(name)

    def all(self) -> list[Skill]:
        """Get all loaded skills."""
        return list(self._skills.values())

    def get_combined_instructions(self) -> str:
        """Get combined instructions from all skills."""
        sections = [skill.get_system_prompt_section() for skill in self._skills.values()]
        return "\n".join(s for s in sections if s)

    def get_all_tools(self) -> list[ToolDefinition]:
        """Get all tools from all skills."""
        tools = []
        for skill in self._skills.values():
            tools.extend(skill.tools)
        return tools


# Global registry
_registry = SkillRegistry()


def load_skill(path: str | Path) -> Skill:
    """Load a skill from a directory."""
    return _registry.load(path)


def load_skills(paths: list[str | Path]) -> list[Skill]:
    """Load multiple skills."""
    return _registry.load_all(paths)


def get_skill(name: str) -> Skill | None:
    """Get a loaded skill by name."""
    return _registry.get(name)


def get_all_skills() -> list[Skill]:
    """Get all loaded skills."""
    return _registry.all()


def get_skill_instructions() -> str:
    """Get combined instructions from all skills."""
    return _registry.get_combined_instructions()


def get_skill_tools() -> list[ToolDefinition]:
    """Get all tools from all skills."""
    return _registry.get_all_tools()
