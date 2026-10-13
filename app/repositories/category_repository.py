from app.db import get_db


def insert_category(name: str) -> int:
    """Insert a category and return its id. The caller commits."""
    cursor = get_db().execute("INSERT INTO categories (name) VALUES (?)", (name,))
    return cursor.lastrowid


def count_categories() -> int:
    return get_db().execute("SELECT COUNT(*) FROM categories").fetchone()[0]


def list_active_categories() -> list[dict]:
    rows = get_db().execute(
        "SELECT id, name FROM categories WHERE active = 1 ORDER BY name"
    )
    return [dict(row) for row in rows]


def get_active_category(category_id: int) -> dict | None:
    row = (
        get_db()
        .execute(
            "SELECT id, name FROM categories WHERE id = ? AND active = 1",
            (category_id,),
        )
        .fetchone()
    )
    return dict(row) if row else None
