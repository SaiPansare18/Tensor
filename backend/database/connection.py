"""
RolePrompt AI: SQLite connection (Iteration 8).

Opens a connection per operation and closes it afterwards. Foreign keys are
switched on for every connection, because SQLite leaves them off by default
and cascade delete depends on them.
"""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent          # Tensor/backend
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "roleprompt.db"


def get_connection():
    """Returns a new connection with foreign keys enabled and rows as dict-like objects."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection