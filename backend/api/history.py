"""
RolePrompt AI: History API (Iteration 8).

GET    /api/history?page=1&page_size=20   list sessions, newest first
GET    /api/sessions/{session_id}         one saved session, no model call
DELETE /api/sessions/{session_id}         delete a session and its versions

Session IDs are validated as UUIDs before any database query runs.
"""

import uuid
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from database import repository

router = APIRouter(prefix="/api", tags=["History"])


class SessionSummary(BaseModel):
    id: str
    original_prompt: str
    role: str
    task: str
    status: str
    overall_score: Optional[int] = None
    refinement_iterations: int
    created_at: str


class HistoryPage(BaseModel):
    items: List[SessionSummary]
    total: int
    page: int
    page_size: int


def _validate_session_id(session_id):
    try:
        return str(uuid.UUID(session_id))
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail={"code": "invalid_session_id", "message": "The session ID is not valid."},
        )


@router.get("/history", response_model=HistoryPage)
def list_history(
    page: int = Query(1, ge=1, le=10000),
    page_size: int = Query(20, ge=1, le=100),
):
    items, total = repository.list_sessions(page, page_size)
    return HistoryPage(items=items, total=total, page=page, page_size=page_size)


@router.get("/sessions/{session_id}")
def get_session(session_id: str):
    valid_id = _validate_session_id(session_id)
    session = repository.get_session(valid_id)
    if session is None:
        raise HTTPException(
            status_code=404,
            detail={"code": "session_not_found", "message": "No saved session has this ID."},
        )
    return session


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(session_id: str):
    valid_id = _validate_session_id(session_id)
    if not repository.delete_session(valid_id):
        raise HTTPException(
            status_code=404,
            detail={"code": "session_not_found", "message": "No saved session has this ID."},
        )
    return None