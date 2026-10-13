from flask import Response, request, session

from app.responses import failure, success
from app.services.sale_service import create_sale

MAX_QUANTITY = 999
# SQLite stores integers in 64 bits; a larger id would crash the query.
MAX_ID = 2**63 - 1


def is_int(value: object) -> bool:
    # bool is a subclass of int in Python, so True would otherwise pass as 1.
    return isinstance(value, int) and not isinstance(value, bool)


def handle_create_sale() -> tuple[Response, int]:
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return failure("Invalid request", ["Body must be a JSON object"])

    raw_lines = body.get("lines")
    if not isinstance(raw_lines, list) or not raw_lines:
        return failure("Invalid request", ["The order needs at least one line"])

    errors = []
    lines = []
    for number, line in enumerate(raw_lines, start=1):
        if not isinstance(line, dict):
            errors.append(f"Line {number}: must be an object")
            continue
        item_id = line.get("item_id")
        quantity = line.get("quantity")
        if not is_int(item_id) or not 1 <= item_id <= MAX_ID:
            errors.append(f"Line {number}: item_id must be a positive whole number")
        if not is_int(quantity) or not 1 <= quantity <= MAX_QUANTITY:
            errors.append(
                f"Line {number}: quantity must be a whole number from 1 to {MAX_QUANTITY}"
            )
        # Only item_id and quantity are used; any price from the browser is ignored.
        lines.append({"item_id": item_id, "quantity": quantity})
    if errors:
        return failure("Invalid request", errors)

    sale, error = create_sale(session["user_id"], lines)
    if error:
        return failure(error)
    return success(sale, "Sale saved", 201)
