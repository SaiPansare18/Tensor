"""
Database package for RolePrompt AI.
Connection setup lives in connection.py, table definitions in models.py,
and all SQL queries in repository.py. Routes never write SQL.
"""

from database.connection import get_connection
from database.models import SCHEMA_SQL


def init_database():
    """Creates the tables if they do not exist. Safe to call on every startup."""
    connection = get_connection()
    try:
        connection.executescript(SCHEMA_SQL)
        connection.commit()
    finally:
        connection.close()
        