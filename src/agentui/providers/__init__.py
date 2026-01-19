"""
LLM Providers for AgentUI.
"""

from agentui.exceptions import ProviderError
from agentui.providers.claude import ClaudeProvider
from agentui.providers.openai import OpenAIProvider

__all__ = [
    "ClaudeProvider",
    "OpenAIProvider",
]


def get_provider(name: str, **kwargs):
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

    return providers[name](**kwargs)
