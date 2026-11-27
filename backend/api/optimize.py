"""
RolePrompt AI: Optimization API route (Iteration 9).

Endpoint: POST /api/optimize

Resolves the provider and model, runs the agent, saves completed and
clarification results with the real provider and model, and maps errors to HTTP.
Failed requests are not saved.
"""

import logging
from typing import Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from agent import run_optimization
from agent.classifier import ClassificationError
from database import repository
from llm.base_provider import LLMProviderError
from llm.registry import get_provider

logger = logging.getLogger("roleprompt.optimize")

router = APIRouter(prefix="/api", tags=["Optimization"])

TargetModel = Literal["generic", "gemini", "openai", "claude"]
OptimizationLevel = Literal["light", "standard", "deep"]
OutputFormat = Literal["markdown", "bullets", "steps", "table", "json", "code", "report", "text"]


class OptimizeRequest(BaseModel):
    """Body of POST /api/optimize."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")

    role: str = Field(min_length=1, max_length=40)
    task: str = Field(min_length=1, max_length=40)
    original_prompt: str = Field(min_length=10, max_length=4000)
    context: str = Field(default="", max_length=1500)
    constraints: str = Field(default="", max_length=1000)
    output_format: OutputFormat
    target_model: TargetModel = "generic"
    optimization_level: OptimizationLevel = "standard"
    model: Optional[str] = Field(default=None, max_length=80)


class CriterionDetail(BaseModel):
    key: str
    label: str
    weight: int
    score: int
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)


class PromptVersion(BaseModel):
    version: int
    refinement_iteration: int
    prompt: str
    overall_score: int
    evaluation: Dict[str, int] = Field(default_factory=dict)
    note: str


class OptimizeResponse(BaseModel):
    session_id: Optional[str] = None
    original_prompt: str
    optimized_prompt: str
    status: Literal["success", "clarification_needed"]
    explanation: str
    assumptions: List[str] = Field(default_factory=list)
    clarification_questions: List[str] = Field(default_factory=list)
    provider: Optional[str] = None
    model: Optional[str] = None
    overall_score: Optional[int] = None
    evaluation: Dict[str, int] = Field(default_factory=dict)
    criteria_details: List[CriterionDetail] = Field(default_factory=list)
    quality_threshold: Optional[int] = None
    max_refinements: Optional[int] = None
    refinement_iterations: int = 0
    improvements: List[str] = Field(default_factory=list)
    remaining_weaknesses: List[str] = Field(default_factory=list)
    versions: List[PromptVersion] = Field(default_factory=list)


STATUS_BY_ERROR_CODE = {
    "invalid_request": 400,
    "not_configured": 503,
    "invalid_api_key": 502,
    "rate_limited": 429,
    "unavailable": 503,
    "invalid_response": 502,
}


@router.post("/optimize", response_model=OptimizeResponse)
def optimize_prompt(request: OptimizeRequest) -> OptimizeResponse:
    """Runs the agent with the chosen provider, then saves the result. Failures are not saved."""
    request_data = request.model_dump()

    try:
        provider = get_provider(request.target_model)
        model = provider.resolve_model(request.model)
        result = run_optimization(request_data, provider, model)
    except ClassificationError as error:
        raise HTTPException(status_code=400, detail={"code": error.code, "message": error.message}) from error
    except LLMProviderError as error:
        raise HTTPException(
            status_code=STATUS_BY_ERROR_CODE.get(error.code, 502),
            detail={"code": error.code, "message": error.message},
        ) from error

    result["provider"] = provider.id
    result["model"] = model

    try:
        session_id = repository.save_session(
            request_data, result, provider=provider.id, model=model
        )
        result["session_id"] = session_id
    except Exception:
        logger.exception("Could not save the optimization session.")

    return OptimizeResponse(**result)