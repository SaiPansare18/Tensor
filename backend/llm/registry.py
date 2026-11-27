"""
RolePrompt AI: Provider registry (Iteration 9).

The only module that knows which providers exist. Routes and the agent ask it
for a provider by id. Adding a provider means one module plus one line here.
"""

import os

from llm.base_provider import ProviderRequestError
from llm.claude_provider import ClaudeProvider
from llm.gemini_provider import GeminiProvider
from llm.openai_provider import OpenAIProvider

PROVIDERS = {provider.id: provider for provider in (GeminiProvider(), OpenAIProvider(), ClaudeProvider())}

GENERIC_CHOICE = "generic"


def default_provider_id():
    return os.getenv("DEFAULT_PROVIDER", "").strip().lower() or "gemini"


def get_provider(choice):
    """Returns the provider for a form choice. 'generic' means the default provider."""
    resolved = default_provider_id() if choice == GENERIC_CHOICE else choice
    provider = PROVIDERS.get(resolved)
    if provider is None:
        raise ProviderRequestError(f"Unknown provider '{resolved}'. Choose one of: {', '.join(PROVIDERS)}.")
    return provider


def list_providers():
    return list(PROVIDERS.values())