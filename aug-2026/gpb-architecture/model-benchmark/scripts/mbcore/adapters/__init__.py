"""Adapter registry.

Adapters are looked up by the `adapter` field in config/models.yaml. Adding a
provider means adding a module here and one entry per model in the registry.
See skills/adapter-authoring/SKILL.md.
"""

from .base import ModelAdapter, ProviderRequest, ProviderResponse, RunProfile  # noqa: F401
from .anthropic import AnthropicClaude4xAdapter, AnthropicClaude5Adapter
from .google import GoogleGemini3xAdapter
from .openai import OpenAIGpt56Adapter

_ADAPTERS = {
    "anthropic-claude5": AnthropicClaude5Adapter,
    "anthropic-claude4x": AnthropicClaude4xAdapter,
    "openai-gpt56": OpenAIGpt56Adapter,
    "google-gemini3x": GoogleGemini3xAdapter,
}


def get_adapter(adapter_id: str) -> ModelAdapter:
    if adapter_id not in _ADAPTERS:
        raise KeyError(
            f"unknown adapter '{adapter_id}'. Registered: {', '.join(sorted(_ADAPTERS))}. "
            f"To add one, see skills/adapter-authoring/SKILL.md."
        )
    return _ADAPTERS[adapter_id]()


def adapter_ids() -> list[str]:
    return sorted(_ADAPTERS)
