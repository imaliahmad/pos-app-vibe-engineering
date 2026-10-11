# Skeleton
Status: done
Plan item: 1

## Goal
A developer can run `uv run flask --app app init-db` to create the SQLite database with
all tables, and `uv run pytest -q` passes. This is the base every later feature builds on.

## Changes
- `app/__init__.py`: `create_app(test_config: dict | None = None) -> Flask`. Sets `SECRET_KEY`
  (dev default, overridable), `DATABASE` = `instance/pos.sqlite`, creates the instance folder,
  configures `logging`, registers `db.init_app(app)`. No blueprints yet.
- `app/db.py`: `get_db()` (one `sqlite3` connection per request in `g`, `row_factory = sqlite3.Row`,
  `PRAGMA foreign_keys = ON`), `close_db()` on app teardown, `init_db()` runs `schema.sql`,
  `init-db` Flask CLI command, `init_app(app)` wires teardown + command.
- `app/schema.sql`: `CREATE TABLE IF NOT EXISTS` for `users`, `categories`, `items`, `sales`,
  `sale_items` exactly as in `docs/ARCHITECTURE.md` (money columns INTEGER, `active` default 1,
  `created_at` default `CURRENT_TIMESTAMP`, foreign keys, `role` CHECK in (`admin`, `cashier`)).
  `IF NOT EXISTS` so re-running `init-db` never wipes data.
- `app/responses.py`: `success(data=None, message="OK", status_code=200)` and
  `failure(message, errors=None, status_code=400)`, both return `(Response, int)` with body
  `{"status", "message", "data", "errors"}`.
- `tests/conftest.py`: `app` fixture (temp-file DB via `tmp_path`, `TESTING=True`, runs `init_db()`),
  `client` and `runner` fixtures. The logged-in client comes later with feature 3.
- `tests/__init__.py`: empty, so pytest puts the project root on `sys.path` and `import app` works.
- `tests/test_skeleton.py`: the tests below.
- `.gitignore`: already lists `instance/`, no change needed.

## Test cases
- `create_app({"TESTING": True, "DATABASE": tmp})` → `app.testing` is True and uses the temp DB path.
- `runner.invoke(args=["init-db"])` → output says the DB was initialised; `sqlite_master` lists all 5 tables.
- Run `init-db` twice after inserting a category → no error, the row is still there.
- Inside an app context, `get_db()` called twice → same connection; `PRAGMA foreign_keys` returns 1.
- `success({"x": 1}, "Done")` in a request context → status 200, JSON `{"status": true, "message": "Done", "data": {"x": 1}, "errors": []}`.
- `failure("Bad input", ["quantity required"], 422)` → status 422, `status: false`, `data: null`, errors list as given.

## Out of scope
No seed data, no users/login, no `auth.py`, no blueprints or API endpoints, no frontend pages,
no changes to `main.py` or `pyproject.toml` (no new dependencies).
