"""
RolePrompt AI: Database schema (Iteration 8).

Table definitions in plain SQL. CREATE TABLE IF NOT EXISTS makes initialization
safe to run on every startup: existing data is never deleted.
"""

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS sessions (
    id TEXT PRIMARY KEY,
    original_prompt TEXT NOT NULL,
    role TEXT NOT NULL,
    task TEXT NOT NULL,
    context TEXT NOT NULL DEFAULT '',
    constraints TEXT NOT NULL DEFAULT '',
    output_format TEXT NOT NULL,
    target_model TEXT NOT NULL,
    optimization_level TEXT NOT NULL,
    provider TEXT NOT NULL DEFAULT 'gemini',
    model TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL,
    optimized_prompt TEXT NOT NULL DEFAULT '',
    explanation TEXT NOT NULL DEFAULT '',
    assumptions_json TEXT NOT NULL DEFAULT '[]',
    clarification_questions_json TEXT NOT NULL DEFAULT '[]',
    clarification_answers_json TEXT NOT NULL DEFAULT '[]',
    improvements_json TEXT NOT NULL DEFAULT '[]',
    remaining_weaknesses_json TEXT NOT NULL DEFAULT '[]',
    overall_score INTEGER,
    refinement_iterations INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prompt_versions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    refinement_iteration INTEGER NOT NULL,
    prompt TEXT NOT NULL,
    overall_score INTEGER NOT NULL,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS evaluations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
    overall_score INTEGER NOT NULL,
    criterion_scores_json TEXT NOT NULL,
    criteria_details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_versions_session ON prompt_versions(session_id);
CREATE INDEX IF NOT EXISTS idx_evaluations_session ON evaluations(session_id);
"""