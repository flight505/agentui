"""
Skills Loader - Load and manage agent skills.

Skills are directories containing:
- SKILL.md: Instructions for the LLM
- skill.yaml: Tool definitions and configuration
"""

from pathlib import Path
from typing import Any

import yaml

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
            raise ValueError(f"Skill path must be a directory: {path}")

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

            # Extract tool definitions
            for tool_def in config.get("tools", []):
                tools.append(ToolDefinition(
                    name=tool_def["name"],
                    description=tool_def.get("description", ""),
                    parameters=tool_def.get("parameters", {}),
                    handler=cls._create_placeholder_handler(tool_def["name"]),
                ))

        return cls(
            name=name,
            path=path,
            instructions=instructions,
            tools=tools,
            config=config,
        )

    @staticmethod
    def _create_placeholder_handler(tool_name: str):
        """Create a placeholder handler for YAML-defined tools."""
        def handler(**kwargs):
            return {
                "error": f"Tool '{tool_name}' is defined in YAML but has no Python handler. "
                         f"Override with @app.tool decorator or implement in skill.py"
            }
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
