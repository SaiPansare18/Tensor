"""
Shared test fixtures (Iteration 10).

Tests never call a real provider. Keys are removed from the environment for
every test, a temporary database is used, and the LLM is replaced with a stub.
"""

import pytest
from fastapi.testclient import TestClient

import database.connection as connection_module
from database import init_database
from llm.registry import PROVIDERS

KEY_VARIABLES = ["GEMINI_API_KEY", "OPENAI_API_KEY", "ANTHROPIC_API_KEY", "DEFAULT_PROVIDER"]

VALID_PROMPT = (
    "### 1. Role\nYou are a senior data analyst.\n\n"
    "### 2. Objective\nPrepare the sales dataset by finding data cleaning issues.\n\n"
    "### 3. Context\nThe user provided a sales CSV with missing values.\n\n"
    "### 4. Task Instructions\n- Clean the data.\n- Find regions with missing data.\n\n"
    "### 5. Constraints\n- Do not lose information silently.\n\n"
    "### 6. Output Format\nStructured Markdown.\n\n"
    "### 7. Validation\n- Report how many rows were changed.\n- Verify column types.\n"
    "- Check the row count before conclusions.\n"
)


@pytest.fixture(autouse=True)
def clean_environment(monkeypatch):
    """Removes keys so no test depends on the developer's real backend/.env."""
    for name in KEY_VARIABLES:
        monkeypatch.delenv(name, raising=False)


@pytest.fixture(autouse=True)
def reset_connection_checks():
    """Connection results are stored on the shared provider objects, so reset them between tests."""
    for provider in PROVIDERS.values():
        provider.last_check = None
    yield
    for provider in PROVIDERS.values():
        provider.last_check = None


@pytest.fixture
def temp_database(tmp_path, monkeypatch):
    """Points the application at a temporary SQLite file."""
    monkeypatch.setattr(connection_module, "DATA_DIR", tmp_path)
    monkeypatch.setattr(connection_module, "DB_PATH", tmp_path / "test.db")
    init_database()
    return tmp_path / "test.db"


@pytest.fixture
def client(temp_database):
    from main import app

    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def fake_gemini(monkeypatch):
    """Replaces the Gemini model call. Returns the list of models that were requested."""
    from llm.registry import PROVIDERS as providers

    calls = []

    def fake_generate_json(system_prompt, user_message, model):
        calls.append(model)
        return {"optimized_prompt": VALID_PROMPT, "explanation": "Stub explanation.", "changes": []}

    monkeypatch.setattr(providers["gemini"], "generate_json", fake_generate_json)
    return calls
