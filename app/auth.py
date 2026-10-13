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
