from flask import Response

from app.responses import failure, success
from app.services.catalog_service import get_categories, get_category_items


def handle_list_categories() -> tuple[Response, int]:
    return success(get_categories())


def handle_list_category_items(category_id: int) -> tuple[Response, int]:
    items, error = get_category_items(category_id)
    if error:
        return failure(error, status_code=404)
    return success(items)
