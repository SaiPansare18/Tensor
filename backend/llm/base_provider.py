"""
RolePrompt AI: Provider interface and shared errors (Iteration 9).

Every provider subclasses LLMProvider and implements _request_text(). The base
class handles configuration checks, model validation, JSON parsing and the
connection status. Keys are read from environment variables and are never
returned, logged or included in error messages.
"""

import json
import os
import re
from abc import ABC, abstractmethod


class LLMProviderError(Exception):
    """Base class for provider failures. 'code' maps to an HTTP status in the route."""

    code = "provider_error"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ProviderConfigurationError(LLMProviderError):
    code = "not_configured"


class ProviderRequestError(LLMProviderError):
    """The request asks for a provider or model this server does not offer."""

    code = "invalid_request"


class ProviderAuthenticationError(LLMProviderError):
    code = "invalid_api_key"


class ProviderRateLimitError(LLMProviderError):
    code = "rate_limited"


class ProviderUnavailableError(LLMProviderError):
    code = "unavailable"


class ProviderResponseError(LLMProviderError):
    code = "invalid_response"


_FENCE_PATTERN = re.compile(r"^```(?:json)?\s*|\s*```$", re.IGNORECASE)


def parse_json_object(text):
    """Parses a model answer as a JSON object, removing Markdown code fences first."""
    cleaned = _FENCE_PATTERN.sub("", (text or "").strip()).strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as error:
        raise ProviderResponseError("The model returned text that is not valid JSON. Try again.") from error
    if not isinstance(parsed, dict):
        raise ProviderResponseError("The model returned JSON, but not a JSON object. Try again.")
    return parsed


class LLMProvider(ABC):
    """Common interface. Subclasses set the class attributes and implement _request_text()."""

    id = ""
    display_name = ""
    api_key_env = ""
    model_env = ""
    default_model = ""
    supported_models = ()

    # Result of the last connection test: (ok, message), or None if never tested
    last_check = None

    def api_key(self):
        return os.getenv(self.api_key_env, "").strip()

    def is_configured(self):
        return bool(self.api_key())

    def configured_model(self):
        return os.getenv(self.model_env, "").strip() or self.default_model

    def resolve_model(self, requested):
        """Returns the model to use. A requested model must be in the supported list or be the configured one."""
        configured = self.configured_model()
        if not requested:
            return configured
        if requested == configured or requested in self.supported_models:
            return requested
        raise ProviderRequestError(
            f"Model '{requested}' is not supported by {self.display_name}. "
            f"Choose one of: {', '.join(self.supported_models)}."
        )

    def status(self):
        if not self.is_configured():
            return "not_configured"
        if self.last_check is None:
            return "configured"
        return "connected" if self.last_check[0] else "connection_failed"

    def generate_json(self, system_prompt, user_message, model):
        """Sends one request that must return a JSON object, and returns that object."""
        if not self.is_configured():
            raise ProviderConfigurationError(
                f"{self.display_name} is not configured. Add {self.api_key_env} to backend/.env, "
                "then restart the server."
            )
        text = self._request_text(model, system_prompt, user_message, json_mode=True)
        return parse_json_object(text)

    def check_connection(self):
        """Sends one tiny request to confirm the key and model work. Records the result."""
        if not self.is_configured():
            raise ProviderConfigurationError(
                f"{self.display_name} is not configured. Add {self.api_key_env} to backend/.env."
            )
        try:
            self._request_text(self.configured_model(), "Reply with the single word OK.", "Connection test.", json_mode=False)
        except LLMProviderError as error:
            self.last_check = (False, error.message)
            raise
        self.last_check = (True, "Connection test passed.")

    @abstractmethod
    def _request_text(self, model, system_prompt, user_message, json_mode):
        """Calls the SDK and returns the answer text. Subclasses map SDK errors to LLMProviderError."""