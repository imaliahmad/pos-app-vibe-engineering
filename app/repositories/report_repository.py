from app.db import get_db


def list_category_sales() -> list[dict]:
    """All-time quantity sold and revenue per category, including never-sold ones (0).

    Revenue sums the saved line totals, so it uses each sale's price at the time.
    """
    rows = get_db().execute(
        "SELECT c.id, c.name,"
        " COALESCE(SUM(si.quantity), 0) AS quantity,"
        " COALESCE(SUM(si.line_total), 0) AS revenue"
        " FROM categories c"
        " LEFT JOIN items i ON i.category_id = c.id"
        " LEFT JOIN sale_items si ON si.item_id = i.id"
        " GROUP BY c.id"
        " ORDER BY revenue DESC, c.name"
    )
    return [dict(row) for row in rows]


def list_item_sales() -> list[dict]:
    """All-time quantity sold and revenue per item with its category name."""
    rows = get_db().execute(
        "SELECT i.id, i.name, c.name AS category,"
        " COALESCE(SUM(si.quantity), 0) AS quantity,"
        " COALESCE(SUM(si.line_total), 0) AS revenue"
        " FROM items i"
        " JOIN categories c ON c.id = i.category_id"
        " LEFT JOIN sale_items si ON si.item_id = i.id"
        " GROUP BY i.id"
        " ORDER BY revenue DESC, i.name"
    )
    return [dict(row) for row in rows]
