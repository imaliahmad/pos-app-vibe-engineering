# Catalog API
Status: planned
Plan item: 4

## Goal
A signed-in user can fetch the list of active categories, and the active items of one
category with their prices, so the POS screen (feature 5) can show them.

## Changes
- `app/repositories/category_repository.py`: add
  - `list_active_categories() -> list[dict]`: `SELECT id, name FROM categories WHERE active = 1 ORDER BY name`.
  - `get_active_category(category_id: int) -> dict | None`: `{id, name}` if it exists and `active = 1`.
- `app/repositories/item_repository.py`: add
  `list_active_items_by_category(category_id: int) -> list[dict]`:
  `SELECT id, name, price FROM items WHERE category_id = ? AND active = 1 ORDER BY name`.
- `app/services/catalog_service.py` (new):
  - `get_categories() -> list[dict]`.
  - `get_category_items(category_id: int) -> tuple[list[dict] | None, str | None]`: category missing or
    inactive → `(None, "Category not found")`; otherwise `(items, None)`. An active category with no
    active items returns `([], None)`.
- `app/handlers/catalog_handler.py` (new): `handle_list_categories()` and
  `handle_list_category_items(category_id: int)`; "Category not found" → `failure(..., status_code=404)`.
- `app/endpoints/catalog_endpoints.py` (new): blueprint `catalog`, prefix `/api/categories`, both `login_required`:
  - `GET /api/categories` → `[{id, name}]`
  - `GET /api/categories/<int:category_id>/items` → `[{id, name, price}]` (price is an integer, smallest unit)
- `app/__init__.py`: register the `catalog` blueprint.
- `tests/test_catalog.py` (new): the tests below.
- `docs/ARCHITECTURE.md`: no change expected (both endpoints are already listed).

## Test cases
- Signed in, `GET /api/categories` → 200, `data` is the 3 seeded categories as `{id, name}` only,
  sorted by name (`Bakery, Drinks, Snacks`).
- Signed in, `GET /api/categories/<Drinks id>/items` → 200, 4 items as `{id, name, price}`, sorted by name,
  Cola has `price == 150` (an int).
- Set one category `active = 0` → it is missing from `GET /api/categories`, and its items URL → 404, `status: false`.
  Set one item `active = 0` → it is missing from its category's item list.
- Unknown category id (e.g. `9999`) → 404, `status: false`, message "Category not found".
- Not signed in: both endpoints → 401.

## Out of scope
Any POS screen / frontend changes (feature 5), item search, listing all items at once, admin CRUD for
categories or items, showing inactive records, pagination, caching, new dependencies.
