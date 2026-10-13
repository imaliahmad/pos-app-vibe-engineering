from app.db import get_db


def insert_item(category_id: int, name: str, price: int) -> int:
    """Insert an item and return its id. The caller commits."""
    cursor = get_db().execute(
        "INSERT INTO items (category_id, name, price) VALUES (?, ?, ?)",
        (category_id, name, price),
    )
    return cursor.lastrowid


def list_active_items_by_category(category_id: int) -> list[dict]:
    rows = get_db().execute(
        "SELECT id, name, price FROM items"
        " WHERE category_id = ? AND active = 1 ORDER BY name",
        (category_id,),
    )
    return [dict(row) for row in rows]
