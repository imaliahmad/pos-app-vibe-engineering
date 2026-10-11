# Backend rules (app/)

## Layers (one direction only)
endpoints → handlers → services → repositories → SQLite

| Layer | Folder | Does | Never does |
|---|---|---|---|
| Endpoint | `endpoints/` | Flask blueprint route, auth decorator, call handler | Logic, SQL |
| Handler | `handlers/` | Read and validate request input, call service, build the JSON response | SQL, business rules |
| Service | `services/` | Business rules (e.g. calculate sale total), return `(data, error)` | SQL, Flask `request` |
| Repository | `repositories/` | SQL queries, return plain dicts/lists | Business rules, formatting |

## Shared files
- `__init__.py`   app factory `create_app()`, registers blueprints and CLI commands
- `db.py`         `get_db()` connection per request, `init-db` command
- `schema.sql`    all CREATE TABLE statements
- `seed.py`       `seed` command: sample categories, items, one admin and one cashier
- `auth.py`       `login_required` and `role_required` decorators
- `responses.py`  `success(data, message)` / `failure(message, errors, status_code)` helpers

## Rules
- All SQL lives in `repositories/`. Always parameterized (`?`). Never f-strings in SQL.
- Saving a sale (header + lines) happens in one transaction: all rows or none.
- Every handler response is built with `responses.py`. Never return a raw dict.
- Every API endpoint except login requires `login_required`.
- Passwords are hashed with `werkzeug.security` (comes with Flask). Never store plain text.
- New endpoint: use the `add-endpoint` skill.
