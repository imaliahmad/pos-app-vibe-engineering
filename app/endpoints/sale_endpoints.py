from flask import Blueprint, Response

from app.auth import login_required
from app.handlers.sale_handler import handle_create_sale

bp = Blueprint("sales", __name__, url_prefix="/api/sales")


@bp.post("")
@login_required
def create_sale() -> tuple[Response, int]:
    return handle_create_sale()
