"""
RolePrompt AI: OpenAI provider (Iteration 9).
Status: implemented, NOT yet tested with a real key.
"""

from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    OpenAI,
    RateLimitError,
)

from llm.base_provider import (
    LLMProvider,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderUnavailableError,
)

REQUEST_TIMEOUT_SECONDS = 60.0


class OpenAIProvider(LLMProvider):
    id = "openai"
    display_name = "OpenAI"
    api_key_env = "OPENAI_API_KEY"
    model_env = "OPENAI_MODEL"
    default_model = "gpt-4o-mini"
    supported_models = ("gpt-4o-mini", "gpt-4o")

    def _request_text(self, model, system_prompt, user_message, json_mode):
        client = OpenAI(api_key=self.api_key(), timeout=REQUEST_TIMEOUT_SECONDS, max_retries=1)

        request_args = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": 0.4,
        }
        if json_mode:
            request_args["response_format"] = {"type": "json_object"}

        # Subclasses come first: APITimeoutError is a kind of APIConnectionError
        try:
            completion = client.chat.completions.create(**request_args)
        except AuthenticationError as error:
            raise ProviderAuthenticationError("OpenAI rejected the API key. Check OPENAI_API_KEY in backend/.env.") from error
        except RateLimitError as error:
            raise ProviderRateLimitError("OpenAI rate limit or quota reached. Wait and try again, or check billing.") from error
        except APITimeoutError as error:
            raise ProviderUnavailableError("The OpenAI request timed out. Try again.") from error
        except APIConnectionError as error:
            raise ProviderUnavailableError("Could not connect to OpenAI. Check your internet connection.") from error
        except APIStatusError as error:
            raise ProviderUnavailableError(f"OpenAI returned an error (HTTP {error.status_code}). Try again later.") from error

        if not completion.choices:
            raise ProviderResponseError("OpenAI returned no answer. Try again.")

        text = completion.choices[0].message.content or ""
        if not text.strip():
            raise ProviderResponseError("OpenAI returned an empty answer. Try again.")
        return text