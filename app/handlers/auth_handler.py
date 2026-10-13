from flask import Response, request, session

from app.responses import failure, success
from app.services.auth_service import authenticate_user, get_current_user


def handle_login() -> tuple[Response, int]:
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return failure("Invalid request", ["Body must be a JSON object"])

    username = body.get("username")
    password = body.get("password")
    errors = []
    if not isinstance(username, str) or not username.strip():
        errors.append("Username is required")
    if not isinstance(password, str) or not password:
        errors.append("Password is required")
    if errors:
        return failure("Invalid request", errors)

    user, error = authenticate_user(username.strip(), password)
    if error:
        return failure(error, status_code=401)

    # Fresh session on login, so nothing from before carries over.
    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]
    return success(user, "Logged in")


def handle_logout() -> tuple[Response, int]:
    session.clear()
    return success(None, "Logged out")


def handle_me() -> tuple[Response, int]:
    user = get_current_user(session["user_id"])
    if user is None:
        # User was deleted or deactivated after signing in.
        session.clear()
        return failure("Login required", status_code=401)
    return success(user)
