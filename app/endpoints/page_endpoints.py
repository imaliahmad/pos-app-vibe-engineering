from pathlib import Path

from flask import Blueprint, Response, redirect, send_from_directory, session

bp = Blueprint("pages", __name__)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


# Each role has one home page: admins see reports, cashiers use the POS.
HOME_PAGES = {"admin": "/admin", "cashier": "/pos"}


def home_page() -> str:
    # An unknown role goes to the login page, which then shows the form (no redirect loop).
    return HOME_PAGES.get(session.get("role"), "/")


@bp.get("/")
def login_page() -> Response:
    if "user_id" in session and session.get("role") in HOME_PAGES:
        return redirect(home_page())
    return send_from_directory(FRONTEND_DIR, "login.html")


@bp.get("/pos")
def pos_page() -> Response:
    if "user_id" not in session:
        return redirect("/")
    if session.get("role") != "cashier":
        return redirect(home_page())
    return send_from_directory(FRONTEND_DIR, "pos.html")


@bp.get("/admin")
def admin_page() -> Response:
    if "user_id" not in session:
        return redirect("/")
    if session.get("role") != "admin":
        return redirect(home_page())
    return send_from_directory(FRONTEND_DIR, "admin.html")


@bp.get("/css/<path:filename>")
def css_file(filename: str) -> Response:
    return send_from_directory(FRONTEND_DIR / "css", filename)


@bp.get("/js/<path:filename>")
def js_file(filename: str) -> Response:
    return send_from_directory(FRONTEND_DIR / "js", filename)
