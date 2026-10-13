from app.repositories.category_repository import (
    get_active_category,
    list_active_categories,
)
from app.repositories.item_repository import list_active_items_by_category

CATEGORY_NOT_FOUND = "Category not found"


def get_categories() -> list[dict]:
    return list_active_categories()


def get_category_items(category_id: int) -> tuple[list[dict] | None, str | None]:
    # Check the category first, so an unknown or inactive one is a 404, not an empty list.
    if get_active_category(category_id) is None:
        return None, CATEGORY_NOT_FOUND
    return list_active_items_by_category(category_id), None
