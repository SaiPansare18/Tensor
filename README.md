# RolePrompt AI

RolePrompt AI turns ordinary instructions into structured, role-aware professional prompts for Data Analysts and Software Developers. It evaluates each prompt against seven weighted criteria, refines it up to three times, and saves every session in a local database.

## Features

- Two professional roles with eight tasks each, validated by a role registry
- Clarification questions when essential information is missing, with answers resubmitted
- Seven-part prompt framework (Role, Objective, Context, Task Instructions, Constraints, Output Format, Validation)
- Weighted internal evaluation with a visible caveat that it is a heuristic
- Refinement up to three rounds, with early stop and discarding of revisions that do not help
- Saved history: reopen a session without calling the model, compare versions, delete sessions
- Provider choice: Google Gemini (tested), OpenAI and Anthropic Claude (implemented, untested)

## Technology stack

- Frontend: HTML5, CSS3, vanilla JavaScript
- Backend: Python 3.9, FastAPI, Uvicorn, Pydantic
- Storage: SQLite (built-in `sqlite3`)
- Providers: google-genai, openai, anthropic (official SDKs)
- Tests: pytest

## Quick start

See [docs/setup.md](docs/setup.md) for the full guide.

```bash
cd Tensor/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then add your key to .env
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/.

## Documentation

- [Setup and troubleshooting](docs/setup.md)
- [Architecture](docs/architecture.md)
- [API reference](docs/api.md)

## Tests

```bash
cd Tensor/backend
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest -v
```

The tests do not call any provider and need no keys.

## Important limits

- Scores are internal heuristics. They are not validated measures of prompt quality.
- The evaluator cannot detect constraints the model invents.
- OpenAI and Claude have not been tested with real keys.
- The application has no login. Run it on your own machine only.# Tensor
