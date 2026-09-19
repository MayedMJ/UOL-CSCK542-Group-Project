"""Open connections to the university database."""

from pathlib import Path
import sqlite3


DEFAULT_DB_PATH = Path(__file__).resolve().with_name("university.db")


def get_connection(db_path=DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Open a SQLite database with foreign-key enforcement enabled.

    The default is university.db beside this module. An explicit relative
    path is resolved from the current working directory. The caller is
    responsible for closing the returned connection.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
