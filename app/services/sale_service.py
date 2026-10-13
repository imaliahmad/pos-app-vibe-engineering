from app.db import transaction
from app.repositories.item_repository import get_active_items
from app.repositories.sale_repository import insert_sale

DUPLICATE_ITEM = "Each item can appear only once"
ITEM_NOT_FOUND = "Item not found or inactive"


def create_sale(user_id: int, lines: list[dict]) -> tuple[dict | None, str | None]:
    """Price each line from the database and save the sale.

    `lines` is already validated: [{item_id: int, quantity: int 1-999}, ...].
    """
    item_ids = [line["item_id"] for line in lines]
    if len(set(item_ids)) != len(item_ids):
        return None, DUPLICATE_ITEM

    # Read prices and save in one transaction, so a price change can't slip in between.
    with transaction():
        items = get_active_items(item_ids)
        if len(items) != len(item_ids):
            return None, ITEM_NOT_FOUND

        sale_lines = []
        for line in lines:
            item = items[line["item_id"]]
            sale_lines.append(
                {
                    "item_id": item["id"],
                    "item_name": item["name"],
                    "unit_price": item["price"],
                    "quantity": line["quantity"],
                    "line_total": item["price"] * line["quantity"],
                }
            )

        total = sum(line["line_total"] for line in sale_lines)
        return insert_sale(user_id, total, sale_lines), None
