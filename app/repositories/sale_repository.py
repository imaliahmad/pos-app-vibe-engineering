from app.db import get_db


def insert_sale(user_id: int, total: int, lines: list[dict]) -> dict:
    """Insert the sale and its lines and return {sale_id, total, created_at}.

    Each line: {item_id, item_name, unit_price, quantity, line_total}.
    Run it inside `transaction()` so the header and lines are saved together.
    """
    db = get_db()
    cursor = db.execute(
        "INSERT INTO sales (user_id, total) VALUES (?, ?)", (user_id, total)
    )
    sale_id = cursor.lastrowid
    for line in lines:
        db.execute(
            "INSERT INTO sale_items"
            " (sale_id, item_id, item_name, unit_price, quantity, line_total)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                sale_id,
                line["item_id"],
                line["item_name"],
                line["unit_price"],
                line["quantity"],
                line["line_total"],
            ),
        )
    row = db.execute(
        "SELECT id AS sale_id, total, created_at FROM sales WHERE id = ?", (sale_id,)
    ).fetchone()
    return dict(row)
