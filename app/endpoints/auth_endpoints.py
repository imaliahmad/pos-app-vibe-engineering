from flask import Blueprint, Response

from app.auth import login_required
from app.handlers.auth_handler import handle_login, handle_logout, handle_me

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login() -> tuple[Response, int]:
    return handle_login()


@bp.post("/logout")
@login_required
def logout() -> tuple[Response, int]:
    return handle_logout()


@bp.get("/me")
@login_required
def me() -> tuple[Response, int]:
    return handle_me()
