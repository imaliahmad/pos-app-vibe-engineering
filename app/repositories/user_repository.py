from app.db import get_db


def insert_user(username: str, password_hash: str, role: str) -> int:
    """Insert a user and return its id. The caller commits."""
    cursor = get_db().execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role),
    )
    return cursor.lastrowid
