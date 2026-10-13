# Seed
Status: done
Plan item: 2

## Goal
A developer can run `uv run flask --app app seed` after `init-db` to fill the database with
3 categories, ~10 items and two users (`admin/admin123`, `cashier/cashier123`), so later
features have data to work with. Local dev only.

## Changes
- `app/repositories/__init__.py`: empty, makes `repositories` a package.
- `app/repositories/user_repository.py`: `insert_user(username: str, password_hash: str, role: str) -> int`
  (parameterized INSERT, returns the new id). Does not commit.
- `app/repositories/category_repository.py`: `insert_category(name: str) -> int` and
  `count_categories() -> int`. Does not commit.
- `app/repositories/item_repository.py`: `insert_item(category_id: int, name: str, price: int) -> int`.
  Does not commit.
- `app/seed.py`: sample data as constants (prices as INTEGER, e.g. `150` = 1.50):
  - Drinks: Cola 150, Water 100, Orange Juice 250, Coffee 200
  - Snacks: Chips 120, Chocolate Bar 180, Cookies 220
  - Bakery: Croissant 250, Bagel 200, Muffin 275
  - Users: `admin` (role `admin`) and `cashier` (role `cashier`), passwords hashed with
    `werkzeug.security.generate_password_hash`.

  `seed_db() -> bool`: if any category already exists, log "already seeded" and return `False`
  without changes. Otherwise insert everything through the repositories, commit once, return `True`.
  `seed` Flask CLI command calls it and echoes "Seeded the database." or "Database already seeded, nothing changed.".
  `init_app(app)` registers the command.
- `app/__init__.py`: call `seed.init_app(app)` after `db.init_app(app)`.
- `tests/test_seed.py`: the tests below.

## Test cases
- `runner.invoke(args=["seed"])` → exit code 0, output says "Seeded"; DB has 3 categories and 10 items.
- After seed, `users` has `admin` with role `admin` and `cashier` with role `cashier`;
  `check_password_hash(row["password_hash"], "admin123")` is True and the stored hash ≠ `"admin123"`.
- After seed, every item `price` is an `int` > 0 and every item's `category_id` points at an existing category.
- Run `seed` twice → second run exit code 0, output says "already seeded"; still 3 categories, 10 items, 2 users.
- `seed` on a DB where `init-db` ran but a category was added manually → nothing inserted, 0 users (seed is skipped as a whole, never partial).

## Out of scope
No login/auth code or `auth.py`, no read/list repository functions (those come with features 3 and 4),
no services/handlers/endpoints, no frontend, no reset/wipe command, no inactive sample rows,
no new dependencies.
