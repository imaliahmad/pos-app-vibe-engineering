from pathlib import Path

from flask import Blueprint, Response, redirect, send_from_directory, session

bp = Blueprint("pages", __name__)

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@bp.get("/")
def login_page() -> Response:
    if "user_id" in session:
        return redirect("/pos")
    return send_from_directory(FRONTEND_DIR, "login.html")


@bp.get("/pos")
def pos_page() -> Response:
    if "user_id" not in session:
        return redirect("/")
    return send_from_directory(FRONTEND_DIR, "pos.html")


@bp.get("/css/<path:filename>")
def css_file(filename: str) -> Response:
    return send_from_directory(FRONTEND_DIR / "css", filename)


@bp.get("/js/<path:filename>")
def js_file(filename: str) -> Response:
    return send_from_directory(FRONTEND_DIR / "js", filename)
