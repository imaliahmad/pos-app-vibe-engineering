from app.repositories.report_repository import list_category_sales, list_item_sales
from app.repositories.sale_repository import get_sale, list_sale_lines, list_sales_since

# How many days before today each period reaches back; today counts as one day.
PERIOD_DAYS = {"today": 0, "7d": 6, "30d": 29}

INVALID_PERIOD = "Unknown period"
ORDER_NOT_FOUND = "Order not found"


def get_category_report() -> list[dict]:
    return list_category_sales()


def get_item_report() -> list[dict]:
    return list_item_sales()


def get_orders(period: str) -> tuple[list[dict] | None, str | None]:
    if period not in PERIOD_DAYS:
        return None, INVALID_PERIOD
    return list_sales_since(PERIOD_DAYS[period]), None


def get_order(order_id: int) -> tuple[dict | None, str | None]:
    order = get_sale(order_id)
    if order is None:
        return None, ORDER_NOT_FOUND
    order["lines"] = list_sale_lines(order_id)
    return order, None
