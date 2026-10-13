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


def list_sales_since(days_back: int) -> list[dict]:
    """Sales from `days_back` days before today up to now, newest first.

    Compares dates as stored (SQLite's clock, which also wrote created_at).
    """
    rows = get_db().execute(
        "SELECT s.id, s.created_at, u.username AS cashier, s.total"
        " FROM sales s JOIN users u ON u.id = s.user_id"
        " WHERE date(s.created_at) >= date('now', '-' || ? || ' days')"
        " ORDER BY s.created_at DESC, s.id DESC",
        (days_back,),
    )
    return [dict(row) for row in rows]


def get_sale(sale_id: int) -> dict | None:
    row = (
        get_db()
        .execute(
            "SELECT s.id, s.created_at, u.username AS cashier, s.total"
            " FROM sales s JOIN users u ON u.id = s.user_id WHERE s.id = ?",
            (sale_id,),
        )
        .fetchone()
    )
    return dict(row) if row else None


def list_sale_lines(sale_id: int) -> list[dict]:
    rows = get_db().execute(
        "SELECT item_name, quantity, unit_price, line_total FROM sale_items"
        " WHERE sale_id = ? ORDER BY id",
        (sale_id,),
    )
    return [dict(row) for row in rows]
