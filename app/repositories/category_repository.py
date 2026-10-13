from app.db import get_db


def insert_category(name: str) -> int:
    """Insert a category and return its id. The caller commits."""
    cursor = get_db().execute("INSERT INTO categories (name) VALUES (?)", (name,))
    return cursor.lastrowid


def count_categories() -> int:
    return get_db().execute("SELECT COUNT(*) FROM categories").fetchone()[0]
