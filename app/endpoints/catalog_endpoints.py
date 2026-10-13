from flask import Blueprint, Response

from app.auth import login_required
from app.handlers.catalog_handler import (
    handle_list_categories,
    handle_list_category_items,
)

bp = Blueprint("catalog", __name__, url_prefix="/api/categories")


@bp.get("")
@login_required
def list_categories() -> tuple[Response, int]:
    return handle_list_categories()


@bp.get("/<int:category_id>/items")
@login_required
def list_category_items(category_id: int) -> tuple[Response, int]:
    return handle_list_category_items(category_id)
