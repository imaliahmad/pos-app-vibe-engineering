from flask import Response, request

from app.handlers.sale_handler import MAX_ID
from app.responses import failure, success
from app.services.report_service import (
    ORDER_NOT_FOUND,
    PERIOD_DAYS,
    get_category_report,
    get_item_report,
    get_order,
    get_orders,
)


def handle_category_report() -> tuple[Response, int]:
    return success(get_category_report())


def handle_item_report() -> tuple[Response, int]:
    return success(get_item_report())


def handle_list_orders() -> tuple[Response, int]:
    period = request.args.get("period")
    if period not in PERIOD_DAYS:
        return failure(
            "Invalid request", [f"period must be one of: {', '.join(PERIOD_DAYS)}"]
        )
    orders, error = get_orders(period)
    if error:
        return failure(error)
    return success(orders)


def handle_get_order(order_id: int) -> tuple[Response, int]:
    # An id too big for SQLite cannot exist and would crash the query.
    if order_id > MAX_ID:
        return failure(ORDER_NOT_FOUND, status_code=404)
    order, error = get_order(order_id)
    if error:
        return failure(error, status_code=404)
    return success(order)
