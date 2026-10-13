import logging

from werkzeug.security import check_password_hash

from app.repositories.user_repository import get_user_by_id, get_user_by_username

logger = logging.getLogger(__name__)

INVALID_LOGIN = "Invalid username or password"


def to_public_user(user: dict) -> dict:
    """Only the fields the browser may see. Never the password hash."""
    return {"id": user["id"], "username": user["username"], "role": user["role"]}


def authenticate_user(username: str, password: str) -> tuple[dict | None, str | None]:
    user = get_user_by_username(username)
    # Same message for every failure, so callers cannot tell which part was wrong.
    if user is None or not user["active"]:
        logger.info("Failed login for %r", username)
        return None, INVALID_LOGIN
    if not check_password_hash(user["password_hash"], password):
        logger.info("Failed login for %r", username)
        return None, INVALID_LOGIN
    logger.info("User %r logged in", username)
    return to_public_user(user), None


def get_current_user(user_id: int) -> dict | None:
    user = get_user_by_id(user_id)
    if user is None or not user["active"]:
        return None
    return to_public_user(user)
