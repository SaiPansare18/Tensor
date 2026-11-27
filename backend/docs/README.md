# RolePrompt AI

RolePrompt AI is a multi-role prompt optimization agent. It converts ordinary instructions into structured, role-aware professional prompts for Data Analysts and Software Developers.

## Current status

**Iteration 1: Project Initialization**

- FastAPI backend with a health-check endpoint
- Welcome page served by FastAPI
- No AI functionality yet

## Technology stack

- Frontend: HTML5, CSS3, vanilla JavaScript
- Backend: Python, FastAPI, Uvicorn
- Database: SQLite (planned for Iteration 8)
- AI provider: OpenAI (planned for Iteration 4)

## Running the application locally

From the project root:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then open:

- Welcome page: http://127.0.0.1:8000
- Health check: http://127.0.0.1:8000/api/health
- Interactive API docs: http://127.0.0.1:8000/docs