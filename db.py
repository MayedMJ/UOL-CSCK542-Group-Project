import sqlite3

def get_connection(db_path="university.db"):
    """
    Opens a SQLite connection with foreign keys enabled.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn
