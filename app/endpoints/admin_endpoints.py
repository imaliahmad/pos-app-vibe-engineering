from flask import Blueprint, Response

from app.auth import login_required, role_required
from app.handlers.report_handler import (
    handle_category_report,
    handle_get_order,
    handle_item_report,
    handle_list_orders,
)

bp = Blueprint("admin", __name__, url_prefix="/api/admin")


@bp.get("/reports/categories")
@login_required
@role_required("admin")
def category_report() -> tuple[Response, int]:
    return handle_category_report()


@bp.get("/reports/items")
@login_required
@role_required("admin")
def item_report() -> tuple[Response, int]:
    return handle_item_report()


@bp.get("/orders")
@login_required
@role_required("admin")
def list_orders() -> tuple[Response, int]:
    return handle_list_orders()


@bp.get("/orders/<int:order_id>")
@login_required
@role_required("admin")
def get_order(order_id: int) -> tuple[Response, int]:
    return handle_get_order(order_id)
