"""
Setup Assistant - Helps users get AgentUI configured without requiring API access.

This is a fallback mode that activates when the main LLM provider can't load.
It helps users troubleshoot and fix their setup, then hands off to the full agent.
"""

import logging
import os
import subprocess
import sys
from collections.abc import AsyncIterator

logger = logging.getLogger(__name__)


class SetupAssistant:
    """
    A non-AI assistant that helps with AgentUI setup.

    This runs when the main provider (Claude/OpenAI) can't load,
    providing intelligent help without requiring API access.
    """

    def __init__(self, provider_error: str):
        self.provider_error = provider_error
        self.context = {}  # Track conversation context

    async def process_message(self, user_input: str) -> AsyncIterator[str]:
        """Process user input and provide setup guidance."""
        user_lower = user_input.lower().strip()

        # Analyze the error first if this is the first message
        error_analysis = self._analyze_provider_error()

        # Check if user is reporting they fixed it
        if any(phrase in user_lower for phrase in [
            "installed", "fixed", "done", "ready", "sync",
            "added", "set up", "configured"
        ]):
            yield await self._check_if_fixed()
            return

        # Check if user wants environment info
        if any(word in user_lower for word in ["check", "status", "environment", "show"]):
            yield await self._show_environment()
            return

        # Check if user wants help
        if any(word in user_lower for word in ["help", "how", "what", "guide"]):
            yield await self._show_help(error_analysis)
            return

        # Default: Provide contextual guidance based on the error
        yield await self._provide_guidance(error_analysis, user_input)

    def _analyze_provider_error(self) -> dict:
        """Analyze the provider error and determine what's wrong."""
        error_lower = self.provider_error.lower()

        analysis = {
            "error_type": "unknown",
            "package_missing": None,
            "fix_command": None,
            "explanation": None,
        }

        if "anthropic" in error_lower and "not installed" in error_lower:
            analysis.update({
                "error_type": "missing_package",
                "package_missing": "anthropic",
                "fix_command": "uv sync --extra claude",
                "alternative": "uv sync --extra all",
                "explanation": """
The 'anthropic' package is an optional dependency. When you ran 'uv sync',
it only installed core dependencies (pyyaml, rich).

For Claude support, you need to install the 'claude' extra group:
  uv sync --extra claude

Or install all providers at once:
  uv sync --extra all
""".strip()
            })

        elif "openai" in error_lower and "not installed" in error_lower:
            analysis.update({
                "error_type": "missing_package",
                "package_missing": "openai",
                "fix_command": "uv sync --extra openai",
                "alternative": "uv sync --extra all",
                "explanation": """
The 'openai' package is an optional dependency. You need to install it separately:
  uv sync --extra openai
""".strip()
            })

        elif "api key" in error_lower:
            analysis.update({
                "error_type": "missing_api_key",
                "fix_command": "export ANTHROPIC_API_KEY='your-key-here'",
                "explanation": """
The ANTHROPIC_API_KEY environment variable is not set.

Get your API key from: https://console.anthropic.com/settings/keys
Then set it:
  export ANTHROPIC_API_KEY='sk-ant-...'
""".strip()
            })

        return analysis

    async def _show_environment(self) -> str:
        """Check and show the current environment status."""
        checks = []

        # Check packages
        checks.append("📦 **Package Status:**\n")
        for pkg in ["anthropic", "openai", "rich", "pyyaml"]:
            try:
                __import__(pkg)
                checks.append(f"  ✅ {pkg} - installed")
            except ImportError:
                checks.append(f"  ❌ {pkg} - not installed")

        # Check API keys
        checks.append("\n\n🔑 **API Keys:**\n")
        for key_name in ["ANTHROPIC_API_KEY", "OPENAI_API_KEY"]:
            value = os.environ.get(key_name)
            if value:
                masked = f"{value[:7]}...{value[-4:]}" if len(value) > 15 else "***"
                checks.append(f"  ✅ {key_name} - set ({masked})")
            else:
                checks.append(f"  ❌ {key_name} - not set")

        # Check Python version
        checks.append(f"\n\n🐍 **Python:** {sys.version.split()[0]}")

        # Check uv
        try:
            result = subprocess.run(
                ["uv", "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                checks.append(f"📦 **uv:** {result.stdout.strip()}")
            else:
                checks.append("📦 **uv:** not found")
        except Exception as e:
            logger.debug(f"Failed to check uv version: {e}")
            checks.append("📦 **uv:** not found")

        return "\n".join(checks)

    async def _show_help(self, error_analysis: dict) -> str:
        """Show setup help based on the error."""
        if error_analysis["error_type"] == "missing_package":
            return f"""
## How to Fix This

{error_analysis["explanation"]}

**Quick Fix:**
```bash
{error_analysis["fix_command"]}
```

**Then restart this example.**

**Alternative** (install all providers):
```bash
{error_analysis.get("alternative", "uv sync --extra all")}
```

Once you've run the command, type 'done' or 'fixed' and I'll check if it worked.
""".strip()

        elif error_analysis["error_type"] == "missing_api_key":
            return f"""
## How to Fix This

{error_analysis["explanation"]}

**To make it permanent** (add to ~/.zshrc or ~/.bashrc):
```bash
echo 'export ANTHROPIC_API_KEY="sk-ant-..."' >> ~/.zshrc
source ~/.zshrc
```

Once set, type 'done' and I'll verify.
""".strip()

        else:
            return """
## General Setup Guide

1. **Install dependencies:**
   ```bash
   uv sync --extra all
   ```

2. **Set API key:**
   ```bash
   export ANTHROPIC_API_KEY="sk-ant-..."
   ```

3. **Restart this example**

For more help: https://github.com/flight505/agentui
""".strip()

    async def _check_if_fixed(self) -> str:
        """Check if the user fixed the issue."""
        error_analysis = self._analyze_provider_error()

        if error_analysis["error_type"] == "missing_package":
            pkg = error_analysis["package_missing"]
            try:
                __import__(pkg)
                return f"""
✅ Great! The '{pkg}' package is now installed!

**Please restart this example** to use the full AI agent with {pkg.title()} support.

Just run the same command again:
  uv run python {' '.join(sys.argv)}
""".strip()
            except ImportError:
                return f"""
❌ Hmm, the '{pkg}' package still isn't installed.

Did you run:
  {error_analysis["fix_command"]}

Make sure you're in the project directory and try again.
Type 'check' to see the current environment status.
""".strip()

        elif error_analysis["error_type"] == "missing_api_key":
            if os.environ.get("ANTHROPIC_API_KEY"):
                return """
✅ API key is now set!

**Please restart this example** to connect to Claude.
""".strip()
            else:
                return """
❌ I still don't see the ANTHROPIC_API_KEY environment variable.

Did you run:
  export ANTHROPIC_API_KEY='sk-ant-...'

Make sure to use your actual API key from:
https://console.anthropic.com/settings/keys
""".strip()

        return "Type 'check' to see what still needs to be fixed."

    async def _provide_guidance(self, error_analysis: dict, user_input: str) -> str:
        """Provide contextual guidance based on the error and user input."""
        # First time - explain the error
        if not self.context.get("explained"):
            self.context["explained"] = True

            return f"""
## 🔧 Setup Assistant

I can't start the full AI agent yet because:

**{self.provider_error}**

{error_analysis.get("explanation", "")}

**To fix this, run:**
```bash
{error_analysis.get("fix_command", "uv sync --extra all")}
```

Then type 'done' or 'fixed' and I'll check if it worked.

You can also:
- Type 'check' to see your environment status
- Type 'help' for detailed setup instructions
""".strip()

        # User is asking something - provide conversational help
        return f"""
I understand you're trying to get set up. Here's what I recommend:

**Next step:**
```bash
{error_analysis.get("fix_command", "uv sync --extra all")}
```

Once you've run that command, type 'done' and I'll verify it worked.

For more details, type 'help'.
""".strip()
