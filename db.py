import sqlite3
from pathlib import Path


def get_connection(db_path=None):
    """
    Opens a SQLite connection with foreign keys enabled.
    """
    if db_path is None:
        db_path = Path(__file__).resolve().parent / "university.db"
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
