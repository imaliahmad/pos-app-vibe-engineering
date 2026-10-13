from app.db import get_db


def insert_user(username: str, password_hash: str, role: str) -> int:
    """Insert a user and return its id. The caller commits."""
    cursor = get_db().execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, password_hash, role),
    )
    return cursor.lastrowid


def get_user_by_username(username: str) -> dict | None:
    row = (
        get_db()
        .execute(
            "SELECT id, username, password_hash, role, active FROM users WHERE username = ?",
            (username,),
        )
        .fetchone()
    )
    return dict(row) if row else None


def get_user_by_id(user_id: int) -> dict | None:
    row = (
        get_db()
        .execute(
            "SELECT id, username, password_hash, role, active FROM users WHERE id = ?",
            (user_id,),
        )
        .fetchone()
    )
    return dict(row) if row else None
