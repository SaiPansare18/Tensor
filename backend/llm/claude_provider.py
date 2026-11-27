"""
RolePrompt AI: Anthropic Claude provider (Iteration 9).
Status: implemented, NOT yet tested. The model names must be checked against
Anthropic's current model list before the first test.

Claude has no JSON mode, so the JSON requirement is stated in the prompt and
parsed by parse_json_object() in base_provider.py.
"""

import anthropic

from llm.base_provider import (
    LLMProvider,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderUnavailableError,
)

REQUEST_TIMEOUT_SECONDS = 60.0
MAX_OUTPUT_TOKENS_JSON = 4096
MAX_OUTPUT_TOKENS_PING = 16


class ClaudeProvider(LLMProvider):
    id = "claude"
    display_name = "Anthropic Claude"
    api_key_env = "ANTHROPIC_API_KEY"
    model_env = "CLAUDE_MODEL"
    default_model = "claude-sonnet-4-5"
    supported_models = ("claude-sonnet-4-5", "claude-haiku-4-5")

    def _request_text(self, model, system_prompt, user_message, json_mode):
        client = anthropic.Anthropic(api_key=self.api_key(), timeout=REQUEST_TIMEOUT_SECONDS, max_retries=1)
        max_tokens = MAX_OUTPUT_TOKENS_JSON if json_mode else MAX_OUTPUT_TOKENS_PING

        # Subclasses come first: APITimeoutError is a kind of APIConnectionError
        try:
            message = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.4,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}],
            )
        except anthropic.AuthenticationError as error:
            raise ProviderAuthenticationError("Anthropic rejected the API key. Check ANTHROPIC_API_KEY in backend/.env.") from error
        except anthropic.RateLimitError as error:
            raise ProviderRateLimitError("Claude rate limit reached. Wait and try again, or check your plan.") from error
        except anthropic.APITimeoutError as error:
            raise ProviderUnavailableError("The Claude request timed out. Try again.") from error
        except anthropic.APIConnectionError as error:
            raise ProviderUnavailableError("Could not connect to Anthropic. Check your internet connection.") from error
        except anthropic.APIStatusError as error:
            raise ProviderUnavailableError(f"Anthropic returned an error (HTTP {error.status_code}). Try again later.") from error

        text = "".join(block.text for block in message.content if getattr(block, "type", "") == "text")
        if not text.strip():
            raise ProviderResponseError("Claude returned an empty answer. Try again.")
            return text    