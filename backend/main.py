"""
RolePrompt AI: FastAPI application entry point (Iteration 9).

Loads backend/.env, creates the SQLite tables, registers routers, and serves
the frontend. Run from the backend folder with: uvicorn main:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
FRONTEND_DIR = PROJECT_ROOT / "frontend"

# Load secrets before the provider modules read their environment variables
load_dotenv(BASE_DIR / ".env")

from api.history import router as history_router  # noqa: E402
from api.models import router as models_router  # noqa: E402
from api.optimize import router as optimize_router  # noqa: E402
from database import init_database  # noqa: E402

APP_NAME = "RolePrompt AI"
APP_VERSION = "0.9.0"


@asynccontextmanager
async def lifespan(app):
    # Create tables on startup. Existing data is kept.
    init_database()
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="Multi-role prompt optimization agent for professional users.",
    lifespan=lifespan,
)

app.include_router(optimize_router)
app.include_router(history_router)
app.include_router(models_router)


@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}


@app.get("/", include_in_schema=False)
def serve_index():
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/frontend/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="frontend-css")
app.mount("/frontend/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="frontend-js")