"""API route tests (Iteration 10). The model is stubbed; no network calls are made."""

VALID_REQUEST = {
    "role": "data-analyst",
    "task": "data-cleaning",
    "original_prompt": "Clean my sales CSV and find regions with missing data",
    "output_format": "markdown",
}


def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_history_starts_empty(client):
    response = client.get("/api/history")
    assert response.status_code == 200
    assert response.json()["total"] == 0


def test_optimize_success_returns_saved_session(client, fake_gemini):
    response = client.post("/api/optimize", json=VALID_REQUEST)
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "success"
    assert body["provider"] == "gemini"
    assert body["model"] == "gemini-3.5-flash-lite"
    assert body["session_id"]
    assert body["overall_score"] is not None
    assert len(fake_gemini) >= 1


def test_clarification_makes_no_model_call(client, fake_gemini):
    request = {
        "role": "data-analyst",
        "task": "predictive-analytics",
        "original_prompt": "Predict which customers will leave next month.",
        "output_format": "table",
    }
    response = client.post("/api/optimize", json=request)
    body = response.json()
    assert body["status"] == "clarification_needed"
    assert body["clarification_questions"]
    assert fake_gemini == []


def test_unconfigured_provider_returns_503(client):
    response = client.post("/api/optimize", json={**VALID_REQUEST, "target_model": "openai"})
    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "not_configured"


def test_unknown_role_returns_400(client):
    response = client.post("/api/optimize", json={**VALID_REQUEST, "role": "chef"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "unknown_role"


def test_task_not_in_role_returns_400(client):
    response = client.post("/api/optimize", json={**VALID_REQUEST, "task": "debugging"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "task_not_in_role"


def test_invalid_output_format_returns_422(client):
    response = client.post("/api/optimize", json={**VALID_REQUEST, "output_format": "pdf"})
    assert response.status_code == 422


def test_unsupported_model_returns_400(client):
    response = client.post("/api/optimize", json={**VALID_REQUEST, "target_model": "gemini", "model": "gpt-9"})
    assert response.status_code == 400
    assert response.json()["detail"]["code"] == "invalid_request"


def test_session_lifecycle(client, fake_gemini):
    session_id = client.post("/api/optimize", json=VALID_REQUEST).json()["session_id"]

    opened = client.get(f"/api/sessions/{session_id}")
    assert opened.status_code == 200
    assert len(opened.json()["versions"]) >= 1

    deleted = client.delete(f"/api/sessions/{session_id}")
    assert deleted.status_code == 204

    assert client.get(f"/api/sessions/{session_id}").status_code == 404


def test_invalid_session_id_returns_400(client):
    assert client.get("/api/sessions/not-a-uuid").status_code == 400


def test_unknown_session_returns_404(client):
    assert client.get("/api/sessions/00000000-0000-4000-8000-000000000000").status_code == 404