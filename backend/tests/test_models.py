"""Models API tests (Iteration 10). Includes a check that keys never appear in responses."""

from llm.base_provider import ProviderAuthenticationError
from llm.registry import PROVIDERS

SECRET = "test-secret-value-123"


def test_models_endpoint_never_returns_the_key(client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", SECRET)
    response = client.get("/api/models")
    assert response.status_code == 200
    assert SECRET not in response.text
    gemini = next(p for p in response.json()["providers"] if p["id"] == "gemini")
    assert gemini["status"] == "configured"


def test_unconfigured_providers_report_not_configured(client):
    response = client.get("/api/models")
    statuses = {p["id"]: p["status"] for p in response.json()["providers"]}
    assert statuses["openai"] == "not_configured"
    assert statuses["claude"] == "not_configured"


def test_connect_without_key_reports_not_configured(client):
    response = client.post("/api/models/connect", json={"provider": "openai"})
    assert response.status_code == 200
    assert response.json()["status"] == "not_configured"


def test_connect_success_marks_connected(client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", SECRET)
    monkeypatch.setattr(PROVIDERS["gemini"], "_request_text", lambda *args, **kwargs: "OK")
    response = client.post("/api/models/connect", json={"provider": "gemini"})
    assert response.json()["status"] == "connected"


def test_connect_failure_marks_connection_failed(client, monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", SECRET)

    def rejected(*args, **kwargs):
        raise ProviderAuthenticationError("Rejected for test.")

    monkeypatch.setattr(PROVIDERS["gemini"], "_request_text", rejected)
    response = client.post("/api/models/connect", json={"provider": "gemini"})
    assert response.json()["status"] == "connection_failed"
    assert SECRET not in response.text