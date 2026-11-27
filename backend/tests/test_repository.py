"""Repository tests (Iteration 10). Uses a temporary database file."""

from database import repository
from database.connection import get_connection

REQUEST = {
    "original_prompt": "Clean my sales CSV and find regions with missing data",
    "role": "data-analyst",
    "task": "data-cleaning",
    "context": "",
    "constraints": "",
    "output_format": "markdown",
    "target_model": "generic",
    "optimization_level": "standard",
}

RESULT = {
    "status": "success",
    "optimized_prompt": "Prompt text",
    "explanation": "Explanation.",
    "assumptions": ["An assumption."],
    "clarification_questions": [],
    "overall_score": 88,
    "refinement_iterations": 1,
    "improvements": [],
    "remaining_weaknesses": [],
    "evaluation": {"clarity": 88},
    "criteria_details": [],
    "versions": [
        {"version": 1, "refinement_iteration": 0, "prompt": "First", "overall_score": 80, "evaluation": {}, "note": "Initial generation"},
        {"version": 2, "refinement_iteration": 1, "prompt": "Second", "overall_score": 88, "evaluation": {}, "note": "Refinement 1"},
    ],
}


def test_save_list_and_get(temp_database):
    session_id = repository.save_session(REQUEST, RESULT, provider="gemini", model="model-x")
    items, total = repository.list_sessions(1, 10)
    assert total == 1
    assert items[0]["id"] == session_id

    session = repository.get_session(session_id)
    assert session["assumptions"] == ["An assumption."]
    assert len(session["versions"]) == 2
    assert session["provider"] == "gemini"
    assert session["model"] == "model-x"


def test_delete_removes_versions_too(temp_database):
    session_id = repository.save_session(REQUEST, RESULT, provider="gemini", model="model-x")
    assert repository.delete_session(session_id) is True
    assert repository.get_session(session_id) is None

    connection = get_connection()
    try:
        remaining = connection.execute(
            "SELECT COUNT(*) FROM prompt_versions WHERE session_id = ?", (session_id,)
        ).fetchone()[0]
    finally:
        connection.close()
    assert remaining == 0


def test_delete_unknown_session_returns_false(temp_database):
    assert repository.delete_session("00000000-0000-4000-8000-000000000000") is False