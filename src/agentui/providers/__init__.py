"""
LLM Providers for AgentUI.
"""

from typing import Any

from agentui.exceptions import ProviderError
from agentui.providers.claude import ClaudeProvider
from agentui.providers.openai import OpenAIProvider

__all__ = [
    "ClaudeProvider",
    "OpenAIProvider",
]


def get_provider(name: str, **kwargs: Any) -> ClaudeProvider | OpenAIProvider:
    """
    Get a provider by name.

    Args:
        name: Provider name ("claude", "openai")
        **kwargs: Provider configuration

    Returns:
        Provider instance
    """
    providers = {
        "claude": ClaudeProvider,
        "openai": OpenAIProvider,
    }

    if name not in providers:
        raise ProviderError(
            f"Unknown provider: {name}. "
            f"Available: {', '.join(providers.keys())}"
        )

    from typing import cast
    provider_class = providers[name]
    return cast(ClaudeProvider | OpenAIProvider, provider_class(**kwargs))
