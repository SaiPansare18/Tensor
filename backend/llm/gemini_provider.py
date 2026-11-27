"""
RolePrompt AI: Google Gemini provider (Iteration 9).
Tested in Iteration 8 with a real key and model.
"""

from google import genai
from google.genai import errors as genai_errors
from google.genai import types

from llm.base_provider import (
    LLMProvider,
    ProviderAuthenticationError,
    ProviderRateLimitError,
    ProviderResponseError,
    ProviderUnavailableError,
)


def _map_api_error(error, model):
    code = getattr(error, "code", None)
    google_message = str(error)[:300]
    if code in (401, 403):
        return ProviderAuthenticationError(
            f"Google rejected the Gemini API key. Check GEMINI_API_KEY in backend/.env. Google said: {google_message}"
        )
    if code == 429:
        return ProviderRateLimitError(f"Gemini rate limit reached. Wait a minute and try again. Google said: {google_message}")
    if code == 404:
        return ProviderUnavailableError(
            f"Gemini model '{model}' was not available. Check GEMINI_MODEL in backend/.env. Google said: {google_message}"
        )
    return ProviderUnavailableError(f"Gemini returned an error (HTTP {code}). Google said: {google_message}")


class GeminiProvider(LLMProvider):
    id = "gemini"
    display_name = "Google Gemini"
    api_key_env = "GEMINI_API_KEY"
    model_env = "GEMINI_MODEL"
    default_model = "gemini-3.5-flash-lite"
    supported_models = ("gemini-3.5-flash-lite", "gemini-2.5-flash")

    def _request_text(self, model, system_prompt, user_message, json_mode):
        client = genai.Client(api_key=self.api_key())

        config_args = {"system_instruction": system_prompt, "temperature": 0.4}
        if json_mode:
            config_args["response_mime_type"] = "application/json"

        try:
            response = client.models.generate_content(
                model=model,
                contents=user_message,
                config=types.GenerateContentConfig(**config_args),
            )
        except genai_errors.APIError as error:
            raise _map_api_error(error, model) from error
        except Exception as error:
            raise ProviderUnavailableError(
                f"Could not reach Gemini ({type(error).__name__}). Check your internet connection and try again."
            ) from error

        try:
            text = response.text or ""
        except Exception as error:
            raise ProviderResponseError("Gemini returned no usable answer. Try again.") from error

        if not text.strip():
            raise ProviderResponseError("Gemini returned an empty answer. Try again.")
        return text