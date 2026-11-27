"""
RolePrompt AI: Repository (Iteration 8).

Every SQL statement for the application lives here. Values are always passed as
parameters (?), never joined into the SQL text, which prevents SQL injection.
Each function opens and closes its own connection.
"""

import json
import uuid
from datetime import datetime, timezone

from database.connection import get_connection


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _loads(text, default):
    try:
        return json.loads(text)
    except (TypeError, json.JSONDecodeError):
        return default


def save_session(request_data, result, provider, model):
    """
    Stores a completed or clarification result with its versions and evaluation.
    Returns the new session ID. Runs in one transaction, so a partial save is never kept.
    """
    session_id = str(uuid.uuid4())
    now = _now()
    status = result["status"]

    connection = get_connection()
    try:
        connection.execute(
            """
            INSERT INTO sessions (
                id, original_prompt, role, task, context, constraints, output_format,
                target_model, optimization_level, provider, model, status,
                optimized_prompt, explanation, assumptions_json,
                clarification_questions_json, clarification_answers_json,
                improvements_json, remaining_weaknesses_json, overall_score,
                refinement_iterations, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                request_data["original_prompt"],
                request_data["role"],
                request_data["task"],
                request_data.get("context", "") or "",
                request_data.get("constraints", "") or "",
                request_data["output_format"],
                request_data["target_model"],
                request_data["optimization_level"],
                provider,
                model,
                status,
                result.get("optimized_prompt", "") or "",
                result.get("explanation", "") or "",
                json.dumps(result.get("assumptions", [])),
                json.dumps(result.get("clarification_questions", [])),
                json.dumps(request_data.get("clarification_answers", [])),
                json.dumps(result.get("improvements", [])),
                json.dumps(result.get("remaining_weaknesses", [])),
                result.get("overall_score"),
                result.get("refinement_iterations", 0),
                now,
                now,
            ),
        )

        for version in result.get("versions", []):
            connection.execute(
                """
                INSERT INTO prompt_versions (
                    session_id, version_number, refinement_iteration, prompt,
                    overall_score, note, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    version["version"],
                    version["refinement_iteration"],
                    version["prompt"],
                    version["overall_score"],
                    version["note"],
                    now,
                ),
            )

        if result.get("overall_score") is not None:
            connection.execute(
                """
                INSERT INTO evaluations (
                    session_id, overall_score, criterion_scores_json,
                    criteria_details_json, created_at
                ) VALUES (?, ?, ?, ?, ?)
                """,
                (
                    session_id,
                    result["overall_score"],
                    json.dumps(result.get("evaluation", {})),
                    json.dumps(result.get("criteria_details", [])),
                    now,
                ),
            )

        connection.commit()
        return session_id
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def list_sessions(page, page_size):
    """Returns one page of session summaries, newest first, and the total count."""
    offset = (page - 1) * page_size
    connection = get_connection()
    try:
        total = connection.execute("SELECT COUNT(*) FROM sessions").fetchone()[0]
        rows = connection.execute(
            """
            SELECT id, original_prompt, role, task, status, overall_score,
                   refinement_iterations, created_at
            FROM sessions
            ORDER BY created_at DESC, rowid DESC
            LIMIT ? OFFSET ?
            """,
            (page_size, offset),
        ).fetchall()
        items = [dict(row) for row in rows]
        return items, total
    finally:
        connection.close()


def get_session(session_id):
    """Returns the full saved session with its versions and evaluation, or None if missing."""
    connection = get_connection()
    try:
        row = connection.execute("SELECT * FROM sessions WHERE id = ?", (session_id,)).fetchone()
        if row is None:
            return None

        versions = connection.execute(
            """
            SELECT version_number, refinement_iteration, prompt, overall_score, note
            FROM prompt_versions WHERE session_id = ? ORDER BY version_number
            """,
            (session_id,),
        ).fetchall()

        evaluation = connection.execute(
            "SELECT criterion_scores_json, criteria_details_json FROM evaluations WHERE session_id = ?",
            (session_id,),
        ).fetchone()

        data = dict(row)
        data["assumptions"] = _loads(data.pop("assumptions_json"), [])
        data["clarification_questions"] = _loads(data.pop("clarification_questions_json"), [])
        data["clarification_answers"] = _loads(data.pop("clarification_answers_json"), [])
        data["improvements"] = _loads(data.pop("improvements_json"), [])
        data["remaining_weaknesses"] = _loads(data.pop("remaining_weaknesses_json"), [])
        data["versions"] = [dict(v) for v in versions]
        data["evaluation"] = _loads(evaluation["criterion_scores_json"], {}) if evaluation else {}
        data["criteria_details"] = _loads(evaluation["criteria_details_json"], []) if evaluation else []
        return data
    finally:
        connection.close()


def delete_session(session_id):
    """Deletes a session and, through cascade, its versions and evaluation. Returns True if one was removed."""
    connection = get_connection()
    try:
        cursor = connection.execute("DELETE FROM sessions WHERE id = ?", (session_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()