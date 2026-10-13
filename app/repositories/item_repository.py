from app.db import get_db


def insert_item(category_id: int, name: str, price: int) -> int:
    """Insert an item and return its id. The caller commits."""
    cursor = get_db().execute(
        "INSERT INTO items (category_id, name, price) VALUES (?, ?, ?)",
        (category_id, name, price),
    )
    return cursor.lastrowid
