"""
RolePrompt AI: Models API (Iteration 9).

GET  /api/models                 list providers, their status and models
POST /api/models/connect         run one small test request for a provider

Responses never contain API keys. Only status, model names and messages are returned.
"""

from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from llm.base_provider import LLMProviderError
from llm.registry import PROVIDERS, list_providers

router = APIRouter(prefix="/api", tags=["Models"])


class ProviderInfo(BaseModel):
    id: str
    display_name: str
    status: str
    configured_model: str
    supported_models: List[str]
    last_check_message: Optional[str] = None


class ModelsResponse(BaseModel):
    default_provider: str
    providers: List[ProviderInfo]


class ConnectRequest(BaseModel):
    provider: str = Field(min_length=1, max_length=20)


class ConnectResponse(BaseModel):
    provider: str
    status: str
    message: str


def _info(provider):
    return ProviderInfo(
        id=provider.id,
        display_name=provider.display_name,
        status=provider.status(),
        configured_model=provider.configured_model(),
        supported_models=list(provider.supported_models),
        last_check_message=provider.last_check[1] if provider.last_check else None,
    )


@router.get("/models", response_model=ModelsResponse)
def get_models():
    from llm.registry import default_provider_id

    return ModelsResponse(
        default_provider=default_provider_id(),
        providers=[_info(provider) for provider in list_providers()],
    )


@router.post("/models/connect", response_model=ConnectResponse)
def connect_provider(request: ConnectRequest):
    provider = PROVIDERS.get(request.provider.lower())
    if provider is None:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_request", "message": f"Unknown provider '{request.provider}'."},
        )

    try:
        provider.check_connection()
    except LLMProviderError as error:
        # The provider records the failure; report it without any key material
        return ConnectResponse(provider=provider.id, status=provider.status(), message=error.message)

    return ConnectResponse(provider=provider.id, status=provider.status(), message="Connection test passed.")