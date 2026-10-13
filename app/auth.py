from collections.abc import Callable
from functools import wraps
from typing import Any

from flask import session

from app.responses import failure


def login_required(view: Callable[..., Any]) -> Callable[..., Any]:
    @wraps(view)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        if "user_id" not in session:
            return failure("Login required", status_code=401)
        return view(*args, **kwargs)

    return wrapped


def role_required(role: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Allow only users whose session role matches. Put it under `login_required`."""

    def decorator(view: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(view)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            if session.get("role") != role:
                return failure("Not allowed", status_code=403)
            return view(*args, **kwargs)

        return wrapped

    return decorator
